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
| 라이선스 | CC BY 4.0 (`AVILIST_SOURCE` 기재값. Codex가 2026-10-19 공식 안내 페이지에서 Explorer 링크와 CC BY 4.0 명시를 웹으로 확인) |
| 고정 SHA-256 | `3b08845b54b8ab53908aee84d05b0fd8df765e9e01dc655599ca304d9f132411` (`AVILIST_SHA256`, 기존 pin) |
| 참조 자료(신규 수집 아님) | 기존 고정 KOS 2025 한국조류목록 v2.1 참조 bundle `src/robingraph/retrieval/species_ko_names.json`, SHA-256 `b660e125…66ba7a` (`KOS_SHA256`) |
| 분류판 | `TAXONOMY_RELEASE=v2025b`, `CONCEPT_SET_ID=rg:concept-set:avilist-v2025b` |

KOS 자료는 이번에 새로 내려받지 않으며, 기존 저장소에 고정된 bundle을 그대로 입력으로 사용한다.
KOS 라이선스 필드는 기존 builder에서 `None`이며 이용 안내 문구(`KOS_USE_NOTE`)만 보존한다.
KOS는 별도 고정 보조 입력이며 CC BY로 재표기하지 않는다.

## 확인한 근거

- **공식 JSON 실제 다운로드 (Codex 전달, 실제 네트워크)**: 19,933,159 byte, 33,684행 / species 11,131,
  SHA-256이 기존 pin과 일치. Writer가 직접 재다운로드하지는 않았다.
- **코드 정독 (Writer, 읽기만)**: `dev-codex/scripts/run_avilist_pipeline.py`(첫 정독 241줄 → 재확인 263줄, 미추적 신규 파일),
  `dev-codex/tests/test_avilist_pipeline_runner.py`(미추적 신규 파일), 기존 추적 파일
  `scripts/build_species_distribution.py`, `src/robingraph/ingest/store.py`의 `begin_run`·`append_batch`·
  `activate_release`·`pipeline_state_version`·`active_release_context`·`fail_run` 존재 확인.
- 코어 모듈 `robingraph.ingest.avilist_pipeline`(`prepare_manifest`, `validate_approval`)은 Writer 첫 확인 때
  없었고, 재확인 시 dev-claude에 `src/robingraph/ingest/avilist_pipeline.py`(8,858 byte)와
  `tests/test_avilist_pipeline.py`가 생겼다. dev-codex 워크트리에는 아직 없다(통합 전). approval 필드는
  `manifest_sha256`·`bundle_sha256`·`decision`·`reviewer`·`reviewer_type`(agent/human) 등이다.
- **approval의 의미 (Codex 전달)**: CLI gate의 approval은 신뢰된 로컬 운영자 파일의 digest 대조이며 인증
  서명이 아니다. 검토 에이전트가 실제 prepare 패키지를 재검증한 뒤 준 agent 승인 메시지를 저장하는 것으로,
  사용자의 Production 승인이나 인간 조류 전문가 검토와 다르다.

## 변경 전후 동작

- 변경 전: AviList 자료는 n8n 기준정보 workflow(`docs/n8n/reference-ingest.md`)와 수동 builder로
  `species_distribution.json`을 생성했다. 자료원 단위로 review 승인·hash gate·PG pilot pointer를 묶는
  재실행 가능한 CLI 경로는 없었다.
