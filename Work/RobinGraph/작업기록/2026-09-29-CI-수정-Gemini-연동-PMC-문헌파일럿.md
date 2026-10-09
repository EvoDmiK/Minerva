---
created: 2026-09-29
updated: 2026-10-05
tags:
  - project/robingraph
  - dev
  - gemini
  - literature
status: in-progress
---

# RobinGraph — CI 테스트 수정, Gemini 근거 답변 연동, PMC 문헌 파일럿 (2026-09-29)

## 오늘 한 일

- Git 작업 상태와 커밋 작성자 정보를 정리했다. 현재 `dev`는 `origin/dev`와 일치하고 작업 트리는 깨끗하다.
- Ponytail 원칙으로 구현 범위를 좁히고, Claude 작업자 두 명에게 Gemini 호출 모듈과 `/v1/chat` 연결을 나누어 맡긴 뒤 통합 결과를 검토했다.
- `GEMINI_API_KEY`가 있을 때만 `serve-neo4j`의 문헌 근거 경로에서 Gemini 답변을 생성하도록 연결했다. 모델 기본값은 `gemini-3.8-flash`이며 `ROBINGRAPH_GEMINI_MODEL`로 바꿀 수 있다.
- 생성 응답의 근거 ID가 실제 검색 청크에 있는지 확인한다. 근거가 없거나 생성·검증이 실패하면 근거 없는 답변을 표시하지 않고 기존 검색 결과를 유지한다.
- CI의 기존 ingest/Windows 계약 테스트를 현재 구현에 맞게 정리했다.
- TEST Neo4j에 CC BY 4.0 PMC 논문 1편을 실험용으로 적재하고, 실제 검색과 Gemini 답변까지 확인했다.

## CI 테스트 수정

- `tests/test_n8n_workflows.py`: 한국어 일반명 통합 테스트에서 이전 `start/finalize` 절차를 제거하고 현재의 배치 적재 계약을 사용했다. 같은 배치를 다시 실행해도 이름 노드가 중복되지 않는지, 새 스냅샷에서 이전 이름이 비활성화되는지, 동명이인을 잘못 매칭하지 않는지 확인한다. 테스트가 공유 `IngestState`를 임시로 바꾸던 과정도 없앴다.
- 같은 파일의 GBIF 관찰 테스트는 현재 입력 계약에 맞춰 `dataset_id`와 허용된 CC-BY 라이선스를 제공하고, 이전 결과 필드 대신 `domain_verified` 상태를 확인하도록 고쳤다.
- `tests/test_nas_deploy_lifecycle.py`: Windows에는 Unix 실행 비트가 없으므로 해당 검사만 제외했다. TEST/PROD 환경 파일 경로 검사도 OS별 절대경로 차이에 영향을 받지 않도록 조정했다.

### CI 변경 스니펫

한국어 일반명 테스트는 전역 `IngestState`를 임시 변경하지 않고, 배치 재실행과 활성 데이터셋 전환을 직접 확인한다.

```python
write_batch(run_1, dataset_1, "release-1", rows_v1)
write_batch(run_1, dataset_1, "release-1", rows_v1)  # 재실행해도 중복 없음
active_dataset = [dataset_2]
# 조회 저장소에 현재 활성 데이터셋과 taxonomy context를 명시적으로 전달
lambda: active_dataset[0]
lambda: (concept_set_id, marker)
```

Windows에서는 존재하지 않는 Unix 실행 비트를 검사하지 않는다. 환경 파일 경로는 OS별 절대경로 대신 `.env.nas.test` / `.env.nas.prod` 접미사를 검사한다.

```python
if os.name != "nt":
    mode = script.stat().st_mode
    self.assertTrue(mode & stat.S_IXUSR)
self.assertRegex(calls, rf"--env-file \S*\.env\.nas\.{target}(?=\s)")
```

## Gemini 연동 세부 내용

