---
title: Hermes 모델·fallback 설정과 CLI 복구
date: 2026-10-06
author: Claude (Sonnet 5.5) with 둘기 (Dove)
category: Infra/Agents
tags:
  - birds-nest
  - hermes
  - codex
  - tailscale
  - mcp
---

# 🪶 Hermes 모델·fallback 설정과 CLI 복구

> [[2026-10-05-Kestrel-MCP-도구화와-Hermes-연결|Kestrel MCP 연결]]의 후속. hybrid-v2의 주 모델/fallback을 바꾸고, 깨져 있던 로컬 `hermes` CLI를 복구했다. 맥미니 SSH 접속 준비 상태도 점검.

## 1. 모델 / fallback 설정 (hybrid-v2)
- 주 모델: `openai-codex` / `gpt-5.6-sol` → **`gpt-6.1-sol`**
- fallback: `openai-codex` / **`gpt-6-sol`** 신규 추가
- 수정 위치는 생성 파일이 아니라 원본 `config/hermes/base.toml`:
```toml
[model]
provider = "openai-codex"
default = "gpt-6.1-sol"

[fallback_model]
provider = "openai-codex"
model = "gpt-6-sol"
```
- `scripts/hermes-control-plane.py validate` → VALID, `render`로 `hermes/profiles/hybrid-v2/config.yaml` 반영 확인.
- **리스트형 `fallback_providers`는 못 씀**: 렌더러 `dump_yaml`이 dict가 든 리스트를 지원하지 않음(`nested container lists are not supported`). 단일 매핑인 `fallback_model`을 사용. 여러 개 체인이 필요하면 렌더러 수정 필요.
- `base.toml`은 공용 레이어라 이 레이어를 쓰는 다른 프로파일에도 적용됨(현재는 hybrid-v2뿐).
- 게이트웨이 재시작은 §7 참고(완료, 새 설정 적용 확인).

## 2. 로컬 hermes CLI 복구
- 증상: `~/.local/bin/hermes` 런처만 남고 `~/.hermes/hermes-agent/venv`가 없어 실행 불가.
- 조치: 공식 `install.sh`를 내려받아 내용(클론 대상, pinned uv, 삭제/sudo 동작) 확인 후 `--skip-setup`으로 실행.
- 결과: v0.21.5 설치, 기존 `~/.hermes/config.yaml`(orca-status 플러그인) 유지, 설정 포맷 v0 → v49, 번들 스킬 58개 동기화.
- 주의: 이 설치는 `~/.hermes`(기본 HERMES_HOME)용. 저장소의 `Birds-Nest/hermes`(state.db, 프로파일)는 별도 홈이므로 쓸 때 `HERMES_HOME` 지정 필요. 저장소의 `hermes/hermes-agent/`는 빈 디렉터리(.gitignore 대상).

## 3. Claude OAuth 검토 → 보류
- Hermes는 `anthropic` 프로바이더(OAuth / `ANTHROPIC_API_KEY` / `ANTHROPIC_TOKEN`)를 지원하고 fallback으로도 사용 가능.
- **Max 5x라도 OAuth 경로는 구독 한도를 쓰지 않고 extra usage 크레딧만 과금**. 크레딧이 없으면 `HTTP 400 "You're out of extra usage."` (소스 `agent/conversation_loop.py`에서 확인). Pro는 OAuth 불가.
- 대안: 구독 포함 Agent SDK 월 크레딧을 쓰는 `claude-subscription-directsdk` 플러그인(실험적), 또는 `claude-code` 스킬로 작업 위임.
- **결정: 추가 비용 없이 OpenAI(Codex) 그대로 유지**, Claude OAuth 로그인/설정 변경 없음.

## 4. 네트워크 / 맥미니 점검
- 로컬 LAN(192.168.219.0/24)에서 ARP·mDNS로 장비 파악. NAS는 `DXP2800-B9B3`로 확인.
- 16GB 맥미니는 Tailscale에서 `dove-mini-16`(온라인, LAN 직접 연결, 3ms)로 확인됨. 다만 mDNS로 찾은 `.97`과 Tailscale이 보는 LAN IP가 달라 어느 쪽이 맞는지 미확인.
- SSH 접속 불가: 22번 포트 닫힘(원격 로그인 꺼짐). **집에서 시스템 설정 → 일반 → 공유 → 원격 로그인 켜기** 필요.

