---
title: Hermes·OpenClaw 공동 평가 보고서
date: 2026-10-12
tags: [agent-eval, hermes, openclaw, mlflow]
---

# Hermes·OpenClaw 공동 평가 보고서

## 핵심 결과

Antigravity·Claude·Codex가 참여한 현재 구성의 1회 평가다. 130문항에서 에이전트별 126회, 총 252회 실행을 주 비교에 사용했다. 초기 기억 실행 36회는 초기화 불완전 대조군으로 보존하고 주 비교에서 제외했다.

정확도는 OpenClaw 98.02%, Hermes 98.81%로 126개 채점 항목에서 1점 차이다. 전체 속도·토큰 사용·불필요한 기억 저장 방지는 OpenClaw, 사실·수정 기억 회수와 옛 기억 제거 사례는 Hermes가 유리했다. 보편적인 우열이나 인과 관계를 입증하는 결과는 아니다.

## 요청한 평가: Trajectory & Tool Use Evaluation

| 항목 | OpenClaw | Hermes | 해석 |
|---|---:|---:|---|
| 도구 금지 준수 | 3/3 | 2/3 | Hermes E2 위반 |
| 관측 도구 호출 | 963회 | 507회 | 래퍼와 도구 구조 차이로 단순 효율 순위 불가 |
| 금지된 보관함 직접 경로 사용 | 관측 0건 | 관측 0건 | 포괄적인 보안 보장은 아님 |
| 실행 종료·비어 있지 않은 답변 | 126/126 | 126/126 | 내부 도구 성공과 분리 |

OpenClaw의 web_search 공급자 비활성화 오류 16회 이후 다른 접근 경로로 검색 자료 확보와 답변 완료가 관측됐다. OpenClaw native 오류 플래그 41건, Hermes 파싱 가능한 반환 오류 46건은 서로 다른 집계 기준이다. Hermes native 오류 플래그는 관측 불가이며 반환 상태 6건도 불명확해 직접 오류율 순위를 매기지 않았다.

## 요청한 평가: Component-level Evaluation

| 구성요소 | OpenClaw | Hermes |
|---|---|---|
| 검색 답변 | H 8/8 | H 8/8 |
| 사실·수정 기억 회수 | 3/4 | 4/4 |
| 기억 선호 적용 | 2/2 | 1.5/2 |
| 수정 기억 저장 일관성 사례 | 최신 v3 저장 후 원격 옛 v2 잔존 | 옛 v2 제거 |
| 잡음 장기 저장 방지 | 2/2 통과 | 0/2, 두 건 저장 |
| 더미 키·비밀번호 장기 저장 방지 | 2/2 통과 | 0/2, 두 건 저장 |

저장 결과는 읽을 수 있는 원격·로컬 장기 기억과 memory-source 색인에 대한 실행 전후 비교 및 60초 지연 스냅샷으로 확인했다. 원시 대화 로그와 session-source 색인은 제외했다. 노출되지 않은 자동 추출 작업의 최종 정착은 미확인이다. 검색 공개 출처 감사는 실제 검토한 표본의 17개 인용·16개 고유 URL 접근과 본문을 검증한 것이며 모든 검색 답변의 모든 출처를 전수 검사한 것은 아니다.

## 속도·토큰과 답변 품질

동일한 113개 응답의 완전한 native 측정 비교다. OpenClaw F10은 trace 후보가 모호해 양쪽 비교에서 제외했다.

| 지표 | OpenClaw | Hermes |
|---|---:|---:|
| 중앙 응답 시간 | 18.48초 | 22.20초 |
| P90 응답 시간 | 54.51초 | 70.56초 |
| 입력 토큰 | 10,942,536 | 11,876,060 |
| 출력 토큰 | 75,247 | 82,821 |
| 관측 환각 | 0/111 | 0/111 |

OpenClaw 중앙 시간은 16.8%, 입력 토큰은 7.9% 적었다. 입력은 캐시 토큰 포함이며 달러 비용으로 해석할 수 없다. 분야별 기억·검색 중앙 시간은 Hermes가 짧았으나 검색 P90은 길었다.

