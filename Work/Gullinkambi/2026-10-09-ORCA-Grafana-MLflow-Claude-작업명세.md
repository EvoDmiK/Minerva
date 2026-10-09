---
title: Claude 작업 명세 — ORCA 개발 사용량·성과 Grafana/MLflow 추적
created: 2026-10-09
status: implementation-brief
project: Gullinkambi
---

# Claude 작업 명세 — ORCA 개발 사용량·성과 Grafana/MLflow 추적

> 이 문서는 Claude에게 전달할 구현 명세다. Dovie가 구현·배포하거나 ORCA 작업을 시작했다는 뜻이 아니다.
> 먼저 현재 저장소·서비스를 확인하고, 아래 **1차 범위**만 구현한다. 운영 반영은 별도 승인 단계다.

## 1. 목표와 판단 기준

ORCA에서 Codex·Claude 등을 사용한 개발 작업을 **사용량 + 실행 흐름 + 검증 결과**로 연결한다.

사용자가 다음 질문에 답할 수 있어야 한다.

1. 어떤 프로젝트·쓰레드·작업·시도에서 토큰과 호출이 많이 발생했나?
2. 입력 문맥이 얼마나 컸고, 캐시에서 재사용한 입력은 얼마였나?
3. 비캐시 입력·캐시 쓰기·출력은 얼마였나?
4. 확인 가능한 재시도·도구 실패·재검증이 몇 번 있었나?
5. 작업 결과는 성공·실패·중단·미확인 중 무엇이고, 테스트 증거가 있나?
6. 관측 데이터가 없는 것과 실제 0을 구분할 수 있나?

**큰 총 토큰 = 낭비**로 자동 판정하지 않는다. 캐시 적중률이 높아도 그 반복이 필요했는지는 별도 검토해야 한다. 사용량으로 테스트 성공·구현 완료를 추론하지 않는다.

## 2. 이미 확인한 환경과 재확인이 필요한 부분

### 확인된 출발점 — 2026-10-09 읽기 전용 확인

- 수집기 저장소: `/Volumes/Dove-Nest-SSD/projects/Birds-Nest`.
- 기존 수집기: `docker-compose/agents/hermes-telemetry/collector.py`, `README.md`, `tests/test_collector.py`.
- 수집 경로: 로컬 ORCA 로그/집계 → 기존 collector → n8n ingest → TimescaleDB → Grafana.
- 기존 테이블: `observability.orca_usage_daily`, `observability.orca_thread_usage_daily`.
- Grafana datasource: `Hermes Telemetry Ingest`, UID `ffskrzljzwr28b`.
- 기존 dashboard UID `dafsnnz67rw6ioc`, panel 46 `Orca 쓰레드별 사용량`의 SQL을 Grafana MCP로 확인했다.
- dashboard 저장소: `/Volumes/Dove-Nest-SSD/projects/Gullinkambi`.
- 현재 source/배포 후보: `source/Aviary Control Room.ui-spec.json`, `provisioning/dashboards/git-sync/Aviary Control Room.json`. 실제 생성·검증 절차는 저장소 문서를 확인한다. 이름이나 옛 dashboard 파일명을 가정하지 않는다.
- 기존 collector는 Codex `token_usage_record.payload.response_id`, Claude `assistant.message.id`로 파일 내 사용량을 중복 제거한 후 일별로 합산한다. 구현을 재사용하되 부분 업데이트·중복 파일·재시작 경계는 추가 검증한다.
- 10월 8일 Vault 기록에 SSD 이전 후 worktree roots 확장과 수집 복구가 있다. root 문자열만 보고 ORCA에서 생성된 세션이라고 확정하지 않는다.
- MLflow 후보 주소 `https://mlflow.dove-nest.com/health`는 10월 9일 HTTP GET 200 / `OK`였다. **인증·SDK 버전·Run 생성·artifact 저장·Tracing 가능 여부는 아직 검증하지 않았다.**
- Dovie 조회 시 Birds-Nest에는 기존 변경 `hermes/profiles/hybrid-v2/config.yaml`, `n8n/carrier_pigeon/workflows.json`이 있었다. Claude 시작 시 다시 확인하고 사용자 변경을 보존한다.

