---
created: 2026-10-25
updated: 2026-10-25
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-24-MLflow-trace-초기화]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# MLflow 기존 trace 정리와 새 관측 시작 — 2026-10-24

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-24-MLflow-trace-초기화]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":20,"데이터":0}

## 1. 개요 및 목적

사용자가 “기존 mlflow trace들을 지우고 새로운걸로 시작”하도록 명시적으로 요청했다. RobinGraph의 `robingraph-test`(실험 33)와 `robingraph-local`(실험 34)에서 기준 시각 이전 trace만 삭제 대상으로 고정했다. 실험 자체·run·dataset과 다른 프로젝트는 대상에서 제외했다.

기준 시각은 2026-10-24 04:36:01.404 UTC, 한국 시간 13:36:01.404다. TEST의 대상 trace 5,512개를 삭제했고 local은 삭제 대상이 없었다. 두 실험 모두 기준 시각 이전 잔여 trace가 0임을 재조회했다. 실험 active 상태와 run ID 집합(TEST 3개·local 0개)은 그대로였고 기존 평가 dataset도 재조회됐다. 실제 TEST 인사 요청으로 새 trace가 OK·10 spans로 생성되는 것을 확인했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 범위 확인
- 2. 처리 방식
- 3. 변경 파일과 실행 증거
- 4. 실제 검증 결과
- 삭제 후 새 기록과 보존 확인
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 사항
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 “기존 mlflow trace들을 지우고 새로운걸로 시작”하도록 명시적으로 요청했다. RobinGraph의 `robingraph-test`(실험 33)와 `robingraph-local`(실험 34)에서 기준 시각 이전 trace만 삭제 대상으로 고정했다. 실험 자체·run·dataset과 다른 프로젝트는 대상에서 제외했다.

기준 시각은 2026-10-24 04:36:01.404 UTC, 한국 시간 13:36:01.404다. TEST의 대상 trace 5,512개를 삭제했고 local은 삭제 대상이 없었다. 두 실험 모두 기준 시각 이전 잔여 trace가 0임을 재조회했다. 실험 active 상태와 run ID 집합(TEST 3개·local 0개)은 그대로였고 기존 평가 dataset도 재조회됐다. 실제 TEST 인사 요청으로 새 trace가 OK·10 spans로 생성되는 것을 확인했다.

이번 작업은 관측 기록의 초기화다. 앱 코드·설정·배포를 바꾸거나 거절 원인의 구조화 로깅을 새로 구현하는 작업이 아니다. 관련 기능이나 백로그의 완료 상태도 바꾸지 않는다.

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| 요구사항 | 기존 RobinGraph trace 삭제 | 사용자 명시 요청에 따라 새 기록부터 관측 |
| 범위 | 실험 33·34의 기준 시각 이전 trace | 실험·run·dataset·다른 프로젝트 보존 |
| 삭제 전 확인 | TEST 5,512개, local 0개 | 고정 cutoff와 trace ID inventory 저장 |
| 실제 처리 | 대상 5,512개 삭제·잔여 0 | 실험·run 보존, 기존 dataset 재조회, 새 trace OK·10 spans 확인 |
| 코드·배포 | 변경 없음 | 앱·환경 설정·운영 배포·commit·push 없음 |

1. `https://mlflow.dove-nest.com`에서 대상 실험과 기존 trace를 읽어 확인했다.
2. 삭제 기준 `cutoff_ms=1792816561404`와 대상 ID를 고정했다.
3. inventory의 명시적인 trace ID를 100개씩 `delete_traces`로 전달했다. 같은 cutoff로 재조회해 기준 시각 이전 잔여 0을 확인했다.
4. 실험·run·dataset을 삭제하지 않고 다른 프로젝트로 범위를 넓히지 않는다. 기존 로깅 흐름은 유지한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-24-MLflow-trace-초기화]]
- [[Dev/index|Dev 인덱스]]
