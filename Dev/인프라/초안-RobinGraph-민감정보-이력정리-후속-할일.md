---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-12-RobinGraph-민감정보-이력정리-후속-할일]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RobinGraph] 민감정보 이력 정리 — 집에서 할 일

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-12-RobinGraph-민감정보-이력정리-후속-할일]] · 분류 근거 {"인프라":6,"자동화":1,"관측성":1,"데이터":0}

## 1. 개요 및 목적

2026-10-12에 공개(PUBLIC) 저장소 `EvoDmiK/RobinGraph`의 민감정보를 정리했다.

- 실제 비밀번호·API 키는 없었다. 노출된 것은 NAS 계정·IP·SSH 포트, 내부 도메인, Tailscale 노드명, 개인 이메일, 로컬 호스트명 같은 인프라·개인 정보였다.
- 문서를 마스킹한 뒤 `git filter-repo`로 **전체 커밋 이력을 다시 썼다.** 작성자 이메일은 전부 GitHub noreply로 바꿨다.
- 브랜치 4개(`main`, `dev`, `dev-claude`, `dev-codex`)를 force push했다. 그래서 **모든 커밋 해시가 바뀌었다.**
- 상세 기록: 저장소 `docs/work-log/2026-10-12-public-repo-sensitive-info-doc-masking.md`

## 2. 핵심 아키텍처 및 원칙

- 배경
- 필수 — 먼저 할 것
- 1. 집 Mac 체크아웃을 새 이력으로 맞추기
- 2. NAS 쪽 체크아웃·릴리스 디렉터리 정리
- 3. 커밋 이메일을 noreply로 바꾸기
- 선택 — 시간 날 때
- 4. GitHub에 남은 옛 커밋 삭제 요청
- 5. 코드에 남긴 Discord ID 정리 여부 결정
- 6. 감사 스크립트 사용법 변경 알아두기
- 7. 백업 폴더 처리
- 8. Minerva vault도 점검
- 참고 — 검증 결과 요약

## 3. 재사용 가능한 코드 스니펫 / 설정

  ```bash
  git fetch origin --prune
  git checkout main && git reset --hard origin/main
  # 로컬에 있는 다른 브랜치도 각각
  git checkout dev && git reset --hard origin/dev
  git checkout dev-claude && git reset --hard origin/dev-claude
  git checkout dev-codex && git reset --hard origin/dev-codex
  ```

  ```bash
  git reflog expire --expire=now --all && git gc --prune=now
  ```

  ```bash
  git config --global user.email "93193661+EvoDmiK@users.noreply.github.com"
  # 저장소에만 적용하려면 --global 대신 저장소 안에서 git config user.email ...
  ```

## 4. 검증 근거 및 트러블슈팅

- [ ] 미커밋 변경이 있는지 확인한다: `git status`
  - 변경이 있으면 `git diff > ~/rg-local-changes.patch`로 따로 저장해 둔다.
- [ ] 각 체크아웃·worktree에서 새 이력으로 맞춘다.
  - 체크아웃이 많거나 헷갈리면 지우고 새로 `git clone` 하는 편이 더 안전하다.
- [ ] 저장해 둔 패치가 있으면 다시 적용한다: `git apply ~/rg-local-changes.patch`
- [ ] 옛 객체를 정리한다(선택).
- [ ] 확인: `git log -3 --format="%h %ae %s"`에 noreply 이메일과 새 해시가 보이면 된다.

- [ ] NAS 홈에 있는 RobinGraph 체크아웃과 릴리스 디렉터리를 확인한다.
  - 새로 배포할 때는 반드시 새 이력에서 받은 코드로 한다.
  - 옛 체크아웃에서는 push하지 않는다.
- [ ] 운영 컨테이너, 이미지, DB는 **건드릴 필요가 없다.** 이번 변경은 git 이력과 문서뿐이고 운영 동작에는 변화가 없다.

- [ ] Windows PC와 집 Mac 모두에서 실행한다.
- [ ] 확인: `git config user.email`

- [ ] `compose.nas.yml`과 `scripts/deploy_n8n_*.py`에 Discord guild/channel ID 기본값이 남아 있다. 운영 동작 때문에 일부러 남겨두었다.
- [ ] 지우려면 먼저 NAS `.env.nas.ingest`에 아래 두 값이 들어 있는지 확인한다.
  - `ROBINGRAPH_DISCORD_GUILD_ID`
  - `ROBINGRAPH_DISCORD_CHANNEL_ID`
- [ ] 값이 들어 있으면 코드 기본값을 빈칸으로 바꾸도록 Claude에게 요청한다. 이력에서까지 지우려면 filter-repo를 한 번 더 해야 한다.

| 항목 | 재작성 전 | 재작성 후 |
|---|---|---|
| 이력 전체에서 민감값이 든 파일 버전 | 17,233건 | 0건 |
| 커밋 메시지 속 민감값 | 1건 | 0건 |
| 작성자 이메일 | 4종 | noreply 1종 |
| 커밋 수 | 319 | 319 |
| 이미지·영상 파일 | — | 해시 동일(손상 없음) |
| 테스트 | unittest 실패 31, node 실패 2 | 동일(기존 실패, 새 실패 없음) |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-12-RobinGraph-민감정보-이력정리-후속-할일]]
- [[Dev/index|Dev 인덱스]]
