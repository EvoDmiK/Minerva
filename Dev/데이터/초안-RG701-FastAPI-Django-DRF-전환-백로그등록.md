---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-701 FastAPI → Django + DRF 전환 백로그 등록 — 2026-10-20

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록]] · 분류 근거 {"인프라":0,"자동화":3,"관측성":0,"데이터":4}

## 1. 개요 및 목적

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|RG-701 상세]]

- 작업 ID **RG-701** (7xx 배포·인프라의 첫 등록 작업), 우선순위 **1 (최우선 · 다음 착수 1순위)**, 상태 **계획 (백로그 등록 · 미착수)**.
- 이번 작업은 백로그 등록 문서 작업이다. 전환 구현·서비스 재시작·DB 변경·TEST/Production 배포·commit/push는 하지 않았다.
- 저장소 기록: `docs/work-log/2026-10-20-django-drf-migration-backlog.md` (main-2 워크트리, Root 검토 후 복사 예정).

## 2. 핵심 아키텍처 및 원칙

- 요약
- 요청 배경과 목표
- 확인한 근거
- 등록 내용
- 변경 전후
- 변경 문서
- 검증 방법과 결과
- 배포·커밋
- 남은 한계와 후속

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- 작업 ID **RG-701** (7xx 배포·인프라의 첫 등록 작업), 우선순위 **1 (최우선 · 다음 착수 1순위)**, 상태 **계획 (백로그 등록 · 미착수)**.
- 이번 작업은 백로그 등록 문서 작업이다. 전환 구현·서비스 재시작·DB 변경·TEST/Production 배포·commit/push는 하지 않았다.
- 저장소 기록: `docs/work-log/2026-10-20-django-drf-migration-backlog.md` (main-2 워크트리, Root 검토 후 복사 예정).

- **중복 확인**: 전체 백로그에 프레임워크 전환 항목 없음. 볼트 본문 검색 `Django OR DRF OR "REST Framework"` 결과는 `Private/인프라/` 노트 2건뿐이고 RobinGraph 작업 항목이 아니다. → 새 ID 부여.
- **ID·카테고리**: 서버 런타임·의존성·Docker·CLI·Jenkins·TEST 통합·롤백이 함께 바뀌므로 7xx 배포·인프라를 주 카테고리로 정했다(가장 큰 변경 쪽 규칙에 따른 문서 담당 판단, Codex 검토로 바뀔 수 있음). 7xx 등록 작업이 없어 다음 번호 701.
- **현재 구현 (main-2 `07b1cf8`, 읽기 전용 예비 분석)**:
  - `pyproject.toml`: `fastapi`, `uvicorn[standard]`, `neo4j`, `psycopg[binary]`, `langchain-core`; 테스트 extra `httpx2`.
  - `src/robingraph/api/app.py`(1,624줄): 라우트와 채팅 오케스트레이션·응답 매핑이 한 파일에 있다. 공개 라우트 `POST /v1/answers`, `POST /v1/chat`, `POST /v1/search`, `GET /v1/observations`, `GET /v1/taxa/lineage`, `GET /v1/taxa/{name-relations,related,similar,ecological-related,subspecies,profile}`, `GET /health`, 화면·정적 `/`, `/chat`, `/birds`, `/favicon.ico`, `/static/{asset_path:path}`.
  - `src/robingraph/api/ingest_router.py`: `/internal/v1/ingest` 접두사, 내부 Bearer 의존성, `active/{pipeline_id}`·`begin`·`{run_id}/append|finalize|fail`, Pydantic `response_model`.
  - `cli.py`가 `uvicorn.run("robingraph.api.app:app")`, Dockerfile CMD `robingraph serve-fixture --port 8000`, HEALTHCHECK `/health`.
  - PostgreSQL은 `ingest/postgres.py`의 `_schema_migration`과 `ingest/migrations/0001~0004_*.sql`로 자체 관리 → Django 마이그레이션과 분리 필요.
  - n8n 워크플로가 `/internal/v1/ingest/begin`, `/internal/v1/ingest/active/reference-taxonomy-traits` 등을 호출 → n8n 호환 검증 필요.
  - `tests/` 72개 중 17개 파일이 `TestClient`/`fastapi` 참조.
  - Jenkins: `docs/jenkins-deployment.md` 기준 `Jenkinsfile`·`ci/Jenkinsfile.production`·`ci/Jenkinsfile.test`. main-2에는 Jenkinsfile이 없어 내용은 미확인.
  - graphify: main-2에 `graphify-out/` 없음 → 원문 직접 확인.
- 이 분석은 **예비 분석**이며 전체 전환 설계를 검증한 결과가 아니다.

목적·범위·단계·완료 기준은 [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx 백로그 RG-701 상세]]에 한 곳으로 관리한다. 핵심: 기존 API URL·응답·오류 계약 보존, `app.py`의 채팅 오케스트레이션·응답 매핑을 프레임워크 독립 서비스로 추출, Django+DRF URL·View·Serializer 계층 추가, Neo4j 드라이버·검색·벡터 코드와 조류 근거·데이터 유지, 기존 PG SQL·스키마 초기 유지 및 Django auth/admin 마이그레이션과 명시 분리, query → chat → ingest 순 이전, 정적 UI 재사용, 테스트·Docker·CLI·Jenkins·런타임 갱신, TEST 통합·브라우저·n8n 호환·롤백 계획 확인 후 별도 승인된 Production. 성능 향상은 약속하지 않는다.

- 저장 후 각 Obsidian 파일을 다시 읽어 RG-701 ID·우선순위·상태·링크와 RG-101·RG-406 기존 문구 보존을 확인했다.
- 코드 테스트·실제 DB/API·브라우저 검증: 해당 없음(문서만 변경, 앱 코드 미변경).

- 착수 시 엔드포인트 전수 계약, 비동기·스트리밍 사용 여부, Pydantic 모델과 Serializer 대응, ASGI/WSGI 선택, Django 설정·비밀값 관리, 실제 Jenkinsfile 내용, Django 마이그레이션 DB·스키마 분리 방식을 확인·결정한다.
- 담당 에이전트·모델 미지정(착수 시 Codex 배정).

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록]]
- [[Dev/index|Dev 인덱스]]
