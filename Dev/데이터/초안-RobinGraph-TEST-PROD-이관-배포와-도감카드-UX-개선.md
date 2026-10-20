---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-RobinGraph-TEST-PROD-이관-배포와-도감카드-UX-개선]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# [RobinGraph] TEST → PROD 데이터 이관·PROD 배포와 도감 카드 UX 개선 (카드 스크롤, 프레임 두께, 차트 목록, 파비콘)

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-RobinGraph-TEST-PROD-이관-배포와-도감카드-UX-개선]] · 분류 근거 {"인프라":0,"자동화":1,"관측성":0,"데이터":25}

## 1. 개요 및 목적

TEST 서버에만 올라가 있던 Neo4j·PostgreSQL 데이터를 **PROD로 전부 이관**하고, PROD API를 최신 코드로 네 차례 배포했다. 이어서 도감 카드의 사용성 문제를 고쳤다. 뒷면 토글(`측정값 더 보기`, `분류 계통 보기`, 도넛 아래 `항목·비율`)을 열면 카드가 작게 줄어들던 문제를 **정상 크기 유지 + 스크롤**로 바꾸고, 카드를 둘러싼 은색 프레임의 두께를 토글 상태와 상관없이 같게 맞췄으며, `항목·비율` 목록을 다시 디자인하고 `자료 1` 표시를 걷어냈다. 브랜드 파비콘(꼬까울새)을 추가하면서 TEST 탭만 파란색으로 구분되게 했다.

문서·운영 쪽에서는 작업 ID를 카테고리 번호(1xx DB, 2xx 검색, … 9xx 기타)로 바꾸고 기존 RG-0xx 표기를 문서 안에서 새 번호로 치환했으며, 문헌 Chunk 검색을 PostgreSQL(pgvector)로 옮기는 설계(ADR-0007)와 백로그 RG-101을 등록했다. 작업 중 쌓인 NAS 임시 파일은 삭제 없이 `/volume3`로 옮겼다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 완료 결과
- 1. 배경 및 문제점
- 2. 주요 변경 및 구현 내용
- 2.1 TEST → PROD 데이터 이관
- 2.2 PROD API 배포
- 2.3 카드 토글 스크롤·프레임 두께·차트 목록
- 2.4 파비콘
- 2.5 문서·체계·운영
- 3. 검증 결과
- 3.1 실제 DB·서버 대상 확인
- 3.2 자동 테스트와 실제 브라우저
- 3.3 확인하지 못했거나 알려야 할 점
- 4. 형상 관리
- 5. 관련 링크

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

TEST 서버에만 올라가 있던 Neo4j·PostgreSQL 데이터를 **PROD로 전부 이관**하고, PROD API를 최신 코드로 네 차례 배포했다. 이어서 도감 카드의 사용성 문제를 고쳤다. 뒷면 토글(`측정값 더 보기`, `분류 계통 보기`, 도넛 아래 `항목·비율`)을 열면 카드가 작게 줄어들던 문제를 **정상 크기 유지 + 스크롤**로 바꾸고, 카드를 둘러싼 은색 프레임의 두께를 토글 상태와 상관없이 같게 맞췄으며, `항목·비율` 목록을 다시 디자인하고 `자료 1` 표시를 걷어냈다. 브랜드 파비콘(꼬까울새)을 추가하면서 TEST 탭만 파란색으로 구분되게 했다.

