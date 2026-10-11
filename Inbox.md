---
created: 2026-10-11
updated: 2026-10-11
type: moc
tags:
  - inbox
  - moc
---

# 📥 Inbox — 미분류 캡처 & 임시 수집함

새로운 아이디어, 빠른 회의/작업 메모, 웹 클리핑, 에이전트 초안 등이 가장 먼저 담기는 공간입니다.  
형식에 구애받지 않고 빠르게 기록한 뒤, 주기적으로 검토하여 각 영역(`Dev`, `Work`, `Learning`)으로 이동하거나 정제합니다.

---

## 🧭 인박스 처리 워크플로우 (GTD)

1. **빠른 캡처 (Capture)**:
   - 본 문서 하단의 **[빠른 메모장]**에 바로 적거나, `Inbox/` 폴더 아래 새 노트(`Inbox/YYYY-MM-DD-메모명.md`)를 생성합니다.
2. **분류 및 라우팅 (Clarify & Organize)**:
   - **재사용 기술 지식 / 엔지니어링 패턴** ➔ `[[Dev/index|Dev/]]` (도메인 폴더: `인프라/`, `자동화/`, `관측성/`, `데이터/`)
   - **프로젝트 작업 로그 / 트러블슈팅 일지** ➔ `[[Work/index|Work/<Project>/작업기록/]]`
   - **도서 요약 / 스터디 / 개념 학습** ➔ `[[Learning/index|Learning/학습노트/]]`
3. **비우기 (Empty)**:
   - 목적지 폴더로 이동이 완료된 메모나 일회성 확인이 끝난 메모는 삭제하여 인박스를 0(Zero) 상태로 유지합니다.

---

## 📋 현재 미정리 메모 목록

```dataview
TABLE file.mtime AS "수정일", file.size AS "크기"
FROM "Inbox"
SORT file.mtime DESC
```

* **[[Inbox/test-note|test-note]]** — 지식 베이스 초기 세팅 점검용 메모

---

## ✍️ 빠른 메모장 (Scratchpad)

* (여기에 자유롭게 임시 메모나 번뜩이는 생각을 적어두세요)

---

## 🔗 관련 링크

- [[Home|🏠 홈으로]]
- [[Dev/index|Dev 인덱스]]
- [[Work/index|Work 인덱스]]
- [[Learning/index|Learning 인덱스]]
