---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-10-근연관계-버튼화살표제거-TEST전용]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 근연 관계 버튼 화살표 제거 — TEST 전용

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-10-근연관계-버튼화살표제거-TEST전용]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":0,"데이터":0}

## 1. 개요 및 목적

사용자가 더 알아보기의 네 버튼을 통일한 화면에서 근연 관계 버튼에만 남은 화살표를 제거하도록 요청했다. 근연 관계 버튼 앞의 접힘·펼침 표시만 없애고 버튼 크기 통일과 탐색 기능을 유지한다. 사용자 지시에 따라 TEST에만 반영한다.

graphify query 후 `src/robingraph/api/static/styles.css`에서 두 ::before 규칙을 확인했다. `.species-related > button[aria-expanded]`에 ▸, expanded=true에 ▾ 문자를 CSS로 붙였다. HTML이나 버튼의 실제 이름에 들어 있는 문자가 아니었다.

## 2. 핵심 아키텍처 및 원칙

- 요청과 목표
- 원인·변경 파일·전후 동작
- 검증과 결과
- 배포·커밋·기록
- 한계·후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 더 알아보기의 네 버튼을 통일한 화면에서 근연 관계 버튼에만 남은 화살표를 제거하도록 요청했다. 근연 관계 버튼 앞의 접힘·펼침 표시만 없애고 버튼 크기 통일과 탐색 기능을 유지한다. 사용자 지시에 따라 TEST에만 반영한다.

graphify query 후 `src/robingraph/api/static/styles.css`에서 두 ::before 규칙을 확인했다. `.species-related > button[aria-expanded]`에 ▸, expanded=true에 ▾ 문자를 CSS로 붙였다. HTML이나 버튼의 실제 이름에 들어 있는 문자가 아니었다.

`node --test tests/frontend/*.test.js`: 303개 통과, 실패·취소·건너뛰기 0. fake DOM·단위 회귀이며 실제 DB 전수 검증은 아니다. 변경 규모가 CSS 두 줄 삭제이므로 새 단위 테스트는 추가하지 않았다. `git diff --check` 통과, `graphify update .` 완료. 기존 SQL 파서 미설치 경고는 이번 CSS 변경과 무관한 추출 범위 제한이다.

배포된 TEST 자산을 사용하는 Chrome 390·1280px에서 접힘 → 펼침 → 다시 접힘의 6상태를 확인했다. getComputedStyle(button, "::before").content가 항상 none이며 aria-expanded는 false → true → false로 정상 바뀌었다. 페이지 오류 0. 입력은 이전 실제 TEST profile 응답을 재생했고 탐색 HTTP는 빈 groups 모의 응답으로 처리했다. 공개 chat.js·styles.css는 로컬 파일과 바이트 단위로 일치했다. 별도 실제 health와 청둥오리 profile 질문 API도 정상 응답했다. 증거는 docs/verification/assets/2026-10-10-related-arrow-test.json, 2026-10-10-related-arrow-assets.json. 브라우저 도구는 /tmp/rg-answer-names-browser/related-arrow.cjs다.

앱 커밋 `06817474f5003bb359579b24868aa1ffa5cb8cdf`, origin/dev-codex push 완료. 표준 NAS 패키지 SHA-256은 `117bd0ce569a8a7cdaf7bf0d00a6d8883b4de07fa369b2d3b1a01a5c009f4754`이며 NAS에서 아카이브 해시를 검증했다. 이전 TEST 환경만 복사하고 PG가 robingraph_test인지 확인했다. 인증 정보는 문서에 넣지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-10-근연관계-버튼화살표제거-TEST전용]]
- [[Dev/index|Dev 인덱스]]
