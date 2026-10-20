---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-07-ORCA-최근7일-토큰-사용량-검증]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# ORCA 최근 7일 토큰 사용량 검증

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-최근7일-토큰-사용량-검증]] · 분류 근거 {"인프라":0,"자동화":1,"관측성":55,"데이터":1}

## 1. 개요 및 목적

오늘을 포함한 한국 시간 달력일 7일, **2026-10-01~10-07** 기준. 일별 테이블이므로 직전 168시간의 정밀 집계는 아니다. 현재 보존된 데이터는 **10-06까지**, 마지막 관측은 **10-06 23:34:45 KST**다. 10-07 사용량이 포함된 완전한 실시간 순위가 아니다.

1위는 **RobinGraph / Codex / 「팝업 스타일로 만들어 주세요」**, 총 **153,580,642 토큰**, **1,174회 모델 호출**, 모델 **gpt-6.1-sol**이다. 여러 작업이 이어진 쓰레드의 누적 사용량이지 단일 팝업 수정 비용이 아니다.

## 2. 핵심 아키텍처 및 원칙

- 기준과 결론
- 조회와 검증
- 상위 3개 캐시 적중률·비캐시 사용량 추가 확인

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- 확인 시각: 2026-10-07 19:21 KST
- Grafana MCP로 확인한 `서비스 모니터링` dashboard `dafsnnz67rw6ioc` / panel 46의 데이터소스 사용.
- PostgreSQL datasource UID: `ffskrzljzwr28b`
- 테이블: `observability.orca_thread_usage_daily`
- MCP에 SQL 실행 도구가 없어 같은 Grafana의 `/api/ds/query`에 인증 HTTP 읽기 전용 SELECT 실행. HTTP 200 및 쿼리 성공 확인.
- 필터: `usage_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-07'`
- 그룹: `agent, project_label, thread_id`; 모델별 행을 합산하여 `sum(total_tokens) DESC` 정렬.
- 해당 기간 64행, 39개 에이전트·쓰레드 조합.
- 1위 쓰레드 ID: `01a0f530-ce91-7b53-8cf2-fb76a11b1cca`
- 입력 153,032,897 / 캐시 읽기 149,049,984 / 출력 547,745 / 총 153,580,642. Codex 입력에 포함된 캐시 읽기를 총량에 다시 더하지 않았다.

[[2026-10-07-ORCA-쓰레드별-토큰-사용량-검증|전체 보존 기간 순위]]

캐시 읽기 제외 토큰은 `total_tokens - cache_read_tokens`, 즉 비캐시 입력 + 캐시 쓰기 + 출력이다. 요금·구독 소진량이 아니라 비교용 비캐시 토큰량이다. 캐시 읽기도 무료가 아니며 모델/구독별 가중치는 확인하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-최근7일-토큰-사용량-검증]]
- [[Dev/index|Dev 인덱스]]
