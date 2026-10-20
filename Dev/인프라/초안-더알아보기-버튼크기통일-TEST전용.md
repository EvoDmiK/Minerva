---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-10-더알아보기-버튼크기통일-TEST전용]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 더 알아보기 네 버튼 크기 통일 — TEST 전용

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-10-더알아보기-버튼크기통일-TEST전용]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":0,"데이터":0}

## 1. 개요 및 목적

사용자는 profile 답변의 더 알아보기 내부에서 근연 관계, 같은 서식 환경·먹이 생태, 아종, 통칭·가축형 네 탐색 버튼의 크기가 서로 다른 화면을 제시하고 크기를 맞추도록 요청했다. 글꼴·높이·폭·내부 여백을 통일하고 PC와 모바일 모두 같은 네 버튼 크기를 유지한다. 변경별 운영 승인 지시를 따라 이번 작업은 TEST에만 반영했다.

`graphify query`로 관련 탐색 코드와 스타일을 먼저 확인했다. 기존 `.species-related button`과 `.species-name-relations > button`은 font 상속을 지정하지 않았다. `.species-subspecies > button`과 `.species-ecological-related button`은 font: inherit를 사용했고, 아종 버튼의 padding도 다른 값이었다. 브라우저 기본 버튼 폰트와 답변 폰트가 섞여 글씨 크기와 높이가 달라졌다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 원인과 구현 근거
- 검증 방법과 결과
- 배포·Git 정보
- 남은 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자는 profile 답변의 더 알아보기 내부에서 근연 관계, 같은 서식 환경·먹이 생태, 아종, 통칭·가축형 네 탐색 버튼의 크기가 서로 다른 화면을 제시하고 크기를 맞추도록 요청했다. 글꼴·높이·폭·내부 여백을 통일하고 PC와 모바일 모두 같은 네 버튼 크기를 유지한다. 변경별 운영 승인 지시를 따라 이번 작업은 TEST에만 반영했다.

`graphify query`로 관련 탐색 코드와 스타일을 먼저 확인했다. 기존 `.species-related button`과 `.species-name-relations > button`은 font 상속을 지정하지 않았다. `.species-subspecies > button`과 `.species-ecological-related button`은 font: inherit를 사용했고, 아종 버튼의 padding도 다른 값이었다. 브라우저 기본 버튼 폰트와 답변 폰트가 섞여 글씨 크기와 높이가 달라졌다.

`node --test tests/frontend/*.test.js`: 303개 통과, 실패·취소·건너뛰기 0. 기존 fake DOM 회귀이며 실제 DB 검증으로 계산하지 않는다. 이번 변경은 CSS 표시 수정이므로 스타일 선언을 그대로 복제하는 새 단위 테스트 대신 실제 브라우저 치수를 검사했다.

Chrome 320·390·768·1280px × diet·magpie·habitat·profile 4종 응답 형식, 총 16사례를 로컬 최종 자산으로 확인했다. 입력 데이터는 이전 작업에서 실제 TEST에서 받은 응답을 재생했다. 매 사례에서 네 버튼 수가 4인지, getBoundingClientRect의 높이·폭과 computed style의 font-size·line-height·padding이 각각 동일한지 검사했다. 버튼 내부 세로 넘침·페이지 가로 넘침 없음, 페이지 오류 0이었다. 390px profile 스크린샷을 직접 열어 동일 높이·줄바꿈·여백을 확인했다. 이 16사례는 UI 재생 검증이며 새 실제 채팅 API 요청 16건으로 기록하지 않는다.

배포된 TEST 자산으로 같은 16사례를 재실행해 모두 통과했다. 모바일·태블릿·PC 네 폭에서 네 버튼의 실제 치수와 폰트·여백 일치, 넘침 없음, 페이지 오류 0을 다시 확인했다. 공개 chat.js·styles.css는 로컬 최종 파일과 바이트 단위로 일치했다. 별도 실제 health와 청둥오리 profile 채팅 API도 정상 응답했으며 학명 Anas platyrhynchos·영문명 Mallard를 확인했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-10-더알아보기-버튼크기통일-TEST전용]]
- [[Dev/index|Dev 인덱스]]
