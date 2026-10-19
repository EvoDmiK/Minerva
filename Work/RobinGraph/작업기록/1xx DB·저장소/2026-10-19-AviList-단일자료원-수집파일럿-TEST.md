---
created: 2026-10-19
updated: 2026-10-19
project: RobinGraph
type: work-log
category: "1xx DB·저장소"
status: draft
tags:
  - robingraph
  - ingest
  - avilist
  - postgresql
  - pilot
---

# AviList 단일 자료원 반복 수집 파이프라인 TEST 파일럿 — 2026-10-19

[[Work/RobinGraph/작업기록/1xx DB·저장소/작업 백로그|1xx DB·저장소 작업 백로그]] · [[Work/RobinGraph/RobinGraph 작업 백로그|전체 작업 백로그]]

저장소 기록: `docs/work-log/2026-10-19-avilist-ingest-pilot.md` (main-2)

> 상태: **초안 (검증 진행 중)**. 아래 "미확인"으로 표시한 항목은 Codex/Claude의 최종 증거를 받은 뒤
> 갱신한다. 이 문서는 현재 시점의 구현 범위와 확인된 사실만 기록하며, 완료·배포·커밋을 주장하지 않는다.

## 요청 배경과 목표

사용자가 대량 수집 작업에 앞서 Airflow를 새로 도입하지 않고 기존 n8n + PostgreSQL 구성으로
**자료원 하나에 대한 반복 가능한 수집 파이프라인**을 먼저 구현하도록 요청했고, 세 담당자 협업으로 진행한다.

- 목표: 공식 자료원 1개(AviList Explorer v2025b JSON)를 고정 SHA-256으로 받아, 결정적(deterministic)
  prepare → 운영자 review → hash gate를 거친 뒤 TEST PostgreSQL에 별도 pilot dataset/source_record/
  pointer만 저장하는 흐름을 확인한다. 같은 입력을 다시 실행하면 새 run 없이 no-op이 되어야 한다.
- 역할: Codex(dev-codex)가 root CLI·통합, Claude(dev-claude)가 코어 모듈·단위 테스트, main 워크트리의
  Codex가 독립 리뷰, Writer(main-2)가 본 작업 기록을 맡는다.
- Airflow 미도입 판단은 사용자 지시에 따른 것이며, 이 문서에서 Airflow와의 비교 평가를 수행하지 않았다.

## 작업 경계 (이번 범위에 포함하지 않는 것)

- 새 종 분포 추론, 도메인 projection(Neo4j/검색 자료 반영), 이름 벡터·임베딩 쓰기 없음.
- n8n schedule/workflow 연결 없음. 현재는 수동 CLI 실행 파일럿이다. "반복"은 동일 입력 재실행의
  멱등성을 뜻하며 주기 실행이 구현됐다는 의미가 아니다.
- Production 대상 실행·배포, commit/push/merge 없음. 운영 배포 승인 규칙(AGENTS.md)을 그대로 따른다.
- Writer는 코드 수정·DB 쓰기·서비스 재시작을 하지 않았다. 이 문서 외 파일을 변경하지 않았다.

## 자료원과 라이선스

| 구분 | 내용 |
|---|---|
| 신규 수집 자료원(1개) | AviList Explorer v2025b JSON `https://explore.avilist.org/data/avilist-2025b.json` |
| 안내 페이지 | `https://www.avilist.org/checklist/v2025b/` |
| 라이선스 | CC BY 4.0 (`scripts/build_species_distribution.py`의 `AVILIST_SOURCE` 기재값) |
| 고정 SHA-256 | `3b08845b54b8ab53908aee84d05b0fd8df765e9e01dc655599ca304d9f132411` (`AVILIST_SHA256`, 기존 pin) |
| 참조 자료(신규 수집 아님) | 기존 고정 KOS 2025 한국조류목록 v2.1 참조 bundle `src/robingraph/retrieval/species_ko_names.json`, SHA-256 `b660e125…66ba7a` (`KOS_SHA256`) |
| 분류판 | `TAXONOMY_RELEASE=v2025b`, `CONCEPT_SET_ID=rg:concept-set:avilist-v2025b` |

KOS 자료는 이번에 새로 내려받지 않으며, 기존 저장소에 고정된 bundle을 그대로 입력으로 사용한다.
KOS 라이선스 필드는 기존 builder에서 `None`이며 이용 안내 문구(`KOS_USE_NOTE`)만 보존한다.

## 확인한 근거

- **공식 JSON 실제 다운로드 (Codex 전달, 실제 네트워크)**: 19,933,159 byte, 33,684행 / species 11,131,
  SHA-256이 기존 pin과 일치. Writer가 직접 재다운로드하지는 않았다.