### Claude가 먼저 재확인할 것

실제 브랜치·dirty state, collector 실행 위치/버전, n8n ingest 및 migration 원본 위치, worktree roots·mount 구성, Grafana source→provisioning 절차, MLflow 서버/SDK 호환성·인증·artifact 권한, 현재 사용 가능한 ORCA 식별 메타데이터를 조사한다.

- read-only SQL/API/파일 확인만으로 discovery를 수행한다.
- 계정·비밀값은 현행 주입 경로로 읽으며 명세·로그·artifact에 출력하지 않는다.
- MLflow 주소는 후보이지 고정 배포값이 아니다. 이미 있는 설정을 재사용하고, 없는 필수 정보만 질문한다.
- Claude는 실제 저장소 기준 변경 계획·대상 파일·테스트 명령을 보고한 뒤 구현한다. 이 명세는 명시된 테스트 환경 변경만 허용하며 운영 쓰기는 허용하지 않는다.

## 3. 범위 — 최소 수직 구현부터

### 1차 필수

- Codex/Claude의 **호출별 privacy-safe 메타데이터** 수집과 제공자별 토큰 정규화.
- 명시적 task/attempt/session 매핑과 미귀속 처리.
- 기존 ingest를 통한 신규 additive 이벤트 저장 및 Grafana 패널.
- 작업 시도당 MLflow Run, 사용량 metric, 결과 tag, 안전한 검증 요약 artifact.
- 명시적 결과 이벤트의 수동 파일 입력 경로. ORCA 공식 구조화 이벤트가 발견되면 동일 계약으로 연결하되, 없으면 최초 데모는 수동 입력으로 검증한다.
- 중복 제거, 부분 파일, source 수정, 재시작, 한 sink 장애, MLflow 전송 복구를 검증한다.
- 기존 일별/쓰레드별 대시보드의 회귀 검증.

### 후속으로 분리

- 상세 모델·도구 span을 연결한 MLflow Tracing. **실제 시작/종료·부모 관계가 확보되는 경로에만** 적용한다.
- Antigravity 호출별 계측: 현재 local converter/집계 schema에서 얻을 수 있는 범위를 먼저 확인한다. 호출별 원본이 없으면 기존 집계만 유지하고 1차 호출별 통계에서 제외한다.
- 자동 작업 lifecycle producer, 실제 과금 추정, 효율 자동 평가, 알림, 전체 역사 backfill.

### 금지

- ORCA/Codex/Claude 내부 코드나 로그 포맷을 강제로 바꾸는 침습적 패치.
- MLflow autolog를 켜면 외부 CLI 에이전트가 자동 추적된다고 가정하기.
- 일별 합계로 과거 호출·재시도·span·테스트 결과를 지어내기.
- 원문 프롬프트, 응답, reasoning, 코드, 도구 인자, 접속정보의 원격 저장.
- 브라우저·GUI·Computer Use·Playwright/Selenium/CDP 사용. UI 검증은 API·JSON·SQL로 한다.
- 새 legacy Hermes gateway/profile/ORCA worker를 자동 시작하거나, 구현 검증을 위해 유료 모델 호출을 임의 발생시키기.
- 운영 서비스 재시작, NAS 배포, 운영 DB migration, n8n 활성화, 운영 MLflow 쓰기, Git push를 승인 없이 실행하기.
- 기존 사용자 변경, 원본 세션 로그, 기존 cursor, MLflow 기록을 삭제·덮어쓰기.

## 4. 최소 구조

```text
ORCA 관련 Codex/Claude 로그 (read-only)
             ↓
기존 collector의 파서 재사용 + 호출 이벤트 정규화
명시적 task/attempt 매핑 + 구조화 result 이벤트
             ↓
기존 n8n ingest / TimescaleDB (신규 additive 테이블)
             ├─ Grafana: 작업/쓰레드/날짜별 조회
             └─ durable outbox / 단일 exporter → MLflow Run
```

