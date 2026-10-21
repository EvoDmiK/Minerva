---
created: 2026-10-21
updated: 2026-10-21
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-21-Jenkins-NAS-WebSocket-배포에이전트]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RG-7xx-NAS-AGENT] SSH 없는 NAS Jenkins WebSocket 배포 에이전트 구성 및 읽기 검증 — 2026-10-21

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-21-Jenkins-NAS-WebSocket-배포에이전트]] · 분류 근거 {"인프라":2,"자동화":9,"관측성":1,"데이터":0}

## 1. 개요 및 목적

> **문서 상태: 완료 — 실제 NAS WebSocket 에이전트 온라인 및 읽기 전용 검증 통과 (Codex 검토 대기).** 사용자 승인에 따라 NAS 인바운드 WebSocket 에이전트(`robingraph-nas-deploy`)를 구성하고 Jenkins를 통한 읽기 검증을 성공적으로 마쳤다. 문서 담당(Writer)은 dev-codex 산출물(`docs/verification/assets/2026-10-21-jenkins-nas-agent/` 및 `docs/jenkins-deployment.md`)을 읽기 전용으로 대조하여 기록했다. 문서 담당은 앱, DB, 서비스, Git 형상을 조작하지 않았다.

---

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 발생 현상 및 한계
- 요구사항 및 설계 검토
- 2. 해결 방안 및 설계
- 1) Inbound WebSocket 에이전트 구조
- 2) 호스트 마운트 및 보안 격리 설계
- 3) 로컬 배포 도우미 (`scripts/deploy_registry_prod.py`) 개선
- 3. 주요 구현 내용
- 수정 및 추가 파일 목록
- 핵심 설정 스니펫
- 4. 검증 및 테스트 결과
- 1) 자동화 테스트 (단위 및 린트)
- 2) NAS 로컬 사전 검증 (`--check-only`)
- 3) Jenkins 실서버 검증 잡 (`RobinGraph-NAS-Agent-Check #1`)
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```yaml
# ci/nas-agent/compose.yml
services:
  agent:
    image: robingraph-nas-agent:20261021
    container_name: robingraph-jenkins-agent
    init: true
    user: ${NAS_AGENT_UID:?Set deployment account uid}:${NAS_DOCKER_GID:?Set Docker socket gid}
    restart: unless-stopped
    network_mode: host
    read_only: true
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
    tmpfs:
      - /tmp
    env_file: agent.env
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./work:/home/jenkins/agent
      - ./helper:/opt/robingraph-deploy:ro
      - ${NAS_DEPLOY_ROOT:?Set the existing Production compose directory}:${NAS_DEPLOY_ROOT}
```

```groovy
// Jenkinsfile (배포 스테이지 변경)
stage('Deploy and verify NAS Production') {
    agent { label 'robingraph-nas-deploy' }
    when { beforeAgent true; expression { !params.CHECK_ONLY } }
    environment {
        DOCKER_CONTEXT = 'default'
        DOCKER_HOST = 'unix:///var/run/docker.sock'
    }
    steps {
        withCredentials([
            usernamePassword(credentialsId: 'robingraph-ghcr', usernameVariable: 'GHCR_USERNAME', passwordVariable: 'GHCR_TOKEN')
        ]) {
            sh '''#!/bin/sh
set -eu
python3 /opt/robingraph-deploy/deploy_registry_prod.py --local   --image "$IMMUTABLE_IMAGE" --revision "$REVISION"
printf '{"revision":"%s","image":"%s","production_verified":true}
'   "$REVISION" "$IMMUTABLE_IMAGE" > production-release.json
'''
        }
        archiveArtifacts artifacts: 'production-release.json'
    }
}
```

## 4. 검증 근거 및 트러블슈팅

> **문서 상태: 완료 — 실제 NAS WebSocket 에이전트 온라인 및 읽기 전용 검증 통과 (Codex 검토 대기).** 사용자 승인에 따라 NAS 인바운드 WebSocket 에이전트(`robingraph-nas-deploy`)를 구성하고 Jenkins를 통한 읽기 검증을 성공적으로 마쳤다. 문서 담당(Writer)은 dev-codex 산출물(`docs/verification/assets/2026-10-21-jenkins-nas-agent/` 및 `docs/jenkins-deployment.md`)을 읽기 전용으로 대조하여 기록했다. 문서 담당은 앱, DB, 서비스, Git 형상을 조작하지 않았다.

