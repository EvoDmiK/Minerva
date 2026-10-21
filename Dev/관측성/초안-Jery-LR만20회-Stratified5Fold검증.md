---
created: 2026-10-21
updated: 2026-10-21
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-21-Jery-LR만20회-Stratified5Fold검증]]"
tags:
  - dev
  - draft
  - "jery"
---

# LR-only20회와 stratified grouped5-fold — 2026-10-21

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-21-Jery-LR만20회-Stratified5Fold검증]] · 분류 근거 {"인프라":2,"자동화":0,"관측성":3,"데이터":0}

## 1. 개요 및 목적

사용자가 비-LR 조건을 고정하고 LR1e-3~5e-3만 탐색하되 검증을 Stratified K-Fold로 요청했다. 직전 공동 탐색 Parent3b7fd13fe2f74146a520fa64d0c2305d는20회 전부 FINISHED임을 확인했다.

직전 공동 탐색에서 best-trained validation accuracy가 가장 높은 run c0635c4ce7c44e97aad5e9f695516a0b(0.85)를 기준으로 비-LR 조건을 고정했다. Test는 이 선택에 사용하지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 고정 조건과 탐색
- 검증과 데이터
- 구현과 검증
- 실행
- 실행 등록

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
python3 scripts/build_laya_stratified_folds.py \
 --source outputs/laya-ten-tools-training-v3-final-20261020/augmented \
 --output outputs/laya-ten-tools-stratified5-20261021 --n-splits 5 --seed 3407
TORCHINDUCTOR_COMPILE_THREADS=4 PYTHONPATH=src /home/persona-ai/envs/jery-cuda/bin/python scripts/run_laya_cv_experiment.py \
 --plan configs/training/laya-ten-tools-train600-lr-only-cv5-20261021.json \
 --model-config configs/training/laya-ten-tools-train600-lr-only-cv5-model-20261021.json \
 --state-dir outputs/laya-ten-tools-train600-lr-only-cv5-20261021/tracking \
 --python /home/persona-ai/envs/jery-cuda/bin/python --detach
```

## 4. 검증 근거 및 트러블슈팅

사용자가 비-LR 조건을 고정하고 LR1e-3~5e-3만 탐색하되 검증을 Stratified K-Fold로 요청했다. 직전 공동 탐색 Parent3b7fd13fe2f74146a520fa64d0c2305d는20회 전부 FINISHED임을 확인했다.

직전 공동 탐색에서 best-trained validation accuracy가 가장 높은 run c0635c4ce7c44e97aad5e9f695516a0b(0.85)를 기준으로 비-LR 조건을 고정했다. Test는 이 선택에 사용하지 않았다.

원래 train600만 CV pool이다. 각 fold480train/120validation, 도구당48/12.355개 scenario group 누수0, 전체600개 validation coverage1회, original test20 byte 보존. Original validation20은 CV에 사용하지 않는다. 모든20 LR trial이 같은 고정5-fold를 사용한다. 총100회 모델 학습으로 기존 단일 split20회보다 학습량이 늘어난다.

Test20은 각 fold head 최종 평가에만 쓰고 TPE/epoch 선택에는 쓰지 않는다. Trial test값은5개 fold-trained 모델 결과의 평균이며 full600 단일 모델 성능이 아니다. Trial val 평균·sample std와 각 fold별 지표/모델을 MLflow3단계 구조로 남긴다. Primary selection은 cv_search_accuracy(5개 fold best-trained validation accuracy 평균)다. 상세 metrics 의미는 계약을 따른다.

테스트는 실제tool alias 복원·층화 균형·group/ID 누수 방지·전체 OOF coverage·heldout bytes·원본 보존·출력 덮어쓰기 거부·설정 drift 거부·LR-only 계획·test와 TPE 분리·학습 export override를 검증한다. 전체 테스트181개 PASS, LR-only8개 실제 Hyperopt 후보의 비-LR 불변식 검증 PASS, 기존 데이터 validator PASS. Graphify AST update 수행. 추가 의존성 없음.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-21-Jery-LR만20회-Stratified5Fold검증]]
- [[Dev/index|Dev 인덱스]]
