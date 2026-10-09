---
project: RobinGraph
type: technical-validation
tags:
  - robingraph
  - decision-model
  - strands-decider
---

# Strands Decider 2B — 의도 분류와 Mac 학습 검토

## 결론

사용자가 지칭한 모델은 Strands Decider 2B다. 공개 선택지 채점 모델로서 RobinGraph 한국어 의도 분류의 평가 후보에 맞는다. 그러나 Mac mini M4 16GB에서 공식 학습 레시피가 그대로 동작한다고 확인된 것은 아니다. 공식 Apple Silicon 지원은 추론용이며, 현재 학습 엔트리는 CUDA 또는 CPU만 선택한다.

검증 범위는 공개 저장소·모델 카드·training/hardware·inference 문서 및 학습/MLX 코드의 읽기 전용 HTTP 조회다. 설치·추론·역전파·학습·제품 코드 변경·배포는 실행하지 않았다.

## 모델 구조와 공개 범위

조회한 공식 저장소는 strands-labs/strands-decider, 코드 기준은 `63d24ae286e50105fba0bd1db15b0e243aea4650`이다. README가 안내하는 reference checkpoint는 `StrandsAgents/strands-decider-2B-hobson-v21`이다.

- Qwen3.5-2B-Base의 decoder torso에 rank-16 LoRA와 작은 pointer/readout head를 사용한다.
- 언어 생성 head 대신 선택지의 hidden state를 채점하므로 텍스트 생성/decoding loop 없이 한 forward로 선택지 확률을 반환한다.
- choice/noul/score를 지원하며 선택지는 요청에서 정의한다.
- 코드·학습 레시피·adapter·head가 공개되어 있고 모델 카드는 Apache-2.0 라이선스를 안내한다. base weights는 별도로 내려받는다.
- 자체 한국어 의도 데이터로 추가 학습하는 연구 출발점이 될 수 있다. 일반 생성 LLM의 SFT와 목적함수·head 계약은 다르므로 기존 mlx_lm.lora 명령만으로 같은 결정 모델을 학습할 수 있다고 단정하지 않는다.

## Mac에서 추론과 학습은 다름

`docs/inference.md`는 macOS Apple Silicon에 대해 'inference only'라고 명시하고 MPS 및 MLX serving을 안내한다. MPS/MLX latency 예시는 M3 Pro/M4 Pro에서의 개발자 측정이며 사용자의 기본 M4 16GB 결과가 아니다. MLX 코드는 torso forward를 MLX로 실행하고 pointer head는 PyTorch CPU에 둔 추론 엔진이다.

`src/strands_decider/train.py`의 train 함수는 `device = "cuda" if torch.cuda.is_available() else "cpu"`를 사용한다. 따라서 현 학습 엔트리의 Mac GPU 학습 경로는 구현되어 있지 않으며, CUDA 없는 환경에서는 CPU를 선택한다. 공식 전체 training recipe는 Linux/WSL2 NVIDIA GPU와 CUDA/Triton 기반 학습 환경을 안내한다. CPU 선택 분기가 있다는 사실은 Mac CPU 전체 레시피 호환성·실용적 속도가 검증됐다는 뜻이 아니다.

`training/hardware.md`는 RTX 3090의 Qwen3.5 torso에서 짧은 분류 corpus(v13) peak 6.2 GiB, 긴 multi-step corpus(v14 이후) peak 12.4 GiB를 보고한다. 이는 NVIDIA 학습 실측으로 Mac 통합 메모리 사용량에 그대로 대입할 수 없다. 짧은 한국어 분류 데이터의 LoRA/head 학습이 16GB에서 원리적으로 불가능하다는 근거는 아니지만, 실제 gradient·kernel·memory 호환성 검증이 선행돼야 한다. Mac에서 end-to-end finetuning 가능/속도/최대 메모리는 미확인이다.

## 한국어 평가와 권장 순서

1. 공식 Mac 추론 경로로 공개 checkpoint를 먼저 평가한다. 사용자 Mac에서 실제 실행은 아직 하지 않았다.
2. 동일 한국어 의도 정답표로 기존 Jina 라우터와 정확도·자동 처리율·고확신 오분류·지연을 비교한다. 훈련되지 않은 조류 이름·표현 변형·복합·범위 밖을 포함한다.
3. 부족하면 학습 지원이 명확한 NVIDIA 환경에서 도메인 LoRA/head adaptation을 검토하고, 별도 validation으로 calibration을 다시 맞춘 뒤 Mac 추론 경로에서 호환성·정확도를 재확인한다. 공식 대규모 recipe 전체를 재학습할 필요가 있는지는 별도 판단이다.
4. Mac만으로 학습해야 한다면 일반적인 모델 크기 추정보다 Mac-compatible 역전파 경로와 head 학습 지원이 먼저 필요하다. 이는 구현·검증이 필요한 조건이며 현재 준비된 공식 명령으로 해결된 사실이 아니다.

모델 카드의 calibration은 primitive별 temperature를 held-out short classification에 맞춘 것으로 해당 confidence bands의 범위를 제한한다. 한국어 조류 도메인의 calibration은 별도 측정해야 한다. 문서상 'questions are read less than documents' 한계도 의도 분류 기준 문구·경계 사례를 평가할 이유다.

## 출처

- [공식 저장소](https://github.com/strands-labs/strands-decider)
- [v21 모델 카드](https://huggingface.co/StrandsAgents/strands-decider-2B-hobson-v21)
- [고정 snapshot 추론 문서](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/docs/inference.md)
- [고정 snapshot 학습 안내](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/training/README.md)
- [학습 하드웨어 측정](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/training/hardware.md)
- [학습 엔트리](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/src/strands_decider/train.py)
- [MLX 추론 엔진](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/src/strands_decider/mlx_engine.py)

[[Work/RobinGraph/검토자료/2026-10-07-RG013-Jev-의도분석-적합성검증]] 및 [[RobinGraph 작업 백로그]]와 관련된 조사다. 백로그 상태·구현·서버는 변경하지 않았다.
