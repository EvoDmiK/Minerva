---
created: 2026-10-25
updated: 2026-10-25
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-24-Jery-OOF오류분석과-seed재검증]]"
tags:
  - dev
  - draft
  - "jery"
---

# OOF 오류 분석과 seed 재검증

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-24-Jery-OOF오류분석과-seed재검증]] · 분류 근거 {"인프라":0,"자동화":1,"관측성":7,"데이터":0}

## 1. 개요 및 목적

기준·최고 설정의 OOF 예측 600개를 비교했고, 같은 5개 fold에서 3개 seed로 재검증하는 실험을 시작했다. 실제 요청 평가셋은 후보 13개·사람 검토 완료 0개여서 준비 단계다.

분석 대상은 [완료된 LR 고정 실험](https://mlflow.dove-nest.com/#/experiments/47/runs/d9636e10f0b6449dbf6975e945e07aad)의 기준 trial1과 최고 trial9다. 각 fold에서 선택된 head의 저장 예측을 원래 validation 정답에 연결했다. 입력·fold 해시, ID별 1회 포함, 후보 안의 선택, report 정확도 일치를 검사했다.

## 2. 핵심 아키텍처 및 원칙

- 완료 실험에서 확인한 차이
- 먼저 검토할 오류
- 실행 중인 재검증
- 독립 test 준비 상태
- 코드와 검증
- 재현과 파일 위치
- 실행 확인 · 2026-10-24 14:06 KST

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
/home/persona-ai/envs/jery-cuda/bin/python scripts/run_laya_cv_experiment.py \
  --plan configs/training/laya-ten-tools-seed-confirmation-cv5-20261024.json \
  --model-config configs/training/laya-ten-tools-seed-confirmation-cv5-20261024-model.json \
  --state-dir outputs/laya-ten-tools-seed-confirmation-cv5-20261024/tracking \
  --python /home/persona-ai/envs/jery-cuda/bin/python --detach

python3 scripts/compare_laya_cv_errors.py \
  --state-dir outputs/laya-ten-tools-fixedlr-params-cv5-20261022/tracking \
  --output outputs/laya-oof-review-new
```

## 4. 검증 근거 및 트러블슈팅

기준·최고 설정의 OOF 예측 600개를 비교했고, 같은 5개 fold에서 3개 seed로 재검증하는 실험을 시작했다. 실제 요청 평가셋은 후보 13개·사람 검토 완료 0개여서 준비 단계다.

정답은 순증 12개, 정확도는 2.0%p 개선됐다. fold별 정확도 변화는 +3.33, +5.00, −1.67, +4.17, −0.83%p다. 5개 중 3개에서 개선했으며 seed가 바뀌어도 개선되는지는 새 실험으로 확인한다. 이 데이터는 설정·epoch 선택에 사용한 합성 검증 자료이므로 독립 일반화 성능이 아니다.

vault 정답은 60개 중 26→30개, edit는 38→44개로 개선했지만 여전히 취약하다. bases·backtest·price_history·order는 정답 수가 소폭 줄었다. 파라미터 하나로 모든 도구가 함께 좋아진 결과는 아니다.

`cases.jsonl`에 요청·이전 맥락·정답·두 예측·fold·scenario ID·개선/퇴보 구분을 남겼다. 공통 오답 104개를 먼저 검토하고, 요청과 맥락이 충분한지, 라벨이 명세와 맞는지 확인하는 것이 다음 순서다. 기준·최고 조건의 10개 fold 보고서에서 입력 잘림은 모두 0건이었다. 따라서 현재 오류를 입력 잘림으로 설명할 근거는 없다. 모델이 틀렸다는 이유로 라벨을 자동 수정하지 않았다.

실험 이름은 `laya-ten-tools-seed-confirmation-cv5-20261024`다. `Parent → 설정·seed 6개 → fold 5개`로 기록하며, 총 **30회 학습**을 순차 실행한다. seed3407도 새로 실행해 이전 결과의 재현성을 확인한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-24-Jery-OOF오류분석과-seed재검증]]
- [[Dev/index|Dev 인덱스]]
