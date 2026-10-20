---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-06-OpenViking-탭-개선과-Hermes-Grafana-MCP-연결]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# OpenViking 탭 개선과 Hermes Grafana MCP 연결

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-06-OpenViking-탭-개선과-Hermes-Grafana-MCP-연결]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":34,"데이터":0}

## 1. 개요 및 목적

`Aviary Control Room`의 `OpenViking 모니터링` 탭을 읽기 쉽게 고치고, Hermes가 Grafana를 조회할 수 있도록 조회 전용 `grafana` MCP를 연결했다. 대시보드 변경은 `main`에 반영했고 NAS Grafana Git Sync가 받았다. Hermes MCP는 연결 시험까지 통과했지만, 실제 세션에서의 조회는 아직 확인하지 못했다.

같은 패널 12개가 두 곳에 중복되어 있다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- OpenViking 대시보드
- 별도 대시보드는 필요 없다
- 지표 종류 확인
- 수정 내용
- Git 기록
- 반영 경로
- Hermes Grafana MCP
- 구성
- 설정 위치
- 시행착오
- 검증
- 남은 일
- 운영 메모
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

`Aviary Control Room`의 `OpenViking 모니터링` 탭을 읽기 쉽게 고치고, Hermes가 Grafana를 조회할 수 있도록 조회 전용 `grafana` MCP를 연결했다. 대시보드 변경은 `main`에 반영했고 NAS Grafana Git Sync가 받았다. Hermes MCP는 연결 시험까지 통과했지만, 실제 세션에서의 조회는 아직 확인하지 못했다.

- **Git Sync:** `main`에 push하면 NAS Grafana(`<NAS-LAN-IP>:3002`)가 60초 주기로 가져온다. Grafana 로그의 `r4l2wj-sync`와 커밋 SHA로 확인했다. 브라우저에 이전 화면이 남아 있어서 처음에는 그대로인 것처럼 보였다. 강제 새로고침이 먼저다.
- **file provisioning:** NAS의 `/volume3/Gullinkambi` checkout이 `provisioning/alerting`, `provisioning/dashboards`를 마운트한다. 이쪽은 자동 갱신되지 않아 `git pull --ff-only`가 필요하다. 이번에 `1ee29a9`, `6ca7243`까지 맞췄다.
- `ssh NAS`(kimdove, port 99)는 이날부터 접속된다.

- 컨테이너 안에서 토큰이 `hermes-dashboard-readonly`로 인증됨을 확인했다.
- `hermes -p hybrid-v2 mcp test grafana`가 1.6초 만에 연결됐고 도구 62개를 확인했다. `mcp list`에는 `15 selected`로 표시된다.

- Hermes 세션에서 `/reload-mcp` 실행 후 실제 조회 확인. Discord 등 gateway 세션은 컨테이너 재시작이 필요할 수 있다.
- 단독 `OpenViking Overview`를 지울지, 같은 수정을 적용할지 결정.
- `README.md`, `docs/README_KO.md`에 OpenViking 패널 변경과 Claude·Antigravity 초기화 패널 통합 반영.
- `hybrid-v2/config.yaml`에는 이번 작업 전부터 커밋되지 않은 큰 변경이 있다. 이번 추가분은 그 위에 한 덩어리만 얹었으므로, 같은 파일을 만지는 다른 작업과 충돌하지 않는지 확인한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-06-OpenViking-탭-개선과-Hermes-Grafana-MCP-연결]]
- [[Dev/index|Dev 인덱스]]
