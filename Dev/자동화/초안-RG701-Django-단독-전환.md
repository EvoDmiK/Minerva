---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-Django-단독-전환]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-701 후속: FastAPI 완전 제거(Django 단독 전환) — 2026-10-20

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-Django-단독-전환]] · 분류 근거 {"인프라":0,"자동화":4,"관측성":0,"데이터":0}

## 1. 개요 및 목적

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx RG-701 상세]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현|1차 전환 구현·TEST 기록]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록|백로그 등록·담당 배정 기록]]

> [!WARNING] 초안 — Root(Codex) 최종 증거 대기
> Root가 코디네이터를 통해 전달한 중간 결과와 문서 담당이 다른 워크트리를 **읽기 전용**으로 확인한 산출물만 근거로 한다. 실제 TEST 배포, 검토 코드 바인딩 갱신, n8n·브라우저·DB 전후 검증은 **아직 증거가 없다(미확인)**. 문서 담당은 테스트·배포를 실행하지 않았다. RG-701은 계속 **진행 중**이며 Production 배포는 없다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 요청 배경과 목표
- 역할 분담 (이번 후속)
- 확인한 원인과 근거
- 1) legacy 비교 기준의 대체 — golden 캡처 (Claude, dev-claude)
- 2) 독립 AviList runner의 Django ASGI 이전 (Root, dev-codex)
- 3) 의존성 제거와 clean venv (Root)
- 4) 독립 검토에서 발견한 회귀와 조치
- 5) 승인 바인딩 가드(코드 fingerprint) 처리 원칙
- 변경 전후 동작
- 변경 파일과 구현 내용
- 검증 방법과 실제 결과 (현재까지)
- 배포·커밋 정보
- 남은 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx RG-701 상세]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현|1차 전환 구현·TEST 기록]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-백로그등록|백로그 등록·담당 배정 기록]]

> [!WARNING] 초안 — Root(Codex) 최종 증거 대기
> Root가 코디네이터를 통해 전달한 중간 결과와 문서 담당이 다른 워크트리를 **읽기 전용**으로 확인한 산출물만 근거로 한다. 실제 TEST 배포, 검토 코드 바인딩 갱신, n8n·브라우저·DB 전후 검증은 **아직 증거가 없다(미확인)**. 문서 담당은 테스트·배포를 실행하지 않았다. RG-701은 계속 **진행 중**이며 Production 배포는 없다.

- 작업 ID: **RG-701** (7xx 배포·인프라). 우선순위 **1 (최우선)** — 변경 없음.
- 상태: **진행 중** 유지. 앞선 단계 "TEST 배포·검증 완료 · Production 승인 대기"는 FastAPI legacy 어댑터를 남긴 이전 이미지(`robingraph-api:test-rg701-django-34f84c494c6a`) 기준이었다. 이번 후속(FastAPI 완전 제거)의 TEST 결과가 나오기 전까지 이번 범위는 **구현·오프라인 검증 단계**다.
- 사용자 요청: 설계 감사 + 테스트 + **Django로의 완전 교체**. 이전 단계에서 남겨 둔 (1) FastAPI 비교용 legacy 어댑터와 (2) 독립 AviList TEST runner(FastAPI)까지 포함한다.
- 요청 문구의 "교체"는 Production 승인이 아니다. Root가 이미 "TEST 이후 별도 명시 승인"을 설명했고, AGENTS.md 운영 배포 승인 규칙을 따른다.
- 이전 기록(1차 전환 구현·백로그 등록)은 **수정하지 않았다**(당시 이력 보존).

- 배경: 1차 전환(같은 날)에서 공개 API 런타임은 네이티브 Django 5.2.18 + DRF 3.16.1로 바뀌었지만, 기존 FastAPI 앱(`api/app.py`)·`ingest_router.py`는 차등 비교 기준으로, 독립 AviList TEST runner는 FastAPI 그대로 남았고 `fastapi` 의존성도 유지됐다. 1차 기록의 "남은 한계"에 이 둘이 후속 결정으로 적혀 있었다.
- 목표:
  1. FastAPI legacy 어댑터 삭제 후에도 기존 계약을 검증할 수 있도록, 삭제 **전에** 실제 FastAPI 응답을 고정 golden으로 캡처하고 비교를 이 golden으로 대체한다(Django 자기 자신과의 비교가 아님).
  2. 독립 AviList runner(`serve_avilist_pipeline`)를 Django ASGI로 이전한다.
  3. `pyproject.toml`·`uv.lock`에서 FastAPI·Starlette 의존성을 제거한다.
  4. TEST에서 실제 배포·검증 후 Production 승인을 요청한다(이번 문서 시점 미실행).
- 범위 밖: Production 배포·운영 컨테이너·운영 DB, commit/push, core·source·bundle 정책 변경(정책은 TEST 전용 유지), Django ORM·데이터 마이그레이션 도입(없음).

| 역할 | 워크트리 | 이번 후속 담당 (Root 전달) |
|---|---|---|
| Root (Codex, 총괄) | dev-codex | 독립 AviList runner의 Django ASGI 이전, 의존성 제거, clean venv 검사, runner mock 테스트 33개, ASGI receive 단계 본문 상한 수정, 이후 TEST 배포·코드 바인딩 갱신·통합 검증 |
| Claude (구현) | dev-claude | `api/app.py`·`ingest_router.py` 삭제, 테스트·import의 네이티브 ASGI 클라이언트 전환, 중복 replay 제거, 삭제 전 golden 캡처 |
| 검토자 `gpt-6.1-sol` | — | 독립 검토(사전 스풀링 본문 상한 회귀 발견) |
| 문서 담당 (Claude) | main-2 (dev) | 저장소 기록, 이 노트, RG-701 백로그 상태 (Obsidian 단독 쓰기) |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-Django-단독-전환]]
- [[Dev/index|Dev 인덱스]]