- TimescaleDB의 정규화 이벤트와 revision을 source of truth로 삼는다. DB 저장과 MLflow 전달 outbox 기록은 같은 transaction으로 묶는다.
- MLflow 중단이 기존 collector·n8n 성공 ack·Grafana 조회를 막지 않게 한다.
- MLflow가 usage 원본을 다시 해석하는 별도 scanner를 만들지 않는다.
- 이미 있는 DB/n8n/collector 배포 계층에 추가한다. 별도 큐·Kafka·새 관측 서버를 만들지 않는다.
- 신규 테이블 이름은 저장소 naming 규칙을 따른다. 아래 schema는 논리 계약이며 migration에 맞는 SQL 타입으로 구현한다.
- 호출별 초기 수집은 최근 48시간의 bounded window를 기본값으로 제안한다. 기존 legacy history는 그대로 유지하며 전체 역사 backfill은 자동 실행하지 않는다. 비밀이 아닌 batch/window 값은 합리적인 기본값으로 제공해 사용자 secret 파일에 관리 부담을 더하지 않는다.
- 변경 없는 파일을 매 주기 전체 재파싱하지 않는다. bounded batch·resume 위치를 유지하고 기존 집계 cursor와 신규 호출 cursor를 분리한다. 테스트 sample에서 scan 시간·최대 batch·입력 대비 DB 저장량·패널 query plan을 보고한다.

## 5. 데이터 계약

### 5.1 호출 이벤트

필수 식별/출처:

- `schema_version`, `source_schema_version`, `normalization_version`.
- `event_key`: 제공자/account-scope/session/request 원본 식별자에 기반한 안정적 키. 파일명·경로·collector_id·수집 시각을 이벤트 정체성으로 사용하지 않는다.
- `source_request_id_hash`, `session_id_hash`, `origin_namespace`, `agent`, `model`, `project_key`, `project_label`.
- `source_kind = raw_call | cumulative_delta | legacy_aggregate`, `observed_at`, `occurred_at`(UTC), `revision`, privacy-safe `fingerprint`.
- `origin_evidence = managed_metadata | explicit_mapping | path_only | unknown`; path-only 세션은 ORCA 확정 목록과 구분한다.
- `task_id`, `attempt_id`는 nullable. `attribution_method`와 `attribution_status = explicit | unassigned | ambiguous`.
- `event_status = partial | final | unknown`, `quality_flags`.

사용량:

- raw 숫자를 담은 allowlist와 `raw_total_tokens` / 기존 호환 `legacy_total_tokens`를 보존한다.
- `uncached_input_tokens`, `cache_read_tokens`, `cache_write_tokens`, `output_tokens`, `reasoning_tokens_subset`.
- `normalized_input_tokens`, `processed_total_tokens`, `non_cache_tokens`.
- 알 수 없는 값은 NULL + 사유. 알려진 0과 구별한다. missing/error를 0으로 강제 변환하지 않는다.
- `model_request_count`는 유일한 모델 request 단위로 센다. assistant 메시지 여러 조각과 tool 호출을 모델 호출 수에 별도 합산하지 않는다.

선택 관측:

- 실제 근거가 있을 때만 `latency_ms`, `turn_id_hash`, `parent_call_id_hash`, `retry_of_hash`, tool 이름·상태·에러 코드.
- file mtime이나 수집 시각을 모델 latency·작업 시작/종료로 사용하지 않는다.
- 에러 본문, trace stack, 도구 argument는 전송하지 않는다.

### 5.2 작업 매핑과 lifecycle

- `task_id`, `attempt_id`, `parent_task_id`, `role`, `session_id_hash`, `project_key`, `result_revision`.
- `started_at`, `ended_at`, `reported_status`, `verified_status`, `verification_state`.
- 종료 상태: `completed | failed | cancelled | blocked | unknown`.
- 테스트 요약: test ID, exit code, passed/failed/skipped 수(실제 machine-readable 결과가 있는 경우), 검증 artifact의 opaque handle와 checksum.
- 본문·전체 경로·작업 제목은 새 telemetry에서 기본 제외한다. 화면 이름이 꼭 필요하면 opt-in + redaction, 기본 label은 안전한 task ID다. 기존 thread_name 정책을 무단 확대하지 않는다.

