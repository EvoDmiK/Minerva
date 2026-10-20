---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Minerva/2026-10-09-Minerva-지식증류-파이프라인-구축-및-Dev-구조개편]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# Minerva 지식 증류(Distillation) 파이프라인 구축 및 Dev 구조 개편

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Minerva/2026-10-09-Minerva-지식증류-파이프라인-구축-및-Dev-구조개편]] · 분류 근거 {"인프라":2,"자동화":14,"관측성":7,"데이터":10}

## 1. 개요 및 목적

- **작업일**: 2026-10-09
- **목표**: `Work/`에 88% 편중되어 있던 Minerva 볼트 구조를 개선하여, 프로젝트 작업 기록에서 재사용 가능한 핵심 기술 지식을 `Dev/` 상록수 노트로 정제(증류)하고 폴더 위계를 정비한다.

기존 Minerva 볼트는 전체 106개 마크다운 문서 중 `Work/`에 93개(87.7%)가 집중되어 있었다.
* **장점**: 개발·배포 실행력과 세부 근거 보존력은 최상 수준.
* **한계 (병목)**:
  1. **지식의 매몰**: n8n 웹훅 노하우, Tailscale DNS, Neo4j 튜닝, Grafana 쿼리 등 범용 기술이 특정 프로젝트의 날짜별 일지(`2026-10-xx-*.md`) 속에 갇혀 재사용성이 떨어짐.
  2. **시계열 기록 편중**: 영구적 개념/패턴(Evergreen Notes)이 부족하고 시계열적 사건 기록에 편중됨.
  3. **Dev/Learning 공동화**: 초기 아키텍처에 정의된 `Dev/`에 문서가 1개뿐이었음.

## 2. 핵심 아키텍처 및 원칙

- 1. 배경 및 문제 진단
- 2. 수행한 변경 내용
- 2.1 [1단계] Work → Dev 핵심 지식 증류 (Distillation)
- 2.2 [2단계] Work 폴더 내부 위계 정돈 (Core vs Logs)
- 2.3 [3단계] 지식 증류 자동화 스크립트 구축
- 3. 검증 결과
- 4. 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

* `Dev/` 내 상록수 가이드 4편 등록 및 `Dev/index` 정상 렌더링 확인.
* `Work/Birds-Nest/index.md`, `Work/Gullinkambi/index.md`, `Work/index.md`의 모든 위키링크 유효성 검증.
* Python 지식 증류 도구 실행 검증: 77개 작업기록 정상 스캔 및 도메인 태깅 확인.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Minerva/2026-10-09-Minerva-지식증류-파이프라인-구축-및-Dev-구조개편]]
- [[Dev/index|Dev 인덱스]]
