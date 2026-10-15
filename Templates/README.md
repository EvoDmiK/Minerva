# 📋 Minerva 템플릿 가이드 (Templates)

에이전트(AI 워커)와 작업자가 볼트 내 문서를 표준화된 형식으로 일관성 있게 작성할 수 있도록 제공되는 템플릿 모음입니다.

---

## 📂 템플릿 목록

| 파일명 | 용도 | 저장 위치 및 명명 규칙 | 주요 구성 |
|---|---|---|---|
| **[`worklog.md`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/Templates/worklog.md)** | **작업 문서 (작업기록)**<br>특정 작업/이슈 해결 후 작성하는 공식 실행 일지 | `Work/<프로젝트>/작업기록/<서브폴더>/`<br>`YYYY-MM-DD-<작업명-슬러그>.md` | 요약, 결과표, 문제분석, 구현내용, 테스트/검증 증거, 배포/형상관리, 후속과제 |
| **[`backlog.md`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/Templates/backlog.md)** | **프로젝트 백로그 전체 MOC**<br>새 프로젝트나 서브 영역 개설 시 생성 | `Work/<프로젝트>/<프로젝트> 작업 백로그.md` | 목차, 1xx~8xx ID 체계, 대시보드, 대기/진행/보류/완료 구역, 검증원칙 |
| **[`backlog-item.md`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/Templates/backlog-item.md)** | **단일 백로그 작업 항목**<br>기존 백로그에 새 작업을 등록할 때 삽입 | 기존 백로그 문서의 `## 1. 신규 착수 대기 작업` 아래 삽입 | 상태, 우선순위, 담당, 목적, 범위, 완료기준(체크리스트), 검증계획 |
| **[`note.md`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/Templates/note.md)** | **범용 일반 노트**<br>아이디어, 빠른 메모, 일반 참고 문서 | `Inbox/`, `Dev/`, `Learning/` 등 | Frontmatter, 요약, 내용, 관련 |

---

## 🤖 에이전트 작업 지침

### 1. 작업 문서 작성 시
* 새 작업 기록 파일은 반드시 **`YYYY-MM-DD-설명적인-제목.md`** 형식으로 생성합니다.
* `Templates/worklog.md`를 기반으로 작성하며, 가정이 아닌 **실제 테스트 명령어 결과 및 서버 배포 증거**를 상세히 기록합니다.
* 작업 완료 후 원천 프로젝트의 `index.md` 및 백로그 문서의 완료 섹션에 링크(`[[...]]`)를 연결합니다.

### 2. 백로그 등록 시
* 새 작업은 `Templates/backlog-item.md` 형식을 준수하여 해당 프로젝트의 백로그 문서에 추가합니다.
* 작업 ID는 해당 프로젝트의 카테고리 접두사 및 순번 규칙(예: `RG-405`, `BN-504`, `GK-201`)을 따릅니다.

### 3. 변수 플레이스홀더 치환 규칙
* `{{date}}`: `YYYY-MM-DD` 형식의 현재 날짜
* `{{project}}`: 프로젝트명 (예: `RobinGraph`, `Birds-Nest`)
* `{{task_id}}`: 작업 ID (예: `BN-504`, `RG-202`)
* `{{title}}`: 작업 제목
