---
created: 2026-10-29
updated: 2026-10-29
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-28-그래프-질의-안내-UI-정리]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RG-213 후속 UI / 검색·그래프 질의] 그래프 질의 안내·유의사항 단일 영역 통합 및 중복 제거 (TEST 배포 검증 완료 · 운영 미반영) — 2026-10-28

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-28-그래프-질의-안내-UI-정리]] · 분류 근거 {"인프라":0,"자동화":1,"관측성":3,"데이터":1}

## 1. 개요 및 목적

> **문서 상태: UI 개선 및 TEST 배포 검증 완료 (운영 미반영)**  
> 그래프 질의(`graph_query`) 결과 렌더링 시 `payload.limitations`와 최상위 `answer.warnings`의 중복 안내 문구를 단일 접힘 영역(`.graph-query-notes`)으로 일원화하고, 주황색 경고 테마를 중립 색조로 정돈한 후속 UI 개선을 완료하였다.  
> TEST 환경 배포(`notice-ui-dc72ada65dbf-46b2cc`) 후 실제 API 2회 호출(8/8 pass) 및 Headless Chromium(390px, 1280px) 실환경 렌더링 검증을 마쳤으며, 운영(Production NAS) 배포 및 Git 커밋·푸시는 수행하지 않았다.

---

## 2. 핵심 아키텍처 및 원칙

- 작업 및 변경 결과 요약
- 1. 작업 배경 및 원인 분석
- 발생 현상
- 원인 분석: 2가지 출력 경로
- 2. 해결 방안 및 구현 내용
- 수정 및 추가 파일 목록
- 핵심 구현 상세
- 3. 검증 및 테스트 결과
- 1) 단위 테스트 (로컬 Node)
- 2) 실서버 API 검증 (`https://robingraph-test.dove-nest.com/v1/chat`)
- 3) 실환경 브라우저 검증 (Headless Chromium CDP)
- 4. 배포 및 형상 관리
- 5. 한계 및 미검증 범위
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

> **문서 상태: UI 개선 및 TEST 배포 검증 완료 (운영 미반영)**  
> 그래프 질의(`graph_query`) 결과 렌더링 시 `payload.limitations`와 최상위 `answer.warnings`의 중복 안내 문구를 단일 접힘 영역(`.graph-query-notes`)으로 일원화하고, 주황색 경고 테마를 중립 색조로 정돈한 후속 UI 개선을 완료하였다.  
> TEST 환경 배포(`notice-ui-dc72ada65dbf-46b2cc`) 후 실제 API 2회 호출(8/8 pass) 및 Headless Chromium(390px, 1280px) 실환경 렌더링 검증을 마쳤으며, 운영(Production NAS) 배포 및 Git 커밋·푸시는 수행하지 않았다.

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **요구사항 및 원인** | 안내 문구 중복 노출 및 과도한 경고 색조 정돈 | `payload.limitations`와 `answer.warnings`의 2중 출력 경로로 인한 동일 문구 중복 및 주황색 경고 박스 노출 문제 해결 |
| **설계 및 해결 방안** | 단일 접힘 영역 통합 및 중립 테마 전환 | 그래프 질의 시 외곽 `.warnings` 목록을 억제하고, 내부에서 `Array.from(new Set(...))`으로 중복 제거 후 카운트 표시, 배경/테두리 중립화 |
| **수정 파일** | 3개 파일 (JS 1, CSS 1, Test 1) | `chat.js`, `styles.css`, `tests/frontend/chat_ui.test.js` |
| **TEST 배포** | TEST 전용 배포 완료 (운영 배포 없음) | 이미지 `robingraph-api:test-notice-ui-dc72ada65dbf`, 릴리스 `notice-ui-dc72ada65dbf-46b2cc` (healthy) |
| **검증 결과** | 단위 333건, 실 API 8/8, 실 브라우저 2종 통과 | 프런트엔드 단위 333 pass(0 fail, 0 skip), 실 API 8 pass, Chromium 390px/1280px 중복 제거 및 무넘침 확인 |
| **형상 관리** | 커밋·푸시 미수행 (워킹 트리 유지) | 운영 NAS 미배포, Git commit/push 없음, DB 쓰기 0건 |

* **대상 환경**: TEST 환경 전용 (`robingraph-test`)
* **배포 승인**: Root 승인 (msg_2fbf1bf9c445)
* **배포 이미지**: `robingraph-api:test-notice-ui-dc72ada65dbf` (arm64, healthy)
* **릴리스 경로**: `/Users/kimdove/robingraph-test/releases/notice-ui-dc72ada65dbf-46b2cc`
* **소스 스냅샷**: `snapshot-dc72ada65dbf` (235개 파일 해시 일치, base: `318e7731fda8`)
* **운영 반영 및 Git**:
  * Production NAS 배포 없음 (`production_changed: false`).
  * Git `commit` 및 `push` 미수행 (`git_commit_push: false`, 워킹 트리 작업 상태 유지).
  * DB / Neo4j / n8n 쓰기 0건.

* **물리 모바일 기기 미검증**: 실제 물리 스마트폰 검사는 생략하고 Chromium CDP 터치 에뮬레이션으로 대체함.
* **기타 브라우저**: WebKit(Safari), Gecko(Firefox) 렌더링 검사는 수행하지 않음.
* **백엔드 스위트 생략**: 프런트엔드 3개 파일 한정 변경으로 Python 백엔드 전체 회귀(1,359건) 재실행은 생략함.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-28-그래프-질의-안내-UI-정리]]
- [[Dev/index|Dev 인덱스]]
