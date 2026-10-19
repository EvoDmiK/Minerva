---
created: 2026-10-19
updated: 2026-10-19
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-n8n-AviList-워크플로-TEST실행]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# n8n AviList 검토 파이프라인 워크플로 TEST 실행 — 2026-10-19

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-n8n-AviList-워크플로-TEST실행]] · 분류 근거 {"인프라":0,"자동화":60,"관측성":4,"데이터":0}

## 1. 개요 및 목적

[[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · 선행: [[2026-10-19-AviList-단일자료원-수집파일럿-TEST]]

저장소 기록: `docs/work-log/2026-10-19-n8n-avilist-workflow.md` (main-2)

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 작업 경계 (이번 범위에 포함하지 않은 것)
- 확인한 원인과 근거
- 변경 전후 동작
- 워크플로 구성
- 변경 파일 (root dev-codex 신규 5개, 이 워크트리에는 반영하지 않음)
- 실제 실행 명령
- 검증 방법과 실제 결과
- 단위 테스트 (mock/fixture 중심)
- TEST n8n 실제 실행 (actual)
- DB 불변 확인 (actual TEST PG)
- 실행기와 실패 분리
- 독립 검토와 graphify
- 보안·자격 증명 처리
- 배포·커밋 정보
- 남은 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
# 관련 단위 테스트 (6개 모듈)
python -m unittest -v tests.test_avilist_pipeline tests.test_avilist_pipeline_runner \
  tests.test_avilist_pipeline_service tests.test_n8n_avilist_pipeline \
  tests.test_postgres_ingest tests.test_species_scope

# 워크플로 JSON 생성 결과와 저장 파일 일치 확인
python scripts/generate_n8n_avilist_pipeline.py --check

# TEST n8n(32GB Mac) 워크플로 실행 — 해당 실행만 Task Broker 포트 분리
ssh kimdove@192.168.219.98 /usr/local/bin/docker exec \
  -e N8N_RUNNERS_BROKER_PORT=15679 -e N8N_RUNNERS_MODE=internal \
  n8n-test n8n execute --id=rgAvilistTest01 --rawOutput
```

## 4. 검증 근거 및 트러블슈팅

[[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]] · 선행: [[2026-10-19-AviList-단일자료원-수집파일럿-TEST]]

> 상태: **TEST n8n 수동 워크플로 구현·실제 실행 검증 완료**. 정기 스케줄·실행기 자동 시작·재부팅 복구는 구성/검증하지 않았다.
> Production 반영·앱 이미지 교체·앱 재시작·commit/push는 없다. 백로그 상태(RG-101 보류, RG-406)는 변경하지 않았다.

같은 날 진행한 [AviList 단일 자료원 TEST 파일럿](2026-10-19-avilist-ingest-pilot.md)은 수동 CLI 실행이었고 n8n 연결은 범위 밖이었다.
사용자가 이 파이프라인을 **n8n 워크플로로 만들고 실제 TEST에서 실행**하도록 요청했다.

- 목표: 기존 prepare → verify(승인·hash gate) → apply 단계를 n8n이 순서대로 호출하되, 각 단계 응답 계약을 검사하고
  HTTP 오류나 계약 불일치 시 다음 단계를 실행하지 않는다(fail-closed). 같은 입력의 재실행은 기존 run으로 no-op(`already_applied`)이어야 한다.
- 역할: Claude(dev-claude) 단계 실행 서비스 `scripts/serve_avilist_pipeline.py`와 mock 테스트 26건 구현, Codex(dev-codex, root) 워크플로 생성기·워크플로 JSON·테스트 3건,
  TEST n8n 등록·실제 실행·통합 검증, 별도 Claude(main) 독립 검토, Writer(main-2) 본 작업 기록·Obsidian 동기화.

- 정기 스케줄 실행 없음: canonical workflow는 `active=false`, Manual Trigger 전용이다.
- 실행기(runner) LaunchAgent 자동 시작 미구성, 재부팅 후 복구 미검증.
- n8n DB 직접 쓰기 없음. 기존 API key·project 정보는 원격 read-only 조회만 수행했다.
- 기존 n8n 컨테이너 재시작 없음, 앱 이미지 교체·앱 재시작 없음, Production 실행·배포 없음, commit/push/merge 없음.
- 새 종 분포 추론·도메인 projection(`projection_performed=false`)·이름 벡터 쓰기 없음.
- Writer는 코드·설정 수정, DB 쓰기, 서비스 재시작을 하지 않았고 이 문서 외 저장소 파일을 변경하지 않았다. 워크트리의 기존 dirty 파일은 보존했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-n8n-AviList-워크플로-TEST실행]]
- [[Dev/index|Dev 인덱스]]
