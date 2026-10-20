---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-07-Claude-사용량-캐시-회귀-진단]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Claude 사용량 캐시 회귀 진단

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-07-Claude-사용량-캐시-회귀-진단]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":15,"데이터":0}

## 1. 개요 및 목적

**전날부터 계속 수집이 멈춘 것이 아니라, 오늘 오후 3시 부근까지 갱신되다가 과거 캐시로 되돌아간 패턴이다.** API 조회 실패 후 status line 캐시 fallback이 유력하지만, 런타임 로그와 현행 코드를 확인하지 않아 근본 원인은 미확인이다.

2026-10-07 16:05~16:08 KST 부근 Grafana MCP 조회 기준. 코드·설정·서비스는 바꾸지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 결과
- 확인된 사실
- 왜 정상으로 표시되는가
- 유력한 설명과 미확인 사항
- 다음 확인 지점
- 이전 안내 정정
- 로컬 근거

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

**전날부터 계속 수집이 멈춘 것이 아니라, 오늘 오후 3시 부근까지 갱신되다가 과거 캐시로 되돌아간 패턴이다.** API 조회 실패 후 status line 캐시 fallback이 유력하지만, 런타임 로그와 현행 코드를 확인하지 않아 근본 원인은 미확인이다.

- 회귀는 15:00:34~15:05:34 표본 사이에 발생했다. 정확한 발생 초는 미확인.
- `ai_subscription_quota_used_percent{provider="claude"}` 최근 2시간, 600초 간격 조회에서도 주간 사용량이 8%에서 7%로 되돌아갔다.
- 세션 사용량은 회귀 전 표본에서 0%였지만 최신 instant 응답에는 없어 현재 값은 미확인.
- 현재 Claude `collector_up=1`이지만 마지막 성공 시각은 오래됐다.
- 같은 instant 조회에서 Codex 데이터는 약 105초 전, Antigravity는 약 96초 전이었다. Claude 데이터 경로에 국한된 이상 패턴이다.
- subscription 관련 metric discovery에서는 오류 유형·API 성공 여부·데이터 출처 지표를 확인하지 못했다.

[[Work/Gullinkambi/작업기록/2026-10-03-Claude-사용량-계정-전체-수집과-서비스-모니터링-개편]]에는 계정 전체 사용량 API를 5분마다 조회하고 실패하면 기존 status line 캐시로 fallback한다고 기록돼 있다.

[[Work/Gullinkambi/작업기록/2026-10-03-AI-subscription-exporter-README]]에는 유효 캐시를 `CLAUDE_MAX_AGE_SECONDS`까지 허용하고, 문서상 기본값이 24시간이라고 기록돼 있다. 이 때문에 오래된 캐시도 허용 범위 내라면 `up=1`일 수 있다. 단, 현행 배포 설정은 확인하지 않았다.

- **유력한 설명:** Claude 계정 API 조회가 실패하여 오래된 status line 캐시로 전환됨. 실제 메트릭 패턴이 문서상 fallback 동작과 일치한다.
- **실패 원인 미확인:** 토큰 만료, HTTP 제한, 네트워크·timeout, 응답 형식 변경 등은 후보일 뿐이다.
- 수집기 버전·설정 변경, 재시작 또는 상태 선택 문제도 배제하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-07-Claude-사용량-캐시-회귀-진단]]
- [[Dev/index|Dev 인덱스]]
