---
created: 2026-10-27
updated: 2026-10-27
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-시맨틱-질의-원인trace-운영배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RG-212 연계] 시맨틱 질의·원인 trace 운영 배포 — 2026-10-26

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-시맨틱-질의-원인trace-운영배포]] · 분류 근거 {"인프라":0,"자동화":5,"관측성":10,"데이터":1}

## 1. 개요 및 목적

사용자 명시 승인에 따라 TEST 검증 소스를 NAS Production에 배포했다. Jenkins `RobinGraph-PROD #9`는 SUCCESS였고, 운영 컨테이너에서 healthy·active/semantic·tracing 활성화와 MLflow 실험 `50 / robingraph-prod`를 확인했다. 운영 공개 요청 3 POST와 3 GET은 모두 HTTP 200이었으며, 동일 질문·마스킹된 응답·태그가 실험 50의 고유 trace 3개와 일치했다.

이번 배포는 Git commit/push 없이 승인된 미커밋 snapshot을 일회성 Jenkins Replay로 빌드한 것이다. 소스 234파일은 SHA256 `6a95918a55332aa0195c07bf4e5a9c60a7cb006b67fd56d255d683f22c72c922`로 식별하고 immutable image digest와 연결했다. 기존 Jenkins 정의·매개변수·job properties와 TEST 컨테이너는 유지했다. 일반 main 자동 파이프라인은 여전히 lexical 설정이므로 이번 snapshot과 main의 동기화는 별도 승인 범위다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 발생 현상 / 요구사항
- 원인 분석 / 설계 검토
- 2. 해결 방안 및 설계
- 3. 주요 구현 및 배포 자산
- 변경 범위와 파일
- 최종 runtime
- 4. 검증 및 테스트 결과
- 자동화·빌드 검사
- NAS 후보 검증 및 실패 이력
- 공개 운영 요청과 실제 trace
- TEST 및 Jenkins 설정 보존
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
검증 TEST manifest → 불변 snapshot → Jenkins 검사·이미지 빌드
→ NAS 후보 실제 API → 운영 교체 → 공개 API → 실험 50 동일 요청 trace
```

```text
ROBINGRAPH_DEPLOY_TARGET=prod
ROBINGRAPH_GRAPH_INTENT_MODE=active
ROBINGRAPH_GRAPH_INTERPRETER=semantic
ROBINGRAPH_MLFLOW_TRACING=true
MLFLOW_EXPERIMENT_ID=50
MLFLOW_EXPERIMENT_NAME=robingraph-prod
```

## 4. 검증 근거 및 트러블슈팅

사용자 명시 승인에 따라 TEST 검증 소스를 NAS Production에 배포했다. Jenkins `RobinGraph-PROD #9`는 SUCCESS였고, 운영 컨테이너에서 healthy·active/semantic·tracing 활성화와 MLflow 실험 `50 / robingraph-prod`를 확인했다. 운영 공개 요청 3 POST와 3 GET은 모두 HTTP 200이었으며, 동일 질문·마스킹된 응답·태그가 실험 50의 고유 trace 3개와 일치했다.

이번 배포는 Git commit/push 없이 승인된 미커밋 snapshot을 일회성 Jenkins Replay로 빌드한 것이다. 소스 234파일은 SHA256 `6a95918a55332aa0195c07bf4e5a9c60a7cb006b67fd56d255d683f22c72c922`로 식별하고 immutable image digest와 연결했다. 기존 Jenkins 정의·매개변수·job properties와 TEST 컨테이너는 유지했다. 일반 main 자동 파이프라인은 여전히 lexical 설정이므로 이번 snapshot과 main의 동기화는 별도 승인 범위다.

이 작업의 배포·관측 검증은 완료했지만 RG-212 전체는 진행 중이다. 기존 TEST의 V2-07A 감사 거부와 V2-10B 수치 경계 보류는 해결하지 않았다. 공개 3건의 운영 관측 성공을 질의 일반화 완료나 모든 계획·감사 경로의 검증으로 해석하지 않는다.

| 구분 | 변경 사항 | 검증 결과 |
| --- | --- | --- |
| 요구사항 | 검증 소스 운영 반영과 질문 처리 원인 관측 | 사용자 명시 운영 승인 |
| 설계 | 일회성 Replay·불변 snapshot·immutable image | 커밋 ancestry와 실제 배포 source를 구분 |
| 코드 / 설정 | 기존 검증 소스·active/semantic·tracing true·실험 50 | 새 질의 수정 없이 검증 snapshot 배포 |
| 실서비스 배포 | NAS Production 교체 | Jenkins #9 SUCCESS·healthy |
| 검증 | Python 1,280 pass/40 skip, ops mock 16, Node 322 | 후보 3/3·공개 POST 3/3·GET 3/3·trace 3/3 |
| 형상 관리 | 기준 revision 834c535의 미커밋 snapshot | commit/push 없음·Jenkins 기존 설정 보존 |

TEST에서 검증한 시맨틱 질의 해석·원문 근거 검증·조건 미적용 metadata·특정 식물 먹이 자료 한계와 원인 관측 기능을 운영에 반영하도록 사용자가 승인했다. 운영에서 정상 답변, 의미가 모호해 되묻는 경우, 자료 부족으로 답하지 못하는 경우를 구분하고 실제 요청의 trace로 확인하는 것이 이번 배포의 완료 조건이었다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-시맨틱-질의-원인trace-운영배포]]
- [[Dev/index|Dev 인덱스]]
