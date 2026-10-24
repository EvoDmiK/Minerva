---
created: 2026-10-25
updated: 2026-10-25
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-24-Jery-seed30회-완료와-성능개선제안]]"
tags:
  - dev
  - draft
  - "jery"
---

# 설정 검증 정리와 성능 개선 순서

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-24-Jery-seed30회-완료와-성능개선제안]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":2,"데이터":0}

## 1. 개요 및 목적

**3개 seed × 2개 설정 × 5-fold, 총 30회가 완료됐다.** 최고 설정은 모든 seed에서 validation F1이 개선됐지만, 기존 test20에서는 일관된 개선이 없었다. 다음 실험은 오류 경계의 데이터 품질과 도구 설명을 우선 확인한다.

아래 값은 각 seed의 5-fold 평균이다. [MLflow 실험](https://mlflow.dove-nest.com/#/experiments/47/runs/af613b715d804393b17872be8d5ad671)에서 원본 결과를 확인할 수 있다.

## 2. 핵심 아키텍처 및 원칙

- 완료 결과
- 이번 리팩토링
- 성능 개선 우선순위
- 다음 실험의 범위

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
PYTHONPATH=src python -m unittest discover -s tests/integration -p test_cuda_experiment_plan.py
PYTHONPATH=src python -m unittest discover -s tests/integration -p test_cv_experiment.py
PYTHONPATH=src python -m unittest discover -s tests/integration -p test_full_tracking.py
python3 scripts/validate_dataset.py
```

## 4. 검증 근거 및 트러블슈팅

**3개 seed × 2개 설정 × 5-fold, 총 30회가 완료됐다.** 최고 설정은 모든 seed에서 validation F1이 개선됐지만, 기존 test20에서는 일관된 개선이 없었다. 다음 실험은 오류 경계의 데이터 품질과 도구 설명을 우선 확인한다.

아래 값은 각 seed의 5-fold 평균이다. [MLflow 실험](https://mlflow.dove-nest.com/#/experiments/47/runs/af613b715d804393b17872be8d5ad671)에서 원본 결과를 확인할 수 있다.

| Seed | 기준 Val F1 | 최고 Val F1 | 변화 | 기준 Test F1 | 최고 Test F1 |
|---|---:|---:|---:|---:|---:|
| 3407 | 0.7443 | 0.7643 | +0.0200 | 0.6453 | 0.6453 |
| 3408 | 0.7268 | 0.7496 | +0.0228 | 0.6374 | 0.6573 |
| 3409 | 0.7314 | 0.7608 | +0.0294 | 0.6307 | 0.5893 |
| 평균 | **0.7342** | **0.7582** | **+0.0241** | **0.6378** | **0.6306** |

평균 validation 정확도는 73.83%→76.17%다. 최고 설정은 validation 기준 후속 비교의 기준점으로 사용할 만하다. 다만 기존 test는 20개이고 반복 관찰했으므로 실제 요청 성능이나 통계적 유의성을 주장하지 않는다. 동일 자료·서로 겹치는 학습 fold에서 나온 15개 점수를 독립 표본 15개로 취급하지 않는다.

선택된 checkpoint의 train 정확도는 기준 설정에서 seed별 90.42%·94.04%·92.38%, 최고 설정에서 95.17%·90.04%·88.75%였다. 대응 validation 정확도는 73.17~76.83%다. 일반화 격차가 있으므로 epoch나 LR을 더 높이는 것을 우선하지 않는다. 이것만으로 한국어 표현력이나 특정 구조가 원인이라고 단정할 수는 없다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-24-Jery-seed30회-완료와-성능개선제안]]
- [[Dev/index|Dev 인덱스]]