- **코드 정독 (Writer, 읽기만)**: `dev-codex/scripts/run_avilist_pipeline.py`(241줄, 미추적 신규 파일),
  `dev-codex/tests/test_avilist_pipeline_runner.py`(미추적 신규 파일), 기존 추적 파일
  `scripts/build_species_distribution.py`, `src/robingraph/ingest/store.py`의 `begin_run`·`append_batch`·
  `activate_release`·`pipeline_state_version`·`active_release_context`·`fail_run` 존재 확인.
- runner가 import하는 코어 모듈 `robingraph.ingest.avilist_pipeline`(`prepare_manifest`, `validate_approval`)은
  2026-10-19 Writer 확인 시점에 dev-codex·dev-claude 어느 워크트리에도 파일이 없었다. Claude 담당 코어로
  진행 중인 것으로 보이며, **코어 구현·단위 테스트 결과는 미확인**이다.

## 변경 전후 동작

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

## 변경 파일

| 워크트리 | 파일 | 담당 | 상태 |
|---|---|---|---|
| dev-codex | `scripts/run_avilist_pipeline.py` | Codex (root CLI·통합) | 미추적 신규, 구현 중 |
| dev-codex | `tests/test_avilist_pipeline_runner.py` | Codex | 미추적 신규 |
| dev-claude(예정) | `src/robingraph/ingest/avilist_pipeline.py` 및 관련 단위 테스트 | Claude | **미확인** (확인 시점 파일 없음) |
| main-2 | `docs/work-log/2026-10-19-avilist-ingest-pilot.md` (저장소 기록) | Writer | 신규 |

dev-codex의 다른 dirty 파일(Jenkins·RG-406 관련)은 이번 작업과 별개이며 본 문서의 변경으로 보지 않는다.
최종 변경 파일 목록과 diff는 **미확인**이다.

## 검증 방법과 실제 결과

| 검증 | 종류 | 결과 |
|---|---|---|
| 공식 JSON 다운로드·크기·행/종 수·SHA pin 대조 | 실제 네트워크 | **통과** (Codex 전달: 19,933,159 byte, 33,684행, 11,131 species, SHA 일치) |
| runner unittest (`tests/test_avilist_pipeline_runner.py`) | mock (실제 DB 아님) | **7개 통과** (Codex 전달). 단, Writer가 읽은 현재 파일에는 test 메서드가 8개 있어 실행 시점과 개수 차이 **확인 필요** |
| 코어 모듈 단위 테스트 (Claude) | 단위 | **미확인** |
| prepare 실제 패키지 생성·manifest SHA | 실제 실행 | **미확인** |
| apply dry-run (TEST 읽기 전용 gate) | 실제 TEST DB/API | **미확인** |
| apply 실제 쓰기·재실행 no-op | 실제 TEST PG 쓰기 | **미확인** |
| main Codex 독립 리뷰 | 리뷰 | **미확인** |
| Python 전체/Node UI 테스트 | — | **미확인** (실행 여부 전달 없음) |
| graphify update | — | **미확인** |

mock 단위 검사가 확인하는 범위(Writer 정독 기준): 동일 release no-op 시 begin_run/append 미호출, 다른
dataset pointer 거부, append 실패 시 미활성화·fail_run·재시도 record ID 유지, CAS `expected_state_version`
전달과 `projection_performed=False`, readiness 실패 시 write lock 미진입, dry-run 시 lock 미진입,
production 대상 시 설정 로드 전 거부, TEST라도 다른 DB명 거부. 이는 실제 DB 동작 검증이 아니다.

## 배포·커밋 정보

- TEST 앱 이미지 교체·서비스 재시작: 현재까지 전달된 사항 없음 (이 파일럿은 앱 배포 대상이 아니라 CLI 실행).
- TEST PG 실제 쓰기: **미확인** (아직 실행 결과 전달 없음).
- Production: 대상 아님, 변경 없음. commit/push/merge: 없음(현재까지).

## 남은 한계와 후속 사항

- 코어 모듈·실제 TEST 실행·독립 리뷰 결과를 받아 위 "미확인" 항목을 갱신해야 한다.
- n8n schedule 연결, 도메인 projection, 두 번째 자료원 확장, 대량 수집 적용은 별도 범위다.
- source_record가 bundle 전체를 1건으로 저장하므로, 행 단위 diff/증분 적재는 이번 파일럿으로 검증되지 않는다.
- `verify_runtime`은 TEST API `http://127.0.0.1:8000`을 가정하므로 실행 위치(16GB Mac TEST 앱)에 의존한다.
- 이번 결과를 다른 자료원이나 Production 수집 경로로 일반화하지 않는다. 인증 정보는 기록하지 않았다.
- Obsidian 동기화: 이 노트가 저장소 초안과 같은 내용이다. 카테고리 백로그는 최종 증거 전 갱신하지 않았다.
