---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-토글-스크롤-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 도넛 차트 아래 항목·비율 토글도 스크롤(NAS TEST·PROD 배포)

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-토글-스크롤-TEST배포]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":1,"데이터":2}

## 1. 개요 및 목적

사용자가 뒷면 도넛 차트 아래의 `▶ 항목·비율` 토글(스크린샷)을 열어도 카드가 축소되지 않고 비율을 유지한 채 스크롤되도록 해 달라고 요청했다.
"ponytail을 이용해서"라는 지시에 따라 Ponytail 방식(공식 저장소 `DietrichGebert/ponytail` revision `9cc65d0`의 `ponytail` SKILL, "요청을 완전히 해결하는 가장 작은 변경, 새 추상화·옵션 없음")으로 진행했다.
Ponytail SKILL.md는 새 빈 임시 디렉터리에 받아 읽기만 했고 설치하거나 그 안의 코드를 실행하지 않았다.
TEST에서 확인한 뒤 사용자의 지시로 네 변경(항목·비율 스크롤, TEST 파란 파비콘 코드, 프레임 두께, 항목·비율 목록 디자인)을 한꺼번에 PROD에 배포하고 `main`에 병합했다.

앞서 `측정값 더 보기`·`분류 계통 보기`에 적용한 스크롤 모드([[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-카드-토글-스크롤-TEST배포|카드 토글 스크롤 기록]])는 `fitCard()`가 `.card-details-scroll` 표식이 붙은 열린 토글을 찾을 때만 켜진다.
`항목·비율`은 `species-distribution-values` 클래스의 `<details>`라 표식이 없어 기존 방식(카드 전체를 프레임 높이에 맞춰 축소)이 그대로 적용됐다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 원인과 접근
- 변경 내용
- 변경 전후 동작
- 검증 (실제 실행 결과)
- 배포·커밋 정보
- 남은 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 뒷면 도넛 차트 아래의 `▶ 항목·비율` 토글(스크린샷)을 열어도 카드가 축소되지 않고 비율을 유지한 채 스크롤되도록 해 달라고 요청했다.
"ponytail을 이용해서"라는 지시에 따라 Ponytail 방식(공식 저장소 `DietrichGebert/ponytail` revision `9cc65d0`의 `ponytail` SKILL, "요청을 완전히 해결하는 가장 작은 변경, 새 추상화·옵션 없음")으로 진행했다.
Ponytail SKILL.md는 새 빈 임시 디렉터리에 받아 읽기만 했고 설치하거나 그 안의 코드를 실행하지 않았다.
TEST에서 확인한 뒤 사용자의 지시로 네 변경(항목·비율 스크롤, TEST 파란 파비콘 코드, 프레임 두께, 항목·비율 목록 디자인)을 한꺼번에 PROD에 배포하고 `main`에 병합했다.

앞서 `측정값 더 보기`·`분류 계통 보기`에 적용한 스크롤 모드([[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-카드-토글-스크롤-TEST배포|카드 토글 스크롤 기록]])는 `fitCard()`가 `.card-details-scroll` 표식이 붙은 열린 토글을 찾을 때만 켜진다.
`항목·비율`은 `species-distribution-values` 클래스의 `<details>`라 표식이 없어 기존 방식(카드 전체를 프레임 높이에 맞춰 축소)이 그대로 적용됐다.

1. 새 기능이 아니라 기존 스크롤 모드의 대상 확대다 → 새 로직·옵션 없이 기존 메커니즘 재사용.
2. 처음에는 `항목·비율` `<details>`에 `card-details-scroll` 클래스를 추가하려 했으나, 기존 테스트가 `className === "species-distribution-values"`로 정확히 비교한다
   (`tests/frontend/chat_ui.test.js:1955`). 클래스를 바꾸면 테스트와 스타일 선택자까지 건드리게 되므로 **클래스는 그대로 두고 `fitCard()`의 선택자만 한 줄 확장**했다.

| 파일 | 내용 |
|---|---|
| `src/robingraph/api/static/chat.js` | `scrollToggleOpen()`의 `card.querySelectorAll(".card-details-scroll")`를 `".card-details-scroll, .species-distribution-values"`로 변경. 설명 주석에 `항목·비율` 추가 |
| `tests/frontend/chat_ui.test.js` | 가짜 DOM이 기대하는 선택자 문자열을 갱신하고, 소스에 확장된 선택자가 있는지 확인하는 단정 1줄 추가 |

| 항목 | 결과 |
|---|---|
| 프런트엔드 `node --test tests/frontend/*.test.js` | 252개 통과, 실패 0(모의 DOM) |
| Python 전체 | 641개 중 통과, 건너뜀 35(기존 DB 옵트인), 실패 0 |
| 실제 Chrome(헤드리스, CDP), 로컬 서버가 TEST Neo4j를 읽음(외부 LLM·MLflow 비활성), 청둥오리 카드, 두 `항목·비율` 모두 열고 측정 | **PC 1280×800**: 닫힘 scale 0.966·스크롤 없음 → 열림 scale 1·`scrollHeight 958 > clientHeight 744`·`overflow-y: auto`. 마우스 휠로 `scrollTop 214`(끝까지), 카드 아래 테두리와 프레임 아래가 0px 차이. 뒤집으면 `scrollTop 0`, 닫으면 scale 0.966·`overflow-y: clip`·`scrollTop 0` 복귀. 스크린샷에서 두 항목 목록(11개·7개 항목)과 아래 두 토글까지 잘리지 않음. **모바일 390×844 에뮬레이션**: scale 0.833 유지, 열어도 내용이 카드 높이 여유 안에 들어가 `scrollHeight 796 = clientHeight`(스크롤 불필요), 스크롤 모드와 복귀는 정상 |
| NAS TEST 배포 | 이미지 `robingraph-api:test-chartscroll-c305f7f`, healthy, 재시작 0, OCI revision `c305f7f…`, `verify` ok(`deployment_target: test`), 서빙되는 `chat.js`에 확장 선택자 확인 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-토글-스크롤-TEST배포]]
- [[Dev/index|Dev 인덱스]]
