---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-카드-토글-스크롤-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 도감 카드 뒷면 토글을 열면 스크롤(NAS TEST·PROD 배포)

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-카드-토글-스크롤-TEST배포]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":2,"데이터":6}

## 1. 개요 및 목적

사용자가 뒷면 스크린샷(집비둘기 카드, `측정값 더 보기 (7)` 열림)을 보내며, "측정값 더 보기"와 "분류 계통 보기" 토글을 열었을 때는
카드가 스크롤되었으면 좋겠다고 요청했다. TEST에서 확인한 뒤 사용자의 지시로 PROD 배포와 `main` 병합까지 진행했다.

카드는 항상 "프레임 높이에 맞춰 통째로 축소"되도록 만들어져 있었다(이전 RG-405 작업에서 카드 내부 스크롤을 없애고 맞춤으로 바꿨다).
`chat.js`의 `fitCard()`가 `scale = min(1, 프레임너비/카드너비, 프레임높이/카드높이)`로 계산한다. 토글을 열면 카드 높이가 늘어
`프레임높이/카드높이`가 작아지고, 그 결과 카드 전체가 작아져 글씨가 읽기 어려워졌다. 스크롤은 `.species-card-fit-frame { overflow: clip; }`으로
막혀 있었고, 모바일에서는 `touch-action: pinch-zoom`이라 세로 팬도 막혀 있었다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 원인
- 변경 전후 동작
- 구현
- 검증 (실제 실행 결과)
- 배포·커밋 정보
- 남은 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 뒷면 스크린샷(집비둘기 카드, `측정값 더 보기 (7)` 열림)을 보내며, "측정값 더 보기"와 "분류 계통 보기" 토글을 열었을 때는
카드가 스크롤되었으면 좋겠다고 요청했다. TEST에서 확인한 뒤 사용자의 지시로 PROD 배포와 `main` 병합까지 진행했다.

| 파일 | 내용 |
|---|---|
| `src/robingraph/api/static/chat.js` | 두 토글(`측정값 더 보기`, `분류 계통 보기`)에 `card-details-scroll` 표식 클래스를 추가. `fitCard()`는 표식 토글이 열려 있으면 너비만 기준으로 scale을 정하고(`scrollToggleOpen()`), 프레임에 `data-fit-scroll="true"`를 설정한다. scale이 1 미만이면 축소된 높이만큼 `margin-bottom`을 음수로 줘서 스크롤 범위가 실제로 보이는 크기와 같게 한다. 맞춤 모드로 돌아가거나 면을 뒤집거나 다시 열면 스크롤을 0으로 되돌린다(`card.resetFitScroll`). 프레임 스크롤 시 도넛 툴팁을 닫는다 |
| `src/robingraph/api/static/styles.css` | `.species-card-fit-frame[data-fit-scroll="true"]`에서만 `overflow-y: auto`, `overscroll-behavior: contain`, 스크롤바 숨김(기존 디자인 방침 유지). 그 안의 카드에는 `touch-action: pan-y pinch-zoom`을 줘서 세로 스크롤은 브라우저가 처리하고 좌우 스와이프 뒤집기는 그대로 JS가 처리한다 |
| `tests/frontend/chat_ui.test.js` | 신규 4개: 토글 열림 시 축소 안 함·닫으면 복귀·스크롤 0 복귀, 좁은 프레임에서 너비 기준 scale과 `margin-bottom` 보정, 뒤집기 시 스크롤 초기화, 표식 클래스와 CSS 규칙 존재(기본 프레임의 `overflow: clip`은 유지) |

설계 결정: 기본 상태의 `overflow: clip`은 그대로 두고 토글이 열린 동안에만 스크롤을 허용했다. 그래서 이전 작업들이 검증한 "평소엔 스크롤 없음" 동작은 바뀌지 않는다.
카드 DOM을 조회하는 `querySelectorAll`이 없는 환경(기존 테스트의 가짜 DOM)에서는 예전 동작으로 처리하도록 방어했다.

