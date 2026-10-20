---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-15-RG202-문헌감사-검색기준선-MRR수정]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-202 선행 문헌 감사·검색 기준선과 MRR 수정

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-15-RG202-문헌감사-검색기준선-MRR수정]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":0,"데이터":6}

## 1. 개요 및 목적

후속 사용자 지시로 NAS TEST 배포·실제 검증을 완료했다. 아래 선행 작업 당시의 미배포 기록과 구별한다. [NAS TEST 배포 상세](2026-10-15-rg202-nas-test-deployment.md). RG-202 전체의 문헌 확보 대기는 유지한다.

사용자가 Obsidian MCP에서 작업 백로그를 읽고 가장 먼저 필요한 작업을 실행하도록 요청했다. 전체 백로그와 2xx·1xx 상세, 구현·검증 가이드를 읽었다. 신규 권장 순서는 RG-202 → RG-406이며 RG-101은 실측 후 순서를 정한다. RG-102·503·504·505는 별도 재개 지시 전 최후순위 보류다. 따라서 RG-202의 첫 단계인 실제 TEST 문헌·청크·관계·인덱스·임베딩 감사를 선택했다. 전체 백로그의 과거 배포 상태를 현재 상태로 추정하지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 선정 근거
- 실제 TEST 감사와 판단
- 확인한 평가 오류와 변경 전후
- 변경 파일과 구현
- 실제 API 기준선
- 검증 명령과 결과
- 기술 방향과 다음 단계
- 배포·커밋·운영 영향

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
docker exec -i robingraph-api-test python - < scripts/audit_retrieval_readiness.py
PYTHONPATH=src /tmp/robingraph-qa-python/bin/python docs/verification/assets/2026-10-15-rg202/benchmark.py
PYTHONPATH=src /tmp/robingraph-qa-python/bin/python -m unittest tests.test_search_cli tests.test_search_evaluation tests.test_retrieval_readiness tests.test_hybrid_retrieval
graphify update .
git diff --check
```

## 4. 검증 근거 및 트러블슈팅

후속 사용자 지시로 NAS TEST 배포·실제 검증을 완료했다. 아래 선행 작업 당시의 미배포 기록과 구별한다. [NAS TEST 배포 상세](2026-10-15-rg202-nas-test-deployment.md). RG-202 전체의 문헌 확보 대기는 유지한다.

사용자가 Obsidian MCP에서 작업 백로그를 읽고 가장 먼저 필요한 작업을 실행하도록 요청했다. 전체 백로그와 2xx·1xx 상세, 구현·검증 가이드를 읽었다. 신규 권장 순서는 RG-202 → RG-406이며 RG-101은 실측 후 순서를 정한다. RG-102·503·504·505는 별도 재개 지시 전 최후순위 보류다. 따라서 RG-202의 첫 단계인 실제 TEST 문헌·청크·관계·인덱스·임베딩 감사를 선택했다. 전체 백로그의 과거 배포 상태를 현재 상태로 추정하지 않았다.

2026-10-15 로컬 robingraph-api-test에 연결해 /health의 status=ok, mode=neo4j, deployment_target=test를 확인했다. 컨테이너의 기존 접속 설정을 사용하고 ROBINGRAPH_DEPLOY_TARGET=test를 확인한 뒤 Neo4j 읽기 트랜잭션만 실행했다. 비밀값은 출력하지 않았다.

전문 인덱스 robingraphFixtureChunkFulltext는 ONLINE, HybridSearchChunk.text 대상, standard-no-stop-words 분석기다. 벡터 인덱스 robingraphFixtureChunkVector는 ONLINE, HybridVectorChunk.hybrid_vector 대상, 512차원·COSINE이다. 저장 벡터는 jinaai/jina-embeddings-v3, normalized=true다. 재인덱싱하거나 기존 인덱스를 교체하지 않았다. 질문/문서 임베딩 작업 계약 전체나 모델 서버 revision은 이번에 다시 검증하지 않았다.

**판단: RG-202의 선행 감사와 합성 기준선은 완료했지만 전체 RG-202는 미완료다.** 현재 자료로 최소 50문항·다단계 20문항 및 여러 문서의 사실 연결을 독립 검증할 수 없다. 합성 문항을 늘려 실제 문헌 품질 검증으로 포장하지 않는다. 기존 검색을 유지하고 새 검색 활성화·자료 자동 수집은 하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-15-RG202-문헌감사-검색기준선-MRR수정]]
- [[Dev/index|Dev 인덱스]]
