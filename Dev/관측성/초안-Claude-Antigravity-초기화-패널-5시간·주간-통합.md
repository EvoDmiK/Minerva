---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-05-Claude-Antigravity-초기화-패널-5시간·주간-통합]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Claude·Antigravity 초기화 패널 5시간·주간 통합

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-05-Claude-Antigravity-초기화-패널-5시간·주간-통합]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":9,"데이터":0}

## 1. 개요 및 목적

`AI 구독` 탭의 Claude·Antigravity 초기화 시각 패널을 각각 5시간·주간 두 값이 한 패널에 위아래로 보이도록 바꿨다. 변경은 `main`에 반영했고 NAS Grafana Git Sync가 이를 받아 두 줄로 표시되는 것을 확인했다.

| 패널 | 변경 전 | 변경 후 |
| --- | --- | --- |
| `panel-ai-subscription-6` | `Claude · 다음 초기화` (5시간만) | `Claude · 초기화` (5시간 + 주간) |
| `panel-ai-subscription-17` | `Antigravity · 다음 초기화` (5시간만) | `Antigravity · 초기화` (5시간 + 주간) |

## 2. 핵심 아키텍처 및 원칙

- 요약
- 변경 내용
- 표시 조정
- Git 기록
- 운영 메모
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

`AI 구독` 탭의 Claude·Antigravity 초기화 시각 패널을 각각 5시간·주간 두 값이 한 패널에 위아래로 보이도록 바꿨다. 변경은 `main`에 반영했고 NAS Grafana Git Sync가 이를 받아 두 줄로 표시되는 것을 확인했다.

1. 처음에 `orientation: vertical`을 적용했더니 5시간·주간이 위아래가 아니라 가로로 나란히 표시되어 두 줄 배치를 다시 요청받았다. Grafana stat 패널의 `vertical`은 값들을 가로로 나란히 놓고, `horizontal`이 위아래로 쌓는다.
2. `orientation: horizontal`로 바꿔 두 줄 배치를 확인했다.
3. 글자를 키워 달라는 요청에 `text.valueSize: 28`, `text.titleSize: 14`로 고정했다. stat 패널에는 줄 간격 설정이 따로 없어, 글자 크기를 키워 상대적인 간격을 줄였다.

- 이 대시보드는 Grafana Git Sync(`EvoDmiK/Gullinkambi`, `main`, `provisioning/dashboards/git-sync`)로 배포된다. `main`에 push하면 NAS Grafana가 pull한다.
- 이번 세션에서는 NAS에 SSH 접속이 거부되어(`Permission denied (publickey,password)`) 직접 확인하지 못했다. 반영 여부는 Grafana 화면에서 확인했다.
- JSON을 스크립트로 수정할 때는 `sort_keys=True`, `ensure_ascii=False`로 저장하고 `<`, `>`, `&`를 `<`, `>`, `&`으로 이스케이프하면 기존 파일 형식과 일치해 diff가 최소화된다.
- 이 저장소의 `main`은 다른 워크트리(`/Users/kimdove/orca/Gullinkambi`)에 체크아웃되어 있고 로컬 `main`이 뒤처져 있다. 그쪽에서는 `git pull`이 필요하다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-05-Claude-Antigravity-초기화-패널-5시간·주간-통합]]
- [[Dev/index|Dev 인덱스]]
