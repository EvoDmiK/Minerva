---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/3xx 질문 의도·LLM/2026-09-29-CI-수정-Gemini-연동-PMC-문헌파일럿]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RobinGraph — CI 테스트 수정, Gemini 근거 답변 연동, PMC 문헌 파일럿 (2026-09-29)

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/3xx 질문 의도·LLM/2026-09-29-CI-수정-Gemini-연동-PMC-문헌파일럿]] · 분류 근거 {"인프라":2,"자동화":2,"관측성":0,"데이터":16}

## 1. 개요 및 목적

- Git 작업 상태와 커밋 작성자 정보를 정리했다. 현재 `dev`는 `origin/dev`와 일치하고 작업 트리는 깨끗하다.
- Ponytail 원칙으로 구현 범위를 좁히고, Claude 작업자 두 명에게 Gemini 호출 모듈과 `/v1/chat` 연결을 나누어 맡긴 뒤 통합 결과를 검토했다.
- `GEMINI_API_KEY`가 있을 때만 `serve-neo4j`의 문헌 근거 경로에서 Gemini 답변을 생성하도록 연결했다. 모델 기본값은 `gemini-3.8-flash`이며 `ROBINGRAPH_GEMINI_MODEL`로 바꿀 수 있다.
- 생성 응답의 근거 ID가 실제 검색 청크에 있는지 확인한다. 근거가 없거나 생성·검증이 실패하면 근거 없는 답변을 표시하지 않고 기존 검색 결과를 유지한다.
- CI의 기존 ingest/Windows 계약 테스트를 현재 구현에 맞게 정리했다.
- TEST Neo4j에 CC BY 4.0 PMC 논문 1편을 실험용으로 적재하고, 실제 검색과 Gemini 답변까지 확인했다.

- `tests/test_n8n_workflows.py`: 한국어 일반명 통합 테스트에서 이전 `start/finalize` 절차를 제거하고 현재의 배치 적재 계약을 사용했다. 같은 배치를 다시 실행해도 이름 노드가 중복되지 않는지, 새 스냅샷에서 이전 이름이 비활성화되는지, 동명이인을 잘못 매칭하지 않는지 확인한다. 테스트가 공유 `IngestState`를 임시로 바꾸던 과정도 없앴다.
- 같은 파일의 GBIF 관찰 테스트는 현재 입력 계약에 맞춰 `dataset_id`와 허용된 CC-BY 라이선스를 제공하고, 이전 결과 필드 대신 `domain_verified` 상태를 확인하도록 고쳤다.
- `tests/test_nas_deploy_lifecycle.py`: Windows에는 Unix 실행 비트가 없으므로 해당 검사만 제외했다. TEST/PROD 환경 파일 경로 검사도 OS별 절대경로 차이에 영향을 받지 않도록 조정했다.

## 2. 핵심 아키텍처 및 원칙

- 오늘 한 일
- CI 테스트 수정
- CI 변경 스니펫
- Gemini 연동 세부 내용
- 요청과 응답 검증 스니펫
- 검증
- 재현 명령과 테스트 범위
- PMC 실제 문헌 파일럿
- 수집 대상과 선택 이유
- 구현
- TEST DB 검증 결과
- 범위와 다음 작업
- 관련 커밋
- 관련
- 상세 보완 — 2026-10-05
- 검색·생성과 인용 검증의 책임
- PMC 파일럿의 적용 한계
- 후속 확인 순서

## 3. 재사용 가능한 코드 스니펫 / 설정

```python
write_batch(run_1, dataset_1, "release-1", rows_v1)
write_batch(run_1, dataset_1, "release-1", rows_v1)  # 재실행해도 중복 없음
active_dataset = [dataset_2]
# 조회 저장소에 현재 활성 데이터셋과 taxonomy context를 명시적으로 전달
lambda: active_dataset[0]
lambda: (concept_set_id, marker)
```

```python
if os.name != "nt":
    mode = script.stat().st_mode
    self.assertTrue(mode & stat.S_IXUSR)
self.assertRegex(calls, rf"--env-file \S*\.env\.nas\.{target}(?=\s)")
```

```python
gemini_api_key = os.getenv("GEMINI_API_KEY")
answer_generator = None
if gemini_api_key:
    answer_generator = GeminiAnswerer(
        gemini_api_key,
        os.getenv("ROBINGRAPH_GEMINI_MODEL", "gemini-3.8-flash"),
    )
```

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

```sh
uv run --locked python -m unittest discover -s tests -q
node --test tests/frontend/chat_ui.test.js
uv run --locked robingraph load-neo4j-fixture
uv run --locked robingraph index-neo4j-fixture
uv run --locked robingraph verify-neo4j-fixture
```

