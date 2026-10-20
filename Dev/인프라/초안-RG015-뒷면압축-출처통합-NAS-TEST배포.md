---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-뒷면압축-출처통합-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-405 카드 뒷면 압축·출처 통합 및 NAS TEST 배포

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-뒷면압축-출처통합-NAS-TEST배포]] · 분류 근거 {"인프라":3,"자동화":0,"관측성":0,"데이터":2}

## 1. 개요 및 목적

- 작업일: 2026-10-08
- 요청: 뒷면 오른쪽 스크롤바를 감추고 정보를 컴팩트하게 배치하며 출처를 하나의 토글로 통합한다.
- 구현 커밋: `cb18d1fc0ab19686711c25fc033f94045803d562` (`origin/dev` push 완료).

기존 뒷면은 각 형질에 자료 출처 details를 붙이고 사진·먹이 아이콘·멸종위기 등급 출처도 별도 details로 표시했다. 넓은 행 간격과 본문에 항상 표시된 종 평균·날개폭 해석 안내가 세로 길이를 더했다. dialog의 `overflow:auto`는 필요한 스크롤과 브라우저의 기본 스크롤바를 함께 제공했다.

## 2. 핵심 아키텍처 및 원칙

- 배경과 확인한 원인
- 변경 전후 동작과 구현
- 협업과 로컬 검증
- 실제 배포·배포 후 검증
- 한계와 기록 관리
- 최종 Git 확인

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

실제 이전 NAS TEST `b58be10`의 API/DB/JS/CSS를 사용하는 Chrome Pixel 7 터치 에뮬레이션(390×844 CSS px)에서 청둥오리를 조회했다. 기본 뒷면의 dialog clientHeight는 812px, scrollHeight는 1,525px, scrollbar-width는 auto였다. 사진 2개, API 형질 18개가 동일값 통합 후 17개 행으로 렌더링됐으며 측정값 더보기 7개를 포함한 details가 총22개였다. 실제 브라우저 스크롤바 노출은 운영체제 설정에도 영향을 받는다. [기존 측정 결과](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-compactback-before.json), [기존 화면](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-compactback-before-390.png).

pc_drag_popup_fix가 JS/CSS/모의 회귀검사 및 graphify 갱신을 담당했다. card_selection_review가 읽기 전용으로 출처 손실·아종 scope·비동기 슬롯·스크롤/드래그 상호작용과 최종 diff를 독립 검토했고 차단 결함을 발견하지 못했다. root는 실제 기존 화면 측정·브라우저 검사·배포·문서·Git을 담당했다. 실제 워커 모델명은 별도 확인하지 않았다.

- 전체 frontend `node --test tests/frontend/*.test.js`: **213 통과, 0 실패, 0 건너뜀**. 기존210 + 출처 통합·비동기 사진 갱신·아종 scope 신규3개이며 모의 DOM 검사다.
- node --check 구현/테스트 파일, git diff --check: 통과.
- 실제 NAS TEST API/DB + 수정 로컬 JS/CSS 대체 검사: 1280×900 마우스, 390×844 터치, 320×640 터치, 390×844 reduced-motion 터치 **4설정 통과**. 모든 실제 형질 값·형질 원자료 URL·사진 원본 및 라이선스 보존, 단일 출처 토글/내부 details0, 안전 링크, 키보드 Enter/Space, native 휠·touch 세로 스크롤, 맨 아래 접근, 스크롤 중 면 유지, PC 뒷면 드래그 전환 및 Escape를 확인했다. pageerror0·runner exit0. [로컬 자산 결과](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-compactback-local-browser.json).
- 로컬 자산 기존 드래그·닫힘 검사: PC1280/1440 일반·1280 reduced 및390 touch 일반/reduced **5설정·내부→외부 해제30건** 유지, 외부→내부 유지, 보통 거리 본문 전환, 이후 정상 backdrop/X/Escape/재열기 통과. 극단적인 화면 가장자리 해제는 팝업 유지가 합격 조건이며 면 전환은 별도 검사한다. pageerror0·runner exit0. [로컬 회귀 결과](https://github.com/EvoDmiK/RobinGraph/blob/dev/docs/verification/assets/2026-10-08-RG015-compactback-drag-local.json).

개발 중 첫 브라우저 검사는 종 평균 안내를 아직 출처 안으로 이동하기 전 실행되어 해당 위치 기대가 불일치했다. 안내 이동 후 위 4설정을 다시 실행해 통과했다. 이 중간 실패를 최종 통과에 합산하거나 배포 실패로 기록하지 않는다.

Python·전체 DB 회귀는 JS/CSS 변경이므로 재실행하지 않았다. 위 실제 API/DB 조회는 전체 DB 회귀나 물리 휴대전화 테스트를 뜻하지 않는다. 비동기 사진 갱신·아종 합성 입력 검증은 모의 검사이며 실서비스 아종과 새 사진 제공처 장애 복구를 실제로 재현한 것은 아니다. 사진 출처 보존을 확인했으며 모든 외부 사진 파일의 완전 전송을 검증한 것은 아니다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-08-RG015-뒷면압축-출처통합-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
