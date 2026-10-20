---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Kestrel/2026-10-05-Kestrel-MCP-도구화와-Hermes-연결]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# 🦅 Kestrel MCP 도구화와 Hermes 연결

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Kestrel/2026-10-05-Kestrel-MCP-도구화와-Hermes-연결]] · 분류 근거 {"인프라":1,"자동화":10,"관측성":4,"데이터":0}

## 1. 개요 및 목적

> [[2026-10-03-Codex-사용량-리셋-모니터링-워크플로우-구축|Kestrel 구축]]의 후속 작업. 알림만 보내던 Kestrel을 에이전트가 질문할 수 있는 MCP 도구로 확장.

## 2. 핵심 아키텍처 및 원칙

- 1. 목표
- 2. 구성
- 3. Hermes 연결 (hybrid-v2 / Dovie)
- 4. 검증
- 5. 배운 점 / 주의
- 6. 커밋
- 7. 후속 과제

## 3. 재사용 가능한 코드 스니펫 / 설정

```
기존: Schedule(5분) → Fetch Reset Status → Detect New Events → Discord Alert
추가: Kestrel MCP (MCP Server Trigger, /mcp/kestrel, Bearer 인증)
       └─ get_codex_reset_status (HTTP Request Tool → https://codex-resets.com/api/v1/status)
```

## 4. 검증 근거 및 트러블슈팅

_작성 필요_

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Kestrel/2026-10-05-Kestrel-MCP-도구화와-Hermes-연결]]
- [[Dev/index|Dev 인덱스]]
