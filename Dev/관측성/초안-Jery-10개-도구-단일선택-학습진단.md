---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-단일선택-학습진단]]"
tags:
  - dev
  - draft
  - "jery"
---

# Jery 10개 도구 단일 선택 학습 진단

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-단일선택-학습진단]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":5,"데이터":0}

## 1. 개요 및 목적

사용자가 한국어 의도 분류는 별도 프로젝트에서 진행하고 Jery는 도구 10개로 실험하도록 요청했다.

Obsidian vault·edit·graph·dataview·bases 5개와 Swallow get_stock_price·get_price_history·get_portfolio·order·backtest 5개를 고정 후보로 사용한다. 요청과 호출 전 context, 한국어 기능 설명 10개를 한 창에 제공한다. no_tool·clarify·unsupported와 action 예측은 제외한다.

## 2. 핵심 아키텍처 및 원칙

- 과제와 데이터
- 협업과 검증
- 실제 실행
- 코드와 재현

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

Obsidian vault·edit·graph·dataview·bases 5개와 Swallow get_stock_price·get_price_history·get_portfolio·order·backtest 5개를 고정 후보로 사용한다. 요청과 호출 전 context, 한국어 기능 설명 10개를 한 창에 제공한다. no_tool·clarify·unsupported와 action 예측은 제외한다.

- 암기 진단: train 20개(도구별 2), validation 20개, test 20개.
- full profile: train 60개(도구별 6), validation 20개, test 20개.
- 두 profile의 validation/test는 바이트 단위로 동일하고 진단 train은 full train의 부분집합이다.
- 합성 정답은 미검토이며 실제 사용 성능을 의미하지 않는다.

통합 후 전체 145개 테스트와 원본 v1/v2 검증이 통과했다. 실제 native builder/tokenizer readiness는 두 profile 모두 skip·target 불일치·학습/추론 특징 불일치·잘림 0건, 최대 229 token이었다.

학습 fit 95% gate를 통과하지 못해 full Hyperopt를 보류했다. Test 점수를 gate나 LR 조정 근거로 사용하지 않았다. LR 1e-3 재진단을 별도 [Parent 37611c82](https://mlflow.dove-nest.com/#/experiments/47/runs/37611c82fb924ba6bccb5d4410db9226) / Child c997b44b16b04a9c9f43c02725ef616e에서 실행했다. 첫 gate JSON은 두 Parent에 업로드하고 SHA-256 read-back을 확인했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-단일선택-학습진단]]
- [[Dev/index|Dev 인덱스]]
