---
created: 2026-10-19
updated: 2026-10-19
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-n8n-AviList-매일06시-스케줄-Docker실행기-TEST]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# n8n AviList 파이프라인 매일 06시 스케줄·Docker 실행기 TEST 전환 — 2026-10-19

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-n8n-AviList-매일06시-스케줄-Docker실행기-TEST]] · 분류 근거 {"인프라":0,"자동화":71,"관측성":5,"데이터":1}

## 1. 개요 및 목적

[[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · 선행: [[2026-10-19-AviList-단일자료원-수집파일럿-TEST]] · [[2026-10-19-n8n-AviList-워크플로-TEST실행]]

저장소 기록: `docs/work-log/2026-10-19-n8n-daily-runner.md` (main-2)

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 이전 기록의 한계 중 이번에 해결한 것
- 작업 경계 (이번 범위에 포함하지 않은 것)
- 확인한 원인과 근거
- 변경 전후 동작
- 워크플로 구성
- 실행기 컨테이너 구성 (`compose.avilist-test.yml`)
- 변경 파일 (dev-codex, git 기준 미추적·미커밋)
- 실제 실행 명령
- 검증 방법과 실제 결과
- 단위 테스트 (mock/fixture 중심)
- 실행기 컨테이너 격리 확인 (actual, 16GB M4 Mac)
- 스케줄 활성화 확인 (actual TEST n8n)
- 승인 디렉터리 취소(negative) 확인 (actual)
- 실행기 복구와 워크플로 성공 (actual)
- DB 불변 확인 (actual TEST PG)
- 종합 (`summary.json`)
- graphify
- 보안·자격 증명 처리
- 배포·커밋 정보
- 남은 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
# 관련 단위 테스트 (6개 모듈)
uv run --locked --extra test python -m unittest \
  tests.test_avilist_pipeline tests.test_avilist_pipeline_runner \
  tests.test_avilist_pipeline_service tests.test_n8n_avilist_pipeline \
  tests.test_postgres_ingest tests.test_species_scope -v

# 워크플로 JSON 재생성
uv run --locked python -m scripts.generate_n8n_avilist_pipeline

# 16GB M4 Mac 실행기 컨테이너 기동
docker --context orbstack compose \
  --env-file /Users/kimdove/robingraph-test/pipelines/n8n-avilist-test/compose.env \
  -f compose.avilist-test.yml up -d

# TEST n8n(32GB Mac) 워크플로 실행 — 해당 실행만 Task Broker 포트 분리
ssh -o BatchMode=yes -i <TEST SSH key path> kimdove@192.168.219.98 /usr/local/bin/docker exec \
  -e N8N_RUNNERS_BROKER_PORT=15679 -e N8N_RUNNERS_MODE=internal \
  n8n-test n8n execute --id=rgAvilistTest01 --rawOutput
```

## 4. 검증 근거 및 트러블슈팅

[[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · 선행: [[2026-10-19-AviList-단일자료원-수집파일럿-TEST]] · [[2026-10-19-n8n-AviList-워크플로-TEST실행]]

> 상태: **TEST n8n 매일 06:00 KST 스케줄 활성화, 실행기 Docker 컨테이너 전환·자동 재시작 복구 검증 완료**.
> 첫 실제 06:00 시계 발화 실행은 아직 관측하지 않았다(대신 CLI로 엔진 전체 실행 2회 성공). 물리 호스트 재부팅·OrbStack 전체 재시작은 실행하지 않았다.
> Production 반영·API 앱 이미지 교체·API 앱 재시작·DB 재시작·commit/push는 없다. 백로그 상태(RG-101 보류, RG-406)는 변경하지 않았다.

- [AviList 단일 자료원 TEST 파일럿](2026-10-19-avilist-ingest-pilot.md): 수동 CLI 실행, n8n 연결 범위 밖.
- [n8n AviList 워크플로 TEST 실행](2026-10-19-n8n-avilist-workflow.md): Manual Trigger 전용(`active=false`) 8노드 워크플로,
  실행기는 대화형 tools 세션의 native foreground 프로세스(PID 59159), 자동 시작·재부팅 복구·정기 스케줄 미구성으로 남겼다.

- 목표: (1) 워크플로에 매일 06:00 Asia/Seoul 스케줄 트리거를 추가하고 TEST n8n에서 실제 활성화한다.
  (2) 세션 의존 native 실행기를 재시작 정책이 있는 격리 Docker 컨테이너로 옮긴다.
  (3) 기존 prepare → verify(승인·hash gate) → apply fail-closed 계약과 멱등성(`already_applied`)을 유지한다.
- 역할: Codex(dev-codex, root) 구현·TEST 반영·통합 검증, 독립 검토(승인 파일 단일 bind의 stale inode 지적),
  Writer(main-2) 본 작업 기록·Obsidian 동기화.

| 이전 한계 | 현재 상태 |
|---|---|
| 2. 실행기가 대화형 tools 세션 프로세스(PID 59159)에 의존 | PID 59159가 정확한 대상임을 확인 후 종료. Docker 컨테이너 `robingraph-avilist-runner-test`(restart `unless-stopped`)로 전환 |
| 3. 스케줄 주기 미정, `active=false` | 매일 `0 6 * * *` Asia/Seoul 스케줄 노드 추가, TEST n8n에서 `active=true` readback 및 활성화 로그 확인 |
| 1. 실행기 자동 시작 미구성·재부팅 복구 미검증 | **부분 해결**: 컨테이너 프로세스 강제 종료 후 Docker 정책에 의한 자동 재시작·health 복원 확인. 물리 재부팅·OrbStack 전체 재시작은 미검증 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-n8n-AviList-매일06시-스케줄-Docker실행기-TEST]]
- [[Dev/index|Dev 인덱스]]
