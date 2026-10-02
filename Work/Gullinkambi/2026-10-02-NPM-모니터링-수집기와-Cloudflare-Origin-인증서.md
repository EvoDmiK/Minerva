---
created: 2026-10-02
date: 2026-10-02
project: Gullinkambi
type: worklog
status: in-progress
tags:
  - gullinkambi
  - grafana
  - prometheus
  - nginx-proxy-manager
  - cloudflare
  - monitoring
---

# NPM 모니터링 수집기와 Cloudflare Origin 인증서

## 요약

Nginx Proxy Manager(NPM)를 Gullinkambi 인프라 모니터링에 추가했다. 인프라 대시보드에 `NPM` 탭과 알림 규칙 4개를 만들고, NPM 액세스 로그와 SQLite DB를 읽는 `npm-exporter`를 NAS에 배포했다.

수집기를 붙이자마자 일부 프록시 호스트의 원본 인증서가 만료된 상태라는 것이 드러났다. Cloudflare가 앞단에서 엣지 인증서를 제공하고 있어 사용자 영향은 없었지만, 근본 해결로 Cloudflare Origin 인증서(와일드카드, 15년)로 교체하는 작업을 진행 중이다.

같은 날 AI 구독 탭에서 초기화 시각이 지난 Claude 사용률이 현재 값처럼 보이던 문제도 함께 정리했다.

## 완료 결과

| 작업 | 결과 |
| --- | --- |
| NPM 대시보드 | 인프라 모니터링에 `NPM` 탭 추가 (상태 요약·트래픽·오류와 인증서·컨테이너 자원) |
| NPM 알림 | 컨테이너 down, 5xx 비율, 인증서 만료 임박, 수집 지연 규칙 4개 |
| NPM 수집기 | `npm-exporter` 컨테이너 배포, NAS Prometheus `npm_exporter` job 연결 |
| AI 구독 탭 | 초기화 시각이 지난 구간을 숨기고 `초기화됨 · 갱신 대기` 표시 |
| 주간 사용률 알림 | 지난 구간을 제외하도록 쿼리 수정 |
| 문서 | Gullinkambi 영문·한국어 README에 수집 조건과 알림 표 추가 |

## NPM 모니터링 구성

### 대시보드

| 영역 | 패널 | 데이터 |
| --- | --- | --- |
| 상태 요약 | 컨테이너 상태, 요청/초, 5xx 비율, 최단 인증서 만료, 수집 지연, 메모리 | cAdvisor + `npm_*` |
| 트래픽 | 호스트별 요청/초, 상태 코드별 요청/초, 호스트별 응답 트래픽 | `npm_*` |
| 오류와 인증서 | 호스트별 5xx 비율, 도메인별 인증서 남은 일수 | `npm_*` |
| 컨테이너 자원 | CPU, 네트워크 | cAdvisor |

### 메트릭 규격

| 메트릭 | 레이블 | 의미 |
| --- | --- | --- |
| `npm_http_requests_total` | `host`, `status` | 프록시 호스트·상태 코드별 요청 누적값 |
| `npm_http_response_bytes_total` | `host` | 프록시 호스트별 응답 바이트 누적값 |
| `npm_certificate_expiry_timestamp_seconds` | `domain` | 사용 중인 인증서 만료 시각 |
| `npm_collector_last_success_timestamp_seconds` | 없음 | 마지막 성공 수집 시각 |
| `npm_collector_up` | 없음 | 최근 수집 성공 여부 |
| `npm_log_parse_errors_total` | 없음 | 형식이 맞지 않은 로그 줄 수 |

### 수집기 설계

```text
NPM proxy-host-*_access.log ─┐
                             ├─▶ npm-exporter :9823 ─▶ NAS Prometheus ─▶ Grafana NPM 탭 / 알림
NPM database.sqlite ─────────┘
```

- 로그는 15초마다 이어서 읽는다. NPM logrotate는 rename 후 새 파일을 만들기 때문에 inode가 바뀌거나 파일이 줄어들면 처음부터 다시 읽는다.
- 시작할 때는 기존 로그를 건너뛰고 새로 쌓이는 요청부터 센다.
- `host` 레이블은 요청의 Host 헤더가 아니라 NPM DB에 등록된 프록시 호스트의 첫 번째 도메인을 쓴다. 스캐너가 임의의 Host 헤더를 보내도 레이블 수가 늘어나지 않는다.
- 인증서 만료일은 인증서 파일이 아니라 NPM DB의 `certificate.expires_on`에서 읽는다. 개인키가 있는 디렉터리는 마운트하지 않는다.
- 컨테이너는 읽기 전용 파일시스템, 모든 capability 제거, 비root 사용자, 메모리 64MB 제한으로 실행한다.
- 실제 로그 전체로 시험했을 때 파싱 오류는 0건이었다.