- **배경 및 요구사항**: 기존 Jenkins Production 배포 파이프라인은 M4 Mac 에이전트(`robingraph-mac16`)에서 빌드·검사 후, SSH(`robingraph-nas-ssh`)를 통해 NAS 운영 서버에 접속하여 배포 스크립트를 원격 실행하는 구조였다. SSH 연결은 네트워크 지연, 키 관리, 세션 실패 위험이 있어, 사용자 승인 하에 NAS에서 Jenkins 컨트롤러로 직접 연결하는 **Inbound WebSocket 에이전트(`robingraph-nas-deploy`)**를 구성하고 SSH 없는 로컬 컨테이너 배포 구조로 전환을 추진했다.
- **아키텍처 및 구현**:
  - 베이스 이미지 `jenkins/inbound-agent:jdk21`에 Docker 27 CLI, Compose v2.33.0, Python 3를 포함한 경량 에이전트 이미지(`robingraph-nas-agent:20261021`)를 빌드했다.
  - 최초 1회 설치(bootstrap)에는 기존 SSH를 사용했으나, 이후 에이전트는 NAS 내부에서 Jenkins 컨트롤러(`http://127.0.0.1:8080/`)로 WebSocket 인바운드 연결하여 온라인 상태(`robingraph-nas-deploy`, executor 1, exclusive)를 유지한다.
  - 컨테이너 보안: `read_only: true`, `cap_drop: [ALL]`, `security_opt: [no-new-privileges:true]`, `restart: unless-stopped`, `user: 1000:121`(초기 권한 오류를 uid 1000 / docker socket gid 121로 정정).
  - Docker socket(`/var/run/docker.sock`)과 호스트 Production compose 디렉터리를 동일한 절대 경로(`${NAS_DEPLOY_ROOT}`)로 마운트하여 Compose 경로 해석 일관성을 확보했다.
  - 배포 helper(`scripts/deploy_registry_prod.py`)에 `--local` 및 무변경 컨텍스트 확인용 `--check-only` 모드를 추가하고, Jenkins 파이프라인에서 SSH 자격증명 바인딩을 제거하고 GHCR 자격증명만 사용하도록 변경했다.
