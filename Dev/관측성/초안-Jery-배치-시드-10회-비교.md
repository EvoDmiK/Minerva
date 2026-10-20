---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-20-Jery-배치-시드-10회-비교]]"
tags:
  - dev
  - draft
  - "jery"
---

# 배치·시드 10회 비교

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-20-Jery-배치-시드-10회-비교]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":2,"데이터":0}

## 1. 개요 및 목적

사용자가 배치 사이즈와 시드 등을 바꿔 10번 테스트하도록 요청했다. 이전 정규화 Parent 75c5cfd07701439d88f29f0cf1158a46는 업로드까지 완료됐다. 검증 기준 최우수는 Child ca0d15030d6543a99ba6a7084679d6bc(검증 65%, 해당 모델 평가 70%)다. Test가 더 높은 다른 Child로 바꾸지 않고 검증 선택을 유지했다.

이전 Hyperopt로 선정한 head LR 0.0003538647078409709, weight_decay 0.05, label_smoothing 0.05를 고정하고 배치 4·8 × 학습 시드 3407~3411의 완전 교차 10개 조건을 사전 고정한다. 이번 단계는 적응형 TPE 대신 배치·시드 반복 비교다.

## 2. 핵심 아키텍처 및 원칙

- 비교 설계
- 실행 및 추적
- 코드

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 배치 사이즈와 시드 등을 바꿔 10번 테스트하도록 요청했다. 이전 정규화 Parent 75c5cfd07701439d88f29f0cf1158a46는 업로드까지 완료됐다. 검증 기준 최우수는 Child ca0d15030d6543a99ba6a7084679d6bc(검증 65%, 해당 모델 평가 70%)다. Test가 더 높은 다른 Child로 바꾸지 않고 검증 선택을 유지했다.

모든 trial은 동일한 원 base에서 새로 학습한다. pretrained encoder·head 초기 가중치는 같고 시드는 학습 shuffle/dropout 등에 적용한다. 원본 데이터와 export를 재생성하지 않으며 train/validation/test 60/20/20, 도구 10개, 후보 순서·별칭·정답도 유지한다. 데이터 hermes-ten-tools-v1, catalog hermes-ten-tools-b4648cc19a90, 계약 decision-export-v2다.

모델은 검증으로 비교하고 test로 검색하거나 후보를 선정하지 않는다. Child 표의 val은 마지막 epoch이며 선택 head의 검증은 report.json과 Parent 요약을 따른다. 작은 미검토 합성 검증·평가를 반복 관찰한 탐색이므로 실사용 성능으로 주장하지 않는다.

설정·원본 데이터 검증, tracking 테스트 11개·CUDA 계획 테스트 5개를 통과했다. 실제 학습 override와 추적 파라미터가 일치하는지, 기존 기본값·거부 규칙을 검증했다. graphify AST 그래프를 업데이트했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-20-Jery-배치-시드-10회-비교]]
- [[Dev/index|Dev 인덱스]]
