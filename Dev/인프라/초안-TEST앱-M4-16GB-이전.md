---
created: 2026-10-18
updated: 2026-10-18
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-17-TEST앱-M4-16GB-이전]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# TEST 앱을 M4 16GB로 이전 — 2026-10-17

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-17-TEST앱-M4-16GB-이전]] · 분류 근거 {"인프라":15,"자동화":3,"관측성":3,"데이터":4}

## 1. 개요 및 목적

사용자가 TEST 앱을 NAS 대신 M4 16GB Mac mini에 배치하도록 승인했다. TEST PostgreSQL은 NAS, TEST Neo4j·n8n은 32GB Mac에 있다는 사용자 설명을 기준으로 기존 연결을 유지하며 앱·빌드 위치와 TEST 도메인 upstream만 이전했다. DB 복제나 마이그레이션을 하지 않는다.

현재 작업 호스트가 Mac16,10·RAM 17,179,869,184bytes(16GiB), 192.168.219.97임을 sysctl/hostname/ipconfig로 확인했다. Docker context는 OrbStack이다. 기존 로컬 TEST는 test-local 이미지로 2026-10-14부터 실행 중이었다. NAS에는 최신 RG-406 고급 옵션 이동 이미지 test-rg406-8ffeb7734750가 실행 중이었다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 확인한 실제 상태와 변경 전후
- 배포 구현과 파일
- TEST 도메인 전환과 보존
- 실제 실행 검증
- 실패·한계·보안 후속
- 관리와 롤백

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 TEST 앱을 NAS 대신 M4 16GB Mac mini에 배치하도록 승인했다. TEST PostgreSQL은 NAS, TEST Neo4j·n8n은 32GB Mac에 있다는 사용자 설명을 기준으로 기존 연결을 유지하며 앱·빌드 위치와 TEST 도메인 upstream만 이전했다. DB 복제나 마이그레이션을 하지 않는다.

현재 작업 호스트가 Mac16,10·RAM 17,179,869,184bytes(16GiB), 192.168.219.97임을 sysctl/hostname/ipconfig로 확인했다. Docker context는 OrbStack이다. 기존 로컬 TEST는 test-local 이미지로 2026-10-14부터 실행 중이었다. NAS에는 최신 RG-406 고급 옵션 이동 이미지 test-rg406-8ffeb7734750가 실행 중이었다.

| 항목 | 이전 | 이후 |
|---|---|---|
| 공식 TEST 앱 | NAS robingraph-api-test | M4 16GB robingraph-api-test |
| 로컬 이전 TEST | 과거 test-local 이미지 | 최신 snapshot ARM64 빌드로 교체 |
| TEST Neo4j | bolt://192.168.219.98:7687 | 동일 |
| TEST PostgreSQL | NAS192.168.219.99:5433 / robingraph_test | 동일 |
| TEST n8n | 32GB Mac이라는 사용자 확인 | 변경/재시작하지 않음, 이번 작업에서 별도 실측하지 않음 |
| TEST 프록시 host20 | robingraph-api-test:8000(NAS Docker) | 192.168.219.97:8000 |
| NAS TEST 앱 | 실행 | 정지, 컨테이너·이미지 롤백용 보존 |
| Production | NAS 기존 앱 | ID·시작·이미지 및 프록시 설정 동일 |

실제 등록된 도메인은 **https://robingraph-test.dove-nest.com**이다. 과거 대화의 robin-test.dove-nest.com은 이번 확인에서 HTTPS525를 반환했으며 해당 도메인을 새로 등록하거나 인증서를 변경하지 않았다.

NAS 최종 배포와 같은 runtime snapshot `8ffeb7734750752ac20356128be9f0c36dd68954b2528a78c081d6cb85447807`을 사용했다. 패키지141파일 SHA-256을 확인하고 macOS에서 linux/arm64로 빌드했다. 실행 이미지 src/scripts101파일 해시가 manifest와 모두 일치했다. NAS amd64와 Mac arm64는 빌드 이미지 ID가 달라도 동일 앱 소스다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-17-TEST앱-M4-16GB-이전]]
- [[Dev/index|Dev 인덱스]]
