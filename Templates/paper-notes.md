---
created: 2026-10-21
updated: 2026-10-21
type: template
tags: [template, learning, paper]
---

# 논문 원문·학습노트 템플릿

하나의 논문을 원문 보관본과 한국어 학습노트 **두 파일**로 저장하기 위한 템플릿입니다.
아래 두 Markdown 블록을 각각 사용합니다. 이 가이드 전체를 학습노트에 복사하지 않습니다.
researcher는 저장 전에 이 템플릿을 Obsidian MCP로 읽고 현재 인덱스와 경로를 확인합니다.

2026-10-21 Obsidian MCP로 확인한 `Home.md`, `Learning/index.md`,
`Learning/원문/index.md`, `Learning/학습노트/index.md`, `Templates/note.md`와
기존 FAST 논문 노트의 규칙을 따른다. 이 파일은 현재 규칙의 참고본이다.
실행 때마다 해당 인덱스·템플릿과 대상 폴더를 MCP로 다시 확인한다.
사용자가 지정한 다른 템플릿·경로는 우선한다. 오래된 경로를 재생성하지 않는다.

## 경로와 파일명

- 원문: `Learning/원문/YYYY-MM-DD-<논문-slug>-원문.md`
- 정리본: `Learning/학습노트/YYYY-MM-DD-<논문-slug>-논문-노트.md`
- 새 노트 날짜는 작성일(Asia/Seoul), 출판일은 별도 메타데이터다.
- slug는 실제 제목/식별자를 짧게 반영하고 `/ \ : * ? " < > |`를 제거한다.
- DOI/arXiv ID·원 URL로 중복 검색하고 기존 노트가 있으면 현재 경로와 파일명을
  재사용한다. 같은 논문의 다른 버전은 버전을 구분하며 과거 분석을 보존한다.
- 링크는 MCP에서 확인한 실제 경로를 사용한다. `.md` 확장자는 위키링크에서 생략한다.

## 원문 노트

```markdown
---
date: <저장일 YYYY-MM-DD>
created: <저장일 YYYY-MM-DD>
collected: <원문 수집일 YYYY-MM-DD>
document_role: source
tags: [learning, source, paper]
paper_title: "<실제 제목>"
paper_date: <확인된 논문 공개일>
paper_id: "<확인된 DOI/arXiv ID 및 버전>"
source_url: "<정규 원문 URL>"
primary_text: "<실제 변환한 전문 URL>"
source_role: primary
capture_scope: "<전문/부분/초록과 실제 확보 범위>"
converter: "markdown-converter / markitdown 0.1.8"
learning_notes:
  - "[[Learning/학습노트/YYYY-MM-DD-<논문-slug>-논문-노트]]"
---
# <실제 제목>

> [!info] 원문 보관 범위
> <변환한 원문 범위·표·수식·그림·각주 누락·이미지 다운로드 여부>
> 변환 검증은 논문 주장에 대한 사실 검증이나 실험 재현을 뜻하지 않는다.

<MarkItDown 변환 본문. 요약·번역으로 대체하지 않는다.>

## 관련

- [[Learning/학습노트/YYYY-MM-DD-<논문-slug>-논문-노트|한국어 정리]]
- [[Learning/원문/index|원문 인덱스]]
```

미확인 메타데이터는 생략하거나 `null`로 둔다. YAML 문자열을 올바르게 이스케이프한다.
원문의 표·코드·링크와 이미지 URL을 보존하고, 광고·메뉴 제거 등 정리가 필요하면
제거 범위를 명시한다. 실제 내려받지 않은 이미지를 로컬 보관했다고 보고하지 않는다.
이미지 보관을 요청받으면 지원 도구로 저장하고 존재를 검증한다. 별도 OCR/유료 API를
임의로 호출하지 않는다. `verification_note`는 실제 존재하는 별도 변환검증 문서를
확인한 경우에만 연결한다. 사용자의 기본 요청은 원문·학습노트 두 개다.

## 정리본 — 학습노트

기존 논문 노트의 `document_role`, `note_kind`, `language`, `source_notes`를 사용한다.
범용 `Templates/note.md`의 요약·내용·관련 구조 안에 논문 분석 항목을 배치한다.

```markdown
---
date: <분석일 YYYY-MM-DD>
created: <작성일 YYYY-MM-DD>
document_role: learning-note
note_kind: summary
language: ko
tags: [learning, paper]
paper_title: "<실제 제목>"
paper_date: <확인된 논문 공개일>
paper_id: "<확인된 DOI/arXiv ID 및 버전>"
source_url: "<정규 원문 URL>"
primary_text: "<실제 읽은 전문 URL>"
source_role: primary
capture_scope: "<실제로 읽고 분석한 범위, 전문 복제 아님>"
source_notes:
  - "[[Learning/원문/YYYY-MM-DD-<논문-slug>-원문]]"
---
# <논문 제목> — 한국어 정리

## 요약
<한 줄 요약과 확인된 핵심.>

## 내용
### 연구 질문과 배경
### 핵심 아이디어와 방법
### 실험 조건과 주요 결과
<데이터셋·비교 대상·지표·수치·원문 섹션/표. 미확인 사항을 구분한다.>
### 한계
<저자 명시 / 분석자의 해석 / 미확인 사항을 구분한다.>
### 활용 관점과 후속 확인
### 근거
<실제 읽은 원문 URL과 해당 섹션/표, 보조 자료.>

## 관련

- [[Learning/원문/YYYY-MM-DD-<논문-slug>-원문|변환 원문]]
- [[Learning/학습노트/index|학습노트 인덱스]]
- [[Home]]
```

초록만 읽었다면 해당 범위에 맞게 줄이고 미확인 결과를 채우지 않는다. 두 노트의
논문 ID·버전·URL과 연결 링크를 일치시킨다. 원문 노트의 요약 대체를 금지한다.

## 인덱스 반영과 검증

- 신규 문서를 실제 저장·재조회한 뒤 `Learning/원문/index.md`,
  `Learning/학습노트/index.md`, `Learning/index.md`를 읽고 기존 형식으로 등록한다.
- 같은 문서 링크는 중복 등록하지 않는다. 기존 항목과 사용자 설명을 보존한다.
- 현재 관리 기준이 달라졌으면 현재 인덱스 지침을 우선한다.
- 본문 두 노트와 변경한 인덱스를 각각 재조회한다. 일부 실패는 부분 완료로 보고한다.
- 별도 변환검증 문서를 자동 생성하지 않는다. 변환 한계·읽기 검증 상태는 원문
  범위와 최종 응답에 남기며, 별도 기록 요청이 있으면 `Learning/변환검증/`의
  현재 규칙을 읽고 작성한다. 링크 대상이 없는 `verification_note`를 만들지 않는다.
