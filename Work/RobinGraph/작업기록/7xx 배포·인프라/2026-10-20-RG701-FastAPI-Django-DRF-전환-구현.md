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

# RG-701 FastAPI → Django + DRF 전환 구현 — 2026-10-20

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx RG-701 상세]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록|백로그 등록·담당 배정 기록]]

> [!WARNING] 진행 중 · 증거 대기
> 구현 착수 시점의 근거와 계획을 기록한다. 구현 완료·전환 후 테스트 통과·TEST 배포·롤백 확인은 **아직 증거가 전달되지 않았고 확인되지 않았다.** Root(Codex)의 최종 실제 증거를 받은 뒤 갱신한다.

저장소 기록: `docs/work-log/2026-10-20-rg701-django-drf-migration.md` (main-2 워크트리)

## 요약

- 작업 ID: RG-701 (7xx 배포·인프라), 우선순위 1 (최우선, 변경 없음)
- 상태: 계획 (미착수) → **진행 중** (2026-10-20 구현 착수). 완료 아님.
- 착수 근거: 사용자가 Orca 코디네이터를 통해 구현 진행을 승인("그렇게 진행해줘").
- 승인 범위: 구현·검증·TEST 배포까지. Production·운영 컨테이너·운영 DB 변경은 별도 명시 승인 전 수행하지 않는다. commit/push는 이번 지시 범위 밖.

## 요청 배경과 목표

- 2026-10-20 RG-701을 최우선·계획 상태로 등록하고 담당을 사전 배정한 뒤, 사용자가 구현 진행을 승인했다.
- 목표(백로그 정의 유지): 기존 공개·내부 API URL과 요청·응답·오류 계약을 유지한 채 웹 계층을 Django + DRF로 전환한다. 조류 근거·데이터와 Neo4j 검색을 재사용하고 프레임워크 독립 서비스 계층을 만든다. 성능 향상은 약속하지 않는다.

## 역할 분담

| 역할 | 에이전트 | 모델 | 워크트리 | 담당 |
|---|---|---|---|---|
| 총괄·통합 (Root) | Codex | 현재 세션 모델 그대로(재설정 없음) | dev-codex | `django_api/settings.py`·`asgi.py`, CLI, 의존성, 인프라, 통합 검증·TEST 배포 |
| 구현 | Claude | `claude-opus-5-5` (계획) | dev-claude | 네이티브 DRF View·Serializer·URL, 서비스 추출 |
| UI 호환 | Codex | `gpt-6.1-sol` (계획) | main (dev-agy) | 정적 UI·API 소비 HTTP 호환 검사 |
| 문서 | Claude | `claude-opus-5-5` | main-2 (dev) | 저장소 기록·Obsidian 단독 쓰기·백로그 |

- UI 담당 세션은 모델 업데이트 프롬프트가 건너뛰어져 같은 터미널에서 재시도 중이라는 코디네이터 전달이 있었다. 실제 실행 모델은 문서 담당이 확인하지 않았다.

## 확인한 근거

### 착수 전 기준선 (Root 실행 · 변경 전)

| 항목 | 값 |
|---|---|
| 명령 | `uv run --locked --extra test python -m unittest discover -s tests -q` |
| 결과 | 999 실행 · 961 통과 · 38 건너뜀 · 0 실패 |
| 소요 | 23.058초 |
| 종류 | 오프라인/모의/fixture. 실제 DB opt-in 통합 검사는 건너뜀 |

- dev-codex `docs/verification/assets/2026-10-20-rg701/baseline-tests.json`과 값이 일치함을 읽기 전용으로 확인했다. 문서 담당은 재실행하지 않았다. 실제 Neo4j/PostgreSQL 검증이 아니다.
- 설치 의존성(Root 전달): Django 5.2.18, DRF 3.16.1. `pyproject.toml`에 `django>=5.2,<5.3`, `djangorestframework>=3.16,<3.17` 추가(작업 트리 diff). FastAPI 의존성은 관찰 시점에 아직 남아 있다.

### 진행 중 관찰 (dev-codex 작업 트리 · 읽기 전용 · 미커밋)

동작·통과를 뜻하지 않으며 최종 diff와 다를 수 있다.

