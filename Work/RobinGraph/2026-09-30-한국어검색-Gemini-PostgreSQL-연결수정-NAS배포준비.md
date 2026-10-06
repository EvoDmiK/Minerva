---
date: 2026-09-30
project: RobinGraph
type: development-log
status: pushed
branch: dev
commit: f3b77e5
tags:
  - project/robingraph
  - development
  - graphrag
  - gemini
  - postgresql
  - nas
updated: 2026-10-05
---

# RobinGraph — 한국어 검색·Gemini·PostgreSQL 연결 수정·NAS 배포 준비

## 오늘의 결과

한국어 질문으로 영어 PMC 문헌을 검색하고, 인용이 포함된 한국어 답변을 받도록 개선했다. PostgreSQL 접속 실패는 기존 내부망 주소를 Tailscale 주소로 바꿔 해결했다. 실제 데이터로 대륙검은지빠귀 분류 조회를 확인했고, Docker에서도 DB 조회와 Gemini 응답을 검증했다.

마지막으로 수정사항을 사용자 Git 작성자 정보로 커밋하고 `origin/dev`에 push했다. **NAS에서 직접 실행한 상태는 아니다. NAS에서 pull한 뒤 사용자가 배포하기로 했다.**

| 항목 | 상태 |
|---|---|
| 한국어 fulltext 문헌 검색 개선 | 구현·실제 API 검증 완료 |
| Gemini 한국어 답변·근거 인용 | TEST 모델로 검증 완료 |
| PostgreSQL 연결 | 주소 수정 후 연결 정상 |
| 대륙검은지빠귀 분류 조회 | HTTP 200·학명 검증 완료 |
| NAS용 Docker 이미지 | 빌드·컨테이너 실행 검증 완료 |
| Git 커밋·push | `f3b77e5` → `origin/dev` |
| 실제 NAS 배포 | 사용자 pull·배포 대기 |

전날 기록: [[2026-09-29-CI-수정-Gemini-연동-PMC-문헌파일럿]]

## 1. 한국어 질문이 영어 문헌을 찾지 못하는 문제

### 원인 확인

PMC9946348 한 편이 들어 있는 TEST Neo4j에서 같은 뜻의 한국어·영어 질문 5쌍을 비교했다.

- 영어 질문은 모두 PMC 검색 결과 3개를 찾았다.
- 한국어 질문은 4개에서 결과가 없었다.
- 철새·물새 질문은 PMC 대신 합성 fixture 결과 2개를 반환했다.
- 기존 fulltext 조회는 한국어 질문을 영어 문헌 본문과 그대로 비교하고 있었다.

### 구현

기존 Gemini 어댑터를 재사용해 한국어 질문에 담긴 개념을 영어 검색어로 바꾸고, 원래 질문 뒤에 붙였다. 패키지는 추가하지 않았다.

```python
# src/robingraph/api/app.py — 핵심 흐름 발췌
search_question = question
if not hybrid and english_search_terms is not None and any(
    "\uac00" <= char <= "\ud7a3" for char in question
):
    terms = english_search_terms(question)
    search_question = f"{question} {terms}"
```

- 한국어 fulltext 요청에만 적용한다.
- 영어 질문과 auto/hybrid 경로에는 추가 번역 호출을 넣지 않는다.
- 검색어 변환 실패 시 원래 질문으로 조회하고 경고를 반환한다.
- 기존 Lucene 검색어 이스케이프를 유지한다.
- `조류`가 algae/tides로 번역되지 않도록 bird ecology 문맥을 명시한다.
- 질문에 없는 사실이나 관련 개념을 덧붙이지 않도록 요청한다.

Gemini 출력도 입력 경계에서 검사한다.

```python
# src/robingraph/generation.py — 출력 검증 발췌
terms = _extract_payload(document).get("terms")
if not isinstance(terms, str) or not re.fullmatch(
    r"[A-Za-z0-9][A-Za-z0-9 '\-]{0,299}", terms
):
    raise GeminiAnswerError("Invalid English search terms")
if len(terms.split()) > 20:
    raise GeminiAnswerError("Too many English search terms")
```

검색어는 최대 20단어·300자, 입력 질문은 최대 2,000자로 제한한다. 답변 생성 프롬프트에도 질문과 같은 언어로 답하도록 명시했다.

### Gemini 503 대응

실제 API 호출에서 `gemini-3.8-flash`의 HTTP 503이 반복됐다. 기존 요청 함수에 **1초 뒤 한 번만 재시도**하는 처리를 추가했다.

```python
# src/robingraph/generation.py — 503 처리 발췌
if exc.code == 503 and attempt == 0:
    time.sleep(1)
    continue
raise GeminiAnswerError(f"Gemini HTTP error {exc.code}") from None
```

