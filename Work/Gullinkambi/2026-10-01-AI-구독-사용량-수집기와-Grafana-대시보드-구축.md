---
created: 2026-10-01
date: 2026-10-01
project: Gullinkambi
type: worklog
status: completed
tags:
  - gullinkambi
  - grafana
  - prometheus
  - codex
  - claude
  - monitoring
---

# AI 구독 사용량 수집기·Grafana 대시보드 구축

## 요약

Codex와 Claude의 개인 구독 사용량을 Mac mini에서 수집하고, Prometheus federation을 거쳐 NAS의 Gullinkambi Grafana 통합 대시보드에서 확인할 수 있게 구성했다.

단기·주간 사용률, 다음 초기화 시각, 수집 상태, 토큰·세션·모델별 추이를 한 화면에 배치했다. 로그인 토큰이나 설정 파일 원문은 메트릭으로 노출하지 않는다.

## 완료 결과

| 작업 | 결과 |
| --- | --- |
| Codex 구독 사용량 수집 | app-server의 제한·사용량 정보를 정규화 |
| Claude 구독 사용량 수집 | status line의 5시간·7일 제한 정보를 정규화 |
| Mac mini 실행 환경 | exporter와 LaunchAgent 설치 도구 구현 |
| Prometheus 연결 | Mac mini scrape와 NAS federation 구성 |
| Grafana 표시 | 통합 대시보드에 `Codex · Claude 구독` 탭 추가 |
| 기존 설정 보존 | Claude의 기존 status line 명령을 multiplexer로 유지 |
| 수집 안정성 | Codex 제한 구간을 응답 순서가 아닌 기간으로 판별 |
| 자동 검증 | exporter 단위 테스트 5개 통과 |

## 데이터 흐름

```text
Codex app-server ─┐
                  ├─ Mac mini ai-subscription-exporter :9819
Claude status line┘                  │
                                     ▼
                         Mac mini Prometheus
                                     │
                              federation
                                     ▼
                            NAS Prometheus
                                     │
                                     ▼
              Grafana 통합 대시보드 / Codex · Claude 구독
```

수집기는 Codex와 Claude Code에 로그인된 Mac mini 사용자 환경에서 실행한다. Mac mini Prometheus가 `host.docker.internal:9819`를 scrape하고, NAS Prometheus가 정규화된 지표를 federation으로 가져간다.

## 수집기 구현

### Codex

`codex app-server`의 `account/rateLimits/read`와 `account/usage/read`를 사용한다. 제한 구간은 응답 배열 순서에 의존하지 않고 구간 길이로 판별해 `session`과 `weekly` 레이블에 매핑한다.

### Claude

Claude Code status line 입력의 `rate_limits.five_hour`와 `rate_limits.seven_day`를 사용한다. 전체 status line 입력 중 사용률과 모델명만 별도 캐시에 저장한다.

기존 status line 명령이 있으면 installer가 원래 명령을 보관하고 multiplexer로 연결한다. multiplexer는 동일한 JSON을 사용량 수집기와 기존 표시 명령 양쪽에 전달한다. 제거할 때는 원래 설정을 복구한다.

## Prometheus 메트릭

| 메트릭 | 필수 레이블 | 의미 |
| --- | --- | --- |
| `ai_subscription_quota_used_percent` | `provider`, `window` | 현재 구독 사용률 |
| `ai_subscription_quota_reset_timestamp_seconds` | `provider`, `window` | 다음 사용량 초기화 시각 |
| `ai_subscription_tokens_total` | `provider`, `type`, `model` | 누적 토큰 수 |
| `ai_subscription_sessions_total` | `provider` | 누적 세션 수 |
| `ai_subscription_collector_up` | `provider` | 최근 수집 성공 여부 |
| `ai_subscription_last_success_timestamp_seconds` | `provider` | 마지막 성공 수집 시각 |

`provider`는 `codex`·`claude`, `window`는 `session`·`weekly`를 사용한다. Claude의 5시간 구간은 단기 사용률로 표시한다.

## Grafana 대시보드

