---
created: 2026-10-18
updated: 2026-10-18
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-18-고급조회-분포옵션-레이아웃-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 고급 조회 옵션 분포 범위 정렬·TEST 배포 — 2026-10-18

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-18-고급조회-분포옵션-레이아웃-TEST배포]] · 분류 근거 {"인프라":0,"자동화":2,"관측성":0,"데이터":0}

## 1. 개요 및 목적

[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/작업 백로그|4xx 채팅 UI·카드 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]]

사용자가 고급 조회 옵션 내부의 분포 범위 4개 라디오 옵션이 불규칙하게 3+1줄로 나열되는 화면을 제시하며 보기 좋게 다듬도록 요청했다. 목표는 4개 옵션을 균일하게 정렬하고 TEST 환경(`192.168.219.97:8000`)에 먼저 배포하여 확인하는 것이다. 운영 배포는 사용자가 TEST 수정 결과를 직접 확인하고 명시적으로 승인한 이후에만 진행하며, 이번 UI 변경에 대해 앞선 Jenkins 운영 배포 승인을 재사용하지 않는다 (현재 운영 승인 없음, 운영 배포 금지).

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 원인과 변경 전후
- 협업과 변경 파일
- TEST 배포 및 환경 격리
- 실제 검증 결과
- 한계 및 후속 확인 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 고급 조회 옵션 내부의 분포 범위 4개 라디오 옵션이 불규칙하게 3+1줄로 나열되는 화면을 제시하며 보기 좋게 다듬도록 요청했다. 목표는 4개 옵션을 균일하게 정렬하고 TEST 환경(`192.168.219.97:8000`)에 먼저 배포하여 확인하는 것이다. 운영 배포는 사용자가 TEST 수정 결과를 직접 확인하고 명시적으로 승인한 이후에만 진행하며, 이번 UI 변경에 대해 앞선 Jenkins 운영 배포 승인을 재사용하지 않는다 (현재 운영 승인 없음, 운영 배포 금지).

- **원인**:
  - 기존 `.species-scope-options`는 `flex-wrap: wrap`을 사용하여 옵션 텍스트 길이에 따라 자동으로 줄이 바뀌었다.
  - 옵션별 너비 차이로 인해 3개 옵션이 윗줄에 배치되고 마지막 1개 옵션만 아랫줄에 홀로 남는 불규칙한 레이아웃이 발생했다.
  - 전역 일반 입력 필드의 최소 높이 규칙이 라디오 입력에도 적용되어, 키보드 포커스 링(`:focus-visible`)이 세로로 늘어나는 문제가 있었다.
- **변경 전후 동작**:
  - `src/robingraph/api/static/styles.css`에서 해당 클래스를 CSS Grid 2열(`repeat(2, minmax(0, 1fr))`), 동일 행 높이, 10px 간격(`gap: 10px`)으로 변경했다.
  - 화면 너비 600px 이하 모바일 환경에서는 미디어 쿼리를 적용하여 1열 단일 열(`grid-template-columns: 1fr`)로 깔끔하게 전환된다.
  - 각 옵션은 `padding: 10px 14px`, `border-radius: 12px`, 기존 최소 터치 타깃 높이 `44px`를 유지한다.
  - 라디오 버튼은 `1rem` 정사각형, `min-height: 0`, `flex-shrink: 0`을 지정하여 텍스트 첫 줄 또는 중앙에 균형 있게 배치했다.
  - 텍스트 문구, API scope 값, JavaScript 상태 처리 로직은 전혀 변경하지 않았으며, 선택 시 강조 색상과 `:focus-within` 동작을 그대로 유지한다.

- UI 담당 워크트리(`main`) 터미널에 작업 협업을 요청했으나, UI 에이전트가 panic으로 비정상 종료됨을 확인했다.
- `main`의 기존 미커밋 파일을 가져오거나 덮어쓰지 않았으며, Codex가 `dev-codex`에서 CSS만 직접 구현하고 검증했다.
- 따라서 UI 에이전트의 검토 완료로 보고하지 않으며, Codex의 실제 TEST 브라우저 및 API 검사 결과만을 단독 근거로 삼는다.
- **변경 파일**:
  - `src/robingraph/api/static/styles.css`: 정렬 및 라디오 크기·포커스 스타일 수정.
  - `docs/work-log/2026-10-18-scope-option-layout.md`: 로컬 작업 기록.
  - `docs/verification/assets/2026-10-18-scope-layout/`: 브라우저 자동화 검사 스크립트, 결과 JSON, 스크린샷 7종, 검사 로그 및 release receipt.

기존 TEST의 immutable 이미지를 기반으로 수정한 CSS 파일 1개만 교체한 ARM64 로컬 이미지를 빌드했다. 전체 저장소의 Git revision과 미커밋 CSS를 명확히 구분하기 위해 별도의 `css-sha256` 라벨과 receipt를 기록했다. 이전 릴리스의 compose 및 환경 설정을 복사하고 image만 교체했으며, atomic 심볼릭 링크 교체 방식을 적용했다.

- **TEST 접속 주소**: `https://robingraph-test.dove-nest.com/chat`
- **배포 이미지**: `robingraph-api:test-scope-layout-733d461cbc61`
- **기반 Git revision**: `bc643ee9edef0fc58c605adde70b4808b7622ac5`
- **CSS SHA-256**: `733d461cbc61ec6361223c056c262a54bc036d70819c11096c5bf5e2138849c6`
- **TEST receipt 상태**: `verified` (`uncommitted_css_patch: true`, 이전 릴리스 `/Users/kimdove/robingraph-test/releases/scope-layout-8651b17c6a36` 보존).
- **운영 격리**: Jenkins 운영 job이나 GHCR 배포는 전혀 실행하지 않았음.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-18-고급조회-분포옵션-레이아웃-TEST배포]]
- [[Dev/index|Dev 인덱스]]
