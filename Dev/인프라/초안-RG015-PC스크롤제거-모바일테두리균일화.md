---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-RG015-PC스크롤제거-모바일테두리균일화]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-405 PC 스크롤 제거·모바일 테두리 균일화

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-RG015-PC스크롤제거-모바일테두리균일화]] · 분류 근거 {"인프라":2,"자동화":0,"관측성":1,"데이터":1}

## 1. 개요 및 목적

- 작업일: 2026-10-09
- 요청: 최종 완료 이후 남은 미세 스크롤을 없앤다. 사용자가 스크롤 대상을 PC로 명확히 했으며, 이어서 모바일 좌우 테두리도 위아래와 같은 굵기로 맞추도록 요청했다.

PC의 .species-popup은 고정 높이와 overflow:auto를 사용했고 fit wrapper는 display:contents였다. 이전 전체 카드 맞춤은 모바일에만 적용했다. 공통 앞·뒷면의 자연 높이가 팝업 내용 높이를 넘으면 숨긴 스크롤바가 보이지 않을 뿐 휠·키보드로 실제 스크롤할 수 있었다.

## 2. 핵심 아키텍처 및 원칙

- 확인한 원인과 변경 전 동작
- 변경 파일·구현·변경 후 동작
- 협업과 자동 검증
- 배포 전 실제 브라우저 검증
- 배포 후 실제 브라우저 검증
- 커밋·배포
- 한계·남은 작업

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

캐시된 청둥오리 응답을 모의 API로 반환한 변경 전 실제 Chrome 실측에서 PC1280×720은 dialog scrollHeight794/clientHeight688, 휠 후 scrollTop106이었다. PC1440×1080은 scrollHeight859/clientHeight844, 휠 후 scrollTop15로 사용자가 말한 작은 스크롤을 재현했다. 같은 모의 응답의1280×900은 스크롤0이었다. 따라서 모든 PC에서 항상 재현되는 문제로 기록하지 않는다. 전역 box-sizing:border-box가 이미 있어서 padding의 content-box 중복을 원인으로 삼지 않는다. [변경 전6설정](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-09-RG015-scroll-before-browser.json)은 모의 API 검증이며 실제 DB 호출로 합산하지 않는다.

모바일에서는 높이에 맞춰 카드가 축소돼도 팝업 외곽 폭이 원래 최대 폭을 유지했다. 특히 가로844×390에서 실제 카드와 팝업의 좌우 간격은140.08px, 위아래는12px였다. 이 수치는 [직전 배포 실제 API/DB 실측](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-09-RG015-final-browser.json)에서 확인했다. 세로375×667도 좌우8.85px 대 위아래8px로 약간 달랐다. 카드 자체의 border 선보다 그 바깥 팝업 배경의 빈 폭이 두꺼워 보이는 원인이었다.

`tests/frontend/chat_ui.test.js`의 PC 자연 스크롤/fit 없음 기대를 새 동작으로 바꾸고, PC 자연 크기→긴 상세 맞춤→복원과 모바일 좁힌 외곽의 반복 측정에도 누적 축소가 없는 회귀를 추가한다.

pc_drag_popup_fix가 JS/CSS·회귀·graphify를 담당하고 card_selection_review가 읽기 전용 독립 검토를 수행했다. root는 변경 전 재현·실제 Chrome 휠/키보드/터치/포커스·간격 측정·NAS TEST 배포·문서/Obsidian·Git을 맡았다. 독립 검토에서 변경이 필요한 차단 문제는 발견하지 않았다.

- frontend 전체 **248 통과·실패0·건너뛰기0·취소0**. [실행 로그](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-09-RG015-scroll-frontend-tests.txt).
- node --check chat.js·git diff --check 통과.
- graphify update .: AST15/15,3845 노드·8178 간선·224 커뮤니티. 기존 SQL parser 미설치4·no-symbol 안내2 및 community label 안내가 있으며 AST 갱신은 완료했다. 의미 추출 API는 사용하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-RG015-PC스크롤제거-모바일테두리균일화]]
- [[Dev/index|Dev 인덱스]]
