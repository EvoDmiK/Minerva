---
created: 2026-10-21
updated: 2026-10-21
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-21-Jenkins-NAS-WebSocket-배포에이전트]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RG-7xx-NAS-AGENT] SSH 없는 NAS Jenkins WebSocket 배포 에이전트 구성 및 사용자 승인 운영 앱 교체 완료 — 2026-10-21

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-21-Jenkins-NAS-WebSocket-배포에이전트]] · 분류 근거 {"인프라":9,"자동화":7,"관측성":0,"데이터":0}

## 1. 개요 및 목적

> **문서 상태: 완료 — 실제 NAS WebSocket 에이전트 온라인 구성, 사용자 명시 승인에 따른 Production 실제 앱 교체(RobinGraph-PROD #6) 및 배포 후 검증(#2 postcheck, Chromium UI/API) 완료.**  
> 본 문서는 1단계(사전 읽기 검증, 배포 전 이력)와 2단계(사용자 승인 후 실제 운영 앱 교체 및 사후 검증)를 날짜 및 단계별로 명확히 분리하여 기록한다. 문서 담당(Writer)은 dev-codex 산출물(`docs/verification/assets/2026-10-21-nas-agent-production/`, `docs/verification/assets/2026-10-21-jenkins-nas-agent/`, `docs/jenkins-deployment.md`)을 읽기 전용으로 대조하여 기록했다. 문서 담당은 앱, DB, 운영 컨테이너를 직접 조작하지 않았다.

---

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 1단계: SSH 없는 NAS WebSocket 에이전트 구성 및 사전 읽기 검증 (배포 전 이력)
- 1) 발생 배경 및 문제 분석
- 2) 해결 방안 및 아키텍처
- 3) 1단계 검증 결과 (배포 전)
- 2. 2단계: 사용자 명시 승인에 따른 실제 운영 앱 교체 및 사후 검증 (2026-10-21 완료)
- 1) 사용자 승인 및 배포 실행
- 2) M4 사전 검사 및 빌드 결과
- 3) 승인 절차 (Production approval)
- 4) NAS WebSocket 에이전트를 통한 실제 컨테이너 교체
- 5) 배포 후 검증 결과
- 3. 작업 브랜치 형상 관리 현황 (summary.json 기준)
- 4. 한계 및 미검증 사항
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

  ```text
  Deploy verified commit 7267df697fc0912752b9b2a848d42fb8baa80b85,
  image ghcr.io/evodmik/robingraph@sha256:b8d68a53064e893c9f23f182e71c81ab33bd84cba00cf4da209ba3393d3003c3 to NAS Production?
  Deploy to NAS Production or Abort
  ```

## 4. 검증 근거 및 트러블슈팅