### 알림 규칙

| 규칙 | 조건 | 지속 | No data |
| --- | --- | --- | --- |
| Nginx Proxy Manager down | cAdvisor가 2분 동안 컨테이너를 관측하지 못함 | 3분 | Alerting |
| Nginx Proxy Manager 5xx elevated | 0.05 req/s 초과 호스트의 5xx 비율 5% 초과 | 10분 | OK |
| Nginx Proxy Manager certificate expiring | 인증서 만료까지 14일 미만 | 10분 | OK |
| Nginx Proxy Manager collector stale | 마지막 성공 수집 15분 초과 | 5분 | Alerting |

## 인증서 만료 발견과 대응

수집기를 연결하자 일부 프록시 호스트의 NPM 인증서가 7월에 이미 만료된 상태로 확인됐다. Let's Encrypt 자동 갱신이 해당 인증서에서만 실패한 것으로 보인다.

```text
브라우저 ──(Cloudflare 엣지 인증서: 유효)──▶ Cloudflare ──(NPM 원본 인증서: 만료)──▶ NAS
```

- Cloudflare SSL 모드가 Full이라 원본 인증서를 검증하지 않아 사용자는 정상 접속 중이었다.
- Full (strict)로 바꾸면 해당 호스트는 526 오류가 난다.
- NPM에 인증서가 연결되지 않은 호스트 일부는 이미 525 오류를 내고 있었다.

### 해결 방향: Cloudflare Origin 인증서

1. Cloudflare → SSL/TLS → Origin Server에서 `*.dove-nest.com`, `dove-nest.com` 인증서 발급 (15년) — **완료**
2. NPM → Certificates → Add Certificate → Custom Certificate로 등록 — 진행 중
3. 각 Proxy Host의 SSL 인증서를 새 인증서로 교체
4. Cloudflare SSL 모드를 Full (strict)로 전환
5. 사용하지 않는 기존 Let's Encrypt 인증서 삭제

- Origin 인증서는 Cloudflare만 신뢰한다. Cloudflare를 거치지 않고 도메인으로 직접 접속하면 브라우저 경고가 뜬다.
- NPM이 Custom 인증서의 만료일을 DB에 기록하므로 수집기와 대시보드는 별도 수정 없이 따라온다.
- 개인키는 vault나 Git 저장소에 저장하지 않고 NPM 입력 창에만 넣는다.

## AI 구독 탭: Claude 수집 지연 정리

Claude 사용량이 14시간 지연된 것으로 보여 원인을 확인했다.

- Claude 값은 웹에서 가져오는 방식이 아니다. Mac mini의 Claude Code CLI status line 입력(`rate_limits`)을 캐시하는 수동 방식이다.
- Claude Pro/Max 구독 사용량을 조회하는 공식 공개 API가 없어서 status line이 사실상 유일한 공식 경로다.
- Mac mini에서 Claude Code를 쓰지 않는 동안에는 갱신되지 않는 것이 정상이다.
- VS Code 확장에서는 status line이 실행되지 않는다. 문서 확인과 임시 probe 테스트로 확인했다. 따라서 NAS의 VS Code 확장 사용분은 직접 수집할 수 없다.
- 구독 한도는 계정 전체 기준이므로, 다른 환경의 사용량도 Mac mini의 다음 갱신 때 사용률에 함께 반영된다.

그래서 수집 방식은 유지하고 표시 방식을 고쳤다.

- 사용률·추이 패널: `unless on (provider, pool, window) (ai_subscription_quota_reset_timestamp_seconds <= time())`로 초기화 시각이 지난 구간을 제외한다.
- 다음 초기화 패널: 지난 시각을 숨긴다.
- 수집 지연 패널 설명에 Claude 갱신 방식을 명시했다.
- Codex는 현재 5시간 구간 데이터가 없고 주간만 제공된다. 이 패널은 원래부터 No data였으므로 갱신 대기 문구를 넣지 않았다.

## 검증

