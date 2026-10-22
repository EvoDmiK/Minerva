---
created: 2026-10-23
updated: 2026-10-23
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-22-RG208-통합-관측-TEST-비교-단계적-전환]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RG-208] 의미 기반 그래프 질의 런타임 통합·관측·TEST 배포 검증 — 2026-10-22

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-22-RG208-통합-관측-TEST-비교-단계적-전환]] · 분류 근거 {"인프라":3,"자동화":2,"관측성":27,"데이터":7}

## 1. 개요 및 목적

> **문서 상태: 검증 범위 완료 (TEST shadow→active→off→active 전환, 실제 API 27건, 브라우저 8건 및 MLflow 관측 검증 완료; 운영 미배포, Git commit/push 없음)**  
> 상위 에픽 **RG-204 (의미 기반 그래프 질의 해석 및 안전한 실행 전환)**의 최종 4단계 과제인 **RG-208 (통합·관측·TEST 비교·단계적 전환)**의 구현, 빌드, TEST 환경 배포 및 엔드투엔드 검증을 완료했다.  
> 신규 컨테이너 이미지 `robingraph-api:test-semantic-graph-b77e26c7e897`를 TEST 환경에 배포하여 **`shadow` -> `active` -> `off` -> `active`** 단계적 전환 라이프사이클을 거치며 기존 7질문 베이스라인 지문(fingerprint) 일치 확인, 확장 27개 혼합 기능 시나리오 실제 API 전수 성공, 공개 Chromium 뷰포트(1280px 데스크톱 / 390px 모바일) 8건 전수 렌더링 정상(페이지 에러 0건)을 확인했다. 또한 외부 원격 MLflow 실험 33에 `route` 및 `candidates` 추적 span이 성공적으로 저장 및 조회됨을 확인했다.  
> **검증 범위 및 한계 명시**: RG-204 에픽 차원의 TEST 구현 및 런타임 통합 검증은 완료되었으나, **RG-205의 정답셋 사람 검토(Human Gold Review)는 미완료 후속 과제로 명확히 분리**되어 있으므로 상위 에픽 전체 완료로 혼동하지 않는다. 또한 MLflow 조회의 경우 50trace/5초 조회는 timeout이 발생하여 최근 5trace/20초 조회로 검증하였으므로 전체 서버의 부하 성능 검증으로 확대 해석하지 않으며, 물리 모바일 기기/Safari/Firefox 검증 및 부하 시험은 미실행 상태이다. 운영(Production) 배포, 조류 DB 쓰기, Git commit/push는 일체 수행하지 않았다.

---

## 2. 핵심 아키텍처 및 원칙

- 작업 및 변경 결과 요약
- 1. 작업 배경 및 아키텍처 통합
- 1) 통합 배경
- 2) 런타임 모드 제어 아키텍처
- 2. 주요 배포 및 구현 내용
- 1) 빌드 및 배포 스펙
- 2) 원격 관측성 (MLflow) 구성 및 DNS 이슈 해결
- 3. 검증 및 테스트 결과
- 1) 단계적 모드 전환 (Lifecycle) 실측 검증
- 2) 실제 UI 브라우저 렌더링 검증 (Chromium)
- 3) Python 전체 회귀 및 그래프 모듈 테스트
- 4) 실제 TEST 런타임 벤치마크 및 리소스 측정 (`runtime-benchmark.json`)
- 4. 중요한 한계 및 방법론적 시사점
- 5. 작업 현황 및 순차 진행 로드맵
- 6. 후속 수정 검증 착수 (전체 분류군 × 형질 질의 일반화)
- 관련 문서 및 검증 증거 링크

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

