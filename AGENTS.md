# Minerva 볼트 에이전트 작업 지침 (AGENTS.md)

이 문서는 Antigravity, Claude Code, Codex, Hermes 등 모든 AI 코딩 에이전트가 Minerva 볼트에서 작업할 때 반드시 준수해야 하는 **문서 작성 및 템플릿 표준 규격**입니다.

---

## 1. 작업 문서 (작업기록) 작성 규칙

새로운 작업 일지, 디버깅 로그, 배포 기록을 작성할 때는 반드시 **[`Templates/worklog.md`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/Templates/worklog.md)** 템플릿을 준수해야 합니다.

* **저장 위치**: `Work/<프로젝트명>/작업기록/[<카테고리>/]YYYY-MM-DD-<작업명-슬러그>.md`
* **필수 YAML Frontmatter**:
  ```yaml
  ---
  created: YYYY-MM-DD
  date: YYYY-MM-DD
  project: <프로젝트명> # Birds-Nest | RobinGraph | Gullinkambi | Jery | Itzcuauhtli
  type: worklog
  status: completed # completed | in-progress | failed
  task_id: <작업ID> # e.g. RG-701, BN-504, JR-102, GK-203, IZ-201 (해당 시)
  tags:
    - worklog
    - <프로젝트_소문자>
  ---
  ```
* **필수 포함 섹션**:
  1. `# [<task_id>] <문서 제목>`
  2. `## 요약`: 2~3개 단락으로 핵심 현상, 해결책, 최종 결과 요약.
  3. `## 작업 및 변경 결과 요약`: 구분 / 변경 사항 / 상세 내용 표.
  4. `## 1. 작업 배경 및 문제 분석`: 발생 현상, 에러 로그, 원인 분석.
  5. `## 2. 해결 방안 및 설계`: 아키텍처, 표준 규격, 대안 검토.
  6. `## 3. 주요 구현 내용`: 수정 파일 목록 및 핵심 코드 스니펫.
  7. `## 4. 검증 및 테스트 결과`: 단위/통합 테스트 패스율 및 실서버/UI 검증 증거.
  8. `## 5. 배포 및 형상 관리`: 배포 환경, Git 브랜치, 커밋 해시.
  9. `## 6. 한계 및 후속 과제`: 남은 과제 및 후속 백로그 링크.
  10. `## 관련 문서`: `[[Home]]`, `[[Work/<Project>/index]]`, `[[Work/<Project>/<Project> 작업 백로그]]`.

---

## 2. 작업 백로그 (Backlog) 작성 규칙

프로젝트 백로그 및 세부 카테고리 백로그는 다음 표준 템플릿을 사용합니다:

* **프로젝트 메인 백로그 개설**: **[`Templates/backlog.md`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/Templates/backlog.md)**
  * 위치: `Work/<프로젝트명>/<프로젝트명> 작업 백로그.md`
  * 메타데이터: `type: backlog`
  * 필수 구성: 목차, 카테고리별 1xx~8xx ID 체계, 작업 현황 대시보드, 대기/진행/보류/완료 구역, 검증 원칙.
* **카테고리 서브 백로그 개설**: **[`Templates/category-backlog.md`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/Templates/category-backlog.md)**
  * 위치: `Work/<프로젝트명>/작업기록/<카테고리>/작업 백로그.md`
  * 메타데이터: `type: category-backlog`, `category: "<카테고리명>"`
* **단일 작업 항목 추가**: **[`Templates/backlog-item.md`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/Templates/backlog-item.md)**
  * 기존 백로그의 `## 1. 신규 착수 대기 작업` 아래에 양식을 복사하여 삽입.
  * 체크리스트(`- [ ]`) 형태의 완료 기준(Acceptance Criteria) 명시 필수.

---

## 3. 지식 증류 (Dev) 거버넌스 규칙

* **시계열 일지와 상록수 지식의 엄격한 분리**:
  * 특정 시점의 디버깅/배포 로그는 `Work/`에만 둡니다.
  * 여러 프로젝트에서 반복 재사용 가능한 범용 엔지니어링 패턴만 `Dev/<도메인>/`으로 승격(Distill)합니다.
* **백로그 문서 증류 금지**:
  * 백로그 문서는 상록수 지식이 아니므로 `Dev/` 폴더에 백로그 초안을 생성하지 마십시오.
  * 지식 증류 스크립트 실행 시 `python3 scripts/distill_knowledge.py`를 사용합니다.

---

## 4. Git 커밋 및 형상 관리 규칙

* **커밋 작성자 (Author)**:
  * GitHub 비공개 이메일 보안 정책(GH007) 통과 및 기여도 잔디 기록을 위해 반드시 아래 설정을 사용합니다:
  * `EvoDmiK <93193661+EvoDmiK@users.noreply.github.com>`
* **커밋 전 자동 정규화**:
  * 새로 작성된 작업 문서가 템플릿을 온전히 준수하는지 검증하기 위해 `python3 scripts/normalize_worklogs.py --apply`를 실행할 수 있습니다.
