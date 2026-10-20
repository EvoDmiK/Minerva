---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-정규화-재학습]]"
tags:
  - dev
  - draft
  - "jery"
---

# 10개 도구 파라미터 수정과 재학습

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-정규화-재학습]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":2,"데이터":0}

## 1. 개요 및 목적

사용자가 파라미터를 수정해 다시 학습하도록 요청했다. 기존 Parent c328674ecd9c4eabb1bf3d4dbc6c9dde는 마지막 모델 업로드 복구를 마쳐 5개 Child와 Parent 모두 완료됐다. 새 실험은 별도 Parent에서 진행한다.

이전 train/validation 곡선을 근거로 과적합 억제 설정을 탐색한다. 5번 Child는 epoch 15 train 90%·validation 65%였지만 epoch 25 train 100%·validation 55%, 마지막 validation 50%였다. Test 점수로 탐색 범위나 후보를 정하지 않는다.

## 2. 핵심 아키텍처 및 원칙

- 변경 이유와 설정
- MLflow와 실행
- 코드와 재현

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

이전 train/validation 곡선을 근거로 과적합 억제 설정을 탐색한다. 5번 Child는 epoch 15 train 90%·validation 65%였지만 epoch 25 train 100%·validation 55%, 마지막 validation 50%였다. Test 점수로 탐색 범위나 후보를 정하지 않는다.

Hyperopt TPE 5회. seed 3407, microbatch 4·누적 1, 선형 LR 감소, frozen FP16 encoder·FP32 routing head·BF16 autocast를 유지한다. 모든 trial은 원 base에서 새로 시작한다. 기존 10개 도구와 train/validation/test 60/20/20도 동일하다. 데이터 hermes-ten-tools-v1, catalog hermes-ten-tools-b4648cc19a90, 계약 decision-export-v2다.

여러 설정을 동시에 바꾸는 탐색이므로 개별 변수의 인과 효과는 주장하지 않는다. 작은 미검토 합성 데이터이며 실제 일반화 성능은 별도 확인해야 한다.

Child 표의 val 값은 마지막 epoch다. 선택된 head의 검증 값은 report.json과 선택 epoch tag, Parent best_val_accuracy로 확인한다. 최종 test는 선택된 head에 대해 측정하며 검색 점수로 쓰지 않는다.

회사 persona-ai Linux RTX 5070 Ti에서 supervisor PID 202417로 시작했다. 다른 GPU 작업은 유지하고 Mac에서 학습하지 않는다. 데이터·계약 검증과 CUDA 계획 테스트 4개, CUDA 모델 테스트 15개를 통과했다. 제품 코드 변경은 없고 기존 구현을 사용한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-정규화-재학습]]
- [[Dev/index|Dev 인덱스]]
