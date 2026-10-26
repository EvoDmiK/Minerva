---
created: 2026-10-26
date: 2026-10-26
project: Gullinkambi
type: worklog
status: completed
title: Mac mini 16 ORCA 수집 범위 확대
tags:
  - worklog
  - gullinkambi
  - orca
  - macmini
  - telemetry
---
# Mac mini 16 ORCA 수집 범위 확대

"오늘도 ORCA 집계가 안 된다"는 문제를 조사했다. Mac mini 16에서 Orca로 실행한 세션 중 `~/orca` 밖 폴더에서 돈 세션이 통째로 빠지고 있었다.

## 결과
- Mac mini 16의 Orca 수집 범위를 `/Users/kimdove/orca`에서 홈 전체 `/Users/kimdove`로 넓혔다.
- 빠졌던 10/24~10/26 사용량을 다시 채웠다(Mac mini 16 기준).

| 날짜 | 수정 전 | 수정 후 |
|---|---|---|
| 10/24 | Codex 1.26억 | Codex 1.65억, Claude 2,800만 |
| 10/25 | 없음 | Codex 1.07억, Claude 3,400만, Antigravity 44만(95건) |
| 10/26 | Codex 29만 | Codex 322만, Claude 48만 |

- 일별 합계(`orca_usage_daily`)와 호출 이벤트 합계(`orca_call_events`)가 Claude·Codex에서 일치하는 것을 확인했다.

## 진단 순서
1. **수집기 확인:** Mac mini 32와 Mac mini 16 수집기 둘 다 전송에 성공하고 있었다. Mac mini 32는 원본 로그 건수와 DB 건수가 일치했다(10/24 Claude 314건 등).
2. **DB와 대시보드 확인:** NAS DB(`timeseries` DB, `observability` 스키마)에 오늘 데이터가 있었다. ORCA 탭 SQL을 `grafana_reader` 권한으로 돌려도 값이 나왔다. 그래서 저장과 표시 쪽 문제는 아니었다.
3. **원인:** `orca search --environment Macmini-16`으로 오늘 세션을 보니 `Banking77 GCD Agentic Flow 보고서` 등이 `~/Desktop/Homework/gcd-baseline`에서 실행됐다. 이 경로는 수집 범위 밖이어서 집계에서 빠졌다.
   - Orca CLI(`repo list`, `worktree list`)로는 원격 환경의 작업 폴더 목록을 얻을 수 없었다.
   - Mac mini 16은 Orca 원격 작업 전용 호스트라서, 폴더를 하나씩 추가하는 대신 홈 전체를 범위로 잡았다.

## 조치
- 수집기 compose(Birds-Nest `hermes-telemetry/compose.macmini16.yml`): `HERMES_TELEMETRY_ORCA_WORKTREE_ROOTS=/Users/kimdove`.
- Antigravity LaunchAgent(`com.gullinkambi.antigravity-orca-usage`): `--worktree-root /Users/kimdove`.
- 상태 볼륨 `telemetry_state`의 `cursor.json`에서 아래 키를 지웠다. 이미 스캔한 파일은 다시 읽지 않기 때문이다.
  - `orca_call_files`
  - `orca_raw_files`, `orca_thread_raw_files`
  - `orca_usage_revision`, `orca_thread_usage_revision`
  - 이미 보낸 이벤트는 `orca_calls`에 지문으로 남아 있어서 중복 전송되지 않는다.

## 배포
| 대상 | 커밋 / 방법 |
|---|---|
| Birds-Nest `dev-codex` | `7be3bc2`(Mac mini 16 범위 확대) |
| Mac mini 16 | `~/Library/Application Support/Gullinkambi/telemetry/docker-compose.yml` 교체(백업 `.bak-20261026`), `docker compose up -d` |

## 알아 둘 점
- 범위를 홈 전체로 넓혀서, Mac mini 16에서 Orca를 거치지 않고 직접 실행한 에이전트도 ORCA에 합쳐진다.
- 다시 보내는 도중 n8n 웹훅에서 Cloudflare 522가 몇 번 났다. 다시 시도하니 1초 안에 들어갔다. NAS SSH가 꺼졌다 켜지던 시간대와 겹친 일시적인 문제로 판단했다.
- LaunchAgent 인자를 `plutil -replace`로 바꿀 때 기존 값이 뒤에 남아(`unrecognized arguments`), 약 15분 동안 Antigravity 집계가 실패했다. 고친 뒤 빠진 데이터는 없다.
- 수집기 stdout이 버퍼링돼서 `docker logs` 줄이 몰려서 찍힌다. 시각만 보고 수집이 멈췄다고 판단하면 안 된다.
- Mac mini 16 Antigravity는 일별 합계(10/22 1,455만)와 호출 이벤트 합계(10/22 1.97억)의 차이가 크다. 이번 범위 밖의 기존 문제로, 집계 기준 차이로 추정하며 확인하지 않았다.

## 남은 일
- Mac mini 16 Antigravity 일별 합계와 호출 이벤트 합계의 차이 확인.

## 관련
- [[Work/Gullinkambi/작업기록/2026-10-24-Mac-mini-16-관측-추가와-Antigravity-할당량-대시보드|Mac mini 16 관측 추가와 Antigravity 할당량 대시보드]]
- [[Work/Gullinkambi/Gullinkambi 작업 백로그|작업 백로그]]
