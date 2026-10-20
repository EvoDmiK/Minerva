---
created: 2026-10-20
updated: 2026-10-20
project: RobinGraph
type: work-log
category: 7xx 배포·인프라
task_id: RG-701
status: in-progress
tags:
  - robingraph
  - django
  - drf
  - migration
---

# RG-701 FastAPI → Django + DRF 전환 구현·TEST 배포 — 2026-10-20

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx RG-701 상세]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록|백로그 등록·담당 배정 기록]]

> [!NOTE] 진행 중 — TEST 배포·검증 완료 · Production 승인 대기
> Root(Codex)가 실제 실행해 전달한 최종 증거와 dev-codex `docs/verification/assets/2026-10-20-rg701/` 산출물(문서 담당 읽기 전용 확인)을 근거로 한다. 문서 담당은 테스트·배포를 재실행하지 않았다. RG-701 항목 전체 완료가 아니다.

저장소 기록: `docs/work-log/2026-10-20-rg701-django-drf-migration.md` (main-2 워크트리)

## 요약

- RG-701 (7xx 배포·인프라), 우선순위 1 (최우선, 변경 없음).
- 상태: 계획 (미착수) → **진행 중 (TEST 배포·검증 완료 · Production 승인 대기)**.
- 착수 근거: 사용자 승인("그렇게 진행해줘").
- 결과: 공개 API 런타임을 네이티브 Django 5.2.18 + DRF 3.16.1로 전환(FastAPI 미import). TEST 이미지 `robingraph-api:test-rg701-django-34f84c494c6a` 배포, healthy·실제 TEST API·공개 브라우저·n8n·DB 불변 검사 통과.
- 남은 범위: Production(별도 승인), commit/push, 롤백 실제 실행, 물리 모바일·재부팅, AMD64 빌드, 네이티브 ingest 실제 DB 쓰기(fake만 검증).

## 요청 배경과 목표

- 2026-10-20 등록·사전 배정 후 사용자가 구현 진행을 승인했다.
- 목표: 기존 공개·내부 API URL과 요청·응답·오류 계약을 유지한 채 Django + DRF로 전환, 조류 근거·데이터·Neo4j 검색 재사용, 프레임워크 독립 서비스 계층. 성능 향상은 약속하지 않는다.
- 승인 범위: 구현·검증·TEST 배포. Production·운영 DB는 별도 승인 전 금지. commit/push 범위 밖.

## 역할 분담

| 역할 | 에이전트 | 모델 | 워크트리 | 담당 |
|---|---|---|---|---|
| 총괄·통합 (Root) | Codex | 현재 세션 모델(재설정 없음) | dev-codex | `django_api` 설정·ASGI, CLI, 의존성, Docker·Jenkins, 통합·TEST 배포 |
| 구현 | Claude | `claude-opus-5-5` (계획) | dev-claude | 네이티브 DRF View·Serializer·URL·factory, 서비스 추출 |
| UI 호환 | Codex | `gpt-6.1-sol` (계획) | main (dev-agy) | 정적 UI·API 소비 HTTP 호환 |
| 독립 검토 | 검토자 | `gpt-6.1-sol` | — | 새 API·런타임·CLI·인프라 전수 검토 |
| 문서 | Claude | `claude-opus-5-5` | main-2 (dev) | 저장소 기록·Obsidian 단독 쓰기 |

- UI 담당 세션은 모델 업데이트 프롬프트가 건너뛰어져 같은 터미널에서 재시도했다는 전달이 있었다. 실제 실행 모델은 문서 담당 미확인.

## 원인·근거와 설계 결정

