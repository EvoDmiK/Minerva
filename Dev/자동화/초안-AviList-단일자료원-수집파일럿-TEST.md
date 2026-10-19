---
created: 2026-10-19
updated: 2026-10-19
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-AviList-단일자료원-수집파일럿-TEST]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# AviList 단일 자료원 반복 수집 파이프라인 TEST 파일럿 — 2026-10-19

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-AviList-단일자료원-수집파일럿-TEST]] · 분류 근거 {"인프라":0,"자동화":11,"관측성":0,"데이터":7}

## 1. 개요 및 목적

[[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]]

저장소 기록: `docs/work-log/2026-10-19-avilist-ingest-pilot.md` (main-2)

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 작업 경계 (이번 범위에 포함하지 않는 것)
- 자료원과 라이선스
- 확인한 근거
- 변경 전후 동작
- 변경 파일
- 검증 방법과 실제 결과
- 배포·커밋 정보
- 남은 한계와 후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

> 상태: **초안 (검증 진행 중)**. 아래 "미확인"으로 표시한 항목은 Codex/Claude의 최종 증거를 받은 뒤
> 갱신한다. 이 문서는 현재 시점의 구현 범위와 확인된 사실만 기록하며, 완료·배포·커밋을 주장하지 않는다.

- 목표: 공식 자료원 1개(AviList Explorer v2025b JSON)를 고정 SHA-256으로 받아, 결정적(deterministic)
  prepare → 운영자 review → hash gate를 거친 뒤 TEST PostgreSQL에 별도 pilot dataset/source_record/
  pointer만 저장하는 흐름을 확인한다. 같은 입력을 다시 실행하면 새 run 없이 no-op이 되어야 한다.
- 역할: Codex(dev-codex)가 root CLI·통합, Claude(dev-claude)가 코어 모듈·단위 테스트, main 워크트리의
  Codex가 독립 리뷰, Writer(main-2)가 본 작업 기록을 맡는다.
- Airflow 미도입 판단은 사용자 지시에 따른 것이며, 이 문서에서 Airflow와의 비교 평가를 수행하지 않았다.

- **공식 JSON 실제 다운로드 (Codex 전달, 실제 네트워크)**: 19,933,159 byte, 33,684행 / species 11,131,
  SHA-256이 기존 pin과 일치. Writer가 직접 재다운로드하지는 않았다.
- **코드 정독 (Writer, 읽기만)**: `dev-codex/scripts/run_avilist_pipeline.py`(241줄, 미추적 신규 파일),
  `dev-codex/tests/test_avilist_pipeline_runner.py`(미추적 신규 파일), 기존 추적 파일
  `scripts/build_species_distribution.py`, `src/robingraph/ingest/store.py`의 `begin_run`·`append_batch`·
  `activate_release`·`pipeline_state_version`·`active_release_context`·`fail_run` 존재 확인.
- runner가 import하는 코어 모듈 `robingraph.ingest.avilist_pipeline`(`prepare_manifest`, `validate_approval`)은
  2026-10-19 Writer 확인 시점에 dev-codex·dev-claude 어느 워크트리에도 파일이 없었다. Claude 담당 코어로
  진행 중인 것으로 보이며, **코어 구현·단위 테스트 결과는 미확인**이다.

- 변경 전: AviList 자료는 n8n 기준정보 workflow(`docs/n8n/reference-ingest.md`)와 수동 builder로
  `species_distribution.json`을 생성했다. 자료원 단위로 review 승인·hash gate·PG pilot pointer를 묶는
  재실행 가능한 CLI 경로는 없었다.
- 변경 후(구현 중, 코드 기준 설명):
  1. `prepare [--source PATH] --output DIR`: `--source`가 없으면 공식 URL을 받으며, 다른 URL로 redirect되면
     거부, 25,000,000 byte 상한. builder로 bundle을 다시 만들고(내부에서 AviList·KOS SHA 불일치 시 실패)
     manifest를 생성한다. 출력 폴더가 이미 있으면 덮어쓰지 않고 실패한다. 결과는 `review_required`.
  2. `apply --package DIR --approval FILE`: 패키지의 source로 bundle·manifest를 재계산해 바이트 단위로
     같은지 확인(hash gate)하고 approval을 검증한다. 이어서 읽기 전용 runtime 검사를 수행한다.
     `--apply`가 없으면 `dry_run`으로 끝나고 쓰기 lock에 들어가지 않는다.
  3. 읽기 전용 runtime 검사: TEST PG/Neo4j(`bolt://192.168.219.98:7687`) allowlist, 설치된
     `species_distribution.json`과 bundle 동일성, `/health`의 `deployment_target=test`, 활성 분류판이 pin과
     같은지, 이름 벡터 인덱스 `dry_run=True` 결과가 최신·호환인지, 고정 검색 회귀 4건
     (Kea outside/all answer, Kee outside clarify, 청둥오리 korea answer), 검사 전후 활성 분류판 불변.
     이름 인덱스에 갱신이 필요하면 쓰기 없이 실패한다.
  4. `--apply` 시: `ROBINGRAPH_DEPLOY_TARGET=test`와 PG 대상 allowlist(host/port/database/user/schema)를
     연결 전에 확인하고, 연결 후 `current_database()/current_user`를 다시 확인한다. advisory lock으로 동시
     실행을 막는다. 같은 manifest의 release가 이미 활성이면 provenance(content/manifest SHA)를 대조한 뒤
     `already_applied` no-op. 아니면 pilot dataset `rg:dataset:avilist-distribution-pilot` 아래 release·run을
     만들고 bundle 전체를 source_record 1건으로 append한 뒤 state version CAS로 pilot pointer를 활성화한다.
     cursor에 `projection_performed: false`를 기록한다. append/activate 실패 시 run을 실패 처리하고 활성화하지
     않으며, 재시도 시 record ID는 manifest 해시 기반이라 같고 run ID만 새로 생성된다.

| 워크트리 | 파일 | 담당 | 상태 |
|---|---|---|---|
| dev-codex | `scripts/run_avilist_pipeline.py` | Codex (root CLI·통합) | 미추적 신규, 구현 중 |
| dev-codex | `tests/test_avilist_pipeline_runner.py` | Codex | 미추적 신규 |
| dev-claude(예정) | `src/robingraph/ingest/avilist_pipeline.py` 및 관련 단위 테스트 | Claude | **미확인** (확인 시점 파일 없음) |
| main-2 | `docs/work-log/2026-10-19-avilist-ingest-pilot.md` (저장소 기록) | Writer | 신규 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-AviList-단일자료원-수집파일럿-TEST]]
- [[Dev/index|Dev 인덱스]]
