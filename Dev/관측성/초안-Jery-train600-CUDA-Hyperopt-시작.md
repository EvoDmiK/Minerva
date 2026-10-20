---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-20-Jery-train600-CUDA-Hyperopt-시작]]"
tags:
  - dev
  - draft
  - "jery"
---

# train600 CUDA Hyperopt 시작

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-20-Jery-train600-CUDA-Hyperopt-시작]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":6,"데이터":0}

## 1. 개요 및 목적

사용자 요청으로 회사 RTX5070Ti에서 고정10개 도구 train600/validation20/test20 전체를 사용한 학습을 시작했다. [Parent 88a5250c](https://mlflow.dove-nest.com/#/experiments/47/runs/88a5250cd54048d8a9593bab7e59d753) 아래 Child5개를 순차 실행한다. 이 문서는 시작 시점 기록이며 완료 결과는 MLflow와 서버 state를 따른다.

Hyperopt TPE5회(startup2), head LR log-uniform1e-5~2e-4. Weight decay0.05, label smoothing0.05, seed3407, batch4/누적1, warmup10 optimizer steps와 linear scheduler를 고정했다. 최대16에폭·최소4에폭·patience3·min_delta0.004다. 600개이므로 epoch당150 optimizer steps다. 매 Child는 pinned 초기 base에서 새로 시작하고 FP16 encoder고정/FP32 head/BF16 autocast를 사용한다. 검증으로 best-trained를 탐색하고 serving은 초기 head보다 엄격히 좋을 때만 교체한다. Test는 탐색에 사용하지 않는다. 데이터와 LR 범위가 함께 바뀌는 탐색이라 순수 데이터 보강 효과의 인과 실험은 아니다.

## 2. 핵심 아키텍처 및 원칙

_작성 필요_

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자 요청으로 회사 RTX5070Ti에서 고정10개 도구 train600/validation20/test20 전체를 사용한 학습을 시작했다. [Parent 88a5250c](https://mlflow.dove-nest.com/#/experiments/47/runs/88a5250cd54048d8a9593bab7e59d753) 아래 Child5개를 순차 실행한다. 이 문서는 시작 시점 기록이며 완료 결과는 MLflow와 서버 state를 따른다.

Hyperopt TPE5회(startup2), head LR log-uniform1e-5~2e-4. Weight decay0.05, label smoothing0.05, seed3407, batch4/누적1, warmup10 optimizer steps와 linear scheduler를 고정했다. 최대16에폭·최소4에폭·patience3·min_delta0.004다. 600개이므로 epoch당150 optimizer steps다. 매 Child는 pinned 초기 base에서 새로 시작하고 FP16 encoder고정/FP32 head/BF16 autocast를 사용한다. 검증으로 best-trained를 탐색하고 serving은 초기 head보다 엄격히 좋을 때만 교체한다. Test는 탐색에 사용하지 않는다. 데이터와 LR 범위가 함께 바뀌는 탐색이라 순수 데이터 보강 효과의 인과 실험은 아니다.

Parent 데이터 등록 중 회사 PC 인터넷이 끊겨 준비 작업이 timeout됐다. 당시 Child는0개였다. 사용자 재연결 후 프로세스 종료와 기존 state를 확인해 같은 Parent로 준비를 재실행했고 새 Parent를 만들지 않았다. detached supervisor PID208808을 시작했다.

첫 Child는 4a01c09c5a2c4edaa2b341d415901a39, LR1.4392629715379414e-5다. 실제 CUDA step1050 및 MLflow의 epoch1~6 동기화를 확인했다. 초기 validation60%, epoch1~5는55%, epoch6은60%였다. 이후9에폭까지 학습했고 serving selected_epoch0 / test45% 기록을 확인했다. 이 첫 조건은 baseline을 넘지 못해 초기 head를 유지했다. 이 시점 Child는 업로드/최종화 중으로 RUNNING이었으며5회 전체 완료 결과가 아니다.

MLflow 필수 params5개·metrics7개만 트래킹하고 설정·상세 에폭/스텝·평가·출처는 JSON Artifacts로 기록한다. best-trained head와 serving 모델을 별도 보존하고, 완료 시 모델 업로드·해시 검증을 수행하는 기존 supervisor다. 다른 GPU 작업을 중단하거나 변경하지 않았다. SSH와 분리된 세션에서 다음 trials를 이어 실행한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-20-Jery-train600-CUDA-Hyperopt-시작]]
- [[Dev/index|Dev 인덱스]]
