---
created: 2026-10-18
updated: 2026-10-18
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-18-Jery-Laya-균형학습-Hyperopt-콜백과-MLflow]]"
tags:
  - dev
  - draft
  - "jery"
---

# Jery Laya 균형 학습, Hyperopt 탐색과 검증 콜백

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-18-Jery-Laya-균형학습-Hyperopt-콜백과-MLflow]] · 분류 근거 {"인프라":1,"자동화":1,"관측성":11,"데이터":0}

## 1. 개요 및 목적

2026-10-18 10:47 KST 확인 기준이다. 학습은 완료되지 않았다. Hyperopt 첫 trial은 **4/64에폭 완료, 8,697 optimizer step**이며 5번째 에폭 학습 중이다. 최신 완료 에폭의 검증 사례 정확도는 7.26%다. 이는 최종 선택 모델의 성능이 아니다. 검증 기준으로 선택한 head와 최종 결과는 학습 종료 후 MLflow report에서 확인한다.

- [현재 Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/9325d1ca84944fe281f94b519c59f305)
- [첫 Hyperopt Child](https://mlflow.dove-nest.com/#/experiments/47/runs/bb1c80ea642040878a392833ea2cadd1)
- 실행 상태 원본 확인 시각(UTC): `2026-10-18T01:47:40.705302+00:00`
- 저장소 검증: 전체 테스트 **109개 통과**, v1/v2 데이터 검증과 staged diff 검사 통과.
- 형상 관리: [커밋 f135208](https://github.com/EvoDmiK/Jery/commit/f135208a6eeade7b33c286360f366b6b4157bfc1), `dev-codex` 커밋·푸시 완료. 푸시 후 원격과 동기화 및 깨끗한 작업 트리를 확인했다.

## 2. 핵심 아키텍처 및 원칙

- 기록 시점과 현재 진행
- 이전 실험에서 확인한 문제
- 데이터와 균형
- 콜백 정책
- Hyperopt
- 한국어·영어 진단
- 실행·검증
- 코드·문서와 관련 기록

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
DECISION_PYTHON=/Volumes/Dove-Nest-SSD/app-data/orca/kimdove/home/workspaces/Jery/main/tmp/venv-decision/bin/python
"$DECISION_PYTHON" scripts/run_laya_full_experiment.py \
  --python "$DECISION_PYTHON" \
  --state-dir outputs/laya-balanced-20261018/tracking \
  --model-config configs/model/laya-balanced-20261018.json --detach
```

## 4. 검증 근거 및 트러블슈팅

2026-10-18 10:47 KST 확인 기준이다. 학습은 완료되지 않았다. Hyperopt 첫 trial은 **4/64에폭 완료, 8,697 optimizer step**이며 5번째 에폭 학습 중이다. 최신 완료 에폭의 검증 사례 정확도는 7.26%다. 이는 최종 선택 모델의 성능이 아니다. 검증 기준으로 선택한 head와 최종 결과는 학습 종료 후 MLflow report에서 확인한다.

- [현재 Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/9325d1ca84944fe281f94b519c59f305)
- [첫 Hyperopt Child](https://mlflow.dove-nest.com/#/experiments/47/runs/bb1c80ea642040878a392833ea2cadd1)
- 실행 상태 원본 확인 시각(UTC): `2026-10-18T01:47:40.705302+00:00`
- 저장소 검증: 전체 테스트 **109개 통과**, v1/v2 데이터 검증과 staged diff 검사 통과.
- 형상 관리: [커밋 f135208](https://github.com/EvoDmiK/Jery/commit/f135208a6eeade7b33c286360f366b6b4157bfc1), `dev-codex` 커밋·푸시 완료. 푸시 후 원격과 동기화 및 깨끗한 작업 트리를 확인했다.

기존 고정 64에폭 Parent의 첫 LR 1e-4 Child는 완료됐지만 최종 검증 정확도 10.08%, 평가 정확도 8.54%였다. 학습 전 검증 정확도 16.13%보다 낮았고, 학습 손실 감소와 검증 손실 증가가 함께 나타났다. 과적합 및 창 라벨 불균형을 의심할 근거다. 두 번째 Child는 체크포인트와 기록을 보존하고 중단했으며 세 번째 설정은 시작하지 않았다. 기존 실험을 수정 완료나 성능 개선 결과로 재해석하지 않는다.

원본 `mcp-routing-v2`와 `decision-export-v1` 파일은 수정하지 않는다. 원본 668/248/246건과 전체 후보를 덮는 4,172/1,592/1,577개 창을 유지한다. 학습에서만 정답 bucket을 참조해 결정적 oversampling을 적용하며, 정답 필드를 모델 입력 특징으로 사용하지 않는다. 검증·평가에는 oversampling을 적용하지 않는다.

`clarify`는 필요한 대상·맥락이 부족하여 사용자 확인이 필요하다는 정답이다. 모델 확신이 낮다는 이유로 이 라벨을 만들지 않는다. `window_none`은 현재 창에 적합한 도구가 없다는 뜻이며 전체 후보에서 처리 불가인 `unsupported`와 구분한다. 기존 label-blind 다중 창 집계와 외부 예측 계약은 유지한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-18-Jery-Laya-균형학습-Hyperopt-콜백과-MLflow]]
- [[Dev/index|Dev 인덱스]]
