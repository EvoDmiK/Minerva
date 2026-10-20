---
created: 2026-10-19
date: 2026-10-19
project: Jery
type: worklog
status: in-progress
source_commit: a8de267f245962c850dde8aa7a19a15a9a64a7ef
tags:
  - jery
  - laya
  - training
  - hyperopt
  - mlflow
  - recovery
  - worklog
---
# Jery MLflow 연결 복구와 Hyperopt 재개

## 요약

학습용 Python에서 NAS 내부 IP에 접속할 때 `No route to host`가 발생해 첫 Hyperopt trial의 기록 동기화와 다음 trial 시작이 대기하고 있었다. 같은 Python으로 공개 HTTPS MLflow에서 기존 Experiment와 run을 읽을 수 있음을 확인하고 실행기를 재개했다. 원래 모델·결과는 재사용했으며 첫 trial을 재학습하지 않았다.

2026-10-19 07:03 KST 확인 기준으로 첫 Child는 MLflow FINISHED, 두 번째 Child는 RUNNING이다. 두 번째 모델은 전체 입력 잘림 검사와 균형 데이터 확인을 통과하고 학습 전 validation을 수행 중이었다. 학습 성능이 개선됐다는 결론은 아직 내리지 않았다.

## 첫 trial의 실제 결과

- 원래 학습 종료: 2026-10-18 11:12 KST.
- 실행 시간: 6,304.3초, 약 1시간 45분.
- 완료: 5에폭, 10,665 optimizer step.
- 조기 종료: 5에폭 연속 학습 전 baseline을 넘지 못함.
- 선택 모델: epoch 0 기본 head 복원. 검증 정확도 16.13%, 평가 정확도 15.04%.
- [첫 Child](https://mlflow.dove-nest.com/#/experiments/47/runs/bb1c80ea642040878a392833ea2cadd1)

MLflow의 마지막 학습 곡선은 epoch 5의 검증 정확도 5.24%다. 최종 선택 모델은 epoch 0이므로 report의 검증 16.13%와 서로 다른 지점을 가리킨다. 원격 run의 종료 시각에는 동기화 대기 시간이 포함되며 실제 학습·평가 시간은 원래 report와 runner 기록을 따른다.

## 원인과 수정

내부 주소 `http://192.168.219.99:5000`은 curl 및 시스템 Python에서는 접속됐으나, 학습용 Python 3.12에서는 경로 오류가 발생했다. 공개 주소 `https://mlflow.dove-nest.com`은 같은 학습용 Python에서 정상 응답했다. OS 권한·라우터·Hermes 설정은 변경하지 않았다.

- 실행기 기본 MLflow 주소를 공개 HTTPS로 변경했다.
- 실제 `tracking_uri`와 연결 복구 시각을 상태 JSON에 기록한다.
- 연결 성공 후 과거 오류 상태를 해제한다.
- 재시작 시 기존 `configuration.json`과 `source.json`을 덮어쓰지 않아 최초 실행 증거를 보존한다.
- 이전 실행기를 종료한 뒤 동일 Parent·Child 상태와 명시적 HTTPS 주소로 재개했다.

## 복구 검증

원래 가중치·report·단계 로그·에폭 로그·소스·설정의 SHA-256이 모두 일치했다. 첫 trial의 누락 에폭 4·5를 동기화하고, 네 개 학습 곡선이 에폭 1~5를 각각 한 번씩 포함하는 것을 원격에서 확인했다. 첫 모델 가중치 59,086,741바이트의 업로드·읽기 SHA-256도 일치한다.

관련 추적·로컬 실행기 테스트 9개, v1 130건·v2 1,162건 데이터 검증, staged diff 검사와 graphify 갱신을 통과했다. 복구 코드·테스트·문서는 `dev-codex`의 [커밋 a8de267](https://github.com/EvoDmiK/Jery/commit/a8de267f245962c850dde8aa7a19a15a9a64a7ef)로 커밋·푸시했다.

원본 복구 전 파일 해시는 `outputs/laya-balanced-20261018/tracking/recovery-20261019-before.json`, 복구 영수증은 같은 폴더의 `recovery-20261019.json`이다. 영수증은 Parent Artifact `recovery/20261019.json`에도 업로드 후 해시 검증했다.

## 후속 실행

- [Parent — Jery](https://mlflow.dove-nest.com/#/experiments/47/runs/9325d1ca84944fe281f94b519c59f305)
- [두 번째 Hyperopt Child](https://mlflow.dove-nest.com/#/experiments/47/runs/fc2c6a50fde549cbb2aebd3e696483e8)
- 파라미터: head LR 4.914736689552478e-5, weight decay 0.01, label smoothing 0.1.
- 기존 40/40/10/10 균형, 최대 64에폭, patience 5와 최적 검증 모델 복원 정책은 유지한다.
- 학습용 Python, 모델 파일, GPU 배치 크기와 학습 데이터 내용은 변경하지 않았다.

## 관련

- [[Work/Jery/index|Jery 프로젝트 인덱스]]
- [[Work/Jery/작업기록/2026-10-18-Jery-Laya-균형학습-Hyperopt-콜백과-MLflow|균형 학습·Hyperopt·콜백 정책]]
- [수정된 실행기](https://github.com/EvoDmiK/Jery/blob/a8de267f245962c850dde8aa7a19a15a9a64a7ef/scripts/run_laya_full_experiment.py)
- [저장소 기술 문서](https://github.com/EvoDmiK/Jery/blob/a8de267f245962c850dde8aa7a19a15a9a64a7ef/docs/model/laya-balanced-hyperopt-20261018.md)


### 07:04 KST 실행 확인

두 번째 모델이 학습 전 전체 validation을 마치고 실제 optimizer step 79회까지 진행한 것을 확인했다. 실행기와 모델 프로세스 모두 살아 있으며 MLflow 추적 주소는 공개 HTTPS다. 첫 모델의 report·가중치·원래 실행 소스와 설정은 해시가 그대로 유지됐다.
