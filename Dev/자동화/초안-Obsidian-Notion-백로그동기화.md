---
created: 2026-11-15
updated: 2026-11-15
type: reference
category: "자동화"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-11-15-Obsidian-Notion-백로그동기화]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# Obsidian 백로그·Notion 칸반 동기화

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-11-15-Obsidian-Notion-백로그동기화]] · 분류 근거 {"인프라":0,"자동화":3,"관측성":0,"데이터":0}

## 1. 개요 및 목적

사용자가 Obsidian 백로그와 Notion 칸반을 동기화하고, 작업 ID와 카테고리는 프로젝트 작업 허브를 기준으로 삼도록 지시했다. Notion 허브의 기존 작업 39개를 기준으로 ID·현재 카테고리·상태·카드 URL을 Obsidian과 저장소 현황표에 명시했다. 기존 구현·실패·검증·배포의 본문과 역사적 보관 경로는 유지했다.

동일한 RG-101 카드가 Itzcuauhtli 프로젝트에 잘못 분류돼 RobinGraph 칸반에서 빠져 있었다. root가 해당 기존 카드의 프로젝트를 RobinGraph로 바로잡고 지원되는 담당 옵션을 기존 권장 담당에 맞췄다. 신규 카드 생성·기존 카드 삭제는 없으며 RobinGraph 39개는 완료 28·진행 중 5·착수 대기 1·보류 5다. 상태의 완료 범위를 넓히거나 미완료 기능을 완료로 바꾸지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 2. 해결 방안 및 설계
- 3. 주요 구현 내용
- 수정 및 추가 파일 목록
- 핵심 코드 / 설정 스니펫
- 4. 검증 및 테스트 결과
- 자동화 테스트 (단위 / 회귀)
- 실서비스 / UI 검증 증거
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 Obsidian 백로그와 Notion 칸반을 동기화하고, 작업 ID와 카테고리는 프로젝트 작업 허브를 기준으로 삼도록 지시했다. Notion 허브의 기존 작업 39개를 기준으로 ID·현재 카테고리·상태·카드 URL을 Obsidian과 저장소 현황표에 명시했다. 기존 구현·실패·검증·배포의 본문과 역사적 보관 경로는 유지했다.

| 구분 | 변경 사항 | 상세 내용 |
|---|---|---|
| 원인 규명 / 요구사항 | 허브 ID·분류와 Obsidian 보관 분류 차이 | RG-CARD/카드-3D alias, RG-101의 다른 프로젝트 오분류, 상세 메타데이터 누락 |
| 설계 및 해결 방안 | 기존 39카드와 중앙표를 기준으로 정렬 | 허브 현재 분류와 역사적 폴더·앵커 구분, null 우선순위 이력 보존 |
| 코드 / 설정 수정 | 앱 코드 변경 없음 | 백로그 문서·메타데이터·외부 문서만 수정 |
| 실서비스 배포 | 미실행 | TEST·Production 배포·DB 쓰기·서비스 재시작 없음 |
| 검증 및 테스트 | 실제 Notion/Obsidian 조회·저장·재조회 | 39키·카테고리·상태·nonnull 우선순위 비교 및 정확 본문 재조회 |
| 형상 관리 | dev-codex, 미커밋 | 이번 commit·push·merge 없음, 기존 사용자 AGENTS.md 변경 보존 |

RG-202의 문헌 PPR 미구현, RG-212의 신규 8문항 최초 5/8과 노출 후 8/8, RG-213의 실제 만료 대기·다중 탭 미실행, RG-507의 운영 수집과 TEST 검토 화면 경계를 Notion 비고·본문에 명확히 했다. 자동화 검증을 사람 Gold로 표현하거나 TEST 결과를 새 운영 검증으로 바꾸지 않았다.

