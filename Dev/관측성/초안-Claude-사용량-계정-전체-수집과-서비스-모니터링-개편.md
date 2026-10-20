---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-03-Claude-사용량-계정-전체-수집과-서비스-모니터링-개편]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Claude 사용량 계정 전체 수집과 서비스 모니터링 개편

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-03-Claude-사용량-계정-전체-수집과-서비스-모니터링-개편]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":25,"데이터":0}

## 1. 개요 및 목적

Claude 사용량이 Mac mini의 Claude Code status line에서만 갱신돼, 다른 기기나 VS Code 확장에서 쓴 양이 늦게 반영되던 문제를 고쳤다. 수집기가 Claude Code 로그인 토큰으로 계정 전체 사용률을 5분마다 조회하고, 실패하면 기존 status line 캐시로 되돌아가게 했다.

같은 날 `통합 대시보드`를 `서비스 모니터링`으로 이름을 바꾸고, Antigravity Claude·GPT(`third_party`) 패널과 알림을 제거했다. 5시간 사용률 알림은 처음 추가했고, 주간 사용률 알림은 구간별 알림으로 바꿨다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 시작한 문제
- Claude 사용량 수집
- 알림 변경
- 대시보드 변경
- 겪은 문제
- instant 쿼리가 모든 구독 패널을 비움
- Git Sync가 방금 고친 내용을 되돌림
- Hermes 사용량이 비어 보임
- 배포 구조
- 남은 일
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```
Claude Code OAuth 토큰(macOS 키체인)
  → 사용량 endpoint 조회 (5분 간격, 읽기 전용)
  → ai_subscription_quota_used_percent{provider="claude",window="session|weekly"}
  → 실패 시 status line 캐시로 폴백
```

## 4. 검증 근거 및 트러블슈팅

Claude 사용량이 Mac mini의 Claude Code status line에서만 갱신돼, 다른 기기나 VS Code 확장에서 쓴 양이 늦게 반영되던 문제를 고쳤다. 수집기가 Claude Code 로그인 토큰으로 계정 전체 사용률을 5분마다 조회하고, 실패하면 기존 status line 캐시로 되돌아가게 했다.

- 토큰은 **읽기만** 한다. refresh하면 Claude Code의 로그인 세션이 바뀔 수 있어서다. 토큰이 만료됐으면 오류로 처리하고 폴백한다.
- 토큰은 로그와 지표 라벨에 출력하지 않는다.
- endpoint는 공식 문서화된 API가 아니다. 응답 형식이 바뀌면 조회가 실패하고 폴백으로 넘어간다.
- 지표 이름과 라벨이 그대로라서 대시보드와 알림은 수정하지 않았다.
- 응답의 `five_hour`, `seven_day`에 사용률(%)과 초기화 시각(ISO)이 들어 있다. 사용률은 0~100 범위라 그대로 쓴다.
- 환경변수 `CLAUDE_USAGE_API`, `CLAUDE_USAGE_INTERVAL_SECONDS`, `CLAUDE_USAGE_TIMEOUT_SECONDS`, `CLAUDE_USAGE_URL`을 추가했다.
- 단위 테스트(응답 파싱, 폴백)를 추가해 11개가 통과한다.

| 규칙 | 조건 | 비고 |
| --- | --- | --- |
| AI 5-hour quota high | 5시간 사용률 80% 초과, 2분 지속 | 신규. Claude·Antigravity Gemini 대상. Codex는 5시간 한도가 없다. |
| AI weekly quota high | 주간 사용률 50/70/85/95% 구간별 1회 알림 | 기존 85% 단일 조건에서 변경. |
| 수집 실패, 사용률 | `pool!="third_party"` | Antigravity Claude·GPT pool 제외. |

- 원인: 대시보드 시간 범위가 `now/d ~ now/d`라 끝 시각이 오늘 23:59다. instant 쿼리는 그 시각을 기준으로 평가돼서 `time()`이 미래가 되고, `reset_timestamp <= time()` 조건에 모든 구간이 걸렸다.
- Prometheus에는 값이 정상으로 있었다. 쿼리를 직접 조회해서 확인했다.
- 해결: `time()`을 쓰는 패널 9개의 instant 설정을 되돌렸다. 시간 범위가 `now/w ~ now`인 인프라 모니터링의 3곳은 그대로 뒀다.
- 교훈: `time()`을 쓰는 쿼리는 시간 범위의 끝이 `now`가 아니면 instant로 바꾸지 않는다.

- Claude에도 15분 stale 알림을 붙일 수 있다. 며칠 지켜본 뒤 추가한다.
- 대시보드 시간 범위를 늘릴지, Hermes 패널만 따로 설정할지 정한다.
- 사용량 endpoint가 바뀌었는지 확인하려면 수집기 에러 로그의 `claude usage API unavailable` 메시지를 본다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-03-Claude-사용량-계정-전체-수집과-서비스-모니터링-개편]]
- [[Dev/index|Dev 인덱스]]
