---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-Production-최신앱-f71b37b-배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# Production 앱 배포 — f71b37b

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-Production-최신앱-f71b37b-배포]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":0,"데이터":1}

## 1. 개요 및 목적

2026-10-09 TEST → Production DB 재이관을 완료한 뒤 사용자가 Production 앱도 배포하도록 요청했다. DB에 저장되지 않고 패키지 코드에 포함된 보전 등급 참고평가 인덱스·형질 연결·카드 표시까지 Production에 반영하는 작업이다.

대상은 당시 main `f71b37bee3a55e3c992b0a4727b57accd8db1b0c`이다. 이 배포를 기록하는 후속 문서 커밋과 실제 실행 코드 커밋을 구분한다.

## 2. 핵심 아키텍처 및 원칙

- 요청과 목표
- 배포 전후
- 준비와 수행
- 반영된 동작
- 실제 검증
- 롤백과 한계
- 보존한 증거
- Git·Obsidian 동기화

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

2026-10-09 TEST → Production DB 재이관을 완료한 뒤 사용자가 Production 앱도 배포하도록 요청했다. DB에 저장되지 않고 패키지 코드에 포함된 보전 등급 참고평가 인덱스·형질 연결·카드 표시까지 Production에 반영하는 작업이다.

| 항목 | 이전 | 이후 |
|---|---|---|
| Production 이미지 | robingraph-api:prod-e90ff85 | robingraph-api:prod-f71b37b |
| Production 코드 revision | e90ff85 | f71b37bee3a55e3c992b0a4727b57accd8db1b0c |
| Production 작업 디렉터리 | /home/kimdove/RobinGraph-e90ff85 | /home/kimdove/RobinGraph-prod-f71b37b |
| TEST 이미지 | robingraph-api:test-badge-017a273 | 동일 |
| DB | 직전 TEST → PROD 이관 완료 상태 | 이번 배포에서 추가 복원·변경 없음 |

배포 후 Production·TEST 컨테이너 모두 healthy를 직접 확인했다. Production health의 deployment_target도 prod로 확인했다.

1. 요청 직후 SSH 99번 포트가 연결 거절 상태였다. 사용자에게 SSH 재개를 요청하고 기다리는 동안 main에서 배포 묶음과 검증 도구를 준비했다. 사용자가 열었다고 응답한 뒤 연결을 재확인했다.
2. `scripts/package_nas_release.sh --ref main --output-dir /tmp/rg-prod-f71b37b`로 패키지를 생성했다. 실행 당시 main은 위 전체 revision이다. 실제 비밀 환경파일이 포함되지 않았음을 확인했다.
3. 아카이브 SHA-256은 `6c180f1bbebcac2557d5aa7b4dea9b574e3290fa4c851d83275d8f14b506e2f3`. SSH 표준입력으로 NAS에 전송한 뒤 동일 해시를 검증했다. 포함 파일 125개에 대해 내장 MANIFEST.txt의 개별 해시도 확인했다.
4. 새 디렉터리에 압축을 풀고 기존 Production `.env.nas.prod`만 내부 복사했다. 권한 600을 설정하고 이미지 태그를 prod-f71b37b로 변경했다. TEST DB 주소나 TEST 비밀을 가져오지 않았다. 배포 대상 prod와 VCS revision을 명시했다.
5. 이전 이미지 prod-e90ff85가 NAS에 존재함을 확인했다. preflight가 통과한 뒤 `ROBINGRAPH_DEPLOY_TARGET=prod sh scripts/deploy_nas.sh deploy`로 빌드·컨테이너 교체·health 대기를 수행했다.
6. 배포 스크립트의 verify가 status ok, deployment_target prod를 반환했다. 별도 docker inspect로 실제 이미지·healthy·OCI revision을 재확인했다.

빌드 시작 로그는 2026-10-09 10:07:57 UTC / 19:07:57 KST다. verify 이후 같은 SSH 표준입력 스크립트의 종료 시각 출력이 남지 않아 정확한 종료 초나 사용자 관점 중단 시간을 추정하지 않았다. 별도 요청의 컨테이너 상태·공개 응답 검증으로 완료를 판정했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-Production-최신앱-f71b37b-배포]]
- [[Dev/index|Dev 인덱스]]
