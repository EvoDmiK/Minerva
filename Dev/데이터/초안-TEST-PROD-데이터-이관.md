---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-09-TEST-PROD-데이터-이관]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# TEST → PROD 데이터 이관

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-09-TEST-PROD-데이터-이관]] · 분류 근거 {"인프라":0,"자동화":2,"관측성":0,"데이터":46}

## 1. 개요 및 목적

TEST 서버에만 올라가 있던 데이터를 PROD DB로 옮긴다. 사용자는 PROD의 기존 데이터를 모두 지우고 TEST 데이터 전부를 옮기도록 승인했고, PROD 직접 접속도 허용했다. 작업 중 TEST Neo4j를 잠시 중지하는 것과 PROD Neo4j의 짧은 중단도 승인받았다.

저장소에는 TEST/PROD 간 데이터 이관 스크립트나 절차 문서가 없었다(`docs/nas-deployment.md`의 TEST/PROD 전환은 API 컨테이너 배포만 다룬다). 적재 스크립트(`load_*.py`)는 원본에서 DB로 넣는 용도이며 DB 간 복사는 하지 않는다. 이관은 DB 덤프와 복원으로 수행했다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 사전 확인한 사실
- 이관 전 상태 (읽기 전용 확인)
- 수행 내용
- 검증 결과 (실제 DB/API)
- 변경 전후 동작
- 중단 시간
- 설계 논의
- 남은 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

TEST 서버에만 올라가 있던 데이터를 PROD DB로 옮긴다. 사용자는 PROD의 기존 데이터를 모두 지우고 TEST 데이터 전부를 옮기도록 승인했고, PROD 직접 접속도 허용했다. 작업 중 TEST Neo4j를 잠시 중지하는 것과 PROD Neo4j의 짧은 중단도 승인받았다.

저장소에는 TEST/PROD 간 데이터 이관 스크립트나 절차 문서가 없었다(`docs/nas-deployment.md`의 TEST/PROD 전환은 API 컨테이너 배포만 다룬다). 적재 스크립트(`load_*.py`)는 원본에서 DB로 넣는 용도이며 DB 간 복사는 하지 않는다. 이관은 DB 덤프와 복원으로 수행했다.

| 항목 | PROD | TEST |
|---|---|---|
| Neo4j 위치 | NAS `neo4j` 컨테이너, `neo4j:latest`(2026.08.1), 데이터 `/volume3/Birds-Nest/docker-data/homelab/neo4j/data` | Mac mini 로컬 `neo4j-test` 컨테이너, `neo4j:5.26.30-community` |
| PostgreSQL | NAS `postgres-n8n` 컨테이너(호스트 포트 5433), DB `robingraph`, 스키마 `ingest` | 같은 컨테이너, DB `robingraph_test` |

- 5433 포트의 PostgreSQL은 n8n이 함께 쓰는 인스턴스다. 이관은 `robingraph` DB의 `ingest` 스키마 안에서만 수행했고 다른 DB는 건드리지 않았다.
- TEST와 PROD는 각각 `.env.nas.test`, `.env.nas.prod`(NAS `~/RobinGraph-rg001-20261002/`)로 구분된다.

| 항목 | PROD | TEST |
|---|---|---|
| Neo4j 노드 | 약 162,000(ExternalIdentifier 60,796 / Taxon 33,684 / ScientificName 33,684 / SourceRecord 33,684 외 소수) | 474,998 |
| Neo4j 관계 | 262,856 | 543,637 |
| TEST 주요 레이블 | — | TraitClaim 174,843 / EvidenceUnit 136,213 / ExternalIdentifier 60,796 / ScientificName 33,723 / Taxon 33,694 / TaxonMappingClaim 17,648 / VernacularName 13,690 / TaxonMappingCandidate 3,371 / BirdNameUsage 396 / VernacularNameCandidate 306 / SourceRecord 116 / Observation 116 / MediaAsset 36 / BirdTaxon 29 / Place 8 / Chunk 4 / TaxonConceptSet 3 / SourceDataset 3 / Document 2 / License 1 |
| Neo4j 인덱스 | — | LOOKUP 2, FULLTEXT 1, VECTOR 1, RANGE 18 |
| PG `ingest` 테이블 | 8개 모두 0행 | `source_record` 57,625 / `ingestion_run` 33 / `source_release` 10 / `source_dataset` 13 / `outbox_event` 0 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-09-TEST-PROD-데이터-이관]]
- [[Dev/index|Dev 인덱스]]
