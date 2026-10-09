---
created: 2026-10-01
date: 2026-10-01
project: Gullinkambi
type: worklog
status: completed
tags:
  - gullinkambi
  - grafana
  - alerting
  - discord
  - prometheus
  - monitoring
---

# Grafana 알람과 Discord 연결

## 요약

Gullinkambi 대시보드에서 실제 조치가 필요한 상태를 선별해 Grafana-managed alert rule 18개를 구축했다. NAS·Mac mini 인프라, n8n·Hermes·OpenViking·Orca 서비스, Codex·Claude 구독 수집 상태를 한곳에서 평가한다.

알람은 파일 provisioning으로 관리하며 Discord Webhook을 contact point로 연결했다. 실제 firing 규칙을 임시로 생성해 Discord 전송을 확인하고, 정상 상태 전환에 따른 복구 알림도 시험한 뒤 임시 규칙을 완전히 삭제했다.

## 구성 방식

별도 Alertmanager를 추가하지 않고 Grafana Unified Alerting을 사용했다. Grafana가 Prometheus와 PostgreSQL 데이터소스를 모두 조회할 수 있어 인프라와 서비스 알람을 같은 정책으로 관리할 수 있다.

```text
Prometheus / PostgreSQL
          │
          ▼
Grafana-managed alert rules
          │
          ▼
Gullinkambi Discord contact point
          │
          ▼
Discord 알림 채널
```

알람 파일은 다음 경로에 있다.

```text
/volume3/Gullinkambi/provisioning/alerting/
├── infrastructure.yml
├── services.yml
├── ai-subscription.yml
└── notifications.yml
```

Birds-Nest의 Grafana Compose는 이 디렉터리를 `/etc/grafana/provisioning/alerting`에 읽기 전용으로 마운트한다.

## 알람 규칙 18개

### 인프라 가용성

| 규칙 | 조건 | 지속 시간 | 등급 |
| --- | --- | --- | --- |
| NAS node exporter down | `node_exporter`의 `up < 1` 또는 No Data | 3분 | critical |
| NAS cAdvisor down | `cadvisor`의 `up < 1` 또는 No Data | 3분 | critical |
| PostgreSQL exporter down | `postgres_exporter`의 `up < 1` 또는 No Data | 3분 | critical |
| Mac mini federation down | NAS의 Mac mini federation target `up < 1` | 3분 | critical |
| Mac mini node exporter down | federation은 있으나 `macmini_node`가 down | 3분 | critical |
| Mac mini M4 exporter down | federation은 있으나 `macmini_soc`가 down | 3분 | warning |

### 인프라 용량·온도

| 규칙 | 조건 | 지속 시간 | 등급 |
| --- | --- | --- | --- |
| NAS disk usage critical | `/volume1~3` 중 사용률 92% 초과 | 10분 | critical |
| Mac mini disk usage critical | OrbStack data 또는 `/mnt/mac` 사용률 92% 초과 | 10분 | critical |
| Mac mini temperature critical | CPU·GPU 최고 온도 95°C 초과 | 3분 | critical |

NAS는 데이터 볼륨만 감시하고 시스템·Docker 내부 mountpoint를 제외했다. Mac mini도 동일 디스크가 여러 경로로 중복 표시되지 않도록 대표 mountpoint 두 개만 사용한다.

### 워크플로우와 서비스

| 규칙 | 조건 | 지속 시간 | 등급 |
| --- | --- | --- | --- |
| n8n repeated failures | 최근 15분 실패 3건 이상 | 5분 | critical |
| n8n execution stuck | 실행이 30분 넘게 `running` | 1분 | critical |
| Hermes task heartbeat missing | 최근 24시간에 시작된 실행의 heartbeat가 10분 이상 없음 | 2분 | critical |
| Orca aggregation delayed | 일일 집계가 2일 이상 지연 | 15분 | warning |
| OpenViking exporter down | exporter 값이 1 미만 또는 No Data | 3분 | critical |
| OpenViking errors elevated | 최근 1시간 오류 3건 이상 | 5분 | warning |

Hermes 테이블에는 2026-07-30에 생성된 `running` 상태 작업 8건이 남아 있었다. 시각 제한 없이 조회하면 배포 직후 즉시 알람이 발생하므로 최근 24시간에 시작된 작업만 감시하도록 조정했다.

### AI 구독 사용량

