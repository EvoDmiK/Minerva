---
created: 2026-10-30
updated: 2026-10-30
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-29-승인3항목-운영배포-main병합]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RG-214·RG-407·RG-408] 승인 범위 운영 배포 및 브랜치 병합 — 2026-10-29

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-29-승인3항목-운영배포-main병합]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":1,"데이터":2}

## 1. 개요 및 목적

사용자가 “일단 운영 배포하고, 브랜치 merge 시켜줘”라고 명시 승인했다. 오늘 독립 등록한 먹이 비율 합산 정렬(RG-214), 도감 먹이 표시명(RG-407), 팝업 재열기 배율 복구(RG-408)를 운영 대상으로 분리했다.

root 작업트리에는 앞선 사용자 피드백(RG-603), 조건 유지 후속 질문(RG-213), 안내 UI의 미커밋 변경도 함께 있었다. 독립 후보와 부분 커밋으로 오늘 3개 작업의 source 5개·test 4개만 포함하고, 나머지 변경은 원래 작업트리에 보존한다. 승인 범위 57파일 commit `5056ccb`를 생성하고 dev-codex에 커밋하고 main으로 fast-forward 병합한 뒤 양쪽 push를 완료했다. 후보 전체 검사와 분리 환경 실제 API 검증을 통과했고 Jenkins PROD #13이 시작됐다. Jenkins PROD #13 SUCCESS로 운영 배포를 완료했다. 실제 운영 정렬·라벨·팝업 재열기 검증까지 통과해 RG-214·RG-407·RG-408의 운영 완료 기준을 충족했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 2. 해결 방안 및 설계
- 3. 주요 구현 내용
- 4. 검증 및 테스트 결과
- Jenkins 운영 빌드와 배포 검증
- 실제 운영 HTTP·브라우저
- NAS 영수증·환경 보존
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

root 작업트리에는 앞선 사용자 피드백(RG-603), 조건 유지 후속 질문(RG-213), 안내 UI의 미커밋 변경도 함께 있었다. 독립 후보와 부분 커밋으로 오늘 3개 작업의 source 5개·test 4개만 포함하고, 나머지 변경은 원래 작업트리에 보존한다. 승인 범위 57파일 commit `5056ccb`를 생성하고 dev-codex에 커밋하고 main으로 fast-forward 병합한 뒤 양쪽 push를 완료했다. 후보 전체 검사와 분리 환경 실제 API 검증을 통과했고 Jenkins PROD #13이 시작됐다. Jenkins PROD #13 SUCCESS로 운영 배포를 완료했다. 실제 운영 정렬·라벨·팝업 재열기 검증까지 통과해 RG-214·RG-407·RG-408의 운영 완료 기준을 충족했다.

| 구분 | 승인 / 설계 | 현재 상태 |
| --- | --- | --- |
| 대상 | RG-214·RG-407·RG-408 | 사용자 명시 운영·병합 승인 |
| 분리 | source 5개·test 4개 독립 후보 | 선행 미커밋 작업 보존·운영 제외 |
| 후보 검사 | Python 1,334 실행·1,294 통과·40 skip·0 실패 | UI 323 통과·Django check 정상 |
| Jenkins | 기존 inline·admin 승인 단계 유지 | PROD #13 SUCCESS, 실제 운영 revision·정적 자산 일치 |
| 백로그 | 세 항목의 운영 완료 기준 충족 | RG-214·RG-407·RG-408 completed |

세 항목은 TEST 구현·배포·실제 검증이 완료됐지만 운영 승인 대기 상태였다. 이번 요청은 그 후속 운영 반영과 브랜치 병합 승인이다. TEST 단계 기록을 소급해 운영 완료로 바꾸지 않고 이번 배포 이력을 별도로 남긴다.

- 기존 운영 계열 코드에 오늘 변경만 적용한 isolated candidate를 검사한다.
- 부분 커밋과 병합·push는 root가 수행한다. 미커밋 선행 작업을 버리거나 덮어쓰지 않는다.
- Jenkins PROD의 저장소와 일치하는 inline 정의 및 admin 승인 단계를 유지한다.
- 실제 운영에서 정렬·라벨·재열기 동작을 검증한 뒤 해당 백로그의 운영 완료 기준을 체크한다.

| 구분 | 실제 경로 |
| --- | --- |
| source 5개 | `src/robingraph/api/static/chat.js`, `src/robingraph/retrieval/birdbase.py`, `graph_condition_extractor.py`, `graph_questions.py`, `species_profile.py` |
| test 4개 | `tests/frontend/chat_ui.test.js`, `tests/test_graph_questions.py`, `test_species_profile.py`, `test_taxon_traits.py` |
| 나머지 commit 내용 | 오늘 작업기록·백로그·TEST 증거를 포함해 총 57파일 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-29-승인3항목-운영배포-main병합]]
- [[Dev/index|Dev 인덱스]]