매핑 방법은 사람이 읽는 제목이 아니라 명시적 ID를 사용한다.

1. 공식 ORCA 메타데이터/API에서 확인된 task→session/request 관계 우선.
2. 없으면 로컬 task manifest + 명시적 request ID 집합 또는 session/time 경계로 등록.
3. time 경계는 `[start, end)`로 고정하고 호출 occurred_at이 없거나 구간이 중첩되면 미귀속/ambiguous 처리.
4. 하나의 호출은 한 leaf task/attempt에만 귀속한다. 부모 roll-up은 별도 view이며 자식과 부모를 함께 합산하지 않는다.
5. 같은 쓰레드에 여러 작업이 이어질 수 있다. 쓰레드 전체를 각각의 task에 중복 할당하지 않는다.
6. 매핑이 없으면 쓰레드-level Grafana 집계만 가능하다. MLflow task Run을 성공으로 가짜 생성하지 않는다.
7. 잘못된 매핑 수정은 versioned attribution으로 처리하고 사용량 재계산·MLflow 정정 snapshot을 함께 재전송한다.

### 5.3 최소 manifest/result 입력 계약

1차는 공식 ORCA task API가 없어도 로컬 JSON/JSONL 입력으로 구현할 수 있어야 한다. 이는 호출을 새로 발생시키는 실행 계층이 아니다.

- manifest: schema version, opaque task/attempt/project/session ID, request ID 집합 또는 UTC `[start,end)` 범위, 매핑 revision, producer ID.
- result event: 안정적 event ID, task/attempt ID, result revision, UTC occurred_at, producer ID/type, `evidence_kind = real | fixture`, reported status, verification state, optional test ID/exit code/counts/allowlisted artifact handle.
- verification state: `unverified | evidence_verified | failed | unknown`. 수동 입력으로 `evidence_verified` 문자열을 넣었다는 이유만으로 검증됐다고 신뢰하지 않는다. 승인된 verifier producer가 artifact/test 결과 readback으로 대조한 이벤트만 verified view에 반영한다.
- fixture 이벤트는 isolated integration에서만 사용한다. 실작업/운영 experiment에 fixture 결과를 기록하지 않는다.
- JSON schema와 실제 sanitized 예제, 유효/무효 입력 test를 구현 산출물에 포함한다. 구조화 start/end 이벤트가 없으면 duration은 NULL이다.
- producer 인증은 기존 ingest 인증·권한과 조합하고 verification 권한을 usage reporter 권한과 구분한다. 비밀값을 manifest에 저장하지 않는다.

## 6. 토큰 의미와 계산 — 반드시 제공자별 테스트

기존 `total_tokens`는 제공자 의미가 섞여 있다. **기존 컬럼의 의미를 조용히 바꾸지 않는다.** 신규 표준화 값을 별도 컬럼/view에 저장하고 대시보드 설명에 정의를 표시한다.

### Codex — 현재 관측된 schema

- `input_tokens`는 cached input을 포함한다.
- `uncached_input = input_tokens - cached_input_tokens`.
- `normalized_input = input_tokens`; `processed_total = normalized_input + output_tokens`.
- `reasoning_output_tokens`는 output의 부분집합이므로 다시 더하지 않는다.
- cache write 미제공은 해당 schema에서 별도 분리 불가임을 표기한다. 별도 토큰을 가정해 추가하지 않는다.
- `token_usage_record` 같은 호출 단위 레코드가 우선. 누적 usage를 호출마다 더하지 않는다.

### Claude — 현재 관측된 schema

- `input_tokens`는 cache read/write와 분리된 uncached input이다.
- `normalized_input = input + cache_read_input + cache_creation_input`.
- `processed_total = normalized_input + output`.
- reasoning 세부량이 없으면 NULL. thinking 본문을 읽어서 추정하지 않는다.
- 동일 message ID의 stream/partial 업데이트는 합산하지 않고 검증된 최종 revision으로 치환한다. 마지막 줄을 항상 최종으로 가정하지 않는다.

