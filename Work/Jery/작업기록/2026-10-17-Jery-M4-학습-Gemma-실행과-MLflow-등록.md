---
created: 2026-10-17
date: 2026-10-17
project: Jery
type: worklog
status: completed
tags:
  - jery
  - mcp
  - dataset
  - training
  - gemma
  - mlflow
  - worklog
---

# Jery M4 기준 모델 학습, Gemma 실행과 MLflow 등록

## 요약

Hermes에 등록된 MCP 5개·도구 96개를 대상으로 합성 데이터셋 v2를 만들고, Mac mini M4·32GB에서 Jery 선형 기준 모델을 실제로 학습했다. Codex가 데이터·계약·통합을, Claude가 모델·평가를, Antigravity가 독립 데이터 감사를 담당했다. 학습은 2026-10-16에 완료했으며 주말 동안 계속 돌아가는 작업은 아니다.

2026-10-17에는 Gemma 4 E4B 4비트를 MLX로 실행해 소규모 도구 선택을 시험했다. Gemma는 사전학습·지시튜닝된 공개 가중치를 그대로 사용했으며 Jery 데이터로 미세조정하지 않았다. 학습한 Jery 선형 모델과 Gemma 실행 결과는 서로 다른 실험이다.

MLflow의 `jery-routing` 실험에 Gemma 결과, 동일 사례의 선형 모델 비교, 전체 학습·평가 결과를 올렸다. 학습 모델은 Model Registry에 등록했고, 학습에 사용한 데이터셋·코드·설정도 함께 업로드했다. 정답은 모두 미검토 합성이므로 결과는 탐색 실험이며 실제 사용 정확도를 뜻하지 않는다.

## 작업 및 변경 결과

| 항목 | 결과 |
|---|---|
| 전체 등록 MCP 분류 데이터 | 서버 5개, 도구 96개, 합성 사례 1,162개 |
| 로컬 기준 모델 | 선형 softmax 학습 완료, 저장·복원·공개 예측 함수 검증 |
| 독립 감사 | 분할 커버리지, 미학습 action, 비선택 사례 부족 등 확인 |
| Gemma 로컬 실행 | E4B 4비트, MLX, 6개 합성 검증 사례로 실행 확인 |
| MLflow 실험 | Gemma 프롬프트 2개, 선형 비교, 학습 결과 등록 |
| 모델·데이터 보존 | Jery-LinearRouter v1, 가중치·v2 데이터·평가·소스 업로드 |
| 운영 범위 | 실제 Hermes 대화 로그를 학습에 사용하지 않았고, 이번 분류 시험에서 MCP 도구를 실행하지 않음 |

## 1. 데이터셋과 공통 계약

데이터 위치는 `datasets/mcp-routing-v2/`, 카탈로그 버전은 `hermes-mcp-57e701d87790`이다. 기존 `hermes-routing-v1`의 130개 사례는 보존했다.

| 구분 | 내용 |
|---|---|
| 전체 사례 | 1,162개 |
| 시나리오 그룹 | 340개, 같은 그룹은 같은 분할에 유지 |
| 학습 / 검증 / 평가 | 668 / 248 / 246 |
| 도구 구성 | Grafana 62, Swallow 13, Obsidian 10, Korean Law 10, Kestrel 1 |
| 결정 유형 | select_tools, no_tool, clarify, unsupported |
| 검토 상태 | 모두 needs_human_review |
| 실행 검증 | 모두 execution_verified: false |

도구 명세는 MCP 스키마 캐시와 Grafana 도구 목록으로 구성했다. 실제 대화·호출 결과를 모아 만든 학습 데이터가 아니다. 등록·명세 확보와 각 도구의 실제 연결·실행 성공은 구분한다.

모델 입력은 요청, 호출 전 맥락, 후보 도구 ID와 명세로 제한한다. 정답·검토 상태·출처·분할·정답을 암시하는 ID는 특징으로 사용하지 않는다. 출력은 `prediction-v1` 계약을 따르며 후보 밖 도구와 잘못된 action을 거부한다.

읽기 전용 Hermes 로그 수집기와 검토 후보 API는 구현되어 있지만, 이번 학습을 위해 실제 로그를 수집하거나 정답으로 승격하지는 않았다. 관측된 호출과 검토된 정답을 분리하는 원칙을 유지한다.

## 2. M4 선형 기준 모델 학습

문자 2·3-gram과 단어 특징, 도구 명세 유사도를 사용하는 경량 선형 라우터다. Transformer나 사전학습 LLM을 학습한 실험은 아니다. 후보 도구와 세 비선택 결정을 함께 점수화하고 action은 보조 헤드로 예측한다.