- `src/robingraph/django_api/settings.py`(신규): stateless 설정 — `INSTALLED_APPS=['rest_framework']`, `MIDDLEWARE=[]`, `DATABASES={}`, `APPEND_SLASH=False`, DRF 인증 없음·`AllowAny`·JSON 렌더러/파서. 주석에 기존 ingest SQL이 스키마 소유권을 유지하고 auth/admin/session 테이블을 설치하지 않는다고 명시. 비밀값은 환경 변수(`ROBINGRAPH_DJANGO_SECRET_KEY`)에서 읽음.
- `src/robingraph/django_api/asgi.py`(신규): `robingraph.api.drf`의 `create_django_app()`을 가져온다. 네이티브 DRF factory는 구현 담당의 `api/drf`에 속하고 `django_api`에는 설정·ASGI 진입점만 둔다.
- `src/robingraph/cli.py`: `serve-fixture`·`serve-ingest`·`serve-neo4j`가 Django ASGI 앱을 uvicorn으로 실행하도록 변경.
- `Dockerfile`: 빌드 시 `python -m django check --settings=robingraph.django_api.settings` 추가.
- `Jenkinsfile`·`ci/Jenkinsfile.production` 수정 상태는 RG-701 관련 여부 미확인.

### Root 중간 증거 (2026-10-20 06:40 UTC · 최종 아님)

Root 보고 값이며 문서 담당은 재실행하지 않았다.

- Django 5.2.18·DRF 3.16.1을 `pyproject.toml`·`uv.lock`에 추가. stateless `settings`·`asgi`, auth/admin/session 미설치, `DATABASES={}`, Django 마이그레이션 없음(기존 PG SQL과 분리).
- CLI `serve-fixture`·`serve-neo4j`·`serve-ingest` → 네이티브 `robingraph.api.drf.create_django_app`.
- Claude: `schemas.py`·`services.py`·`ingest_service.py` 추출·얇은 legacy 어댑터, 네이티브 `api/drf` View·factory 작성 중.
- 기존 FastAPI는 차등 비교 기준으로만 유지, 런타임 FastAPI 프록시 없음. Docker·Jenkins에 `django check` 단계.
- 테스트: 기준선 999/961/38/0(오프라인). Root 런타임 설정/CLI 2개 통과(0.025초). UI Node 317개 통과. UI HTTP 95사례 비교 도우미 준비, Django 대상 미실행.
- TEST 배포 없음. 변경 전 공개 OpenAPI 스냅샷 `docs/verification/assets/2026-10-20-rg701/openapi-before.json` 존재.
- TEST 배포 전 읽기 전용 DB 스냅샷 `db-before.json`: 실제 이름 벡터 855개, 파일럿 수집 실행 1건(succeeded), 이름 카탈로그 fingerprint·기타 파이프라인 상태 해시. 전환 후 비교 결과는 증거 대기.
- 문서 범위: README 현재 런타임 문장은 Root 담당. `deployment-profile.md`의 과거 FastAPI 제안은 유지하고 검증된 배포 후 날짜 붙인 전환 메모를 추가한다.

### 배포 전 독립 검토 (2026-10-20 06:52 UTC · 최종 아님)

검토자 `gpt-6.1-sol` 보고(문서 담당 재실행 없음, mock/fake 기반, 공유 DB 문제 아님).

- 네이티브 legacy 스위트 242 실행·1 건너뜀·0 실패. DTO 33개 AST 동일. 네이티브 import에 FastAPI 없음. 150ms 모의 호출 4건 164ms(병렬), 앱 2개 handler 격리.
- 발견 1: Django 기본 2.5MiB 상한으로 정상 3MB ingest가 기존 200 → 새 400. 조치: `DATA_UPLOAD_MAX_MEMORY_SIZE=None`(Root), mock 회귀 테스트(Claude) 진행 중.
- 발견 2: 허용되지 않은 Host 응답 200/500 불일치. 조치: 초기 `get_host()` 검증 → 400과 테스트(Claude) 진행 중.
- 발견 3: Root 런타임 테스트의 `DATABASES == {}` 순서 문제 → dummy backend 단언으로 수정.
- 재검증·TEST 배포는 증거 대기.

