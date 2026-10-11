---
created: 2026-10-09
date: 2026-10-09
project: RobinGraph
type: work-log
status: completed
tags:
  - robingraph
  - neo4j
  - postgresql
  - nas
  - deploy
  - production
  - ui
  - ponytail
---

# [RobinGraph] TEST → PROD 데이터 이관·PROD 배포와 도감 카드 UX 개선 (카드 스크롤, 프레임 두께, 차트 목록, 파비콘)

## 요약

TEST 서버에만 올라가 있던 Neo4j·PostgreSQL 데이터를 **PROD로 전부 이관**하고, PROD API를 최신 코드로 네 차례 배포했다. 이어서 도감 카드의 사용성 문제를 고쳤다. 뒷면 토글(`측정값 더 보기`, `분류 계통 보기`, 도넛 아래 `항목·비율`)을 열면 카드가 작게 줄어들던 문제를 **정상 크기 유지 + 스크롤**로 바꾸고, 카드를 둘러싼 은색 프레임의 두께를 토글 상태와 상관없이 같게 맞췄으며, `항목·비율` 목록을 다시 디자인하고 `자료 1` 표시를 걷어냈다. 브랜드 파비콘(꼬까울새)을 추가하면서 TEST 탭만 파란색으로 구분되게 했다.

문서·운영 쪽에서는 작업 ID를 카테고리 번호(1xx DB, 2xx 검색, … 9xx 기타)로 바꾸고 기존 RG-0xx 표기를 문서 안에서 새 번호로 치환했으며, 문헌 Chunk 검색을 PostgreSQL(pgvector)로 옮기는 설계(ADR-0007)와 백로그 RG-101을 등록했다. 작업 중 쌓인 NAS 임시 파일은 삭제 없이 `/volume3`로 옮겼다.

모든 변경은 TEST에서 먼저 확인한 뒤 사용자의 승인으로 PROD에 배포했다. 사용자가 PROD 화면과 모바일을 직접 확인했다.

## 완료 결과

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

---

## 1. 배경 및 문제점

1. **PROD에 데이터가 없었다.** PROD Neo4j에는 AviList 분류(약 16.2만 노드)뿐이고 PostgreSQL `ingest`는 비어 있었다. 저장소에는 TEST/PROD 간 이관 절차가 없었다(적재 스크립트는 원본→DB 용도).
2. **카드 토글이 카드를 줄였다.** 카드는 항상 프레임 높이에 맞춰 통째로 축소되도록 만들어져 있어, 뒷면 토글을 열면 카드 전체가 더 작아져 글씨가 읽기 어려웠다. 같은 원리로 PC에서는 축소된 카드 좌우의 은색 프레임만 두꺼워졌다.
3. **TEST와 PROD 탭이 구분되지 않았다.** 파비콘 자체가 없었고, 추가한 뒤에도 같은 모양이면 헷갈린다.
4. **작업 번호가 등록 순서뿐이라** DB·검색·UI·데이터 작업이 섞여 보였다.
5. **문헌 Chunk가 계속 늘어난다.** Neo4j에 본문·벡터를 두면 메모리(16GB NAS 공유)를 압박하고 정형 조건 사전 필터가 불편하다.

---

## 2. 주요 변경 및 구현 내용

### 2.1 TEST → PROD 데이터 이관
- TEST(Mac mini `neo4j-test`, 5.26 Community)와 PROD(NAS `neo4j`, 2026.08.1)는 버전이 달라 `neo4j-admin database dump/load` 후 `migrate`로 스토어를 올렸다.
- 순서: ① TEST 덤프 ② PROD 이관 전 백업 ③ 덤프를 NAS로 전송(체크섬 일치) ④ PROD 중지·로드·마이그레이트·시작 ⑤ 개수·인덱스 비교. PostgreSQL은 `robingraph_test`의 `ingest` 스키마를 `pg_dump`로 떠서 `robingraph` DB에만 복원(같은 서버의 n8n DB는 건드리지 않음).
- 설계 논의(관찰·문헌을 RDB에 둘지)는 구조를 바꾸지 않고 그대로 이관하기로 정리했다. → [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-09-TEST-PROD-데이터-이관|상세 기록]], [[Work/RobinGraph/검토자료/2026-10-09-DB-저장소-분담-논의|DB 저장소 분담 논의]]