- 환경: Apple M4, 통합 메모리 32GB, Python 3.9.6, 외부 Python 의존성 없음.
- 실행 ID: `v2-baseline-20261016`.
- 비교: 검색 기준 24개 + 선형 기준 24개 설정.
- 선택: epochs 20, lr 0.3, l2 0, seed 13, 도구 명세 특징 사용.
- 학습·선택: train만 학습하고 validation으로 설정 선택 후 test 보고.
- 실행 시간: 233.53초, 프로세스 4개·각 스레드 1개.

### 평가 결과

| 지표 | 검색 기준 | 학습한 선형 기준 |
|---|---:|---:|
| 도구 선택 정확도 | 59.13% | 82.61% |
| MCP 서버 정확도 | 88.70% | 99.13% |
| 결정 유형 정확도 | 90.65% | 98.37% |
| 결정 유형 macro F1 | 0.3160 | 0.8755 |
| 불필요 호출 비율 | 56.25% | 6.25% |

평가 분할은 246건이다. 도구·서버 정확도는 정답이 select_tools인 230건에서 계산했고, 평가에 나타난 도구 클래스는 84개다. 불필요 호출 비율은 비선택 정답 16건 중 도구 호출을 선택한 비율이다.

선형 모델 recall@1/3/5는 83.48% / 96.96% / 99.13%, 후보 밖 선택은 0건이다. 도구를 맞힌 action 사례의 action 정확도는 36.67%다. 적재된 모델의 추론 p50은 1.306ms, p95는 6.310ms이며 프로세스 시작과 모델 로딩은 포함하지 않는다.

독립 감사에서는 train에만 있는 도구, 검증·평가의 미학습 action, 작은 no_tool·clarify 표본, 분할별 서버 비율 차이와 후보 개수 단서 등을 확인했다. 새로운 표현과 비Swallow 후보 누락에 대한 일반화는 추가 평가가 필요하다.

### 파일과 재현

- 학습 코드: `src/jery/model/cli.py`, `routers.py`, `features.py`.
- 평가: `src/jery/evaluation/metrics.py`.
- 설정: `configs/model/mcp-routing-v2-baseline.json`.
- 가중치: `models/mcp-routing-v2/v2-baseline-20261016/linear.json.gz`.
- 기본 예측 가중치: `models/mcp-routing-v2/latest/model.json.gz` — 위 선형 모델과 동일한 바이트.
- 결과: `outputs/model/mcp-routing-v2/v2-baseline-20261016/`.

```sh
PYTHONPATH=src python3 -m jery.model.cli --config configs/model/mcp-routing-v2-baseline.json --run-id v2-baseline-20261016 --workers 4
python3 scripts/predict_tool.py --request '삼성전자 지금 주가 확인해줘.'
```

위 학습 명령은 기존 실험의 재현 명령이다. 새 실험은 별도 run ID를 사용한다.

## 3. Gemma 4 E4B 4비트 실행

- 공개 모델: `mlx-community/gemma-4-e4b-it-4bit`.
- revision: `475b9088d29754a3379866cf5aeb6b41acd313c2`.
- 로컬 위치: `models/gemma-4-e4b-it-4bit/`, 약 4.8GiB.
- 환경: Python 3.12.15, MLX 0.32.4, mlx-lm 0.32.2, Transformers 5.20.1.
- 설정: thinking 비활성, temperature 0, 최대 생성 256토큰.
- 사례: validation에서 서로 다른 시나리오 6개, 후보 4~8개. 전체 96개 후보 실행은 시험하지 않음.

| 실행 | 출력 계약 통과 | 계약 통과 및 결정 일치 | 도구 선택 일치 | 응답 중앙값 |
|---|---:|---:|---:|---:|
| 첫 영어 프롬프트 | 2/6 | 2/6 | 0/2 | 5.084초 |
| 수정 한국어 프롬프트 | 5/6 | 2/6 | 0/2 | 5.109초 |
| 선형 모델, 같은 6건 | 6/6 | 4/6 | 2/2 | 준비 후 1.890ms |

수정 실행에서 모델 로딩은 3.186초, MLX 최대 할당 메모리는 약 5.034GB였다. MLX 메모리는 시스템 전체 메모리가 아니다. LLM 지연은 프롬프트 처리와 생성, 첫 사례 컴파일 비용을 포함한다. 선형 모델 중앙값은 로딩이 포함된 첫 호출을 제외하며, 첫 호출은 0.303초였다.

주요 오류는 잘못된 action 값·출력 구조, 도구 선택 대신 clarify 반환, 카메라 요청을 no_tool로 판단한 사례다. 프롬프트 수정은 형식 통과를 개선했지만 정답 일치를 늘리지는 못했다. 같은 검증 사례를 보며 수정한 결과라 독립 평가 성능으로 해석하지 않는다.

```sh
.venv/bin/python scripts/run_llm_smoke.py
```

실행기: `scripts/run_llm_smoke.py`. 기록: `docs/data/gemma-e4b-smoke.md`. 원본 예측·프롬프트·지표는 `outputs/gemma-e4b-smoke/20261017-071522/`와 `20261017-071618/`에 보존했다. 아직 Gemma 미세조정이나 기존 라우터 대체는 하지 않았다.

