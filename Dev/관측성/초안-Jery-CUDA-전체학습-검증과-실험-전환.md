---
created: 2026-10-19
updated: 2026-10-19
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-19-Jery-CUDA-전체학습-검증과-실험-전환]]"
tags:
  - dev
  - draft
  - "jery"
---

# CUDA 전체 학습 검증과 다음 실험 전환

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-19-Jery-CUDA-전체학습-검증과-실험-전환]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":8,"데이터":0}

## 1. 개요 및 목적

RTX 5070 Ti 회사 서버에서 전체 데이터 한 에폭을 학습·평가·저장하고, 새 모델 인스턴스 복원과 native optimizer checkpoint 재개를 확인했다. 기존 Mac Hyperopt 실험은 유지한다.

| 구간 | 시간 |
|---|---:|
| CUDA optimizer 계산 합계 | 243.61초 |
| CUDA 한 에폭 학습 + 검증 + native checkpoint | 271.85초 (4분 32초) |
| CUDA CLI 전체: 로드·인코딩·baseline·학습·평가·저장·복원·최종 test | 356.28초 (5분 56초) |
| 이전 Mac 첫 에폭 학습·checkpoint·검증 | 1,149.71초 (19분 10초) |

## 2. 핵심 아키텍처 및 원칙

- 실제 시간과 정확도
- 구성과 검증
- MLflow와 다음 실험

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

RTX 5070 Ti 회사 서버에서 전체 데이터 한 에폭을 학습·평가·저장하고, 새 모델 인스턴스 복원과 native optimizer checkpoint 재개를 확인했다. 기존 Mac Hyperopt 실험은 유지한다.

| 구간 | 시간 |
|---|---:|
| CUDA optimizer 계산 합계 | 243.61초 |
| CUDA 한 에폭 학습 + 검증 + native checkpoint | 271.85초 (4분 32초) |
| CUDA CLI 전체: 로드·인코딩·baseline·학습·평가·저장·복원·최종 test | 356.28초 (5분 56초) |
| 이전 Mac 첫 에폭 학습·checkpoint·검증 | 1,149.71초 (19분 10초) |

해당 구성의 에폭 학습·검증은 약 4.2배 빨랐다. backend precision, micro batch/누적 방식과 학습률이 달라 하드웨어 단독 비교는 아니다. 서버에서는 기존 IsaacLab·vision 작업을 유지했다. 다른 작업의 처리량 변화는 측정하지 않았다. 최대 PyTorch CUDA 할당은 1.359GiB였다.

정확도 개선은 없었다. baseline validation 16.13% → 학습 한 에폭 후 3.63%로 하락해 정책대로 epoch 0 head를 선택·복원했다. 최종 validation 16.13%, test 15.04%는 복원한 초기 head의 결과다. 실제 한 에폭 학습 head는 MLflow의 `model/last-trained/`로 구분해 올렸다.

- 경로: `/home/persona-ai/git/Jery-cuda`, Python `/home/persona-ai/envs/jery-cuda/bin/python`.
- 모델: 같은 Laya multilingual base, FP16 frozen encoder / FP32 routing head 14,770,945개 / BF16 autocast.
- 데이터: 합성 미검토 `mcp-routing-v2`, 계약 `decision-export-v1`, 카탈로그 `hermes-mcp-57e701d87790`.
- 원본 사례 668/248/246개, exhaustive window 4,172/1,592/1,577개. 학습의 모든 원래 window를 유지한 균형 샘플링 8,530개, 2,133 step/epoch.
- micro batch 4 / accumulation 1 / eval batch 4. CUDA allocator 한도 30%는 메모리 한도이며 연산 점유율 제한이 아니다.
- 모든 split 토큰 절단 0. 특징은 state·questions만 사용하며 blind encoder와 native dataset builder의 특징을 전수 비교했다.
- encoder 전체 파라미터 해시 불변, head 갱신, 새 모델 인스턴스에서 validation 확률 차이 0 및 동일한 case 예측 확인.
- checkpoint의 trainer·Adam optimizer step을 2,133→2,134로 재개하고, 원본 checkpoint 모든 파일 해시 보존 확인. 저장 학습률 0에서 한 스텝을 이어 가는 호환성 확인이며 성능 개선 검사가 아니다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-19-Jery-CUDA-전체학습-검증과-실험-전환]]
- [[Dev/index|Dev 인덱스]]