### 2.2 PROD API 배포
- 배포 방식은 `docs/nas-deployment.md` §9의 릴리스 묶음(`package_nas_release.sh`)이다. 아카이브 SHA-256과 MANIFEST를 NAS에서 검증하고, 새 체크아웃에 직전 PROD env를 복사해 이미지 태그만 바꿔 `deploy`했다.
- `3e639ce` 배포 후 PROD env에 Jev·Gemini 키가 없어 TEST와 키 이름을 비교해 11개를 추가하고 재배포했다. → [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-PROD-API-3e639ce-배포|상세 기록]]

### 2.3 카드 토글 스크롤·프레임 두께·차트 목록
- **스크롤**: `fitCard()`가 열린 토글(`.card-details-scroll`, 차트 `항목·비율`)을 감지하면 너비 기준 크기만 유지하고 프레임을 세로 스크롤하게 한다. 평소의 "스크롤 없음"은 그대로이고 토글이 열린 동안에만 허용한다. 모바일은 세로 팬을 브라우저에 맡기고 좌우 스와이프 뒤집기는 JS가 처리한다.
- **프레임 두께**: 팝업 폭이 축소된 카드를 따르도록 모바일 로직을 PC에도 적용했다. 한 줄만 바꿨을 때 간격이 그대로여서 원인을 찾아보니 PC의 카드 표면이 프레임 폭을 따라 이중으로 줄고 있었고, 측정한 폭을 고정해 해결했다.
- **목록**: 목록 행을 `swatch / 이름 / 구분자 / 퍼센트` 구조로 바꿨다(구분자는 CSS로 숨겨 텍스트 추출 호환 유지). 색은 도넛과 같은 팔레트를 공유한다. → [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-카드-토글-스크롤-TEST배포|토글 스크롤]], [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-토글-스크롤-TEST배포|항목·비율 토글 스크롤]], [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-TEST-파란-파비콘-프레임두께-TEST배포|프레임 두께]], [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-목록-다듬기-TEST배포|목록 다듬기]]
- 항목·비율 스크롤은 Ponytail 방식(요청을 완전히 해결하는 가장 작은 변경)으로 진행해 `chat.js`의 선택자 한 줄만 확장했다.

### 2.4 파비콘
- 투명 배경 PNG를 잘라 `favicon.ico`(16·32·48px), 32·192px PNG, 180px apple-touch 아이콘을 만들었다(iOS는 투명을 검게 채우므로 크림색 배경).
- 서버는 허용 목록 4개 이름만 서빙하는 선택 자산으로 처리하고(없으면 아이콘만 404, 채팅 UI는 영향 없음), `ROBINGRAPH_DEPLOY_TARGET=test`일 때 같은 URL에서 파란 변형을 돌려준다. PROD는 기본 주황 그대로다. → [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-파비콘-추가-TEST배포|파비콘 기록]]

### 2.5 문서·체계·운영
- README에 IUCN 등급별 카드 색 표를 추가했다(출처 이름이 없으면 회색 "미확인" 등 코드의 조건 포함). → [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-09-README-IUCN-등급별-카드색-매핑|상세 기록]]
- 작업 ID는 `docs/task-ids.md`에 대응표를 두고 파일명·코드·과거 커밋은 바꾸지 않았다. 백로그 ToC를 카테고리별로 다시 만들고 변경 이력을 접이식으로 만들었다.
- NAS의 릴리스 tar.gz 51개·체크아웃 57개·이전 배포 백업 13개·이관 덤프 2개를 옮겼다. 실행 중 스택과 롤백용 체크아웃 3개는 홈에 남겼다. → [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-NAS-임시파일-volume3-이동|상세 기록]]

---

## 3. 검증 결과

### 3.1 실제 DB·서버 대상 확인

| 항목 | 결과 |
| --- | --- |
| PROD Neo4j | 노드 474,998 / 관계 543,637(TEST와 일치), 인덱스 LOOKUP 2·FULLTEXT 1·VECTOR 1·RANGE 18 모두 ONLINE, 제약조건 17개 |
| PROD PostgreSQL | `source_record` 57,625 / `ingestion_run` 33 / `source_release` 10 / `source_dataset` 13(TEST와 일치) |
| PROD 최종 배포 `e90ff85` | healthy·재시작 0·OCI revision 일치, `verify` ok(`deployment_target: prod`), `verify_api_deployment.py` `passed: true` |
| PROD 채팅 | `흰뺨검둥오리에 대해서 알려줘` → 200, `route_method: jev`, `disposition: answer`, 경고 없음 (Jev·Gemini 설정 추가 후) |
| PROD 아이콘 | 기본(주황) 4개 서빙, TEST 변형과 해시가 다름 |

