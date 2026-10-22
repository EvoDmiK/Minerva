---
created: 2026-10-23
updated: 2026-10-23
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-22-RG208-그래프-질의-496건-MLflow-GenAI-평가]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RG-208 / 평가] MLflow GenAI Evaluate 기반 그래프 질의 496건 TEST 재평가 — 2026-10-22

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-22-RG208-그래프-질의-496건-MLflow-GenAI-평가]] · 분류 근거 {"인프라":0,"자동화":2,"관측성":44,"데이터":28}

## 1. 개요 및 목적

> **문서 상태: 평가 및 검증 완료 (실제 API 496건 계약오류 0건, 이전 관측치 대비 상태/커버리지 차이 0건, fresh DB Oracle 480건 1,879종 3,126조건 불일치 0건, 18건 비답변 strict safety 18/18 통과 및 변조 13/13 탐지 완료; MLflow native 평가엔진 점수 저장 및 496행 결과표 등록 완료, Run `0295848aaa854d8cb8acc289373daf67` FINISHED 확인 완료; 원본 기대값 불변, 사람 검토 false, 운영 미배포, Git commit/push 없음, 조류 DB 쓰기 0건)**  
> 2026-10-22 등록된 496건 고유 질의 Native MLflow 평가 데이터셋(`robingraph-taxonomic-regression-v1-746baf0adb1b`, ID `d-9b84fb796702487a90cbf57e754995a8`)에 대해 `mlflow.genai.evaluate` SDK 인터페이스를 활용한 공식 재평가(Re-evaluation)를 성공적으로 완결했다.  
> 본 평가는 단순한 상위 API 상태 코드 확인에 그치지 않고, 결정적(deterministic) 계약 스코어러(Contract Scorer)를 통한 기대 조건 전수 검증(496건), TEST 컨테이너(`robingraph-api-test`) 환경에서 외부 TEST Neo4j(32GB Mac .98) 및 PostgreSQL(NAS .99)을 직접 조회하는 fresh DB Oracle 전수 대조(480건), 그리고 18개 비답변(non-answering) 케이스에 대한 사유별 엄격 감사(`scripts/audit_graph_question_safety.py`)를 결합하여 수행되었다.  
> 첫 번째 시도에서 MLflow SDK의 최상위 `expectations` Null 값 제약(`MlflowException: The 'value' field must be specified`)으로 인해 24개 응답 수집 시점에서 하네스 중단이 발생했으나(실패 런 보존: `20261022T113250Z`, Run ID `765da50a79ba42cd860bd13b5730499f`), 원본 데이터셋의 기대값을 불변 보존한 채 평가 DataFrame에서 `expectations={"contract": 원본expectations}`로 중첩 래핑하여 하네스를 정상화하고 신규 Run(`0295848aaa854d8cb8acc289373daf67`)으로 496건 전체 재실행 및 서버 집계표 등록을 완료했다.

---

## 2. 핵심 아키텍처 및 원칙

- 작업 및 변경 결과 요약
- 1. 작업 배경 및 1차 하네스 중단 분석
- 1) 작업 배경
- 2) 1차 시도 하네스 중단 원인 분석 (20261022T113250Z)
- 2. 해결 방안 및 3중 엄격 검증 체계
- 1) 원본 데이터셋 보존 및 DataFrame 중첩 래핑
- 2) 3중 엄격 검증 파이프라인
- 3) 지연 시간 및 라우팅 메타데이터 기록 원칙
- 3. 평가 실행 및 검증 완료 증거
- 1) 실행 환경 및 명령어
- 2) 실제 TEST API 496건 전수 실행 결과
- 3) Fresh DB Oracle 480건 재대조 결과 (`db-evidence.json`)
- 4) Safety 비답변 사유 엄격 감사 결과 (`safety-audit.json`)
- 4. MLflow 평가 결과 등록 및 아티팩트 보존
- 1) Run 상태 및 결과표 등록
- 2) 보존 아티팩트 목록 (`docs/verification/assets/2026-10-22-dataset-evaluation-20261022T113441Z/`)
- 5. 형상 관리 및 거버넌스 상태
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

  ```text
  File ".../mlflow/genai/evaluation/harness.py", line 982, in _get_new_expectations
    for exp in eval_item.get_expectation_assessments()
  File ".../mlflow/genai/evaluation/entities.py", line 194, in get_expectation_assessments
    Expectation(name=key, value=val)
  File ".../mlflow/entities/assessment.py", line 419, in __init__
    raise MlflowException.invalid_parameter_value("The `value` field must be specified.")
  mlflow.exceptions.MlflowException: The `value` field must be specified.
  ```

  ```python
  # 최상위 Null 제약을 우회하면서 내부 Null을 완벽히 보존
  eval_df["expectations"] = eval_df["expectations"].apply(lambda exp: {"contract": exp})
  ```

  ```bash
  uv run --with mlflow==3.14.0 python scripts/evaluate_graph_question_dataset.py \
    --env-file [TEST_ENV_FILE]
  ```

