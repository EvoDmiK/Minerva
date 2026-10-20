---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-701 FastAPI → Django + DRF 전환 구현·TEST 배포 — 2026-10-20

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현]] · 분류 근거 {"인프라":0,"자동화":7,"관측성":1,"데이터":4}

## 1. 개요 및 목적

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx RG-701 상세]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록|백로그 등록·담당 배정 기록]]

> [!NOTE] 진행 중 — TEST 배포·검증 완료 · Production 승인 대기
> Root(Codex)가 실제 실행해 전달한 최종 증거와 dev-codex `docs/verification/assets/2026-10-20-rg701/` 산출물(문서 담당 읽기 전용 확인)을 근거로 한다. 문서 담당은 테스트·배포를 재실행하지 않았다. RG-701 항목 전체 완료가 아니다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 요청 배경과 목표
- 역할 분담
- 원인·근거와 설계 결정
- 기준선 (착수 전)
- 배포 전 독립 검토 발견과 조치
- 계약과 변경 전후
- 변경 파일
- 검증 결과 (최종 · `summary.json`)
- 중간 실패·건너뛰기
- TEST 배포와 롤백
- 배포 프로필 메모
- 배포·커밋
- 남은 한계와 후속
- 진행 경과 (UTC)
- Obsidian 재조회

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

> [!NOTE] 진행 중 — TEST 배포·검증 완료 · Production 승인 대기
> Root(Codex)가 실제 실행해 전달한 최종 증거와 dev-codex `docs/verification/assets/2026-10-20-rg701/` 산출물(문서 담당 읽기 전용 확인)을 근거로 한다. 문서 담당은 테스트·배포를 재실행하지 않았다. RG-701 항목 전체 완료가 아니다.

- RG-701 (7xx 배포·인프라), 우선순위 1 (최우선, 변경 없음).
- 상태: 계획 (미착수) → **진행 중 (TEST 배포·검증 완료 · Production 승인 대기)**.
- 착수 근거: 사용자 승인("그렇게 진행해줘").
- 결과: 공개 API 런타임을 네이티브 Django 5.2.18 + DRF 3.16.1로 전환(FastAPI 미import). TEST 이미지 `robingraph-api:test-rg701-django-34f84c494c6a` 배포, healthy·실제 TEST API·공개 브라우저·n8n·DB 불변 검사 통과.
- 남은 범위: Production(별도 승인), commit/push, 롤백 실제 실행, 물리 모바일·재부팅, AMD64 빌드, 네이티브 ingest 실제 DB 쓰기(fake만 검증).

- 2026-10-20 등록·사전 배정 후 사용자가 구현 진행을 승인했다.
- 목표: 기존 공개·내부 API URL과 요청·응답·오류 계약을 유지한 채 Django + DRF로 전환, 조류 근거·데이터·Neo4j 검색 재사용, 프레임워크 독립 서비스 계층. 성능 향상은 약속하지 않는다.
- 승인 범위: 구현·검증·TEST 배포. Production·운영 DB는 별도 승인 전 금지. commit/push 범위 밖.

| 역할 | 에이전트 | 모델 | 워크트리 | 담당 |
|---|---|---|---|---|
| 총괄·통합 (Root) | Codex | 현재 세션 모델(재설정 없음) | dev-codex | `django_api` 설정·ASGI, CLI, 의존성, Docker·Jenkins, 통합·TEST 배포 |
| 구현 | Claude | `claude-opus-5-5` (계획) | dev-claude | 네이티브 DRF View·Serializer·URL·factory, 서비스 추출 |
| UI 호환 | Codex | `gpt-6.1-sol` (계획) | main (dev-agy) | 정적 UI·API 소비 HTTP 호환 |
| 독립 검토 | 검토자 | `gpt-6.1-sol` | — | 새 API·런타임·CLI·인프라 전수 검토 |
| 문서 | Claude | `claude-opus-5-5` | main-2 (dev) | 저장소 기록·Obsidian 단독 쓰기 |

- UI 담당 세션은 모델 업데이트 프롬프트가 건너뛰어져 같은 터미널에서 재시도했다는 전달이 있었다. 실제 실행 모델은 문서 담당 미확인.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현]]
- [[Dev/index|Dev 인덱스]]