### Antigravity — 제공자 검증이 먼저

- 현재 기존 collector는 raw total 또는 input+output을 total로 사용한다. 과거 관측에서는 cache read가 total보다 컸다.
- 따라서 `total - cache_read`를 일괄 적용하면 안 된다.
- raw converter schema와 source 의미가 검증된 경우에만 canonical normalized 수치를 제공한다. 확인 전에는 `legacy_total` 및 cache 값을 별도로 보여주고 canonical 파생값은 NULL.
- 호출 단위 없는 aggregate를 raw call과 합쳐 합산하지 않는다.

### 공통

- `processed_total = normalized_input + output` (reasoning subset 중복 제외).
- Claude의 `non_cache_tokens = uncached_input + cache_write + output`; 각 성분이 확인될 때만 계산한다.
- 현재 Codex schema의 `non_cache_tokens = input_tokens - cached_input_tokens + output_tokens`. input이 캐시를 포함한 전체 입력이라는 의미에 근거한다. 별도 cache-write 성분이 없다는 이유로 가상의 0 필드를 만들거나 확인된 비캐시 합계를 N/A로 만들지 않는다. 분리 미지원 cache-write metric은 NULL + not_separately_exposed로 남긴다.
- `cache_hit_rate = sum(cache_read) / sum(normalized_input) × 100`; 행별 백분율 단순 평균 금지. numerator와 denominator가 모두 알려진 동일 호출 cohort로 계산한다. input 합계 0 또는 분모 미확인인 경우 N/A.
- aggregate에는 complete/partial/unknown coverage와 known/eligible call count를 붙인다. SQL SUM이 NULL을 생략한 부분합을 전체 사용량이라고 표시하지 않는다. mixed-provider 집계에서 Antigravity 미확인 canonical 값도 조용히 제외한 뒤 전체라고 부르지 않는다.
- `cached_share_of_total`은 별도 값이며 `cache_hit_rate`와 혼동하지 않는다.
- invalid 음수, Codex `cached_input_tokens > input_tokens`, 완전히 확인된 normalized input에서 `cache_read > normalized_input` 같은 **제공자 schema별** 불변식 위반은 reject/quarantine + 지표로 남긴다. Claude의 raw uncached input보다 cache read가 큰 것은 정상일 수 있다. 0으로 clamp해 정상처럼 통과시키지 않는다.
- 누적 로그만 있는 경우 동일 session/model/segment의 baseline과 reset 경계를 검증한 delta만 사용한다. baseline 없으면 과거 호출별 사용량으로 환산하지 않는다.
- 문맥 압축/모델 변경은 segment 경계로 취급한다. 실제 retry 연결 없으면 호출 수 증가를 retry로 부르지 않는다.
- model 가격표·계정별 할인·구독 가중치가 없으므로 USD/실제 구독 소진량 계산은 1차에서 제외한다. UI 이름은 ‘캐시 제외 토큰’이며 ‘청구 토큰’이라고 부르지 않는다.

## 7. 멱등성·정정·전송 복구