- **검증 및 최종 상태**:
  - 로컬 단위 테스트 5개 전수 통과(mock), Jenkins declarative lint 통과.
  - Jenkins 검증 잡 [RobinGraph-NAS-Agent-Check #1](http://192.168.219.99:8080/job/RobinGraph-NAS-Agent-Check/1/) SUCCESS: SSH 호출 없이 NAS 에이전트 노드에서 helper `--local --check-only` 및 운영 API(`/health`, `/openapi.json`, `/v1/taxa/lineage?name=청둥오리`) GET 200 정상, 스키마/응답 drift 0건, 계약 검사 통과.
  - 운영 컨테이너(`robingraph-api`, id `a4d2ce5232a9...`, 기동 시각 `2026-10-20T08:55:43Z`, Django digest `sha256:336ace79...`)는 검증 전후 완벽히 동일하며 `healthy` 유지.
  - 운영 앱 교체, DB 쓰기, Production 빌드, commit/push/merge 없음. 실제 SSH 없는 이미지 교체/실패 복구/호스트 재부팅은 미실행(check-only 읽기 검증 완료).

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **원인 규명 / 요구사항** | 배포 시 SSH 의존성 제거 | M4 → NAS 원격 SSH 연결 대신 NAS에서 Jenkins 컨트롤러로 직접 연결하는 WebSocket 에이전트 도입 요구 |
| **설계 및 해결 방안** | Inbound WebSocket 에이전트 | `jenkins/inbound-agent:jdk21` 기반 컨테이너, Docker socket + 동일 절대경로 compose 마운트, helper `--local` 실행 |
| **보안 및 권한 설계** | 최소 권한 및 파일 격리 | root 파일시스템 읽기 전용, cap-drop ALL, no-new-privileges, uid 1000/gid 121, `agent.env` 0600 권한 격리 |
| **코드 / 설정 수정** | helper 및 Jenkinsfile 갱신 | `scripts/deploy_registry_prod.py`(`--local`/`--check-only`), `Jenkinsfile`, `ci/nas-agent/` 신설 |
| **실서비스 배포 현황** | 검증 잡 통과 / 운영 앱 불변 | `RobinGraph-NAS-Agent-Check #1` SUCCESS, 운영 앱 ID/기동시각/이미지 전후 불변 healthy |
| **검증 및 테스트** | 자동화/실서버 검증 | 단위 테스트 5/5 통과, lint 통과, 실제 NAS 에이전트에서 health/openapi/lineage GET 200 통과 |
| **형상 관리** | Git 미커밋 / Inline 적용 | Jenkins Inline 파이프라인은 갱신 적용 완료, Git dev-codex/main은 미커밋 상태 (commit/push 없음) |

1. **`ci/nas-agent/Dockerfile`** (신규)
   - Docker CLI 27 바이너리 및 cli-plugins 복사, Python 3 설치.
2. **`ci/nas-agent/compose.yml`** (신규)
   - Inbound 에이전트 서비스 정의 (`robingraph-jenkins-agent`).
   - `network_mode: host`, `read_only: true`, `cap_drop: [ALL]`, `security_opt: [no-new-privileges:true]`.
   - Docker socket, workspace(`./work`), helper(`./helper:ro`), compose root 동등 마운트.
3. **`scripts/deploy_registry_prod.py`** (수정)
   - `production_context()` 추출 및 검증 로직 재사용.
   - `--local` 및 `--check-only` CLI 플래그 추가.
   - 로컬 실행 시 SSH 없이 GHCR 자격증명만으로 Docker login 및 compose pull/up 실행.
4. **`tests/test_registry_prod_deployment.py`** (수정)
   - `test_local_check_needs_no_credentials_and_does_not_mutate` 단위 테스트 추가.
   - `test_local_deploy_does_not_require_ssh_credentials` 단위 테스트 추가.
5. **`Jenkinsfile` & `ci/Jenkinsfile.production`** (수정)
   - `Deploy and verify NAS Production` 스테이지에 `agent { label 'robingraph-nas-deploy' }` 지정.
   - `when { beforeAgent true; expression { !params.CHECK_ONLY } }` 추가.
   - `withCredentials`에서 `robingraph-nas-ssh` 제거 및 `robingraph-ghcr`만 바인딩.
   - 명령을 `python3 /opt/robingraph-deploy/deploy_registry_prod.py --local`로 변경.
6. **`docs/jenkins-deployment.md`** (수정)
   - 최상단에 `2026-10-21 SSH 없는 NAS 배포 에이전트 전환` 운영 문서 추가.

- **Jenkins 파이프라인**:
  - Inline Pipeline 정의(`RobinGraph-PROD`)에 새 에이전트 라벨(`robingraph-nas-deploy`) 및 `--local` 배포 명령 적용 완료.
  - 검증용 잡 `RobinGraph-NAS-Agent-Check` 구성 및 빌드 #1 통과 완료.
- **Git 저장소 상태**:
  - `Jenkinsfile`, `ci/Jenkinsfile.production`, `scripts/deploy_registry_prod.py`, `tests/test_registry_prod_deployment.py`, `ci/nas-agent/` 변경 사항은 dev-codex 워크트리에 미커밋 상태로 존재.
  - 신규 commit, push, main 병합은 수행하지 않음 (`commit_push_merge: false`).
  - 다음 사용자 승인된 릴리스 커밋 반영 전까지 Jenkins Inline 정의와 Git main 간에 파이프라인 정의 차이가 존재함.
- **자격증명 관리**:
  - `robingraph-nas-ssh` Jenkins 자격증명은 신규 배포에서 참조되지 않으나, 타 용도 확인 전까지 시스템에서 임의 삭제하지 않고 유지함.
  - NAS 에이전트 인증 정보(`agent.env`)는 `0600` 권한으로 NAS 로컬에만 보관.
  - 최초 부트스트랩에 사용된 임시 SSH/로컬 파일은 정리 완료됨.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-21-Jenkins-NAS-WebSocket-배포에이전트]]
- [[Dev/index|Dev 인덱스]]
