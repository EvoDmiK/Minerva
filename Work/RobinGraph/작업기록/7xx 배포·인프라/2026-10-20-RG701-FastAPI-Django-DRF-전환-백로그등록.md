---
created: 2026-10-20
updated: 2026-10-20
project: RobinGraph
type: work-log
category: 7xx 배포·인프라
task_id: RG-701
tags:
  - robingraph
  - backlog
  - django
  - drf
  - fastapi
---

# RG-701 FastAPI → Django + DRF 전환 백로그 등록 — 2026-10-20

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|RG-701 상세]]

## 요약

- 작업 ID **RG-701** (7xx 배포·인프라의 첫 등록 작업), 우선순위 **1 (최우선 · 다음 착수 1순위)**, 상태 **계획 (백로그 등록 · 미착수)**.
- 이번 작업은 백로그 등록 문서 작업이다. 전환 구현·서비스 재시작·DB 변경·TEST/Production 배포·commit/push는 하지 않았다.
- 저장소 기록: `docs/work-log/2026-10-20-django-drf-migration-backlog.md` (main-2 워크트리, Root 검토 후 복사 예정).

## 요청 배경과 목표

- 사용자가 Orca 코디네이터를 통해 FastAPI → Django + Django REST Framework(DRF) 전환을 최우선 백로그로 추가하도록 요청했다.
- 기존 일치 항목이 있으면 재사용하고 없으면 카테고리 체계에 맞는 새 ID를 부여한다. 최우선·다음 착수 1순위·계획 상태로 등록한다.

## 확인한 근거

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

## 등록 내용

목적·범위·단계·완료 기준은 [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx 백로그 RG-701 상세]]에 한 곳으로 관리한다. 핵심: 기존 API URL·응답·오류 계약 보존, `app.py`의 채팅 오케스트레이션·응답 매핑을 프레임워크 독립 서비스로 추출, Django+DRF URL·View·Serializer 계층 추가, Neo4j 드라이버·검색·벡터 코드와 조류 근거·데이터 유지, 기존 PG SQL·스키마 초기 유지 및 Django auth/admin 마이그레이션과 명시 분리, query → chat → ingest 순 이전, 정적 UI 재사용, 테스트·Docker·CLI·Jenkins·런타임 갱신, TEST 통합·브라우저·n8n 호환·롤백 계획 확인 후 별도 승인된 Production. 성능 향상은 약속하지 않는다.

## 변경 전후

- 전: 7xx 등록 작업 없음, 다음 착수 대기 표는 RG-406(후속 대기)·RG-101(보류).
- 후: RG-701을 최우선(1)·계획 상태로 등록하고 대기 표 맨 위에 추가. RG-406(우선순위 5·상태 문구)·RG-101(보류)·최후순위 보류 4건·완료 항목은 변경하지 않았다.

## 변경 문서

- `Work/RobinGraph/RobinGraph 작업 백로그.md`: 카테고리 표 7xx 수치, 카테고리별 보기 701 행, 현황 대시보드 첫 행, 신규 착수 대기 설명·표 첫 행, `### RG-701` 안내 절, 7xx 안내 문장, 변경 이력, `updated`.
- `Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그.md`: 작업 현황, RG-701 상세, 작업기록 링크, `updated`.
- `Work/RobinGraph/작업기록/index.md`: 7xx 작업기록 수, `updated`.
- 이 작업기록(신규).

## 검증 방법과 결과

- 저장 후 각 Obsidian 파일을 다시 읽어 RG-701 ID·우선순위·상태·링크와 RG-101·RG-406 기존 문구 보존을 확인했다.
- 코드 테스트·실제 DB/API·브라우저 검증: 해당 없음(문서만 변경, 앱 코드 미변경).

## 배포·커밋

- 배포·commit/push 없음. Root(Codex)가 저장소 로컬 기록을 검토 후 반영한다.

## 남은 한계와 후속

- 착수 시 엔드포인트 전수 계약, 비동기·스트리밍 사용 여부, Pydantic 모델과 Serializer 대응, ASGI/WSGI 선택, Django 설정·비밀값 관리, 실제 Jenkinsfile 내용, Django 마이그레이션 DB·스키마 분리 방식을 확인·결정한다.
- 담당 에이전트·모델: 최초 등록 시점에는 미지정(착수 시 Codex 배정)이었다. 이 문구는 당시 이력이며 아래 2026-10-20 사전 배정으로 대체되었다.

## 담당 에이전트·모델 사전 배정 (2026-10-20 추가)

- 사용자가 Orca 코디네이터를 통해 RG-701 담당 에이전트·모델의 사전 배정을 요청했고, 코디네이터가 승인한 배정을 문서 담당이 기록했다. 우선순위 1·계획(미착수)과 RG-101 보류·RG-406 상태는 변경하지 않았다.
- 단계별 표(단계·범위, 역할, 에이전트, 정확한 계획 모델 ID, 워크트리, 산출물, 의존·순서)는 [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 담당 사전 배정 (2026-10-20 · 계획)|7xx 백로그의 RG-701 담당 사전 배정]]에 한 곳으로 관리한다.
- 요약: 총괄 책임 Codex·`gpt-6.1-sol`·dev-codex / 구현 책임 Claude·`claude-opus-5-5`·dev-claude / UI 호환 책임 Codex·`gpt-6.1-sol`·main(dev-agy, 제품명 Antigravity 워크트리의 UI 역할 범위 유지, RG-701 한정 선택) / 문서 담당 Claude·`claude-opus-5-5`·main-2. Codex↔Claude 교차 검토, UI는 소비 화면 검증, 문서 담당은 실제 증거만 기록.
- 모델은 향후 계획 선택이며 실행 중 모델 검증·설정 변경이 아니다. Root는 기존 dev-claude 세션 모델 `claude-opus-5-5`를 확인했고, `gpt-6.1-sol`은 사용 가능한 Codex 계획 모델이다(현재 실행 중이라는 주장 아님). 공통 AGENTS.md·세션 설정 변경, 구현·다른 에이전트 기동·서비스·DB·배포·commit/push는 없다.
- 반영 문서: 전체 백로그(대기 표 담당 칸·RG-701 안내 절·변경 이력), 7xx 백로그(작업 현황·RG-701 담당 항목·배정 표), 이 작업기록, 저장소 `docs/work-log/2026-10-20-django-drf-migration-backlog.md`(main-2). 저장 후 재조회로 확인했다.
