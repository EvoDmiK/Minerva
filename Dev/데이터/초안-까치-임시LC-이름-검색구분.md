---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-09-까치-임시LC-이름-검색구분]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 까치 LC 임시 표시와 두 까치 종의 이름·검색 구분

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-09-까치-임시LC-이름-검색구분]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":0,"데이터":8}

## 1. 개요 및 목적

사용자는 까치를 우선 LC로 표시하도록 요청했다. 이름 표기 요청의 최종 기준은 **Pica pica → Eurasian magpie**, **Pica serica → 까치 / Oriental magpie**, **한국어 ‘까치’ 검색 → Pica serica**다. 두 종의 분류·종 ID를 합치지 않고 앱의 표시·검색 정책을 명시적으로 적용한다.

기존 Pica serica는 활성 AviList v2025b 원자료 NE로, 평가 자료 연결 확인 필요 상태였다. Pica pica 역시 실제 NAS TEST 프로필의 원자료는 NE이며 한국어 표시는 없었다. GBIF 목록의 Pica pica LC를 앱 종에 자동 연결한 상태가 아니었다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 최종 목표
- 확인한 원인과 변경 전후
- 구현 파일
- 협업과 검증
- 실제 서비스 검증 결과
- 배포·커밋과 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

기존 Pica serica는 활성 AviList v2025b 원자료 NE로, 평가 자료 연결 확인 필요 상태였다. Pica pica 역시 실제 NAS TEST 프로필의 원자료는 NE이며 한국어 표시는 없었다. GBIF 목록의 Pica pica LC를 앱 종에 자동 연결한 상태가 아니었다.

최종 변경 후 Pica serica의 앱 표시 등급은 LC, 배지는 **‘관심대상 (LC) · 임시 보정’**이다. `manual_override`로 저장하며 `independently_verified=false`, 원자료 NE·출처·해시·연결 검토 상태는 `original_snapshot`에 그대로 보존한다. 평가 원문을 새로 확인한 결과나 GBIF 연결 결과로 표현하지 않는다. 답변 출처 보기에 사용자 요청에 따른 보정 사유와 기존 AviList 자료를 표시한다.

- `retrieval/conservation.py`, `species_profile.py`: 검증된 AviList NE의 Pica serica 한 종에만 사용자 지정 LC 표시를 적용한다. 공개 평가 연결을 먼저 시도하고 기존 원본을 별도 객체로 보존한다.
- `api/static/chat.js`: 정확한 임시 보정 계약·종 ID·학명·원본 해시가 맞을 때 LC 색을 적용한다. 평가 검증 플래그는 false로 유지하며 보정 배지와 출처 설명을 제공한다. 다른 NE와 카드 제스처·배치는 유지한다.
- `retrieval/taxonomy_lineage.py`: 두 종의 영어 표시 대소문자를 지정하고 source-checked 한국어 이름과 구분한다. 반복 변환에도 같은 결과를 반환한다. 공식 이름 JSON은 변경하지 않았다.
- `retrieval/taxonomy_lineage_neo4j.py`: 한국어 ‘까치’를 활성 Pica serica의 정확한 종으로 연결하며 분류 컨텍스트·반환 종을 검증한다.
- `tests/test_conservation.py`, `tests/test_korean_display_names.py`, `tests/test_taxonomy_lineage_neo4j.py`, `tests/frontend/chat_ui.test.js`: 다른 종·새 릴리스·잘못된 ID·원자료 변조·이름 반복 변환·검색 대상 경계 회귀.
- `README.md`: 현재 임시 보정과 최종 이름·검색 정책을 설명한다.

경로는 모두 `src/robingraph/` 기준인 구현 파일과 저장소 루트의 테스트·README다. 근연종·생태 후보 선택은 원래 source-checked 한국어 이름 목록을 유지한다. 두 종을 같은 한국어 후보로 만드는 중간 변경도 되돌렸다.

부모가 backend·검색·배포를 담당했고 `quality_audit_report`가 임시 LC 화면·frontend 검사와 최종 두 이름의 렌더러를 검토했다. 모의 DOM에서 Pica pica는 영어 주제목과 별도 학명, Pica serica는 한국어 제목과 작은 영어 이름으로 구분됨을 확인했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-09-까치-임시LC-이름-검색구분]]
- [[Dev/index|Dev 인덱스]]