Gullinkambi의 `통합 대시보드`에 `Codex · Claude 구독` 탭을 추가했다.

### 현재 구독 상태

- Codex 단기 사용률
- Codex 주간 사용률
- Claude 5시간 사용률
- Claude 주간 사용률

### 초기화 및 수집 상태

- Codex 다음 초기화
- Claude 다음 초기화
- 구독 수집 상태
- 수집 지연

### 사용 추이와 활동

- 구독 사용률 추이
- 토큰 사용 추이
- 세션 수 추이
- 모델별 토큰 사용량

수집기 실패나 오래된 데이터를 실제 사용량 변화로 오해하지 않도록 데이터 품질 정보를 사용량 패널과 분리해서 표시한다.

## 구현 중 수정한 문제

### Codex 제한 구간 오매핑 방지

Codex가 반환하는 제한 구간의 배열 순서가 달라질 수 있으므로 첫 번째 값을 무조건 단기 사용량으로 처리하지 않는다. 구간의 기간을 기준으로 단기·주간을 구분하도록 수정하고 회귀 테스트를 추가했다.

### Claude 기존 status line 보존

사용량 수집 설정이 기존 Claude status line 표시를 대체하던 문제를 수정했다. multiplexer를 추가해 수집과 기존 표시를 함께 실행하고, 원래 설정을 복구할 수 있게 했다.

### 민감정보 최소화

수집기는 로그인 토큰이나 설정 파일 자체를 노출하지 않는다. Claude status line 캐시에도 사용률과 모델명만 저장한다.

## 검증

2026-10-01에 exporter 단위 테스트를 다시 실행해 5개 모두 통과했다.

```text
test_capture_strips_sensitive_status_fields ... ok
test_claude_status ... ok
test_codex_primary_window_uses_duration ... ok
test_codex_rate_limits ... ok
test_codex_tokens_deduplicates_nested_totals ... ok

Ran 5 tests — OK
```

## 주요 파일

| 저장소 | 파일 | 역할 |
| --- | --- | --- |
| Birds-Nest | `docker-compose/monitoring/ai-subscription-exporter/exporter.py` | Codex·Claude 수집과 Prometheus 메트릭 제공 |
| Birds-Nest | `docker-compose/monitoring/ai-subscription-exporter/install.py` | macOS LaunchAgent 설치·제거 |
| Birds-Nest | `docker-compose/monitoring/ai-subscription-exporter/claude_statusline_capture.py` | Claude 사용량 캐시 |
| Birds-Nest | `docker-compose/monitoring/ai-subscription-exporter/claude_statusline_mux.py` | 기존 status line과 수집 명령 병행 |
| Birds-Nest | `docker-compose/monitoring/prometheus.yml` | Mac mini scrape 대상 등록 |
| Birds-Nest | `docker-data/monitoring/prometheus/prometheus.yml` | NAS federation 지표 등록 |
| Gullinkambi | `provisioning/dashboards/git-sync/Aviary Control Room.json` | 통합 Grafana 대시보드 |

## Git 기록

| 저장소 | 커밋 | 내용 |
| --- | --- | --- |
| Birds-Nest | `8798911` | AI 구독 exporter와 Prometheus 연결 구현 |
| Birds-Nest | `df84574` | Claude status line 보존 |
| Birds-Nest | `9ce7a29` | Codex 제한 구간을 기간 기준으로 매핑 |
| Gullinkambi | `18a8a25` | AI 구독 대시보드 추가 |

## 운영 메모

- Claude Code에서 메시지를 한 번 전송해야 status line에 구독 제한 값이 들어온다.
- exporter의 기본 endpoint는 `0.0.0.0:9819/metrics`다.
- 9819 포트는 신뢰할 수 있는 모니터링 네트워크에서만 접근시킨다.
- 로그인 자격 증명은 Grafana나 Prometheus 레이블에 포함하지 않는다.
- 수집기가 실패하거나 데이터가 오래되면 사용률과 별개로 수집 상태·지연 패널에서 확인한다.

## 관련

- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
