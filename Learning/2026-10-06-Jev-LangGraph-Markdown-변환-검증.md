---
date: 2026-10-06
type: verification
tags:
  - learning
  - verification
  - markdown
  - jev
  - langgraph
source_url: https://www.langchain.com/blog/building-prod-with-jev-and-langgraph
---

# Jev·LangGraph 문서 Markdown 변환·저장 검증

## 대상과 저장 경로

- 제목: Building Prod with Jev and LangGraph
- 작성자: Sydney Runkle, Hunter Lovell
- 게시일: 2026-09-25
- 원문: https://www.langchain.com/blog/building-prod-with-jev-and-langgraph
- 보관본: [[Learning/2026-10-06-Jev-LangGraph-프로덕션-에이전트-원문]]
- 저장 수단: `obsidian_vault` MCP
- 작업일: 2026-10-06 (KST)

## 변환 방법과 실제 확인

- 요청된 `markdown-converter` 스킬은 현재 활성 프로필에서 조회되지 않았다. 대체 도구 `markdownify`와 BeautifulSoup으로 일반 HTTP로 가져온 HTML의 본문 영역을 변환했다. 브라우저는 사용하지 않았다.
- 영문 원문을 요약하거나 번역하지 않았다.
- 원문 본문과 Markdown을 HTML로 다시 파싱한 결과의 텍스트가 공백 차이를 제외하고 동일함을 자동 검증했다. 영상 링크 설명을 추가한 부분은 원문 텍스트 비교에서 제외했다.
- 본문 소제목 8개와 순서를 보존했다.
- 본문 원래 하이퍼링크 33개 및 임베드 영상 링크 2개를 보존했다. 총 링크 35개의 URL과 순서를 재파싱 결과와 대조했다.
- 본문 이미지 4개의 URL과 순서를 재파싱 결과와 대조했다. 괄호가 포함된 이미지 URL도 정상 파싱됨을 확인했다.
- 원문 본문에는 HTML 표 및 `<pre>` 코드 블록이 없었다. 인라인 코드 표기는 유지했다.
- 출처 URL, 실제 화면에 표시된 작성자, 게시일, 태그를 보관본 메타데이터로 추가했다.

## 범위와 한계

- 포함: 글의 영문 본문, 소제목, 목록, 인용, 인라인 코드, 본문 이미지 URL, 참고 링크, 감사의 말, 본문 임베드 영상 링크.
- 제외: 사이트 메뉴, 관련 글, 공통 홍보 영역, 영상 자막 및 영상 파일, 연결된 GitHub/Gist·문서·LangSmith trace의 본문.
- 이미지는 외부 URL 참조이므로 오프라인 이미지 보관본이 아니다.
- 문서 내 성능·가격 수치는 저자의 원문 주장을 보관한 것이며, 이 변환 작업에서 별도 실험으로 검증한 것은 아니다.

## 로컬 근거

`agent-artifacts/local/2026-10-06-jev-langgraph-markdown/`

- `source.html`: 실제 수집 HTML
- `building-prod-with-jev-and-langgraph.md`: 변환 원문
- `conversion-checks.json`: 본문·소제목·링크·이미지 검증 결과
- `convert_article.py`: 일회성 변환·검증 스크립트

원문 노트·이 검증 노트·Learning index는 저장 후 동일 경로 재조회로 확인한다.
