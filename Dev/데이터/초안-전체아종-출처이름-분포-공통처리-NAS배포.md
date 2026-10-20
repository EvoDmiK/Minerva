---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-06-전체아종-출처이름-분포-공통처리-NAS배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 전체 아종 이름·분포 공통 처리와 출처 수집 — 2026-10-06

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-06-전체아종-출처이름-분포-공통처리-NAS배포]] · 분류 근거 {"인프라":4,"자동화":4,"관측성":3,"데이터":12}

## 1. 개요 및 목적

사용자는 청둥오리·왜가리만 고치는 방식이 아니라 다른 종의 아종들도 확인된 한국어·영어 이름과 출처 있는 분포로 표시하도록 요청했다. Claude·Antigravity와 실제 협업하고 상세 작업 문서, Obsidian 기록, Git 커밋·푸시 및 기존 NAS TEST 배포 흐름을 이어간다. 임의 한국어 작명, 과거 분류명의 무조건적인 현재 종 치환, 학명을 숨겨 종 정체성을 잃는 처리는 허용하지 않는다.

기존 AviList 분류 수집은 이미 아종의 분포문을 적재하고 있었다. 그러나 API가 이를 목록에 내보내지 않고 수동 검토한 청둥오리 두 아종·왜가리 네 아종만 보완해 다른 종은 구분 정보가 부족했다. AviList v2025b 원자료를 새로 내려받아 이전 캐시와 바이트 일치를 확인했다. 공식 JSON은 19,933,159바이트, SHA-256 `3b08845b54b8ab53908aee84d05b0fd8df765e9e01dc655599ca304d9f132411`이다.

## 2. 핵심 아키텍처 및 원칙

- 배경과 목표
- 원인과 전체 자료 확인
- 협업과 책임
- 공통 구현
- 검증 범위
- 한계
- 변경 파일과 검증 책임
- 화면 검증 자료
- 자료 수집 방식과 배포 범위
- 최종 이름 자료와 전수 감사 결과
- 최종 테스트 결과와 재현
- NAS TEST 배포와 공개 HTTP 검증

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
ROBINGRAPH_SUBSPECIES_SOURCE_DIR=DIR uv run --locked --extra test --extra tracing --with pypdf==6.19.0 --with cryptography==50.0.2 python -m unittest discover -s tests -v
node --test tests/frontend/*.test.js
uv run --locked --extra test python scripts/audit_subspecies_display.py --output report.json
uv run --no-project --with pypdf==6.19.0 --with cryptography==50.0.2 python scripts/build_subspecies_names.py --cache-dir DIR --offline --check
```

## 4. 검증 근거 및 트러블슈팅

사용자는 청둥오리·왜가리만 고치는 방식이 아니라 다른 종의 아종들도 확인된 한국어·영어 이름과 출처 있는 분포로 표시하도록 요청했다. Claude·Antigravity와 실제 협업하고 상세 작업 문서, Obsidian 기록, Git 커밋·푸시 및 기존 NAS TEST 배포 흐름을 이어간다. 임의 한국어 작명, 과거 분류명의 무조건적인 현재 종 치환, 학명을 숨겨 종 정체성을 잃는 처리는 허용하지 않는다.

기존 AviList 분류 수집은 이미 아종의 분포문을 적재하고 있었다. 그러나 API가 이를 목록에 내보내지 않고 수동 검토한 청둥오리 두 아종·왜가리 네 아종만 보완해 다른 종은 구분 정보가 부족했다. AviList v2025b 원자료를 새로 내려받아 이전 캐시와 바이트 일치를 확인했다. 공식 JSON은 19,933,159바이트, SHA-256 `3b08845b54b8ab53908aee84d05b0fd8df765e9e01dc655599ca304d9f132411`이다.

- Claude Task `task_5ba506a07b6b` / Dispatch `ctx_4b8469d56908`: 전체 원자료와 1차 이름 출처를 대조해 정확한 아종 학명에 연결할 수 있는 영어 통칭을 수집하고 생성 스크립트·참고 JSON·검증·상세 출처 문서를 작성한다. 런타임·DB·배포는 수정하지 않는다.
- Antigravity Task `task_5534b0dc6360` / Dispatch `ctx_d28a979f129e`: 전체 데이터 가용성, 공통 폴백, 모바일, 출처 분리, 선택 프로필 검토. 읽기 전용 검토 성공 보고를 받았고 세션을 release했다. 보고서 `2026-10-06-subspecies-global-ux-review.md`. 전수 원자료 검사와 모의 테스트를 실제 DB 검사로 혼동하지 않는다.
- Codex(코디네이터): 공통 API/프로필/UI 구현, 통합 검증, 전체 NAS TEST 그래프 읽기 검사, 배포 및 문서 동기화.

Antigravity는 왜가리 외부 분포 설명의 출처가 AviList와 다르다는 이유로 카드 앞면에서 제외되는 결함도 발견했다. 이를 실제로 수정하고 안전한 외부 출처는 표시하되 위험한 URL은 제외하는 회귀 테스트를 추가했다. 검토 보고서의 일부 표현은 코디네이터가 정정했다. 원자료의 한국어 열 부재는 전 세계 공식 한국어 아종명의 부재를 입증하지 않으며, Parus major는 현재 한국의 박새 Parus cinereus와 구분해야 한다. 고정 스냅샷의 제목 중복 0건도 미래 자료의 구별성을 보장하지 않는다.

표시 우선순위는 확인된 한국어 이름 → 출처 있는 영어 이름 → 부모 종의 일반명과 분포 설명용 캡션이다. 캡션은 통칭 필드와 분리한 display_label이며 이름이 없는 아종에 대해서만 쓰인다. 첫 분포 절을 72자까지 제목으로 쓰고 전체 원문은 보존한다. 제목이 같으면 목록 번호를 추가해 구별한다. 아종 선택 시 프로필과 카드의 제목에도 같은 공통 표시 필드를 사용한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/5xx 데이터·분류·이름/2026-10-06-전체아종-출처이름-분포-공통처리-NAS배포]]
- [[Dev/index|Dev 인덱스]]