| 확인 항목 | 결과 |
| --- | --- |
| 신규 패널 PromQL (instant·range) | 모두 성공 |
| 대시보드 JSON 문법 | `jq empty` 통과 |
| Git Sync 반영 | `NPM` 탭과 패널 13개 저장 확인 |
| alerting YAML 파싱·프로비저닝 | 성공, 규칙 22개 |
| docker compose config / promtool check config | 통과 |
| `up{job="npm_exporter"}` | 1 |
| 수집 지연 | 약 10초 |

## 트러블슈팅 메모

- Grafana가 dashboard JSON을 Go 방식으로 이스케이프(`&` → `&`, `<`, `>`)하므로 스크립트로 수정할 때 같은 형식으로 저장해야 diff가 깔끔하다.
- Grafana 관리자 비밀번호가 UI에서 바뀌어 있어 컨테이너 환경변수로는 API 인증이 안 된다. 상태 확인은 Grafana DB의 `resource`·`alert_rule` 테이블을 읽기 전용으로 조회했다.
- NAS Prometheus에는 `--web.enable-lifecycle`가 없어서 scrape 설정을 바꾸면 컨테이너를 재시작해야 한다.
- NPM 탭이 "아무것도 안 나온다"고 보였던 것은 수집기 없이 `npm_*` 패널만 먼저 배포했기 때문이다. 데이터가 없는 stat 패널이 임계값 기본 색(빨강·초록)으로 칠해져 장애처럼 보일 수 있다.
- 디스코드 Webhook URL은 파일 프로비저닝된 contact point라 Grafana UI에서는 바꿀 수 없다. `GF_DISCORD_WEBHOOK_URL`을 바꾸고 `docker compose up -d grafana`로 컨테이너를 다시 만들어야 한다.

## 주요 파일

| 저장소 | 파일 | 역할 |
| --- | --- | --- |
| Gullinkambi | `provisioning/dashboards/git-sync/Nest-Control-Room.json` | 인프라 대시보드 `NPM` 탭 |
| Gullinkambi | `provisioning/dashboards/git-sync/Aviary Control Room.json` | AI 구독 탭 지난 구간 처리 |
| Gullinkambi | `provisioning/alerting/services.yml` | NPM 알림 규칙 |
| Gullinkambi | `provisioning/alerting/ai-subscription.yml` | 주간 사용률 알림 쿼리 |
| Birds-Nest | `docker-compose/monitoring/npm-exporter/` | NPM 수집기 |
| Birds-Nest | `docker-compose/monitoring/docker-compose.yml` | `npm-exporter` 서비스 |
| Birds-Nest | `docker-data/monitoring/prometheus/prometheus.yml` | `npm_exporter` scrape job |

## Git 기록

| 저장소 | 브랜치 | 커밋 | 내용 |
| --- | --- | --- | --- |
| Gullinkambi | `main` | `8fb4c7b` | NPM 모니터링 탭과 알림 추가 |
| Gullinkambi | `main` | `521b22c` | AI 구독 지난 구간 숨김 |
| Gullinkambi | `main` | `0154e5b` | NPM 수집기 문서화, 수집 지연 알림 No data 처리 |
| Birds-Nest | `feat/npm-exporter` | `fce2a62` | NPM 트래픽·인증서 exporter |

Birds-Nest의 NAS 체크아웃(`dev-nas`)은 원격보다 커밋 약 90개 뒤처져 있었다. 실행 중인 서비스 설정이 바뀌는 것을 피하려고 병합하지 않고 수집기 커밋만 `feat/npm-exporter` 브랜치로 push했다.

## 남은 일

- [ ] NPM에 Cloudflare Origin 인증서 등록
- [ ] 모든 Proxy Host의 SSL 인증서 교체
- [ ] Cloudflare SSL 모드를 Full (strict)로 전환하고 전체 호스트 응답 확인
- [ ] 사용하지 않는 Let's Encrypt 인증서 삭제
- [ ] NAS Birds-Nest 체크아웃을 원격 `dev-nas`와 정리하고 `feat/npm-exporter` 병합

## 관련

- [[Work/Gullinkambi/2026-10-02-Grafana-Discord-알림-단일-카드-개선|Grafana Discord 알림 단일 카드 개선]]
- [[Work/Gullinkambi/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축|AI 구독 사용량 수집기·Grafana 대시보드 구축]]
- [[Work/Gullinkambi/2026-10-01-Grafana-알람과-Discord-연결|Grafana 알람과 Discord 연결]]
- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
