---
created: 2026-10-22
updated: 2026-10-22
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-22-Jery-LR고정-기준1회-파라미터탐색19회]]"
tags:
  - dev
  - draft
  - "jery"
---

# LR 고정 · 학습 파라미터 탐색

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-22-Jery-LR고정-기준1회-파라미터탐색19회]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":7,"데이터":0}

## 1. 개요 및 목적

지정한 run의 설정으로 첫 조건을 학습하고, 나머지 19개 조건은 LR을 고정한 채 다른 학습 파라미터를 탐색한다. 기존과 동일한 층화·시나리오 그룹 보존 5-fold를 사용한다.

[새 MLflow 실험](https://mlflow.dove-nest.com/#/experiments/47/runs/d9636e10f0b6449dbf6975e945e07aad) · 실행 코드 `94f6364`

## 2. 핵심 아키텍처 및 원칙

- 기준 모델
- 나머지 19개 조건
- 데이터와 MLflow
- 실행 자료
- 검증 결과

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
TORCHINDUCTOR_COMPILE_THREADS=4 PYTHONPATH=src \
  /home/persona-ai/envs/jery-cuda/bin/python scripts/run_laya_cv_experiment.py \
  --plan configs/training/laya-ten-tools-fixedlr-params-cv5-20261022.json \
  --model-config configs/training/laya-ten-tools-fixedlr-params-cv5-20261022-model.json \
  --state-dir outputs/laya-ten-tools-fixedlr-params-cv5-20261022/tracking \
  --python /home/persona-ai/envs/jery-cuda/bin/python --detach
```

## 4. 검증 근거 및 트러블슈팅

- 합성 train 600개 → fold마다 학습 480개 / 검증 120개.
- 조건 20개 × fold 5개 = **총 100회 학습**. 원래 validation 20개는 사용하지 않는다.
- MLflow 구조는 **Parent → 조건 20개 → 조건별 fold 5개**.
- 탐색은 fold별 best-trained validation accuracy의 평균으로 결정한다. Test는 선택에 사용하지 않는다.
- Trial의 test 점수는 5개 fold 모델의 평균이며, 전체 600개로 학습한 단일 모델의 점수가 아니다.
- 핵심·비교 파라미터 10개와 필수 지표를 표에 남기고, 전체 설정과 상세 이력은 JSON Artifact에 저장한다.

과거 test 결과를 반복 관찰한 데이터와 사용자 지정 기준을 활용한 탐색이다. 실제 사용 성능이나 독립적인 최종 평가로 해석하지 않는다.

- [학습 계획](https://github.com/EvoDmiK/Jery/blob/dev-codex/configs/training/laya-ten-tools-fixedlr-params-cv5-20261022.json)
- [기준 모델 설정](https://github.com/EvoDmiK/Jery/blob/dev-codex/configs/training/laya-ten-tools-fixedlr-params-cv5-20261022-model.json)
- [CV 실행기](https://github.com/EvoDmiK/Jery/blob/dev-codex/scripts/run_laya_cv_experiment.py)
- [교차 검증 계약](https://github.com/EvoDmiK/Jery/blob/dev-codex/docs/contracts/laya-cross-validation-v1.md)

서버에서 CV 5개·tracking 15개·계획 6개 테스트가 모두 통과했다. 실제 Hyperopt 후보 20개를 생성해 다음을 확인했다.

- 첫 후보가 지정 run의 설정과 일치.
- 나머지 19개 후보도 LR이 정확히 동일하며 기준 조합 전체의 반복은 제외.
- 유효 배치와 실제 학습 override·MLflow 값 일치.
- Test 값을 바꿔도 다음 후보가 동일.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-22-Jery-LR고정-기준1회-파라미터탐색19회]]
- [[Dev/index|Dev 인덱스]]