계속 실패하면 기존 검색·생성 fallback을 사용한다. 오류 로그에는 예외 종류만 남기고 API 키나 제공자 오류 본문은 노출하지 않는다.

### 실제 질문 검증

TEST 서버에서는 지원 여부를 확인한 `gemini-3.5-flash-lite`를 환경 변수로 지정했다. 코드 및 루트 `.env`의 기본 모델은 변경하지 않았다. NAS용 `.env.nas.test`에는 검증 모델을 지정했다.

| 질문 | 결과 | 응답 시간 |
|---|---|---:|
| 로스앤젤레스 기후·토지 이용 변화와 조류 다양성 | 한국어 답변·PMC 인용 | 3.08초 |
| 로스앤젤레스와 센트럴밸리 차이 | 감소·상대적 안정 설명 | 3.03초 |
| 기후와 토지 이용의 반대 영향 | 상쇄 영향 설명 | 2.84초 |
| 과거 조사와 최근 조사 비교 | 역사적 야장·지점 설명 | 2.42초 |
| 철새·물새 적용 가능 여부 | 현재 근거로 확인 불가라고 응답 | 2.75초 |

인용 ID가 실제 검색 결과에 속하고 PMC URL·문단 위치·CC BY 4.0 표기가 있는지 확인했다.

> [!warning] 남은 검색 문제
> 철새·물새 질문에서 중요한 연구 한계 문단 `p017`을 놓쳤다. 인용이 연결된 한국어 응답을 받았다는 사실이 검색 완전성이나 모든 주장 정확성을 보증하지는 않는다. 실험은 PMC 문헌 한 편으로 수행했다.

한국어 fulltext 요청에는 검색어 변환 호출이 한 번 추가되어 지연과 비용이 늘어난다.

## 2. GraphDB에 새가 없는 것처럼 보이는 문제 확인

AviList 분류는 이미 대규모로 적재되어 있었다. 곧바로 수집 워크플로를 추가하기보다 기존 데이터와 활성 설정을 확인했다.

| AviList 분류 단계 | 적재 수 |
|---|---:|
| 목 | 46 |
| 과 | 252 |
| 속 | 2,376 |
| 종 | 11,131 |
| 아종 | 19,879 |
| 합계 | 33,684 |

이 수치는 AviList 개념 집합 기준이다. 별도 fixture 분류 10개가 추가로 존재한다. 한국어 이름 노드는 2,548개이며 여러 Wikidata 스냅샷에 걸쳐 있다.

대륙검은지빠귀 데이터도 실제로 존재했다.

```text
대륙검은지빠귀
학명: Turdus mandarinus
영명: Chinese Blackbird
계보: Passeriformes → Turdidae → Turdus → Turdus mandarinus
AviList 개념 집합: rg:concept-set:avilist-v2025b
```

한국어 이름은 Wikidata에서 가져온 커뮤니티 기반 이름이며 공식 이름 인증을 의미하지 않는다. 여러 스냅샷이 있어도 API는 PostgreSQL에 지정된 활성 데이터셋을 기준으로 조회한다.

**오늘 n8n의 새 수집 워크플로를 추가하거나 활성화하지는 않았다.** 우선 API가 기존 데이터를 정상 조회하도록 PostgreSQL 연결부터 해결했다.

## 3. PostgreSQL 연결 실패 해결

### 원인

프로젝트 루트 `.env`는 접속되지 않는 내부망 주소를 사용했다.

```text
기존: 192.168.219.99:5433
오류: No route to host
```

반면 기존 테스트 자격정보 파일 `~/.config/robingraph/test-postgres.env`에는 연결 가능한 Tailscale 주소가 들어 있었다. 두 설정의 DB 이름·사용자·비밀번호가 같음을 값 노출 없이 확인했다.

### 수정

`.env`에서 주소 한 줄만 변경했다.

```dotenv
ROBINGRAPH_PG_HOST=100.93.181.111
ROBINGRAPH_PG_PORT=5433
ROBINGRAPH_PG_DATABASE=robingraph_test
ROBINGRAPH_PG_SCHEMA=ingest
ROBINGRAPH_PG_SSLMODE=prefer
```

기존 DB와 자격정보를 재사용했다. 새 PostgreSQL을 만들거나 마이그레이션·데이터 적재를 수행하지 않았다.

### 읽기 전용 확인

- `robingraph_test` 접속 성공.
- 필수 테이블 7개 존재: `ingest_state`, `ingestion_run`, `outbox_event`, `quarantine_item`, `source_dataset`, `source_record`, `source_release`.
- `reference-taxonomy-traits` 활성 상태 정상.
- 활성 AviList 분류 버전: `v2025b`.
- `korean-vernacular-names` 활성 상태 정상.