## 5. 배운 점 / 주의
- Hermes 운영 설정은 control plane이 생성하므로 `config.yaml` 직접 수정 금지, `config/hermes/*.toml` 수정 후 렌더.
- fallback이 동작하면 주 프로바이더 실패는 게이트웨이 로그에서만 보이고 사용 기록에는 fallback 모델이 최종 모델로 나타남.

## 6. 후속 과제

## 6. 커밋 / git 정리
- `6c84c5d` feat(hermes): switch primary to gpt-6.1-sol with gpt-6-sol fallback → `dev-mac` push (변경은 `config/hermes/base.toml` 하나).
- `dev-mac`은 Orca 워크트리(`~/orca/workspaces/Birds-Nest/dev-mac`)에서 사용 중이라 거기서 패치를 적용해 커밋. 워크트리에는 런타임 파일 `hermes/active_profile`이 없어 `validate`가 실패하므로, 검증은 메인 체크아웃에서 먼저 수행.
- NAS의 `dev-nas`에도 머지·push(`3269dbf`)했으나 **불필요한 작업**이었음. Hermes는 NAS가 아니라 이 맥의 OrbStack에서 돈다(§7).
- 메인 체크아웃 정리: 미커밋 변경 5개(`base.toml`, `integrations.toml`, exporter 3개)가 모두 `dev-mac`에 이미 커밋된 내용과 동일함을 확인한 뒤 폐기하고, detached HEAD를 `8a25a0e` → `6c84c5d`(dev-mac)로 이동. 이전 "메인 체크아웃을 dev-mac으로 정리" 과제 해소. `hermes/profiles/hybrid-v2/config.yaml`은 시작 시 재생성되는 런타임 파일이라 그대로 둠(`render --check` IN SYNC).

## 7. Hermes 재시작
- **Hermes(`hermes` 컨테이너)는 이 맥의 OrbStack에서 실행**됨(`docker-compose/agents/docker-compose.yml`의 `hermes-app`, 마운트가 전부 이 맥 경로). 컨테이너가 읽는 `config/hermes`는 이 맥의 메인 체크아웃.
- README 절차대로 재시작 전 스냅샷: `python3 scripts/hermes-control-plane.py snapshot` → `hermes/agent-artifacts/local/2026-10-06-hermes-control-plane/20261006T015624Z`.
- `docker restart hermes`가 멈춤 → 원인은 **OrbStack 엔진 먹통**(`docker ps`, `orbctl status`도 무응답). 앱을 종료(vmgr 프로세스는 SIGTERM)하고 다시 실행하자 약 14초 만에 Docker가 응답함. 같은 엔진의 다른 컨테이너(n8n-test, neo4j-test, openviking 등)도 함께 재기동됨.
- 확인: `hermes` healthy, 렌더된 설정에 `gpt-6.1-sol` + `fallback_model gpt-6-sol`, 게이트웨이 로그에 `✓ discord connected`, 오류 없음.
- 미확인: 새 모델로 실제 응답이 나오는지(Discord에서 Dovie 호출로 확인 필요).

## 8. 후속 과제
- [x] hybrid-v2 재시작 및 새 설정 적용 확인
- [x] `base.toml` 변경 커밋·push (`6c84c5d`)
- [x] 메인 체크아웃을 `dev-mac`으로 정리
- [ ] Discord에서 Dovie에게 말을 걸어 `gpt-6.1-sol` 실제 응답 확인(로그의 모델명도 확인)
- [ ] 맥미니(`dove-mini-16`) 원격 로그인 켜고 SSH 설정(`~/.ssh/config`), 메모리 16GB와 실제 IP(.97 vs .174) 확인
- [ ] Hermes 쪽 obsidian_vault MCP 실제 연결 확인
- [ ] 필요 시 렌더러가 dict 리스트(`fallback_providers`)를 지원하도록 개선
- [ ] `~/.ssh/config`의 `Host NAS`에 `IdentityFile` 추가(키: `nas_codex_ed25519`, 포트 99)
