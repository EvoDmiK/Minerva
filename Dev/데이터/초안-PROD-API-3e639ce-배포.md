---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-PROD-API-3e639ce-배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# PROD API 최신 버전 배포 (3e639ce)

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-PROD-API-3e639ce-배포]] · 분류 근거 {"인프라":2,"자동화":0,"관측성":2,"데이터":6}

## 1. 개요 및 목적

같은 날 TEST의 Neo4j·PostgreSQL 데이터를 PROD로 이관했다([[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-09-TEST-PROD-데이터-이관|TEST → PROD 데이터 이관]]).
이어서 PROD API도 최신 버전으로 배포해 달라는 요청을 받았다. PROD 직접 접속은 사용자가 이미 허용했다.

| 항목 | PROD(배포 전) | TEST |
|---|---|---|
| 컨테이너 / 이미지 | `robingraph-api` / `robingraph-api:prod-local` | `robingraph-api-test` / `robingraph-api:test-rg015scroll-3e639ce` |
| 소스 커밋(OCI revision) | `62c07d8` (이미지 생성 2026-10-01) | `3e639ce` |
| 상태 | running, healthy | running, healthy |

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 배포 전 상태와 대상 버전 결정
- 수행 내용
- 검증 결과 (실제 PROD 컨테이너·DB 대상)
- 변경 전후 동작
- 설정 차이와 남은 한계
- 롤백
- 배포·커밋 정보

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
cd ~/RobinGraph-3e639ce   # 옮겨진 뒤 경로: /volume3/Birds-Nest/backups/robingraph-deploy/checkouts/RobinGraph-3e639ce
ROBINGRAPH_DEPLOY_TARGET=prod sh scripts/deploy_nas.sh rollback robingraph-api:prod-local
```

## 4. 검증 근거 및 트러블슈팅

같은 날 TEST의 Neo4j·PostgreSQL 데이터를 PROD로 이관했다([[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-09-TEST-PROD-데이터-이관|TEST → PROD 데이터 이관]]).
이어서 PROD API도 최신 버전으로 배포해 달라는 요청을 받았다. PROD 직접 접속은 사용자가 이미 허용했다.

| 항목 | PROD(배포 전) | TEST |
|---|---|---|
| 컨테이너 / 이미지 | `robingraph-api` / `robingraph-api:prod-local` | `robingraph-api-test` / `robingraph-api:test-rg015scroll-3e639ce` |
| 소스 커밋(OCI revision) | `62c07d8` (이미지 생성 2026-10-01) | `3e639ce` |
| 상태 | running, healthy | running, healthy |

- 대상은 **`3e639ce`**(마지막 코드 변경 `fix: fit desktop cards without scroll and align mobile borders`)다.
  TEST에서 이미 검증한 커밋이다. 이후 dev의 커밋은 문서뿐이고, `main`과 `3e639ce`는 코드 경로
  (`src`, `Dockerfile`, `pyproject.toml`, `uv.lock`, `compose.nas.yml`, `scripts`, `config`, `data`)에 차이가 없다.
- `62c07d8` → `3e639ce`는 40개 파일, +61,864/−475줄(대부분 자료·UI)이다.
- PROD 체크아웃(`~/RobinGraph-rg001-20261002`)은 git 저장소가 아니라 배포 묶음에서 푼 것이다.
  `docs/nas-deployment.md` §9의 `package_nas_release.sh` 절차를 그대로 따랐다.

1. **릴리스 묶음 생성**: `sh scripts/package_nas_release.sh --ref 3e639ce`로 결정적 tar.gz와 manifest를 만들었다.
   아카이브 SHA-256 `6866f47a2f2fac2c8782d8e14cd49e5b8ac4c393fc61f4dfe5cb269a63be5c64`.
2. **전송과 무결성 확인**: `scp`가 이 NAS에서 되지 않아(이관 때와 동일) `ssh … "cat > file" < archive`로 전송했다.
   NAS에서 SHA-256이 manifest의 `archive_sha256`과 일치했고, 내장 `MANIFEST.txt`의 파일별 SHA-256 검증에서
   불일치 0건이었다.
3. **새 체크아웃**: `~/RobinGraph-3e639ce`에 풀고, 현재 PROD 체크아웃의 `.env.nas.prod`를 NAS 안에서 복사했다
   (권한 0600, 비밀 값은 화면과 문서에 출력하지 않음). 새 파일에서만 `ROBINGRAPH_IMAGE=robingraph-api:prod-3e639ce`,
   `ROBINGRAPH_VCS_REF=3e639ce51d9c247a244a2451adcb2a2e9da60a67`로 바꿨다. 기존 체크아웃과 그 env는 건드리지 않았다.
4. **점검**: `ROBINGRAPH_DEPLOY_TARGET=prod sh scripts/deploy_nas.sh preflight`는 "configuration is valid",
   `dry-run`은 이미지 `robingraph-api:prod-3e639ce`, `restart: unless-stopped`, 읽기 전용 루트, `no-new-privileges`,
   외부 네트워크 `proxy_manager`로 컨테이너가 교체됨을 보였다.
5. **배포**: `… deploy_nas.sh deploy` 한 번 실행. 이미지를 빌드해 `robingraph-api:prod-3e639ce`를 만들고
   `robingraph-api` 컨테이너를 recreate한 뒤 healthcheck를 통과했다("RobinGraph API is healthy").
   시작 14:21:41, 종료 14:22:15(약 34초, 빌드 포함).

모의 검증은 없었다. 위 조회는 이관된 PROD Neo4j·PostgreSQL에 대한 실제 요청이다.
프런트엔드·Python 테스트 스위트는 이번에 다시 실행하지 않았다(소스 변경 없이 이미 TEST에서 검증된 커밋을 배포).

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-PROD-API-3e639ce-배포]]
- [[Dev/index|Dev 인덱스]]
