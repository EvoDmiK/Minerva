---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-01-Grafana-알람과-Discord-연결]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Grafana 알람과 Discord 연결

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-01-Grafana-알람과-Discord-연결]] · 분류 근거 {"인프라":0,"자동화":13,"관측성":41,"데이터":4}

## 1. 개요 및 목적

Gullinkambi 대시보드에서 실제 조치가 필요한 상태를 선별해 Grafana-managed alert rule 18개를 구축했다. NAS·Mac mini 인프라, n8n·Hermes·OpenViking·Orca 서비스, Codex·Claude 구독 수집 상태를 한곳에서 평가한다.

알람은 파일 provisioning으로 관리하며 Discord Webhook을 contact point로 연결했다. 실제 firing 규칙을 임시로 생성해 Discord 전송을 확인하고, 정상 상태 전환에 따른 복구 알림도 시험한 뒤 임시 규칙을 완전히 삭제했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 구성 방식
- 알람 규칙 18개
- 인프라 가용성
- 인프라 용량·온도
- 워크플로우와 서비스
- AI 구독 사용량
- Discord 알림
- Source·Silence 외부 링크
- 배포와 검증
- 정적 검증
- Grafana 검증
- Discord 실전 테스트
- 실제 Claude 수집 알람과 후속 수정
- 주요 파일
- Git 기록
- 후속 조정
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

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

```text
/volume3/Gullinkambi/provisioning/alerting/
├── infrastructure.yml
├── services.yml
├── ai-subscription.yml
└── notifications.yml
```

```text
group_by: alertname, service, severity
group_wait: 30s
group_interval: 5m
repeat_interval: 4h
```

```dotenv
GF_DISCORD_WEBHOOK_URL=<Discord Webhook URL>
```

```dotenv
GF_SERVER_DOMAIN=monitoring.dove-nest.com
GF_SERVER_ROOT_URL=https://monitoring.dove-nest.com/
```

```ini
description = Mac mini exporter와 Codex·Claude 로그인 상태를 확인하세요.
summary = claude 구독 사용량 수집에 실패했습니다.
```

## 4. 검증 근거 및 트러블슈팅

알람은 파일 provisioning으로 관리하며 Discord Webhook을 contact point로 연결했다. 실제 firing 규칙을 임시로 생성해 Discord 전송을 확인하고, 정상 상태 전환에 따른 복구 알림도 시험한 뒤 임시 규칙을 완전히 삭제했다.

| 규칙 | 조건 | 지속 시간 | 등급 |
| --- | --- | --- | --- |
| n8n repeated failures | 최근 15분 실패 3건 이상 | 5분 | critical |
| n8n execution stuck | 실행이 30분 넘게 `running` | 1분 | critical |
| Hermes task heartbeat missing | 최근 24시간에 시작된 실행의 heartbeat가 10분 이상 없음 | 2분 | critical |
| Orca aggregation delayed | 일일 집계가 2일 이상 지연 | 15분 | warning |
| OpenViking exporter down | exporter 값이 1 미만 또는 No Data | 3분 | critical |
| OpenViking errors elevated | 최근 1시간 오류 3건 이상 | 5분 | warning |

Birds-Nest monitoring Compose가 두 값을 Grafana 컨테이너에 전달한다. `GF_SERVER_ROOT_URL`을 변경한 뒤에는 Grafana 컨테이너를 재생성해야 하며, 외부 health endpoint `https://monitoring.dove-nest.com/api/health`가 HTTP 200으로 응답하는 것을 확인했다.

정정된 주소로 `Source`와 `Silence` 링크를 넣은 Discord 테스트 메시지도 다시 보내 Webhook HTTP 204 응답을 확인했다.

- alerting YAML 파일 파싱 성공.
- 규칙 UID 중복 없음.
- 모든 규칙에 Query·Reduce·Threshold 단계 존재 확인.
- `git diff --check` 통과.
- Docker Compose 병합 검증 통과.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-01-Grafana-알람과-Discord-연결]]
- [[Dev/index|Dev 인덱스]]