```json
{
  "question": "fixture 호수",
  "intent": "evidence",
  "filters": {"kind": "evidence", "limit": 3}
}
```

```python
if not any(LICENSE_URI in statement for statement in license_statements):
    raise ValueError("PMC article does not declare the expected CC BY 4.0 license")
if ids.get("pmcid") != PMCID:
    raise ValueError("PMC OAI record did not match the requested PMCID")
if tag in {"fig", "table-wrap", "supplementary-material", "ref-list", "boxed-text"}:
    return
```

```sh
uv run --locked python scripts/load_pmc_pilot.py
uv run --locked python scripts/load_pmc_pilot.py --apply
```

```json
{
  "question": "How did climate and land use change affect birds in Los Angeles?",
  "intent": "evidence",
  "filters": {"kind": "evidence", "limit": 3}
}
```

## 4. 검증 근거 및 트러블슈팅

- Git 작업 상태와 커밋 작성자 정보를 정리했다. 현재 `dev`는 `origin/dev`와 일치하고 작업 트리는 깨끗하다.
- Ponytail 원칙으로 구현 범위를 좁히고, Claude 작업자 두 명에게 Gemini 호출 모듈과 `/v1/chat` 연결을 나누어 맡긴 뒤 통합 결과를 검토했다.
- `GEMINI_API_KEY`가 있을 때만 `serve-neo4j`의 문헌 근거 경로에서 Gemini 답변을 생성하도록 연결했다. 모델 기본값은 `gemini-3.8-flash`이며 `ROBINGRAPH_GEMINI_MODEL`로 바꿀 수 있다.
- 생성 응답의 근거 ID가 실제 검색 청크에 있는지 확인한다. 근거가 없거나 생성·검증이 실패하면 근거 없는 답변을 표시하지 않고 기존 검색 결과를 유지한다.
- CI의 기존 ingest/Windows 계약 테스트를 현재 구현에 맞게 정리했다.
- TEST Neo4j에 CC BY 4.0 PMC 논문 1편을 실험용으로 적재하고, 실제 검색과 Gemini 답변까지 확인했다.

- `tests/test_n8n_workflows.py`: 한국어 일반명 통합 테스트에서 이전 `start/finalize` 절차를 제거하고 현재의 배치 적재 계약을 사용했다. 같은 배치를 다시 실행해도 이름 노드가 중복되지 않는지, 새 스냅샷에서 이전 이름이 비활성화되는지, 동명이인을 잘못 매칭하지 않는지 확인한다. 테스트가 공유 `IngestState`를 임시로 바꾸던 과정도 없앴다.
- 같은 파일의 GBIF 관찰 테스트는 현재 입력 계약에 맞춰 `dataset_id`와 허용된 CC-BY 라이선스를 제공하고, 이전 결과 필드 대신 `domain_verified` 상태를 확인하도록 고쳤다.
- `tests/test_nas_deploy_lifecycle.py`: Windows에는 Unix 실행 비트가 없으므로 해당 검사만 제외했다. TEST/PROD 환경 파일 경로 검사도 OS별 절대경로 차이에 영향을 받지 않도록 조정했다.

한국어 일반명 테스트는 전역 `IngestState`를 임시 변경하지 않고, 배치 재실행과 활성 데이터셋 전환을 직접 확인한다.

Windows에서는 존재하지 않는 Unix 실행 비트를 검사하지 않는다. 환경 파일 경로는 OS별 절대경로 대신 `.env.nas.test` / `.env.nas.prod` 접미사를 검사한다.

- `generation.py`는 표준 라이브러리로 Gemini REST API를 호출하고, 검색된 청크의 본문과 출처 정보만 전달한다. API 오류 내용이나 키는 사용자 응답에 노출하지 않는다.
- `/v1/chat`의 문헌 근거 경로에서만 생성기를 호출한다. 근거가 없으면 답변을 보류하고, 모델 호출 실패·빈 답변·중복되거나 검색 결과에 없는 근거 ID는 생성 답변을 사용하지 않는다. 분류·관찰 경로는 그대로 유지한다.
- `cli.py`는 `GEMINI_API_KEY`가 있을 때만 생성기를 연결한다. `.env.example`, `.env.nas.example`, README와 채팅 UI 설명도 실제 동작에 맞게 갱신했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/3xx 질문 의도·LLM/2026-09-29-CI-수정-Gemini-연동-PMC-문헌파일럿]]
- [[Dev/index|Dev 인덱스]]