- `generation.py`는 표준 라이브러리로 Gemini REST API를 호출하고, 검색된 청크의 본문과 출처 정보만 전달한다. API 오류 내용이나 키는 사용자 응답에 노출하지 않는다.
- `/v1/chat`의 문헌 근거 경로에서만 생성기를 호출한다. 근거가 없으면 답변을 보류하고, 모델 호출 실패·빈 답변·중복되거나 검색 결과에 없는 근거 ID는 생성 답변을 사용하지 않는다. 분류·관찰 경로는 그대로 유지한다.
- `cli.py`는 `GEMINI_API_KEY`가 있을 때만 생성기를 연결한다. `.env.example`, `.env.nas.example`, README와 채팅 UI 설명도 실제 동작에 맞게 갱신했다.

### 요청과 응답 검증 스니펫

`GEMINI_API_KEY`가 있을 때만 생성기를 연결한다. 검색 결과가 없으면 Gemini를 호출하지 않는다.

```python
gemini_api_key = os.getenv("GEMINI_API_KEY")
answer_generator = None
if gemini_api_key:
    answer_generator = GeminiAnswerer(
        gemini_api_key,
        os.getenv("ROBINGRAPH_GEMINI_MODEL", "gemini-3.8-flash"),
    )
```

요청은 검색 청크를 신뢰할 수 없는 자료로 표시하고, 답변 본문과 인용할 청크 ID를 JSON으로 받는다. 실제 API 호출로 확인한 설정은 다음과 같다.

```python
"generationConfig": {
    "responseMimeType": "application/json",
    "responseSchema": {
        "type": "OBJECT",
        "properties": {
            "text": {"type": "STRING"},
            "evidence_ids": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["text", "evidence_ids"],
    },
}
```

모델이 반환한 ID는 다시 서버에서 검사한다. 중복 ID, 검색하지 않은 ID, 빈 본문은 버리고 `근거 문서를 확인했습니다.`와 검색 결과를 반환한다.

```python
retrieved_ids = {result.chunk_id for result in results}
if len(set(evidence_ids)) != len(evidence_ids):
    return None
if not set(evidence_ids) <= retrieved_ids:
    return None
if not isinstance(answer_text, str) or not answer_text.strip():
    return None
return f"{answer_text} [{', '.join(evidence_ids)}]"
```

## 검증

- Python 전체 테스트: **415개 실행, 통과** (환경 의존 테스트 31개 건너뜀). 프런트엔드 테스트: **37개 통과**.
- 실제 Gemini API 호출에서 JSON 답변과 요청에 포함한 근거 ID를 받았다. 이 과정에서 `responseFormat` 요청이 HTTP 400을 반환하는 것을 확인하고, 실제로 동작하는 `responseMimeType`/`responseSchema` 형식으로 수정했다.
- TEST Neo4j에 합성 fixture **분류군 10개, 관찰 100건, 문서 2개, 청크 4개**를 적재하고 전문 검색 인덱스를 생성했다. fixture 검증에서 비공개 좌표와 제한 관찰 노출은 모두 0건이었다.
- 실제 Neo4j 검색 + Gemini를 잇는 `POST /v1/chat` 요청이 **HTTP 200**을 반환했다. 검색 근거 3개를 받았고, 생성 답변의 근거 ID가 검색 결과에 포함됐다.

## 재현 명령과 테스트 범위

```sh
uv run --locked python -m unittest discover -s tests -q
node --test tests/frontend/chat_ui.test.js
uv run --locked robingraph load-neo4j-fixture
uv run --locked robingraph index-neo4j-fixture
uv run --locked robingraph verify-neo4j-fixture
```

마지막 통합 확인은 실행 중인 배포 서버 대신 FastAPI `TestClient`에 **실제 TEST Neo4j 검색 핸들러와 실제 Gemini 생성기**를 연결해 수행했다. 요청 본문은 아래와 같고, `limit`은 최상위 필드가 아니라 `filters`에 넣는다.

