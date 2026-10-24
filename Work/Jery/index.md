---
created: 2026-10-14
updated: 2026-10-24
project: Jery
type: index
tags: [jery, mcp, dataset, training, hyperopt]
---

# Jery

사용자 요청과 후보 명세를 읽고 다음 MCP 도구를 선택하는 경량 로컬 모델.

## 최근 완료 실험

**기준·최고 설정 × seed 3개 × 동일한 층화 5-fold · 30회 모두 완료**

| 항목 | 기준 설정 | 최고 설정 |
|---|---:|---:|
| 평균 validation 정확도 | 73.83% | 76.17% |
| 평균 validation Macro F1 | 0.7342 | 0.7582 |
| 기존 test20 평균 Macro F1 | 0.6378 | 0.6306 |

모든 seed에서 validation F1이 개선됐지만 기존 test20에서는 일관된 개선이 없었다. 실제 요청 성능으로 해석하지 않는다. 현재 추가 학습은 시작하지 않았다.

[MLflow 완료 결과](https://mlflow.dove-nest.com/#/experiments/47/runs/af613b715d804393b17872be8d5ad671) · [[Work/Jery/작업기록/2026-10-24-Jery-seed30회-완료와-성능개선제안|결과·리팩토링·다음 실험 제안]]

다음 우선순위는 공통 오답 검토, 혼동 도구 쌍의 대조 데이터, 후보 설명 개선이다. 독립 실제 test 목표 200개 중 현재 후보는 13개·사람 검토 완료는 0개다.

## 남은 과제

- 합성 데이터의 사람 검토와 실제 요청 평가셋 확보.
- 실제 요청 평가 후 모델 채택 여부 결정. 현재 반복 실험 점수를 실제 사용 성능으로 해석하지 않는다.

[[Work/Jery/Jery 작업 백로그|전체 작업 백로그]]

## 작업 기록

### 2026-10-24

- [[Work/Jery/작업기록/2026-10-24-Jery-seed30회-완료와-성능개선제안|seed 30회 완료 · 검증 코드 정리와 성능 개선 순서]]
- [[Work/Jery/작업기록/2026-10-24-Jery-OOF오류분석과-seed재검증|OOF 오류 분석 · 3개 seed 재검증 시작]]
- [[Work/Jery/작업기록/2026-10-24-Jery-Ponytail-리팩토링과-후속제안|Ponytail 리팩토링 · 탐색 중복 방지와 다음 작업]]

### 2026-10-22

- [[Work/Jery/작업기록/2026-10-22-Jery-LR고정-기준1회-파라미터탐색19회|LR 고정 · 기준 1개 + 파라미터 탐색 19개]]

- [[Work/Jery/작업기록/2026-10-22-Jery-MLflow-HTTP520-업로드복구|MLflow HTTP 520 · 업로드 중단 복구]]

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
