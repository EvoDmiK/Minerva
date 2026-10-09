---
created: 2026-10-02
date: 2026-10-02
project: Gullinkambi
type: worklog
status: completed
tags:
  - gullinkambi
  - orca
  - telemetry
  - nginx-proxy-manager
  - cloudflare
  - git
---

# ORCA 쓰레드 이름 복구와 Birds-Nest 브랜치 정리

## 요약

ORCA 대시보드에 데이터가 안 들어온다는 문제를 확인했다. Codex·Antigravity 사용량은 실제 사용이 늦게 시작돼 반영이 늦었을 뿐 수집 경로는 정상이었다. 조사하면서 **Codex 쓰레드 이름이 하루 종일 비어 있던** 별도 문제를 찾아, 상태 DB를 스냅샷으로 넘기는 방식으로 고쳤다.

같은 날 인증서를 Cloudflare Origin으로 최종 정리했고, 원격보다 82커밋 뒤처져 있던 NAS의 Birds-Nest 체크아웃을 `dev-nas`에 맞췄다.

## 완료 결과

| 작업 | 결과 |
| --- | --- |
| ORCA 사용량 수집 | 정상 확인. 10/2 Codex·Antigravity 데이터 14:52 반영 |
| Codex 쓰레드 이름 | 스냅샷 LaunchAgent 도입, 오늘 쓰레드 이름 0/2 → 2/2 |
| 수집기 오류 로그 | `unable to open database file` 약 2,400회 → 0회 |
| 인증서 | 12개 호스트 Cloudflare Origin으로 통일, Let's Encrypt 와일드카드와 토큰 파일 삭제 |
| Birds-Nest NAS 체크아웃 | 원격 `dev-nas` 82커밋 병합 후 push |
| Birds-Nest Mac mini | `dev-mac`에 쓰레드 이름 수정 push |

## ORCA 대시보드 데이터

### 수집 경로

```text
Mac mini
  ├─ ~/.codex/sessions/*.jsonl ─────────┐
  ├─ ~/.claude/projects/*.jsonl ────────┤
  └─ orca-antigravity-usage.json ───────┼─▶ hermes-telemetry (60초) ─▶ n8n webhook ─▶ TimescaleDB
     (antigravity-orca-usage LaunchAgent, 60초)            observability.orca_usage_daily
                                                           observability.orca_thread_usage_daily
```

- Codex·Claude는 Orca worktree 루트 안에서 실행된 세션만 센다.
- Antigravity는 `worktreeId`나 `repoId`가 있는 집계만 쓴다.
- Orca 앱이 만드는 `orca-codex-usage.json`은 9/6 이후 갱신되지 않지만, 최근 구간은 세션 로그를 직접 읽으므로 영향이 없다.

### 비어 보였던 이유

| 에이전트 | 확인 내용 |
| --- | --- |
| Claude | 10/2 데이터 정상 |
| Codex | 10/1 21:27 ~ 10/2 12:52 사이 Orca 작업 폴더에서 Codex 사용 없음. 오늘 세션은 12:52에 시작됐고 사용량 기록은 14:51부터 쌓임 |
| Antigravity | 오늘 집계가 14:52에 처음 생성 |

처음 조회한 시각(14:50)이 데이터가 들어오기 2분 전이었다. 수집기가 "변경 0건"을 반복한 것도 정상 동작이었다.

## Codex 쓰레드 이름 복구

### 원인

- 수집기는 Codex 상태 DB(`~/.codex/state_5.sqlite`)의 `threads` 테이블에서 쓰레드 이름을 읽는다.
- compose가 이 DB와 `-wal`, `-shm` 파일을 **파일 단위로** 마운트하고 있었다.
- Codex는 WAL 모드라 보조 파일을 지웠다 다시 만든다. 그러면 컨테이너 안에서는 보조 파일이 사라지고, SQLite가 DB를 열지 못한다.
- 컨테이너 시작 직후부터 오류가 반복됐고, 쓰레드별 사용량 표에서 오늘 Codex 쓰레드 이름이 모두 비었다. 토큰 집계에는 영향이 없었다.

### 선택지

| 방법 | 장점 | 단점 | 결정 |
| --- | --- | --- | --- |
| A. Mac에서 필요한 칸만 스냅샷, 폴더 마운트 | 인증 정보 노출 없음, 이름 최신 유지 | LaunchAgent 추가 | **채택** |
| B. `~/.codex` 전체 읽기 전용 마운트 | 가장 간단 | Codex 로그인 정보가 컨테이너에 노출 | — |
| C. 본 DB만 `immutable`로 읽기 | 수정 최소 | 최근 이름이 WAL 정리 전까지 늦게 반영 | — |
| 컨테이너 재시작 | 즉시 복구 | 보조 파일이 다시 만들어지면 재발 | — |

### 구현

