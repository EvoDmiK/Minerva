---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-카드버튼제거-답변출처통합-먹이비율-영어이름-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-405 카드 버튼 제거·답변 출처 통합·먹이 비율·영어 보조 이름

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-카드버튼제거-답변출처통합-먹이비율-영어이름-NAS-TEST배포]] · 분류 근거 {"인프라":3,"자동화":0,"관측성":0,"데이터":1}

## 1. 개요 및 목적

- 작업일: 2026-10-08
- 구현 커밋: `ddf002f78932633ba49ea68c3b7ab2c4a8212873` (`origin/dev` push 완료)
- 사용자 요청: 앞/뒤 전환 버튼을 없애고 카드 출처를 설명의 ‘답변 출처 보기’ 하나로 옮기며, 먹이 구성 시각화와 한국어 이름 옆 작은 영어 이름을 추가한다.

직전 TEST `cb18d1f`는 카드의 `.species-card-flip` 버튼과 `.species-card-sources` 출처 토글을 제공했다. 설명의 `.species-answer-sources`와 별개라 같은 자료를 두 위치에서 확인해야 했다. 먹이 구성은 긴 퍼센트 문자열이었다. 카드 제목은 speciesLabel을 사용해 한국어 또는 영어 하나만 표시했고 학명은 별도로 제공했다.

## 2. 핵심 아키텍처 및 원칙

- 배경과 확인한 원인
- 변경 전후 동작과 구현 파일
- 협업과 검증
- NAS TEST 배포와 서버 검증
- 한계와 기록 관리
- 최종 Git 확인

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

직전 TEST `cb18d1f`는 카드의 `.species-card-flip` 버튼과 `.species-card-sources` 출처 토글을 제공했다. 설명의 `.species-answer-sources`와 별개라 같은 자료를 두 위치에서 확인해야 했다. 먹이 구성은 긴 퍼센트 문자열이었다. 카드 제목은 speciesLabel을 사용해 한국어 또는 영어 하나만 표시했고 학명은 별도로 제공했다.

기존 appendAnswerMessage는 초기 설명의 출처만 메시지 끝으로 옮겼다. buildDeferredEnrichment는 추가 설명에서 별도 출처 토글을 생성할 수 있었고 사진 갱신은 카드 내부 photoSourcesSlot만 바꿨다. 따라서 단순 DOM 이동만 하면 지연 설명의 출처가 분리되거나 사진 교체·삭제 뒤 오래된 근거가 남을 수 있었다. 앞뒤 버튼 또한 flip.disabled와 애니메이션 상태가 연결돼 버튼을 삭제하면서 독립 상태와 키보드 입력을 마련해야 했다. graphify 관계 질의 및 해당 소스·테스트를 확인했다.

초기 설명·질문별 targeted 답변·citations·지연 추가 설명·사진 retry/update/remove 및 하위 종/아종/비교 팝업 경로에 동일 출처 통합을 연결했다. 일반 DB/API·질문 라우팅 정책은 변경하지 않았다. 아종 직접 자료와 종 수준 참고 확정 불가 안내, 활성 warnings는 카드 본문에 남기고 상세 서지·사진 라이선스·IUCN·분류·자료 해석 안내를 설명 아래에서 확인한다. 기존 '출처는 뒷면' 안내와 뒷면 제목도 최종 구조에 맞췄다.

pc_drag_popup_fix가 JS/CSS 및 모의 회귀검사·graphify 갱신, card_selection_review가 읽기 전용 독립 검토를 맡았다. 검토자는 초기/지연 설명·사진 슬롯·동일 URL의 서로 다른 메타·키보드 자식 예외를 확인했고 최종 영어 제목과 자료 번호 대응까지 차단 결함을 발견하지 못했다. root는 실제 브라우저·fixture 통합검사·NAS 배포·문서·Git을 담당했다. 워커 모델명은 별도로 확인하지 않았다.

- 전체 frontend `node --test tests/frontend/*.test.js`: **225 통과, 0 실패, 0 건너뜀**. 이전213 + 신규12이며 모의 DOM 검사다. 단일 패널·중복 제거와 메타 보존·사진 삭제 뒤 링크 재표시·deferred·키보드/캡처 정리·분포별 실제 비율과 invalid/unknown·영어 보조 제목을 검증한다.
- node --check 구현/테스트, git diff --check: 통과.
- 실제 NAS TEST API/DB + 로컬 JS/CSS 대체: 1280×900 마우스,390×844 터치,320×640 터치,390×844 reduced-motion 터치,1280px targeted 먹이 질문 **5설정 통과**. 버튼·카드 출처 없음, 한국어/영어/학명, 양면 키보드·포인터 전환, 식단5개 양의 비율40/20/20/10/10, 개별 항목명, 단일 설명 출처와 모든 실제 형질·사진 원본 URL1회 및 라이선스 보존, 측정값 토글, 맨 아래 접근·Escape·안전 링크·pageerror0을 확인했다. [로컬 실제API 결과](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-finalcard-local-browser.json).
- 실제 NAS API/DB + 로컬 자산 드래그/닫힘 회귀 **5설정·내부→밖 해제30건 통과**. PC1280/1440 일반·1280 reduced,390 touch 일반/reduced에서 밖에서 놓아도 유지, 밖→안쪽 유지, 보통 거리 전환, 정상 backdrop/X/Escape/재열기 초기화를 확인했다. [로컬 회귀 결과](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-finalcard-drag-local.json).
- 실제 Chrome DOM + **모의 초기/지연 API·사진 SVG fixture**로 deferred 통합을 검사했다. 같은 URL의 서로 다른 locator·evidence·license가 유지되고 링크는1개였다. 추가 설명·사진 creator/credit/license가 같은 열린 토글에 합쳐졌고 출처 URL 개수19→23, 별도 토글0, 카드 버튼/출처0, pageerror0이다. 이는 실제 외부 API/사진 전송 검증이 아니다. [로컬 모의API 통합 결과](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-finalcard-deferred-local.json).

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-카드버튼제거-답변출처통합-먹이비율-영어이름-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
