---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-main-Production-Django-배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-701 main 통합·Production 배포 (Django 단독 런타임) — 2026-10-20

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-main-Production-Django-배포]] · 분류 근거 {"인프라":5,"자동화":13,"관측성":0,"데이터":7}

## 1. 개요 및 목적

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx RG-701 상세]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-Django-단독-전환|Django 단독 전환 TEST 기록]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현|1차 전환 구현·TEST 기록]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-18-Jenkins-Production-배포-대상-정정|Jenkins Production 배포 체계]]

> [!SUCCESS] RG-701 완료 — main 병합·Production 배포·실제 검증 (Jenkins `RobinGraph-PROD` #3 SUCCESS)
> Root(Codex)가 Git·Jenkins·앱 배포를 실행했고, 문서 담당은 dev-codex `docs/verification/assets/2026-10-20-production-django/` 산출물과 Git ref를 **읽기 전용**으로 확인했다. 문서 담당은 commit/push/merge/배포·앱/설정 수정을 하지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 요청 배경과 목표
- 역할 분담
- 과거 TEST 증거 (이력 — 이번에 재실행하지 않음)
- 현재 preflight (2026-10-20 17:50–17:52 KST)
- Jenkins 빌드와 승인 gate (실제)
- Production 배포 결과 (실제)
- 운영 DB 관련 사용자 결정 (이번 배포 중)
- 변경 전후 동작 (Production)
- 변경 파일과 구현 내용
- 검증 방법과 실제 결과 (구분)
- 롤백 기준
- 배포·커밋 정보
- 남은 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

[[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그#RG-701 — FastAPI에서 Django + Django REST Framework로 백엔드 전환|7xx RG-701 상세]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-Django-단독-전환|Django 단독 전환 TEST 기록]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-FastAPI-Django-DRF-전환-구현|1차 전환 구현·TEST 기록]] · [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-18-Jenkins-Production-배포-대상-정정|Jenkins Production 배포 체계]]

> [!SUCCESS] RG-701 완료 — main 병합·Production 배포·실제 검증 (Jenkins `RobinGraph-PROD` #3 SUCCESS)
> Root(Codex)가 Git·Jenkins·앱 배포를 실행했고, 문서 담당은 dev-codex `docs/verification/assets/2026-10-20-production-django/` 산출물과 Git ref를 **읽기 전용**으로 확인했다. 문서 담당은 commit/push/merge/배포·앱/설정 수정을 하지 않았다.

- 작업 ID: **RG-701** (7xx 배포·인프라), 우선순위 1 (변경 없음).
- 사용자 지시: TEST 결과 확인 후 **git push, main 병합, Production 배포를 명시 승인**(코디네이터 전달). AGENTS.md 운영 배포 승인 규칙의 "명시 승인"에 해당한다.
- 결과:
  - Git: 커밋 `e3a8bda`(네이티브 Django 전환, 269 files) + `770495a`(과거 배포 로그 5개 줄 끝 공백 정리). main을 `770495a13fe7c7431c2d66cbf41a1080272d42f0`으로 **fast-forward**, dev-codex·main push 성공.
  - Jenkins: `RobinGraph-PROD` checkout을 `dev-codex` → `main`으로 바꾼 뒤 build **#3 SUCCESS**(203,615ms). 빌드 안에서 Python 1,029 실행·991 통과·38 건너뜀, Node 317 통과, ARM64+AMD64 이미지 게시, AMD64 fixture 기동 smoke 통과.
  - Production: NAS `robingraph-api`가 이미지 `ghcr.io/evodmik/robingraph@sha256:336ace7938471bdcdf2be1bfac904a33aa1cfd20987ed945c4ed5a74632f005d`, revision `770495a…2f0`로 교체됨. healthy, 네이티브 Django ASGI, FastAPI·Starlette 없음. 내부 API health·OpenAPI·lineage 200, drift 없음. 공개 URL Chromium 6/6 통과.
  - 운영 DB: 앱만 교체했다. 감시 범위(ingest 상태 해시·Taxon 33,694·이름 벡터 0/카탈로그 비어 있음)가 전후 바이트 동일하다. **DB 전체 체크섬이 아니다.** TEST DB 복사·backfill·마이그레이션·운영 n8n 변경 없음.
- TEST 검증(clean 1,029/991/38, Node 317 등)은 이전 기록의 **과거 증거**로 따로 정리했다. 현재 preflight와 Jenkins·Production 실제 증거와 섞지 않는다.

- 배경: RG-701 후속(FastAPI 완전 제거·Django 단독 전환)은 TEST에서 실제 API·브라우저·runner·n8n·DB 불변 검증을 마쳤고 Production 승인 대기였다([[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-Django-단독-전환|Django 단독 전환 기록]]).
- 목표:
  1. dev-codex의 검증된 작업을 커밋해 main에 병합·push한다.
  2. Jenkins Production 파이프라인의 checkout 대상을 `dev-codex`에서 `main`으로 바꾼다.
  3. 기존 admin 승인 gate를 거쳐 NAS Production 앱을 교체하고 실제로 검증한다.
- 범위 밖: 운영 DB 스키마·데이터 변경(이번 전환에는 Django ORM 마이그레이션이 없다), TEST DB 복사, 운영 n8n 워크플로 변경, 문서 담당의 Git·Jenkins·앱 조작.

| 역할 | 워크트리 | 이번 담당 |
|---|---|---|
| Root (Codex, 총괄) | dev-codex | 커밋, main 병합·push, Jenkins 설정 전환·빌드, 승인 gate 제출, Production 교체·검증, 증거 산출 |
| 문서 담당 (Claude) | main-2 (dev) | 저장소 기록, 이 노트, RG-701 백로그(Obsidian 단독 쓰기). Git·배포·앱/설정 수정 없음 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-20-RG701-main-Production-Django-배포]]
- [[Dev/index|Dev 인덱스]]
