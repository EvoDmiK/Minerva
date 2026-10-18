---
created: 2026-10-18
updated: 2026-10-18
project: RobinGraph
type: work-log
category: "7xx 배포·인프라"
tags:
  - robingraph
  - deployment
  - jenkins
  - production
  - ghcr
---

# Jenkins 배포 대상을 NAS Production으로 정정 — 2026-10-18

[[Work/RobinGraph/작업기록/7xx 배포·인프라/작업 백로그|7xx 배포·인프라 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]]

## 요청 배경과 목표

사용자는 Jenkins 도입의 목적이 기존 NAS 운영 배포 자동화임을 명시하고, 배포 대상을 TEST가 아닌 NAS Production으로 정정하도록 지시했다. 직전 구성은 `RobinGraph-TEST`를 자동 빌드·배포 대상으로 설정하고 `RobinGraph-PROD`를 비활성 승격 파이프라인으로 두었으나, 사용자 지시에 따라 기본 파이프라인을 Production 직접 배포로 전면 전환했다. 이번 배포 요청은 이미 TEST 결과를 보고받은 현재 릴리스의 운영 반영 지시로 해석하여 적용했으며, 향후 릴리스에 대한 포괄적 자동 승인으로 확대하지 않고 명시적 admin 승인 gate를 유지한다.

## 원인과 변경 전후

- **변경 전**:
  - 루트 `Jenkinsfile`이 M4 16GB Mac TEST 배포를 포함하고 5분 간격 SCM polling으로 동작.
  - `RobinGraph-PROD`는 `TEST_BUILD` 매개변수 및 최신 성공 TEST artifact를 요구하는 2단계 승격 구조.
  - 운영 배포를 위해 TEST 배포가 필수 선행 조건이었음.
- **변경 후**:
  - 루트 `Jenkinsfile` 및 `ci/Jenkinsfile.production`이 직접 Production CI 파이프라인으로 동작.
  - M4 16GB 에이전트에서 locked Python 전체 검사, Node UI 검사, ARM64/AMD64 멀티 아키텍처 GHCR 게시, AMD64 fixture 검사를 실행한 뒤, commit/digest를 확인하는 admin input 승인을 거쳐 NAS 운영 앱(`robingraph-api`)만 교체.
  - TEST artifact 승격 의존성을 완전히 제거.
  - `RobinGraph-TEST` job은 비활성화(`disabled: true`)하고 SCM polling을 제거. 수동 실행 레시피는 `ci/Jenkinsfile.test`에 보존.
  - TEST 컨테이너 및 TEST DB(PostgreSQL/Neo4j)는 일절 변경하지 않음.
- **운영 호스트 환경 복원 및 네트워크 안정화**:
  - NAS 앱의 compose label이 가리키는 `/home/kimdove/RobinGraph-approved-ui-e7ad221` 디렉터리에 기존 compose/env 파일이 유실되어 있음을 확인.
  - 실행 중이던 운영 컨테이너의 환경변수와 이미지 기본 환경을 대조하여 앱 환경변수 47개 값을 누락 없이 보존한 private `.env.nas.prod`를 권한 `0600`으로 생성·복원.
  - compose 렌더링 결과의 47개 환경값 일치와 `proxy_manager` 네트워크 유지를 확인. 이 준비 과정에서 기존 운영 컨테이너 ID는 유지되었음.
  - M4 Mac의 Tailscale `BackendState=Stopped`로 인해 `http://dove-jenkins/` DNS 해석 실패를 관측했으나, `tailscale up`으로 복구 후 LaunchAgent 관리 에이전트가 WebSocket Connected/online(idle=true) 상태로 정상 복귀함을 확인. 내부 LAN 접속 경로 `http://192.168.219.99:8080/` 병행 가능 확인.
  - 인증 정보(PAT, SSH 비밀키 등)는 문서나 로그에 일절 기록하지 않음.

## 구현 파일 및 설정

- `Jenkinsfile`: 기본 배포 대상을 NAS Production으로 교체. TEST artifact 의존성 제거, admin 승인 인터랙션 및 `production-release.json` 아카이브 추가.
- `ci/Jenkinsfile.production`: 루트 `Jenkinsfile`과 동일한 운영 실행 정의.
- `ci/Jenkinsfile.test`: 기존 TEST 자동 배포 파이프라인을 수동 보관용으로 보존, SCM polling 제거.
- `docs/jenkins-deployment.md`, `docs/deployment-profile.md`: 운영 대상 정정 및 절차 갱신.
- `AGENTS.md`: 운영 대상 정정, TEST 비활성, 미래 명시 승인 유지 규칙 반영.
- 앱 Python/JS/CSS 소스 및 DB 스키마 변경 없음. 기존 production deploy helper(`scripts/deploy_registry_prod.py`)는 로컬 원본과 관리 호스트(`/Users/kimdove/robingraph-test/deploy_registry_prod.py`)의 해시 일치를 확인.

## 실행과 검증 과정

