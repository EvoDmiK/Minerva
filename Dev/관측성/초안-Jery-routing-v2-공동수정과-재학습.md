---
created: 2026-10-19
updated: 2026-10-19
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-19-Jery-routing-v2-공동수정과-재학습]]"
tags:
  - dev
  - draft
  - "jery"
---

# Jery routing v2 공동 수정과 재학습

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-19-Jery-routing-v2-공동수정과-재학습]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":3,"데이터":0}

## 1. 개요 및 목적

사용자 요청에 따라 기존 Mac·CUDA 학습을 중단하고 결과와 가중치를 보존했다. 새 정책의 전체 데이터 CUDA 재학습은 통합 검증 후 시작한다.

- Mac Parent: `9325d1ca84944fe281f94b519c59f305`
- CUDA Parent: `29552487a8a94b10ad942d9bbc331953`
- 두 Parent의 MLflow 상태 `KILLED`, 로컬 supervisor 종료 및 전용 학습 프로세스 종료 확인.
- 다른 회사 GPU 작업은 유지했다. 중단 증거 JSON은 기존 Parent의 `control/stopped-for-routing-v2.json`에 업로드하고 해시를 검증했다.

## 2. 핵심 아키텍처 및 원칙

- 종료한 실행
- 원인과 수정
- 검증
- 새 실행

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자 요청에 따라 기존 Mac·CUDA 학습을 중단하고 결과와 가중치를 보존했다. 새 정책의 전체 데이터 CUDA 재학습은 통합 검증 후 시작한다.

- Mac Parent: `9325d1ca84944fe281f94b519c59f305`
- CUDA Parent: `29552487a8a94b10ad942d9bbc331953`
- 두 Parent의 MLflow 상태 `KILLED`, 로컬 supervisor 종료 및 전용 학습 프로세스 종료 확인.
- 다른 회사 GPU 작업은 유지했다. 중단 증거 JSON은 기존 Parent의 `control/stopped-for-routing-v2.json`에 업로드하고 해시를 검증했다.

기존 동일 test 점수는 같은 초기 head를 최종 선택한 결과였다. validation 248개 요청 중 232개는 도구 선택이지만, 1,592개 후보 창 중 1,305개는 `window_none`이었다. Mac 첫 trial에서 정답 도구 창 정확도가 26.81%→1.70%로 떨어지는 동안 전체 창 정확도는 8.79%→78.96%로 올랐다. 창 loss와 최종 요청 선택 성능이 다른 방향으로 움직였다. 한국어 성능이 주원인이라고 단정하지 않는다.

- `window_none` loss 가중치 1.0/0.5/0.25를 비교하며 원래 모든 창·분할·기존 oversampling을 유지한다.
- train 평균 가중치 1.0/0.8/0.7로 정규화한다. validation/test는 통계 계산에 쓰지 않는다.
- best trained(epoch≥1)·serving selected·last trained를 분리한다.
- Hyperopt 목적값은 최고 trained validation 점수로 계산하며 baseline 점수로 올림하지 않는다.
- serving은 최고 trained가 baseline을 넘을 때만 교체한다.
- min_epochs 10, trained-only patience 5, min_delta 0.004. 최초 제어 실험은 세 조건 각 10에폭이며 64에폭 Hyperopt를 실행 중이라고 보고하지 않는다.
- prepared configuration과 실행 configuration 일치 검사를 보강했다.

AGY는 독립 감사 도구와 검증 테스트를 구현했다. 현재 CLI 입력 격리와 이식성을 추가 검토 중이다. 실제 협업은 Orca Run `run_e483b51bc37f`에서 Claude·Antigravity와 진행했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-19-Jery-routing-v2-공동수정과-재학습]]
- [[Dev/index|Dev 인덱스]]