현재 코드로 띄운 8002 서버를 재시작한 뒤 대륙검은지빠귀 조회가 HTTP 200을 반환하고 `Turdus mandarinus`로 해석되는지 검증했다.

## 4. NAS 배포 준비와 Docker 검증

기존 `Dockerfile`, `compose.nas.yml`, `scripts/deploy_nas.sh`를 재사용했다. 새로운 배포 체계를 추가하지 않았다.

준비한 파일 및 설정:

- `.env.nas.test`: 실제 테스트 DB와 Gemini 설정, 파일 권한 `0600`, Git 제외.
- 실행 모드: `serve-neo4j`.
- TEST 전용 이미지: `robingraph-api:test-20260930`.
- Gemini 모델: `gemini-3.5-flash-lite`.
- PostgreSQL: `100.93.181.111:5433` / `robingraph_test`.

로컬 Docker 이미지 빌드가 성공했다. NAS와 같은 읽기 전용 파일시스템·비루트 사용자·capability 제거 조건으로 임시 컨테이너를 실행했다.

### 컨테이너에서 확인한 내용

- `/health`: HTTP 200.
- OpenAPI·응답 계약 일치.
- 대륙검은지빠귀 계보: HTTP 200, `Turdus mandarinus`.
- 활성 계보 분류 버전: `v2025b`.
- `/v1/chat`: HTTP 200, 한국어 답변과 PMC 근거 인용.
- 검증 완료 후 임시 컨테이너 종료.

예시 채팅 응답은 기후와 토지 이용의 복합 영향이 지역별로 다르다는 설명과 `pmc-pilot:PMC9946348:p019` 인용을 반환했다.

> [!note] health의 분류 버전
> `/health`의 `fixture-avlist-2025`는 프로세스의 fixture 코퍼스 버전이다. 계보 API의 `v2025b`는 활성 AviList 참조 분류 버전이다. 두 값은 서로 다른 데이터 영역을 나타낸다.

처음에는 수동 이전용 소스 묶음도 만들고 체크섬·비밀값 제외·최신 소스 일치를 검증했다. 이후 사용자가 **Git push → NAS pull 배포** 방식을 선택해 최종 안내를 해당 방식으로 변경했다.

NAS Tailscale SSH 경로에서 기존 호스트 키 검증은 진행할 수 있었으나 사용자 인증이 거부됐다. 따라서 NAS 설치·실행 성공을 주장하지 않는다.

## 5. 테스트와 Git 반영

- 전체 Python 테스트: 420개 실행, 통과, 31개 건너뜀.
- NAS 관련 테스트: 47개 통과.
- `git diff --check`: 통과.
- `graphify update .`: AST 기반 그래프 갱신.
- Docker 이미지 빌드와 실제 DB·Gemini API 검증 완료.
- 최종 push 후 작업 트리는 깨끗하고 로컬·원격 `dev` 차이는 0이다.

### 수정한 파일

| 파일 | 변경 |
|---|---|
| `src/robingraph/generation.py` | 영어 검색어 추출·검증, 공통 JSON 추출, 503 재시도, 답변 언어 지정 |
| `src/robingraph/api/app.py` | 한국어 fulltext 검색어 확장·실패 fallback·경고 |
| `src/robingraph/cli.py` | 검색 핸들러와 Gemini 검색어 변환 연결 |
| `tests/test_api.py` | 한국어 확장·실패·영어/hybrid 경로 검증 |
| `tests/test_gemini_generation.py` | 출력 경계·503 재시도 상한 검증 |
| `tests/test_semantic_chat.py` | 변경된 Gemini 어댑터 테스트 대응 |
| `docs/chat-ui.md` | 검색 변환 동작·비용·재시도 문서화 |
| `docs/nas-deployment.md` | 검증된 TEST 설정·Git pull 배포·실데이터 검증 안내 |
| `docs/work-log/2026-09-30-korean-pmc-api-verification.md` | 질문별 결과와 남은 한계 기록 |

`.env` 주소 수정과 `.env.nas.test`의 실제 키·비밀번호는 Git에 포함하지 않았다.

