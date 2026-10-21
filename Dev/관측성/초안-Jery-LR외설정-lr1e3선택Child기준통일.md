---
created: 2026-10-21
updated: 2026-10-21
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-21-Jery-LR외설정-lr1e3선택Child기준통일]]"
tags:
  - dev
  - draft
  - "jery"
---

# LR 외 전체 설정을 lr1e3 Parent 선택 Child로 통일 — 2026-10-21

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-21-Jery-LR외설정-lr1e3선택Child기준통일]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":2,"데이터":0}

## 1. 개요 및 목적

사용자 요청으로 `laya-ten-tools-train600-lr1e3-20261021` Parent(6261a1bdca194867a835cbfb2216493f)의 실제 Child 설정을 기준으로 다음 LR-only CV 계획을 준비했다. 학습 중단 지시는 유지하며 새 MLflow run을 만들거나 학습을 재개하지 않았다.

Parent의 서버 state가 최종 선정한 `selected_child_run_id`는 **c04cdad0246b4d6896ef89e5f9032ce2**(두 번째 Child)다. Best-trained validation accuracy0.95이며 동률에서는 낮은 LR 기준이다. Test로 기준을 고르지 않았다. Parent의20개 Child를 모두 비교하니 LR 외에 WD와 label smoothing도 서로 달랐다. 따라서 Parent 전체의 공통값이라고 가정하지 않고 Parent가 실제 최종 선정한 Child의 configuration.json을 복사했다.

## 2. 핵심 아키텍처 및 원칙

- 기준 Child
- 불변식과 상태 보존
- 검증

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

Parent의 서버 state가 최종 선정한 `selected_child_run_id`는 **c04cdad0246b4d6896ef89e5f9032ce2**(두 번째 Child)다. Best-trained validation accuracy0.95이며 동률에서는 낮은 LR 기준이다. Test로 기준을 고르지 않았다. Parent의20개 Child를 모두 비교하니 LR 외에 WD와 label smoothing도 서로 달랐다. 따라서 Parent 전체의 공통값이라고 가정하지 않고 Parent가 실제 최종 선정한 Child의 configuration.json을 복사했다.

중단한 기존 CV state/원래 plan/config/weights/MLflow 기록은 변경하지 않는다. 새 설정을 서버에 배포해도 prepare·detach·resume 명령을 실행하지 않는다. 학습 프로세스가 없는 상태와 기존 state interrupted를 확인한다. 재학습은 별도 사용자 요청이 있어야 시작한다.

원본 데이터 validator PASS(130examples/10tools/65isolated scenarios), CV 통합4개 PASS. 실제 원본 Child config와 비-LR 전체 값 equality 검증 및8개 실제 Hyperopt/TPE 후보의 불변식 검증 PASS. 회귀 테스트는 LR·새 결과 저장 경로 변경은 허용하되 warmup/smoothing뿐 아니라 eval_batch_size/gradient_checkpointing처럼 탐색 공간 밖 값의 drift도 거부한다. Graphify AST update 수행. 추가 의존성과 모델 코드 변경 없음.

서버4a98932 반영 후 기준 Child 전체 비-LR 값 equality와 CV 통합4개 테스트 PASS. 기존 CV state interrupted 및 활성 Jery 학습 프로세스0개를 확인했다. 새 run 생성·학습 재개는 실행하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-21-Jery-LR외설정-lr1e3선택Child기준통일]]
- [[Dev/index|Dev 인덱스]]
