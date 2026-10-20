---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-파비콘-추가-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 꼬까울새 파비콘 추가·TEST·PROD 배포

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-파비콘-추가-TEST배포]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":4,"데이터":0}

## 1. 개요 및 목적

사용자가 투명 배경의 둥근 꼬까울새 이미지(`~/Downloads/robingraph.png`, 1254×1254 RGBA)를 파비콘으로 추가해 달라고 요청했다.
저장소의 `docs/assets/robingraph-logo.png`는 글자와 가지가 들어간 전체 로고라 다른 그림이며 파비콘 원본으로 쓰지 않았다.
작업 시작 전에 이미지는 채팅에 붙여 넣은 상태라 디스크에 파일이 없어서, 사용자에게 저장 경로를 받았다.
TEST에서 확인한 뒤 사용자의 지시로 PROD까지 배포하고 `main`에 병합했다.

- 파비콘 설정이 전혀 없었다(`<link rel="icon">`·`/favicon.ico` 라우트 없음).
- `src/robingraph/api/app.py`는 `/static/`으로 `_REQUIRED_CHAT_ASSETS`(index.html, chat.js, styles.css)와 `birds.*`만 서빙하고
  각 응답을 정해진 파일 묶음 단위로 읽는다. 이미지(바이너리)를 서빙하는 경로가 없어 HTML 태그 추가만으로는 해결되지 않았다.
- 같은 파일 읽기 함수(`_read_chat_asset_bundle`)는 열린 파일 기술자에서 읽고 빈 파일·비정규 파일을 거부하므로 아이콘에도 재사용했다.
- `pyproject.toml`의 package-data는 `*.html/*.js/*.css`만 포함해 PNG·ICO가 wheel에 빠질 상태였다.
- 기존 프런트엔드 테스트가 `index.html`의 `<link>`가 `/static/styles.css` 하나뿐이라고 단정하고 있었다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 확인한 사실
- 변경 전후 동작
- 변경 파일과 구현
- 검증 (실제 실행 결과)
- 배포·커밋 정보
- 남은 한계와 후속

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 투명 배경의 둥근 꼬까울새 이미지(`~/Downloads/robingraph.png`, 1254×1254 RGBA)를 파비콘으로 추가해 달라고 요청했다.
저장소의 `docs/assets/robingraph-logo.png`는 글자와 가지가 들어간 전체 로고라 다른 그림이며 파비콘 원본으로 쓰지 않았다.
작업 시작 전에 이미지는 채팅에 붙여 넣은 상태라 디스크에 파일이 없어서, 사용자에게 저장 경로를 받았다.
TEST에서 확인한 뒤 사용자의 지시로 PROD까지 배포하고 `main`에 병합했다.

- 파비콘 설정이 전혀 없었다(`<link rel="icon">`·`/favicon.ico` 라우트 없음).
- `src/robingraph/api/app.py`는 `/static/`으로 `_REQUIRED_CHAT_ASSETS`(index.html, chat.js, styles.css)와 `birds.*`만 서빙하고
  각 응답을 정해진 파일 묶음 단위로 읽는다. 이미지(바이너리)를 서빙하는 경로가 없어 HTML 태그 추가만으로는 해결되지 않았다.
- 같은 파일 읽기 함수(`_read_chat_asset_bundle`)는 열린 파일 기술자에서 읽고 빈 파일·비정규 파일을 거부하므로 아이콘에도 재사용했다.
- `pyproject.toml`의 package-data는 `*.html/*.js/*.css`만 포함해 PNG·ICO가 wheel에 빠질 상태였다.
- 기존 프런트엔드 테스트가 `index.html`의 `<link>`가 `/static/styles.css` 하나뿐이라고 단정하고 있었다.

| 파일 | 내용 |
|---|---|
| `src/robingraph/api/static/favicon.ico` | 16·32·48px 멀티 사이즈 ICO(8,568바이트) |
| `src/robingraph/api/static/favicon-32.png`, `favicon-192.png` | 투명 배경 PNG(2,559 / 46,864바이트) |
| `src/robingraph/api/static/apple-touch-icon.png` | 180×180, 크림색(`#fdf6e3`) 배경. iOS는 투명 영역을 검게 채우므로 별도 배경을 입혔다(24,595바이트) |
| `src/robingraph/api/app.py` | `_ICON_ASSET_MEDIA_TYPES` 허용 목록(4개 이름만), `/favicon.ico` 라우트, `/static/{name}`에서 허용 목록 이름은 아이콘으로 처리. `Cache-Control: public, max-age=3600` |
| `src/robingraph/api/static/index.html`, `birds.html` | `<link rel="icon">`(ico, 32px, 192px)과 `apple-touch-icon` 추가 |
| `pyproject.toml` | package-data에 `api/static/*.png`, `api/static/*.ico` 추가 |
| `tests/test_favicon.py`(신규) | 8개 테스트 |
| `tests/frontend/chat_ui.test.js` | `<link>` 단정을 파비콘 4개 + 스타일시트의 정확한 목록으로 갱신. 같은 출처(원격 금지) 검사는 그대로 유지 |

| 항목 | 결과 |
|---|---|
| 신규 `tests/test_favicon.py` | 8개 통과. 실제 패키지 static 디렉터리 대상 서빙·미디어 타입·캐시 헤더·PNG 크기(32/192/180)·ICO 16/32 포함·페이지 링크·허용 목록·누락·빈 파일·package-data |
| Python 전체(`unittest discover`, 로컬 `/tmp/rg010-venv`) | 641개 중 통과, 건너뜀 35, 실패 0 (DB 옵트인 등 기존 건너뜀) |
| 프런트엔드(`node --test tests/frontend/*.test.js`) | 248개 통과, 실패 0. 처음 한 번은 위 `<link>` 단정 때문에 1건 실패해 단정을 갱신한 뒤 재통과 |
| `graphify update .` | 3,950노드·8,298간선·235커뮤니티 |
| TEST 배포 | 이미지 `robingraph-api:test-favicon-336d987`, healthy, 재시작 0, OCI revision `336d987…`, `verify` ok(`deployment_target: test`) |
| TEST 컨테이너 내부 HTTP | `/favicon.ico` 200 `image/x-icon` 8,568바이트, `favicon-32.png` 200 2,559, `favicon-192.png` 200 46,864, `apple-touch-icon.png` 200 24,595(모두 소스 파일 크기와 일치), `public, max-age=3600`. `/static/favicon.png`는 404. `/chat`·`/birds`에 아이콘 링크 포함 |
| PROD 배포 | 같은 릴리스 묶음(`336d987`)으로 이미지 `robingraph-api:prod-336d987`. 14:50:27 시작, 14:50:36 종료(이미지 레이어 캐시 사용). healthy, 재시작 0, OCI revision `336d987…`, `verify` ok(`deployment_target: prod`) |
| PROD `verify_api_deployment.py` | `passed: true`, `contract_parity_ok`·`backend_reachable` true, schema/response drift·canary 이슈 없음 |
| PROD 컨테이너 내부 HTTP | TEST와 같은 결과: 아이콘 4개 200(8,568 / 2,559 / 46,864 / 24,595바이트), `favicon.png` 404, `/chat`·`/birds`에 링크 포함 |

테스트 구분: 위 Python·프런트엔드는 모의 클라이언트(TestClient·jsdom류) 검증이고, TEST·PROD 확인은 실제 NAS 컨테이너 HTTP 요청이다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-파비콘-추가-TEST배포]]
- [[Dev/index|Dev 인덱스]]
