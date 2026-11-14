---
created: 2026-11-14
updated: 2026-11-14
type: spec
category: 워크플로우·자동화
id: DEV-202-v2
status: ready_for_deploy
tags:
  - n8n
  - workflow
  - automation
  - spec
  - knowledge-distillation
---

# [수정 명세서] Minerva 지식 증류 워크플로우 품질 개선 (DEV-202 v2)

## 1. 개요 및 배경

* **배경**: 기존 `DEV-202`([n8n-지식-증류-워크플로우-작업-명세서](Dev/자동화/n8n-지식-증류-워크플로우-작업-명세서.md)) 운영 결과, `Dev/` 폴더에 자동 생성된 초안 257건에서 다음과 같은 품질·거버넌스 문제가 확인되었다.
  1. **거버넌스 위반**: `AGENTS.md`에서 금지한 백로그(`작업 백로그.md`, `Swallow 작업 백로그.md`) 및 `index.md` 초안 7건이 `Dev/`로 복제됨.
  2. **저신호 문서 남발**: 코드 블록이 없거나(`163/257`건) 키워드 1~2회만 언급된 일회성 UI/배포 로그가 전부 초안으로 생성됨.
  3. **본문 중복 및 빈 아키텍처 섹션**: `158/257`건에서 1장(개요) 첫 문단이 4장(검증 근거)에 그대로 중복되었고, `237/257`건에서 2장(핵심 아키텍처 및 원칙)이 소제목 목차만 나열됨.
* **조치 현황**:
  * Minerva 볼트의 기존 저품질 초안 257건 삭제 및 `main` 푸시 완료 (`a092123`).
  * 로컬 CLI([distill_knowledge.py](scripts/distill_knowledge.py)) 가드 반영 및 `main` 푸시 완료 (`ab2220e`).
  * `Birds-Nest/dev-swallow` 워크트리의 n8n 워크플로우 JSON 및 단위 테스트 수정 완료 (**운영 n8n 서버 반영 대기**).

---

## 2. 수정 대상 및 상세 명세

### 2.1. n8n 워크플로우 (`Birds-Nest/dev-swallow/n8n/Minerva_Distill/knowledge-distillation.json`)

| 대상 노드 | 변경 전 | 변경 후 |
|---|---|---|
| **`대상 경로 확정`** | `Work/<project>/작업기록/**/*.md` 전체 허용 | 파일명이 `index.md`이거나 `백로그`를 포함하면 제외 (`github`/`schedule`은 조용히 스킵, `test`/`manual`은 오류 반환) |
| **`원천 파싱·분류`** | 키워드 점수 `best > 0`이면 무조건 `check` | 1) `frontmatter.type`이 `backlog`, `category-backlog`, `index`, `moc`이면 `skip` (`reason: non_worklog_type`)<br>2) `(codeBlocks.length > 0 && best >= 1) \|\| best >= 3` 미충족 시 `skip` (`reason: low_signal`) |
| **`초안 생성 판정·렌더`** | - 2장: `##`/`###` 제목 목록만 나열<br>- 4장: 1장과 중복 검사 없이 키워드 매칭 | - 2장: `아키텍처\|설계\|원칙\|해결\|구조\|패턴\|방안\|전략\|구현\|구성` 섹션의 실제 본문 문단 추출<br>- 4장: 1장(`intro`)·2장(`design`)에 이미 포함된 문단을 제외 집합(`Set`)으로 필터링해 중복 차단 |

### 2.2. 로컬 CLI (`Minerva/scripts/distill_knowledge.py`)

* `extract_distill_candidates()` 반환값에 `type` 필드(frontmatter `type` 소문자) 추가.
* `--create-draft` 실행 시 `type in ("backlog", "category-backlog", "index", "moc")` 또는 `code_block_count == 0 and not domains`이면 초안 파일을 생성하지 않고 건너뜀.

---

## 3. 사전 검증 결과

* **n8n 워크플로우 단위·계약 테스트** (`Birds-Nest/dev-swallow`):
  * 명령어: `node --test n8n/Minerva_Distill/tests/*.test.mjs`
  * 결과: **19개 통과, 0개 실패, 0개 건너뜀**
  * 추가 검증 항목:
    * `index.md`·`작업 백로그.md` 경로 제외 및 테스트 트리거 거부
    * `type: backlog` 문서 `non_worklog_type` 스킵, 저신호 문서 `low_signal` 스킵
    * 1장 개요 문단의 4장 중복 방지 및 2장 설계 섹션 본문 추출
* **Minerva 로컬 CLI**:
  * `python3 scripts/distill_knowledge.py --list-candidates`: 정상 실행 (`252개` 작업기록 스캔).

---

## 4. 운영 배포 절차 (`workflow.dove-nest.com`)

> [!IMPORTANT]
> 현재 환경에 `N8N_API_KEY`가 없어 자동 반영이 차단되어 있으므로, 아래 절차로 운영 n8n 인스턴스(`vtOMX12kZzpS6Uwc`)에 반영해야 합니다.

1. **n8n API 또는 UI 반영**:
   * **방법 A (API)**: 운영 n8n API 키를 사용해 `PUT https://workflow.dove-nest.com/api/v1/workflows/vtOMX12kZzpS6Uwc`로 `Birds-Nest/dev-swallow/n8n/Minerva_Distill/knowledge-distillation.json` 반영.
   * **방법 B (UI Import)**: `workflow.dove-nest.com`에서 워크플로우 `vtOMX12kZzpS6Uwc`를 열고 JSON 파일 Import 후 저장.
2. **연결 및 활성화 확인**:
   * `settings.errorWorkflow`가 `Aofvp7nvJxHuvmCZ`로 유지되는지 확인.
   * Credential 3종(`BQk1Fk6Loe4bDsUg`, `HBtZ19pWsrf4lwrk`, `obsVaultMcp2026A`) 및 `active: true` 상태 확인.
3. **배포 후 스모크 테스트**:
   * 테스트 웹훅(`minerva-distill-test`)으로 `작업 백로그.md` 경로 요청 시 거부 오류 반환 확인.
   * 정상 `worklog` 문서로 실행 시 1장·4장 중복 없이 초안이 생성되는지 확인.
4. **Git 형상 관리 (`Birds-Nest`)**:
   * `Birds-Nest/dev-swallow`의 `knowledge-distillation.json` 및 `knowledge-distillation.test.mjs` 변경사항 커밋 및 PR/main 반영.

---

## 5. 관련 문서

* [[Dev/자동화/n8n-지식-증류-워크플로우-작업-명세서|DEV-202 — 기존 작업 명세서]]
* [[Work/Birds-Nest/작업기록/지식연동/2026-10-17-Minerva-지식-증류-n8n-워크플로우-구현|BN-504 — 구현 및 운영 기록]]
* [[Dev/index|Dev 인덱스]]
