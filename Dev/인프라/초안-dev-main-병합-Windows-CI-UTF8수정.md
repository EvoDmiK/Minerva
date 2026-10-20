---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-dev-main-병합-Windows-CI-UTF8수정]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# dev → main 병합과 Windows CI UTF-8 보완

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-dev-main-병합-Windows-CI-UTF8수정]] · 분류 근거 {"인프라":10,"자동화":3,"관측성":1,"데이터":9}

## 1. 개요 및 목적

- 작업일: 2026-10-09
- 요청: 완료한 개발 작업을 main 브랜치에 병합한다.

dev 작업 디렉터리는 `/Volumes/Dove-Nest-SSD/app-data/orca/kimdove/home/workspaces/RobinGraph/dev-3`, 기존 main worktree는 `/Volumes/Dove-Nest-SSD/projects/RobinGraph`다. 두 worktree 모두 미커밋 변경이 없었다. origin을 fetch한 후 main/origin/main은 `834ddd28c12bda819209be3cda715076d773ffce`, dev/origin/dev는 `b4049cb8cff8cb26622c3d834f9fe21dba2779ba`였다. main 전용 커밋0·dev 전용109로 main이 dev의 조상이었다.

## 2. 핵심 아키텍처 및 원칙

- 대상·범위와 병합 전 상태
- 발견한 CI 실패·원인·보완
- 협업과 로컬 검증
- 실제 GitHub CI 결과
- 병합·푸시 결과
- 배포·남은 한계·백로그

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

병합은 지금까지의 dev 변경 전체를 대상으로 한다. 분류·국명/아종·계통/생태 관계 검색, Jev 질문 의도 분석, LangChain/MLflow 관측과 응답 결과 구분, PC/모바일 조류 카드 UI 및 검증 기록이 포함된다. 이전 TEST 배포 완료 기능을 main에 통합하는 작업이며 새 백로그 기능에 착수하는 요청으로 확대하지 않는다.

main은 보호 브랜치가 아니고 추가 PR/merge 의무 규칙은 없었다. 기존 main worktree를 그대로 사용해 fast-forward 병합했다. 브랜치 삭제·강제 푸시·기존 커밋 재작성은 하지 않는다. `.github/workflows/ci.yml`은 push/pull_request의 테스트와 Docker 빌드만 실행하며 NAS 자동 배포는 없다.

병합 점검 중 dev의 [기존 CI 실행37877070049](https://github.com/EvoDmiK/RobinGraph/actions/runs/37877070049)가 실패한 사실을 확인했다. Windows fixture만633개 실행 중 errors3/skipped46이었고 Ubuntu·macOS·프런트·Neo4j·PostgreSQL·Docker의 나머지6개 작업은 통과했다.

세 테스트는 UTF-8로 저장된 한국어 JSON을 Path.read_text()의 기본 인코딩으로 읽었다. Windows Python3.12 CI의 기본 cp1252에서는 각각0x9d·0x81·0x90 바이트에서 UnicodeDecodeError가 발생했다. 다음 세 줄에만 encoding='utf-8'을 명시했다.

| 파일 | 기존 실패 테스트 |
|---|---|
|tests/test_korean_display_names.py|test_snapshot_sources_crosswalks_and_split_species|
|tests/test_subspecies_name_references.py|test_domesticated_form_names_do_not_become_wild_subspecies_names|
|tests/test_subspecies_ranges.py|test_build_rejects_changed_source|

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-09-dev-main-병합-Windows-CI-UTF8수정]]
- [[Dev/index|Dev 인덱스]]