1. 원본 호출 ID로 canonical event upsert; 여러 파일·collector·재시작에서 같은 이벤트 1건.
2. raw call과 legacy aggregate가 겹치는 범위는 source precedence와 coverage ledger로 선택한다. 둘을 함께 SUM하지 않는다.
3. 스트리밍 partial/late final, 토큰 수정, 시간·모델 정정에 대한 revision 선택 규칙과 충돌 표식을 테스트한다.
4. source 파일 append 중 끝줄 불완전하면 해당 줄을 보류한다. truncate/rotate/file-copy/mtime 변경은 source identity와 offset을 구분해 재처리한다.
5. DB transaction ack 전에는 source 처리 성공으로 확정하지 않는다. 기존 cursor를 통째로 초기화하지 않는다.
6. outbox는 snapshot revision 단위로 기록한다. 재시도 횟수·next_attempt_at·마지막 안전한 error code를 보존한다. bounded retry/backoff, dead-letter, backlog count/oldest-age 제공.
7. task+attempt+experiment→MLflow run_id 매핑을 DB에 보관하고, exporter는 초기에는 단일 실행자 + DB claim/lock로 serialize한다.
8. MLflow create_run 응답 유실 시 correlation tag로 후보를 검색하고 readback으로 재조정한다. candidate 여러 개면 conflict 상태로 멈춘다. tag에 서버-side UNIQUE가 있다고 가정하지 않는다.
9. 외부 MLflow와 DB 간 분산 transaction/정확히 한 번 전달을 약속하지 않는다. at-least-once + durable mapping + reconciliation으로 설계한다. SDK 자동 create 재시도로 Run이 중복되는 경계도 검증한다.
10. usage summary metric은 snapshot revision을 step으로 기록하고 latest revision으로 표시한다. 재전송된 metric history를 사용량으로 SUM하지 않는다. payload fingerprint와 revision을 함께 대조해 중복 발행을 줄인다.
11. 늦은 이벤트/attribution 수정은 새 summary revision으로 반영한다. 완료 Run의 late metrics 지원은 실제 SDK/server로 확인하고, 불가하면 명시적인 superseding reconciliation Run으로 연결한다. 최종 상태를 임의 reopen하거나 기존 기록을 삭제하지 않는다.

## 8. MLflow Run 계약

- 전용 experiment 제안: `orca-dev-observability`; 구현 전에 기존 명명·권한을 확인한다. RobinGraph 앱 RAG 및 SLAM 실험과 분리한다.
- **Run 하나 = task의 attempt 하나**. parent grouping은 선택이며 없어도 1차 완료 가능하다.
- tags: schema/normalization version, opaque task/attempt/session ID, project, agent/role, usage_scope, attribution_method, reported_status, verification_state, coverage, latest_snapshot_revision.
- metrics: processed_total, non_cache_tokens, input/cache_read/cache_write/output, known reasoning subset, request_count, known duration, known retry/tool_failure/reverification counts, 테스트 숫자(근거 있는 값만).
- unknown metric은 미기록 + availability tag로 구분한다. 숫자 0으로 대체하지 않는다.
- 결과 tag/artifact는 구조화 producer 이벤트나 test runner artifact에 근거한다. 에이전트의 자유문장 ‘통과’는 `reported`일 뿐 `verified`가 아니다.
- `FINISHED`는 관측 종료를 의미할 뿐 제품 검증 통과로 사용하지 않는다. 성공 여부는 result/verification tag로 따로 제공한다. failed/cancelled/blocked 상태 매핑은 실제 MLflow 지원 enum과 정책을 확인해 문서화한다.
- MLflow trace 자동 계측은 앱 SDK 호출에 적용된다. 외부 ORCA CLI의 상세 흐름은 별도 event adapter가 필요하다. 1차에서는 span을 날조하지 않는다.
- artifact는 새로 만든 allowlisted 요약 JSON·검증 manifest만 허용한다. 기존 로그/파일을 통째로 업로드하지 않는다. artifact readback으로 실제 저장을 확인한다.

## 9. Grafana 1차 패널

기존 대시보드는 유지하고 별도 ORCA 개발 관측 section/panel을 추가한다.

1. 작업/시도 또는 미귀속 쓰레드별: legacy total, processed total, cache hit, non-cache, request_count, reported/verified 상태, MLflow 링크.
2. 호출별 input 크기·cache read·output 시간 추이. raw call 있는 기간만 표시하고 시간순 unique request 기준 p50/p95도 제공한다.
3. source/attribution coverage, data freshness, unknown 필드, exporter backlog/failed count.
4. 근거 있는 retry/tool failure/reverification 지표만 표시한다. 관측 불가면 N/A.

