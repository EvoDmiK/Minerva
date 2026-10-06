---
created: 2026-10-06
date: 2026-10-05
project: Gullinkambi
type: worklog
status: completed
tags:
  - gullinkambi
  - grafana
  - claude
  - antigravity
  - monitoring
---

# Claude·Antigravity 초기화 패널 5시간·주간 통합

## 요약

`AI 구독` 탭의 Claude·Antigravity 초기화 시각 패널을 각각 5시간·주간 두 값이 한 패널에 위아래로 보이도록 바꿨다. 변경은 `main`에 반영했고 NAS Grafana Git Sync가 이를 받아 두 줄로 표시되는 것을 확인했다.

## 변경 내용

| 패널 | 변경 전 | 변경 후 |
| --- | --- | --- |
| `panel-ai-subscription-6` | `Claude · 다음 초기화` (5시간만) | `Claude · 초기화` (5시간 + 주간) |
| `panel-ai-subscription-17` | `Antigravity · 다음 초기화` (5시간만) | `Antigravity · 초기화` (5시간 + 주간) |

- 각 패널은 쿼리 두 개를 가진다. 라벨은 `5시간`(`window="session"`)과 `주간`(`window="weekly"`)이다.
- Antigravity는 기존처럼 `pool="gemini"`만 조회한다. `third_party` 풀은 대시보드 대상이 아니다.
- 쿼리는 `max(ai_subscription_quota_reset_timestamp_seconds{...} > time()) * 1000` 형태다. 초기화 시각이 지난 구간은 해당 줄만 `초기화됨 · 갱신 대기`로 표시한다.
- 레이아웃 크기와 위치는 그대로다. Codex `주간 초기화` 패널은 변경하지 않았다.

## 표시 조정

1. 처음에 `orientation: vertical`을 적용했더니 5시간·주간이 위아래가 아니라 가로로 나란히 표시되어 두 줄 배치를 다시 요청받았다. Grafana stat 패널의 `vertical`은 값들을 가로로 나란히 놓고, `horizontal`이 위아래로 쌓는다.
2. `orientation: horizontal`로 바꿔 두 줄 배치를 확인했다.
3. 글자를 키워 달라는 요청에 `text.valueSize: 28`, `text.titleSize: 14`로 고정했다. stat 패널에는 줄 간격 설정이 따로 없어, 글자 크기를 키워 상대적인 간격을 줄였다.

## Git 기록

| 커밋 | 내용 |
| --- | --- |
| `75ab0c8` | Claude·Antigravity 초기화 패널에 5시간·주간 통합 |
| `9610151` | 5시간·주간 값을 세로로 배치 (`orientation: horizontal`) |
| `ef2df4d` | 초기화 패널 글자 크기 확대 |

- 세 커밋 모두 `origin/main`에 fast-forward로 push했다.
- 작업용으로 임시로 올렸던 원격 `EvoDmiK/main` 브랜치는 삭제했다.
- 수정한 파일은 `provisioning/dashboards/git-sync/Aviary Control Room.json` 하나다.

## 운영 메모

- 이 대시보드는 Grafana Git Sync(`EvoDmiK/Gullinkambi`, `main`, `provisioning/dashboards/git-sync`)로 배포된다. `main`에 push하면 NAS Grafana가 pull한다.
- 이번 세션에서는 NAS에 SSH 접속이 거부되어(`Permission denied (publickey,password)`) 직접 확인하지 못했다. 반영 여부는 Grafana 화면에서 확인했다.
- JSON을 스크립트로 수정할 때는 `sort_keys=True`, `ensure_ascii=False`로 저장하고 `<`, `>`, `&`를 `<`, `>`, `&`으로 이스케이프하면 기존 파일 형식과 일치해 diff가 최소화된다.
- 이 저장소의 `main`은 다른 워크트리(`/Users/kimdove/orca/Gullinkambi`)에 체크아웃되어 있고 로컬 `main`이 뒤처져 있다. 그쪽에서는 `git pull`이 필요하다.

## 관련

- [[Work/Gullinkambi/2026-10-03-AI-subscription-exporter-README|AI subscription exporter README]]
- [[Work/Gullinkambi/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축|AI 구독 사용량 수집기·Grafana 대시보드 구축]]
- [[Work/Gullinkambi/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구|ORCA Antigravity 사용량 집계와 Hermes 인증 복구]]
- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
