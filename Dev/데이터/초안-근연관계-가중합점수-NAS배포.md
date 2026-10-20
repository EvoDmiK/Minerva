---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-06-근연관계-가중합점수-NAS배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 근연 관계 가중합 점수 · NAS TEST 배포

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-06-근연관계-가중합점수-NAS배포]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":0,"데이터":8}

## 1. 개요 및 목적

계통 관계 50%, 분류 관계 30%(같은 속 20%·같은 과 10%), 서식 환경 10%, 먹이 생태 10%로 변경했다. `taxonomy-phylogeny-ecology-v3`이며 표시 점수 내림차순으로 순위를 정한다.

공통 조상 depth의 숫자 간격 대신 확인된 서로 다른 공통 조상 단계의 상대 순서 k/N으로 계통 기여를 계산한다. 같은 조상은 같은 점수다. 계통 자료가 없으면 해당 항목을 제외하고 나머지 50%를 100점으로 환산해 ‘분류·생태 대체 점수(계통 자료 부족)’로 표시한다. 초기 서비스 가중치이며 진화 거리·유전 유사도·확률의 측정값은 아니다.

## 2. 핵심 아키텍처 및 원칙

- 검증
- 배포

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

공통 조상 depth의 숫자 간격 대신 확인된 서로 다른 공통 조상 단계의 상대 순서 k/N으로 계통 기여를 계산한다. 같은 조상은 같은 점수다. 계통 자료가 없으면 해당 항목을 제외하고 나머지 50%를 100점으로 환산해 ‘분류·생태 대체 점수(계통 자료 부족)’로 표시한다. 초기 서비스 가중치이며 진화 거리·유전 유사도·확률의 측정값은 아니다.

- Python 549개 모두 통과, 실패·오류·건너뛰기 0. 실제 Neo4j/PostgreSQL 통합 포함.
- 프런트엔드 126개 모두 통과.
- 상대 단계 정규화·같은 조상 동점·소수점 표시·대체 점수·기여 합 검증.
- 기존 Fixture 555개·논문 노드 168개 유지. 임시 DB 컨테이너·스키마·터널·인증 파일 정리.

Runtime commit `f1a1e60d063b0b4632cbb38fa20e559993d1b716`, origin/dev push 완료. NAS `/home/kimdove/RobinGraph-weighted-f1a1e60`, image `robingraph-api:test-weighted-f1a1e60` healthy. 전송 해시·manifest 107개 파일·OCI revision 확인. TEST preflight/update/verify와 공개 계약 검증 passed=true. PROD 유지.

공개 API에서 오리·해오라기·박새·매류·비둘기 5종의 v3·가중치·점수순·기여 합을 검증했다. 흰뺨검둥오리 후보: 청둥오리 100, Indian Spot-billed Duck 100, Philippine Duck 98.21. Parus major는 작은노랑배박새 88.48, 박새(Parus cinereus) 80으로, 가중합에서는 생태 가점도 최종 순위에 영향을 준다. 계통 자료가 없는 Nycticorax mauritianus 조회는 상위 후보 모두 분류·생태 대체 점수 60으로 표시됨을 확인했다. 채팅도 v3 및 소수점 점수를 반환한다.

상세 계약: 저장소 `docs/phylogenetic-relations.md`. 배포 검증: `docs/verification/2026-10-06-weighted-phylogenetic-score.md`.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-06-근연관계-가중합점수-NAS배포]]
- [[Dev/index|Dev 인덱스]]
