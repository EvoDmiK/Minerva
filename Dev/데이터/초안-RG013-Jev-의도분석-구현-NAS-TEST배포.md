---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/3xx 질문 의도·LLM/2026-10-08-RG013-Jev-의도분석-구현-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-301 — Jev 질문 의도 분석 구현·검증 기록

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/3xx 질문 의도·LLM/2026-10-08-RG013-Jev-의도분석-구현-NAS-TEST배포]] · 분류 근거 {"인프라":1,"자동화":1,"관측성":15,"데이터":19}

## 1. 개요 및 목적

“청둥오리 아종 알려줘”, “흰뺨검둥오리 아종 알려줘”가 자동 분류에서 막히는 문제를 해결한다. 기존 규칙에는 아종 목록 요청이 없고, 임베딩 라우터의 capability는 분류·관찰·근거뿐이다. 분류를 profile로 바꾸는 것만으로는 전체 질문이 이름으로 넘어가므로 이름 구간 추출과 실제 아종 핸들러 연결이 함께 필요했다.

사용자는 `thejevai.com/settings`에서 키를 발급했다. 초기 smoke의 TypeSafe 직접 주소 401은 제공자 불일치였으며, 해당 제공자 주소와 `typesafe/jev-1.13`로 HTTP 200을 확인했다. 실제 응답은 `code=0 → data.result.answers.intent`이고, 기본 Python User-Agent에서는 403/error1010이 발생했다. 서버 클라이언트는 고유 User-Agent와 실제 응답 래퍼를 사용한다. 인증 값은 이 기록에 포함하지 않는다.

## 2. 핵심 아키텍처 및 원칙

- 배경·목표와 확인한 원인
- 협업·변경 파일·구현
- 테스트와 실제 API 평가
- 배포·커밋과 후속 실제 검증
- 남은 한계·후속 사항
- 제공된 테스트 DB로 통합 테스트 재실행 (2026-10-08)
- 재실행 배경과 원인 정정
- 실행 환경과 격리
- 실행 중 실패와 수정
- 최종 검증 결과
- 변경 파일·배포·커밋 및 남은 한계

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자는 `thejevai.com/settings`에서 키를 발급했다. 초기 smoke의 TypeSafe 직접 주소 401은 제공자 불일치였으며, 해당 제공자 주소와 `typesafe/jev-1.13`로 HTTP 200을 확인했다. 실제 응답은 `code=0 → data.result.answers.intent`이고, 기본 Python User-Agent에서는 403/error1010이 발생했다. 서버 클라이언트는 고유 User-Agent와 실제 응답 래퍼를 사용한다. 인증 값은 이 기록에 포함하지 않는다.

Orca run `run_8bdb7fd51302`에서 역할을 나눴다. Codex가 구현·API 실행·회귀·배포를 담당하고, Claude가 120문항 정답표를 작성했다(워커 자기 보고 모델 `claude-sonnet-5-5`; 런타임 모델 필드는 미제공). Antigravity가 제공자 문서·응답 계약·인증 리다이렉트·확률 검증·불확실/장애 분리와 구현을 읽기 전용으로 검토했다. Antigravity의 실제 모델명은 확인하지 못했다. Claude task `task_cdef8bdada28`, Antigravity task `task_8380e4f86d01`은 성공 정산 후 해제했다. 독립 검토는 유료 호출·DB·브라우저 테스트를 대신하지 않는다.

| 파일 | 최종 변경 내용 |
|---|---|
| `src/robingraph/api/jev_router.py` | 서버 HTTP 클라이언트, 설정·호환 키 변수·롤백 선택, Choice/확률 검증, 제한된 HTTP 재시도, 비밀 비노출, MLflow span |
| `src/robingraph/api/question_entities.py` | 원문 이름 구간 추출, 접속사·다중 학명 거절, 기존 검토 통칭 대조 |
| `src/robingraph/api/app.py` | 명시/규칙 우선, Jev 세부 의도 연결, 불확실 확인 질문·장애 대체, 필터 일치, 아종 부모/릴리스 대조와 응답 |
| `src/robingraph/cli.py` | Neo4j 서버 시작 시 설정된 Jev 주입 |
| `src/robingraph/api/static/chat.js` | 아종 응답을 즉시 펼쳐 표시, 기존 안전한 출처·카드 재사용, 중복 목록 HTTP 제거 |
| `.env.example`, `.env.nas.example` | 키·모델·timeout·threshold·router 선택 예시 |
| `tests/test_jev_router.py`, `tests/frontend/chat_ui.test.js` | 실제 응답 형식 모의 검증, 오류/불확실/필터/회귀, 즉시 표시·부모/분류판 불일치 거절 |
| `tests/fixtures/jev_intent_eval.json`, `scripts/evaluate_jev_intents.py` | 120문항, calibration/heldout 분리, opt-in 실제 API 비교 평가 |
| `docs/jev-intent-routing.md`, 이 기록·JSON 첨부 | 설정·계약·검증 범위·한계와 실제 결과 |

명시적 모드와 기존 확실한 규칙은 기존 결과를 유지하며 Jev를 호출하지 않는다. 추가 자동 경로만 13개 의도를 판단한다. 아종 목록은 `selected_intent=profile`, `route_method=jev`, `question_answer.topic=subspecies`, `result.subspecies`로 기존 profile 계약에 추가했다. 낮은 확신도·불확실·원문 이름 추출 실패는 조회를 강제하지 않는다. 관찰 날짜·장소는 자유형 모델 출력으로 생성하지 않고 기존 검증 필터를 요구한다. 답변 생성 모델과 RG-202/RG-602은 변경하지 않는다.

모의·회귀와 실제 외부 검증을 분리한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/3xx 질문 의도·LLM/2026-10-08-RG013-Jev-의도분석-구현-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
