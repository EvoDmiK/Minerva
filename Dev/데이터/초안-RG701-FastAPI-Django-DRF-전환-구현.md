---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-701 FastAPI → Django + DRF 전환 구현 — 2026-10-20

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현]] · 분류 근거 {"인프라":0,"자동화":2,"관측성":0,"데이터":4}

## 1. 개요 및 목적

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx RG-701 상세]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록|백로그 등록·담당 배정 기록]]

> [!WARNING] 진행 중 · 증거 대기
> 구현 착수 시점의 근거와 계획을 기록한다. 구현 완료·전환 후 테스트 통과·TEST 배포·롤백 확인은 **아직 증거가 전달되지 않았고 확인되지 않았다.** Root(Codex)의 최종 실제 증거를 받은 뒤 갱신한다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 요청 배경과 목표
- 역할 분담
- 확인한 근거
- 착수 전 기준선 (Root 실행 · 변경 전)
- 진행 중 관찰 (dev-codex 작업 트리 · 읽기 전용 · 미커밋)
- 계약과 변경 전후
- 변경 파일
- 검증 결과
- 배포·커밋
- 남은 한계와 후속
- Obsidian 재조회

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

> [!WARNING] 진행 중 · 증거 대기
> 구현 착수 시점의 근거와 계획을 기록한다. 구현 완료·전환 후 테스트 통과·TEST 배포·롤백 확인은 **아직 증거가 전달되지 않았고 확인되지 않았다.** Root(Codex)의 최종 실제 증거를 받은 뒤 갱신한다.

- 작업 ID: RG-701 (7xx 배포·인프라), 우선순위 1 (최우선, 변경 없음)
- 상태: 계획 (미착수) → **진행 중** (2026-10-20 구현 착수). 완료 아님.
- 착수 근거: 사용자가 Orca 코디네이터를 통해 구현 진행을 승인("그렇게 진행해줘").
- 승인 범위: 구현·검증·TEST 배포까지. Production·운영 컨테이너·운영 DB 변경은 별도 명시 승인 전 수행하지 않는다. commit/push는 이번 지시 범위 밖.

- 2026-10-20 RG-701을 최우선·계획 상태로 등록하고 담당을 사전 배정한 뒤, 사용자가 구현 진행을 승인했다.
- 목표(백로그 정의 유지): 기존 공개·내부 API URL과 요청·응답·오류 계약을 유지한 채 웹 계층을 Django + DRF로 전환한다. 조류 근거·데이터와 Neo4j 검색을 재사용하고 프레임워크 독립 서비스 계층을 만든다. 성능 향상은 약속하지 않는다.

| 역할 | 에이전트 | 모델 | 워크트리 | 담당 |
|---|---|---|---|---|
| 총괄·통합 (Root) | Codex | 현재 세션 모델 그대로(재설정 없음) | dev-codex | `django_api/settings.py`·`asgi.py`, CLI, 의존성, 인프라, 통합 검증·TEST 배포 |
| 구현 | Claude | `claude-opus-5-5` (계획) | dev-claude | 네이티브 DRF View·Serializer·URL, 서비스 추출 |
| UI 호환 | Codex | `gpt-6.1-sol` (계획) | main (dev-agy) | 정적 UI·API 소비 HTTP 호환 검사 |
| 문서 | Claude | `claude-opus-5-5` | main-2 (dev) | 저장소 기록·Obsidian 단독 쓰기·백로그 |

- UI 담당 세션은 모델 업데이트 프롬프트가 건너뛰어져 같은 터미널에서 재시도 중이라는 코디네이터 전달이 있었다. 실제 실행 모델은 문서 담당이 확인하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현]]
- [[Dev/index|Dev 인덱스]]