## 4. 검증 근거 및 트러블슈팅

> **문서 상태: 평가 및 검증 완료 (실제 API 496건 계약오류 0건, 이전 관측치 대비 상태/커버리지 차이 0건, fresh DB Oracle 480건 1,879종 3,126조건 불일치 0건, 18건 비답변 strict safety 18/18 통과 및 변조 13/13 탐지 완료; MLflow native 평가엔진 점수 저장 및 496행 결과표 등록 완료, Run `0295848aaa854d8cb8acc289373daf67` FINISHED 확인 완료; 원본 기대값 불변, 사람 검토 false, 운영 미배포, Git commit/push 없음, 조류 DB 쓰기 0건)**  
> 2026-10-22 등록된 496건 고유 질의 Native MLflow 평가 데이터셋(`robingraph-taxonomic-regression-v1-746baf0adb1b`, ID `d-9b84fb796702487a90cbf57e754995a8`)에 대해 `mlflow.genai.evaluate` SDK 인터페이스를 활용한 공식 재평가(Re-evaluation)를 성공적으로 완결했다.  
> 본 평가는 단순한 상위 API 상태 코드 확인에 그치지 않고, 결정적(deterministic) 계약 스코어러(Contract Scorer)를 통한 기대 조건 전수 검증(496건), TEST 컨테이너(`robingraph-api-test`) 환경에서 외부 TEST Neo4j(32GB Mac .98) 및 PostgreSQL(NAS .99)을 직접 조회하는 fresh DB Oracle 전수 대조(480건), 그리고 18개 비답변(non-answering) 케이스에 대한 사유별 엄격 감사(`scripts/audit_graph_question_safety.py`)를 결합하여 수행되었다.  
> 첫 번째 시도에서 MLflow SDK의 최상위 `expectations` Null 값 제약(`MlflowException: The 'value' field must be specified`)으로 인해 24개 응답 수집 시점에서 하네스 중단이 발생했으나(실패 런 보존: `20261022T113250Z`, Run ID `765da50a79ba42cd860bd13b5730499f`), 원본 데이터셋의 기대값을 불변 보존한 채 평가 DataFrame에서 `expectations={"contract": 원본expectations}`로 중첩 래핑하여 하네스를 정상화하고 신규 Run(`0295848aaa854d8cb8acc289373daf67`)으로 496건 전체 재실행 및 서버 집계표 등록을 완료했다.

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **요구사항 / 목적** | MLflow GenAI Evaluate 공식 재평가 완결 | 등록된 496건 질의에 대해 `mlflow.genai.evaluate` 기반 정식 평가 수행. API 계약 통과, DB Oracle 전수 대조 및 비답변 엄격 감사 연계 완결 |
| **평가 대상 환경** | 실제 TEST API 환경 | Target URL: `https://robingraph-test.dove-nest.com`<br>Container Image: `robingraph-api:test-taxonomic-traits-eb8169862c0e`<br>데이터셋 ID: `d-9b84fb796702487a90cbf57e754995a8` (496건 고유 질의) |
| **1차 하네스 중단 및 조치** | SDK Assessment 스키마 제약 해결 | 24개 응답 수집 시점(`rank=None`, `taxon=None` 포함 케이스)에서 MLflow SDK 최상위 Null 제약 발생 (앱 오류 아님, 실패 런 `20261022T113250Z` 보존). 원본 불변 유지 및 `expectations={"contract": ...}` 중첩 래핑으로 해결 |
| **실제 API 496건 결과** | 계약 오류 0건, 이전 차이 0건 | - 계약 오류: **0건** (496 / 496 전수 통과, pass rate 100%)<br>- 이전 baseline 대비 status/disposition/coverage 차이: **0건**<br>- 응답 분포: `answer` 289건, `empty` 137건, `insufficient` 58건, `clarify` (status 없음) 12건 (합계 496건) |
| **DB Oracle 전수 대조** | 480건 직대조 불일치 0건 | - 대상: 480건 (`query`/`empty` 478건 + 아종 직접 부족 2건)<br>- 외부 활성 TEST Neo4j 및 PG 직접 조회 실행 완결 (`db-evidence.json`)<br>- 고유 반환 종수: **1,879종** / 검증 조건 근거: **3,126건** / 근거 오류: **0건** |
| **Safety 엄격 감사** | 18개 비답변 사유 100% 부합 | - 18건 비답변 사유별 엄격 감사 전수 통과 (`18/18 pass`, `safety-audit.json`)<br>- 모의 변조 13건 대상 self-check 전수 탐지 (`13/13`) *(감사기 자체 검증이며 앱 API 13건 검증 아님)* |
| **지연 시간 및 라우팅 추적** | 지연 측정 및 라우팅 메타 보존 | - 지연 시간: `first_request` **1,484.569 ms**, `subsequent_request` (495건) **p50 774.13 ms**, **p95 1,527.66 ms** (정렬 floor .95*(n-1) 계산, 가열 상태 확인, 부하테스트 아님)<br>- 라우팅: 496건 전수 `semantic` 라우팅 확인 (`selected_intent`, `route_method`, `kind` 보존) |
| **MLflow 실행 정보** | 신규 평가 Run 완료 | - Experiment ID: `33` (`robingraph-test`)<br>- Run ID: `0295848aaa854d8cb8acc289373daf67`<br>- Run URL: https://mlflow.dove-nest.com/#/experiments/33/runs/0295848aaa854d8cb8acc289373daf67<br>- 자산 경로: `docs/verification/assets/2026-10-22-dataset-evaluation-20261022T113441Z`<br>- 상태: **FINISHED (MLflow 결과표 496행 저장 완료, `summary.json`, `extended-summary.json`, `verified-results.json` 보존)** |
| **거버넌스 및 안전 상태** | 무영향 원칙 준수 | 기존 데이터셋 불변, 백로그 상태 일체 무변경, 운영 미배포, 조류 DB 쓰기 0건 (`bird_db_writes: 0`), Git commit/push 0건, 서비스 재시작 0건 |