## 4. MLflow 등록과 다운로드 검증

[MLflow jery-routing 실험](https://mlflow.dove-nest.com/#/experiments/46)

| 등록 항목 | 링크 |
|---|---|
| Gemma 첫 프롬프트 | [실행 결과](https://mlflow.dove-nest.com/#/experiments/46/runs/6dffc0a589754e71b5751fa9454162fc) |
| Gemma 수정 프롬프트 | [실행 결과](https://mlflow.dove-nest.com/#/experiments/46/runs/cfa1464d0ec44fae9cff1bc386b00520) |
| 같은 6건의 선형 모델 비교 | [실행 결과](https://mlflow.dove-nest.com/#/experiments/46/runs/41747af688ea43bc99977cad410d1539) |
| 학습 모델·전체 평가·데이터셋 | [학습 아티팩트](https://mlflow.dove-nest.com/#/experiments/46/runs/bf3206a9898d42ac917865f256bcc60d) |
| 등록 모델 | [Jery-LinearRouter v1](https://mlflow.dove-nest.com/#/models/Jery-LinearRouter/versions/1) |

학습 아티팩트 실행에는 다음 16개 파일을 업로드했다.

- `model/`: 실제 학습 가중치 `linear.json.gz`와 사용 방법.
- `datasets/mcp-routing-v2/`: train·validation·test JSONL, tools, scenarios, labels, manifest, README.
- `evaluation/`: report JSON/Markdown, validation sweep, test 예측, 통합 검증 기록.
- `source/source.zip`: 학습·예측 코드와 설정.

파일마다 업로드 후 재다운로드해 SHA-256 일치를 확인했다. 내려받은 모델을 실제로 읽어 이전 비교 사례 6건의 예측이 모두 동일하게 재현되는지 확인했다. Registry 버전은 READY, 실행은 FINISHED 상태다.

등록 모델은 Jery 전용 gzip JSON 형식이며 함께 올린 Jery 로더로 읽는다. MLflow pyfunc 모델은 아니다. Gemma 가중치는 로컬에 있고 MLflow에는 업로드하지 않았다. 실제 Hermes 원본 로그·운영 DB도 포함하지 않았다.

## 5. 검증과 형상 관리

- 기존 v1 데이터 검증: 130개 사례·도구 10개·시나리오 65개 통과.
- v2 데이터 검증: 1,162개 사례·도구 96개·서버 5개·시나리오 그룹 340개 통과.
- 기준 모델 통합 시 검증: 서로 다른 테스트 58개 통과.
- Gemma 실행기 추가 후 통합 테스트: 13개 통과. 위 58개와 중복되는 테스트가 있어 단순 합산하지 않는다.
- 후보·action·출력 계약 검증, 모델 입력의 정답 정보 제외, 저장·복원 일치 확인.
- MLflow 업로드 파일 해시 및 다운로드 모델 예측 재현 확인.
- 브랜치: `dev-codex`.
- 모델·감사 통합 커밋: `bd6d2cc`.
- 데이터 확장: `b0d3fb8`, 예측 계약: `05030ed`, 학습 실행기: `23deefa`.
- 로컬 원격 추적 ref `origin/dev-codex`는 `280db74`이며 이후 위 커밋은 아직 푸시하지 않은 상태다. 원격 ref를 새로 fetch한 검증은 아니다.
- Gemma 문서·실행기·테스트·선택 의존성 파일은 현재 미커밋이다.
- 가중치·실험 출력은 Git 제외 상태로 유지하며 이번에는 MLflow에 별도 보존했다.

## 6. 후속 과제

- [ ] 합성 정답 검토와 실제 요청으로 구성한 독립 평가셋 확보.
- [ ] no_tool·clarify·비Swallow 후보 누락 사례와 action 평가 보강.
- [ ] Gemma 출력 제약·프롬프트와 더 넓은 후보 수에서 정확도·지연 검증.
- [ ] 검토 데이터로 미세조정할지, 다른 소형 모델과 비교할지 결정.
- [ ] 실제 Hermes 로그 수집·정제·검토를 수행한 후 학습 데이터 반영.
- [ ] 로컬 커밋과 Gemma 변경사항을 검토해 커밋·푸시.

## 관련 문서

- [[Work/Jery/index|Jery 프로젝트 인덱스]]
- [[Work/Jery/작업기록/2026-10-14-Jery-데이터셋-구축과-Hermes-MLflow-수집-방향|초기 데이터셋과 수집 방향]]
- [Jery 저장소](https://github.com/EvoDmiK/Jery)
- [MLflow 등록 모델](https://mlflow.dove-nest.com/#/models/Jery-LinearRouter/versions/1)

이 기록은 실제 실행 보고서, 데이터 manifest, MLflow 업로드·검증 영수증과 현재 Git 상태를 근거로 작성했다.