| 항목 | 결과 |
|---|---|
| 프런트엔드 `node --test tests/frontend/*.test.js` | 252개 통과, 실패 0(기존 248개 + 신규 4개). 모의 DOM 검증 |
| Python 전체 `unittest discover` | 641개 중 통과, 건너뜀 35(기존 DB 옵트인), 실패 0 |
| 실제 Chrome(헤드리스, CDP) — 로컬 서버가 TEST Neo4j를 읽음, 외부 LLM·MLflow 비활성, 흰뺨검둥오리 카드, 토글 2개 모두 열고 측정 | **PC 1280×800**: 닫힘 scale 1·스크롤 없음(`overflow-y: clip`) → 열림 scale 1 유지·`scrollHeight 988 > clientHeight 744`·`overflow-y: auto`. 마우스 휠로 `scrollTop 244`(끝까지). 끝에서 카드 아래 테두리가 프레임 아래와 0px 차이로 정확히 닿음. 뒤집으면 `scrollTop 0`. 토글을 닫으면 다시 `clip`·`scrollTop 0`. 스크린샷으로 분류 계통 목록까지 잘리지 않음을 확인. **모바일 390×844(터치 에뮬레이션)**: scale 0.833(너비 기준) 유지, 터치 스와이프로 `scrollTop 17`(끝까지), 뒤집기·닫기 후 복귀 동일 |
| NAS TEST 배포 | 이미지 `robingraph-api:test-cardscroll-5fb401e`, healthy, 재시작 0, OCI revision `5fb401e…`, `verify` ok(`deployment_target: test`). 서빙되는 `chat.js`에 `card-details-scroll` 3곳, CSS에 `data-fit-scroll` 규칙 확인 |
| PROD 배포 | 같은 릴리스 묶음(`5fb401e`)으로 이미지 `robingraph-api:prod-5fb401e`. 15:30:33 시작, 15:30:41 종료. healthy, 재시작 0, OCI revision `5fb401e…`, `verify` ok(`deployment_target: prod`). `JEV_API_KEY`·`GEMINI_API_KEY`·`ROBINGRAPH_INTENT_ROUTER`가 컨테이너 환경에 설정됨을 이름으로 확인 |
| PROD `verify_api_deployment.py` | `passed: true`, `contract_parity_ok` true |
| PROD 서빙 자산 | `chat.js`에 `card-details-scroll` 3곳, CSS에 `data-fit-scroll` 규칙 확인 |

- 구현 커밋 `5fb401ebbe9963baa9e8fa56ba8da4ffbfb21bd2`(`dev-claude`). 릴리스 묶음 SHA-256 `fa949c6db69e7417d425f9e2af4ae05ce4ad6c7813baf83a345eaf2e19f44a04`, NAS 일치·MANIFEST 불일치 0.
- NAS 체크아웃 `~/RobinGraph-5fb401e`. TEST env는 직전 TEST env(`~/RobinGraph-336d987/.env.nas.test`)를 복사해 이미지 태그와 `ROBINGRAPH_VCS_REF`만 변경했다.
- PROD: `~/RobinGraph-5fb401e/.env.nas.prod`는 직전 PROD env(`~/RobinGraph-336d987/.env.nas.prod`)를 NAS 안에서 복사해 이미지 태그와 `ROBINGRAPH_VCS_REF`만 바꿨다. PROD 이미지 `robingraph-api:prod-5fb401e`.
- 롤백: 직전 PROD 이미지 `robingraph-api:prod-336d987`이 NAS에 있다. `cd ~/RobinGraph-5fb401e && ROBINGRAPH_DEPLOY_TARGET=prod sh scripts/deploy_nas.sh rollback robingraph-api:prod-336d987`(실행하지 않음).
- `main` 병합은 병합 커밋으로 반영했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-카드-토글-스크롤-TEST배포]]
- [[Dev/index|Dev 인덱스]]
