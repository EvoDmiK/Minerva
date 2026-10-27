---
created: 2026-10-28
updated: 2026-10-28
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-27-RG603-답변피드백-MLflow-trace-연결]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RG-603] 답변별 사용자 피드백과 MLflow trace 연결 — 2026-10-27

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-27-RG603-답변피드백-MLflow-trace-연결]] · 분류 근거 {"인프라":0,"자동화":2,"관측성":25,"데이터":0}

## 1. 개요 및 목적

답변에 피드백 자격 token이 있을 때 세 버튼을 표시하고, 별도 API로 해당 답변의 MLflow trace에 HUMAN `user_feedback` assessment를 저장하도록 구현했다. 최종 TEST `2e822237c9dc`에서 세 평가 버튼의 첫 클릭 3/3과 키보드 Enter 1건이 모두 200이었고, 실험 33의 고유 trace 4개에 원래 질문·마스킹한 응답·원 rating이 일치하는 assessment가 각각 하나씩 저장됐음을 재조회했다.

기존 chat JSON 본문은 유지하고 trace ID와 24시간 유효 서명 capability를 응답 헤더로 전달한다. feedback 실패는 기존 답변을 바꾸지 않으며 재시도 가능한 장애와 영구 오류를 구분해 안내한다. 초기 첫 제출 503/400, 하네스 오류와 진단 assessment 8건은 최종 4건과 분리해 보존했다. 자동화가 생성한 HUMAN 유형 평가를 실제 사용자의 gold로 표시하지 않는다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 2. 해결 방안 및 설계
- 3. 주요 구현 내용
- 사용자 값
- 파일·계약
- 4. 검증 및 테스트 결과
- 최종 자동 검사
- 첫 TEST 관측과 후속 보완 이력
- 실제 TEST 브라우저·MLflow 검증
- 독립 후검
- 피드백 검토 사용법
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
chat 응답 + trace ID/서명 token 헤더
→ 해당 답변의 피드백 버튼 → POST /v1/chat/feedback
→ 환경·실험·root·서명 검증 → HUMAN user_feedback assessment
```

## 4. 검증 근거 및 트러블슈팅

답변에 피드백 자격 token이 있을 때 세 버튼을 표시하고, 별도 API로 해당 답변의 MLflow trace에 HUMAN `user_feedback` assessment를 저장하도록 구현했다. 최종 TEST `2e822237c9dc`에서 세 평가 버튼의 첫 클릭 3/3과 키보드 Enter 1건이 모두 200이었고, 실험 33의 고유 trace 4개에 원래 질문·마스킹한 응답·원 rating이 일치하는 assessment가 각각 하나씩 저장됐음을 재조회했다.

기존 chat JSON 본문은 유지하고 trace ID와 24시간 유효 서명 capability를 응답 헤더로 전달한다. feedback 실패는 기존 답변을 바꾸지 않으며 재시도 가능한 장애와 영구 오류를 구분해 안내한다. 초기 첫 제출 503/400, 하네스 오류와 진단 assessment 8건은 최종 4건과 분리해 보존했다. 자동화가 생성한 HUMAN 유형 평가를 실제 사용자의 gold로 표시하지 않는다.

RG-603은 진행 중(TEST 구현·검증 완료, 운영 승인 대기)으로 기록한다. 운영 배포·운영 실험 50 쓰기·Git commit/push·조류 DB 쓰기는 수행하지 않았다. RG-601·RG-602의 완료 상태와 RG-212 진행 중 및 잔여 문제는 변경하지 않는다.

| 구분 | 구현·현재 상태 | 경계 |
| --- | --- | --- |
| 요구사항 | 답변별 평가를 실제 trace와 연결 | 전체 질의 정확도 개선 작업 아님 |
| UI | token이 있는 답변에 세 버튼 | token 없는 과거 답변은 대상 아님 |
| API | POST /v1/chat/feedback | 기존 chat JSON 본문 불변 |
| 저장 | HUMAN user_feedback assessment | 실험·target·실제 root 검증 |
| 중복 | trace당 한 표, 같은 재시도 200·다른 값 409 | 단일 process lock; exactly-once 보장 아님 |
| 최종 검사 | Python 1,300 pass/40 skip, Node 326 pass | 실제 TEST assessment 4건 별도 재조회 |
| 배포·형상 | TEST 검증 완료·운영/Git 작업 없음 | 운영 승인 대기 |

기존 trace는 시스템이 어떤 경로와 이유로 답변했는지 보여 주지만 사용자가 답변을 유용하게 여겼는지, 질문을 잘못 이해했다고 느꼈는지, 답변이 틀렸다고 판단했는지는 수집하지 않았다. 시스템 판단 태그와 사용자 판단을 별도로 남겨 같은 요청의 입력·처리·응답과 함께 확인할 필요가 있다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-27-RG603-답변피드백-MLflow-trace-연결]]
- [[Dev/index|Dev 인덱스]]
