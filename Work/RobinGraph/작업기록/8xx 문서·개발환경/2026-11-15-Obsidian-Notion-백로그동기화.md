---
created: 2026-11-15
date: 2026-11-15
project: RobinGraph
type: worklog
status: completed
task_id: obsidian-notion-backlog-sync
tags: [worklog, robingraph, backlog, obsidian, notion]
---

# Obsidian 백로그·Notion 칸반 동기화

## 요약

사용자가 Obsidian 백로그와 Notion 칸반을 동기화하고, 작업 ID와 카테고리는 프로젝트 작업 허브를 기준으로 삼도록 지시했다. Notion 허브의 기존 작업 39개를 기준으로 ID·현재 카테고리·상태·카드 URL을 Obsidian과 저장소 현황표에 명시했다. 기존 구현·실패·검증·배포의 본문과 역사적 보관 경로는 유지했다.

동일한 RG-101 카드가 Itzcuauhtli 프로젝트에 잘못 분류돼 RobinGraph 칸반에서 빠져 있었다. root가 해당 기존 카드의 프로젝트를 RobinGraph로 바로잡고 지원되는 담당 옵션을 기존 권장 담당에 맞췄다. 신규 카드 생성·기존 카드 삭제는 없으며 RobinGraph 39개는 완료 28·진행 중 5·착수 대기 1·보류 5다. 상태의 완료 범위를 넓히거나 미완료 기능을 완료로 바꾸지 않았다.

## 작업 및 변경 결과 요약

| 구분 | 변경 사항 | 상세 내용 |
|---|---|---|
| 원인 규명 / 요구사항 | 허브 ID·분류와 Obsidian 보관 분류 차이 | RG-CARD/카드-3D alias, RG-101의 다른 프로젝트 오분류, 상세 메타데이터 누락 |
| 설계 및 해결 방안 | 기존 39카드와 중앙표를 기준으로 정렬 | 허브 현재 분류와 역사적 폴더·앵커 구분, null 우선순위 이력 보존 |
| 코드 / 설정 수정 | 앱 코드 변경 없음 | 백로그 문서·메타데이터·외부 문서만 수정 |
| 실서비스 배포 | 미실행 | TEST·Production 배포·DB 쓰기·서비스 재시작 없음 |
| 검증 및 테스트 | 실제 Notion/Obsidian 조회·저장·재조회 | 39키·카테고리·상태·nonnull 우선순위 비교 및 정확 본문 재조회 |
| 형상 관리 | dev-codex, 미커밋 | 이번 commit·push·merge 없음, 기존 사용자 AGENTS.md 변경 보존 |

## 1. 작업 배경 및 문제 분석

프로젝트 작업 허브의 현재 분류명과 과거 Obsidian 작업기록 폴더 분류가 달랐고 상세 문서 중 task_id/category가 없는 항목이 있었다. 카드 3D 효과는 허브에서 RG-CARD, Obsidian에서는 카드-3D라는 파일명으로 관리돼 ID 대응 설명이 필요했다. RG-101은 실제 카드가 없는 것이 아니라 본문에 RobinGraph를 명시하면서 프로젝트 속성만 Itzcuauhtli로 잘못 지정된 기존 카드였다. 새 티켓을 만들지 않고 해당 속성만 정정했다.

RG-202의 문헌 PPR 미구현, RG-212의 신규 8문항 최초 5/8과 노출 후 8/8, RG-213의 실제 만료 대기·다중 탭 미실행, RG-507의 운영 수집과 TEST 검토 화면 경계를 Notion 비고·본문에 명확히 했다. 자동화 검증을 사람 Gold로 표현하거나 TEST 결과를 새 운영 검증으로 바꾸지 않았다.

## 2. 해결 방안 및 설계