- 변경 후(구현 중, 코드 기준 설명):
  (아래는 Writer가 2026-10-19 재확인한 263줄 runner 기준)
  1. `prepare [--source PATH] --output DIR`: `--source`가 없으면 공식 URL을 받으며, 다른 URL로 redirect되면
     거부, 25,000,000 byte 상한. builder로 bundle을 다시 만들고(내부에서 AviList·KOS SHA 불일치 시 실패)
     manifest를 생성한다. 출력 폴더가 이미 있으면 덮어쓰지 않고 실패한다. 결과는 `review_required`.
  2. `apply --package DIR --approval FILE`: 패키지의 source로 bundle·manifest를 재계산해 바이트 단위로
     같은지 확인(hash gate)하고 approval을 검증한다. 이어서 읽기 전용 runtime 검사를 수행한다.
     `--apply`가 없으면 `dry_run`으로 끝나고 쓰기 lock에 들어가지 않는다.
  3. 읽기 전용 runtime 검사: TEST PG/Neo4j(`bolt://192.168.219.98:7687`) allowlist, 설치된
     `species_distribution.json`과 bundle 동일성, `/health`의 `deployment_target=test`, 활성 분류판이 pin과
     같은지, 이름 벡터 인덱스 `dry_run=True` 결과가 최신·호환인지, 고정 검색 회귀 4건
     (Kea outside/all answer, Keaa outside clarify, 청둥오리 korea answer). answer 응답은 API의 분포 status·
     evidence가 승인 bundle과 같은지도 대조한다. 검사 전후 활성 분류판·한국어 이름 dataset 불변을 확인한다.
     이 검색 검증은 기존 runtime의 같은 bundle 근거 회귀 + 이름 인덱스(855종) dry-run이며, 새 PG artifact의
     projection 검증이 아니다.
     이름 인덱스에 갱신이 필요하면 쓰기 없이 실패한다.
  4. `--apply` 시: `ROBINGRAPH_DEPLOY_TARGET=test`와 PG 대상 allowlist(host/port/database/user/schema)를
     연결 전에 확인하고, 연결 후 `current_database()/current_user`를 다시 확인한다. advisory lock으로 동시
     실행을 막고, 기존 pilot dataset이 있으면 source_id·`policy_status=allowed`가 맞는지 확인한다. 같은 manifest의 release가 이미 활성이면 provenance(content/manifest SHA)를 대조한 뒤
     `already_applied` no-op. 아니면 pilot dataset `rg:dataset:avilist-distribution-pilot` 아래 release·run을
     만들고 bundle 전체를 source_record 1건으로 append한 뒤 state version CAS로 pilot pointer를 활성화한다.
     cursor에 `projection_performed: false`를 기록한다. release/record의 URI는
     `urn:robingraph:avilist-pilot:bundle:<bundle canonical sha256>`이며 실제 artifact는 `source_record.payload`에
     있다. 원문 URL·각 SHA·라이선스는 release metadata의 sources/inputs로 보존한다.
     append/activate 예외 시 먼저 활성 pointer를 다시 읽어 같은 run/release가 이미 커밋됐으면
     `applied_reconciled`로 처리하고(응답 유실 대비), 아니면 run을 실패 처리하며 활성화하지 않는다. 실패 상태
     확인마저 실패하면 재시도 시 reconcile된다는 note를 남긴다. 재시도 시 record ID는 manifest 해시 기반이라
     같고 run ID만 새로 생성된다.

## 변경 파일

| 워크트리 | 파일 | 담당 | 상태 |
|---|---|---|---|
| dev-codex | `scripts/run_avilist_pipeline.py` (263줄) | Codex (root CLI·통합) | 미추적 신규, 잠금/정책/응답유실 보강 |
| dev-codex | `tests/test_avilist_pipeline_runner.py` (test 13개) | Codex | 미추적 신규 |
| dev-claude | `src/robingraph/ingest/avilist_pipeline.py`, `tests/test_avilist_pipeline.py` | Claude | 신규, dev-codex 통합 **미확인** |
| main-2 | `docs/work-log/2026-10-19-avilist-ingest-pilot.md` (저장소 기록) | Writer | 신규 |

dev-codex의 다른 dirty 파일(Jenkins·RG-406 관련)은 이번 작업과 별개이며 본 문서의 변경으로 보지 않는다.
최종 변경 파일 목록과 diff는 **미확인**이다.

## 검증 방법과 실제 결과