모든 변경은 TEST에서 먼저 확인한 뒤 사용자의 승인으로 PROD에 배포했다. 사용자가 PROD 화면과 모바일을 직접 확인했다.

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **데이터 이관** | TEST → PROD Neo4j·PostgreSQL 전체 이관 | Neo4j 노드 약 16.2만→474,998, 관계 262,856→543,637, PG `ingest` 스키마(`source_record` 57,625행 등). 사전에 PROD 백업, 이관 후 개수·인덱스(22개 ONLINE)·API 검증 |
| **PROD 배포** | API 4회 배포 | `3e639ce` → `336d987`(파비콘) → `5fb401e`(토글 스크롤) → `e90ff85`(프레임·차트·TEST 파비콘). 매번 preflight·dry-run·verify, 롤백용 이전 이미지 보존 |
| **외부 연동** | PROD에 Jev·Gemini 설정 추가 | TEST env와 키 이름을 비교해 PROD에 없던 11개를 NAS 안에서만 복사. 채팅 질문 `route_method: jev`로 응답 확인 |
| **카드 UX** | 토글을 열면 카드가 줄지 않고 스크롤 | 두 토글과 차트 `항목·비율`에 적용. 닫거나 뒤집으면 맞춤 상태로 복귀 |
| **카드 UX** | 프레임 두께 통일 | PC 좌우 19~76px → 12px, 모바일 8px. 팝업 폭이 축소된 카드를 따라가도록 변경 |
| **카드 UX** | `항목·비율` 다듬기, `자료 1` 제거 | 알약 토글, 색 점·이름·오른쪽 정렬 퍼센트, 0% 행 흐리게. 주의 문구만 남기고 없으면 숨김 |
| **브랜딩** | 꼬까울새 파비콘 | ico·32/192px·apple-touch 4종. TEST 배포는 색상을 파랑으로 돌린 변형 서빙 |
| **문서** | README IUCN 등급별 카드 색 표 | 등급 8행, 코드(`chat.js`, `styles.css`)에서 확인한 hex 값 |
| **체계** | 카테고리별 작업 ID | 대응표(`docs/task-ids.md`), 백로그 ToC·이력 접이식, 문서 내 표기 치환(Obsidian 42개·저장소 44개 파일) |
| **설계** | 문헌 Chunk 검색 저장소 분리(ADR-0007) | PG(pgvector)=본문·벡터, Neo4j=관계·정책 기준. 백로그 RG-101 등록 |
| **운영 정리** | NAS 임시 파일 이동 | 706MB를 `/volume3/Birds-Nest/backups/robingraph-deploy/`로 이동(삭제 없음) |
| **형상 관리** | `main` 병합 | 5회 병합, 매번 CI 7개 job 성공(최종 `ab977b8`) |

1. **PROD에 데이터가 없었다.** PROD Neo4j에는 AviList 분류(약 16.2만 노드)뿐이고 PostgreSQL `ingest`는 비어 있었다. 저장소에는 TEST/PROD 간 이관 절차가 없었다(적재 스크립트는 원본→DB 용도).
2. **카드 토글이 카드를 줄였다.** 카드는 항상 프레임 높이에 맞춰 통째로 축소되도록 만들어져 있어, 뒷면 토글을 열면 카드 전체가 더 작아져 글씨가 읽기 어려웠다. 같은 원리로 PC에서는 축소된 카드 좌우의 은색 프레임만 두꺼워졌다.
3. **TEST와 PROD 탭이 구분되지 않았다.** 파비콘 자체가 없었고, 추가한 뒤에도 같은 모양이면 헷갈린다.
4. **작업 번호가 등록 순서뿐이라** DB·검색·UI·데이터 작업이 섞여 보였다.
5. **문헌 Chunk가 계속 늘어난다.** Neo4j에 본문·벡터를 두면 메모리(16GB NAS 공유)를 압박하고 정형 조건 사전 필터가 불편하다.

| 항목 | 결과 |
| --- | --- |
| PROD Neo4j | 노드 474,998 / 관계 543,637(TEST와 일치), 인덱스 LOOKUP 2·FULLTEXT 1·VECTOR 1·RANGE 18 모두 ONLINE, 제약조건 17개 |
| PROD PostgreSQL | `source_record` 57,625 / `ingestion_run` 33 / `source_release` 10 / `source_dataset` 13(TEST와 일치) |
| PROD 최종 배포 `e90ff85` | healthy·재시작 0·OCI revision 일치, `verify` ok(`deployment_target: prod`), `verify_api_deployment.py` `passed: true` |
| PROD 채팅 | `흰뺨검둥오리에 대해서 알려줘` → 200, `route_method: jev`, `disposition: answer`, 경고 없음 (Jev·Gemini 설정 추가 후) |
| PROD 아이콘 | 기본(주황) 4개 서빙, TEST 변형과 해시가 다름 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-RobinGraph-TEST-PROD-이관-배포와-도감카드-UX-개선]]
- [[Dev/index|Dev 인덱스]]
