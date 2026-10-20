---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Hermes/2026-10-11-Orca-프로젝트명-오기록-수정]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# Orca 프로젝트명 오기록 수정 및 통합

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Hermes/2026-10-11-Orca-프로젝트명-오기록-수정]] · 분류 근거 {"인프라":0,"자동화":1,"관측성":6,"데이터":1}

## 1. 개요 및 목적

Orca의 새 경로 `…/app-data/orca/kimdove/home/workspaces/<저장소>/<브랜치>`에서 Hermes telemetry가 프로젝트 이름을 `kimdove`로 기록했다. `orca` 이후의 `workspaces`를 찾아 그 다음 경로를 저장소 이름으로 사용하도록 수집기와 Antigravity 변환기를 수정했다.

- 구현: `8575ca2a8781a144153ea8fa8f8de6629c9d0da3` — dev-claude, push 완료.
- dev-codex 코드 통합: `1df4bfb1c1cad9d204a2abdd3c741934166c49ee`.
- ORCA_USAGE_REVISION: 2 → 3, ORCA_THREAD_USAGE_REVISION: 5 → 6.
- revision 변경으로 원본을 재스캔하고 동일 event_id의 project_label을 upsert한다.

## 2. 핵심 아키텍처 및 원칙

- 문제와 수정
- 확인 결과
- 문서와 남은 작업

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- Codex가 통합 후 `docker-compose/agents/hermes-telemetry`에서 `python3 -m unittest discover -s tests -q` 실행: 전체 179개 중 131개 통과, 48개 skip, 실패 0개.
- DB 잔여 `kimdove` 행과 실제 적재 결과: 해소됨 — 사용자 확인(2026-10-11).
- Claude 보고 당시 배포 이미지는 dev-claude 코드로 빌드했으며 compose와 .env는 dev-codex 경로를 사용했다. 컨테이너 revision 3/6 및 LaunchAgent 재시작은 Claude의 직접 확인 보고이다.
- 이 통합 작업에서는 운영 재배포를 수행하지 않았다.
- Codex의 실환경 n8n → DB → Grafana 통합 검증은 미실행이다. 위 사용자 확인과 구분한다.

코드 수정과 검토한 dev-docs 문서를 dev-codex에 반영하고 push했다. [Draft PR #5](https://github.com/EvoDmiK/Birds-Nest/pull/5)를 생성했다. 실환경 독립 E2E 검증이 남아 Draft 상태이며, PR에는 기존 dev-codex 미병합 변경도 포함한다. 문서의 통합 완료·Obsidian 반영 완료 상태도 최종 검토 후 dev-codex에 반영했다. 기존 graphify 변경을 보존하고 `graphify update .`를 실행했으며, 생성 파일은 로컬에 유지한다.

- 48개 skip 조건: 테스트용 DB 컨테이너 미설정 16건, PostgreSQL/MLflow 테스트 환경 및 의존성 필요 32건.
- 운영 재배포와 main 머지는 수행하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Hermes/2026-10-11-Orca-프로젝트명-오기록-수정]]
- [[Dev/index|Dev 인덱스]]
