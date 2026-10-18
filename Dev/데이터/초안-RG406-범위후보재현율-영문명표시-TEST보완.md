---
created: 2026-10-18
updated: 2026-10-18
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-18-RG406-범위후보재현율-영문명표시-TEST보완]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-406 범위별 후보 재현율·영문명 표시 TEST 보완 — 2026-10-18

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-18-RG406-범위후보재현율-영문명표시-TEST보완]] · 분류 근거 {"인프라":0,"자동화":1,"관측성":0,"데이터":15}

## 1. 개요 및 목적

[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/작업 백로그|4xx 채팅 UI·카드 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]]

사용자가 RG-101을 일단 보류하고 RG-406 진행을 지시했다. RG-101은 소규모 문헌 기준선 실측 결과를 온전히 보존한 보류 상태로 전환되었으며(새 문헌 축적 후 재개 판단, DB 이전이나 추가 수집 없음), Codex가 MCP 재조회로 보류 상태를 확인했다.

## 2. 핵심 아키텍처 및 원칙

- 사용자 요청과 완료 범위
- 재현 근거와 원인
- 구현과 변경 파일
- 점수·재현율 해석
- 실제 검증 결과
- TEST 배포 및 환경 격리
- 현재 상태와 남은 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 RG-101을 일단 보류하고 RG-406 진행을 지시했다. RG-101은 소규모 문헌 기준선 실측 결과를 온전히 보존한 보류 상태로 전환되었으며(새 문헌 축적 후 재개 판단, DB 이전이나 추가 수집 없음), Codex가 MCP 재조회로 보류 상태를 확인했다.

이번 작업은 RG-406 후속 과제 중 미검증으로 남아 있던 **범위별 이름 벡터 후보 재현율(전역 상위 10위 밖 누락 문제)**을 해결하고, **국외 범위 후보의 영문명(Kea) 표시 정책**을 보완하여 TEST 환경에 배포·검증한 것이다.
- **주의**: 이번 작업은 전체 RG-406의 완료가 아니며, 국내/국외/미확인 지리 판정 자료의 추가 수집이나 전 세계 종 분류 완료를 뜻하지 않는다.
- 사용자의 결과 확인 및 별도 명시 승인 전까지 운영 배포는 엄격히 금지된다.

1. **전역 10위 밖 범위 후보 누락 구조**:
   - 기존 `TaxonNameResolver`는 Neo4j 전역 ANN 검색으로 상위 10개 후보를 먼저 받은 뒤 `scope_matches`로 범위를 필터링했다.
   - 따라서 특정 범위에 속한 후보라도 전역 유사도 순위에서 11위 이하로 밀려나면, 점수 하한(0.25)을 충분히 넘기더라도 확인 후보로 선정될 수 없는 구조적 한계가 있었다.
   - 실제 TEST DB의 850개 저장 벡터에 대해 8개 질의 입력 × 3개 범위(24사례)를 전수 감사했으나, 현재 자료에서는 0.25 이상 후보가 전역 10위 밖으로 탈락한 지리 사례가 우연히 관측되지 않았다 (이를 실제 종 검색 장애 재현으로 왜곡하지 않음).
   - 대신 11개 가짜 후보 중 앞선 10개는 범위 밖, 11번째는 범위 안인 부정 회귀 테스트를 작성했다. 변경 전 HEAD resolver에서는 `not_found`로 실패했으나, 새 코드에서는 정상적으로 `candidates`로 통과함을 입증했다.
   - 실제 TEST DB에서도 허용 ID 집합을 통제한 `limit=1` 검증을 수행하여, 전역 2위 후보가 기존 코드에서는 누락되고 새 코드에서 정확히 회수됨을 확인했다 (실제 저장 벡터를 이용한 cutoff 경계 검증이며, 종의 지리적 분포 근거를 새로 판정한 것은 아님).