### 3.2 자동 테스트와 실제 브라우저

| 항목 | 결과 |
| --- | --- |
| 프런트엔드 `node --test` | 최종 255개 통과, 실패 0(모의 DOM) |
| Python 전체 | 644개 중 통과, 건너뜀 35(기존 DB 옵트인), 실패 0 |
| 실제 Chrome(헤드리스 CDP, 로컬 서버가 TEST Neo4j를 읽음) | PC 1280×800·600, 모바일 390×844 에뮬레이션에서 토글 스크롤·프레임 간격(PC 12px, 모바일 8px)·`자료 1` 제거·목록 스타일을 측정하고 스크린샷으로 확인 |
| GitHub CI | `main` 병합마다 7개 job(Frontend, Neo4j 통합, PostgreSQL 통합, Fixture 3개 OS, NAS Docker 이미지) 성공 |
| 사용자 확인 | PROD 화면과 모바일을 사용자가 직접 확인 |

모의 검증(단위 테스트)과 실제 DB·브라우저·NAS 확인을 구분했다. 브라우저 측정은 에뮬레이션이며 실제 휴대폰·Safari 측정은 없다.

### 3.3 확인하지 못했거나 알려야 할 점
- `main`에는 같은 날 다른 세션이 병합한 코드 변경(`fix: distinguish conservation snapshots from verified assessments`)이 있고 PROD(`e90ff85`)에는 아직 배포되지 않았다.
- 모바일 스크롤은 에뮬레이션에서 측정했고, 사용한 종은 카드 높이 여유 안에 들어가 스크롤 범위가 작았다.
- TEST Neo4j 비밀번호가 작업 중 대화에 노출되었고 NAS 로그인 비밀번호와 같아 교체를 권고했다(값은 기록하지 않았다).
- NAS Docker에는 오늘 만든 `test-*`·`prod-*` 이미지가 많이 남아 있다(롤백 태그는 보존, 정리 여부 미정).
- `dev-3`의 `dev` 브랜치는 오늘 병합이 반영되지 않았다.

---

## 4. 형상 관리

| 구분 | 내용 |
| --- | --- |
| 작업 브랜치 | `dev-claude`(최종 `b5ebc3f`까지 push) |
| `main` 병합 | `25c4a7a`(README), `d19a49f`(파비콘), `ebd0e3c`(토글 스크롤), `ab977b8`(프레임·차트·TEST 파비콘) 등 |
| PROD 이미지 | `prod-3e639ce` → `prod-336d987` → `prod-5fb401e` → `prod-e90ff85`(현재) |
| 롤백 | 직전 이미지가 NAS에 있고 문서에 명령을 적어 두었다(실행하지 않음) |

---

## 5. 관련 링크

- [[Work/RobinGraph/index|RobinGraph 인덱스]]
- [[Work/RobinGraph/작업기록/index|작업기록 목록]]
- [[Work/RobinGraph/RobinGraph 작업 백로그|작업 백로그]] — RG-101(문헌 Chunk 검색 저장소 분리), RG-102(PROD 활성 종 데이터 준비)
- [[Work/RobinGraph/작업기록/1xx DB·저장소/2026-10-09-TEST-PROD-데이터-이관|TEST → PROD 데이터 이관]]
- [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-PROD-API-3e639ce-배포|PROD API 3e639ce 배포]]
- [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-파비콘-추가-TEST배포|파비콘 추가]]
- [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-카드-토글-스크롤-TEST배포|카드 토글 스크롤]]
- [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-토글-스크롤-TEST배포|도넛 차트 항목·비율 토글 스크롤]]
- [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-TEST-파란-파비콘-프레임두께-TEST배포|TEST 파란 파비콘·프레임 두께]]
- [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-09-도넛차트-항목비율-목록-다듬기-TEST배포|항목·비율 목록 다듬기]]
- [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-09-README-IUCN-등급별-카드색-매핑|README IUCN 등급별 카드 색]]
- [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-NAS-임시파일-volume3-이동|NAS 임시 파일 이동]]
- [[Work/RobinGraph/검토자료/2026-10-09-DB-저장소-분담-논의|DB 저장소 분담 논의]]
