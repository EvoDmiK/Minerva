---
created: 2026-10-14
updated: 2026-10-21
project: Jery
type: index
tags: [jery, mcp, dataset, training, hyperopt]
---

# Jery

사용자 요청과 후보 명세를 읽고 다음 MCP 도구를 선택하는 경량 로컬 모델.

## 현재 실험

**LR만 변경하는 20개 조건 × 층화 5-fold 검증**

| 항목 | 내용 |
|---|---|
| 진행 확인 | 2026-10-21 17:41 KST · 5개 조건 완료, 6번째 조건의 fold 2 학습 중 |
| 학습률 | `1e-3 ~ 5e-3` · Hyperopt TPE |
| 기준 설정 | 지정한 `lr1e3` 실험의 최종 선택 Child · LR 외 설정 고정 |
| 데이터 | 합성 600개 · fold별 학습 480 / 검증 120 |
| 환경 | Linux · RTX 5070 Ti · Laya 인코더 고정, head 학습 |

[MLflow에서 진행 확인](https://mlflow.dove-nest.com/#/experiments/47/runs/675bf807c9674425ba6f9de1ad536b91) · [[Work/Jery/작업기록/2026-10-21-Jery-LR외설정-lr1e3선택Child기준통일|설정·검증·실행 자료]]

MLflow는 **전체 실험 → LR 조건 → fold** 순서로 펼친다. 조건별 평균·표준편차는 5개 fold 완료 후 표시된다. 위 진행은 확인 시점의 기록이다.

## 남은 과제

- 합성 데이터의 사람 검토와 실제 요청 평가셋 확보.
- 실제 요청 평가 후 모델 채택 여부 결정. 현재 반복 실험 점수를 실제 사용 성능으로 해석하지 않는다.

[[Work/Jery/Jery 작업 백로그|전체 작업 백로그]]

## 작업 기록

### 2026-10-21

- [[Work/Jery/작업기록/2026-10-21-Jery-LR외설정-lr1e3선택Child기준통일|LR 단독 5-fold · 기준 설정 통일 및 실행]]
- [[Work/Jery/작업기록/2026-10-21-Jery-LR만20회-Stratified5Fold검증|첫 LR 단독 5-fold · 중단 기록]]
- [[Work/Jery/작업기록/2026-10-21-Jery-MLflow비교params-완료검증오류-복구|완료 검증 오류 · 원인과 복구]]
- [[Work/Jery/작업기록/2026-10-21-Jery-MLflow-비교파라미터-복원과-실시간동기화|MLflow 비교 파라미터 · 5개 항목 복원]]
- [[Work/Jery/작업기록/2026-10-21-Jery-Warmup배치ClippingScheduler-공동탐색20회|다중 파라미터 탐색 20회 · 완료]]
- [[Work/Jery/작업기록/2026-10-21-Jery-LR1e-3부터5e-3와-추가탐색후보|LR 1e-3~5e-3 · 추가 탐색 후보]]
- [[Work/Jery/작업기록/2026-10-21-Jery-다음20회-LR상한1e-3|LR 상한 1e-3 · 탐색 계획]]
- [[Work/Jery/작업기록/2026-10-21-Jery-train600-F1조건-범위축소-Hyperopt20회|F1 조건을 참고한 탐색 범위 축소]]

### 2026-10-20

- [[Work/Jery/작업기록/2026-10-20-Jery-train600-참고모델기반-Hyperopt20회|참고 모델 기반 탐색 20회]]
- [[Work/Jery/작업기록/2026-10-20-Jery-train600-CUDA-Hyperopt-시작|Train 600 · CUDA 탐색 5회]]
- [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-학습데이터600개-보강|학습 데이터 240→600개 보강]]
- [[Work/Jery/작업기록/2026-10-20-Jery-실제요청-고정평가셋-준비와-협업|실제 요청 평가셋 준비 · 검토 대기]]
- [[Work/Jery/작업기록/2026-10-20-Jery-반복오류-검토와-데이터보강|반복 오류 검토 · 학습 데이터 보강]]
- [[Work/Jery/작업기록/2026-10-20-Jery-배치-시드-10회-비교|배치·시드 조합 10회 비교]]
- [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-정규화-재학습|정규화·콜백 조정 후 재학습]]
- [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-단일선택-학습진단|10개 도구 단일 선택 · 학습 진단]]

### 2026-10-19

- [[Work/Jery/작업기록/2026-10-19-Jery-LR-가중치-공동탐색과-데이터형식검증|낮은 LR·가중치 탐색과 데이터 형식]]
- [[Work/Jery/작업기록/2026-10-19-Jery-routing-v2-공동수정과-재학습|Routing v2 · 공동 수정 및 재학습]]
- [[Work/Jery/작업기록/2026-10-19-Jery-CUDA-전체학습-검증과-실험-전환|CUDA 전체 학습 검증]]
- [[Work/Jery/작업기록/2026-10-19-Jery-RTX5070Ti-CUDA-서버-실행-검증|RTX 5070 Ti · 서버 실행 검증]]
- [[Work/Jery/작업기록/2026-10-19-Jery-MLflow-연결-복구와-Hyperopt-재개|MLflow 연결 복구와 탐색 재개]]

### 2026-10-18

- [[Work/Jery/작업기록/2026-10-18-Jery-Laya-균형학습-Hyperopt-콜백과-MLflow|균형 학습·Hyperopt·콜백]]

### 2026-10-17

- [[Work/Jery/작업기록/2026-10-17-Jery-M4-학습-Gemma-실행과-MLflow-등록|M4 기준 모델·Gemma 실행·MLflow 등록]]

### 2026-10-14

- [[Work/Jery/작업기록/2026-10-14-Jery-데이터셋-구축과-Hermes-MLflow-수집-방향|초기 데이터셋과 Hermes 수집 방향]]

## 참고

- [GitHub 저장소](https://github.com/EvoDmiK/Jery)
- [[Work/Jery/작업기록/2026-10-21-Jery-누적상태기록-보관|정리 전 누적 상태 원문]]
- [[Work/index|프로젝트 목록]]
- [[Work/Birds-Nest/작업기록/Hermes/index|Hermes 작업기록]]
