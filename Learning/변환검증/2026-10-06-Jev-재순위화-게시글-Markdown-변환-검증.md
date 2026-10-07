---
document_role: verification
source_note: "[[Learning/원문/2026-10-06-Jev-추천-재순위화-실증-연구-원문]]"
date: 2026-10-06
tags:
  - verification
  - markdown
  - reranking
source_url: https://discuss.pytorch.kr/t/jev-reranking-llm/12091
---

# Jev 재순위화 게시글 Markdown 변환 검증

## 결과
게시글 첫 번째 본문 전체를 요약 없이 Markdown으로 변환하고 파일 전체 readback 및 구조 검증을 완료했다.

- 요청된 `markdown-converter` 스킬은 활성 환경에 설치되어 있지 않아 사용하지 못했다.
- 대체 도구: `markdownify`. 브라우저 제어 없이 Discourse 공개 JSON API에서 HTML 본문을 가져왔다.
- 보존 확인: 원문 제목·소제목, 비교 방법·추천 품질·지연 시간의 표 3개와 각 셀 텍스트, 수식, 본문 이미지 3개의 원본 URL, 참조 링크, 작성자 안내와 말미 고지.
- 이미지 파일 자체를 내려받지는 않았으며 외부 URL 참조로 유지했다.
- 링크 미리보기 카드는 제목·URL·설명으로 단순화했다.
- 연결된 논문이나 다른 게시글 본문은 이번 변환 범위에 포함하지 않았다. 내용에 대한 논문 대조·사실 검증은 수행하지 않았다.

## 산출물
- Markdown: `/opt/data/agent-artifacts/local/2026-10-06-jev-reranking-markdown/jev-reranking.md`
- 원본 증거: 같은 디렉터리의 `source-post.json`
- 변환 검증 결과: 같은 디렉터리의 `verification.json`

표 셀의 첫 비교는 HTML 수식 전후 공백과 Markdown 표현 차이로 실패했다. 공백 및 Markdown 서식 정규화 후 모든 셀의 텍스트 보존을 확인했으며, 변환 본문 수정은 필요하지 않았다.

## Obsidian 원문 보관본 저장

- `obsidian_vault` MCP로 [[Learning/원문/2026-10-06-Jev-추천-재순위화-실증-연구-원문|Jev 추천 재순위화 실증 연구 — 게시글 원문 보관본]]을 생성했다.
- 현재 Vault의 `README.md`와 `Learning/index.md`를 확인하여 기존 개인 학습 영역에 저장했다. 과거의 `LLM Wiki/01_Sources/article/` 구조를 새로 만들지 않았다.
- 변환 본문은 유지하고 출처·작성자·태그 frontmatter와 보관본 관련 링크를 추가했다.
- 연결된 논문 원문은 포함하지 않으며 이미지도 외부 URL 참조로 유지한다.
