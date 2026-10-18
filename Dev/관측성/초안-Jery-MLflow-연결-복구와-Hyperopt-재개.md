---
created: 2026-10-19
updated: 2026-10-19
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-19-Jery-MLflow-연결-복구와-Hyperopt-재개]]"
tags:
  - dev
  - draft
  - "jery"
---

# Jery MLflow 연결 복구와 Hyperopt 재개

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-19-Jery-MLflow-연결-복구와-Hyperopt-재개]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":14,"데이터":0}

## 1. 개요 및 목적

학습용 Python에서 NAS 내부 IP에 접속할 때 `No route to host`가 발생해 첫 Hyperopt trial의 기록 동기화와 다음 trial 시작이 대기하고 있었다. 같은 Python으로 공개 HTTPS MLflow에서 기존 Experiment와 run을 읽을 수 있음을 확인하고 실행기를 재개했다. 원래 모델·결과는 재사용했으며 첫 trial을 재학습하지 않았다.

2026-10-19 07:03 KST 확인 기준으로 첫 Child는 MLflow FINISHED, 두 번째 Child는 RUNNING이다. 두 번째 모델은 전체 입력 잘림 검사와 균형 데이터 확인을 통과하고 학습 전 validation을 수행 중이었다. 학습 성능이 개선됐다는 결론은 아직 내리지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 첫 trial의 실제 결과
- 원인과 수정
- 복구 검증
- 후속 실행
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

학습용 Python에서 NAS 내부 IP에 접속할 때 `No route to host`가 발생해 첫 Hyperopt trial의 기록 동기화와 다음 trial 시작이 대기하고 있었다. 같은 Python으로 공개 HTTPS MLflow에서 기존 Experiment와 run을 읽을 수 있음을 확인하고 실행기를 재개했다. 원래 모델·결과는 재사용했으며 첫 trial을 재학습하지 않았다.

2026-10-19 07:03 KST 확인 기준으로 첫 Child는 MLflow FINISHED, 두 번째 Child는 RUNNING이다. 두 번째 모델은 전체 입력 잘림 검사와 균형 데이터 확인을 통과하고 학습 전 validation을 수행 중이었다. 학습 성능이 개선됐다는 결론은 아직 내리지 않았다.

- 원래 학습 종료: 2026-10-18 11:12 KST.
- 실행 시간: 6,304.3초, 약 1시간 45분.
- 완료: 5에폭, 10,665 optimizer step.
- 조기 종료: 5에폭 연속 학습 전 baseline을 넘지 못함.
- 선택 모델: epoch 0 기본 head 복원. 검증 정확도 16.13%, 평가 정확도 15.04%.
- [첫 Child](https://mlflow.dove-nest.com/#/experiments/47/runs/bb1c80ea642040878a392833ea2cadd1)

MLflow의 마지막 학습 곡선은 epoch 5의 검증 정확도 5.24%다. 최종 선택 모델은 epoch 0이므로 report의 검증 16.13%와 서로 다른 지점을 가리킨다. 원격 run의 종료 시각에는 동기화 대기 시간이 포함되며 실제 학습·평가 시간은 원래 report와 runner 기록을 따른다.

내부 주소 `http://192.168.219.99:5000`은 curl 및 시스템 Python에서는 접속됐으나, 학습용 Python 3.12에서는 경로 오류가 발생했다. 공개 주소 `https://mlflow.dove-nest.com`은 같은 학습용 Python에서 정상 응답했다. OS 권한·라우터·Hermes 설정은 변경하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-19-Jery-MLflow-연결-복구와-Hyperopt-재개]]
- [[Dev/index|Dev 인덱스]]
