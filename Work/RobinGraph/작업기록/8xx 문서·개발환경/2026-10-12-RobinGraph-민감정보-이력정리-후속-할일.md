---
created: 2026-10-12
date: 2026-10-12
project: RobinGraph
category: "8xx 문서·개발환경"
type: worklog
status: open
tags:
  - worklog
  - robingraph
  - security
  - git
  - todo
---
# [RobinGraph] 민감정보 이력 정리 — 집에서 할 일

## 배경

2026-10-12에 공개(PUBLIC) 저장소 `EvoDmiK/RobinGraph`의 민감정보를 정리했다.

- 실제 비밀번호·API 키는 없었다. 노출된 것은 NAS 계정·IP·SSH 포트, 내부 도메인, Tailscale 노드명, 개인 이메일, 로컬 호스트명 같은 인프라·개인 정보였다.
- 문서를 마스킹한 뒤 `git filter-repo`로 **전체 커밋 이력을 다시 썼다.** 작성자 이메일은 전부 GitHub noreply로 바꿨다.
- 브랜치 4개(`main`, `dev`, `dev-claude`, `dev-codex`)를 force push했다. 그래서 **모든 커밋 해시가 바뀌었다.**
- 상세 기록: 저장소 `docs/work-log/2026-10-12-public-repo-sensitive-info-doc-masking.md`

| 브랜치 | 이전 | 이후 |
|---|---|---|
| main | `e4a1b4b` | `1745eca` (이후 `eca1d56` 작업기록 커밋 추가) |
| dev | `8db363b` | `07b1cf8` |
| dev-claude | `e592951` | `56a4261` |
| dev-codex | `5b297f5` | `dea9d8a` |

## 필수 — 먼저 할 것

### 1. 집 Mac 체크아웃을 새 이력으로 맞추기

> [!warning] 옛 이력이 남은 체크아웃에서 `push`나 `merge`를 하면 지운 값이 다시 올라간다. 아무 작업도 하기 전에 먼저 맞춘다.

- [ ] 미커밋 변경이 있는지 확인한다: `git status`
  - 변경이 있으면 `git diff > ~/rg-local-changes.patch`로 따로 저장해 둔다.
- [ ] 각 체크아웃·worktree에서 새 이력으로 맞춘다.
  ```bash
  git fetch origin --prune
  git checkout main && git reset --hard origin/main
  # 로컬에 있는 다른 브랜치도 각각
  git checkout dev && git reset --hard origin/dev
  git checkout dev-claude && git reset --hard origin/dev-claude
  git checkout dev-codex && git reset --hard origin/dev-codex
  ```
  - 체크아웃이 많거나 헷갈리면 지우고 새로 `git clone` 하는 편이 더 안전하다.
- [ ] 저장해 둔 패치가 있으면 다시 적용한다: `git apply ~/rg-local-changes.patch`
- [ ] 옛 객체를 정리한다(선택).
  ```bash
  git reflog expire --expire=now --all && git gc --prune=now
  ```
- [ ] 확인: `git log -3 --format="%h %ae %s"`에 noreply 이메일과 새 해시가 보이면 된다.

### 2. NAS 쪽 체크아웃·릴리스 디렉터리 정리

- [ ] NAS 홈에 있는 RobinGraph 체크아웃과 릴리스 디렉터리를 확인한다.
  - 새로 배포할 때는 반드시 새 이력에서 받은 코드로 한다.
  - 옛 체크아웃에서는 push하지 않는다.
- [ ] 운영 컨테이너, 이미지, DB는 **건드릴 필요가 없다.** 이번 변경은 git 이력과 문서뿐이고 운영 동작에는 변화가 없다.

### 3. 커밋 이메일을 noreply로 바꾸기

> [!info] GitHub에 "Block command line pushes that expose my email"이 켜져 있다. 개인 메일로 커밋하면 push가 거절된다.

- [ ] Windows PC와 집 Mac 모두에서 실행한다.
  ```bash
  git config --global user.email "93193661+EvoDmiK@users.noreply.github.com"
  # 저장소에만 적용하려면 --global 대신 저장소 안에서 git config user.email ...
  ```
- [ ] 확인: `git config user.email`

## 선택 — 시간 날 때

### 4. GitHub에 남은 옛 커밋 삭제 요청

- [ ] 머지된 PR(#4~#8 등)의 `refs/pull/*`는 force push로 바꿀 수 없다. 그래서 옛 커밋을 **해시로 직접 열면** 아직 보인다.
- [ ] 완전히 지우려면 GitHub Support → "Remove sensitive data / cached views" 요청을 보낸다.
  - 대상 저장소: `EvoDmiK/RobinGraph`
  - force push 완료, fork 0개라고 함께 적는다.

### 5. 코드에 남긴 Discord ID 정리 여부 결정

- [ ] `compose.nas.yml`과 `scripts/deploy_n8n_*.py`에 Discord guild/channel ID 기본값이 남아 있다. 운영 동작 때문에 일부러 남겨두었다.
- [ ] 지우려면 먼저 NAS `.env.nas.ingest`에 아래 두 값이 들어 있는지 확인한다.
  - `ROBINGRAPH_DISCORD_GUILD_ID`
  - `ROBINGRAPH_DISCORD_CHANNEL_ID`
- [ ] 값이 들어 있으면 코드 기본값을 빈칸으로 바꾸도록 Claude에게 요청한다. 이력에서까지 지우려면 filter-repo를 한 번 더 해야 한다.

### 6. 감사 스크립트 사용법 변경 알아두기

- [ ] `scripts/audit_trait_coverage.py`의 `--ssh` 기본값이 placeholder(`<nas-user>@<nas-host>`)로 바뀌었다.
  - 실행할 때는 `--ssh 계정@NAS주소`를 직접 넘긴다.
  - `--port` 기본값은 그대로다.

### 7. 백업 폴더 처리

- [ ] Windows PC `Downloads\RobinGraph-history-backup-20261012\`에 이력 재작성 전 원본 mirror가 있다. **원래 민감값이 들어 있다.**
  - 며칠 써보고 문제가 없으면 지우거나, 공유되지 않는 곳으로 옮긴다.
  - 그 폴더를 git 저장소나 OneDrive 공유 폴더에 넣지 않는다.

### 8. Minerva vault도 점검

- [ ] 이 vault(`EvoDmiK/Minerva`)도 **PUBLIC**이다.
  - RobinGraph 작업기록에 NAS IP, 계정, SSH 포트, 내부 도메인이 적혀 있을 수 있다.
  - 같은 방식으로 점검하도록 Claude에게 요청한다: "Minerva 폴더도 민감정보 점검해줘"

## 참고 — 검증 결과 요약

| 항목 | 재작성 전 | 재작성 후 |
|---|---|---|
| 이력 전체에서 민감값이 든 파일 버전 | 17,233건 | 0건 |
| 커밋 메시지 속 민감값 | 1건 | 0건 |
| 작성자 이메일 | 4종 | noreply 1종 |
| 커밋 수 | 319 | 319 |
| 이미지·영상 파일 | — | 해시 동일(손상 없음) |
| 테스트 | unittest 실패 31, node 실패 2 | 동일(기존 실패, 새 실패 없음) |

---

## 관련 문서

- [[Home|🏠 홈으로]]
- [[Work/RobinGraph/index|RobinGraph 프로젝트 인덱스]]
- [[Work/RobinGraph/RobinGraph 작업 백로그|RobinGraph 작업 백로그]]
