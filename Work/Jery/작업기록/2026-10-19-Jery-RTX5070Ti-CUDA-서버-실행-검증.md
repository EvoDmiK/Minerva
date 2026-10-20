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
# RTX 5070 Ti CUDA 서버 실행 검증

Tailscale SSH로 `persona-ai@persona-ai` 접속을 확인하고, Ubuntu 24.04.4 / RTX 5070 Ti 16GB에 독립 환경을 준비했다. 기존 IsaacLab·vision 작업은 유지했다.

- 코드: `/home/persona-ai/git/Jery-cuda` (`dev-codex`)
- Python: `/home/persona-ai/envs/jery-cuda/bin/python` (3.12.3)
- PyTorch 2.11.0+cu128, Unsloth/Zoo 2026.10.6, Transformers 5.17.0, Laya 0.4.9
- 코드: `scripts/probe_laya_cuda.py`, 환경: `requirements-decision-cuda.txt`, 재현 방법: `docs/model/laya-cuda-probe-20261019.md`

## 결과

동일한 base 모델의 encoder를 고정하고 routing head·scorer·type embedding 14,770,945개만 학습했다. native action head는 고정했다. FP16 encoder / FP32 head / BF16 autocast를 사용했다. 초기 FP16 시도의 gradient overflow는 BF16으로 해결했고 그 시도는 속도 비교에서 제외했다.

| micro batch × accumulation | 유효 배치 | 중앙 스텝 시간 | PyTorch 최대 할당 |
|---|---:|---:|---:|
| 1 × 4 | 4 | 0.1461초 | 0.965GiB |
| 4 × 1 | 4 | 0.1206초 | 1.138GiB |

각각 32 optimizer step, 최초 5 step 제외 중앙값이다. 다른 작업이 GPU 약 7.2GiB 및 연산 자원을 사용하는 상태였다. Mac에서 관측한 약 0.47초/step보다 빨랐지만 backend·precision·샘플 순서가 달라 엄밀한 하드웨어 단독 비교는 아니다. 전체 epoch·평가 시간이나 최종 정확도는 이번에 측정하지 않았다.

전체 train 4,172개 window를 인코딩 검증했고 누락·절단 0, 최대 950토큰이다. 기존 균형 샘플링 8,530개 인덱스를 구성했으며 실제 각 검증은 128개 예제만 소비했다. 유한 loss/gradient, head 갱신, encoder 파라미터 표본 불변, head 파일 저장·재로드와 재로드 후 logits 일치를 확인했다. `pip check` 및 공통 Laya 테스트 11개, v1/v2 데이터 검증도 통과했다.

## 기록과 현재 학습

결과 JSON·환경·코드는 기존 [MLflow Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/9325d1ca84944fe281f94b519c59f305)의 `diagnostics/cuda-20261019/` artifact에 저장했다. 기존 trial 정확도 메트릭이나 Hyperopt 탐색 결과에는 섞지 않는다. 검증용 head도 같은 진단 경로에 보관한다.

서버 원본은 `outputs/laya-cuda-probe-20261019-final-b1/`, `outputs/laya-cuda-probe-20261019-final-b4/`이며 로컬 수집본은 `outputs/laya-cuda-probe-20261019/`다. 가중치와 결과물은 Git에 넣지 않는다.

Mac의 기존 Hyperopt 학습은 유지한다. 확인 시 1~3번째 trial이 완료되고 4번째 trial이 실행 중이었다. CUDA의 이번 실행은 짧은 공학 검증이며 전체 학습을 이전하거나 Mac checkpoint를 이어 학습한 것이 아니다. 전체 CUDA 학습에는 window 집계·검증 콜백·Hyperopt·MLflow 정책 연결과 baseline 평가·재개 검증이 남아 있다.

합성 미검토 `mcp-routing-v2`, `decision-export-v1`, 카탈로그 `hermes-mcp-57e701d87790`를 사용했다. 실제 요청 정확도 개선을 입증한 결과는 아니다.

## 커밋과 업로드 확인

`dev-codex`의 [`4f7a706`](https://github.com/EvoDmiK/Jery/commit/4f7a706)을 `origin/dev-codex`에 푸시했다. 로컬 작업 트리는 깨끗하다. MLflow 결과·환경·코드 JSON과 두 검증용 head(각 59,086,748바이트)를 업로드하고 GET 재조회 SHA-256 일치를 확인했다. 가중치는 `diagnostics/cuda-20261019/b1/head.safetensors`, `b4/head.safetensors`에 있다.

---

## 관련 문서

- [[Home|🏠 홈으로]]
- [[Work/Jery/index|Jery 프로젝트 인덱스]]
- [[Work/Jery/Jery 작업 백로그|Jery 작업 백로그]]
