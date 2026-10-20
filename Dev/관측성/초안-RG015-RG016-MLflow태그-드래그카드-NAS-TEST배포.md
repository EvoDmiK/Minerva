---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-08-RG015-RG016-MLflow태그-드래그카드-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-602 MLflow 응답 구분·RG-405 마우스 드래그 카드 뒤집기

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-08-RG015-RG016-MLflow태그-드래그카드-NAS-TEST배포]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":26,"데이터":10}

## 1. 개요 및 목적

작업일: 2026-10-08 (KST). 브랜치: `dev`.

사용자가 오늘 RG-405까지 진행하도록 요청했다. 백로그의 권장 실행 순서인 RG-602 → RG-405에 따라 두 작업을 함께 처리했다. RG-202 HippoRAG 검색과 RG-406 한국 서식 토글은 대기 상태를 유지한다. 기존 최후순위 보류 작업의 재개는 이번 범위에 포함하지 않는다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 범위
- 원인과 변경 전후
- RG-602
- RG-405
- 변경 파일과 역할
- 협업과 검토 근거
- 테스트 방법과 실제 결과
- NAS TEST·MLflow 실서버·브라우저
- 실제 MLflow 저장·검색
- MLflow 화면에서 찾기
- 실제 NAS 카드 브라우저 검증
- 커밋·배포 정보
- 작업 관리 문서 동기화
- 남은 한계와 후속

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

RG-602은 MLflow에서 정상 답변과 이름 미발견·추가 확인·조회 장애를 구별하는 작업이다. 신고 화면의 “박새에 대해 알고 싶어”는 HTTP 성공이어도 `profile=null`이므로 실행 성공과 유효한 답변 제공 여부를 따로 관측해야 한다. 제공 화면만으로 박새 자료가 없다고 확정하지 않는다. RG-405는 기존 버튼 외에 마우스 드래그로 도감 카드 앞·뒷면을 전환하는 작업이다.

태그 값은 허용 집합으로 제한한다. 질문·이름·인증 정보는 새 태그에 넣지 않는다. 정상 답변은 `none/none`, 분류할 수 없는 미응답은 `unknown/unknown`을 쓴다. 조회기 미설정과 외부 조회 실패는 모니터링 태그에서 `error`로 구별하되, 기존 HTTP 200 `abstain` 응답과 MLflow 실행 상태 `OK`를 강제로 바꾸지 않는다. HTTPException이 실제 전파되면 기존대로 trace 실행 상태가 `ERROR`가 된다.

추적 비활성 상태에서는 새 기록 경로가 동작하지 않고, span 시작 실패·태그 쓰기 실패도 API 응답을 바꾸지 않는다. 비-chat 라우트는 성공 시 기본 answer/none을 기록하고 HTTP 404·400/422·503에 상태코드 기반 사유를 기록한다.

| 파일 | 구현 내용 |
|---|---|
| `src/robingraph/api/app.py` | 응답 분기의 구조화 사유, 라우트 태그 기록·예외 처리 |
| `src/robingraph/tracing.py` | ContextVar 수집기, 허용 값·결과 매핑, fail-open 태그 쓰기 |
| `tests/test_mlflow_response_tags.py` | 결과별 분기, 비활성·기록 실패·동시성, 실제 SDK 로컬 exporter 검증 |
| `scripts/verify_mlflow_response_tags.py` | TEST 요청 후 실제 MLflow 서버에서 태그 필터로 새 trace 검색 |
| `docs/mlflow-tracing.md` | 태그 의미·검색 예제·운영 한계 |
| `src/robingraph/api/static/chat.js` | 드래그 상태·임계값·회전·취소·조작 제외·안내 |
| `src/robingraph/api/static/styles.css` | 드래그 커서·피드백·fine pointer 및 reduced-motion 스타일 |
| `tests/frontend/chat_ui.test.js` | 제스처·취소·중복 click·선택 영역·기존 버튼 회귀 |

[orchestration 스킬](/Users/kimdove/.agents/skills/orchestration/SKILL.md)을 사용해 실제 Orca run `run_e82e62b9bbeb`에서 작업을 분담했다. Claude 워커가 서버 태그와 화면 구현을 각각 담당하고, Antigravity가 읽기 전용 독립 코드 검토를 맡았다. Codex 주 담당은 요구사항 대조·수정 지시·실제 DB·MLflow·NAS·브라우저·문서·Git을 통합했다. 런타임 receipt의 모델 필드가 null이므로 워커의 실제 모델명은 미확인으로 기록한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/6xx 관측·평가/2026-10-08-RG015-RG016-MLflow태그-드래그카드-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