| 규칙 | 조건 | 지속 시간 | 등급 |
| --- | --- | --- | --- |
| AI subscription collector down | Codex·Claude 수집 상태가 1 미만 | 5분 | warning |
| Codex subscription data stale | Codex 데이터가 15분 이상 갱신되지 않음 | 5분 | warning |
| AI weekly quota high | Codex·Claude 주간 사용률 85% 초과 | 10분 | warning |

Claude 사용량은 Claude Code에서 실제 메시지를 보낼 때 status line이 갱신된다. 따라서 Claude에 15분 지연 규칙을 적용하면 미사용 상태도 장애로 오인한다. 15분 stale 규칙은 Codex에만 적용하고, Claude는 exporter의 collector 상태와 24시간 캐시 만료 판단에 맡겼다.

## Discord 알림

Grafana contact point 이름은 `Gullinkambi Discord`다. 모든 Gullinkambi 알람은 다음 레이블로 묶어 같은 Discord 채널로 전달한다.

```text
group_by: alertname, service, severity
group_wait: 30s
group_interval: 5m
repeat_interval: 4h
```

복구 메시지도 활성화했다. Webhook URL은 저장소에 넣지 않고 다음 환경변수로만 전달한다.

```dotenv
GF_DISCORD_WEBHOOK_URL=<Discord Webhook URL>
```

실제 값은 Birds-Nest monitoring `.env`에만 있으며 `.env.example`에는 비밀값이 없는 예시 URL만 기록했다.

### Source·Silence 외부 링크

Grafana가 Discord 알림의 `Source`와 `Silence` 링크를 `localhost`로 만들지 않도록 외부 기준 URL을 명시했다.

```dotenv
GF_SERVER_DOMAIN=monitoring.dove-nest.com
GF_SERVER_ROOT_URL=https://monitoring.dove-nest.com/
```

Birds-Nest monitoring Compose가 두 값을 Grafana 컨테이너에 전달한다. `GF_SERVER_ROOT_URL`을 변경한 뒤에는 Grafana 컨테이너를 재생성해야 하며, 외부 health endpoint `https://monitoring.dove-nest.com/api/health`가 HTTP 200으로 응답하는 것을 확인했다.

정정된 주소로 `Source`와 `Silence` 링크를 넣은 Discord 테스트 메시지도 다시 보내 Webhook HTTP 204 응답을 확인했다.

## 배포와 검증

### 정적 검증

- alerting YAML 파일 파싱 성공.
- 규칙 UID 중복 없음.
- 모든 규칙에 Query·Reduce·Threshold 단계 존재 확인.
- `git diff --check` 통과.
- Docker Compose 병합 검증 통과.

### Grafana 검증

Grafana 13.2.1에서 파일 provisioning을 수행했다.

| 확인 | 결과 |
| --- | --- |
| Grafana 컨테이너 | 정상 실행 |
| 등록된 영구 규칙 | 18개 |
| 생성된 규칙 평가 상태 | 18개 |
| 초기 pending/firing | 0개 |
| alerting provisioning 오류 | 없음 |
| Discord contact point | `Gullinkambi Discord` / `discord` |
| 기본 notification policy | Discord로 라우팅 |

Prometheus와 PostgreSQL 원본 쿼리도 직접 실행해 데이터 반환을 확인했다. 검증 시점에는 NAS·Mac mini 수집 대상과 OpenViking exporter가 모두 `up=1`이었고, n8n 최근 실패·장기 실행은 0건이었다.

### Discord 실전 테스트

1. 항상 참이 되는 임시 Grafana 규칙 `gk_discord_test` 생성.
2. Grafana에서 firing 평가 후 local notifier 전송 로그 확인.
3. 규칙을 정상 상태로 바꿔 복구 알림 전송 확인.
4. `deleteRules` provisioning으로 임시 규칙 삭제.
5. 테스트 파일 제거 후 영구 규칙이 18개만 남은 것을 확인.
6. Git 작업 트리가 깨끗한 상태인지 확인.

Discord Webhook 자체도 테스트 메시지를 전송해 HTTP 204 응답을 확인했다.

### 실제 Claude 수집 알람과 후속 수정

테스트와 별개로 다음 실제 warning 알람이 발생했다.

```ini
description = Mac mini exporter와 Codex·Claude 로그인 상태를 확인하세요.
summary = claude 구독 사용량 수집에 실패했습니다.
```

