---
trigger: always_on
---
# 문서 템플릿 및 거버넌스 준수 규칙

Minerva 볼트에서 신규 문서를 생성하거나 편집할 때는 다음 규칙을 엄격히 준수해야 합니다.

1. **작업 문서 (Worklog)**:
   - 파일 위치: `Work/<프로젝트>/작업기록/[<카테고리>/]YYYY-MM-DD-<작업명-슬러그>.md`
   - 반드시 `Templates/worklog.md` 구조 및 YAML 프론트매터 (`type: worklog`, `status: completed`, `created`, `date`, `project`, `task_id`, `tags`) 준수.
   - 문서 하단에 `## 관련 문서` (홈, 프로젝트 인덱스, 작업 백로그 링크) 필수 포함.

2. **작업 백로그 (Backlog)**:
   - 프로젝트 메인 백로그: `Templates/backlog.md`
   - 카테고리 서브 백로그: `Templates/category-backlog.md`
   - 작업 항목 추가: `Templates/backlog-item.md`

3. **지식 증류 (Dev)**:
   - 백로그나 시계열 일지는 `Dev/` 폴더로 증류하지 않음.
   - 범용 패턴만 `Dev/<도메인>/`으로 승격.

4. **Git 커밋 규격**:
   - Author: `EvoDmiK <93193661+EvoDmiK@users.noreply.github.com>`
