---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-08-Gemini-세션-주간-사용률-차이-진단]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Gemini 세션·주간 사용률 차이 진단

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-08-Gemini-세션-주간-사용률-차이-진단]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":6,"데이터":0}

## 1. 개요 및 목적

조회 시각: 2026-10-08 17:38 KST. Grafana Prometheus `PBFA97CFB590B2093`, `provider=antigravity`, `pool=gemini`. 코드·설정·서비스 변경 없음.

| 시각 KST | 세션 사용률 | 주간 사용률 | 설명 |
|---|---:|---:|---|
| 16:12:33 | 19.75% | 55.73% | 초기화 전 |
| 16:17:33 | 21.76% | 56.07% | 두 사용률 함께 증가 |
| 16:22:33 | 22.80% | 56.24% | 두 사용률 함께 증가 |
| 16:42:33 | 22.80% | 0% | 주간 reset이 다음 주로 이동 |
| 17:29:34~17:30:34 | 23.30% | 0% | 세션의 짧은 변동 |
| 17:31:34 이후 조회 표본 | 22.80% | 0% | 세션 이전 값으로 복귀 |

## 2. 핵심 아키텍처 및 원칙

- 결과
- 실제 관측
- 의미·미확인
- 후속 확인
- 근거 쿼리
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```promql
{__name__=~"ai_subscription_quota_(used_percent|reset_timestamp_seconds)",provider="antigravity",pool="gemini"}
max_over_time(ai_subscription_quota_used_percent{provider="antigravity",pool="gemini"}[45m]) - min_over_time(ai_subscription_quota_used_percent{provider="antigravity",pool="gemini"}[45m])
ai_subscription_quota_used_percent{provider="antigravity",pool="gemini",window="session"}
```

## 4. 검증 근거 및 트러블슈팅

- 주간 reset timestamp: `1791445247`(10/08 16:40:47) → `1792050047`(10/15 16:40:47).
- 초기 시계열은 5분 step, 짧은 변동 재검증은 1분 step이다.
- 45분 구간 raw 표본의 max-min: 세션 `0.5048811435999987`%p, 주간 `0`%p.
- 17:37:54 instant에서 collector_up=1, 마지막 수집 약 58초 전. 수집 성공과 quota 원본 정확성은 별개다.
- 대시보드 `dafsnnz67rw6ioc` panel 2014는 weekly 메트릭을 max로 표시하고 만료된 reset을 제외한다. Prometheus 원본도 0%이므로 패널만의 표시 문제는 아니다.

수집기 README는 `agy -p /usage --output-format json`의 `remaining_fraction`을 사용률로 변환하고 5시간/주간을 따로 정규화한다고 설명한다. 실행 중 코드 자체는 이번에 확인하지 못했다.

주간 초기화 전에는 주간 사용률도 실제로 증가했다. 초기화 후 세션 변동은 있었지만 이전 값으로 복귀했으므로, 이 기록만으로 지속적인 새 사용량이 주간에 누락된다고 확정할 수 없다. 공급자 API 집계 지연·quota 응답 불일치·exporter 파싱/캐시 문제 중 어느 것이 원인인지도 미확인이다.

공개 GitHub raw 코드 후보는 HTTP 404, 공식 Antigravity usage 문서 HTTP 가져오기는 실패했다. 브라우저·인증정보·서비스 변경은 사용하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-08-Gemini-세션-주간-사용률-차이-진단]]
- [[Dev/index|Dev 인덱스]]
