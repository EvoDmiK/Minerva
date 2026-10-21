---
created: 2026-10-21
updated: 2026-10-21
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-21-Jery-MLflow비교params-완료검증오류-복구]]"
tags:
  - dev
  - draft
  - "jery"
---

# MLflow 비교 params 추가 후 supervisor 중단 복구 — 2026-10-21

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-21-Jery-MLflow비교params-완료검증오류-복구]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":4,"데이터":0}

## 1. 개요 및 목적

사용자가 공동 탐색 표가 멈춰 있다고 보고했다. 서버에서 Parent3b7fd13fe2f74146a520fa64d0c2305d의 supervisor226349가 종료됐고 state는 supervisor_failed임을 확인했다. Child1~9는 finished, Child10 f599948302284d26ab2a7a66173d2379는 uploading에서 멈췄다.

Child10의 실제 CUDA 학습은17epoch/2550steps, 2026-10-21 01:47:11 UTC에 succeeded로 종료했다. Report·head·원본 config/source가 보존돼 있다. 선택 epoch11의 test accuracy0.65/F1 0.56도 이미 기록했다. 03:24 UTC 확인 시 supervisor는 죽어 있었고 예외는 `Nonessential MLflow keys were logged, or required keys are missing`였다.

## 2. 핵심 아키텍처 및 원칙

- 원인과 수정
- 복구 원칙과 재현

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
TORCHINDUCTOR_COMPILE_THREADS=4 PYTHONPATH=src /home/persona-ai/envs/jery-cuda/bin/python scripts/run_laya_full_experiment.py \
 --python /home/persona-ai/envs/jery-cuda/bin/python \
 --model-config configs/training/laya-ten-tools-train600-joint20-model-20261021.json \
 --state-dir outputs/laya-ten-tools-train600-joint20-20261021/tracking --detach
```

## 4. 검증 근거 및 트러블슈팅

사용자가 공동 탐색 표가 멈춰 있다고 보고했다. 서버에서 Parent3b7fd13fe2f74146a520fa64d0c2305d의 supervisor226349가 종료됐고 state는 supervisor_failed임을 확인했다. Child1~9는 finished, Child10 f599948302284d26ab2a7a66173d2379는 uploading에서 멈췄다.

Child10의 실제 CUDA 학습은17epoch/2550steps, 2026-10-21 01:47:11 UTC에 succeeded로 종료했다. Report·head·원본 config/source가 보존돼 있다. 선택 epoch11의 test accuracy0.65/F1 0.56도 이미 기록했다. 03:24 UTC 확인 시 supervisor는 죽어 있었고 예외는 `Nonessential MLflow keys were logged, or required keys are missing`였다.

비교용5개 optimizer params를 기존 Child에 backfill했지만 기존 supervisor의 완료 검증은 예전 plan의5개 params와 정확히 같은 key 집합만 허용했다. 실제10개를 만나 실패했다. 파라미터 표시 확장 때 post-upload 완료 검증 경로를 갱신하지 못한 코드 결함이다.

`scripts/run_laya_full_experiment.py`의 완료 key 검증을 `validate_logged_keys`로 분리하고 plan의 필수 params는 계속 요구하되 승인된 COMPARISON_PARAMS5개만 추가 허용한다. Unknown params·필수 누락·metrics 추가/누락은 계속 거부한다. 새 plan에서 비교 params를 필수로 선언했으면 누락을 허용하지 않는다. 실제 실패 Child의 remote params/metrics도 새 검증을 통과했다.

회귀 테스트는 legacy5개/보강10개/신규10개를 정상으로, unknown·core 누락·metric 추가/누락·새 plan의 비교 param 누락을 오류로 검증한다. Tracking 통합14개 PASS, 원본 데이터 검증 PASS(130examples/10tools/65isolated scenarios). Graphify AST update를 수행한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-21-Jery-MLflow비교params-완료검증오류-복구]]
- [[Dev/index|Dev 인덱스]]