- 사용자 지시대로 작업 ID·카테고리는 [프로젝트 작업 허브](https://www.notion.so/4181c8daeb6a8080ab45c8000b657551)가 기준이다. [RobinGraph 프로젝트 칸반](https://www.notion.so/4181c8daeb6a81c6b4c3e88f404b103b), [마스터 작업 DB](https://www.notion.so/4181c8daeb6a81c89de0dee1a9b5483f)의 기존 카드 URL을 그대로 연결했다.
- 현재 분류는 1xx 인프라 · DB · 보안, 2xx 코어 · 검색 · API, 3xx AI · 모델 · 프롬프트, 4xx UI · 화면 · MCP, 5xx 데이터 · 리소스 · 정제, 6xx 관측 · 평가 · 검증, 7xx 배포 · 자동화 · 빌드, 8xx 문서 · 기획 · 가이드다. 9xx 기타·실험은 허브에 없는 역사적 보관 분류이며 임의 새 분류·ID를 만들지 않는다.
- 상태 39개는 저장된 Obsidian과 일치해 유지했다. 허브 우선순위가 있는 7개만 기준값을 적용하고, null은 기존 P1/P2·역사를 지우는 지시로 해석하지 않았다. Writer 역할은 원문에 보존하며 허브에 없는 담당 옵션을 새로 만들지 않았다.
- Codex/root가 Notion 변경과 통합·독립 비교를, Writer 한 명이 이 작업의 Obsidian 쓰기와 저장소 문서를 맡았다. 변경안을 root에 전달해 확인받고 순차 저장·직전 동시변경 확인·재조회를 수행했다.
- `Templates/worklog.md`를 실제 Obsidian MCP로 조회해 이 기록에 적용했다. 현재 사용자 변경 AGENTS.md의 백로그 템플릿 의무 제거를 보존했으며 해당 파일은 수정하지 않았다.

## 3. 주요 구현 내용

### 수정 및 추가 파일 목록

- `docs/backlog/README.md` — 허브 기준·39행 ID/category/state/우선순위/카드 URL 중앙표, 집계와 alias·역사 경로 정책. 기존 기능별 완료·미완료 설명 보존.
- `docs/backlog/RG-213.md`, `RG-214.md`, `RG-215.md`, `RG-407.md`, `RG-408.md`, `RG-409.md`, `RG-507.md`, `RG-603.md` — 기존 8개 상세의 task_id/category/notion_url 정렬. RG-213·603은 누락된 최소 frontmatter 추가. 상태·기능·검증 원문은 변경하지 않았다.
- `docs/work-log/2026-11-15-obsidian-notion-backlog-sync.md` — 이 기록.
- Obsidian `Work/RobinGraph/RobinGraph 작업 백로그.md` — 39행 중앙표·허브 우선순위·카드 링크, RG-CARD 제목과 legacy 앵커, updated 11/15.
- Obsidian `Work/RobinGraph/백로그 상세/`의 기존 35문서 — task_id/category/notion_url 정렬. RG-CARD는 기존 `카드-3D.md`에 legacy alias와 현행 ID를 기록하며 파일 이동·중복 생성 없음. RG-209~212는 기존 별도 상세파일이 없어 중앙표로 완결하고 새 파일을 만들지 않았다. RG-101의 과거 PPR 의존성은 미구현 문헌 계획으로 명확히 했다.
- Obsidian 1~8xx 카테고리 `작업 백로그.md` — 현재 제목·category 메타데이터를 허브명으로 정렬하고 원래 폴더·과거 본문·링크·앵커를 유지했다. 9xx는 역사분류 안내만 추가했다. 기존 5xx의 도구 표시 wrapper는 주석으로 보존하고 YAML frontmatter를 문서 최상단으로 정상화했다.
- Obsidian `Work/RobinGraph/작업기록/index.md` — 현행 카테고리 표시명만 허브명으로 정렬, 역사 경로·당시 기록 수 보존.
- Obsidian 8xx 작업기록 목록과 `2026-11-15-Obsidian-Notion-백로그동기화.md` — 이 기록 링크·본문 동기화.

### 핵심 코드 / 설정 스니펫

앱 코드·API·설정 수정은 없어 해당하지 않는다. 기준 매핑은 root가 실제 허브에서 조회한 39카드이며 임시 `/tmp/robingraph-notion-backlog-sync-map.json`은 영구 산출물이나 새 DB가 아니다. 재현 가능한 현재 대응표는 저장소·Obsidian 중앙표의 39개 카드 링크로 확인한다.

## 4. 검증 및 테스트 결과

### 자동화 테스트 (단위 / 회귀)

앱 코드가 없어 단위·회귀 suite, 실제 조류 DB/API·브라우저 기능 검증은 미실행이다. 문서 동기화의 검증은 실제 외부 서비스 조회·저장·재조회이며 mock/fixture 성공으로 대신하지 않았다.

| 실제 실행 검사 | 결과·범위 |
|---|---|
| Notion 실제 SQL 카드 조회 | 39건, has_more=false, ID 중복 0, 기존 Obsidian과 상태 차이 0 |
| 저장된 실제 칸반 view 재조회 | 39건·RG-101 포함·모두 프로젝트 RobinGraph·has_more=false |
| root의 독립 중앙표 대조 | 저장 후 Obsidian 39행을 실제 Notion 39건과 비교: ID/category/state 차이 0, nonnull 우선순위 7개 일치, 누락·중복 0, 카드 URL 39개 존재 |
| Obsidian 기존 문서 저장·정확 재조회 | 중앙표 1 + 상세 35 + 카테고리 9 + 작업기록 index 1 = 46문서. 각 변경 직전 원문 대조로 다른 작업 변경 없음 확인, 저장 후 요청 전체 본문과 정확 일치 |
| 기존 5카드 재조회 | RG-101 프로젝트·지원 담당, RG-202 PPR 미구현, RG-212 최초/노출 평가, RG-213 실제 만료·다중 탭 미실행, RG-507 TEST/운영 경계 확인 |
| Notion 프로젝트·허브·Itz 문서 재조회 | RobinGraph 28/39, Itz 1/3 집계와 RG-101 위치 정정·기존 child DB 유지. 다른 동시 작업의 최신 원문 보존 |
| root 독립 메타데이터 샘플 재조회 | RG-101의 task_id/category/priority, RG-202·507의 현재 메타데이터, 카드-3D의 RG-CARD·legacy alias, 5xx 문서의 MCP frontmatter category 인식·현행 H1을 실제 재조회해 5문서 통과 |

RobinGraph 카테고리별 실제 카드 수는 1xx 2·2xx 15·3xx 1·4xx 10·5xx 7·6xx 3·7xx 1·8xx 0으로 총 39다. 완료율은 28/39=71.8%, 미완료 11개는 진행 5+대기 1+보류 5다. Itzcuauhtli 고유 3카드(완료 1·대기 2)는 수정하지 않았고 잘못 붙은 RG-101 요약 행만 옮겼다. 전체 Notion 카드 136행은 보존하며 신규·삭제 0, 다른 고유 프로젝트 카드 변경 0이다. RG-101의 지원 담당만 Claude Code·Codex로 보완하고 다른 담당 속성은 바꾸지 않았다.

### 실서비스 / UI 검증 증거

root가 실제 Notion `view://4181c8da-eb6a-812b-82da-000c1925f956` 결과를 재조회했고 RobinGraph 페이지 패널 표시 호출도 성공했다. 이는 웹 브라우저에서 칸반을 시각 검수한 결과로 확대하지 않는다. Writer는 Obsidian 실제 MCP 읽기·쓰기·재조회를 수행했다. TEST·Production 배포, 앱 호출, 조류 DB 읽기/쓰기, 수집·검토·공개는 이번에 수행하지 않았다.

## 5. 배포 및 형상 관리

- 대상: Notion 기존 카드·프로젝트 요약, Obsidian 문서, 로컬 저장소 문서.
- 브랜치: `dev-codex`. 이번 commit·push·merge·브랜치 삭제·이력 재작성 없음.
- 사용자 기존 `AGENTS.md` 미커밋 변경은 작업 시작부터 존재했으며 그대로 보존했다.
- TEST·Production 배포·컨테이너 재시작·이미지 교체·DB 변경·롤백 없음.
- 코드 변경이 없어 Graphify AST 갱신·semantic 재추출을 실행하지 않았다.
- 인증값은 조회 결과·문서에 기록하지 않았다.

## 6. 한계 및 후속 과제

이번 동기화는 요청 시점의 저장 상태를 대조한 일회성 작업이며 자동 양방향 동기화 서비스를 만들지 않았다. 진행 상태·완료율은 작업 개수이며 기능 품질이나 사람 검토 완료율이 아니다. RG-205 사람 검토·RG-212 일반화·RG-409/507 운영 승인·실제 사람 청취/동정은 기존 미완료 범위를 유지한다.

역사적 폴더 분류·과거 작업기록의 옛 명칭·당시 통계·검증 결과는 소급 변경하지 않았다. 현재 분류를 찾을 때는 허브 기준 중앙표를 먼저 사용한다. RG-CARD와 카드-3D는 alias 관계이며 독립 작업 두 개로 세지 않는다. 우선순위 null과 기존 상세의 P1/P2는 서로 다른 정보이므로 무조건 빈 값으로 동기화하지 않았다.

## 관련 문서

- [현재 백로그·39개 대응표](../backlog/README.md)
- [프로젝트 작업 허브](https://www.notion.so/4181c8daeb6a8080ab45c8000b657551)
- [RobinGraph Notion 칸반](https://www.notion.so/4181c8daeb6a81c6b4c3e88f404b103b)
- [이전 Graphify·백로그 정리](2026-11-14-graphify-backlog-cleanup.md)
- [[Work/RobinGraph/RobinGraph 작업 백로그|Obsidian 전체 백로그]]
