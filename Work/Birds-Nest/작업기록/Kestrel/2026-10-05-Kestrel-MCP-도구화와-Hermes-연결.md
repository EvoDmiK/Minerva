---
title: Kestrel MCP 도구화와 Hermes 연결
date: 2026-10-05
author: Claude (Opus 5.5) with 둘기 (Dove)
category: Infra/Automation
tags:
  - birds-nest
  - n8n
  - kestrel
  - mcp
  - hermes
  - codex
---

# 🦅 Kestrel MCP 도구화와 Hermes 연결

> [[2026-10-03-Codex-사용량-리셋-모니터링-워크플로우-구축|Kestrel 구축]]의 후속 작업. 알림만 보내던 Kestrel을 에이전트가 질문할 수 있는 MCP 도구로 확장.

## 1. 목표
- Discord에서 Dovie(Hermes)에게 "Codex 다음 리셋 언제야?"처럼 물으면, Hermes가 Kestrel을 통해 실시간 리셋 현황을 조회해 답하도록 한다.
- MCP는 도구 호출이므로 대화는 에이전트가 맡고, Kestrel은 데이터를 제공한다. (n8n에 Discord 메시지 트리거가 없어 Kestrel이 직접 대화하는 구조보다 단순)

## 2. 구성
```
기존: Schedule(5분) → Fetch Reset Status → Detect New Events → Discord Alert
추가: Kestrel MCP (MCP Server Trigger, /mcp/kestrel, Bearer 인증)
       └─ get_codex_reset_status (HTTP Request Tool → https://codex-resets.com/api/v1/status)
```
- 도구 설명에 "시각은 KST로 바꿔 답할 것"을 넣어 응답 정리는 에이전트에 맡김 (Detect New Events 로직 재사용 없이 노드 하나로 처리).
- 인증: n8n credential `Kestrel MCP`(Bearer). 토큰 없이 접근하면 403.
- 엔드포인트: `https://workflow.dove-nest.com/mcp/kestrel`

## 3. Hermes 연결 (hybrid-v2 / Dovie)
- `config/hermes/integrations.toml`에 `mcp_servers.kestrel` 추가 (`Authorization: Bearer ${KESTREL_MCP_TOKEN}`).
- 토큰은 `docker-data/agents/secrets/hermes.env`의 `KESTREL_MCP_TOKEN` (기존 파일은 `.bak-20261005`로 백업).
- `env_file`은 컨테이너 생성 시 주입되므로 재시작이 아니라 재생성 필요: `docker compose up -d --no-deps hermes-app` (dry-run으로 hermes만 바뀌는 것 확인).
- 결과: `MCP server 'kestrel' (HTTP): registered 1 tool(s): mcp__kestrel__get_codex_reset_status`

## 4. 검증
- Hermes 컨테이너에서 MCP 직접 호출: 인증 없음 403, 인증 시 `get_codex_reset_status` 호출 성공.
- 응답 예: 마지막 리셋 2026-10-02 21:18 UTC (10-03 06:18 KST), 마지막 리셋 후 2.5일, 평균 간격 6.8일, 예정 리셋 없음.

## 5. 배운 점 / 주의
- **Hermes 설정은 control plane이 매 시작 시 재생성**: 운영 `hermes/profiles/hybrid-v2/config.yaml`을 직접 고치면 재시작 때 덮어써짐. 원본 `config/hermes/integrations.toml`을 고쳐야 함.
- 메인 체크아웃(`/Volumes/Dove-Nest-SSD/Birds-Nest`)이 detached HEAD라 `integrations.toml` 변경이 미커밋 상태로 남아 있음. 같은 내용이 `dev-mac`(`bae0c6c`)에 커밋돼 있으니 체크아웃을 옮기면 정리됨.
- Cloudflare가 Python 기본 User-Agent(urllib)를 Error 1010으로 차단함. Hermes(httpx)는 통과.
- n8n CLI 반영: `export:workflow` → 수정 → `import:workflow`(비활성화됨) → `publish:workflow` → n8n 재시작.

## 6. 커밋
- `bae0c6c` feat(kestrel): expose Codex reset status as an MCP tool for Hermes → `dev-mac` push, NAS `dev-nas` merge

## 7. 후속 과제
- [ ] Discord에서 Dovie에게 실제 질의해 E2E 확인
- [ ] 필요하면 Claude Code / Codex에도 kestrel MCP 등록
- [ ] 메인 체크아웃을 `dev-mac`으로 정리