- `codex_thread_names_snapshot.py`: 상태 DB를 읽기 전용으로 열어 `threads(id, name, title)`만 rollback-journal SQLite로 복사한다. 같은 폴더의 임시 파일에 쓴 뒤 원자적으로 교체한다.
- `com.gullinkambi.codex-thread-names` LaunchAgent: 60초마다 실행한다. 실행본은 `~/Library/Application Support/Gullinkambi/`에 둔다.
- compose: 파일 3개 마운트를 `~/Library/Application Support/Gullinkambi/codex-state` 폴더 마운트 하나로 바꾸고, `HERMES_TELEMETRY_ORCA_CODEX_STATE_DB`를 `threads.sqlite`로 바꿨다.
- 수집기 컨테이너만 `--no-deps --no-build`로 다시 만들었다.
- 컨테이너에는 이제 원격 제어 등록 정보 같은 다른 테이블 없이 쓰레드 이름 세 칸만 들어간다.

### 검증

| 항목 | 결과 |
| --- | --- |
| 스냅샷 | 쓰레드 347개, 이름 347개, journal mode `delete` |
| LaunchAgent | exit 0 |
| 재시작 후 쓰레드 이름 오류 | 0건 |
| 10/2 Codex 쓰레드 이름 | 2/2 |

> [!tip] 단일 파일 bind mount 주의
> 원자적으로 교체되거나 지웠다 다시 만들어지는 파일(SQLite WAL/SHM 등)은 파일 단위로 마운트하지 말고, 그 파일이 있는 폴더를 마운트한다.

## 인증서 최종 상태

- Tailscale 경로를 되돌린 뒤 Cloudflare 경로만 쓰므로 Cloudflare Origin 인증서로 통일했다.
- 12개 프록시 호스트 모두 `Cloudflare Origin *.dove-nest.com` 사용, 정상 응답 확인.
- Let's Encrypt 와일드카드 인증서를 NPM에서 삭제했고, NAS의 인증서 파일과 DNS Challenge 토큰 파일도 남아 있지 않다.
- 다음 단계로 Cloudflare SSL 모드 **Full (strict)**를 권장했다. Origin 인증서가 2041년까지 유효해 막힐 위험이 낮고, 원본 인증서 검증으로 중간자 공격과 인증서 방치를 막는다.

## Birds-Nest 브랜치 정리

### NAS 체크아웃

| 항목 | 내용 |
| --- | --- |
| 정리 전 | `dev-nas`가 원격보다 82커밋 뒤, 오늘 작업 4커밋 앞 |
| 원격 변경 범위 | Mac mini 전용 설정(`macmini` 프로필), 이미 적용된 DB·n8n 정의, 문서, 새 테스트 스택 |
| NAS 실행 서비스 영향 | 없음 (컨테이너 재시작 안 함) |
| 겹친 파일 | `docker-compose/monitoring/docker-compose.yml` 하나, 자동 병합 |
| 검증 | `monitoring`, `npm` compose 설정 검증 통과 |
| 결과 | `dev-nas` push (`3a7e21e..d3b3216`) |
| 백업 | 로컬 `backup/dev-nas-before-sync-20261002` |

`feat/npm-exporter`의 커밋은 모두 `dev-nas`에 포함됐다. 원격 브랜치 삭제는 자동 실행이 권한 확인에 걸려 직접 정리하기로 했다.

### Mac mini 체크아웃

- `dev-mac`에 쓰레드 이름 수정 커밋(`b9a0e01`)을 push했다.
- 기존 미커밋 변경 `hermes/profiles/hybrid-v2/config.yaml`은 건드리지 않았다.

## Git 기록

| 저장소 | 브랜치 | 커밋 | 내용 |
| --- | --- | --- | --- |
| Birds-Nest | `dev-mac` | `b9a0e01` | Codex 쓰레드 이름 스냅샷 |
| Birds-Nest | `dev-nas` | `d3b3216` | 원격 `dev-nas` 병합 (NPM 수집기·Split DNS 되돌림 포함) |

## 남은 일

- [ ] Cloudflare SSL 모드 Full (strict) 전환 후 12개 호스트 확인
- [ ] Cloudflare에서 와일드카드 발급용 API 토큰 삭제
- [ ] 원격 `feat/npm-exporter` 브랜치 삭제
- [ ] 문제없으면 로컬 백업 브랜치 정리
- [ ] 원본 443을 Cloudflare IP 대역만 허용하도록 제한 검토

## 관련

- [[Work/Gullinkambi/작업기록/2026-10-02-Tailscale-Split-DNS와-와일드카드-인증서|Tailscale Split DNS와 와일드카드 인증서]]
- [[Work/Gullinkambi/작업기록/2026-10-02-NPM-모니터링-수집기와-Cloudflare-Origin-인증서|NPM 모니터링 수집기와 Cloudflare Origin 인증서]]
- [[Work/Gullinkambi/작업기록/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구|ORCA Antigravity 사용량 집계와 Hermes 인증 복구]]
- [[Work/RobinGraph/작업기록/2026-10-02-임베딩-API-내부망-직접-호출|임베딩 API 내부망 직접 호출]]
- [[Dev/인프라/2026-10-02-홈랩-인증서·Cloudflare·접속-경로-비교-정리|홈랩 인증서·Cloudflare·접속 경로 비교 정리]]
- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Home]]