```json
{
  "question": "fixture 호수",
  "intent": "evidence",
  "filters": {"kind": "evidence", "limit": 3}
}
```

결과: HTTP 200, `disposition: answer`, Neo4j 검색 근거 3개, 생성 답변에 검색된 청크 ID 인용. 이 검증에서는 전문 검색만 사용했고 Jina 벡터 검색이나 운영 배포 서버는 시험하지 않았다.

## PMC 실제 문헌 파일럿

### 수집 대상과 선택 이유

- 논문: *Concordant and opposing effects of climate and land-use change on avian assemblages in California’s most transformed landscapes* (PMC9946348, DOI `10.1126/sciadv.abn0250`).
- [PMC 원문](https://pmc.ncbi.nlm.nih.gov/articles/PMC9946348/)의 CC BY 4.0 문헌 한 편만 `config/source-registry.json`에 허용 대상으로 등록했다. PMC 전체를 일괄 수집하는 설정은 아니다.
- 처음 시도한 BioC 요청은 실제 적재 전에 HTTP 429를 받아, 논문 메타데이터와 본문을 한 번에 받는 [PMC OAI-PMH GetRecord](https://pmc.ncbi.nlm.nih.gov/tools/oai/) JATS XML 경로로 바꿨다.

### 구현

- `scripts/load_pmc_pilot.py`는 기본 실행 시 파싱 결과만 출력하는 dry run이다. `--apply`를 붙이면 TEST Neo4j에 기록한다. 새 패키지 없이 Python 표준 라이브러리와 기존 Neo4j 드라이버를 사용했다.
- XML의 `article-meta`에서 PMCID, DOI, 제목, CC BY 4.0 표시를 확인한 뒤 초록과 본문의 문단을 청크로 만든다. 그림·표·보충자료·참고문헌은 제외한다. OAI 응답 시각을 제외한 논문 XML에 SHA-256을 계산해 같은 원문인지 확인한다.
- Document → Chunk → EvidenceUnit와 SourceRecord/SourceDataset/License 출처 관계를 생성했다. 노드에 `PmcPilot`·`Fixture` 라벨을 붙여 파일럿을 구별하고, 청크에는 `HybridSearchChunk`를 붙여 기존 전문 검색에 연결했다. 임베딩은 생성하지 않았다.
- 다시 실행하면 이전 `PmcPilot` 노드만 교체한다. `load-neo4j-fixture`를 다시 실행하면 이 실험 데이터도 지워질 수 있다.

라이선스와 논문 ID 확인, 문단 제외 규칙의 핵심 부분:

```python
if not any(LICENSE_URI in statement for statement in license_statements):
    raise ValueError("PMC article does not declare the expected CC BY 4.0 license")
if ids.get("pmcid") != PMCID:
    raise ValueError("PMC OAI record did not match the requested PMCID")
if tag in {"fig", "table-wrap", "supplementary-material", "ref-list", "boxed-text"}:
    return
```

실행 명령:

```sh
uv run --locked python scripts/load_pmc_pilot.py
uv run --locked python scripts/load_pmc_pilot.py --apply
```

### TEST DB 검증 결과

- 실제 논문 **1편, 문단 청크 55개** 적재. 반복 `--apply` 후에도 문서 1개·청크 55개로 유지됐다.
- `climate land use Los Angeles birds` 검색에서 파일럿 청크 5개가 나왔고, `source_id=pmc-oa-ccby-pilot-9946348`, `license_name=CC BY 4.0`을 확인했다.
- 실제 TEST Neo4j 검색기와 실제 Gemini 생성기를 연결한 FastAPI `TestClient` 요청이 HTTP 200, `disposition=answer`를 반환했다. 검색 근거 3개를 받았고 생성 답변의 인용 ID가 그 안에 있었다.

```json
{
  "question": "How did climate and land use change affect birds in Los Angeles?",
  "intent": "evidence",
  "filters": {"kind": "evidence", "limit": 3}
}
```

- Python 전체 테스트 415개 통과(31개 건너뜀), fixture 검증 통과. 추가한 3개 테스트는 문단 추출과 그림 제외, 잘못된 라이선스 거부, OAI 응답 시각 변화에도 같은 원문 해시 유지 여부를 확인한다.
- TEST/fixture 검색 경로를 사용했으므로 API의 `fixture_only: true`는 정상이다. 운영 DB 적재나 배포 서버 검증은 아직 하지 않았다. 구현 범위는 `docs/pmc-literature-pilot.md`에 기록했다.

## 범위와 다음 작업

- 합성 문서에 이어 실제 PMC 문헌 1편으로 검색과 답변을 시험했다. 운영 수집기로 확대하려면 여러 문헌의 선별·증분 갱신·오류 처리·저작권 정책을 별도로 설계해야 한다.
- 이번 문헌은 TEST fixture 영역에 둔 실험 데이터다. fixture 재적재 시 제거되며 운영 데이터로 배포하지 않았다.
- API 키와 DB 자격 증명은 로컬 `.env`에만 두며 노트나 Git에는 기록하지 않는다.

## 관련 커밋

- `b1b002c` — CI 테스트 계약 정리
- `6d19cce` — Gemini 근거 답변 연결
- `4f84e89` — 실제 호출로 확인한 구조화 출력 형식 적용
- `27bc23b` — 일회용 PMC 문헌 검색 파일럿 추가

## 관련

- [[Work/index|Work]]

## 상세 보완 — 2026-10-05

### 검색·생성과 인용 검증의 책임

문헌 답변은 검색기가 먼저 허용된 청크와 근거 ID를 조회한 다음 생성기가 그 자료로 답변하는 구조다. Gemini가 답변 중 새로 만든 ID는 출처로 인정하지 않는다. 검색 근거가 없으면 모델의 지식만으로 답변을 만들어 이 경로의 검색 성공처럼 표시하지 않는다.

| 단계 | 확인할 내용 | 실패 시 의미 |
|---|---|---|
| Neo4j 검색 | 실제 청크·본문·문헌 식별자가 반환되는가 | 자료 없음 또는 검색 경로 문제 |
| Gemini 호출 | 구성된 모델이 유효한 응답을 반환하는가 | 생성 실패이며 DB 자료 부재와 다름 |
| 인용 검증 | 반환 ID가 이번 검색 결과 안에 있으며 출력 계약을 지키는가 | 생성 답변을 채택하지 않음 |
| 화면 제공 | 생성 실패에도 검색 결과를 유지하는가 | 근거 확인 경로를 보존해야 함 |

### PMC 파일럿의 적용 한계

이 날짜의 확인 대상은 허용된 PMC 논문 1편과 TEST fixture 검색 경로다. 실제 Neo4j와 Gemini를 연결한 TestClient 검증은 API 핸들러의 통합 확인이며, 공용 도메인·NPM·NAS 컨테이너를 통과한 검증과 구별한다. Jina 벡터 검색을 검증한 결과로 확대하지 않는다.

415건의 Python 테스트 중 31건은 환경에 따라 제외되었으며, 프런트엔드 37건은 당시 버전의 결과다. 이후 기능 추가로 테스트 수가 증가한 것은 이 기록의 숫자가 틀렸다는 뜻이 아니다.

### 후속 확인 순서

1. 문헌 검색 결과와 인용된 청크 ID를 먼저 대조한다.
2. 그다음 생성 응답과 인용 검증 결과를 확인한다.
3. 배포 검증에서는 실행 이미지의 기능 존재와 실제 HTTP 요청까지 확인한다.
4. 현재 기능·자료 영역은 [[Work/RobinGraph/RobinGraph 구현·데이터·검증 가이드|구현·데이터·검증 가이드]], 후속 배포 복구는 [[2026-09-30-NAS-Git이력분기-구형이미지-Gemini검색복구-525진단|NAS 검색 복구 기록]]을 참고한다.
