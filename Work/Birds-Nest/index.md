---
created: 2026-10-02
project: Birds-Nest
type: project-index
tags:
  - birds-nest
  - homelab
  - n8n
  - agents
---

# Birds-Nest

Birds-Nest는 개인 AI 에이전트(Hermes/Dovie), 자동화 워크플로우(n8n), 지식 저장소(Obsidian/Neo4j)와 홈랩 서비스를 함께 관리하는 메인 인프라 리포지토리다.

## 작업 기록

- [[Work/Birds-Nest/2026-10-03-Minerva-Git-Sync-웹훅-버그-수정과-NAS-obsidian-mcp-정리|2026-10-03 — Minerva Git Sync 웹훅 버그 수정과 NAS obsidian-mcp 정리]]
- [[Work/Birds-Nest/2026-10-03-Magpie-기반-Minerva-볼트-실시간-Git-Sync-파이프라인-구축|2026-10-03 — Magpie 기반 Minerva 볼트 실시간 Git Sync 파이프라인 구축]]
- [[Work/Birds-Nest/2026-10-03-Codex-사용량-리셋-모니터링-워크플로우-구축|2026-10-03 — OpenAI Codex 사용량 리셋 모니터링 워크플로우 (Kestrel) 구축]]
- [[Work/Birds-Nest/2026-10-02-Jev-AI-기반-carrier-pigeon-개편과-n8n-테스트베드-구축|2026-10-02 — Jev AI 기반 carrier pigeon 워크플로우 개편과 n8n 테스트베드 구축]]

## 주요 구성 요소

- **에이전트 게이트웨이**: Hermes `hybrid-v2` (Dovie), OpenViking, WebUI, telemetry
- **로컬 AI/임베딩**: Apple Silicon MPS 가속 `jina-embeddings-v3` API
- **자동화 & 데이터**: n8n, TimescaleDB, Neo4j, Redis, pgBackWeb
- **테스트베드**: Mac mini 로컬 `n8n-test`, `neo4j-test`

## 관련

- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
