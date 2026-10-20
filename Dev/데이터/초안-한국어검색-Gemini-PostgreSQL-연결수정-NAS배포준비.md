---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-09-30-한국어검색-Gemini-PostgreSQL-연결수정-NAS배포준비]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RobinGraph — 한국어 검색·Gemini·PostgreSQL 연결 수정·NAS 배포 준비

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-09-30-한국어검색-Gemini-PostgreSQL-연결수정-NAS배포준비]] · 분류 근거 {"인프라":11,"자동화":2,"관측성":0,"데이터":22}

## 1. 개요 및 목적

한국어 질문으로 영어 PMC 문헌을 검색하고, 인용이 포함된 한국어 답변을 받도록 개선했다. PostgreSQL 접속 실패는 기존 내부망 주소를 Tailscale 주소로 바꿔 해결했다. 실제 데이터로 대륙검은지빠귀 분류 조회를 확인했고, Docker에서도 DB 조회와 Gemini 응답을 검증했다.

마지막으로 수정사항을 사용자 Git 작성자 정보로 커밋하고 `origin/dev`에 push했다. **NAS에서 직접 실행한 상태는 아니다. NAS에서 pull한 뒤 사용자가 배포하기로 했다.**

## 2. 핵심 아키텍처 및 원칙

- 오늘의 결과
- 1. 한국어 질문이 영어 문헌을 찾지 못하는 문제
- 원인 확인
- 구현
- Gemini 503 대응
- 실제 질문 검증
- 2. GraphDB에 새가 없는 것처럼 보이는 문제 확인
- 3. PostgreSQL 연결 실패 해결
- 원인
- 수정
- 읽기 전용 확인
- 4. NAS 배포 준비와 Docker 검증
- 컨테이너에서 확인한 내용
- 5. 테스트와 Git 반영
- 수정한 파일
- 6. NAS에서 이어서 할 일
- 이후 개발 과제
- 관련
- 상세 보완 — 2026-10-05
- 한국어 문헌 검색과 종 이름 조회의 차이
- 연결 문제를 확인한 범위
- 이후 배포 상태

## 3. 재사용 가능한 코드 스니펫 / 설정

```python
# src/robingraph/api/app.py — 핵심 흐름 발췌
search_question = question
if not hybrid and english_search_terms is not None and any(
    "\uac00" <= char <= "\ud7a3" for char in question
):
    terms = english_search_terms(question)
    search_question = f"{question} {terms}"
```

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

```python
# src/robingraph/generation.py — 503 처리 발췌
if exc.code == 503 and attempt == 0:
    time.sleep(1)
    continue
raise GeminiAnswerError(f"Gemini HTTP error {exc.code}") from None
```

```text
대륙검은지빠귀
학명: Turdus mandarinus
영명: Chinese Blackbird
계보: Passeriformes → Turdidae → Turdus → Turdus mandarinus
AviList 개념 집합: rg:concept-set:avilist-v2025b
```

```text
기존: <NAS-LAN-IP>:5433
오류: No route to host
```

```dotenv
ROBINGRAPH_PG_HOST=<NAS-Tailscale-IP>
ROBINGRAPH_PG_PORT=5433
ROBINGRAPH_PG_DATABASE=robingraph_test
ROBINGRAPH_PG_SCHEMA=ingest
ROBINGRAPH_PG_SSLMODE=prefer
```

```sh
git switch dev
git pull --ff-only origin dev
```

```sh
cp .env.nas.example .env.nas.test
chmod 600 .env.nas.test
```

```dotenv
ROBINGRAPH_API_MODE=serve-neo4j
ROBINGRAPH_IMAGE=robingraph-api:test-20260930
ROBINGRAPH_PG_HOST=<NAS-Tailscale-IP>
ROBINGRAPH_PG_PORT=5433
ROBINGRAPH_PG_DATABASE=robingraph_test
ROBINGRAPH_GEMINI_MODEL=gemini-3.5-flash-lite
```

```sh
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh preflight
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh deploy
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh verify

docker exec robingraph-api-test python scripts/verify_api_deployment.py \
  --base-url http://127.0.0.1:8000 \
  --lineage-name 대륙검은지빠귀 \
  --expected-scientific-name 'Turdus mandarinus' --json
```

## 4. 검증 근거 및 트러블슈팅

한국어 질문으로 영어 PMC 문헌을 검색하고, 인용이 포함된 한국어 답변을 받도록 개선했다. PostgreSQL 접속 실패는 기존 내부망 주소를 Tailscale 주소로 바꿔 해결했다. 실제 데이터로 대륙검은지빠귀 분류 조회를 확인했고, Docker에서도 DB 조회와 Gemini 응답을 검증했다.

| 항목 | 상태 |
|---|---|
| 한국어 fulltext 문헌 검색 개선 | 구현·실제 API 검증 완료 |
| Gemini 한국어 답변·근거 인용 | TEST 모델로 검증 완료 |
| PostgreSQL 연결 | 주소 수정 후 연결 정상 |
| 대륙검은지빠귀 분류 조회 | HTTP 200·학명 검증 완료 |
| NAS용 Docker 이미지 | 빌드·컨테이너 실행 검증 완료 |
| Git 커밋·push | `f3b77e5` → `origin/dev` |
| 실제 NAS 배포 | 사용자 pull·배포 대기 |

PMC9946348 한 편이 들어 있는 TEST Neo4j에서 같은 뜻의 한국어·영어 질문 5쌍을 비교했다.

- 한국어 fulltext 요청에만 적용한다.
- 영어 질문과 auto/hybrid 경로에는 추가 번역 호출을 넣지 않는다.
- 검색어 변환 실패 시 원래 질문으로 조회하고 경고를 반환한다.
- 기존 Lucene 검색어 이스케이프를 유지한다.
- `조류`가 algae/tides로 번역되지 않도록 bird ecology 문맥을 명시한다.
- 질문에 없는 사실이나 관련 개념을 덧붙이지 않도록 요청한다.

계속 실패하면 기존 검색·생성 fallback을 사용한다. 오류 로그에는 예외 종류만 남기고 API 키나 제공자 오류 본문은 노출하지 않는다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-09-30-한국어검색-Gemini-PostgreSQL-연결수정-NAS배포준비]]
- [[Dev/index|Dev 인덱스]]
