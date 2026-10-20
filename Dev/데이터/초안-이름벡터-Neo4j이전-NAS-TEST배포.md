---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-15-이름벡터-Neo4j이전-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 이름 벡터의 Neo4j 영구 저장·인덱스 검색 이전

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-15-이름벡터-Neo4j이전-NAS-TEST배포]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":3,"데이터":54}

## 1. 개요 및 목적

사용자는 현재 이름 벡터 검색이 Neo4j가 아닌 Python 앱 메모리에서 수행된다는 설명을 들은 뒤, Neo4j에 저장하고 검색하도록 변경할 것을 요청했다. 초기 구현은 검토 국명 850개의 벡터를 각 앱 프로세스에서 처음 만들고 캐시했다. 앱 재시작과 여러 프로세스에서 목록 전체 임베딩을 반복하는 문제가 있었다. 이름 벡터를 별도 인덱스에 준비하고, 채팅 요청에서는 질문 이름만 임베딩하여 Neo4j에서 후보를 찾도록 이전하는 것이 목표다.

사용자 후속 질문에 따라 실제 활성 분류판도 읽었다. TEST에는 종 11,131개·아종 19,879개(속 2,376·과 252·목 46)가 있다. 이번 이름 벡터 범위는 기존 검토 국명 850종이다. 전체 종·아종으로 벡터 범위를 확대하지 않았다. 기존 그래프 정확 이름 조회와 후보 선택·주제 보존, 일반 하한 및 제한적 자모 보완 정책은 유지한다. Production 이전은 이번 범위가 아니다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 협업과 확인한 근거
- 변경 전후 동작과 파일
- 검증: mock과 실제 DB/API 구분
- 단위·계약 검사
- 실제 격리 Neo4j
- 실제 NAS TEST 색인
- 실제 NAS API와 브라우저
- 배포·소스·운영 불변
- 증거와 남은 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자 후속 질문에 따라 실제 활성 분류판도 읽었다. TEST에는 종 11,131개·아종 19,879개(속 2,376·과 252·목 46)가 있다. 이번 이름 벡터 범위는 기존 검토 국명 850종이다. 전체 종·아종으로 벡터 범위를 확대하지 않았다. 기존 그래프 정확 이름 조회와 후보 선택·주제 보존, 일반 하한 및 제한적 자모 보완 정책은 유지한다. Production 이전은 이번 범위가 아니다.

- Claude: 새 Neo4j 이름 벡터 저장소와 fake-driver 검사. Task `task_be62670e89d0` / Dispatch `ctx_ac184290460a`, 실제 분류 문맥 후속 정정 Task `task_9fcf93720f88` / Dispatch `ctx_29dad5f7b08f`를 성공 보고로 전달했다. 새 파일 두 개만 수정했고 DB/API 쓰기나 배포는 하지 않았다.
- Codex: 메모리 벡터·캐시 제거, CLI 연결과 TEST 전용 색인 명령, 단위 검사와 실제 격리 DB 검증, NAS DB 대상 확인·색인·배포·API/브라우저 검증·기록을 맡았다. 저장소 통합 시 실수로 Taxon 노드를 수정하지 않도록 entry guard도 보완했다.
- Antigravity가 앞서 만든 후보 UI는 변경하지 않았다. 기존 사용자 확인 UI와 실제 브라우저 검증 자산을 재사용했다.
- Orca의 두 완료 보고를 실제 Task/Dispatch와 대조한 뒤 정산했다. 외부 사용자 터미널은 worker-release 결과 retained/external_terminal로 유지됐고 reclaimable worker는 0개다.

실제 NAS Neo4j 버전은 5.26.30이었다. 기존 문헌 인덱스는 `robingraphFixtureChunkVector`, 라벨 `HybridVectorChunk`, 속성 `hybrid_vector`, 512차원·cosine·ONLINE으로 확인했다. 새 이름 인덱스와 분리했다. 최신 Cypher SEARCH를 무조건 사용하지 않고 실제 5.26에서 지원하는 `db.index.vector.queryNodes`를 사용했다.

Neo4j의 cosine 점수 범위는 기존 앱의 raw cosine과 다르다. [공식5.x 벡터 인덱스 문서](https://neo4j.com/docs/cypher-manual/5/indexes/semantic-indexes/vector-indexes/)의 규약에 따라 `2*score-1`로 변환한다. 실제 격리5.26.30에서 직교 벡터가 Neo4j0.5, 어댑터 raw0.0을 반환함을 확인했다. 이 차이를 무시해 후보 하한이 사실상 바뀌지 않도록 했다.

처음 전달된 저장소에는 이전 그래프 `IngestState`를 요구하는 경로가 있었다. 실제 NAS에서 해당 노드가 없음을 읽기 조회로 확인했다. 현재 활성 분류판의 기준은 PostgreSQL `active_release_context('reference-taxonomy-traits')`이며 CLI가 기존 계통 저장소에도 callback으로 전달한다. Claude 후속 작업에서 레거시 상태 의존성을 제거했고, 전달받은 문맥과 allowed TaxonConceptSet·실제 종 연결을 확인하도록 정정했다. 옛 상태 노드를 새로 만들지 않았다. 색인 명령·resolver가 PostgreSQL 문맥을 전후로 다시 확인한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-15-이름벡터-Neo4j이전-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