> **문서 상태: 검증 범위 완료 (TEST shadow→active→off→active 전환, 실제 API 27건, 브라우저 8건 및 MLflow 관측 검증 완료; 운영 미배포, Git commit/push 없음)**  
> 상위 에픽 **RG-204 (의미 기반 그래프 질의 해석 및 안전한 실행 전환)**의 최종 4단계 과제인 **RG-208 (통합·관측·TEST 비교·단계적 전환)**의 구현, 빌드, TEST 환경 배포 및 엔드투엔드 검증을 완료했다.  
> 신규 컨테이너 이미지 `robingraph-api:test-semantic-graph-b77e26c7e897`를 TEST 환경에 배포하여 **`shadow` -> `active` -> `off` -> `active`** 단계적 전환 라이프사이클을 거치며 기존 7질문 베이스라인 지문(fingerprint) 일치 확인, 확장 27개 혼합 기능 시나리오 실제 API 전수 성공, 공개 Chromium 뷰포트(1280px 데스크톱 / 390px 모바일) 8건 전수 렌더링 정상(페이지 에러 0건)을 확인했다. 또한 외부 원격 MLflow 실험 33에 `route` 및 `candidates` 추적 span이 성공적으로 저장 및 조회됨을 확인했다.  
> **검증 범위 및 한계 명시**: RG-204 에픽 차원의 TEST 구현 및 런타임 통합 검증은 완료되었으나, **RG-205의 정답셋 사람 검토(Human Gold Review)는 미완료 후속 과제로 명확히 분리**되어 있으므로 상위 에픽 전체 완료로 혼동하지 않는다. 또한 MLflow 조회의 경우 50trace/5초 조회는 timeout이 발생하여 최근 5trace/20초 조회로 검증하였으므로 전체 서버의 부하 성능 검증으로 확대 해석하지 않으며, 물리 모바일 기기/Safari/Firefox 검증 및 부하 시험은 미실행 상태이다. 운영(Production) 배포, 조류 DB 쓰기, Git commit/push는 일체 수행하지 않았다.

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **요구사항 / 목적** | 런타임 파이프라인 통합 & TEST 단계적 전환 | 의미 기반 라우터(`RG-206`)와 조건 추출기(`RG-207`)를 Django + Django REST Framework(DRF) 서비스 레이어에 통합하고, shadow/active/off 런타임 제어 및 관측 가능성(MLflow) 확보 |
| **컨테이너 빌드 & 배포** | TEST 이미지 스냅샷 배포 | 이미지 `robingraph-api:test-semantic-graph-b77e26c7e897` 빌드 및 TEST 환경 배포, manifest 소스 일치(`source_manifest_matches: true`), 컨테이너 healthy 확인 |
| **모드 전환 라이프사이클** | `shadow` -> `active` -> `off` -> `active` | 1) `shadow`: 기존 7질문 fingerprint 일치 확인, 동일 요청 흐름 내 동기 방식으로 임베딩/추출 라우팅 실행 및 span 기록 (백그라운드/병렬 아님).<br>2) `active`: 27개 혼합 기능 시나리오 실제 API 전수 정상 응답 (`api-active.json`).<br>3) `off`: 런타임 비활성화 시 기존 정규식/레거시 경로로 안전 폴백 (7질문 fingerprint 동일).<br>4) `active`: 최종 정상 활성화 복귀 확인 |
| **API 검증** | Baseline(7), Shadow(7), Active(27), Off(7) | 기존 7대 질문 응답 지문 보존 확인 및 확장 27개 혼합 기능 시나리오 실제 API 전수 정상 응답 (표본 내 오실행 0건, 계약 준수) |
| **UI 및 브라우저 검증** | 공개 Chromium 1280px / 390px 8건 통과 | 데스크톱(1280px) 4질문, 모바일(390px) 4질문 통과 (페이지 에러 0건, 스크린샷 8종 증거 확보, 모의 응답 아님) |
| **원격 측정 (Telemetry)** | MLflow 실험 33 저장 및 조회 | `graph_intent.route` 및 `graph_intent.candidates` span 실제 저장 확인.<br>구 내부 URI(`http://mlflow:80`) DNS 실패를 사용자 제공 HTTPS 엔드포인트로 TEST env 설정 수정하여 해결 |
| **런타임 벤치마크** | 순차 호출 지연 및 리소스 샘플링 | active 모드 동일 질문 순차 호출: cold 2,616.623ms, warm 5회 644~781ms (평균 694.7ms). 컨테이너 메모리 159.9MiB(2.0%) 안정화 관측 (`runtime-benchmark.json`) |
| **단위/통합 테스트** | 1,122실행 1,083통과 39skip 0fail | 전체 1,122건 실행 중 1,083 pass, 39 skip, 0 fail (23.857s) 및 graph 모듈 최종 89건 pass 통과 (0.197s) |
| **인프라 및 안전 경계** | 무영향 원칙 준수 | Production 배포 0건, 조류 DB 쓰기 0건, Git commit/push 0건, 격리 TEST 환경 한정 수행 |

