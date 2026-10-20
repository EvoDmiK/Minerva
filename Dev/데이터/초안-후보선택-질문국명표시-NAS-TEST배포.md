---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-15-후보선택-질문국명표시-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 후보 선택 후 질문을 종 이름으로 표시·NAS TEST 배포

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-15-후보선택-질문국명표시-NAS-TEST배포]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":0,"데이터":6}

## 1. 개요 및 목적

사용자가 후보 선택 후 `Anas platyrhynchos에 대해 알고 싶어`라는 질문이 채팅에 들어가는 것을 보여주며 종 이름으로 표시하도록 요청했다. 검토 국명이 있는 후보는 `청둥오리에 대해 알고 싶어`처럼 읽을 수 있게 표시하고, 먹이 등 원래 질문 주제를 유지하는 것이 목표다. 실제 조회 대상은 선택한 후보 그대로 유지해야 한다.

API는 후보 확인용 question의 오타 이름을 정규 학명으로 바꾸어 반환했다. UI는 이를 `appendUserMessage(question)`와 실제 제출에 함께 사용하므로 학명이 사용자 말풍선에 그대로 나타났다. 검색 실패나 잘못된 종 조회 문제가 아니라, 식별용 질문과 사용자 표시가 같은 문자열을 사용하는 문제였다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 확인한 원인과 변경 전후
- 변경 파일과 구현
- 검증 방법과 실제 결과
- NAS TEST 배포·소스 확인
- 기록·한계와 후속

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

API는 후보 확인용 question의 오타 이름을 정규 학명으로 바꾸어 반환했다. UI는 이를 `appendUserMessage(question)`와 실제 제출에 함께 사용하므로 학명이 사용자 말풍선에 그대로 나타났다. 검색 실패나 잘못된 종 조회 문제가 아니라, 식별용 질문과 사용자 표시가 같은 문자열을 사용하는 문제였다.

변경 후 후보의 검토된 `display_name`을 질문 표시용으로 사용한다. 후보 질문의 학명 부분만 표시 이름으로 바꾸고 나머지 문장은 그대로 둔다. 검토 국명이 없으면 기존 학명 표시를 유지한다. API가 반환한 확인용 질문과 profile 이름 필터는 학명을 그대로 사용하여 다른 종으로 해소되거나 고급 필터에 남은 이름으로 대상이 바뀌지 않게 했다.

표시와 실제 API 요청을 구분한다. POST의 question·filters.name은 기존 정규 학명이며 화면에만 국명 질문을 보여준다. 질문 원문, 확인 대화, busy/대화 초기화 guard, 영구 별칭을 저장하지 않는 정책은 그대로다. 후보 버튼의 국명·학명 병기, API 계약과 Neo4j 검색·색인 정책은 이번 변경 범위가 아니다.

- `src/robingraph/api/static/chat.js`: 기존 후보 콜백에 displayName을 전달한다. 표시 이름이 있으면 callback의 질문에서 학명 한 부분만 안전한 치환 함수로 바꾸어 appendUserMessage에 넣는다. 실제 submitQuestion에는 기존 question과 학명 필터를 전달한다. 말풍선은 기존 textContent 경로로 표시한다.
- `tests/frontend/chat_ui.test.js`: 먹이 확인 말풍선이 국명이고 학명이 드러나지 않는지, 실제 요청은 정규 학명인지 확인한다. 일반 질문도 국명으로 표시하고 이름이 없으면 학명으로 대체하는 검사를 추가했다.
- 실제 브라우저 검증 코드·JSON·스크린샷과 작업 기록을 추가했다. API/Python 소스·DB schema/data·벡터는 수정하지 않았다.

`node --test tests/frontend/chat_ui.test.js tests/frontend/birds_ui.test.js`를 실행해 307개 전부 통과했다(실패·제외0). fake DOM·fixture 검사이며 실제 DB 검증과 구분한다. 새 검사 초기에 수집한 말풍선 텍스트에 기존 사용자 라벨 `나`가 포함되어 문자열 전체 비교가 실패했다. 검증 대상을 질문 부분으로 맞춘 뒤 다시 실행해 통과했다. 제품 코드의 실패를 fixture 결과로 감추지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-15-후보선택-질문국명표시-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