### HTTP 동등성 비교 (2026-10-20 06:53 UTC · 중간)

- 자산 `docs/verification/assets/2026-10-20-rg701/http-parity-overlay.json`. 기존 FastAPI(18011) vs 새 네이티브 Django(18012), 같은 fixture, 로컬 실제 소켓 95사례.
- 전체 JSON(`error: null` 포함)·바이트·MIME·cache·location·traversal 비교 → Root 보고 **95/95 일치**.
- 한계: 로컬 fixture HTTP, 실제 DB·브라우저·최종 통합 이미지 아님. 소스 수정 시 최종 통합 후 재실행.

## 계약과 변경 전후

- 유지 대상: `POST /v1/answers`, `/v1/chat`, `/v1/search`, `GET /v1/observations`, `/v1/taxa/lineage`, `/v1/taxa/{name-relations,related,similar,ecological-related,subspecies,profile}`, `/health`, 정적 `/`·`/chat`·`/birds`·`/favicon.ico`·`/static/...`, 내부 `/internal/v1/ingest/*`(내부 Bearer).
- 전: FastAPI/Pydantic 앱을 uvicorn으로 실행. 후(진행 중): Django + DRF ASGI 앱. 실제 계약 일치: **증거 대기**.

## 변경 파일

- 문서 담당: 저장소 `docs/work-log/2026-10-20-rg701-django-drf-migration.md`(신규); Obsidian 전체 백로그·7xx 백로그·이 노트·작업기록 index.
- 구현 변경 파일(Root·구현 담당): **증거 대기**.

## 검증 결과

| 구분 | 상태 |
|---|---|
| 기준선 단위/모의/fixture (변경 전) | 999 실행·961 통과·38 건너뜀·0 실패 |
| Root 런타임 설정/CLI (중간) | 2개 통과 (0.025초) |
| UI Node (중간) | 317개 통과 |
| 전환 후 전체 단위/모의/fixture | 증거 대기 |
| DRF 계약 테스트 | 증거 대기 |
| 실제 DB/API 통합 | 증거 대기 |
| HTTP 동등성 95사례 (중간) | 95/95 일치 (로컬 fixture, 실제 DB·브라우저 아님) |
| UI 호환 (main) 최종 | 증거 대기 |
| n8n ingest 호환 | 증거 대기 |
| TEST 배포 (M4 16GB Mac) | 증거 대기 |
| 롤백 계획·확인 | 증거 대기 |
| Production | 해당 없음 (별도 승인 전 수행 안 함) |

## 배포·커밋

- 확인된 배포 없음. commit/push 없음.

## 남은 한계와 후속

- 최종 diff·전환 후 테스트·실제 DB/API·UI 호환·n8n·TEST 배포·롤백 증거를 받아 갱신한다. mock/fixture와 실제 결과를 분리해 기록한다.
- 백로그 완료 기준 전체를 충족하기 전에는 완료로 옮기지 않는다.

## Obsidian 재조회

초기 단계(2026-10-20) 저장 후 MCP로 다시 읽어 확인했다.

- 전체 백로그(463 → 475줄): 목차에 `진행 중 작업`, 7xx 작업기록 수 `15`, 카테고리별 보기 701 `진행 중 (최우선 1 · 2026-10-20 구현 착수)`, 현황 대시보드 `RG-701 | 진행 중 | 1 (최우선)`, 신규 `## 진행 중 작업` 구역, 대기 표 RG-701 담당 칸 보존, RG-701 안내 절의 구현 착수 문단, 변경 이력 최상단 항목. RG-406(`… 운영 배포 대기 | 5`)·RG-101(`보류 …`) 행과 기존 등록·배정 이력은 원문 그대로.
- 7xx 백로그(93 → 95줄): 작업 현황 첫 항목, RG-701 상태 `진행 중 …`(우선순위 1·담당 배정 표 불변), 결과 기록에 구현 노트 링크, 작업기록 목록 첫 링크.
- 작업기록 index: 7xx `15`.
- 이 노트 생성 확인(108줄). 링크 앵커는 텍스트 대조만 했고 Obsidian 화면 클릭 검증은 하지 않았다.
