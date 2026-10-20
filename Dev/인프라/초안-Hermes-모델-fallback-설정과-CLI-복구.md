---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Hermes/2026-10-06-Hermes-모델-fallback-설정과-CLI-복구]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# 🪶 Hermes 모델·fallback 설정과 CLI 복구

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Hermes/2026-10-06-Hermes-모델-fallback-설정과-CLI-복구]] · 분류 근거 {"인프라":6,"자동화":1,"관측성":1,"데이터":1}

## 1. 개요 및 목적

> [[2026-10-05-Kestrel-MCP-도구화와-Hermes-연결|Kestrel MCP 연결]]의 후속. hybrid-v2의 주 모델/fallback을 바꾸고, 깨져 있던 로컬 `hermes` CLI를 복구했다. 맥미니 SSH 접속 준비 상태도 점검.

## 2. 핵심 아키텍처 및 원칙

- 1. 모델 / fallback 설정 (hybrid-v2)
- 2. 로컬 hermes CLI 복구
- 3. Claude OAuth 검토 → 보류
- 4. 네트워크 / 맥미니 점검
- 5. 배운 점 / 주의
- 6. 후속 과제
- 6. 커밋 / git 정리
- 7. Hermes 재시작
- 8. 후속 과제

## 3. 재사용 가능한 코드 스니펫 / 설정

```toml
[model]
provider = "openai-codex"
default = "gpt-6.1-sol"

[fallback_model]
provider = "openai-codex"
model = "gpt-6-sol"
```

## 4. 검증 근거 및 트러블슈팅

_작성 필요_

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Hermes/2026-10-06-Hermes-모델-fallback-설정과-CLI-복구]]
- [[Dev/index|Dev 인덱스]]
