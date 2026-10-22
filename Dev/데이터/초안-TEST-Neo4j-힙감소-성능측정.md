---
created: 2026-10-22
updated: 2026-10-22
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-22-TEST-Neo4j-힙감소-성능측정]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# TEST Neo4j Heap 감소 성능측정 (2GiB/4GiB) — 2026-10-22

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-22-TEST-Neo4j-힙감소-성능측정]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":5,"데이터":20}

## 1. 개요 및 목적

> **문서 상태: 읽기 전용 벤치마크 완료 (설정·코드·DB 무변경)**  
> TEST 환경(16GB Mac .97 앱 / 32GB Mac .98 Neo4j)에서 Neo4j 힙 설정(초기 2GiB / 최대 4GiB, pagecache 1GiB) 하의 순수 읽기 성능을 실측했다. Chunk 검색(과거 관측 비교), 3.3만 종 도메인 그래프 복합 질의, 855종 이름 벡터 조회를 순차 warm 조건에서 측정했다. 설정 변경, 컨테이너 재시작, DB 쓰기, 애플리케이션 코드 변경, 운영 반영 및 Git commit/push는 일체 수행하지 않았다.

---

## 2. 핵심 아키텍처 및 원칙

- 1. 벤치마크 환경 및 핵심 실측 요약
- 핵심 실측 결과 비교표
- 2. 세부 검증 내용 및 관측 사실
- 1) Chunk 검색 관측 비교 (`chunk-current.json`, `summary.json`)
- 2) 도메인 그래프 관계 질의 실측 (`graph-current.json`, `graph-probe.py`)
- 3) 종 이름 벡터 검색 실측 및 프로브 가드 보정 (`names-current.json`, `names-probe.py`)
- 4) JVM 힙 및 GC 동작 관측 (`runtime-mid.json`, `runtime-after.json`)
- 3. 한계 및 해석 유의사항
- 관련 문서 및 증거 자산

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

> **문서 상태: 읽기 전용 벤치마크 완료 (설정·코드·DB 무변경)**  
> TEST 환경(16GB Mac .97 앱 / 32GB Mac .98 Neo4j)에서 Neo4j 힙 설정(초기 2GiB / 최대 4GiB, pagecache 1GiB) 하의 순수 읽기 성능을 실측했다. Chunk 검색(과거 관측 비교), 3.3만 종 도메인 그래프 복합 질의, 855종 이름 벡터 조회를 순차 warm 조건에서 측정했다. 설정 변경, 컨테이너 재시작, DB 쓰기, 애플리케이션 코드 변경, 운영 반영 및 Git commit/push는 일체 수행하지 않았다.

- **대상 인프라**: TEST Neo4j (`bolt://192.168.219.98:7687`), PostgreSQL (`robingraph_test`, 192.168.219.99).
- **연결 확인**: 초기 SSH BatchMode 읽기 실패 후, 기존 정상 작동 중인 TEST 앱 환경을 통해 Neo4j 연결 및 측정 프로브 실행(인증 정보 미기록).
- **Neo4j 메모리 설정**:
  - 현재: `server.memory.heap.initial_size=2.00GiB`, `server.memory.heap.max_size=4.00GiB`, `server.memory.pagecache.size=1.00GiB`
  - 과거 (2026-10-18): 초기 4.00GiB / 최대 6.00GiB, pagecache 1.00GiB (동일)
- **도메인 데이터 규모 (현재 실측)**:
  - `Taxon`: 33,694개, `TraitClaim`: 174,843개, `TaxonNameVector`: 855개, `Chunk`: 4개 (Fixture 본문 171자, 357바이트).
  - 도메인 그래프 노드/관계 해시는 측정 전후 불변 확인 (`counts_mid_to_after_unchanged: true`).

