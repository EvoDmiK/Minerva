---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# AI 구독 사용량 수집기·Grafana 대시보드 구축

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":50,"데이터":0}

## 1. 개요 및 목적

Codex와 Claude의 개인 구독 사용량을 Mac mini에서 수집하고, Prometheus federation을 거쳐 NAS의 Gullinkambi Grafana 통합 대시보드에서 확인할 수 있게 구성했다.

단기·주간 사용률, 다음 초기화 시각, 수집 상태, 토큰·세션·모델별 추이를 한 화면에 배치했다. 로그인 토큰이나 설정 파일 원문은 메트릭으로 노출하지 않는다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 완료 결과
- 데이터 흐름
- 수집기 구현
- Codex
- Claude
- Prometheus 메트릭
- Grafana 대시보드
- 현재 구독 상태
- 초기화 및 수집 상태
- 사용 추이와 활동
- 구현 중 수정한 문제
- Codex 제한 구간 오매핑 방지
- Claude 기존 status line 보존
- Claude 빈 사용량 입력으로 인한 오탐 방지
- 민감정보 최소화
- 검증
- 주요 파일
- Git 기록
- 운영 메모
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

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

```text
test_capture_strips_sensitive_status_fields ... ok
test_capture_preserves_last_valid_status_when_limits_are_missing ... ok
test_claude_status ... ok
test_codex_primary_window_uses_duration ... ok
test_codex_rate_limits ... ok
test_codex_tokens_deduplicates_nested_totals ... ok

Ran 6 tests — OK
```

## 4. 검증 근거 및 트러블슈팅

Codex와 Claude의 개인 구독 사용량을 Mac mini에서 수집하고, Prometheus federation을 거쳐 NAS의 Gullinkambi Grafana 통합 대시보드에서 확인할 수 있게 구성했다.

| 작업 | 결과 |
| --- | --- |
| Codex 구독 사용량 수집 | app-server의 제한·사용량 정보를 정규화 |
| Claude 구독 사용량 수집 | status line의 5시간·7일 제한 정보를 정규화 |
| Mac mini 실행 환경 | exporter와 LaunchAgent 설치 도구 구현 |
| Prometheus 연결 | Mac mini scrape와 NAS federation 구성 |
| Grafana 표시 | 통합 대시보드에 `Codex · Claude 구독` 탭 추가 |
| 기존 설정 보존 | Claude의 기존 status line 명령을 multiplexer로 유지 |
| 수집 안정성 | Codex 제한 구간을 기간으로 판별하고 Claude의 마지막 유효 캐시를 보존 |
| 자동 검증 | exporter 단위 테스트 6개 통과 |

Claude는 모든 status line 입력에 `rate_limits`를 포함하지 않는다. 새 입력에 유효한 제한 정보가 없으면 기존 정상 캐시를 덮어쓰지 않고 유지하며, 마지막 정상 캐시가 `CLAUDE_MAX_AGE_SECONDS`의 기본값인 24시간을 초과했을 때만 수집 실패로 처리한다.

수집기 실패나 오래된 데이터를 실제 사용량 변화로 오해하지 않도록 데이터 품질 정보를 사용량 패널과 분리해서 표시한다.

Codex가 반환하는 제한 구간의 배열 순서가 달라질 수 있으므로 첫 번째 값을 무조건 단기 사용량으로 처리하지 않는다. 구간의 기간을 기준으로 단기·주간을 구분하도록 수정하고 회귀 테스트를 추가했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축]]
- [[Dev/index|Dev 인덱스]]
