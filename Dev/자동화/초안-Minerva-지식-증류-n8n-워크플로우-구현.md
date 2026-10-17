---
created: 2026-10-17
updated: 2026-10-17
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/지식연동/2026-10-17-Minerva-지식-증류-n8n-워크플로우-구현]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# [BN-504 / DEV-202] Minerva 지식 증류 n8n 워크플로우 구현

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/지식연동/2026-10-17-Minerva-지식-증류-n8n-워크플로우-구현]] · 분류 근거 {"인프라":1,"자동화":22,"관측성":0,"데이터":0}

## 1. 개요 및 목적

사용자 요청으로 Obsidian MCP의 DEV-202 작업 명세서와 DEV-201 신뢰성 패턴을 읽고 구현에 착수했다. 기준 dev-codex 3dfc2158161c30a2ec6984c5894bd134cf42c398. n8n·백엔드는 dev-claude, Codex는 계약 검토·통합·개발 검증을 담당한다.

GitHub Push/매일03시 AsiaSeoul/수동 실행 → Work/<project>/작업기록/**/*.md 선별 → Obsidian MCP 읽기 → 4개 Dev 카테고리 분류 → 기존 초안 확인 → overwrite:false 생성 → Discord 카드. 실패 알림은 별도 Error Trigger workflow에 연결한다. 실제 MCP는 vault 도구의 action read/create/list이며 목록은 recursive·modified epochms·pagination 구조다. 존재하지 않는 파일은 content 안의 error.message=File not found 및 isError:true로 전달되므로 권한/통신 실패와 구분한다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 1. 요구사항 및 설계
- 2. 구현 및 검증 현황
- 3. 배포 및 형상 관리
- 4. 한계 및 후속 과제
- 관련 문서
- 개발 구현 및 통합 검증 결과
- 운영 전 확인 사항
- 최종 통합 및 검토 결과

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자 요청으로 Obsidian MCP의 DEV-202 작업 명세서와 DEV-201 신뢰성 패턴을 읽고 구현에 착수했다. 기준 dev-codex 3dfc2158161c30a2ec6984c5894bd134cf42c398. n8n·백엔드는 dev-claude, Codex는 계약 검토·통합·개발 검증을 담당한다.

GitHub Push/매일03시 AsiaSeoul/수동 실행 → Work/<project>/작업기록/**/*.md 선별 → Obsidian MCP 읽기 → 4개 Dev 카테고리 분류 → 기존 초안 확인 → overwrite:false 생성 → Discord 카드. 실패 알림은 별도 Error Trigger workflow에 연결한다. 실제 MCP는 vault 도구의 action read/create/list이며 목록은 recursive·modified epochms·pagination 구조다. 존재하지 않는 파일은 content 안의 error.message=File not found 및 isError:true로 전달되므로 권한/통신 실패와 구분한다.

구현 진행 중이며 아직 완료로 기록하지 않는다. 명세의 RobinGraph 원천 문서를 실제 MCP로 읽어 개발 fixture를 준비했다. 격리된 Docker minerva-dev202-stub을 n8n-test_default에 만들었으며 실제 볼트 쓰기/Discord 발송을 대신한다. n8n-test 버전2.15.0 및 standalone MCP Client 지원을 확인했다.

운영 배포·GitHub Webhook 등록·실제 Discord 발송은 아직 수행하지 않았다. 기존 사용자 hermes/config.yaml 변경을 보존한다. 개발 검증과 코드/문서 통합 후 PR을 작성하고 운영 변경은 별도 요청 시 수행한다.

실제 볼트 overwrite:false의 동시 생성 원자성은 아직 미검증이다. 알림 실패 후 재실행 시 이미 생성한 초안의 처리 정책을 구현과 대조해 기록한다. 검증 결과·커밋·PR은 완료 후 덧붙인다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/지식연동/2026-10-17-Minerva-지식-증류-n8n-워크플로우-구현]]
- [[Dev/index|Dev 인덱스]]