- **stateless Django**: `INSTALLED_APPS=['rest_framework']`, `MIDDLEWARE=[]`, `DATABASES={}`, `APPEND_SLASH=False`, DRF 인증 없음·`AllowAny`·JSON 전용. auth/admin/session 미설치, **Django 마이그레이션 없음**. PG 스키마는 기존 `ingest/migrations` SQL·`_schema_migration`이 소유.
- `SECRET_KEY`는 환경 변수 `ROBINGRAPH_DJANGO_SECRET_KEY` 또는 실행 시 생성(값 미기록). `DATA_UPLOAD_MAX_MEMORY_SIZE=None`(아래 발견 1).
- 공개 API는 `robingraph.api.drf.create_django_app` → `DjangoApiApplication`. 런타임 FastAPI 프록시 없음.
- 기존 FastAPI 앱·보조 함수는 차등 비교 기준으로만 보존. 고정 OpenAPI(`api/drf/openapi.json`·`openapi_ingest.json`)는 호환용이며 이후 API 변경 시 함께 갱신해야 한다.
- 독립 AviList TEST runner(FastAPI)는 설계상 미전환·불변.

### 기준선 (착수 전)

| 항목 | 값 |
|---|---|
| Python 전체 | 999 실행 · 961 통과 · 38 건너뜀 · 0 실패 (23.058초, 오프라인/모의) |
| 공개 OpenAPI | `openapi-before.json` |
| TEST DB 읽기 | 이름 벡터 855, 파일럿 실행 1건 succeeded, 카탈로그·기타 파이프라인 해시 (`db-before.json`) |
| TEST API·계약 | `live-before.json` 5사례, `live-contract-before.json` |

### 배포 전 독립 검토 발견과 조치

- 확인: 네이티브 legacy 스위트 242 실행·1 건너뜀·0 실패, DTO 33개 AST 동일, FastAPI 미import, 150ms 모의 호출 4건 164ms(병렬), 앱 2개 handler 격리. (mock/fake 기반)
- 발견 1: Django 기본 2.5MiB 상한으로 정상 3MB ingest가 기존 200 → 새 400. → `DATA_UPLOAD_MAX_MEMORY_SIZE=None`(Root) + 회귀 테스트(Claude).
- 발견 2: 허용되지 않은 Host 응답 200/500 혼재. → 초기 `get_host()` 검증으로 일반 JSON `400` + 테스트(Claude, 후속 dispatch).
- 발견 3: Root 런타임 테스트 `DATABASES == {}` 순서 문제 → dummy backend 단언.

## 계약과 변경 전후

- 유지: `POST /v1/answers`, `/v1/chat`, `/v1/search`, `GET /v1/observations`, `/v1/taxa/lineage`, `/v1/taxa/{name-relations,related,similar,ecological-related,subspecies,profile}`, `/health`, `/openapi.json`, 정적 `/`·`/chat`·`/birds`·`/favicon.ico`·`/static/...`, 내부 `/internal/v1/ingest/*`(내부 Bearer).
- 전: FastAPI/Pydantic(`robingraph.api.app`) + uvicorn. 후: `serve-fixture` → `robingraph.django_api.asgi:application`, `serve-neo4j`·`serve-ingest` → `robingraph.api.drf.create_django_app(...)` + uvicorn. TEST 명령 `robingraph serve-neo4j --host 0.0.0.0 --port 8000`.
- 동등성: 기존 FastAPI(18011) vs 새 Django(18012), 같은 fixture·로컬 실제 소켓 95사례 — 전체 JSON(`error: null`)·바이트·MIME·cache·location·traversal **95/95 일치**.
- 의도한 변화: 잘못된 Host → 모든 경로에서 일반 JSON `400`.
- 기존 동작(새 문제 아님): 공개 서버 끝 슬래시 `307` → `http` 리다이렉트는 전환 전부터 존재.

## 변경 파일

dev-codex 미커밋 작업 트리. 이전 작업의 미커밋 변경과 섞여 있어 RG-701 관련으로 확인한 파일만 적는다. 이미지 소스 전체는 `test-release.json` 파일별 SHA-256으로 고정.

