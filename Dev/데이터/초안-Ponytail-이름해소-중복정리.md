---
created: 2026-10-27
updated: 2026-10-27
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-26-Ponytail-이름해소-중복정리]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# Ponytail 이름 해소 중복 정리·응답 보존 검증 — 2026-10-26

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-26-Ponytail-이름해소-중복정리]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":0,"데이터":3}

## 1. 개요 및 목적

사용자의 Ponytail 리팩토링 요청에 따라 `services.py`의 두 이름 해소 경로에 반복된 resolver 호출·검증을 `_resolve_taxon_name` 하나로 모았다. 앱 변경은 한 파일이며 16줄 helper와 두 호출로 정리해 순 4줄을 줄였다. graph/profile별 응답 렌더링·질문 재작성·예외 처리·trace 경계는 유지했다.

fixture API 60건의 전후 HTTP 상태·응답 본문·resolver 인자와 scope·후속 호출 횟수가 동일했다. 이 비교는 실제 DB·provider 호출 0인 모의 환경 검사다. 전체 Python 검사는 1,327 실행·1,287 통과·40 skip·0 실패(24.973초), graphify 갱신과 git diff check도 통과했다. TEST/운영 배포나 commit/push는 수행하지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 2. 해결 방안 및 설계
- 3. 주요 구현 내용
- 4. 검증 및 테스트 결과
- 전후 fixture API 비교
- 독립 코드 리뷰
- 전체 회귀 검사와 graphify
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
graph 경로 ─┐
            ├─ _resolve_taxon_name → 각 경로의 기존 응답·예외·trace 처리
profile 경로┘
```

## 4. 검증 근거 및 트러블슈팅

사용자의 Ponytail 리팩토링 요청에 따라 `services.py`의 두 이름 해소 경로에 반복된 resolver 호출·검증을 `_resolve_taxon_name` 하나로 모았다. 앱 변경은 한 파일이며 16줄 helper와 두 호출로 정리해 순 4줄을 줄였다. graph/profile별 응답 렌더링·질문 재작성·예외 처리·trace 경계는 유지했다.

fixture API 60건의 전후 HTTP 상태·응답 본문·resolver 인자와 scope·후속 호출 횟수가 동일했다. 이 비교는 실제 DB·provider 호출 0인 모의 환경 검사다. 전체 Python 검사는 1,327 실행·1,287 통과·40 skip·0 실패(24.973초), graphify 갱신과 git diff check도 통과했다. TEST/운영 배포나 commit/push는 수행하지 않았다.

| 구분 | 변경 사항 | 근거 |
| --- | --- | --- |
| 요구사항 | Ponytail 방식의 최소 리팩토링 | 중복 이름 해소 두 곳만 정리 |
| 설계 | 기존 검증·resolver 동작을 단일 helper로 재사용 | 새로운 parser·추상화·의존성 없음 |
| 앱 수정 | services.py 한 파일, 순 4줄 감소 | 16줄 helper와 두 호출 |
| 회귀 검사 | invalid identity 외부 API 검사 1 method·16 subcases 추가 | 응답 계약 보호 |
| 전후 비교 | fixture API 60건 동일 | 15 variants × 2 routes × 2 scopes |
| 배포 / Git | 미실행 | 리팩토링 요청 범위 유지 |

graph와 profile의 이름 해소 경로에 같은 resolver 호출 및 identity 검증이 반복됐다. 같은 검증을 두 곳에서 유지하면 향후 한 경로만 고치는 불일치 위험이 있어, 이미 쓰는 동작을 작은 공통 helper로 정리했다. 이는 새로운 질의 지원이나 기존 오거절을 수정하는 작업이 아니다.

- 두 호출부의 공통 이름 해소·identity 확인을 `_resolve_taxon_name`으로 모았다.
- graph/profile별 후속 로직은 각 호출부에 유지했다. 공통화 범위를 응답 생성이나 추적 전체로 넓히지 않았다.
- 기존 오류 처리와 검증을 삭제하지 않고 이동·재사용했다.
- fixture 전후 응답뿐 아니라 resolver 호출 인자·scope와 후속 호출 횟수도 비교해 숨은 동작 변화 여부를 확인했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-26-Ponytail-이름해소-중복정리]]
- [[Dev/index|Dev 인덱스]]