- **백로그 상태**: **기존 백로그 상태 일체 무변경 (RG-208 완료 보존, RG-204/RG-205 진행 중 보존)**
- **기존 데이터셋**: **불변 유지 (`d-9b84fb796702487a90cbf57e754995a8` 기대값 수정 없음)**
- **사람 검토 상태**: **`human_reviewed: false` 명시 유지 (에이전트 검증셋)**
- **조류 DB 쓰기**: **0건 (`bird_db_writes: 0`)**
- **운영(Production) 배포**: **0건 (일체 미반영)**
- **Git 상태**: **commit / push 0건**
- **서비스 재시작**: **0건**

1. **회귀 전용 평가 (Regression Assessment)**:
   - 본 평가는 모델/파서 수정 피드백에 노출된 496건 회귀 데이터셋을 대상으로 하므로, 미공개 일반 성능 측정이 아닌 기존 품질 기준선의 엄격한 유지 여부를 검증하는 용도임.
2. **단일 스코프(`species_scope='all'`) 중심**:
   - 현재 496건 평가셋은 전수 종 스코프 위주로 구성되어 있으므로, 향후 한반도 조류 스코프(`korea`) 및 다양한 정렬 기준에 대한 추가 평가셋 보강이 권장됨.
3. **MLflow 평가 하네스 동시성 설정 최적화**:
   - 향후 대규모 평가 시에는 API 호출과 SDK 트레이스 집계 단계의 동시성을 분리하거나 적정 Worker 수를 확보하여 불필요한 직렬화 지연을 완화할 필요가 있음.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-22-RG208-그래프-질의-496건-MLflow-GenAI-평가]]
- [[Dev/index|Dev 인덱스]]