- 신규: `src/robingraph/django_api/{settings,asgi,__init__}.py`; `src/robingraph/api/drf/`(`application.py`·`views.py`·`serializers.py`·`urls.py`·`validation.py`, 고정 OpenAPI·문서 HTML); `src/robingraph/api/{schemas,services,ingest_service}.py`; `tests/test_django_runtime.py`·`test_drf_legacy_suite.py`·`test_drf_parity.py`.
- 수정: `api/app.py`·`api/ingest_router.py`(서비스 이전 후 얇은 legacy 어댑터), `cli.py`, `pyproject.toml`·`uv.lock`(django·djangorestframework 추가, 공유 DTO 직접 의존 `pydantic>=2.12,<3` 명시(설치 2.13.5), fastapi는 legacy·AviList용으로 유지), `Dockerfile`·`Jenkinsfile`·`ci/Jenkinsfile.production`·`ci/Jenkinsfile.test`(`django check` 단계), `scripts/verify_api_deployment.py`, `README.md`(Root 담당).
- 문서 담당: 저장소 이 작업 기록(신규), Obsidian 아래 4개. 선행 등록 기록·`docs/deployment-profile.md`는 수정하지 않음.

## 검증 결과 (최종 · `summary.json`)

| 구분 | 결과 | 종류 |
|---|---|---|
| Python 전체 | 1,262 실행 · 1,223 통과 · 39 건너뜀 · 0 실패 (27.690초) | 오프라인 fixture/mock |
| 프런트엔드 Node | 317 통과 · 0 실패 · 0 건너뜀 | mock |
| HTTP 동등성 | 95/95 | 로컬 실제 소켓 + fixture |
| `django check` / `git diff --check` | 문제 없음 / 0 | 정적 |
| Host·3MB 회귀 + 변이 검증 | 통과 (Host 검증 제거 시 7개, 상한 해제 제거 시 3MB 테스트 실패) | mock |
| Docker ARM64 전체 소스 빌드 | 통과 (`django check` 포함) | 실제 빌드 |
| 격리 fixture smoke | `--network none` 통과 | 실제 컨테이너 |
| TEST 앱 교체 | 앱만 재생성 → healthy → `manage.sh verify` 통과 | 실제 TEST |
| 런타임 | `DjangoApiApplication`, Django 5.2.18, DRF 3.16.1, FastAPI 미import | 실제 TEST 이미지 |
| 실제 TEST API 5사례 | 전후 5/5: Kea(all·outside→answer), Keaa(outside→clarify), Anas platyrhynchos(korea→answer), lineage | **실제 DB/API** |
| 계약 검사 | health·OpenAPI·`청둥오리` lineage 200, drift 없음 | **실제 API** |
| 공개 브라우저 | Chromium 1280·390·320 × 2질의 = 6 요청 통과, JS 오류 0, 넘침 없음, `/birds` 200, 스크린샷 | **실제 공개 URL**, mocking 없음, 물리 기기 아님 |
| n8n | `n8n-test` `rgAvilistTest01` 7노드, exit 0, prepare reused·verify 회귀 4건·apply `already_applied`, projection 없음 | **실제 n8n TEST** |
| DB 불변 | 전후 동일: 벡터 855, 카탈로그·파이프라인 해시, 파일럿 1건 | **실제 DB 읽기** |
| graphify | rc 0, 6,576 nodes · 13,829 edges · 389 communities | — |

- health `fixture-avlist-2025`와 lineage `v2025b` 차이는 서로 다른 데이터 영역이라 정상(검증기 기록).
- 실행 수 증가 999 → 1,262 = 정확히 263개: Django 런타임 4 + DRF 동등성 17 + legacy 스위트 네이티브 재실행 242 (Root 전달).

### 중간 실패·건너뛰기

- 계약 검증기 첫 실행: `schemas` 모듈 통합 전이라 `ModuleNotFoundError` → 통합 후 해결, 그 시점 앱 배포 시도 없음.
- 공개 health: Python 기본 `urllib` `403`, `curl` GET `200`, 내부 `200`. 실제 공개 브라우저 통과. 앱 장애 아님(403 원인 미확인).
- 중간 회귀 1,260/1,221/39/0은 Host·3MB 테스트 추가 전 값(최종값으로 대체).
- 건너뜀 39건: 외부 통합 opt-in 검사, 이번에 켜지 않음.

## TEST 배포와 롤백

