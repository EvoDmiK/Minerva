---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-모바일터치스와이프-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-405 후속 — 모바일 터치로 조류 카드 뒤집기

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-모바일터치스와이프-NAS-TEST배포]] · 분류 근거 {"인프라":2,"자동화":0,"관측성":0,"데이터":3}

## 1. 개요 및 목적

작업일: 2026-10-08 KST. 구현 커밋: `a2a9bad62ee70426b6947b639a7f09e01d2c7e93`. 배포 대상: NAS TEST.

사용자가 “모바일에는 적용 안되어있는거 같은데 모바일 환경에도 적용해줘”라고 요청했다. 직전 RG-405는 마우스 드래그가 기본 범위였고, 320·390px 검증도 작은 화면에서 **마우스**를 사용한 시험이었다. 실제 손가락 스와이프를 지원하거나 검증한 것으로 볼 수 없었다. 이번 후속 작업은 터치 입력을 지원하고 세로 스크롤·확대·기존 버튼·사진 조작을 유지하는 것이다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 원인과 변경 전후 근거
- 변경 파일과 구현
- 협업과 검토
- 검증 범위와 실제 결과
- 구문·모의 프런트엔드 회귀
- 배포 전 실제 브라우저 입력
- 실제 NAS TEST 자산·API·DB를 사용한 터치 검사
- 기존 조작 회귀
- 초기 검증 실패와 정정
- 화면 확인
- 배포·커밋·지식 그래프
- 사용법·남은 한계와 후속

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

작업일: 2026-10-08 KST. 구현 커밋: `a2a9bad62ee70426b6947b639a7f09e01d2c7e93`. 배포 대상: NAS TEST.

사용자가 “모바일에는 적용 안되어있는거 같은데 모바일 환경에도 적용해줘”라고 요청했다. 직전 RG-405는 마우스 드래그가 기본 범위였고, 320·390px 검증도 작은 화면에서 **마우스**를 사용한 시험이었다. 실제 손가락 스와이프를 지원하거나 검증한 것으로 볼 수 없었다. 이번 후속 작업은 터치 입력을 지원하고 세로 스크롤·확대·기존 버튼·사진 조작을 유지하는 것이다.

실제 변경 전 NAS TEST를 Chrome 모바일 에뮬레이션에서 열고 CDP `Input.dispatchTouchEvent`로 수평 이동했다. `isTrusted=true`, `pointerType=touch`인 pointerdown/move 이후 pointercancel이 발생했고 뒷면은 표시되지 않았다. 계산된 `touch-action`은 `auto`였다. [변경 전 증거](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-mobile-before.json).

| 파일 | 구현 내용 |
| --- | --- |
| `src/robingraph/api/static/chat.js` | primary 한 손가락 터치 지원, 축 판정·임계값·취소·선택·capture·후속 click 정리, 모바일 안내 영역 생성 |
| `src/robingraph/api/static/styles.css` | `touch-action: pan-y pinch-zoom`, coarse pointer에서 너비 전체·최소 높이 44px의 스와이프 안내 |
| `tests/frontend/chat_ui.test.js` | 터치 상태 전환·취소·제외 영역·리스너 해제·빠른 연속 제스처·동작 줄이기 모의 회귀 검사 |
| 이 문서 및 `docs/verification/assets/2026-10-08-RG015-mobile-*` | 원인, 검증 단계별 결과와 화면 증거 |

실제 Orca run `run_bfb68f6544af`에서 Claude가 UI·CSS·회귀 테스트를 구현하고 Antigravity가 독립적으로 읽기 전용 검토를 수행했다. Codex는 통합 검토, 실제 브라우저 입력·NAS 배포·문서·Git을 담당했다. 런타임의 모델 필드가 null이므로 두 워커의 실제 모델명은 확인되지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-모바일터치스와이프-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
