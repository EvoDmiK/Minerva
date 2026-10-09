---
updated: 2026-10-09
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

## 주요 구성 요소

- **에이전트 게이트웨이**: Hermes `hybrid-v2` (Dovie), OpenViking, WebUI, telemetry
- **로컬 AI/임베딩**: Apple Silicon MPS 가속 `jina-embeddings-v3` API
- **자동화 & 데이터**: n8n, TimescaleDB, Neo4j, Redis, pgBackWeb
- **테스트베드**: Mac mini 로컬 `n8n-test`, `neo4j-test`

## 작업 관리

- [[Work/Birds-Nest/Birds-Nest 작업 백로그|Birds-Nest 작업 백로그]] — 상태·우선순위·카테고리별 작업 ID (1xx 인프라, 2xx n8n, 3xx 에이전트, 4xx MCP, 5xx 지식연동, 6xx 관측성)

## 관련 공통 기술 문서 (Dev)

- [[Dev/자동화/n8n-워크플로우-신뢰성-및-에러-복구-패턴|n8n 워크플로우 신뢰성 및 에러 복구 설계 패턴]]
- [[Dev/인프라/2026-10-02-홈랩-인증서·Cloudflare·접속-경로-비교-정리|홈랩 인증서·Cloudflare·접속 경로 비교 정리]]

## 작업 기록 (Work Logs)

- [[Work/Birds-Nest/작업기록/2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포|2026-10-09 — [Stock] Swallow 워크플로우 고도화 (단일 체인 개편 및 NAS n8n 배포)]]
- [[Work/Birds-Nest/작업기록/2026-10-09-Minerva-지식증류-파이프라인-구축-및-Dev-구조개편|2026-10-09 — Minerva 지식증류 파이프라인 구축 및 Dev 구조개편]]
- [[Work/Birds-Nest/작업기록/2026-10-08-Carrier-Pigeon-Gmail-바로가기-404-오류-수정과-NAS-n8n-배포|2026-10-08 — Carrier Pigeon Gmail 바로가기 404 오류 수정과 NAS n8n 배포]]
- [[Work/Birds-Nest/작업기록/2026-10-06-n8n-워크플로우-실패율-검증|2026-10-06 — n8n 워크플로우 실패율 검증]]
- [[Work/Birds-Nest/작업기록/2026-10-06-Hermes-모델-fallback-설정과-CLI-복구|2026-10-06 — Hermes 모델 fallback 설정과 CLI 복구]]
- [[Work/Birds-Nest/작업기록/2026-10-06-Hermes-Discord-설정과-ORCA-SSD-이전-NAS-백업|2026-10-06 — Hermes Discord 설정과 ORCA SSD 이전 NAS 백업]]
- [[Work/Birds-Nest/작업기록/2026-10-05-Kestrel-MCP-도구화와-Hermes-연결|2026-10-05 — Kestrel MCP 도구화와 Hermes 연결]]
- [[Work/Birds-Nest/작업기록/2026-10-03-Minerva-Git-Sync-웹훅-버그-수정과-NAS-obsidian-mcp-정리|2026-10-03 — Minerva Git Sync 웹훅 버그 수정과 NAS obsidian mcp 정리]]
- [[Work/Birds-Nest/작업기록/2026-10-03-Magpie-기반-Minerva-볼트-실시간-Git-Sync-파이프라인-구축|2026-10-03 — Magpie 기반 Minerva 볼트 실시간 Git Sync 파이프라인 구축]]
- [[Work/Birds-Nest/작업기록/2026-10-03-Codex-사용량-리셋-모니터링-워크플로우-구축|2026-10-03 — Codex 사용량 리셋 모니터링 워크플로우 구축]]
- [[Work/Birds-Nest/작업기록/2026-10-02-Jev-AI-기반-carrier-pigeon-개편과-n8n-테스트베드-구축|2026-10-02 — Jev AI 기반 carrier pigeon 개편과 n8n 테스트베드 구축]]

## 인덱스 관리

- 작업 기록은 날짜가 최신인 순서로 `작업기록/` 하위에 보관합니다.
- 상태·검증 결과는 원문 작업 문서를 기준으로 확인하며 인덱스 제목만으로 완료를 판단하지 않습니다.

## 관련

- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