| 항목 | 값 |
|---|---|
| 대상 | TEST M4 16GB Mac 앱 (`https://robingraph-test.dove-nest.com`) |
| 새 이미지 | `robingraph-api:test-rg701-django-34f84c494c6a` |
| 소스 해시 | `34f84c494c6a100a73674a5c25be599d52a50431a2a5af264f4deb7688f4370a` (미커밋 스냅샷, 기준 HEAD `bc643ee9edef0fc58c605adde70b4808b7622ac5`) |
| 새 release | `/Users/kimdove/robingraph-test/releases/rg701-django-34f84c494c6a-4f4628` (verified) |
| 롤백 기준 이미지 | `robingraph-api:test-rg406-outside-spelling-1c7cbbdaf1c7` |
| 롤백 기준 release | `/Users/kimdove/robingraph-test/releases/rg406-outside-spelling-1c7cbbdaf1c7` |
| 롤백 | 이전 release·이미지 보존, 자동 복구 경로 준비. **실제 롤백 미실행** |
| 불변 | TEST DB·Neo4j·n8n 위치, DB 스키마, 도메인 이름 벡터, Jenkins job, 독립 AviList runner |

## 배포 프로필 메모

`docs/deployment-profile.md`의 FastAPI 아키텍처 설명은 당시 제안 기록으로 유지. 현재 구현(2026-10-20): 공개 API 런타임은 Django 5.2.18 + DRF 3.16.1 네이티브 ASGI(`robingraph.api.drf`, 설정 `robingraph.django_api.settings`), Django DB·마이그레이션 없음, PG 스키마는 기존 SQL 소유. TEST 검증 완료, Production은 아직 전환 전 이미지(승인 대기). AviList TEST runner는 FastAPI 유지.

## 배포·커밋

- TEST: 위 이미지로 앱만 교체·검증. Production: 변경 없음. commit/push·Jenkins job 실행·AMD64 빌드 없음.

## 남은 한계와 후속

- Production 승인 대기: 운영 반영 시 AMD64 포함 이미지 빌드·운영 승인 gate·운영 검증 별도 필요.
- 롤백 미실행(경로만 준비). 물리 모바일·Safari·Firefox·물리 재부팅·네이티브 ingest 실제 DB 쓰기·AMD64 미검증.
- legacy FastAPI 어댑터·고정 OpenAPI·`fastapi` 의존성 제거 시점은 후속 결정. API 변경 시 스냅샷 갱신 필요.
- TEST 이미지는 미커밋 소스 스냅샷: 커밋 시 `test-release.json` 해시와 대조 필요.
- 백로그 완료 기준의 Production 단계가 남아 RG-701은 진행 중으로 유지.

## 진행 경과 (UTC)

- 06:40 Root 아키텍처·초기 증거 / 06:42 asgi import 정정(초기 초안 폐기, 빠진 파일 관찰은 실패가 아니어서 제외) / 06:52 독립 검토 발견 3건 / 06:53 HTTP overlay 95/95 / 06:58 통합 회귀 1,260/1,221/39/0 / 07:00 최종 1,262/1,223/39/0, TEST 빌드 시작 / 07:02 TEST 배포·전체 검사 통과.

## Obsidian 재조회

- 초기 단계: 전체 백로그 `진행 중 작업` 구역·목차·현황·대기 표·안내 절·변경 이력, 7xx 백로그, index 7xx 15 확인. RG-406·RG-101·기존 등록·배정 이력 원문 유지.
- 최종 단계(2026-10-20 저장 후 MCP 재조회): 이 노트 158줄(frontmatter `status: in-progress`, 최종 검증 표·TEST 배포/롤백 표 포함). 전체 백로그 479줄 — 카테고리별 보기 701 `진행 중 (최우선 1 · TEST 배포·검증 완료 · Production 승인 대기)`, 현황표 `진행 중 (TEST 검증 완료 · Production 승인 대기) | 1 (최우선)`, 진행 중 작업 구역·대기 표·안내 절 TEST 결과 문단·변경 이력 최상단 항목 확인, RG-406·RG-101 행 원문 유지. 7xx 백로그 96줄 — 작업 현황 첫 항목·RG-701 상태·작업기록 링크 확인, 담당 배정 표 불변. index 7xx `15`. 링크는 텍스트 대조만, 화면 클릭 검증 없음.
