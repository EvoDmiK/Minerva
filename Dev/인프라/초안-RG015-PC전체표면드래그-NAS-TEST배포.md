---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-PC전체표면드래그-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-405 후속 — PC 카드 전체 표면에서 드래그 뒤집기

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-PC전체표면드래그-NAS-TEST배포]] · 분류 근거 {"인프라":3,"자동화":0,"관측성":0,"데이터":1}

## 1. 개요 및 목적

작업일: 2026-10-08 KST. 구현 커밋: `719e5bcf44e920a5cb9a3d8639279bd1f7b3d066`.

사용자가 PC에서 카드 앞·뒷면을 잘 넘길 수 없다고 제보한 뒤 카드 전체 영역에서 넘길 수 있게 요청했다. 카드의 제목·본문·중첩 글씨·사진·장식·빈 표면에서 마우스 드래그를 시작하도록 확대한다. 버튼·링크·출처 펼치기·입력 등의 클릭 기능과 이전의 글씨 선택 차단, 모바일 터치 정책은 유지한다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 원인과 재현 근거
- 변경 전후와 구현 파일
- 협업
- 검증 방법과 실제 결과
- 로컬 자산 검사와 실제 NAS 배포 자산 검사
- 배포·Git·그래프
- 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

실제 NAS TEST `570fd3f`·Chrome 1280px에서 앞면 제목과 뒷면 h3에 카드 폭 38%만큼 마우스를 이동했다. 두 경우 모두 data-dragging이 없고 앞·뒷면이 바뀌지 않았다. [수정 전 실제 재현](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-pcdrag-before.json).

- `src/robingraph/api/static/chat.js`: PC의 layout class 허용 목록과 관련 미사용 helper를 제거하고 일반 본문 및 중첩 요소에서 시작하도록 했다. PC는 img/picture/canvas/svg 및 role=img도 허용한다. 부모를 따라 올라가 button/a/summary/input/select/textarea/label/video/audio·편집 영역·명시적 draggable·role button/link/textbox가 있는 경우 계속 제외한다. 모바일은 사진·그림 시작 제외를 유지한다.
- 사진의 브라우저 native drag가 카드 드래그 활성화 전에 시작할 수 있어, 추적 중인 mouse gesture에서는 pending 단계의 dragstart도 preventDefault한다. 드래그 외부와 조작 요소의 native drag는 가로채지 않는다.
- `src/robingraph/api/static/styles.css`: PC 본문의 cursor:auto 예외를 제거해 카드 표면에 grab, 진행 중에는 grabbing을 보여 준다. 버튼·링크의 기존 pointer와 글씨 선택 금지는 유지한다.
- `tests/frontend/chat_ui.test.js`: 과거 ‘마우스 글씨 시작 거부’ 기대를 새 정책으로 갱신했다. 양면·양방향·중첩 글씨·reduced-motion, 사진/장식의 PC 허용과 touch 제외, 중첩 조작 예외와 pending native drag를 보강했다.
- PC 안내를 ‘카드의 사진·글씨·빈 곳을 좌우로 끌어 뒤집어 보세요’로 바꿨다.

`pc_card_drag_fix`가 UI/CSS·테스트 구현과 전체 frontend 검사를 담당했다. `card_selection_review`는 읽기 전용 독립 diff 검토로 양면·사진·중첩 조작 예외·touch 분기·native drag·cleanup을 확인했고 차단 결함을 발견하지 못했다. root는 실제 수정 전 재현, 로컬 자산/배포 자산 브라우저 검증, 패키지·NAS 배포·문서·Git을 담당했다. 이번 협업의 실제 워커 모델명은 별도로 확인하지 않았다.

구문 검사와 `git diff --check` 통과. 전체 `node --test tests/frontend/*.test.js`는 **205 통과, 0 실패, 0 건너뜀**이다. 단일 chat UI는 202개이며 기존 단일200/전체203 대비 신규2개다. 변경된 기존 검사도 포함되지만 검사 삭제는 없다. 모의 DOM 검사이며 실제 브라우저·GPU 검증과 구분한다. JS/CSS 변경이므로 Python·전체 DB 회귀는 재실행하지 않았다.

PC 검사는 실제 NAS TEST API/DB 응답을 사용하며 외부 사진 파일만 SVG fixture로 대체했다. 로딩된 img에서도 native 사진 드래그에 빼앗기지 않고 넘겨지는지 확인하려는 목적이다. API 응답·사진 메타데이터를 모의 처리하지 않았으며 실제 외부 사진 전송 성공으로 해석하지 않는다. 배포 전에는 JS/CSS도 로컬 파일로 대체했고 배포 후에는 실제 서버 JS/CSS를 사용했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-PC전체표면드래그-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
