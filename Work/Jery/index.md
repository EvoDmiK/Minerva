---
created: 2026-10-14
updated: 2026-10-19
project: Jery
type: index
tags: [jery, mcp, dataset, training, hyperopt]
---

# Jery

MCP 도구 선택을 위한 경량 로컬 학습 결정 모델 프로젝트.

## 작업기록

- [[Work/Jery/작업기록/2026-10-19-Jery-RTX5070Ti-CUDA-서버-실행-검증|2026-10-19 — RTX 5070 Ti CUDA 서버 환경과 32스텝 실행 검증]]
- [[Work/Jery/작업기록/2026-10-19-Jery-MLflow-연결-복구와-Hyperopt-재개|2026-10-19 — MLflow HTTPS 연결 복구, 완료 기록 동기화와 Hyperopt 재개]]
- [[Work/Jery/작업기록/2026-10-18-Jery-Laya-균형학습-Hyperopt-콜백과-MLflow|2026-10-18 — Laya 균형 학습, Hyperopt 탐색, 검증 콜백과 커밋·푸시]]
- [[Work/Jery/작업기록/2026-10-17-Jery-M4-학습-Gemma-실행과-MLflow-등록|2026-10-17 — M4 기준 모델 학습, Gemma 실행, MLflow 모델·데이터셋 등록]]
- [[Work/Jery/작업기록/2026-10-14-Jery-데이터셋-구축과-Hermes-MLflow-수집-방향|2026-10-14 — 초기 데이터셋 구축, 에이전트 역할, n8n 초안과 MLflow 수집 방향]]

## 현재 상태

등록 MCP 5개·도구 96개의 합성 데이터셋 v2(1,162개)와 학습·예측 가능한 선형 기준 모델을 구현하고 Mac mini M4에서 학습을 완료했다. MLflow에 학습 모델 Jery-LinearRouter v1, 데이터셋, 평가 결과와 코드를 등록했다. Gemma 4 E4B 4비트의 로컬 실행도 확인했지만 미세조정하지 않았으며, 6건의 탐색 결과는 기존 모델 대체를 뒷받침하지 못했다.

Laya multilingual은 인코더를 고정하고 결정 head를 학습한다. 첫 전체 데이터 64에폭 실험에서 성능 저하와 불균형을 확인해 기존 실행을 보존하고 중단했다. 후속 실험은 학습 비중 40/40/10/10, 검증 기준 최적 head 복원·patience 5 조기 종료와 Hyperopt TPE 5회 탐색을 적용하며, `Jery` Experiment에서 진행 중이다. 모델 성능이 개선됐다는 결론은 아직 내리지 않았다. [현재 MLflow Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/9325d1ca84944fe281f94b519c59f305)

읽기 전용 Hermes 로그 수집기·검토 후보 API와 독립 데이터 감사 도구는 구현했다. 이번 학습에는 실제 대화 로그를 사용하지 않았고 합성 정답은 모두 미검토 상태다. 정답 검토와 실제 요청 평가, action·비선택 사례 보강이 남아 있다.

2026-10-18 전체 테스트 109개 및 v1/v2 데이터 검증을 통과하고, `dev-codex`의 [`f135208`](https://github.com/EvoDmiK/Jery/commit/f135208a6eeade7b33c286360f366b6b4157bfc1)을 `origin/dev-codex`에 푸시했다. 상세 설정·재현 방법과 시각별 학습 상태는 최신 작업기록을 따른다.

2026-10-19 학습용 Python의 내부 IP 연결 실패를 공개 HTTPS 주소로 우회하고, 첫 trial 결과를 재학습 없이 동기화해 두 번째 Hyperopt trial을 시작했다. 복구 코드는 `a8de267`로 커밋·푸시했다. 상세 검증과 시각별 상태는 2026-10-19 작업기록을 따른다.

## 관련

- [GitHub 저장소](https://github.com/EvoDmiK/Jery)
- [[Work/index|프로젝트 목록]]
- [[Work/Birds-Nest/작업기록/Hermes/index|Hermes 작업기록]]
