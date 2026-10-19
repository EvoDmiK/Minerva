---
created: 2026-10-19
updated: 2026-10-19
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-19-Jery-LR-가중치-공동탐색과-데이터형식검증]]"
tags:
  - dev
  - draft
  - "jery"
---

# LR·가중치 공동 탐색과 데이터 형식 검증

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-19-Jery-LR-가중치-공동탐색과-데이터형식검증]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":5,"데이터":0}

## 1. 개요 및 목적

성능 저하 상황에서 초기 LR을 그대로 고정한 점에 대한 사용자 지적을 반영했다. 사용자 추가 요청에 따라 window_none 가중치도 Hyperopt 파라미터와 MLflow 비교 파라미터에 포함했다.

고정 LR Parent `bc61fce284ae468e8b7022508f36e819`는 KILLED로 중단했다. 가중치 1.0/0.5 조건은 10에폭 완료 및 FINISHED 상태로 보존했고, 0.25 조건은 진행 중 중단해 checkpoint를 보존했다. 완료한 최고 trained validation 정확도 10.89%/12.50%는 baseline 16.13%보다 낮았다.

## 2. 핵심 아키텍처 및 원칙

- 기존 실행 보존
- 공동 탐색
- 데이터 형식 대조 결과
- 코드·검증
- 실제 시작 확인

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- 초기 LR: log-uniform `1e-6~1e-5`.
- window_none loss 가중치: choice `[0.25, 0.5, 1.0]`.
- Hyperopt TPE 5회, 각 10에폭. 같은 base에서 새로 시작하며 전체 데이터를 사용한다.
- weight decay 0.01, label smoothing 0, seed 3407, 유효 batch 4, warmup 64 및 linear scheduler 유지.
- 최고 trained validation 점수만 검색에 사용하고 test로 튜닝하지 않는다. serving baseline 보호와 callback 정책은 유지한다.
- 필수 Child params는 LR·가중치·epochs·seed·effective_batch_size 5개. metrics는 기존 7개. 나머지는 JSON artifact이며 모델 binary는 별도 저장한다. 기존 params 4개 plan도 지원한다.

첫 Hyperopt 후보는 LR `2.2090148907640474e-6`, 가중치 `0.5`다. 이는 시작 전 생성한 후보이며 실제 optimizer 실행 증거는 아래에 따로 기록한다. LR이 성능 저하의 유일한 원인이라고 확정하지 않는다.

| split | 창 | skip | target·입력 불일치 | 잘림·충돌 | 최대 토큰 |
|---|---:|---:|---:|---:|---:|
| train | 4,172 | 0 | 0 | 0 | 950 |
| validation | 1,592 | 0 | 0 | 0 | 953 |
| test | 1,577 | 0 | 0 | 0 | 930 |

한도는 max_len 1024, head_max_len 256이다. 정답 확률의 선택지 인덱스 대응, 기록된 원래 결정·허용 도구와의 대응, gold·metadata를 읽지 않는 추론 특징과 native 학습 특징의 일치를 확인했다. 검사기는 모델 가중치를 로드하거나 GPU forward를 실행하지 않는다. 실제 학습 코드에서도 native 학습 특징과 추론 특징의 일치를 확인한다.

현재 Unsloth Laya 미세조정 형식과 호환된다는 결과이며, 원 사전학습 코퍼스의 형식·분포·품질이 같다고 확인한 것은 아니다. 도구 설명 120자 압축, criteria의 별칭 표현, window_none 분포와 다중 창 집계의 적합성은 별도 문제다. 형식 통과를 성능 개선 근거로 해석하지 않는다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-19-Jery-LR-가중치-공동탐색과-데이터형식검증]]
- [[Dev/index|Dev 인덱스]]
