---
created: 2026-10-27
updated: 2026-10-27
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-26-Mac-mini-16-ORCA-수집-범위-확대]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Mac mini 16 ORCA 수집 범위 확대

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-26-Mac-mini-16-ORCA-수집-범위-확대]] · 분류 근거 {"인프라":1,"자동화":2,"관측성":14,"데이터":0}

## 1. 개요 및 목적

"오늘도 ORCA 집계가 안 된다"는 문제를 조사했다. Mac mini 16에서 Orca로 실행한 세션 중 `~/orca` 밖 폴더에서 돈 세션이 통째로 빠지고 있었다.

| 날짜 | 수정 전 | 수정 후 |
|---|---|---|
| 10/24 | Codex 1.26억 | Codex 1.65억, Claude 2,800만 |
| 10/25 | 없음 | Codex 1.07억, Claude 3,400만, Antigravity 44만(95건) |
| 10/26 | Codex 29만 | Codex 322만, Claude 48만 |

## 2. 핵심 아키텍처 및 원칙

- 결과
- 진단 순서
- 조치
- 배포
- 알아 둘 점
- Antigravity 일별 합계 차이 (같은 날 후속)
- 남은 일
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- 일별 합계(`orca_usage_daily`)와 호출 이벤트 합계(`orca_call_events`)가 Claude·Codex에서 일치하는 것을 확인했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-26-Mac-mini-16-ORCA-수집-범위-확대]]
- [[Dev/index|Dev 인덱스]]