- project/agent/model/task/status/usage_scope 필터; canonical task와 unassigned 행을 동시에 중복 집계하지 않는다.
- UTC event 저장, `Asia/Seoul` 표시 및 KST 달력일 집계. DB session timezone에 의존하지 않는 SQL.
- task/session/request IDs를 Prometheus label로 대량 생성하지 않는다. 상세 차원은 기존 PostgreSQL datasource로 조회한다.
- `docs/README_KO.md`는 file-provisioning JSON을 원본으로 설명한다. 동시에 `source/`에 UI spec도 있으므로 실제 authoritative 파일과 두 표현의 동기화 방법을 먼저 확인한다. 자동 generator 존재를 가정하거나 임의 새 생성기를 만들지 않는다. 기존 절차가 있으면 따르고, 없으면 authoritative JSON 변경과 companion spec의 일관성을 최소 범위로 유지한다. Grafana UI만 수정하지 않는다.
- MLflow URL은 검증된 tracking base/run ID로 생성한다. 비밀값/전체 경로/임의 URL을 tag나 링크에 넣지 않는다.
- 알람/주기 job/Discord 알림은 자동 활성화하지 않는다.

## 10. 테스트와 실행 검증

구현 계획에서 아래 각 항목에 실제 test ID/명령을 매핑한다. tests는 Claude가 작성·실행하며 Dovie는 명세만 제공한다.

### Offline/local 필수

- Codex/Claude 정상 및 missing/invalid tokens, reasoning subset, zero-input/N/A, partial→final, 늦은 정정.
- 호출 ID 중복, 같은 파일 replay, 여러 collector/source 사본, cumulative baseline/reset, truncate/rotate/incomplete EOF.
- raw/legacy 겹침, 시간대 KST 자정, 모델 변경, 멀티 task 쓰레드, 매핑 중첩·정정, unassigned 보존.
- DB ingest/outbox transaction 실패, retry/dead-letter, create_run 응답 유실, duplicate correlation tag conflict, 재시작 후 복구.
- metric latest revision 조회와 재전송 불변성, lifecycle unknown/blocked/cancelled, MLflow 종료 후 late revision 경계.
- Grafana JSON/schema/SQL 검증, 기존 collector tests·기존 usage 집계 회귀.
- payload/run tags/artifact/log에 가짜 secret·prompt·path marker를 주입했을 때 외부 출력에 포함되지 않는 privacy 테스트.
- 메타데이터만 수집하는 구현이며 기존 인증 파일·browser/session cookie를 접근하지 않는지 확인.

### Disposable integration 필수

사용자 승인된 운영계가 아닌 전용 로컬 테스트 DB/MLflow 또는 기존 격리 테스트 서비스를 사용한다. production URI에 integration test를 실행하지 않는다. ephemeral 로컬 서비스 실행에 필요한 자원은 Claude의 변경 계획에 정확히 명시한다.

- fixture/log 입력 → ingest DB → Grafana panel SQL → MLflow Run 생성 → API readback을 실제 연결해서 확인.
- 같은 입력 replay·collector/exporter 재시작 후 DB 호출 수·Run 수·latest totals 불변 확인.
- MLflow 장애 중 DB 저장/Grafana 조회 정상, 복구 후 같은 Run으로 전송되는지 확인.
- 실제 raw log의 **사용량-only bounded sample**을 로컬 read-only로 비교한다. private body를 복사하거나 fixture로 commit하지 않는다.
- 기존 합계와 canonical 집계 대조 시 source 기간·project 분류·provider semantics를 맞춘다. 과거 대화의 9월 14일 숫자를 최신 데이터의 hard-coded 정답으로 쓰지 않는다.
- API readback이 성공해도 UI 시각 품질 검증까지 됐다고 말하지 않는다. 브라우저 검증은 사용자가 별도로 한다.

운영 반영은 이 검증 후 plan/rollback/대상 service를 제시하고 별도 승인받는다. 승인 없이는 provisioning apply나 NAS migration을 실행하지 않는다.

## 11. 수용 기준