> **문서 상태: 완료 — 실제 NAS WebSocket 에이전트 온라인 구성, 사용자 명시 승인에 따른 Production 실제 앱 교체(RobinGraph-PROD #6) 및 배포 후 검증(#2 postcheck, Chromium UI/API) 완료.**  
> 본 문서는 1단계(사전 읽기 검증, 배포 전 이력)와 2단계(사용자 승인 후 실제 운영 앱 교체 및 사후 검증)를 날짜 및 단계별로 명확히 분리하여 기록한다. 문서 담당(Writer)은 dev-codex 산출물(`docs/verification/assets/2026-10-21-nas-agent-production/`, `docs/verification/assets/2026-10-21-jenkins-nas-agent/`, `docs/jenkins-deployment.md`)을 읽기 전용으로 대조하여 기록했다. 문서 담당은 앱, DB, 운영 컨테이너를 직접 조작하지 않았다.

- **배경 및 요구사항**: 기존 Jenkins Production 배포 파이프라인은 M4 Mac 에이전트(`robingraph-mac16`)에서 빌드·검사 후, SSH(`robingraph-nas-ssh`)를 통해 NAS 운영 서버에 접속하여 배포 스크립트를 원격 실행하는 구조였다. SSH 연결의 지연과 키 관리 부담을 줄이기 위해, NAS에서 Jenkins 컨트롤러로 직접 연결하는 **Inbound WebSocket 에이전트(`robingraph-nas-deploy`)**를 구성하고 SSH 없는 로컬 컨테이너 배포 구조로 전환했다.
- **아키텍처 및 1단계(사전 읽기 검증, 배포 전 이력)**:
  - 베이스 이미지 `jenkins/inbound-agent:jdk21`에 Docker 27 CLI, Compose v2.33.0, Python 3를 포함한 경량 에이전트 이미지(`robingraph-nas-agent:20261021`)를 빌드했다.
  - 컨테이너 보안: `read_only: true`, `cap_drop: [ALL]`, `security_opt: [no-new-privileges:true]`, `restart: unless-stopped`, `user: 1000:121`.
  - Docker socket(`/var/run/docker.sock`)과 호스트 Production compose 디렉터리(`/home/kimdove/RobinGraph-approved-ui-e7ad221`, 기존 초안의 `/volume3...` 추정 경로를 실제 호스트 경로로 정정)를 동일한 절대 경로로 마운트했다.
  - 배포 helper(`scripts/deploy_registry_prod.py`)에 `--local` 및 `--check-only` 모드를 추가하고, Jenkins 사전 검증 잡 [RobinGraph-NAS-Agent-Check #1](http://192.168.219.99:8080/job/RobinGraph-NAS-Agent-Check/1/) SUCCESS를 통해 무변경(`mutations: 0`) 읽기 검증을 완료했다.
- **2단계(사용자 명시 승인 후 실제 운영 앱 교체 및 사후 검증 완료)**:
  - 사용자의 "모든 브랜치 commit/push 및 운영 앱 교체" 명시 승인에 따라 [RobinGraph-PROD #6](http://192.168.219.99:8080/job/RobinGraph-PROD/6/) 파이프라인을 실행했다 (소요 시간 175,317ms, 결과 `SUCCESS`).
  - M4 사전 검사: Python 1,031건(993 통과, 38 skip, 0 실패), Node UI 317건 통과, AMD64 fixture 기동 smoke 통과.
  - 승인 절차: Codex가 Jenkins admin API로 승인 제출. 1차 소문자 ID 제출 시 HTTP 404로 무변경 거부된 후, 실제 액션 ID(`ApproveProduction`)로 정정 제출하여 정상 수락됨.
  - 실제 배포: NAS Inbound WebSocket 에이전트 노드(`robingraph-nas-deploy`)가 SSH 없이 로컬 Docker compose를 통해 운영 앱을 교체했다.
    - 배포 revision: `7267df697fc0912752b9b2a848d42fb8baa80b85` (main)
    - 배포 이미지 digest: `ghcr.io/evodmik/robingraph@sha256:b8d68a53064e893c9f23f182e71c81ab33bd84cba00cf4da209ba3393d3003c3`
    - 신규 컨테이너 ID: `3e5cda21d1b8058e9f58811cabd15513f0337e3a7a34182771735cab5836fb8f` (기동 `2026-10-21T07:42:57.518338114Z`, `healthy`)
    - 이전 컨테이너 환경 백업: `/home/kimdove/RobinGraph-approved-ui-e7ad221/.registry-deployments/7267df697fc0912752b9b2a848d42fb8baa80b85-1792568561760212125.env.previous` (0600 격리)
  - 배포 후 검증:
    - Jenkins 읽기 사후 검증 잡 [RobinGraph-NAS-Agent-Check #2](http://192.168.219.99:8080/job/RobinGraph-NAS-Agent-Check/2/) SUCCESS: 내부 health/OpenAPI/lineage GET 200 계약 통과.
    - 공개 Chromium 검증 (1280px / 390px): "천둥오리" 입력 -> "청둥오리" 벡터 후보 선택 -> 답변 렌더링 2/2 통과. Chromium same-origin fetch로 공개 API 3/3 200 통과. (초기 urllib 요청은 Cloudflare edge 403 차단이었으며 브라우저 검사로 공개 동작 입증).
  - DB 및 데이터 상태: DB 쓰기/마이그레이션/백필 없음, 전체 DB 체크섬 비교 미실행. 롤백 미실행, 물리 기기/호스트 재부팅 미검증.

| 구분 | 1단계: 에이전트 구성 및 사전 검증 (과거 이력) | 2단계: 실제 운영 앱 교체 후속 (2026-10-21 완료) |
| --- | --- | --- |
| **원인 / 요구사항** | 배포 파이프라인의 SSH 의존성 제거 및 Inbound 전환 | 사용자 명시 승인에 따른 운영 앱 교체 및 브랜치 푸시 |
| **파이프라인 실행** | `RobinGraph-NAS-Agent-Check #1` (SUCCESS) | `RobinGraph-PROD #6` (SUCCESS, 175,317ms) |
| **배포 실행 주체** | 에이전트 기동 및 `--check-only` (무변경) | NAS `robingraph-nas-deploy` WebSocket 노드 (SSH 완전 배제) |
| **배포 리비전 / 이미지** | 운영 앱 불변 (`a4d2ce52...`, `sha256:336ace79...`) | main `7267df69...` / `sha256:b8d68a53064e893c9f23f182e71c81ab...` |
| **컨테이너 상태** | 기존 컨테이너 healthy 유지 | 신규 `3e5cda21...` (시작 `07:42:57Z`, `healthy`) |
| **승인 절차** | 승인 단계 없음 (사전 검증 잡) | admin API 승인 (1차 404 거부 후 정정 제출로 정상 수락) |
| **자동화 테스트** | 단위 테스트 5/5 통과, Jenkins declarative lint 통과 | Python 1,031건(993 통과, 38 skip, 0 실패), UI 317 통과, AMD64 fixture 통과 |
| **배포 후 검증** | 내부 GET 3/3 계약 검사 통과 | 사후 검증 잡 #2 통과, 공개 Chromium 1280/390 후보 흐름 2/2 및 동일출처 GET 3/3 통과 |
| **DB 및 데이터** | DB 쓰기 없음, 스키마/응답 drift 0 | DB 쓰기/마이그레이션/백필 없음, 전체 DB 체크섬 비교 미실행 |
| **형상 관리** | Git 미커밋 (dev-codex 로컬 변경 상태) | main/dev-codex `7267df6` 푸시 완료, dev(Writer) 본 문서 푸시 진행 |

| 브랜치 | 커밋 해시 | 상태 및 검증 한계 |
| --- | --- | --- |
| **`main`** | `7267df6` | Production 운영 배포 반영 완료 |
| **`dev-codex`** | `7267df6` | 통합 및 배포 검증 완료, origin 푸시 완료 |
| **`dev-claude`** | `e6618a2` | 현황 보존용 브랜치 커밋. 기존 3개 `species_scope_api` 테스트 실패 및 Django 의존성 선언 누락이 있는 상태이며 **Production에 미통합** |
| **`dev-agy`** | `bc89db6` | Node UI 314개 통과; 에이전트 CLI 프로세스 종료로 인해 Codex가 검증 확인 후 커밋/푸시 대행 |
| **`dev` (Writer)** | `499c976` (후속 갱신 중) | 문서 및 검증 자산 동기화 후 dev 브랜치 푸시 |

1. **실제 롤백 미실행**:
   - 배포는 성공적으로 검증되었으며, 이전 env 백업 파일은 보존되었으나 실제 롤백 명령(`--rollback`)은 실행하지 않음 (`rollback: not executed`).
2. **물리 기기 미검증**:
   - Chromium 390px 뷰포트 에뮬레이션을 통한 모바일 검증은 통과했으나, 실제 물리 모바일 기기에서의 브라우징 검증은 미실행 (`physical_mobile: false`).
3. **호스트 물리 재부팅 미실행**:
   - NAS 호스트 물리 재부팅 시 에이전트 컨테이너 자동 재시작(`restart: unless-stopped`) 및 WebSocket 재연결 안정성은 미실행.
4. **전체 DB 체크섬 비교 미실행**:
   - DB 쓰기/마이그레이션 명령이 실행되지 않은 점은 확인했으나, 전체 DB 바이트 단위 체크섬 전수 비교는 이번 배포에서 생략됨.
5. **dev-claude 분기 상태 보존**:
   - `dev-claude`는 단위 테스트 실패(3건)와 Django 선언 누락이 남아 있는 상태의 스냅샷 커밋이며 운영 코드에는 통합되지 않음.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-21-Jenkins-NAS-WebSocket-배포에이전트]]
- [[Dev/index|Dev 인덱스]]
