---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-07-ORCA-쓰레드별-토큰-사용량-검증]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# ORCA 쓰레드별 토큰 사용량 검증

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-쓰레드별-토큰-사용량-검증]] · 분류 근거 {"인프라":0,"자동화":3,"관측성":30,"데이터":2}

## 1. 개요 및 목적

Grafana의 보존 집계 전체에서 최고 사용량은 **RobinGraph / Codex / 「작업 진행 상황 확인」** 쓰레드다. 사용일은 **2026-09-21~09-28**, 총 **280,576,166 토큰**, 모델 호출 **2,048회**이며 모델은 `gpt-5.6-sol`, `gpt-6-sol`이다.

단일 작업 ID의 순위가 아닌 **쓰레드 누적 순위**다. ORCA 세션 검색 DB의 해당 쓰레드 원문 사용자 메시지에서 n8n 재수집, 테스트 Neo4j/n8n 구성, source record의 PostgreSQL 분리, RAG/LangChain·LangGraph, NAS TEST/PROD 환경 준비가 함께 이어졌음을 확인했다. 구현 성공 여부를 이번 조회에서 재검증한 것은 아니다.

## 2. 핵심 아키텍처 및 원칙

- 결론
- 상위 5개
- 1위의 토큰 해석
- 출처와 범위

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

Grafana의 보존 집계 전체에서 최고 사용량은 **RobinGraph / Codex / 「작업 진행 상황 확인」** 쓰레드다. 사용일은 **2026-09-21~09-28**, 총 **280,576,166 토큰**, 모델 호출 **2,048회**이며 모델은 `gpt-5.6-sol`, `gpt-6-sol`이다.

단일 작업 ID의 순위가 아닌 **쓰레드 누적 순위**다. ORCA 세션 검색 DB의 해당 쓰레드 원문 사용자 메시지에서 n8n 재수집, 테스트 Neo4j/n8n 구성, source record의 PostgreSQL 분리, RAG/LangChain·LangGraph, NAS TEST/PROD 환경 준비가 함께 이어졌음을 확인했다. 구현 성공 여부를 이번 조회에서 재검증한 것은 아니다.

|순위|프로젝트·에이전트|쓰레드|사용일|총 토큰|모델 호출|
|---|---|---|---|---:|---:|
|1|RobinGraph·Codex|작업 진행 상황 확인|09-21~09-28|280,576,166|2,048|
|2|RobinGraph·Codex|팝업 스타일로 만들어 주세요|10-01~10-06|153,580,642|1,174|
|3|RobinGraph·Codex|Git 상태 확인|09-28~10-01|86,416,055|727|
|4|RobinGraph·Codex|작업 진행 상황 확인|09-05~09-07|70,203,853|547|
|5|RobinGraph·Codex|Graphify 적용 방안 검토하기|09-08~09-12|62,155,962|446|

총 토큰 순위는 실제 요금 또는 구독 한도 소진율 순위가 아니다. 특히 1위에는 반복되는 캐시 입력이 크게 포함된다. 호출별 비용 가중치나 세부 작업별 사용량은 확인하지 않았다.

- 확인: 2026-10-07 19:18 KST
- Grafana MCP에서 대시보드 및 SQL 조회 구조 확인: `서비스 모니터링`, UID `dafsnnz67rw6ioc`, 패널 46 `Orca 쓰레드별 사용량`
- 데이터소스: `Hermes Telemetry Ingest`, UID `ffskrzljzwr28b`
- 테이블: `observability.orca_thread_usage_daily`
- MCP에 SQL 실행 도구가 없어 같은 Grafana의 인증 HTTP `/api/ds/query`에 읽기 전용 SELECT를 실행. HTTP 200 및 각 쿼리 성공 확인.
- 집계 범위: 2026-09-05~2026-10-06, 219행, 167개 에이전트·쓰레드 조합
- 마지막 관측: 2026-10-06 23:34:45 KST. 10월 7일의 새 사용량을 포함한 실시간 전체 이력이라고 주장하지 않는다.
- `event_id` 중복 0건. 에이전트·프로젝트·쓰레드로 그룹화하고 모델별 행을 합산했다.
- 1위 쓰레드 ID: `01a0c281-9bea-78e2-9a36-b1dd36df900c`
- 작업 내용 대조: ORCA `ai-vault/session-search.sqlite`의 원문 메시지, 해당 쓰레드 사용자 메시지 58개. 예: 09-21 n8n 재수집 요청, 09-22 source record RDB 분리 요청, 09-24 LangChain/LangGraph RAG 요청, 09-27 NAS TEST/PROD 환경변수 요청.
- 상세 SQL·응답·계산 근거: `/opt/data/agent-artifacts/local/2026-10-07-orca-token-ranking/grafana-evidence.json`

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-쓰레드별-토큰-사용량-검증]]
- [[Dev/index|Dev 인덱스]]