- [ ] AC1 — Codex/Claude 호출별 데이터와 원본 stable ID, coverage/unknown 정책이 실제 파서 테스트로 검증된다.
- [ ] AC2 — 토큰 정규화·캐시 적중률·reasoning 중복 제외가 제공자별 fixture와 설명으로 검증된다. Antigravity 미확인 파생값은 N/A다.
- [ ] AC3 — task/attempt 명시적 매핑과 ambiguous/unassigned 처리, 부모·자식 중복 방지, 매핑 정정이 동작한다.
- [ ] AC4 — replay/부분 업데이트/late correction/재시작/누적 reset 뒤 이벤트와 최신 summary가 중복·유실되지 않는다.
- [ ] AC5 — MLflow Run·metric·result tag·artifact를 실제 테스트 서버에서 만들고 readback한다. 응답 유실·중복 tag 경계가 처리된다.
- [ ] AC6 — MLflow 장애가 기존 ingest를 막지 않고 outbox retry/reconcile로 복구한다. unknown과 0이 구분된다.
- [ ] AC7 — Grafana 신규 SQL/JSON이 실제 테스트 DB에서 올바르게 조회되고 기존 usage 집계 및 개인정보 경계가 보존된다.
- [ ] AC8 — 테스트 결과가 실행 artifact에 연결되며 reported와 verified가 분리된다. latency/retry/traces의 미관측값을 날조하지 않는다.
- [ ] AC9 — 기존 사용자 변경·운영 서비스·원본 로그·cursor를 보존하고, 테스트 자원만 정확하게 정리한다.
- [ ] AC10 — 코드/테스트/문서/변경 계획/rollback·설정 목록·한계를 최종 보고한다. 자동 배포·push·알림은 수행하지 않는다.

AC는 1차 MVP에 대한 기준이다. 후속 Tracing/Antigravity 호출별/전체 역사 backfill 미구현을 1차 완료인 것처럼 보고하지 않는다.

## 12. Claude 최종 반환 형식

1. **결과:** 진단/구현/테스트 연결/운영 반영을 각각 됨·안됨·미확인으로 구분.
2. **실제 파일:** repo/branch, 기존 dirty state 보존 여부, 변경 파일·diffstat. 커밋했으면 실제 ref, push 여부 별도.
3. **데이터 계약:** provider 의미, source 범위, 매핑/중복/정정 정책, 미지원 항목.
4. **실행 증거:** 정확한 test 명령·exit code·passed/failed/skipped·bounded 실행 시간.
5. **연결 증거:** 테스트 DB count/totals, MLflow experiment/run ID와 readback 결과, Grafana SQL 결과 및 JSON 검증.
6. **실패·복구 증거:** MLflow outage, create 응답 유실, replay, restart, late correction 테스트 결과.
7. **안전:** 비밀/원문 전송 여부, 운영 변경 없음, 테스트 자원 생성/정리 목록.
8. **설정·운영 계획:** 실제 secret 참조 방식, nonsecret defaults, migration/provisioning/exporter 변경 plan과 rollback. 운영 승인 전 상태 명시.
9. **수용 기준 표:** AC1~AC10 각 PASS/FAIL/UNKNOWN과 artifact 근거.

테스트를 실행하지 않았으면 미실행으로 적는다. 로그나 결과를 그럴듯하게 만들어 반환하지 않는다. CLI/API가 없는 ORCA 기능은 불가/미확인으로 남긴다.

## 13. 참고와 증거

- MLflow 공식 Tracing: https://mlflow.org/docs/latest/genai/tracing/ — 2026-10-09 HTTP 200. 단계별 latency/token, OpenTelemetry, SDK autolog/manual instrumentation 지원 확인. 특정 ORCA 통합은 확인하지 않았다.
- 수집기 README 및 `collector.py`의 `normalize_orca_usage`, `raw_orca_row`, `parse_codex_usage_file`, `parse_claude_usage_file`를 2026-10-09 read-only 확인.
- Vault: `Work/Gullinkambi/2026-10-08-ORCA-SSD-이전-후-사용량-수집-복구.md`.
- Vault: `Work/Gullinkambi/2026-10-08-RobinGraph-ORCA-전체기간-토큰-사용량-검증.md`.
- 이 문서의 경로·schema 관측은 출발점이다. Claude가 구현할 시점에 최신 원문/저장소를 재확인한다.