| 모드 | 검증 대상 | 질문 수 | 검증 결과 | 세부 판정 |
|---|---|:---:|---|---|
| **Shadow** | 기존 베이스라인 7문항 | 7 | 기존 응답 fingerprint와 일치 확인 | 레거시 응답 보존 및 동기 span 기록 성공 |
| **Active** | 확장 실제 질의 세트 (혼합 기능 시나리오) | 27 | 27건 정상 HTTP 200 및 정형 스키마 응답 | 자연어/대조/부정/미지원 질의 정상 분기 |
| **Off** | 폴백 안전성 검증 | 7 | 기존 응답 fingerprint와 일치 확인 | 레거시 라우터로 무손실 즉각 폴백 확인 |
| **Active** | 최종 서빙 상태 확정 | - | 컨테이너 Health Check 200 OK | 최종 active 서빙 모드로 안착 확인 |

- **API 지연 분석 및 해석 주의사항**:
  - 임베딩 라우팅 및 조건 추출 로직이 추가되면서 baseline 대비 shadow/active 모드의 지연시간이 증가함 (median 약 300ms -> 620~660ms, max 2,500ms대). 여기에는 최초 질의 시의 초기 프로토타입 콜드 로드 비용이 포함되어 있음.
  - 본 측정은 소표본 순차 호출(비동시 호출)이며 각 모드별/질문별 조건이 상이하므로, **부하 시험(load testing)이나 성능 향상 주장으로 해석해서는 안 됨**.
  - **지연 시간 구분**: 라우터 단위의 순수 추론 지연(warm p95 = 0.379초)과 전체 웹 API 종단 간(HTTP 요청-Django-DRF-DB-직렬화) 지연시간(active median 659.2ms, max 2,592.1ms)을 명확히 구분하여 기록함.
  - **27개 active API의 성격**: 27개 질문은 자연어 질의뿐만 아니라 명시적 intent, filter, species_scope 등을 포함한 혼합 기능 시나리오 검증 세트이며, 40건 고정 홀드아웃셋(정답셋 평가)과 명확히 구분됨.

1. **RG-204 상위 에픽 완료 범위와 RG-205 사람 검토의 분리**:
   - RG-204의 하위 구현 과제인 RG-206, RG-207, RG-208이 모두 검증 완료되어 TEST 환경 런타임 배포가 완수됨.
   - 그러나 **RG-205의 정답 평가셋(Gold Questions)에 대한 '인간/전문가 검토(Human Gold Review)'는 아직 미완료 상태**이므로, 상위 에픽 RG-204는 '진행 중'으로 유지하며 전체 완료로 혼동하지 않아야 함. 사람 검토는 향후 운영 배포 승인 전 독립적인 후속 과제로 명확히 분리 관리됨.
2. **원격 관측(MLflow) 조회 성능 한계**:
   - 50개 트레이스를 5초 타임아웃으로 일괄 조회하는 질의는 타임아웃이 발생함.
   - 최근 5개 트레이스를 20초 타임아웃으로 조회하여 span 기록이 정상 저장됨을 확인함.
   - 따라서 본 검증 결과는 원격 서버에 라우팅 span이 유실 없이 기록된다는 **관측 가능성(Observability) 입증**에 한정되며, MLflow 서버의 대량 부하 처리 성능을 보증하는 것이 아님.
3. **브라우저 및 클라이언트 검증 범위의 한계**:
   - 자동화된 공개 Chromium(1280px, 390px 에뮬레이션)으로 UI 레이아웃 및 렌더링을 검증함.
   - 실제 물리 모바일 기기 터치/제스처 반응, Safari(WebKit) 엔진, Firefox(Gecko) 엔진 검증은 미실행 상태임.
4. **운영 환경 및 데이터 무변경 원칙**:
   - 모든 배포 및 검증은 격리된 TEST 환경(16GB Mac .97)에서만 수행됨.
   - Production 배포, 운영 DB 및 조류 DB 쓰기, Git commit/push는 수행하지 않음.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-22-RG208-통합-관측-TEST-비교-단계적-전환]]
- [[Dev/index|Dev 인덱스]]
