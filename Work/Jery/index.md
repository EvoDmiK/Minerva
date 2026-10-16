---
created: 2026-10-14
updated: 2026-10-17
project: Jery
type: index
tags: [jery, mcp, dataset]
---

# Jery

MCP 도구 선택을 위한 경량 로컬 학습 결정 모델 프로젝트.

## 작업기록

- [[Work/Jery/작업기록/2026-10-17-Jery-M4-학습-Gemma-실행과-MLflow-등록|2026-10-17 — M4 기준 모델 학습, Gemma 실행, MLflow 모델·데이터셋 등록]]
- [[Work/Jery/작업기록/2026-10-14-Jery-데이터셋-구축과-Hermes-MLflow-수집-방향|2026-10-14 — 초기 데이터셋 구축, 에이전트 역할, n8n 초안과 MLflow 수집 방향]]

## 현재 상태

등록 MCP 5개·도구 96개의 합성 데이터셋 v2(1,162개)와 학습·예측 가능한 선형 기준 모델을 구현하고 Mac mini M4에서 학습을 완료했다. MLflow에 학습 모델 Jery-LinearRouter v1, 데이터셋, 평가 결과와 코드를 등록했다. Gemma 4 E4B 4비트의 로컬 실행도 확인했지만 미세조정하지 않았으며, 6건의 탐색 결과는 기존 모델 대체를 뒷받침하지 못했다.

읽기 전용 Hermes 로그 수집기·검토 후보 API와 독립 데이터 감사 도구는 구현했다. 이번 학습에는 실제 대화 로그를 사용하지 않았고 합성 정답은 모두 미검토 상태다. 정답 검토와 실제 요청 평가, action·비선택 사례 보강, 로컬 변경 커밋·푸시가 남아 있다. 상세 상태와 실험 링크는 최신 작업기록을 따른다.

## 관련

- [GitHub 저장소](https://github.com/EvoDmiK/Jery)
- [[Work/index|프로젝트 목록]]
- [[Work/Birds-Nest/작업기록/Hermes/index|Hermes 작업기록]]
