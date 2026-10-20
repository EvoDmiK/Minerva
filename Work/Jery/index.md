---
created: 2026-10-14
updated: 2026-10-20
project: Jery
type: index
tags: [jery, mcp, dataset, training, hyperopt]
---

# Jery

MCP 도구 선택을 위한 경량 로컬 학습 결정 모델 프로젝트.

## 작업기록

- [[Work/Jery/작업기록/2026-10-20-Jery-반복오류-검토와-데이터보강|2026-10-20 — 반복 오류·정답 대조, 기능 설명 보완과 train 240개]]
- [[Work/Jery/작업기록/2026-10-20-Jery-배치-시드-10회-비교|2026-10-20 — 배치 4·8 × 학습 시드 5개, 10회 비교]]
- [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-정규화-재학습|2026-10-20 — LR·정규화·콜백 조정 후 Hyperopt 재학습]]
- [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-단일선택-학습진단|2026-10-20 — 10개 고정 도구, 암기 진단 통과와 CUDA Hyperopt]]
- [[Work/Jery/작업기록/2026-10-19-Jery-LR-가중치-공동탐색과-데이터형식검증|2026-10-19 — 낮은 LR·가중치 Hyperopt 공동 탐색, Laya native 데이터 형식 검증]]
- [[Work/Jery/작업기록/2026-10-19-Jery-routing-v2-공동수정과-재학습|2026-10-19 — Claude·AGY 공동 수정, routing v2 검증과 전체 CUDA 재학습]]
- [[Work/Jery/작업기록/2026-10-19-Jery-CUDA-전체학습-검증과-실험-전환|2026-10-19 — CUDA 전체 한 에폭 검증과 Mac 이후 Hyperopt 전환]]
- [[Work/Jery/작업기록/2026-10-19-Jery-RTX5070Ti-CUDA-서버-실행-검증|2026-10-19 — RTX 5070 Ti CUDA 서버 환경과 32스텝 실행 검증]]
- [[Work/Jery/작업기록/2026-10-19-Jery-MLflow-연결-복구와-Hyperopt-재개|2026-10-19 — MLflow HTTPS 연결 복구, 완료 기록 동기화와 Hyperopt 재개]]
- [[Work/Jery/작업기록/2026-10-18-Jery-Laya-균형학습-Hyperopt-콜백과-MLflow|2026-10-18 — Laya 균형 학습, Hyperopt 탐색, 검증 콜백과 커밋·푸시]]
- [[Work/Jery/작업기록/2026-10-17-Jery-M4-학습-Gemma-실행과-MLflow-등록|2026-10-17 — M4 기준 모델 학습, Gemma 실행, MLflow 모델·데이터셋 등록]]
- [[Work/Jery/작업기록/2026-10-14-Jery-데이터셋-구축과-Hermes-MLflow-수집-방향|2026-10-14 — 초기 데이터셋 구축, 에이전트 역할, n8n 초안과 MLflow 수집 방향]]

## 현재 상태

등록 MCP 5개·도구 96개의 합성 데이터셋 v2(1,162개)와 학습·예측 가능한 선형 기준 모델을 구현하고 Mac mini M4에서 학습을 완료했다. MLflow에 학습 모델 Jery-LinearRouter v1, 데이터셋, 평가 결과와 코드를 등록했다. Gemma 4 E4B 4비트의 로컬 실행도 확인했지만 미세조정하지 않았으며, 6건의 탐색 결과는 기존 모델 대체를 뒷받침하지 못했다.

Laya multilingual은 인코더를 고정하고 결정 head를 학습한다. 배치·시드 10회 실험은 완료됐으며 최고 validation 65%였다. 선정 head의 validation 예측 200건(원본 20개 반복) 중 80개 오류와 모든 실행에서 틀린 4개 사례를 확인했다. 카탈로그에는 있지만 짧은 선택지 설명에서 빠진 rename·frontmatter·Bases view 등의 기능을 보완했다. Native 옵션당 24token 한도를 넘긴 초안은 보존·차단하고, 압축한 representation v2.1-native-budget으로 두 profile 모두 잘림·특징/target 불일치 0건을 확인했다. hermes-ten-tools-v2의 train을 60→240개(도구당 24)로 보강하고, 기존 validation/test의 state·gold·alias·분할은 보존했다. 설명은 명시적으로 바뀌었으며 이미 관찰된 회귀 데이터다. 현재 회사 RTX 5070 Ti에서 [보강 학습](https://mlflow.dove-nest.com/#/experiments/47/runs/5f64008a2b974b7f87fab5088bafcf8a)과 [설명만 보완 대조군](https://mlflow.dove-nest.com/#/experiments/47/runs/f7faeae2708945d6b62f59e54a6f56ae)을 실행한다. 최대 optimizer 예산은 각 480step이고 평가 주기·조기 종료는 다르다. 전체 테스트 151개 통과. 정답·신규 사례는 AI 검토/작성이며 사람 검토와 실사용 독립 평가가 남아 있다.

읽기 전용 Hermes 로그 수집기·검토 후보 API와 독립 데이터 감사 도구는 구현했다. 이번 학습에는 실제 대화 로그를 사용하지 않았고 합성 정답은 모두 미검토 상태다. 정답 검토와 실제 요청 평가, action·비선택 사례 보강이 남아 있다.

2026-10-18 전체 테스트 109개 및 v1/v2 데이터 검증을 통과하고, `dev-codex`의 [`f135208`](https://github.com/EvoDmiK/Jery/commit/f135208a6eeade7b33c286360f366b6b4157bfc1)을 `origin/dev-codex`에 푸시했다. 상세 설정·재현 방법과 시각별 학습 상태는 최신 작업기록을 따른다.

2026-10-19 학습용 Python의 내부 IP 연결 실패를 공개 HTTPS 주소로 우회하고, 첫 trial 결과를 재학습 없이 동기화해 두 번째 Hyperopt trial을 시작했다. 복구 코드는 `a8de267`로 커밋·푸시했다. 상세 검증과 시각별 상태는 2026-10-19 작업기록을 따른다.

2026-10-19 회사 RTX 5070 Ti에서 전체 한 에폭 학습·검증·checkpoint 저장은 4분 32초, 로드·최종 평가·복원까지 전체 CLI는 5분 56초였다. epoch 1 정확도는 하락해 초기 head를 복원했으며 정확도 개선을 주장하지 않는다. 당시 Mac 실험을 유지하면서 사용자 요청으로 CUDA Hyperopt 5회도 시작했으나, 이후 이번 routing v2 전환 요청에 따라 두 실행을 모두 중단했다. 현재 실행 상태는 위 routing v2 Parent와 최신 작업기록을 따른다. 전체 테스트 112개 통과, `1c0011f` 커밋·푸시 및 서버 반영 완료. 자세한 상태와 한계는 최신 CUDA 전체 학습 작업기록을 따른다.

## 관련

- [GitHub 저장소](https://github.com/EvoDmiK/Jery)
- [[Work/index|프로젝트 목록]]
- [[Work/Birds-Nest/작업기록/Hermes/index|Hermes 작업기록]]
