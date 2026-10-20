---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Swallow/index]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# Swallow 작업 문서

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Swallow/index]] · 분류 근거 {"인프라":0,"자동화":3,"관측성":4,"데이터":0}

## 1. 개요 및 목적

Swallow의 n8n 워크플로우, 주식·뉴스 DB, 모의투자, MCP 도구와 Grafana 대시보드 작업을 함께 관리한다.

- [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그|Swallow 작업 백로그]] — 검토 항목과 관심종목 정기 수집의 최신 진행 상태·검증 결과.

## 2. 핵심 아키텍처 및 원칙

- 작업 관리
- 기록
- 기록 규칙

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그|Swallow 작업 백로그]] — 검토 항목과 관심종목 정기 수집의 최신 진행 상태·검증 결과.

Swallow 관련 신규 문서는 이 폴더에 `YYYY-MM-DD-Swallow-작업명.md`로 기록하고, SW 작업 ID와 검증 결과를 연결한다. 과거 기록은 당시 상태이며 현재 수정·검증 완료의 근거로 대신 사용하지 않는다.

- [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-뉴스-적재-및-평가-백로그-구현|뉴스 적재 및 평가 백로그 구현]] — SW-001/002/004/005/006/007/009 구현·개발 검증 완료, 운영 승인 대기. 최종 84ff835.

- [[Work/Birds-Nest/작업기록/Swallow/2026-10-13-Swallow-거래량-수집-및-표시-수정|2026-10-13 거래량 수집 및 표시 수정 (SW-013, 개발검증 완료·운영 반영 대기)]]

- 2026-10-13 SW-013 거래량 운영배포 및 검증 완료: [[Work/Birds-Nest/작업기록/Swallow/2026-10-13-Swallow-거래량-수집-및-표시-수정|거래량 수집 및 표시 수정]]. PR7 main4f16b69, 24노드 active, 30393/30398 예약 성공과 실제Grafana누적선그래프확인. 앞의배포대기상태갱신.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Swallow/index]]
- [[Dev/index|Dev 인덱스]]
