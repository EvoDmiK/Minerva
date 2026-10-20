---
created: 2026-10-21
updated: 2026-10-21
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-21-이름벡터-카탈로그-TEST-Production-한정반영]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 종 이름 벡터·카탈로그 TEST → Production 한정 반영 — 2026-10-21

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-21-이름벡터-카탈로그-TEST-Production-한정반영]] · 분류 근거 {"인프라":0,"자동화":1,"관측성":4,"데이터":50}

## 1. 개요 및 목적

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 백로그]] · [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-15-이름벡터-Neo4j이전-NAS-TEST배포|이름 벡터 Neo4j 이전 (TEST)]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-main-Production-Django-배포|RG-701 Production 배포 (Production 이름 벡터 0 기록)]]

> [!SUCCESS] 완료 — 실제 Production 반영과 검증 통과 (Root 최종 승인 2026-10-21 07:22 KST)
> Root(Codex)가 원천 export, Production 계획·반영, 실제 벡터·API·브라우저 검증을 실행했다. 문서 담당은 dev-codex `docs/verification/assets/2026-10-21-name-vector-promotion/` 산출물과 `/tmp/rg-name-promotion/` 운영 스크립트를 **읽기만** 해서 대조했다. 문서 담당은 DB·서비스·Git·코드·환경 설정을 조작하지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 요청 배경과 목표
- 범위
- 역할 분담
- 원천(TEST)·대상(Production) 확인 — 2026-10-21 새 확인
- 운영 스크립트와 가드
- 독립 검토
- 실행 이력 (2026-10-21, KST)
- 백업
- 복사 정밀도: 복사한 벡터 vs 원시 export
- 모델 호출: 검증 vs 재생성
- 실제 벡터·API·브라우저 회귀
- 벡터 인덱스 (실제 Production Neo4j)
- API (실제 Production 앱, NAS 컨테이너 내부 `127.0.0.1:8000`, 응답 mocking 없음)
- 공개 URL 브라우저 (`https://robingraph.dove-nest.com/chat`, 응답 mocking 없음)
- 관련 없는 변경 없음
- 변경 전후 동작
- 실제 사용한 명령 (Root 전달·자산 기준)
- 검증 종류 구분
- 변경 파일과 구현 내용
- 배포·커밋 정보
- 롤백 기준
- 남은 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
# 원천 export: TEST 컨테이너에서 common.py snapshot('test') (promote.py --plan 내부, Python)
python3 /tmp/rg-name-promotion/promote.py --plan
python3 /tmp/rg-name-promotion/promote.py --apply
python3 /tmp/rg-name-promotion/live-api.py
node docs/verification/assets/2026-10-21-name-vector-promotion/browser.cjs
# 독립 검토(오프라인, dev-codex)
.venv/bin/python -m unittest tests.test_taxon_name_vectors_neo4j tests.test_index_taxon_name_vectors tests.test_embeddings tests.test_taxon_name_resolution
```

## 4. 검증 근거 및 트러블슈팅

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 백로그]] · [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-15-이름벡터-Neo4j이전-NAS-TEST배포|이름 벡터 Neo4j 이전 (TEST)]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-main-Production-Django-배포|RG-701 Production 배포 (Production 이름 벡터 0 기록)]]

> [!SUCCESS] 완료 — 실제 Production 반영과 검증 통과 (Root 최종 승인 2026-10-21 07:22 KST)
> Root(Codex)가 원천 export, Production 계획·반영, 실제 벡터·API·브라우저 검증을 실행했다. 문서 담당은 dev-codex `docs/verification/assets/2026-10-21-name-vector-promotion/` 산출물과 `/tmp/rg-name-promotion/` 운영 스크립트를 **읽기만** 해서 대조했다. 문서 담당은 DB·서비스·Git·코드·환경 설정을 조작하지 않았다.

- 사용자 승인 범위: TEST의 **종 이름 벡터(TaxonNameVector)와 그 카탈로그만** Production에 반영한다. **TEST DB 전체 복사가 아니다.** 사용자는 팀 작업을 명시적으로 요청했다(Root 총괄, 독립 검토자, 문서 담당).
- 실행: Root가 만든 명시적·가드 포함 일회성 운영 스크립트 `/tmp/rg-name-promotion/promote.py`(`--plan`·`--apply`)와 검증 모듈 `common.py`. dev-claude의 독립 Claude 검토자가 사전 검토했다.
- 결과(실제 Production):
  - 이름 벡터 **0 → 855**, 카탈로그 1개(fingerprint `a96ed6f8…1919f4c1`). 이름 전용 인덱스(512차원, cosine, ONLINE)와 entry key 유일성 constraint를 새로 만들었다. `state: verified`.
  - 벡터는 TEST에서 **복사**했다. 복사용 외부 임베딩 호출은 0회다. 원시 export 대비 성분별 최대 차이는 2.78e-17이다(허용 1e-12).
  - 모델 호출은 호환성 검증용 텍스트 6개(plan 3 + apply 3)뿐이다. 카탈로그를 재생성하지 않았다.
  - 실제 벡터 인덱스 질의 6/6, 실제 Production API 4/4, 공개 URL 브라우저 2/2(1280·390px) 통과.
  - Taxon 33,694와 속성 해시, PostgreSQL ingest 상태 해시는 반영 전후가 같다. 다만 **감시 범위 비교이며 DB 전체 체크섬은 아니다.**
  - 앱 배포·재시작, PostgreSQL 쓰기, TEST DB 전체 복사, commit/push, 자동 롤백 **없음**.
- 진행 중 NAS SSH 연결 거부로 첫 계획이 Production을 읽기 전에 중단됐다. 사용자가 SSH를 복구한 뒤 재실행했다(아래 이력).

- 배경:
  - 2026-10-15 이름 벡터를 Neo4j 영구 저장·인덱스 검색으로 옮겼다(dev-codex `docs/work-log/2026-10-15-neo4j-name-vector-migration.md`). 그때는 TEST에만 색인했고 Production 반영은 범위 밖이었다.
  - 2026-10-19 RG-406 후속으로 TEST 카탈로그가 850 → 855종으로 늘었다(dev-codex `docs/work-log/2026-10-19-rg406-outside-name-search.md`: inventory 855 / reused 849 / embedded 6).
  - 2026-10-20 RG-701 Production 배포 때 운영 DB 감시 범위에서 TaxonNameVector 0과 빈 카탈로그를 확인했다. 사용자는 TEST DB 전체 복사를 하지 않고 데이터셋별로 따로 검토·승인하기로 했다([[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-main-Production-Django-배포|RG-701 Production 배포 기록]]). 그래서 운영의 그래프 우선 이름 해소에서 벡터 후보 경로는 데이터가 없어 보류 상태였다.
- 목표: TEST에서 검증된 이름 벡터·카탈로그만 Production Neo4j에 반영해 운영 이름 후보 경로를 활성화한다. 다른 운영 데이터와 서비스는 바꾸지 않는다.
- RG-701(Django 전환)은 이미 완료됐다. 이 작업은 그 상태와 기록을 다시 열거나 바꾸지 않았다.

| 포함 | 제외 |
|---|---|
| `TaxonNameVectorEntry`·`TaxonNameVector`(`name_vector` 속성)·`NAME_VECTOR_OF` 연결, `TaxonNameVectorCatalog`, 이름 전용 vector index·constraint | TEST DB 전체 복사, 다른 TEST 데이터, 운영 PostgreSQL 쓰기, Taxon·Document·Chunk 등 다른 그래프 데이터, 문헌 벡터 인덱스 |
| 원천·대상의 활성 분류 문맥과 프로필 대응 확인, 반영 전 백업, 반영 후 실제 회귀 | 앱 이미지 교체·컨테이너 재시작·Jenkins·n8n 변경, 저장소 코드·환경 설정 변경, commit/push |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-21-이름벡터-카탈로그-TEST-Production-한정반영]]
- [[Dev/index|Dev 인덱스]]