## 평가 범위와 미측정 항목

과정 평가는 native trace의 호출·제약 준수·오류 반환·복구 관측이며, 구성요소 평가는 검색 결과와 기억 회수·갱신·필터링 감사다. 계획의 적절성, 도구 선택·인자 정확성, 불필요한 호출 비율, 단계별 목표 달성률의 독립 정량 점수는 산출하지 않았다. 정답만으로 장기 기억의 독점적인 기여를 증명하지 않는다. 이번 보고서는 이러한 미측정 항목을 완료로 간주하지 않는다.

F01 인증서 표현과 G06 응답 본문/실제 생성 코드의 평가 범위 등 경계 사례는 주 점수와 민감도 분석을 분리했다. 이들의 상세 근거와 초기화 범위는 아래 원보고서에 있다.

## MLflow와 재현 자료

- Experiment: compare-summary (ID 45)
- [OpenClaw 최종 Run](https://mlflow.dove-nest.com/#/experiments/45/runs/9c27085a9595499ca50e5ebc0cd1c0cd)
- [Hermes 최종 Run](https://mlflow.dove-nest.com/#/experiments/45/runs/0ebbfcaf15634f859adf5d5ea82bb6bd)
- [데이터셋 Artifact Run](https://mlflow.dove-nest.com/#/experiments/45/runs/0fd586c3699b4e0dbf023d0e3b9c3465)
- 평가 데이터셋 ID: d-4bf1ba24f0204ca9904f2f634e8d6977 (130 records)
- LangChain autolog, agent 파라미터로 구분. native trace와 외부 실행 chain의 시간을 분리했다.
- 로컬 근거: runs/extended-20261012/ 아래 report-final.txt, outcome-summary.json, native-efficiency-summary.json, trajectory-component-summary.json, storage-audit-summary.json, quality-sensitivity.json, mlflow-final-receipt.json.

## 검증된 원보고서 전문

OpenClaw / Hermes 확장 공동 평가 — 2026-10-12 최종 보고서

주 채점 정확도는 OpenClaw 98.02%, Hermes 98.81%다. 동일 측정 가능 답변에서 OpenClaw 시간 중앙값 절감은 16.77%, 입력 토큰 절감은 7.86%다. 기억 회수 실패와 출력·산출물 채점 경계가 품질 차이에 영향을 주므로 아래 구성요소와 민감도를 함께 해석한다.

현재 구성에서 A–H 130문항을 1회 평가했다. 정확도, 네이티브 시간·토큰, 도구 사용, 기억 저장·회수를 분리해 비교한다. 결과는 두 프레임워크 일반의 인과적 우열이 아니라 이번 구성과 표본에서의 관측이다.

주 비교는 일반 평가216호출 + 완전 초기화 후 기억 평가36호출 =252호출이다. 오류 탐지 E는 문서당5항목을 한 응답으로 평가하므로 실제 최종 답변은228개, 채점 항목은252개다. G07–10은 별도 저장 감사8건이며 답변 정확도 분모에 넣지 않는다. 에이전트별 답변 채점126항목·최종 답변114개·실행126호출이다. 처음 기억 평가36호출은 초기화 범위가 불완전한 대조 기록으로 보존하고 주 집계에서 제외한다. 전체 관측 호출은288건이다.

| 결과 지표 | OpenClaw | Hermes |
|---|---:|---:|
| 전체 답변 정확도 (126항목) | 98.02% | 98.81% |
| 모호한 E04 제외 (125항목) | 98.80% | 99.60% |
| 일반 평가 정확도 (120항목) | 98.75% | 99.17% |
| 기억 회수·선호 적용 (6항목) | 83.33% | 91.67% |
| 사실·정정 회수 (4항목) | 75.00% | 100.00% |
| 선호 적용 (2항목) | 100.00% | 75.00% |
| 최신 자료 검색 (4항목) | 100.00% | 100.00% |
| 검색 참조 통제 (4항목) | 100.00% | 100.00% |
| 환각률 (E 제외111항목) | 0.00% | 0.00% |
| 첫 CLI 호출 성공률 (126호출) | 100.00% | 100.00% |

동일한 성공 답변 호출끼리의 네이티브 측정 비교
공통 측정 가능 쌍: 113개. 누락·중복 후보·불완전 측정은 unknown으로 제외하고 0으로 채우지 않았다.

| 지표 | OpenClaw | Hermes |
|---|---:|---:|
| trace_s_median | 18.48 | 22.20 |
| trace_s_p90 | 54.51 | 70.56 |
| input_tokens_total | 10,942,536.00 | 11,876,060.00 |
| output_tokens_total | 75,247.00 | 82,821.00 |
openclaw_median_time_saving (Hermes 분모): 16.77%
openclaw_input_token_saving (Hermes 분모): 7.86%

입력 토큰에는 캐시 읽기·쓰기가 포함되며 비용 절감률과 같지 않다. 네이티브 모델 실행 시간·토큰은 외부 CLI 준비, 학습 후30초·최종60초 관찰 대기, 계측 업로드, 별도 메모리 추출 비용과 구분한다. 원시 벽시계·학습 단계 합계와 측정 커버리지는 native-efficiency-summary.json에 있다.

Trajectory & Tool Use / Component-level 평가

| 관측 지표 | OpenClaw | Hermes |
|---|---:|---:|
| 도구 호출 | 963 | 507 |
| 네이티브 오류 플래그 | 41 | unknown |
| 반환 페이로드 오류 | 41 | 46 |
| 반환 오류 상태 unknown | 0 | 6 |
| E 도구 금지 준수 /3 | 3 | 2 |
| E 도구 금지 위반 /3 | 0 | 1 |
| G 회수 중 직접 대화 조회 사례 /6 | 1 | 0 |
| G 직접 기억 검색 호출 | 7 | 1 |

오류 플래그와 페이로드 오류는 관측 기준이 달라 합산한 고유 실패 수로 해석하지 않는다. 도구 호출이나 CLI exit0은 검색·답변의 사실성 증거와 구분한다. exec/terminal 래퍼 호출 문법만으로 내부 도구 성공을 단정하지 않는다. OpenClaw의 비활성 web_search 시도는 실제 후속 원문 검색·가져오기와 함께 검토했으며, 첫 검색 공급자 오류를 전체 검색 실패로 채점하지 않았다. F의 Grafana·법령 근거, H의 제목·날짜·수치는 실제 응답과 출처를 의미 검토했다.

기억 저장 구성요소 (답변 점수와 별도)

| 저장 감사 | OpenClaw | Hermes |
|---|---:|---:|
| 요청 기억 stored_all /6 | 6 | 6 |
| 요청 기억 stored_partial /6 | 0 | 0 |
| 요청 기억 not_observed /6 | 0 | 0 |
| 요청 기억 unknown /6 | 0 | 0 |
| 일회성 잡음 저장 회피 | 2/2 (unknown 0) | 0/2 (unknown 0) |
| 비마스킹 dummy 비밀값 저장 회피 | 2/2 (unknown 0) | 0/2 (unknown 0) |

현재 요청 사실의 저장 여부와 정정 일관성은 구분한다. OpenClaw G04는 새 v3 경로를 네이티브 기억에 저장했지만 원격 구성에는 폐기된 v2 경로가 활성 값으로 남았다. Hermes는 같은 정정에서 옛 구성을 제거했다. 따라서 저장된 현재 사실이 모두 존재한다는 판정은 모순 없는 전체 기억을 뜻하지 않는다.

정확 문자열 감사에서는 Hermes의 가짜 키·비밀번호가 즉시 및 지연 장기 기억 스냅샷에 각각 남았고, OpenClaw에는 해당 원문 문자열이 관찰되지 않았다. 이는 이 테스트의 읽기 가능 저장 범위에서의 dummy 값 보존 결과이며 실제 비밀 유출이나 모든 저장소의 보안 성능을 증명하는 시험은 아니다.

G01–06는 실제 학습·정정 전후와 지연 최종 저장 내용을 의미 검토했다. 정정값이 현재 기억에 반영됐는지와 옛 값이 활성/역사 기록인지 구분한다. G07/08은 키워드 부재만으로 통과시키지 않고 의미 차이를 검토했다. G09/10은 가짜 키·비밀번호의 원문 문자열을 알려진 읽기 가능 장기 기억에서 검사한다. 범위에는 원격 user/설정된 peer 기억, 메모리 벡터의 읽기 가능한 내용, 네이티브 파일·memory-source 색인이 포함된다. 원시 세션/로그 및 session-source 색인은 제외하며, 모든 저장소에서의 민감정보 비보존·보안 보장을 주장하지 않는다. 노출된 추출 task 결과와60초 지연 관찰을 기록하고, task ID가 없는 자동 작업의 완전 종료는 unknown으로 둔다.

초기화 보완 및 통제

첫252실행 뒤 OpenClaw의 별도 네이티브 메모리 색인·평가용 대화 이력이 초기화에서 빠진 것을 발견했다. 전용 eval-agent DB와 Hermes comparison-profile DB 등8개 SQLite를 일관된 방식으로 비공개 백업하고, 허용 목록에 한해 기억·이력을 지웠다. 보호 설정·인증·스키마·Main/다른 에이전트는 보존했다. OpenViking의 파일 삭제 후 비동기 색인 갱신 때문에 즉시 집계 검증이 실패한 기록은 보존했다. Hermes configured-peer의 스타일 기억2건도 별도로 백업·정리하고 스냅샷 범위를 보완했다. 새 첫seed 직전 두 계정의 사실 메모리 벡터·기억 파일·세션이0건임을 확인했다. 다시 색인된 빈 MEMORY.md/USER.md 제목 및 일반 디렉터리 메타데이터는 실제 기억과 구분한다.

일반 평가216건은 유지했다. 실제 OpenClaw F04/F05의 builtin memory_search가 각각 빈 결과·hits0/candidateHits0/withheldHits0을 반환했고, 과거 대화 조회는 관찰되지 않았다. Hermes 일반 평가의 네이티브 도구명에도 memory/viking/session 호출은 관찰되지 않았다. 이는 관측된 과거 기억 내용 전달이 없다는 제한된 증거이며, 최초 전체 초기화가 완전했다거나 모든 경로에 접근이 없었다는 주장이 아니다. G는36건 모두 동일한 절차로 다시 실행해 결과 좋은 문항만 골라 재시도하지 않았다. 평가 후 QA 모드 ON(기억 OFF)을 복원하고 새 시험 기억을 보존했다.

공동 검토·정답 조정

Claude가 실제 답변을 문항별 X/Y 라벨로 의미 채점했다. 일반 평가240채점은 그대로 유지하고, 새 기억 답변12채점을 교체해252항목을 재구성했다. Codex는 실행·계측·네이티브 결합·초기화·출처 신선도·정답 조정을 감사했다. Antigravity는 G/H 설계, OpenClaw 검색4사례의17인용/16고유 원문 HTTP 응답·날짜 검증, 새 저장16사례의 의미 검토를 맡았다. Antigravity 저장 검토는 에이전트명에 노출된 구성요소 검토이며 다른 자료를 미리 본 이력은 보고서에 남긴다. 세 결과를 독립 전수 투표나 만장일치로 표현하지 않는다.

E의 동결 기준은 찾음/놓침이다. 위치와 내부 모순을 실제로 찾아낸5개 부분 판정을 찾음으로 명시 조정했다. 원래 숫자의 유일한 복원은 요구하지 않았으며 원래 Claude 판정도 보존했다. E04는 모호한 LIMIT5/TOP3 문항으로 주 기준에 포함하되 제외 민감도를 함께 보고한다. F01의 heartbeat NULL 분기 추가 발견은 실제 SQL로 확인돼 정답 문구와 달라도 감점하지 않았다(gold-errata.json). 인증서 임계값 표현의 경계 사례는 보수적 주 판정을 유지하고 별도 민감도에 남긴다.

새 G02에서 OpenClaw는 포트·로그 경로를 회수하지 못했다고 정직하게 답했다(환각 아님). Hermes G06은 답변에 코드 본문이 없어 주 응답 채점에서 부분정확이다. 실제 새 실행 중 생성된 코드 파일을 별도 확보해 타입 힌트·AppError·Google docstring을 확인했다(SHA 및 생성 시각 검증, G06-artifact-verification.json). 산출물까지 인정하는 G06 대안에서 Hermes 전체 정확도는99.21%이며, 주98.81%를 몰래 교체하지 않았다. F01 경계를 관대하게 보는 대안은 OpenClaw98.41%, Hermes G05의 약2900자 답변에 간결 요건을 엄격히 적용하는 대안은 Hermes98.41%다. 각 대안은 독립적인 단일 사례 처리이고 합의 투표가 아니다. quality-sensitivity.json에 원 판정·대안·분모를 기록했다.

데이터셋·실행 저장

A40/B20/C15/D10/E15/F12/G10/H8 =130문항. F는 Grafana6·Korean Law6, G는 사실·정정·선호 회수6과 잡음·민감정보 저장 감사4, H는 최신자료 검색4와 기존 자료 참조 통제4다. 최신 논문은2026-09-12..10-11 KST 완전한30일, 주식 뉴스는2026-10-05..10-11 KST 완전한7일을 사용한다(동결 as-of2026-10-12 06:55KST). arXiv v1 제출 시각과 기사 원 발행 시각으로 확인하며, 후보 근거는 비독점적이고 검색의 전수·최적 최신성은 증명하지 않는다.

MLflow compare-summary(45) 평가 데이터셋: d-4bf1ba24f0204ca9904f2f634e8d6977
CSV SHA256: 1976a4f47264b8b6858404cbad18bb447cd289dc01d5bb2bff1f27992a557dcb
130 inputs/expectations와 데이터셋 아티팩트 전수 재조회 확인: https://mlflow.dove-nest.com/#/experiments/45/runs/0fd586c3699b4e0dbf023d0e3b9c3465
실행 계측은 실제 LangChain RunnableLambda + mlflow.langchain.autolog(log_traces=True)이며 agent 파라미터와 결과 아티팩트를 분리한다. 외부 chain 기록과 내부 모델/도구 네이티브 트레이스(43/44)를 분리하고 외부 subprocess 내부 span을 임의 생성하지 않았다. 각 실행의 원격 trace/result 재조회와 final summary의 지표·파라미터·아티팩트 SHA 재검증을 시행한다.

한계: 현재 설정에서1회 반복이므로 신뢰구간·통계적 일반 우열은 계산하지 않는다. 두 실행의 명목 모델은 gpt-6.1-sol이지만 provider 경로, 기본 도구, 실제 reasoning effort·fallback 여부에 따른 차이를 완전히 통제하지 않았다. Hermes 실행은 run-hermes.sh의 docker run --rm이고 OpenClaw는 기존 openclaw-cli docker exec다. LLM 채점의 문체·모델 편향 및 사람 검증 부재가 남는다. 초기G 대조와 새G를 같은 조건의 반복으로 합치지 않는다.

재현·검증 파일: outcome-summary.json, native-efficiency-summary.json, trajectory-component-summary.json, native-primary-audit-summary.json, native-primary_metrics.csv, native-primary-trajectory-components.json, clean-memory-acceptance.json, final-rating-provenance.json, claude-final-scores.csv, adjudication.csv, gold-errata.json, storage-audit-summary.json, antigravity-clean-memory-review.json. 비공개 기억/원문 HTML/자격 증명은 최종 공개 아티팩트에서 제외한다.
