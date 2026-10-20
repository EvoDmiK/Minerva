---
created: 2026-10-20
updated: 2026-10-20
project: Jery
type: worklog
tags: [jery, training, hyperopt, cuda, mlflow]
---

# train600 CUDA Hyperopt 시작

사용자 요청으로 회사 RTX5070Ti에서 고정10개 도구 train600/validation20/test20 전체를 사용한 학습을 시작했다. [Parent 88a5250c](https://mlflow.dove-nest.com/#/experiments/47/runs/88a5250cd54048d8a9593bab7e59d753) 아래 Child5개를 순차 실행한다. 이 문서는 시작 시점 기록이며 완료 결과는 MLflow와 서버 state를 따른다.

Hyperopt TPE5회(startup2), head LR log-uniform1e-5~2e-4. Weight decay0.05, label smoothing0.05, seed3407, batch4/누적1, warmup10 optimizer steps와 linear scheduler를 고정했다. 최대16에폭·최소4에폭·patience3·min_delta0.004다. 600개이므로 epoch당150 optimizer steps다. 매 Child는 pinned 초기 base에서 새로 시작하고 FP16 encoder고정/FP32 head/BF16 autocast를 사용한다. 검증으로 best-trained를 탐색하고 serving은 초기 head보다 엄격히 좋을 때만 교체한다. Test는 탐색에 사용하지 않는다. 데이터와 LR 범위가 함께 바뀌는 탐색이라 순수 데이터 보강 효과의 인과 실험은 아니다.

Parent 데이터 등록 중 회사 PC 인터넷이 끊겨 준비 작업이 timeout됐다. 당시 Child는0개였다. 사용자 재연결 후 프로세스 종료와 기존 state를 확인해 같은 Parent로 준비를 재실행했고 새 Parent를 만들지 않았다. detached supervisor PID208808을 시작했다.

첫 Child는 4a01c09c5a2c4edaa2b341d415901a39, LR1.4392629715379414e-5다. 실제 CUDA step1050 및 MLflow의 epoch1~6 동기화를 확인했다. 초기 validation60%, epoch1~5는55%, epoch6은60%였다. 이후9에폭까지 학습했고 serving selected_epoch0 / test45% 기록을 확인했다. 이 첫 조건은 baseline을 넘지 못해 초기 head를 유지했다. 이 시점 Child는 업로드/최종화 중으로 RUNNING이었으며5회 전체 완료 결과가 아니다.

MLflow 필수 params5개·metrics7개만 트래킹하고 설정·상세 에폭/스텝·평가·출처는 JSON Artifacts로 기록한다. best-trained head와 serving 모델을 별도 보존하고, 완료 시 모델 업로드·해시 검증을 수행하는 기존 supervisor다. 다른 GPU 작업을 중단하거나 변경하지 않았다. SSH와 분리된 세션에서 다음 trials를 이어 실행한다.

서버 상태: outputs/laya-ten-tools-train600-20261020/tracking/state.json
설정: configs/training/laya-ten-tools-train600-20261020.json 및 laya-ten-tools-train600-model-20261020.json
설명: docs/data/ten-tool-train600-20261020.md
실행 코드 기준 커밋 ce638ba, 시작 문서3af6a02, README47e8829까지 dev-codex에 커밋·푸시했다. 서버의 실행 코드는 ce638ba이며 후속 커밋은 문서뿐이다.

기존 데이터 검증 PASS, CUDA 계획 통합 테스트5개와 새 명시 계획 검증 PASS. native format audit은600/20/20에서 누락·잘림·특징/정답 불일치0이었다. 합성 AI 검토 정답이며 사람 검토와 실제 요청 독립 평가가 남아 있다.

## 후속 상태 확인

첫 Child 4a01c09c5a2c4edaa2b341d415901a39는9에폭 종료 후 모델·상세 결과 등27개 Artifact의 업로드 검증까지 마쳐 finished 상태다. 최고 trained validation60%로 초기60%를 넘지 못했고 selected_epoch0을 유지했다. 두 번째 Child 3c1d2aad62ff40878078ee0b97a04ca5가 자동 생성돼 running 상태임을 확인했다. Parent는running, error/tracking_error는없었다. 전체5회 완료가 아니다. 로컬 outputs/laya-ten-tools-train600-20261020/server-state-snapshot.json에 서버 상태 사본을 남겼다.
