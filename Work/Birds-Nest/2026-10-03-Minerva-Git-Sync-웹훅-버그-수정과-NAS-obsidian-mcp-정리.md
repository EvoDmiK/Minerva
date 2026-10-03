---
title: Minerva Git Sync 웹훅 버그 수정과 NAS obsidian-mcp 정리
date: 2026-10-03
author: Claude (Opus 5.5) with 둘기 (Dove)
category: Infra/Wiki
tags:
  - infra
  - birds-nest
  - obsidian
  - git-sync
  - magpie
  - n8n
  - mcp
  - troubleshooting
---

# 🔧 Minerva Git Sync 웹훅 버그 수정과 NAS obsidian-mcp 정리

> 오전에 구축한 [[Work/Birds-Nest/2026-10-03-Magpie-기반-Minerva-볼트-실시간-Git-Sync-파이프라인-구축|Magpie 기반 Git Sync 파이프라인]]의 후속 작업.

## 1. 증상
- 볼트 변경은 GitHub(`EvoDmiK/Minerva`)로 정상 commit/push 되지만, Discord `#llm-위키` 알림이 오지 않음.
- n8n 로그: push 때마다 `Error in handling webhook request POST /webhook/minerva-sync: Failed to parse request body`.

## 2. 원인 (`docker-compose/homelab/obsidian-git-sync/sync.sh`)
1. **한글 파일명 → 깨진 JSON** (실제 장애 원인)
   - Git 기본값(`core.quotePath=true`)이 한글 경로를 `"\354\236\221..."`처럼 8진수 이스케이프 + 따옴표로 출력.
   - 스크립트가 다시 따옴표로 감싸 `[""\354..."]` 형태가 되어 n8n이 422로 거부.
   - `curl -s`가 HTTP 상태를 확인하지 않아 실패가 로그에 드러나지 않음.
2. **pull만 해도 "Push 완료" 알림**: 다른 기기의 변경을 pull해 HEAD가 바뀌면 push·알림을 보내는 조건.
3. **inotify 실패 시 무한 반복**: `inotifywait` 에러(예: `max_user_watches` 초과)를 "변경 없음"으로 처리해 sync가 쉬지 않고 실행됨. 에러 출력도 숨겨져 있었음. (NAS 한도는 2,000,000이라 운영에서는 미발생)

## 3. 수정
- `git diff --name-only -z`로 원본 경로를 받고, JSON용으로 `\`·`"` 이스케이프.
- `git rev-list --count origin/main..HEAD`가 0이면 push·알림 생략 (원격에 없는 로컬 커밋이 있을 때만 push).
- `inotifywait` 종료 코드 구분: 0 = 변경, 2 = 타임아웃, 그 외 = 경고 로그 후 interval 간격 폴링.
- 로컬에서 alpine 이미지 빌드 + bare remote + 가짜 webhook 서버로 E2E 테스트 (한글/따옴표/백슬래시 파일명, 원격 전용 변경, 무변경, inotify 실패).

## 4. 배포와 검증
- 커밋 `13a561b` → `dev-mac` push → NAS `/volume3/Birds-Nest`(`dev-nas`)에서 merge → `docker compose up -d --build obsidian-git-sync`.
- 테스트 문서 `Test/동기화 테스트 2026-10-03.md` 생성 → 커밋 `39e18e6` push → n8n 실행 #22218 **success**, parse 에러 사라짐.
- ⚠️ 발견: `39e18e6`은 sidecar가 아니라 obsidian 컨테이너의 Obsidian Git 플러그인이 만든 커밋(메시지 `84eacea65c0a 2026-10-3:14:31:9`). 자동 커밋 주체가 둘이라 단일 Writer 원칙과 어긋남 → 플러그인 자동 커밋 비활성화 검토 필요.

## 5. Obsidian MCP 정리
- **NAS `obsidian-mcp` 컨테이너 제거** (커밋 `e9ca118`)
  - 오늘 커밋 `2fb534f`에서 명령을 `npx -y obsidian-mcp-server@...` → `obsidian-mcp-server`로 바꿨지만 `supercorp/supergateway` 이미지에 바이너리가 없어 세션마다 `exit 127`.
  - `/healthz`는 gateway만 확인해 정상처럼 보였음.
  - 참조하는 n8n 워크플로·Hermes 설정이 없어 서비스 정의와 `docker-compose.override.yml`을 삭제하고 컨테이너 제거.
- **Claude Code에 `obsidian_vault` MCP 등록**: Codex 설정과 동일하게 `https://wiki.dove-nest.com/mcp` (Streamable HTTP, Bearer 인증, user scope). 이제 Codex·Claude Code 모두 같은 엔드포인트 사용.
- ⚠️ 서버 보안 경고: semantic-vault-mcp 플러그인이 `0.0.0.0:3443`에서 평문 HTTP로 열려 있음. 외부 구간은 Cloudflare HTTPS지만 LAN 노출이 의도가 아니면 `127.0.0.1` 바인딩 권장.

## 6. 기타
- `ai-subscription-exporter`: Claude Code OAuth 토큰으로 `/api/oauth/usage`를 조회해 계정 전체 5시간·7일 사용률을 수집하는 변경을 커밋 (`417d335`, 테스트 11개 통과).
- NAS SSH는 `~/.ssh/config`의 `Host NAS`에 키가 지정되지 않아 `-i ~/.ssh/nas_codex_ed25519`로 접속.

## 7. 후속 과제
- [ ] Obsidian Git 플러그인 자동 커밋 끄기 (sidecar 단일 Writer)
- [ ] `Test/동기화 테스트 2026-10-03.md` 정리
- [ ] semantic-vault-mcp 바인딩을 loopback으로 제한할지 결정
- [ ] `~/.ssh/config` `Host NAS`에 `IdentityFile ~/.ssh/nas_codex_ed25519` 추가
