---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-08-RobinGraph-ORCA-전체기간-토큰-사용량-검증]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# RobinGraph ORCA 전체 보존 기간 토큰 사용량 검증

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-08-RobinGraph-ORCA-전체기간-토큰-사용량-검증]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":53,"데이터":0}

## 1. 개요 및 목적

Grafana의 `project_label = RobinGraph` 전체 보존 기간 **2026-09-05~2026-10-06** 합계는 **1,439,637,032토큰 (약 14.40억)**이다. 모델 호출 **12,165회**, 에이전트·쓰레드 조합 **134개**.

|에이전트|Grafana 총 토큰|모델 호출|쓰레드|
|---|---:|---:|---:|
|Codex|1,217,062,287|10,399|103|
|Claude|214,348,726|1,388|30|
|Antigravity|8,226,019|378|1|
|합계|1,439,637,032|12,165|134|

## 2. 핵심 아키텍처 및 원칙

- 결론
- 캐시와 집계 의미
- 근거와 범위
- 사용량이 가장 많았던 기간
- 하루 총 토큰 상위 3개
- 연속 7일 최대 구간
- 캐시 읽기 제외 기준의 최대 하루

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- 조회 시각: 2026-10-08 18:47 KST
- Grafana MCP로 확인한 서비스 모니터링 대시보드 `dafsnnz67rw6ioc`, panel 46.
- 데이터소스 `Hermes Telemetry Ingest`, UID `ffskrzljzwr28b`, 테이블 `observability.orca_thread_usage_daily`.
- 같은 Grafana `/api/ds/query`에 인증된 읽기 전용 SELECT 실행. HTTP 200, 쿼리 오류 없음.
- 필터 `lower(project_label) = 'robingraph'`, 시간 필터 없음. 에이전트별 `sum(total_tokens)`, `sum(request_count)`, `count(DISTINCT thread_id)`와 전체 프로젝트 집계 교차 확인.
- RobinGraph 172행, event_id 중복 0건, collector_id 4개. 이는 event_id 중복 여부만 검사한 것으로 다른 ID를 가진 의미적 중복까지 완전히 배제한다는 주장은 아니다.
- Grafana 전체 데이터 최신일은 10-08, 마지막 관측 10-08 18:31:59 KST이나, RobinGraph로 식별된 데이터 최신일은 10-06.
- **ORCA의 실제 최초 사용부터 모두 보존되었다는 의미는 아니다.** 9월 5일 이전 누락 기록은 확인하지 않았으며 `kimdove`, `projects`, `orca` 등의 다른 프로젝트 라벨 행은 RobinGraph에 임의 합산하지 않았다.

2026-10-08 18:50 KST에 같은 Grafana 데이터소스에 읽기 전용 SELECT 재실행(HTTP 200, 오류 없음). RobinGraph 보존 범위와 합계는 그대로 2026-09-05~10-06 / 1,439,637,032토큰이다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-08-RobinGraph-ORCA-전체기간-토큰-사용량-검증]]
- [[Dev/index|Dev 인덱스]]