2. **국외 후보 영문명 표시 누락**:
   - 실제 API에서 국외 범위 선택 후 `높은산앵무아` 입력 시, 후보가 영어 우선 정책에 반하여 한국어 `높은산앵무`로 표시되는 결함을 확인했다.
   - 후보 inventory 구조가 한국어 표시명만 유지하고 있어 기존 `with_species_scope` 호출 시 영어 이름이 전달되지 못했기 때문이었다.
   - 재검증된 그래프 종 노드의 `english_name`을 추출하여 `Kea`로 정확히 표시되도록 수정했다.

- `src/robingraph/retrieval/taxon_name_resolution.py`:
  - 선택된 범위에 해당하는 reviewed inventory ID 집합을 저장소에 전달.
  - 전체 inventory도 함께 전달하여 catalog fingerprint 검증 유지.
  - 후보 회수 후에도 범위를 재확인하고, 최대 10개 그래프 재검증, 최대 3개 제안, 기존 cosine 하한(0.25) 및 철자 보완 하한(0.20) 조건을 엄격히 유지.
  - `_verified_target`에서 LineageTaxon의 영문명을 추출하여 국외 후보 표시명에 적용.
- `src/robingraph/retrieval/taxon_name_vectors_neo4j.py`:
  - `eligible_taxon_ids` 인자 추가.
  - `all`(전체) 범위는 기존의 효율적인 전역 ANN 경로를 유지.
  - 특정 선택 범위는 해당 ID 집합의 저장 벡터에 `vector.similarity.cosine`을 적용하고 정렬 후 limit을 적용(현재 reviewed inventory 상한 1,000개 내에서 exact cosine 계산).
  - index, profile, catalog fingerprint, 활성 concept set, graph link, 본문 hash guard 일체 보존.
  - 알 수 없는 ID 거부, 빈 범위 입력 시 빈 후보 반환, 잘못 반환된 범위 밖 hit 차단 로직 적용.
- `tests/test_taxon_name_resolution.py`, `tests/test_taxon_name_vectors_neo4j.py`:
  - 전역 cutoff 이후 후보 복구, 빈 범위, ID guard, stale catalog, 범위 밖 hit 차단, 검증 영문명 표시 단위 테스트 추가.

1. **회귀 및 자동화 테스트**:
   - Python 전체 검사: 939개 실행 중 **901개 통과, 38개 skip, 실패 0**.
   - Node UI 단위 검사: **317개 통과, 실패/skip 0** (이번 작업에서 UI 자산 변경 없음).
   - 기존 코드 부정 회귀: 전역 11위 범위 후보의 `not_found` 실패 확인 (`before-regression.txt`).
2. **실제 TEST Neo4j / Jina 검증**:
   - 8개 입력 × 3개 범위 = 24사례 Python oracle 대조 통과.
   - 통제된 `limit=1` / `global-rank=2` cutoff 복구 검증 통과.
   - 배포된 코드에서 24회 scoped repository 검색 지연: median 21.182 ms / max 58.25 ms (단발 지연 측정이며 성능 보장 주장이 아님).
3. **TEST 내부 API 검증 (전후 각 5요청)**:
   - 국외 범위 `높은산앵무아` → `Kea` (영문명 정상 적용).
   - 국내 범위 `청둥오리아`, `천둥오리` → `청둥오리` (국명 정상 적용).
   - 미확인 범위 `타조아` → `타조` (국명 정상 적용).
   - 국외 범위에서 `청둥오리아` 요청 시 후보 없음(`abstain`) 정상 유지.
4. **공개 TEST 브라우저 UI 검증 (Chromium 1280px, 390px, 320px)**:
   - 각 화면 폭별 3회 요청 = 총 9POST 검증 통과.
   - 후보 이름 정상 렌더링, scope 파라미터 전달, 가로 넘침(horizontal overflow) 없음, console/page error 0건 확인.
5. **무결성 및 배포 검증**:
   - TEST health 및 API 계약 검사(/birds/mallard/lineage GET) 통과.
   - 배포된 두 Python 파일의 SHA-256 해시가 로컬 수정 소스와 100% 일치.
   - `graphify update .` AST 갱신 완료.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-18-RG406-범위후보재현율-영문명표시-TEST보완]]
- [[Dev/index|Dev 인덱스]]
