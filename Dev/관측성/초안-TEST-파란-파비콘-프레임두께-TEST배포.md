---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-TEST-파란-파비콘-프레임두께-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# TEST 전용 파란 파비콘·카드 프레임 두께 통일(NAS TEST·PROD 배포)

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-TEST-파란-파비콘-프레임두께-TEST배포]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":2,"데이터":2}

## 1. 개요 및 목적

1. "TEST 웹의 파비콘은 다른 색으로 만들어 줄 수 있을까? PROD랑 헷갈려" — TEST와 PROD 탭을 구분할 수 있게 한다.
2. "테두리의 굵기는 토글을 열든 말든 얇은 걸로 통일해줘" — 카드를 둘러싼 은색 팝업 프레임의 두께가 토글 상태와 상관없이 얇고 같게 한다.

TEST에서 확인한 뒤 사용자의 지시로 네 변경(항목·비율 스크롤, TEST 파란 파비콘 코드, 프레임 두께, 항목·비율 목록 디자인)을 한꺼번에 PROD에 배포하고 `main`에 병합했다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 1. TEST 전용 파란 파비콘
- 결정
- 변경
- 2. 카드 프레임 두께 통일
- 원인 (실측)
- 변경
- 변경 전후 동작
- 검증 (실제 실행 결과)
- 배포·커밋 정보
- 남은 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

1. "TEST 웹의 파비콘은 다른 색으로 만들어 줄 수 있을까? PROD랑 헷갈려" — TEST와 PROD 탭을 구분할 수 있게 한다.
2. "테두리의 굵기는 토글을 열든 말든 얇은 걸로 통일해줘" — 카드를 둘러싼 은색 팝업 프레임의 두께가 토글 상태와 상관없이 얇고 같게 한다.

TEST에서 확인한 뒤 사용자의 지시로 네 변경(항목·비율 스크롤, TEST 파란 파비콘 코드, 프레임 두께, 항목·비율 목록 디자인)을 한꺼번에 PROD에 배포하고 `main`에 병합했다.

색을 구분하는 가장 단순한 방법으로, 같은 URL(`/favicon.ico`, `/static/favicon-32.png`, `favicon-192.png`, `apple-touch-icon.png`)이
`ROBINGRAPH_DEPLOY_TARGET=test`일 때만 파란 변형을 돌려주도록 했다. HTML과 아이콘 링크는 바꾸지 않았다. 변형 파일이 없으면 기본 아이콘으로 대체하므로 404가 생기지 않는다.
`/health`가 이미 같은 환경 변수로 `deployment_target`을 노출하므로 새 설정은 없다. 탭 제목에 `[TEST]`를 붙이는 등 요청 범위 밖의 변경은 하지 않았다.

| 파일 | 내용 |
|---|---|
| `src/robingraph/api/static/favicon-test.ico`, `favicon-32-test.png`, `favicon-192-test.png`, `apple-touch-icon-test.png` | 같은 새 이미지의 색상(hue)만 약 185° 돌려 주황→파랑으로 바꾼 변형. 채도·명도·투명도는 유지. iOS용 아이콘 배경은 PROD의 크림색 대신 연한 하늘색(`#e8f1fa`). 원본은 `~/Downloads/robingraph.png`, Pillow(컨테이너)로 생성 |
| `src/robingraph/api/app.py` | `icon_asset()`이 TEST 대상이면 `<이름>-test.<확장자>`를 먼저 찾고 없으면 기본 파일을 서빙. 허용 목록(4개 이름)은 그대로라 변형 파일명을 직접 요청하면 404 |
| `tests/test_favicon.py` | 신규 3개: TEST에서는 4개 아이콘이 모두 PROD/기본과 다른 바이트이고 PNG는 같은 정사각 크기, prod·legacy·미설정은 기본 유지, 변형 파일명 직접 요청은 404이며 변형 누락 시 기본으로 대체 |

`tests/frontend/chat_ui.test.js`: 기존 "데스크톱으로 돌아가면 CSS 너비를 복원한다" 단정은 옛 동작을 고정하고 있어 새 동작("데스크톱도 축소된 카드를 따르고, 축소가 없으면 기본 너비")으로 바꾸고 표면 너비 고정 단정을 추가했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-TEST-파란-파비콘-프레임두께-TEST배포]]
- [[Dev/index|Dev 인덱스]]