| 검증 | 종류 | 결과 |
|---|---|---|
| 공식 JSON 다운로드·크기·행/종 수·SHA pin 대조 | 실제 네트워크 | **통과** (Codex 전달: 19,933,159 byte, 33,684행, 11,131 species, SHA 일치) |
| runner unittest 1차 | mock (실제 DB 아님) | 7개 통과 (Codex 전달, 보강 전 이력) |
| `uv run --locked --extra test python -m unittest tests.test_avilist_pipeline_runner tests.test_postgres_ingest tests.test_species_scope -v` | mock/단위 (실제 DB 아님) | **34 통과 · 실패 0 · skip 0** (runner 13 + 기존 21, Codex 실제 실행, 로그 `/tmp/rg-avilist-pipeline/related-tests.log`) |
| 코어 모듈 단위 테스트 `tests/test_avilist_pipeline.py` (Claude) | 단위 | **미확인** (위 34개에 포함되지 않음) |
| TEST PG 읽기 전용 identity | 실제 TEST DB (읽기) | `current_database(), current_user` = (robingraph_test, robingraph_test_app), pilot dataset 수 0 확인 (Codex) |
| TEST 앱 HTTP smoke | 실제 TEST API (읽기) | `/health` target=test, Kea/outside answer + Nestor notabilis 확인. **단발 smoke이며 최종 파이프라인 검증 아님** |
| prepare 실제 패키지 생성·manifest SHA | 실제 실행 | **미확인** |
| apply dry-run (TEST 읽기 전용 gate) | 실제 TEST DB/API | **미확인** |
| apply 실제 쓰기·재실행 no-op | 실제 TEST PG 쓰기 | **미확인** |
| main Codex 독립 리뷰 | 리뷰 | **미확인** |
| Python 전체/Node UI 테스트 | — | **미확인** (실행 여부 전달 없음) |
| graphify update | — | **미확인** |

mock 단위 검사가 확인하는 범위(Writer 첫 정독 시 8개 test 기준, 보강 후 13개의 추가 세부는 미정리): 동일 release no-op 시 begin_run/append 미호출, 다른
dataset pointer 거부, append 실패 시 미활성화·fail_run·재시도 record ID 유지, CAS `expected_state_version`
전달과 `projection_performed=False`, readiness 실패 시 write lock 미진입, dry-run 시 lock 미진입,
production 대상 시 설정 로드 전 거부, TEST라도 다른 DB명 거부. 이는 실제 DB 동작 검증이 아니다.

## 배포·커밋 정보

- 실행 위치(예정, Codex 전달): root batch를 TEST 기존 앱 컨테이너의 `/tmp` 별도 코드 경로에 설치해 실행한다.
  앱 이미지 교체·컨테이너 재시작은 없다(예정 사항이며 실행 결과는 **미확인**).
- TEST PG 실제 쓰기(`apply --apply`): **아직 미실행** (2026-10-19 05:07Z Codex 전달 기준).
- Production: 대상 아님, 변경 없음. commit/push/merge: 없음(현재까지).

## 남은 한계와 후속 사항

- 코어 모듈·실제 TEST 실행·독립 리뷰 결과를 받아 위 "미확인" 항목을 갱신해야 한다. 확정 후에도 표현은
  "1차 수동 TEST pilot 완료"로 하고, 전체 파이프라인(주기 실행·projection·대량 수집) 완료로 쓰지 않는다.
- 도구 이력: Writer 작업은 처음 Codex 세션으로 배정됐으나 startup agent-update-prompt 실패로 같은 Task를
  Claude 세션으로 재시도했고, 이 문서는 그 재시도 세션(main-2 Writer)이 작성했다. 앱·데이터 결과와 무관하다.
- n8n schedule 연결, 도메인 projection, 두 번째 자료원 확장, 대량 수집 적용은 별도 범위다.
- source_record가 bundle 전체를 1건으로 저장하므로, 행 단위 diff/증분 적재는 이번 파일럿으로 검증되지 않는다.
- `verify_runtime`은 TEST API `http://127.0.0.1:8000`을 가정하므로 실행 위치(예정: TEST 앱 컨테이너 내부)에 의존한다.
- 이번 결과를 다른 자료원이나 Production 수집 경로로 일반화하지 않는다. 인증 정보는 기록하지 않았다.
- Obsidian 동기화: `Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-19-AviList-단일자료원-수집파일럿-TEST.md`에
  같은 초안을 기록하고 재조회했다(status: draft). 카테고리 백로그는 최종 증거 전 갱신하지 않았다.
