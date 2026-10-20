---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-NAS-임시파일-volume3-이동]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# NAS 임시 파일 /volume3로 이동

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-NAS-임시파일-volume3-이동]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":0,"데이터":4}

## 1. 개요 및 목적

오늘 배포·이관 작업으로 NAS 홈(`/home/kimdove`, `/volume1`)에 릴리스 묶음과 체크아웃이 쌓였다. 사용자가 이 임시 파일들을 NAS의 `/volume3/` 아래에 적절히 폴더를 만들어 옮겨 달라고 요청했다.
삭제는 요청 범위가 아니어서 **아무것도 지우지 않고 옮기기만** 했다(비어 버린 임시 폴더 2개만 `rmdir`).

- `/volume3` 루트는 root 소유(`drwxr-xr-x`)라 `kimdove`가 폴더를 만들 수 없다(`touch` 시 `Permission denied`).
- `/volume3/RobinGraph`는 앱 저장소의 작업 트리(`.git` 포함, 10월 2일 생성)다. 임시 파일을 섞으면 git 상태가 지저분해져서 대상에서 제외했다.
- `/volume3/Birds-Nest/backups/`는 `kimdove` 소유(`drwx------`)이고 이미 다른 백업이 모여 있다. Birds-Nest 저장소에서 `backups/`는 untracked 폴더다. 여기에 새 폴더를 만들었다.
- 홈 사용량: 릴리스 tarball 51개, 체크아웃 60개, 이전 세션의 배포 백업 13개, 합계 약 549MB. 디스크 여유는 `/volume3` 390G, `/home` 2.2T.
- 실행 중 컨테이너 2개(`robingraph-api`, `robingraph-api-test`)에는 바인드 마운트가 없고 이미지에서 실행된다. compose 작업 디렉터리 라벨은 둘 다 `/home/kimdove/RobinGraph-e90ff85`, 프로젝트 이름은 `robingraph`, `robingraph-test`로 고정이다.
- 저장소 스크립트와 `compose.nas.yml`, `docs/nas-deployment.md`는 `~/RobinGraph-*` 같은 홈 경로를 참조하지 않는다(검색 결과 없음).

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 확인한 사실 (이동 전, 읽기 전용)
- 이동한 것
- 홈에 남긴 것과 이유
- 검증 (실제 실행 결과)
- 발견한 점
- 문서에 반영한 경로 변경
- 남은 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- `/volume3` 루트는 root 소유(`drwxr-xr-x`)라 `kimdove`가 폴더를 만들 수 없다(`touch` 시 `Permission denied`).
- `/volume3/RobinGraph`는 앱 저장소의 작업 트리(`.git` 포함, 10월 2일 생성)다. 임시 파일을 섞으면 git 상태가 지저분해져서 대상에서 제외했다.
- `/volume3/Birds-Nest/backups/`는 `kimdove` 소유(`drwx------`)이고 이미 다른 백업이 모여 있다. Birds-Nest 저장소에서 `backups/`는 untracked 폴더다. 여기에 새 폴더를 만들었다.
- 홈 사용량: 릴리스 tarball 51개, 체크아웃 60개, 이전 세션의 배포 백업 13개, 합계 약 549MB. 디스크 여유는 `/volume3` 390G, `/home` 2.2T.
- 실행 중 컨테이너 2개(`robingraph-api`, `robingraph-api-test`)에는 바인드 마운트가 없고 이미지에서 실행된다. compose 작업 디렉터리 라벨은 둘 다 `/home/kimdove/RobinGraph-e90ff85`, 프로젝트 이름은 `robingraph`, `robingraph-test`로 고정이다.
- 저장소 스크립트와 `compose.nas.yml`, `docs/nas-deployment.md`는 `~/RobinGraph-*` 같은 홈 경로를 참조하지 않는다(검색 결과 없음).

| 하위 폴더 | 내용 | 개수 |
|---|---|---:|
| `releases/` | `~/robingraph-*.tar.gz` 릴리스 묶음(오늘 것과 이전 세션 것 모두) | 51 |
| `checkouts/` | `~/RobinGraph-<태그>` 체크아웃 | 57 |
| `deploy-backups/` | `~/robingraph-deploy-backups/` 안의 이전 배포 백업(2026-10-01) | 13 |
| `neo4j-migration-20261009/` | `prod-pre-migration-20261009.dump`(PROD 이관 전 백업, 92,939,227바이트)와 `test-dump-20261009.dump`(PROD에 로드한 TEST 덤프, 104,719,306바이트) | 2 |

| 남긴 체크아웃 | 이유 |
|---|---|
| `~/RobinGraph-e90ff85` | 실행 중인 PROD·TEST 스택의 compose 작업 디렉터리이고 현재 배포의 `.env.nas.prod`·`.env.nas.test`가 있다 |
| `~/RobinGraph-5fb401e` | PROD를 `robingraph-api:prod-5fb401e`로 롤백할 때 쓰는 `.env.nas.prod` |
| `~/RobinGraph-51cecd1` | TEST를 `robingraph-api:test-framefav-51cecd1`로 롤백할 때 쓰는 `.env.nas.test` |

`mv`는 `/volume1`에서 `/volume3`로(다른 파일시스템) 복사 후 삭제하는 방식이다. 모든 개수가 일치함을 확인했지만 파일별 해시 비교는 하지 않았다.

- 옮긴 체크아웃의 비밀 값이 있는 `.env.nas.*` 파일 62개 중 22개는 이전부터 `-rwxrwxrwx+`(Synology ACL, 모두 읽기 가능)였다. 새 위치는 폴더가 `700`이라 소유자만 접근할 수 있어 노출이 줄었지만, 파일 자체의 권한과 ACL은 바꾸지 않았다. 홈의 남은 3개 체크아웃의 `.env.nas.*`도 확인하지 않았다.
- PROD 이관 전 백업 덤프는 컨테이너 사용자(uid 7474) 소유라 `kimdove`가 `-rw-r--r--` 파일을 읽을 수 있지만 지우려면 폴더 권한에 의존한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-NAS-임시파일-volume3-이동]]
- [[Dev/index|Dev 인덱스]]