| 구분 | 모드 / 질의 대상 | 표본 수 | 과거 실측 (10/18, 4G/6G) | 현재 실측 (10/22, 2G/4G) | 차이 (관측치) | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| **Chunk 검색** | Fulltext (전문) | 50회 | p50: 3.945ms / p95: 6.806ms | p50: **5.453ms** / p95: 9.535ms | +1.508ms (+38.2%) | 4개 Fixture 코퍼스 동일 |
| | Vector (벡터) | 50회 | p50: 8.920ms / p95: 18.262ms | p50: **10.901ms** / p95: 13.303ms | +1.981ms (+22.2%) | 임베딩 생성 지연 제외 |
| | Hybrid (RRF) | 50회 | p50: 9.504ms / p95: 10.851ms | p50: **11.386ms** / p95: 13.413ms | +1.882ms (+19.8%) | 정책 재확인 포함 |
| **그래프 질의** | 복합 관계 6문항 | 120회 (문항당 20) | (과거 기준선 없음) | DB 왕복: **60.3 ~ 273.7ms**<br>전체: **132.8 ~ 490.0ms** | (신규 실측) | 380 Cypher 실행, 해시 100% 일치 |
| **이름 벡터** | 저장 벡터 3종 검색 | 60회 (종당 20) | (과거 기준선 없음) | DB 왕복: **2.456 ~ 2.924ms** | (신규 실측) | self top-1 100% 일치 |
| **JVM 힙 관측** | Used Heap (스냅샷) | 3회 관측 | 전: 1,068MB / 후: 1,412MB | **303.9MB → 265.9MB → 123.0MB** | (순간 관측치) | 프로세스 RSS 아님, 최고치 아님 |
| **GC 동작** | G1 GC (mid→after) | 구간 측정 | - | Young GC: **4회 (47ms)**<br>Old GC: **0회 (0ms)** | 안정적 GC | 장기 부하 테스트 아님 |

1. **인과적 A/B 비교 불가**: 10/18과 10/22 간 힙 외의 다양한 요인이 존재하므로 관측된 지연 차이를 힙 축소의 직접적 영향으로 단정하지 않는다.
2. **힙 추가 축소 안전 확언 금지**: 본 벤치마크는 단일 스레드(동시성 1) 순차 warm 읽기 부하에 국한된다. "현재의 순차 읽기 부하 하에서 큰 성능 장애나 비정상 메모리 누수가 관측되지 않았다"는 선까지만 유효하며, 힙을 더 줄여도 안전하다거나 대규모 운영 부하를 견딜 수 있다는 결론으로 확대 해석하지 않는다.
3. **미검증 영역**: Cold cache(인스턴스 재시작 직후), 다중 동시 요청(고동시성), 장기 GC soak, OS 레벨 물리 메모리(RSS, Swap, 페이지 캐시 히트율)는 검증 대상에 포함되지 않았다.

- [[Work/RobinGraph/RobinGraph 작업 백로그|RobinGraph 전체 작업 백로그]]
- [[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 작업 백로그]] (기존 백로그 항목 상태 변경 없음, 기록 링크만 보존)
- 선행 기준선 기록: [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-18-RG101-문헌청크-검색기준선-실측|RG-101 문헌 Chunk 검색 기준선 실측 (2026-10-18)]]
- **실제 검증 자산 보존 위치** (`dev-codex`):
  `/Users/kimdove/orca/workspaces/RobinGraph/dev-codex/docs/verification/assets/2026-10-22-neo4j-heap-benchmark/`
  - 검증 요약: `summary.json`
  - Chunk 검색 실측: `chunk-current.json`
  - 도메인 그래프 실측: `graph-current.json`
  - 이름 벡터 실측: `names-current.json`
  - 런타임 중간 스냅샷: `runtime-mid.json`
  - 런타임 종료 스냅샷: `runtime-after.json`
  - 시작 전 메모리 스냅샷: `memory-before.json`
  - 과거 기준선 자산: `/Users/kimdove/orca/workspaces/RobinGraph/dev-codex/docs/verification/assets/2026-10-18-rg101/benchmark.json`

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-22-TEST-Neo4j-힙감소-성능측정]]
- [[Dev/index|Dev 인덱스]]