1. **Jenkins 파이프라인 문법 및 모델 검증**: Jenkins Pipeline model converter를 통해 실제 서버에서 문법 통과 확인.
2. **Inline Pipeline 등록 및 재조회**: 로컬 `Jenkinsfile`과 Jenkins 서버에 등록된 Production Inline Pipeline script를 API로 재조회하여 내용 일치 확인.
3. **Helper 단위 검사**: `uv run --locked --extra test python -m unittest tests.test_registry_prod_deployment tests.test_registry_test_deployment` 실행 결과 6개 테스트 통과. (subprocess mock 및 임시 파일 검증이며 실제 운영 rollback 검증이 아님을 명시).
4. **Production #1 시도**: 오래된 agent 채널에서 checkout이 진행되지 않아 사용자 개입으로 중단. 운영 앱 변경 전에 안전하게 중단됨.
5. **Production #2 실제 실행 및 성공**:
   - 원격 dev-codex commit `bc643ee9edef0fc58c605adde70b4808b7622ac5` 체크아웃.
   - Node UI 단위 검사 317개 모두 통과 (실패 0, 건너뜀 0).
   - locked Python 928개 실행: 890개 통과, 38개 조건부 skip (통합/외부 의존성 건너뜀으로 실제 DB 성공으로 간주하지 않음).
   - M4 agent에서 ARM64 및 AMD64 멀티 아키텍처 빌드 후 GHCR 게시 완료.
   - M4 agent에서 AMD64 network-none fixture 시작 검사(health/openapi) 통과 (실제 운영 DB 검증과 구분).
   - 생성된 manifest digest: `sha256:100e4aa30fd8981ebb631ced8c4bfecd95e71fcdb6d90cc5026e42f11b333ead`.
   - **Admin Input 승인**: 현재 사용자의 명시적 운영 배포 요청에 따라 해당 commit 및 digest 확인 후 admin 승인 처리.
   - NAS 운영 컨테이너(`robingraph-api`) 교체: private env 백업 후 immutable digest 및 OCI revision(`bc643ee9edef0fc58c605adde70b4808b7622ac5`), amd64 아키텍처 검증 후 교체 완료.
   - 최종 job 결과: **SUCCESS** (`http://dove-jenkins/job/RobinGraph-PROD/2/`, LAN `http://192.168.219.99:8080/job/RobinGraph-PROD/2/`).

## 최종 실제 결과

- **운영 런타임 상태**:
  - NAS `robingraph-api` 컨테이너 교체 완료.
  - Image: `ghcr.io/evodmik/robingraph@sha256:100e4aa30fd8981ebb631ced8c4bfecd95e71fcdb6d90cc5026e42f11b333ead`
  - VCS Ref: `bc643ee9edef0fc58c605adde70b4808b7622ac5`
  - Architecture: `amd64`, Target: `prod`, Health: `healthy`.
  - 이전 운영 이미지: `robingraph-api:prod-approved-ui-0681747` (private env 백업 보존).
  - Neo4j(`bolt://neo4j:7687`), PostgreSQL(`robingraph`) 운영 DB 연결 유지 확인.
- **내부 및 공개 운영 API 검증**:
  - NAS 내부 HTTP GET: `/health` 200, `/openapi.json` 200, `/birds/mallard/lineage` 200 통과. contract parity 및 canary 통과.
  - 공개 운영 도메인 `https://robingraph.dove-nest.com`: 동일 GET 검증 수행하여 `passed=true` 확인.
- **공개 Chromium 브라우저 UI 검증 (1280px / 390px / 320px)**:
  - 실제 공개 운영 웹 자산 접속 검증 통과.
  - 고급 조회 옵션 접힘/펼침, outside 선택, 질문 작성 입력 유지, 가로 넘침(horizontal overflow) 없음, console/page error 0건 확인.
  - POST 요청은 전면 차단하여 검증(Cloudflare `/cdn-cgi/rum` 텔레메트리 필터링 정정 후 검증 통과).
  - 본 검사는 UI 렌더링 및 읽기 검사이며, 운영 환경에서의 답변 생성이나 그래프 쓰기 검증이 아님을 명시.
- **TEST 환경 보존**:
  - M4 16GB Mac의 TEST 컨테이너(`5796debae46cafe293f62288a0e4c0a16cc5880d32ef6dafcab614f828c3d133`) 배포 전후 ID·image·StartedAt 완전 일치 확인.
  - `RobinGraph-TEST` job: `disabled: true`.
- **에이전트 연결 상태**:
  - Tailscale 연결 복구 후 LaunchAgent를 통한 inbound WebSocket agent Connected 및 idle=true 확인.
- **검증 증거 자산**:
  - `docs/verification/assets/2026-10-18-jenkins-production/`: `production-2.json`, `production-2.txt`, `production-release.json`, `image-metadata.json`, `public-api.json`, `production-before.json`, `production-after.json`, `test-unchanged.json`, `pipeline-readback.json`, `approval.json`, `browser-readonly.json`, 스크린샷 3종 (`production-1280.png`, `production-390.png`, `production-320.png`).

## 한계 및 후속 확인 사항

1. **미래 운영 배포 승인 gate 유지**: 이번 배포는 사용자의 명시적 운영 반영 지시에 따라 승인되었으며, 향후 dev-codex 변경에 따른 운영 배포는 Jenkins admin input 단계에서의 명시적 승인을 거쳐야만 실행된다.
2. **실제 런타임 Rollback 미유발**: 배포 롤백 로직은 단위 검사(mock subprocess)로 검증되었으며, 실제 운영 런타임에서의 롤백은 의도적으로 유발하지 않았다.
3. **DB 검증 범위**: 운영 DB 마이그레이션이나 대량 데이터 쓰기는 수행하지 않았으며, DB 내용 전수 비교는 실행하지 않았다.
4. **미검증 환경**: 물리 머신 재부팅 후 부팅 시점 자동 복구, Safari/Firefox 및 물리 모바일 기기에서의 브라우저 검증은 수행하지 않았다.
5. **Git 형상 상태**: 이번 파이프라인 정정은 로컬 파일 수정 및 Jenkins inline script 등록으로 반영되었으며, 신규 commit/push는 수행하지 않았다.
