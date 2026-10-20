---
created: 2026-10-19
date: 2026-10-19
project: Jery
type: worklog
status: completed
tags:
  - worklog
  - jery
  - laya
  - cuda
  - training
  - mlflow
---
# Jery routing v2 공동 수정과 재학습

사용자 요청에 따라 기존 Mac·CUDA 학습을 중단하고 결과와 가중치를 보존했다. 새 정책의 전체 데이터 CUDA 재학습은 통합 검증 후 시작한다.

## 종료한 실행

- Mac Parent: `9325d1ca84944fe281f94b519c59f305`
- CUDA Parent: `29552487a8a94b10ad942d9bbc331953`
- 두 Parent의 MLflow 상태 `KILLED`, 로컬 supervisor 종료 및 전용 학습 프로세스 종료 확인.
- 다른 회사 GPU 작업은 유지했다. 중단 증거 JSON은 기존 Parent의 `control/stopped-for-routing-v2.json`에 업로드하고 해시를 검증했다.

## 원인과 수정

기존 동일 test 점수는 같은 초기 head를 최종 선택한 결과였다. validation 248개 요청 중 232개는 도구 선택이지만, 1,592개 후보 창 중 1,305개는 `window_none`이었다. Mac 첫 trial에서 정답 도구 창 정확도가 26.81%→1.70%로 떨어지는 동안 전체 창 정확도는 8.79%→78.96%로 올랐다. 창 loss와 최종 요청 선택 성능이 다른 방향으로 움직였다. 한국어 성능이 주원인이라고 단정하지 않는다.

Claude는 `dev-claude`의 `b3ea679`로 weighted soft CE와 학습 head 선택 정책을 구현하고 푸시했다. Codex는 `2480f06`으로 통합했다. Claude의 후속 읽기 전용 검토에서 차단 문제는 없었다.

- `window_none` loss 가중치 1.0/0.5/0.25를 비교하며 원래 모든 창·분할·기존 oversampling을 유지한다.
- train 평균 가중치 1.0/0.8/0.7로 정규화한다. validation/test는 통계 계산에 쓰지 않는다.
- best trained(epoch≥1)·serving selected·last trained를 분리한다.
- Hyperopt 목적값은 최고 trained validation 점수로 계산하며 baseline 점수로 올림하지 않는다.
- serving은 최고 trained가 baseline을 넘을 때만 교체한다.
- min_epochs 10, trained-only patience 5, min_delta 0.004. 최초 제어 실험은 세 조건 각 10에폭이며 64에폭 Hyperopt를 실행 중이라고 보고하지 않는다.
- prepared configuration과 실행 configuration 일치 검사를 보강했다.

AGY는 독립 감사 도구·입력 격리·이식성 보강을 `dev-agy`의 `1e5610f`·`08a7c3d`·`e7a7655`로 커밋·푸시했다. 실제 CUDA 10에폭 smoke의 독립 감사도 PASS했다. Codex는 생성된 대형 JSON을 제외한 최종 변경만 `275fee1`로 통합·푸시하고 서버에 반영했다. 통합 후 전체 테스트 132개 및 데이터 검증을 통과했다. 실제 협업은 Orca Run `run_e483b51bc37f`에서 Claude·Antigravity와 진행했고 모든 담당 작업은 succeeded로 종료했다.

## 검증

전체 저장소 테스트 123개 및 v1 130건·v2 1,162건 데이터 검증을 통과했다. 소규모 CUDA fixture에서 10에폭·30스텝을 완료했다. 가중치 0.25/평균 0.7, 최고 학습 head epoch 1과 serving baseline epoch 0의 별도 저장, 재로딩 확률 차이 0, frozen encoder 불변을 확인했다. 소규모 fixture는 코드 검증용이며 모델 품질 향상 근거가 아니다.

별도 출력 경로에서 native checkpoint의 global step 및 optimizer state가 30→31로 이어졌다. 원본 checkpoint 파일 해시는 모두 보존됐다.

Codex 통합 실행 보강 커밋 `fe805c4`는 `origin/dev-codex`에 푸시하고 회사 CUDA 서버에 반영했다. 코드·계약·재현 명령은 `docs/data/laya-routing-v2-20261019.md`와 `docs/contracts/laya-training-result-v2.md`를 따른다.

## 새 실행

2026-10-19 14:24 KST에 회사 RTX 5070 Ti에서 전체 CUDA 학습을 시작했다. 새 [Jery Parent `bc61fce284ae468e8b7022508f36e819`](https://mlflow.dove-nest.com/#/experiments/47/runs/bc61fce284ae468e8b7022508f36e819), 첫 [Child `18dc59a3819d42739340f20890702b08`](https://mlflow.dove-nest.com/#/experiments/47/runs/18dc59a3819d42739340f20890702b08)는 모두 RUNNING이다. 첫 조건은 window_none 가중치 1.0이며 이후 0.5·0.25를 순차 실행한다. supervisor PID 176131, 학습 PID 176205에서 실제 optimizer step 128 이상과 유한한 loss·gradient를 확인했다. 코드 기준은 `275fee1`; native Unsloth CUDA 환경은 `requirements-decision-cuda.txt`를 따른다. Mac 학습은 재시작하지 않았다. 첫 에폭 지표는 실제 validation 완료 후 기록한다. 데이터 및 readiness JSON 다섯 개는 Parent에 업로드하고 GET 재조회 SHA-256을 확인했다. 전체 데이터는 source train/validation/test 668/248/246개, 후보 창 4,172/1,592/1,577개다. 필수 Child params 4개·metrics 7개만 기록하며 상세 설정·진단·실행 근거는 JSON artifact에 저장한다. 데이터와 가중치는 Git에 넣지 않는다.

합성 정답은 미검토 상태이며 실제 사용 정확도나 성능 개선을 주장하지 않는다.


## 후속 변경 — 낮은 LR·가중치 공동 탐색

성능 저하 및 초기 LR 고정에 대한 사용자 지적에 따라 이 문서의 Parent `bc61fce284ae468e8b7022508f36e819`는 KILLED로 중단했다. 완료한 두 Child는 FINISHED로 보존했고 세 번째는 중단했다. 준비한 LR 단독 Parent도 학습 시작 전에 폐기했다. 현재 실행은 [[Work/Jery/작업기록/2026-10-19-Jery-LR-가중치-공동탐색과-데이터형식검증|LR·가중치 공동 탐색 작업기록]]과 [새 Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/afef02bf60dc496e8287ca3dc3057ad7)를 따른다. 기존 시점의 실행 기록을 현재 상태로 해석하지 않는다.

---

## 관련 문서

- [[Home|🏠 홈으로]]
- [[Work/Jery/index|Jery 프로젝트 인덱스]]
- [[Work/Jery/Jery 작업 백로그|Jery 작업 백로그]]
