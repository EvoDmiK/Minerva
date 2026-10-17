---
created: 2026-10-18
updated: 2026-10-18
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-17-Jery-M4-학습-Gemma-실행과-MLflow-등록]]"
tags:
  - dev
  - draft
  - "jery"
---

# Jery M4 기준 모델 학습, Gemma 실행과 MLflow 등록

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-17-Jery-M4-학습-Gemma-실행과-MLflow-등록]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":27,"데이터":0}

## 1. 개요 및 목적

Hermes에 등록된 MCP 5개·도구 96개를 대상으로 합성 데이터셋 v2를 만들고, Mac mini M4·32GB에서 Jery 선형 기준 모델을 실제로 학습했다. Codex가 데이터·계약·통합을, Claude가 모델·평가를, Antigravity가 독립 데이터 감사를 담당했다. 학습은 2026-10-16에 완료했으며 주말 동안 계속 돌아가는 작업은 아니다.

2026-10-17에는 Gemma 4 E4B 4비트를 MLX로 실행해 소규모 도구 선택을 시험했다. Gemma는 사전학습·지시튜닝된 공개 가중치를 그대로 사용했으며 Jery 데이터로 미세조정하지 않았다. 학습한 Jery 선형 모델과 Gemma 실행 결과는 서로 다른 실험이다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과
- 1. 데이터셋과 공통 계약
- 2. M4 선형 기준 모델 학습
- 평가 결과
- 파일과 재현
- 3. Gemma 4 E4B 4비트 실행
- 4. MLflow 등록과 다운로드 검증
- 5. 검증과 형상 관리
- 6. 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
PYTHONPATH=src python3 -m jery.model.cli --config configs/model/mcp-routing-v2-baseline.json --run-id v2-baseline-20261016 --workers 4
python3 scripts/predict_tool.py --request '삼성전자 지금 주가 확인해줘.'
```

```sh
.venv/bin/python scripts/run_llm_smoke.py
```

## 4. 검증 근거 및 트러블슈팅

| 항목 | 결과 |
|---|---|
| 전체 등록 MCP 분류 데이터 | 서버 5개, 도구 96개, 합성 사례 1,162개 |
| 로컬 기준 모델 | 선형 softmax 학습 완료, 저장·복원·공개 예측 함수 검증 |
| 독립 감사 | 분할 커버리지, 미학습 action, 비선택 사례 부족 등 확인 |
| Gemma 로컬 실행 | E4B 4비트, MLX, 6개 합성 검증 사례로 실행 확인 |
| MLflow 실험 | Gemma 프롬프트 2개, 선형 비교, 학습 결과 등록 |
| 모델·데이터 보존 | Jery-LinearRouter v1, 가중치·v2 데이터·평가·소스 업로드 |
| 운영 범위 | 실제 Hermes 대화 로그를 학습에 사용하지 않았고, 이번 분류 시험에서 MCP 도구를 실행하지 않음 |

| 구분 | 내용 |
|---|---|
| 전체 사례 | 1,162개 |
| 시나리오 그룹 | 340개, 같은 그룹은 같은 분할에 유지 |
| 학습 / 검증 / 평가 | 668 / 248 / 246 |
| 도구 구성 | Grafana 62, Swallow 13, Obsidian 10, Korean Law 10, Kestrel 1 |
| 결정 유형 | select_tools, no_tool, clarify, unsupported |
| 검토 상태 | 모두 needs_human_review |
| 실행 검증 | 모두 execution_verified: false |

- 환경: Apple M4, 통합 메모리 32GB, Python 3.9.6, 외부 Python 의존성 없음.
- 실행 ID: `v2-baseline-20261016`.
- 비교: 검색 기준 24개 + 선형 기준 24개 설정.
- 선택: epochs 20, lr 0.3, l2 0, seed 13, 도구 명세 특징 사용.
- 학습·선택: train만 학습하고 validation으로 설정 선택 후 test 보고.
- 실행 시간: 233.53초, 프로세스 4개·각 스레드 1개.

독립 감사에서는 train에만 있는 도구, 검증·평가의 미학습 action, 작은 no_tool·clarify 표본, 분할별 서버 비율 차이와 후보 개수 단서 등을 확인했다. 새로운 표현과 비Swallow 후보 누락에 대한 일반화는 추가 평가가 필요하다.

- 학습 코드: `src/jery/model/cli.py`, `routers.py`, `features.py`.
- 평가: `src/jery/evaluation/metrics.py`.
- 설정: `configs/model/mcp-routing-v2-baseline.json`.
- 가중치: `models/mcp-routing-v2/v2-baseline-20261016/linear.json.gz`.
- 기본 예측 가중치: `models/mcp-routing-v2/latest/model.json.gz` — 위 선형 모델과 동일한 바이트.
- 결과: `outputs/model/mcp-routing-v2/v2-baseline-20261016/`.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-17-Jery-M4-학습-Gemma-실행과-MLflow-등록]]
- [[Dev/index|Dev 인덱스]]
