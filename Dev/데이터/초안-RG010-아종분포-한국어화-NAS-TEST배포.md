---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-07-RG010-아종분포-한국어화-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-503 — 아종 분포 설명·설명용 제목 한국어화

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-07-RG010-아종분포-한국어화-NAS-TEST배포]] · 분류 근거 {"인프라":1,"자동화":1,"관측성":1,"데이터":7}

## 1. 개요 및 목적

2026-10-07 사용자가 Obsidian 백로그의 RG-503을 먼저 진행하도록 요청했다. 기준선은 AviList v2025b의 아종 19,879개, 한국어 분포 6개, 영어 원문 19,873개였다. 목표는 종별 예외 코드 대신 공통 생성·검토·조회 경로로 한국어 분포 설명과 설명용 제목을 제공하고, ID·학명·분류판·원문 해시가 달라지면 기존 번역을 재사용하지 않는 것이다. 정식 국명 수집은 RG-504이며 이번 설명용 제목을 국명으로 등록하지 않는다.

현재 상태는 **RG-503 일부 적용 완료·전체 한국어 검토 미완료·최후순위 보류**이다. 공통 구현·1차 적용·NAS TEST 배포와 당시 검증은 완료했지만, 1,109개만 검토했고 18,770개는 미검토다. 사용자 재개 지시 전까지 현재 TEST 상태로 유지한다. 이후 검증 결과와 커밋 정보는 아래 최종 기록으로 갱신한다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 확인한 원인과 근거
- 변경 전후 동작
- 변경 파일과 구현
- 전수 처리·검토 범위
- 검증 방법과 실제 결과
- 배포·커밋 정보
- 한계와 후속 사항
- 협업 결과와 의견 반영
- 최종 검증 결과
- 증거 파일
- 최종 배포·커밋 정보
- 후속 상태 정정 및 Git 반영 — 2026-10-07

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
python scripts/build_subspecies_ranges.py --snapshot AVILIST_JSON --report report.json --ledger ledger.jsonl --check
python scripts/audit_subspecies_display.py --snapshot AVILIST_JSON --output display-audit.json
python -m unittest discover -s tests -v
node --test tests/frontend/*.test.js
graphify update .
```

## 4. 검증 근거 및 트러블슈팅

현재 상태는 **RG-503 일부 적용 완료·전체 한국어 검토 미완료·최후순위 보류**이다. 공통 구현·1차 적용·NAS TEST 배포와 당시 검증은 완료했지만, 1,109개만 검토했고 18,770개는 미검토다. 사용자 재개 지시 전까지 현재 TEST 상태로 유지한다. 이후 검증 결과와 커밋 정보는 아래 최종 기록으로 갱신한다.

- `src/robingraph/retrieval/subspecies.py`에 청둥오리 두 아종의 요약과 왜가리 네 아종의 외부 분포 설명이 하드코딩되어 있었다. 다른 아종은 AviList 영어 원문을 표시했다.
- 왜가리 예외는 ID·학명·분류판을 확인하지만 실제 조회된 분포 원문 변경과 결합되어 있지 않았다. 새 구조는 원문 해시까지 확인한다.
- 청둥오리 기준 아종의 기존 짧은 요약은 AviList의 상세 번식·월동 범위, 널리 도입된 분포 및 현지 동속 조류와의 교잡 내용을 모두 전달하지 않았다. 새 설명은 이 한정 정보를 보존한다.
- 고정 공식 자료: https://explore.avilist.org/data/avilist-2025b.json. SHA-256 `3b08845b54b8ab53908aee84d05b0fd8df765e9e01dc655599ca304d9f132411`. 실행 중 실제 내려받아 해시를 확인했다. 원자료는 CC BY 4.0이며 아종 이름 자체의 다른 출처·권리는 기존처럼 구분한다.
- 기존 Graphify 산출물이 checkout에 없었다. 소스와 작업 기록을 확인한 후 `graphify update .`로 AST 그래프를 생성했다.

| 상황 | 변경 전 | 변경 후 |
|---|---|---|
| 검토 자료가 있는 아종 | 두 종의 전용 예외에 한정 | 동일 원문 표현을 공유하는 모든 아종에 ID별 검토 레코드 생성 |
| 분포 원문 변경 | 왜가리의 외부 설명 예외 유지 가능 | `stale-review`, 영어 원문 표시 |
| 분류판·개념집합·학명 변경 | 예외별 조건 | 공통 확인, 불일치 번역 재사용 차단 |
| 이름 없는 아종 | 부모 이름 + 영어 분포 캡션 | 검토된 한국어 설명용 제목; 별도 국명 필드 생성 안 함 |
| 미검토·충돌·번역 실패 | 명시적 처리 상태 없음 | 상태 구분, 영어 원문 유지 |
| 자료 없음 | 분포 미확인 안내 | 기존 안내 유지, `missing-source` 상태 |
| 목록·선택 카드·채팅 | 공통 표시 함수 + 종별 예외 | 동일한 공통 검토 자료와 표시 함수 |

- `src/robingraph/retrieval/subspecies_ranges.py`: 오프라인 검토 자료 로딩, ID·학명·분류판·개념집합·정규화 원문 SHA-256 확인, reviewed/pending-review/stale-review/conflict/translation-failed/missing-source/invalid-review 판정. 검토 상태와 필요한 필드가 유효한 경우만 한국어 표시.
- `src/robingraph/retrieval/subspecies_range_reviews.json`: 런타임에 포함되는 ID별 한국어 설명·캡션·원문 해시·검토 주체와 방법. 요청 처리 중 외부 번역 API를 호출하지 않는다.
- `data/review/subspecies-range-ko.json`: 완전 일치하는 원문 표현을 기준으로 재사용하는 1차 한국어 원문 대조 자료. 특정 종에 대한 조건문이나 별도 분포 사전을 추가하지 않는다. 새 후보는 명시적 reviewed 상태가 없으면 검토 완료로 승격하지 않는다.
- `scripts/build_subspecies_ranges.py`: 고정 자료 해시 확인, 모든 아종의 처리 원장과 집계 생성, 검토 자료 생성 및 `--check` 바이트 재현 검증. 원문에 매칭되지 않는 검토 표현·중복 ID·잘못된 상태를 거부한다.
- `src/robingraph/retrieval/subspecies.py`: 이전 종별 예외 제거, 공통 검토 결과 연결, 영어 원문·출처 유지. 검토된 제목을 길이 때문에 잘라 멸종·도입 등 한정 표현을 없애지 않는다.
- `scripts/audit_subspecies_display.py`: 기존 전수 표시 감사에 검토 상태별 집계 추가.
- `tests/test_subspecies.py`, `tests/test_subspecies_ranges.py`: 실제 출처 원문을 쓰는 왜가리 fixture 및 원문 변경·불일치·후보 보류·멸종·계절·도입·잠정 표현·목록/프로필 일치 회귀 검증.
- 기존 프런트엔드가 API의 공통 설명·캡션과 영어 원문 출처 상세를 사용하므로 제품 JS/CSS 변경은 필요하지 않았다.

| 구분 | 수 |
|---|---:|
| 전체 처리 대상 | 19,879 |
| 한국어 원문 대조 적용 | 1,109 |
| 미검토·영어 원문 유지 | 18,770 |
| 확인된 충돌 | 0 |
| 번역 실행 실패 | 0 |
| 원문 분포 없음 | 0 |
| 원문 대조한 고유 표현 | 137 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-07-RG010-아종분포-한국어화-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
