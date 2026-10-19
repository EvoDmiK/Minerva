---
created: 2026-10-19
updated: 2026-10-19
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-19-Jery-RTX5070Ti-CUDA-서버-실행-검증]]"
tags:
  - dev
  - draft
  - "jery"
---

# RTX 5070 Ti CUDA 서버 실행 검증

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-19-Jery-RTX5070Ti-CUDA-서버-실행-검증]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":6,"데이터":0}

## 1. 개요 및 목적

Tailscale SSH로 `persona-ai@persona-ai` 접속을 확인하고, Ubuntu 24.04.4 / RTX 5070 Ti 16GB에 독립 환경을 준비했다. 기존 IsaacLab·vision 작업은 유지했다.

- 코드: `/home/persona-ai/git/Jery-cuda` (`dev-codex`)
- Python: `/home/persona-ai/envs/jery-cuda/bin/python` (3.12.3)
- PyTorch 2.11.0+cu128, Unsloth/Zoo 2026.10.6, Transformers 5.17.0, Laya 0.4.9
- 코드: `scripts/probe_laya_cuda.py`, 환경: `requirements-decision-cuda.txt`, 재현 방법: `docs/model/laya-cuda-probe-20261019.md`

## 2. 핵심 아키텍처 및 원칙

- 결과
- 기록과 현재 학습

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

Tailscale SSH로 `persona-ai@persona-ai` 접속을 확인하고, Ubuntu 24.04.4 / RTX 5070 Ti 16GB에 독립 환경을 준비했다. 기존 IsaacLab·vision 작업은 유지했다.

전체 train 4,172개 window를 인코딩 검증했고 누락·절단 0, 최대 950토큰이다. 기존 균형 샘플링 8,530개 인덱스를 구성했으며 실제 각 검증은 128개 예제만 소비했다. 유한 loss/gradient, head 갱신, encoder 파라미터 표본 불변, head 파일 저장·재로드와 재로드 후 logits 일치를 확인했다. `pip check` 및 공통 Laya 테스트 11개, v1/v2 데이터 검증도 통과했다.

결과 JSON·환경·코드는 기존 [MLflow Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/9325d1ca84944fe281f94b519c59f305)의 `diagnostics/cuda-20261019/` artifact에 저장했다. 기존 trial 정확도 메트릭이나 Hyperopt 탐색 결과에는 섞지 않는다. 검증용 head도 같은 진단 경로에 보관한다.

Mac의 기존 Hyperopt 학습은 유지한다. 확인 시 1~3번째 trial이 완료되고 4번째 trial이 실행 중이었다. CUDA의 이번 실행은 짧은 공학 검증이며 전체 학습을 이전하거나 Mac checkpoint를 이어 학습한 것이 아니다. 전체 CUDA 학습에는 window 집계·검증 콜백·Hyperopt·MLflow 정책 연결과 baseline 평가·재개 검증이 남아 있다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-19-Jery-RTX5070Ti-CUDA-서버-실행-검증]]
- [[Dev/index|Dev 인덱스]]
