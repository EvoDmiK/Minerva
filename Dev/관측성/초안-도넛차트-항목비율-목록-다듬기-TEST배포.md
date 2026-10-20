---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-목록-다듬기-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 도넛 차트 항목·비율 목록 다듬기와 자료 N 제거(NAS TEST·PROD 배포)

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-목록-다듬기-TEST배포]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":1,"데이터":1}

## 1. 개요 및 목적

사용자가 뒷면 도넛 차트 아래 `항목·비율`에 나오는 내용을 조금 더 예쁘게 다듬고, 두 차트 모두 도넛 아래의 `자료 1`을 지워 달라고 요청했다(스크린샷 첨부).
TEST에서 확인한 뒤 사용자의 지시로 네 변경(항목·비율 스크롤, TEST 파란 파비콘 코드, 프레임 두께, 항목·비율 목록 디자인)을 한꺼번에 PROD에 배포하고 `main`에 병합했다.

- 차트 아래에 `자료 1`(작은 글씨)이 있었고, `▼ 항목·비율`은 기본 삼각형 마커의 일반 summary, 목록은 불릿(•) 항목에 `라벨 · 40%` 형태의 한 줄 텍스트였다.
- `자료 1`은 `buildDistributionChart()`의 `datasetLabel`이 `note` 문단의 앞부분에 들어간 것이다. 같은 문단에 `미기록분 N%`, `추정값`, `미분류 항목 포함` 같은 주의 문구도 이어 붙었다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 변경 전 상태
- 변경 내용
- `자료 N` 제거 (출처 정보는 유지)
- `항목·비율` 디자인
- 테스트
- 검증 (실제 실행 결과)
- 배포·커밋 정보
- 남은 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 뒷면 도넛 차트 아래 `항목·비율`에 나오는 내용을 조금 더 예쁘게 다듬고, 두 차트 모두 도넛 아래의 `자료 1`을 지워 달라고 요청했다(스크린샷 첨부).
TEST에서 확인한 뒤 사용자의 지시로 네 변경(항목·비율 스크롤, TEST 파란 파비콘 코드, 프레임 두께, 항목·비율 목록 디자인)을 한꺼번에 PROD에 배포하고 `main`에 병합했다.

- 카드 면에는 더 이상 데이터셋 라벨을 쓰지 않고 **주의 문구만** 남긴다(`미기록분 N%`, `추정값`, `미분류 항목 포함`을 ` · `로 연결). 주의 문구가 없으면 note 요소를 숨겨(`hidden`) 여백도 생기지 않는다.
- 출처 연결은 사라지지 않는다. 라벨은 차트의 `data-source-label` 속성, 접근성 이름(`aria-label`), 그리고 출처 토글의 `먹이 구성 · 자료 1` 항목에 그대로 있다.
- note 요소 자체는 항상 만든다(숨김). 기존 테스트가 이 요소 위에서 시작하는 스와이프를 검증하기 때문이다.

텍스트 추출 호환: 각 행은 `swatch / name / sep(" · ") / amount` 구조이고 `sep`은 CSS로 숨긴다. 그래서 DOM 텍스트는 여전히 `무척추동물 · 40%` 형태이고 화면에는 점·이름·퍼센트로 보인다.
`비율 미확인`인 행은 퍼센트 칸에 `… · 비율 미확인`이 붙는 기존 문구를 유지한다.

변경 파일: `src/robingraph/api/static/chat.js`, `src/robingraph/api/static/styles.css`, `tests/frontend/chat_ui.test.js`.

| 항목 | 결과 |
|---|---|
| 프런트엔드 `node --test tests/frontend/*.test.js` | 255개 통과, 실패 0(기존 252 + 신규 3). 모의 DOM |
| Python 전체 | 644개 중 통과, 건너뜀 35(기존 DB 옵트인), 실패 0 |
| 실제 Chrome(헤드리스, CDP), 로컬 서버가 TEST Neo4j를 읽음(외부 LLM·MLflow 비활성), 청둥오리 뒷면 | **PC 1280×900, 모바일 390×844 모두** 두 차트의 note가 `hidden`·`display: none`·빈 텍스트, 차트 영역에 `자료 1` 문자열 없음. `항목·비율` 펼침: summary `border-radius 999px`·`display: flex`·마커 없음, 행 `display: flex`·불릿 없음·퍼센트가 행 오른쪽 끝에서 2px, 구분자 `display: none`. 스크린샷으로 색 점이 도넛 색과 일치하고 0% 행이 옅게 보이며 두 열이 정렬됨을 확인 |
| NAS TEST 배포 | 이미지 `robingraph-api:test-chartlook-e90ff85`, healthy, 재시작 0, OCI revision `e90ff85…`, `verify` ok(`deployment_target: test`), 서빙되는 `chat.js`·`styles.css`에 새 코드 확인 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-목록-다듬기-TEST배포]]
- [[Dev/index|Dev 인덱스]]