- 브랜치: `dev`.
- 커밋: `f3b77e5`.
- 메시지: `Improve Korean literature search and document NAS test deployment`.
- 작성자: Dove. J. Kim.
- 원격: `origin/dev`.
- [커밋 확인](https://github.com/EvoDmiK/RobinGraph/commit/f3b77e5).

## 6. NAS에서 이어서 할 일

NAS 저장소에서 먼저 최신 코드를 받는다.

```sh
git switch dev
git pull --ff-only origin dev
```

NAS의 `.env.nas.test`는 별도 설정이 필요하다. 파일이 없을 때만 아래 템플릿 복사를 실행한다.

```sh
cp .env.nas.example .env.nas.test
chmod 600 .env.nas.test
```

파일에 TEST Neo4j·PostgreSQL 자격정보와 Gemini API 키를 입력하고 다음 값을 확인한다.

```dotenv
ROBINGRAPH_API_MODE=serve-neo4j
ROBINGRAPH_IMAGE=robingraph-api:test-20260930
ROBINGRAPH_PG_HOST=100.93.181.111
ROBINGRAPH_PG_PORT=5433
ROBINGRAPH_PG_DATABASE=robingraph_test
ROBINGRAPH_GEMINI_MODEL=gemini-3.5-flash-lite
```

`robingraph-edge` 네트워크가 필요하며 NAS 컨테이너에서 TEST Neo4j와 PostgreSQL 주소에 접속할 수 있어야 한다.

```sh
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh preflight
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh deploy
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh verify

docker exec robingraph-api-test python scripts/verify_api_deployment.py \
  --base-url http://127.0.0.1:8000 \
  --lineage-name 대륙검은지빠귀 \
  --expected-scientific-name 'Turdus mandarinus' --json
```

마지막 결과에서 `passed: true`를 확인한다. TEST 화면을 공개하려면 NPM의 별도 테스트 호스트를 `http://robingraph-api-test:8000`으로 연결한다.

### 이후 개발 과제

- [ ] NAS에서 TEST 배포·분류·한국어 채팅 확인.
- [ ] 연구 한계 문단을 놓치는 검색 문제와 합성/실제 문헌 혼합 평가.
- [ ] 허용된 논문 몇 편으로 코퍼스를 확대하고 여러 출처 인용 평가.
- [ ] 필요한 분류·한국어 이름 갱신 범위를 정한 뒤 기존 n8n 수집 경로 검토.

## 관련

- [[Work/index|Work — 토이 프로젝트]]
- [[2026-09-29-CI-수정-Gemini-연동-PMC-문헌파일럿]]

## 상세 보완 — 2026-10-05

### 한국어 문헌 검색과 종 이름 조회의 차이

한국어 문헌 질문을 영어 검색어로 확장하는 기능은 문헌의 검색어 불일치를 줄이는 경로다. 한국어 종 이름을 활성 분류군에 연결하는 조회와는 다르다. 문헌을 찾지 못한 결과가 곧 해당 종이 그래프에 없다는 뜻은 아니다.

| 요청 | 핵심 확인 |
|---|---|
| 한국어 문헌 질문 | 실제 전문 검색 입력에 확장 검색어가 전달되는가 |
| 한국어 종 조회 | 활성 한국어 이름 자료와 정확한 대상 taxon이 연결되는가 |
| 학명 조회 | 활성 개념집합·분류 릴리스의 정확한 이름이 있는가 |
| 관찰 조회 | 별도 관찰 자료 영역의 검색 조건과 접근 정책이 맞는가 |

영어 검색어 확장은 생성 모델의 결과를 검증한 뒤 검색 입력으로 사용한다. 잘못된 출력·호출 오류는 원래 질문으로 검색을 계속하는 경로와 구분해 기록한다.

### 연결 문제를 확인한 범위

당시 PostgreSQL 주소 변경과 Docker 검증은 클라이언트에서 실제 DB에 접근해 종 조회가 성공하는지 확인한 결과다. 비밀번호가 설정된 사실만 확인한 것이 아니다. 호스트 실행과 컨테이너 실행은 네트워크 경로가 다르므로 각각 확인했다.

### 이후 배포 상태

원문에 있는 ‘NAS 배포 대기’는 이 기록을 작성한 시점의 상태다. 이어진 [[Work/RobinGraph/2026-09-30-NAS-Git이력분기-구형이미지-Gemini검색복구-525진단|NAS 복구·실제 배포 기록]]에서 TEST 이미지 재빌드와 내부·공용 도메인 검증이 완료되었다. 이 문서의 당시 결과를 실제 NAS 배포 완료로 소급해서 바꾸지 않는다.

현재는 [[Work/RobinGraph/2026-10-05-RG003-생태관계탐색-NAS배포|RG-003 생태 관계 탐색·NAS TEST 검증]]의 별도 TEST 릴리스가 최신 작업 기록이며, PROD 종 데이터 준비는 [[Work/RobinGraph/RobinGraph 작업 백로그|작업 백로그]]의 RG-002로 남아 있다.