Prometheus 이력을 확인한 결과 Claude의 `ai_subscription_collector_up`이 2026-10-01 15:59~16:10 KST에 약 12분 동안 `0`이었다. `AI subscription collector down` 규칙의 5분 지속 조건을 충족했으므로 Discord 전송 자체는 정상 동작이었다.

원인은 로그인 만료나 24시간 캐시 만료가 아니었다. Claude가 `rate_limits`를 포함하지 않은 status line 입력을 보냈을 때 마지막 정상 캐시를 빈 값으로 교체해 수집 실패가 발생했다. `claude_statusline_capture.py`를 유효한 제한 정보가 있을 때만 캐시를 교체하도록 수정하고 회귀 테스트를 추가했다.

수정은 Birds-Nest `dev-nas`의 `92bc329`와 Mac mini `dev-mac`의 `ab78629`로 배포했다. NAS와 Mac mini에서 단위 테스트 6개를 통과했고, 배포 후 `ai_subscription_collector_up{provider="claude"} 1`을 확인했다. 이제 일시적인 빈 status line 입력은 마지막 정상 캐시를 보존하며, 기본 24시간을 실제로 초과한 경우에만 Claude 수집 실패로 전환된다.

## 주요 파일

| 저장소 | 파일 | 역할 |
| --- | --- | --- |
| Gullinkambi | `provisioning/alerting/infrastructure.yml` | 호스트·exporter·디스크·온도 알람 |
| Gullinkambi | `provisioning/alerting/services.yml` | n8n·Hermes·Orca·OpenViking 알람 |
| Gullinkambi | `provisioning/alerting/ai-subscription.yml` | AI 구독 수집·지연·사용률 알람 |
| Gullinkambi | `provisioning/alerting/notifications.yml` | Discord contact point와 notification policy |
| Birds-Nest | `docker-compose/monitoring/docker-compose.yml` | alerting 디렉터리와 Webhook 환경변수 전달 |
| Birds-Nest | `docker-compose/monitoring/.env.example` | 비밀값 없는 Discord 변수 예시 |

## Git 기록

원격 변경을 먼저 가져온 뒤 Gullinkambi 알람 커밋을 최신 `main` 위에 rebase했다. 강제 push는 사용하지 않았다.

| 저장소 | 브랜치 | 커밋 | 내용 |
| --- | --- | --- | --- |
| Gullinkambi | `main` | `c6f38c0` | Grafana 알람 규칙 18개 추가 |
| Gullinkambi | `main` | `7f1ef56` | Discord contact point·policy 추가 |
| Birds-Nest | `dev-nas` | `c4b6f3f` | Grafana alerting provisioning 마운트 |
| Birds-Nest | `dev-nas` | `e67a95d` | Discord Webhook 환경변수 전달 |
| Birds-Nest | `dev-nas` | `92bc329` | Claude의 마지막 유효 사용량 캐시 보존 |
| Birds-Nest | `dev-mac` | `ab78629` | Mac mini 수집기에 캐시 보존 수정 배포 |
| Birds-Nest | `dev-nas` | `b766c33` | Grafana 외부 URL과 Source·Silence 링크 기준 설정 |
| Birds-Nest | `dev-mac` | `68153bc` | AI 구독 알람 운영 문서 추가 |
| Gullinkambi | `main` | `59a51d5` | Grafana 알람·Discord·외부 URL README 문서화 |

두 브랜치는 GitHub 원격과 동기화했다. Birds-Nest의 다른 homelab 미커밋 변경은 이 커밋과 push에 포함하지 않았다.

## 후속 조정

- [ ] 1~2주 운영 후 실제 발생 빈도를 보고 임계값과 `for` 시간을 조정한다.
- [ ] warning과 critical을 서로 다른 Discord 채널로 나눌 필요가 있는지 검토한다.
- [ ] 핵심 컨테이너 allowlist가 확정되면 컨테이너 미관측 알람을 추가한다.
- [ ] NAS RAID·SMART 상태는 전용 exporter를 추가한 뒤 별도 알람으로 구성한다.

## 관련

- [[Work/Gullinkambi/작업기록/2026-10-02-Grafana-Discord-알림-단일-카드-개선|Grafana Discord 알림 단일 카드 개선]]
- [[Work/Gullinkambi/작업기록/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구|ORCA Antigravity 사용량 집계와 Hermes 인증 복구]]
- [[Work/Gullinkambi/작업기록/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축|AI 구독 사용량 수집기·Grafana 대시보드 구축]]
- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
