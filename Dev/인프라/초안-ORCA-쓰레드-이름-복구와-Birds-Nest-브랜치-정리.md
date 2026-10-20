---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-02-ORCA-쓰레드-이름-복구와-Birds-Nest-브랜치-정리]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# ORCA 쓰레드 이름 복구와 Birds-Nest 브랜치 정리

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-02-ORCA-쓰레드-이름-복구와-Birds-Nest-브랜치-정리]] · 분류 근거 {"인프라":53,"자동화":3,"관측성":8,"데이터":1}

## 1. 개요 및 목적

ORCA 대시보드에 데이터가 안 들어온다는 문제를 확인했다. Codex·Antigravity 사용량은 실제 사용이 늦게 시작돼 반영이 늦었을 뿐 수집 경로는 정상이었다. 조사하면서 **Codex 쓰레드 이름이 하루 종일 비어 있던** 별도 문제를 찾아, 상태 DB를 스냅샷으로 넘기는 방식으로 고쳤다.

같은 날 인증서를 Cloudflare Origin으로 최종 정리했고, 원격보다 82커밋 뒤처져 있던 NAS의 Birds-Nest 체크아웃을 `dev-nas`에 맞췄다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 완료 결과
- ORCA 대시보드 데이터
- 수집 경로
- 비어 보였던 이유
- Codex 쓰레드 이름 복구
- 원인
- 선택지
- 구현
- 검증
- 인증서 최종 상태
- Birds-Nest 브랜치 정리
- NAS 체크아웃
- Mac mini 체크아웃
- Git 기록
- 남은 일
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
Mac mini
  ├─ ~/.codex/sessions/*.jsonl ─────────┐
  ├─ ~/.claude/projects/*.jsonl ────────┤
  └─ orca-antigravity-usage.json ───────┼─▶ hermes-telemetry (60초) ─▶ n8n webhook ─▶ TimescaleDB
     (antigravity-orca-usage LaunchAgent, 60초)            observability.orca_usage_daily
                                                           observability.orca_thread_usage_daily
```

## 4. 검증 근거 및 트러블슈팅

ORCA 대시보드에 데이터가 안 들어온다는 문제를 확인했다. Codex·Antigravity 사용량은 실제 사용이 늦게 시작돼 반영이 늦었을 뿐 수집 경로는 정상이었다. 조사하면서 **Codex 쓰레드 이름이 하루 종일 비어 있던** 별도 문제를 찾아, 상태 DB를 스냅샷으로 넘기는 방식으로 고쳤다.

| 작업 | 결과 |
| --- | --- |
| ORCA 사용량 수집 | 정상 확인. 10/2 Codex·Antigravity 데이터 14:52 반영 |
| Codex 쓰레드 이름 | 스냅샷 LaunchAgent 도입, 오늘 쓰레드 이름 0/2 → 2/2 |
| 수집기 오류 로그 | `unable to open database file` 약 2,400회 → 0회 |
| 인증서 | 12개 호스트 Cloudflare Origin으로 통일, Let's Encrypt 와일드카드와 토큰 파일 삭제 |
| Birds-Nest NAS 체크아웃 | 원격 `dev-nas` 82커밋 병합 후 push |
| Birds-Nest Mac mini | `dev-mac`에 쓰레드 이름 수정 push |

| 에이전트 | 확인 내용 |
| --- | --- |
| Claude | 10/2 데이터 정상 |
| Codex | 10/1 21:27 ~ 10/2 12:52 사이 Orca 작업 폴더에서 Codex 사용 없음. 오늘 세션은 12:52에 시작됐고 사용량 기록은 14:51부터 쌓임 |
| Antigravity | 오늘 집계가 14:52에 처음 생성 |

- 수집기는 Codex 상태 DB(`~/.codex/state_5.sqlite`)의 `threads` 테이블에서 쓰레드 이름을 읽는다.
- compose가 이 DB와 `-wal`, `-shm` 파일을 **파일 단위로** 마운트하고 있었다.
- Codex는 WAL 모드라 보조 파일을 지웠다 다시 만든다. 그러면 컨테이너 안에서는 보조 파일이 사라지고, SQLite가 DB를 열지 못한다.
- 컨테이너 시작 직후부터 오류가 반복됐고, 쓰레드별 사용량 표에서 오늘 Codex 쓰레드 이름이 모두 비었다. 토큰 집계에는 영향이 없었다.

| 항목 | 결과 |
| --- | --- |
| 스냅샷 | 쓰레드 347개, 이름 347개, journal mode `delete` |
| LaunchAgent | exit 0 |
| 재시작 후 쓰레드 이름 오류 | 0건 |
| 10/2 Codex 쓰레드 이름 | 2/2 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-02-ORCA-쓰레드-이름-복구와-Birds-Nest-브랜치-정리]]
- [[Dev/index|Dev 인덱스]]
