---
created: 2026-10-18
updated: 2026-10-18
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-18-Jenkins-GHCR-배포-구성-사전검증]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# Jenkins·GHCR 배포 구성과 사전 검증 — 2026-10-18

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-18-Jenkins-GHCR-배포-구성-사전검증]] · 분류 근거 {"인프라":0,"자동화":5,"관측성":1,"데이터":2}

## 1. 개요 및 목적

사용자가 수동 tar NAS 배포를 Jenkins로 자동화하는 방안을 요청하고 Jenkins 주소·접속 정보를 제공했다. Registry는 GHCR을 선택했다. TEST 자동 배포와 사용자 승인 후 Production 승격을 준비하되 운영 반영은 실행하지 않는 범위다. 인증 값은 기록하지 않는다.

실제 Jenkins2.580.1/Linux amd64/Java21.0.12.1, job0·plugin0·controller executor2였다. admin 인증 성공을 확인했다. 로컬 GitHub 계정은 EvoDmiK이며 repo/workflow 등의 기존 OAuth scope만 있고 write:packages가 없어 GHCR 업로드에 사용할 수 없었다. Git 저장소는 공개이며 default branch main, 현재 작업 브랜치는 dev-codex다. GHCR credential robingraph-ghcr 등록을 사용자에게 요청했고 현재 미등록이다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경·목표
- 초기 확인
- 변경 내용
- 실제 검증·실패 보정
- 초기 credential 대기 시점의 완료 경계
- 초기 대기 단계의 후속·한계
- GHCR 등록 후 최종 TEST 배포 결과
- 첫 실제 실행의 실패와 보정
- TEST#2 실제 성공
- 운영 보존과 재조회
- 최종 증거와 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 수동 tar NAS 배포를 Jenkins로 자동화하는 방안을 요청하고 Jenkins 주소·접속 정보를 제공했다. Registry는 GHCR을 선택했다. TEST 자동 배포와 사용자 승인 후 Production 승격을 준비하되 운영 반영은 실행하지 않는 범위다. 인증 값은 기록하지 않는다.

실제 Jenkins2.580.1/Linux amd64/Java21.0.12.1, job0·plugin0·controller executor2였다. admin 인증 성공을 확인했다. 로컬 GitHub 계정은 EvoDmiK이며 repo/workflow 등의 기존 OAuth scope만 있고 write:packages가 없어 GHCR 업로드에 사용할 수 없었다. Git 저장소는 공개이며 default branch main, 현재 작업 브랜치는 dev-codex다. GHCR credential robingraph-ghcr 등록을 사용자에게 요청했고 현재 미등록이다.

- workflow-aggregator/git/credentials-binding/junit 및 copyartifact와 의존성, 총68개 플러그인 설치. 캐시된 Pipeline option descriptor 갱신을 위해 유휴 Jenkins만 safeRestart하고 정상 복귀·agent 재연결을 확인했다.
- M4 16GB에 Homebrew openjdk@21·uv 설치. robingraph-mac16 inbound WebSocket agent·1executor/exclusive·로그인 LaunchAgent를 구성했다. controller executor는0으로 바꿔 빌드를 실행하지 않게 했다. agent secret은0600 파일, LaunchAgent는 secret 파일 참조만 가진다.
- Jenkinsfile: checkout/tests·임시 registry 인증·ARM64/AMD64 build/publish·AMD64 fixture smoke·digest TEST 배포·검증 receipt. CHECK_ONLY 지원, TEST5분 polling, concurrent build 금지.
- ci/Jenkinsfile.production: 성공한 최신 TEST artifact를 읽고 번호/검증 flag/commit/digest 확인 후 admin input 승인, 이후 NAS pull·앱교체·검증 경로. 자동 트리거 없음.
- scripts/deploy_registry_test.py: digest/revision/기존 TEST target 및 image architecture 확인, private release·atomic current·공개 health 포함 검증, 실패 시 이전 TEST 복구. 관리 호스트에도 설치했다.
- scripts/deploy_registry_prod.py: 승인 후 실행할 SSH/NAS 코드. 실제 prod target·DB 설정 유지·AMD64/revision 확인, image-only compose 교체·API 검증·환경/이미지 rollback, 임시 Registry 인증 정리. 관리 호스트에 설치했지만 운영 실행하지 않았다.
- tests/test_registry_test_deployment.py, tests/test_registry_prod_deployment.py: 임시 파일과 mock subprocess로 private env 유지·mutable/foreign image 거절·target 거절·rollback 복구 검증.
- docs/jenkins-deployment.md: 실제 상태·credential 등록·운영 절차·한계.

job은 RobinGraph-Preflight(실행), RobinGraph-TEST(비활성), RobinGraph-PROD(비활성) 세 개다. 초기 TEST/PROD job은 로컬 Jenkinsfile과 같은 inline source를 저장하고 API로 재조회해 일치함을 확인했다. 앱은 원격 공개 dev-codex에서 checkout한다. 새 CI 파일은 현재 commit/push하지 않았으며 원격에 없으므로 Pipeline from SCM으로 등록했다고 표현하지 않는다. helper host 사본은 source와 함께 관리한다.

1. Jenkins Preflight#1: 원격 commit b7c787e27811e17a41e7a33d9561bde71d109ad2 checkout. Python922개 중884통과·38건너뜀, Node317통과. 이후 임시 DOCKER_CONFIG에 OrbStack context가 없어 Docker 연결 실패, build FAILURE.
2. registry 인증만 임시 분리할 때 context도 import하도록 수정. Preflight#2는 docker context export가 기본 파일로 내보내는 동작을 잘못 사용하여 metadata 없는 stdin import로 실패했다. 앱·DB 변경 없음.
3. export에 `-`를 명시하여 stdout tar stream을 import했다. 실제 임시 Docker config에서 orbstack daemon arm64 연결을 먼저 확인한 뒤 Preflight#3 전체를 재실행했다. **SUCCESS**. Python884통과/38건너뜀(922개), UI317통과/실패0/건너뜀0, Docker arm64 확인. 38개는 외부/통합 조건부 skip이며 전체 실 DB 검사로 표현하지 않는다.
4. TEST helper 최초 단위3개 중2개는 macOS /var→/private/var 경로 비교 fixture 오류로 실패했다. tempfile path를 resolve하여 고친 뒤 Production helper 검사와 함께 **6개 통과**했다. 실제 서비스·DB rollback 검증은 아니다.
5. Jenkinsfile과 Production Pipeline 모두 실제 Jenkins model converter validate 통과. TEST/PROD job disabled 및 저장 source 일치를 readback 확인했다. 새로운 CI helper6개는 로컬에서 실행했으며 원격 체크아웃922개 결과에 합산하지 않는다.
6. 최종 source에는 이전 workspace의 image metadata/test receipt 삭제를 추가해 stale artifact 보존을 막았다. public TEST health 실패도 helper rollback 범위에 포함했고 해당 변경 후6개 단위를 재실행·통과했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-18-Jenkins-GHCR-배포-구성-사전검증]]
- [[Dev/index|Dev 인덱스]]