- 사용자 지시대로 작업 ID·카테고리는 [프로젝트 작업 허브](https://www.notion.so/4181c8daeb6a8080ab45c8000b657551)가 기준이다. [RobinGraph 프로젝트 칸반](https://www.notion.so/4181c8daeb6a81c6b4c3e88f404b103b), [마스터 작업 DB](https://www.notion.so/4181c8daeb6a81c89de0dee1a9b5483f)의 기존 카드 URL을 그대로 연결했다.
- 현재 분류는 1xx 인프라 · DB · 보안, 2xx 코어 · 검색 · API, 3xx AI · 모델 · 프롬프트, 4xx UI · 화면 · MCP, 5xx 데이터 · 리소스 · 정제, 6xx 관측 · 평가 · 검증, 7xx 배포 · 자동화 · 빌드, 8xx 문서 · 기획 · 가이드다. 9xx 기타·실험은 허브에 없는 역사적 보관 분류이며 임의 새 분류·ID를 만들지 않는다.
- 상태 39개는 저장된 Obsidian과 일치해 유지했다. 허브 우선순위가 있는 7개만 기준값을 적용하고, null은 기존 P1/P2·역사를 지우는 지시로 해석하지 않았다. Writer 역할은 원문에 보존하며 허브에 없는 담당 옵션을 새로 만들지 않았다.
- Codex/root가 Notion 변경과 통합·독립 비교를, Writer 한 명이 이 작업의 Obsidian 쓰기와 저장소 문서를 맡았다. 변경안을 root에 전달해 확인받고 순차 저장·직전 동시변경 확인·재조회를 수행했다.
- `Templates/worklog.md`를 실제 Obsidian MCP로 조회해 이 기록에 적용했다. 현재 사용자 변경 AGENTS.md의 백로그 템플릿 의무 제거를 보존했으며 해당 파일은 수정하지 않았다.

- `docs/backlog/README.md` — 허브 기준·39행 ID/category/state/우선순위/카드 URL 중앙표, 집계와 alias·역사 경로 정책. 기존 기능별 완료·미완료 설명 보존.
- `docs/backlog/RG-213.md`, `RG-214.md`, `RG-215.md`, `RG-407.md`, `RG-408.md`, `RG-409.md`, `RG-507.md`, `RG-603.md` — 기존 8개 상세의 task_id/category/notion_url 정렬. RG-213·603은 누락된 최소 frontmatter 추가. 상태·기능·검증 원문은 변경하지 않았다.
- `docs/work-log/2026-11-15-obsidian-notion-backlog-sync.md` — 이 기록.
- Obsidian `Work/RobinGraph/RobinGraph 작업 백로그.md` — 39행 중앙표·허브 우선순위·카드 링크, RG-CARD 제목과 legacy 앵커, updated 11/15.
- Obsidian `Work/RobinGraph/백로그 상세/`의 기존 35문서 — task_id/category/notion_url 정렬. RG-CARD는 기존 `카드-3D.md`에 legacy alias와 현행 ID를 기록하며 파일 이동·중복 생성 없음. RG-209~212는 기존 별도 상세파일이 없어 중앙표로 완결하고 새 파일을 만들지 않았다. RG-101의 과거 PPR 의존성은 미구현 문헌 계획으로 명확히 했다.
- Obsidian 1~8xx 카테고리 `작업 백로그.md` — 현재 제목·category 메타데이터를 허브명으로 정렬하고 원래 폴더·과거 본문·링크·앵커를 유지했다. 9xx는 역사분류 안내만 추가했다. 기존 5xx의 도구 표시 wrapper는 주석으로 보존하고 YAML frontmatter를 문서 최상단으로 정상화했다.
- Obsidian `Work/RobinGraph/작업기록/index.md` — 현행 카테고리 표시명만 허브명으로 정렬, 역사 경로·당시 기록 수 보존.
- Obsidian 8xx 작업기록 목록과 `2026-11-15-Obsidian-Notion-백로그동기화.md` — 이 기록 링크·본문 동기화.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-11-15-Obsidian-Notion-백로그동기화]]
- [[Dev/index|Dev 인덱스]]
