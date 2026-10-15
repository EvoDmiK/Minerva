---
date: 2026-10-13
created: 2026-10-13
document_role: verification
tags:
  - markdown-converter
  - conversion-verification
  - unsloth
source_url: https://discuss.pytorch.kr/t/unsloth-llm-laya-clef-jev/12158
source_note: "[[Learning/원문/2026-10-13-Unsloth-Jev식-결정-모델-학습과-로컬-서빙-원문]]"
converter: "MarkItDown 0.1.8"
---

# Unsloth 결정 모델 게시글 — Markdown 변환 검증

## 결과

- `markdown-converter` 스킬의 MarkItDown 방식으로 변환했다.
- 현재 hybrid-v2 스킬 목록에는 보이지 않았지만, `/opt/data/skills/markdown-converter/SKILL.md`를 읽어 해당 스킬을 확인했다. 다른 프로필의 파일이나 설정은 수정하지 않았다.
- MarkItDown 0.1.8을 실행했으며 종료 코드는 0이다.
- 게시글 첫 게시물 전체를 요약하지 않고 원문 보관본으로 저장했다.
- 원문 보관본은 Obsidian MCP `vault` 도구로 생성한 뒤 같은 경로 전체 readback을 수행했으며, 로컬 변환본과 내용이 정확히 일치했다.

## 수집 범위와 출처

- 원문 제목: Unsloth, LLM을 Laya, Clef와 같인 Jev식 결정 모델을 미세조정하고 로컬에서 서빙하는 학습 가이드 공개
- 작성자: 박정환 (9bow)
- 게시 시각: 2026-10-12T23:00:58.795Z (UTC), 2026-10-13 08:00:58 KST
- 게시물 ID: 22723
- Discourse 공개 JSON API의 첫 게시물 `cooked` HTML을 입력으로 사용했다. 로그인·브라우저 제어는 사용하지 않았다.
- 현재 Minerva의 README와 Learning 인덱스를 확인하여 `Learning/원문/`에 저장했다. 존재하지 않는 과거 `LLM Wiki/01_Sources/article/` 폴더는 새로 만들지 않았다.

## 실행 방법

```sh
/opt/hermes/tools/uv-0.12.3-linux-arm64/uvx markitdown article.html -o article-converted.md
```

위 입력·출력 파일은 이 작업의 로컬 artifact 디렉터리 안에 있다. 최종 Vault 저장은 로컬 복사나 Git push가 아니라 Obsidian MCP의 `vault` 도구 호출로 수행했다.

## 실제 변환 확인

- 제목 요소 18개: 원문 HTML의 제목 텍스트가 모두 남아 있다.
- 표 5개: Markdown 표로 변환되었다.
- 코드 블록 12개: 개수와 코드 본문이 HTML 입력과 일치한다. 코드 펜스의 언어 표시는 변환기가 생략한다.
- 이미지 요소 38개, 고유 이미지 URL 22개: 모두 외부 URL로 보존했다. 장식 이모지와 링크 카드 썸네일도 이 수에 포함된다.
- 제목 내부 앵커를 제외한 링크 54개: URL 인코딩을 정규화하여 대조했고 모두 보존했다.
- 상대 카테고리 링크를 절대 URL로 바꾸고, 이미지와 캡션이 결합된 링크 5곳을 일반 이미지·캡션 링크로 정리했다. 원문 문구·코드·수치는 수정하지 않았다.
- 최종 원문 보관본 SHA-256: `7f468b2460510a61b525df1d3829bc2018dfe2badfa682e86b19c39e003bb037`

## 한계

- 변환·저장 확인이며, 게시글의 기술 주장·성능 수치·라이선스 해석에 대한 독립 사실 검증은 아니다.
- 학습·서빙 명령과 예제 코드는 보관했지만 실행하지 않았다.
- 이미지 파일을 Vault에 다운로드하지 않았으므로, 원격 이미지 URL이 사라지면 표시되지 않을 수 있다.
- 링크된 다른 문서·논문·저장소 전문은 수집하지 않았다. 게시글 안의 링크 카드에는 원래 말줄임표로 끝나는 발췌가 포함되어 있다.
- 댓글은 수집하지 않았다. 수집 당시 이 토픽에는 첫 게시물만 있었다.
- 원문 제목의 `같인` 표기를 포함하여 원문 표현은 교정하지 않았다.

## 관련

- [[Learning/원문/2026-10-13-Unsloth-Jev식-결정-모델-학습과-로컬-서빙-원문|원문 보관본]]
- [[Learning/원문/index|원문 인덱스]]
- [[Learning/변환검증/index|변환 검증 인덱스]]
- [[Learning/index|Learning 전체 목록]]

## 로컬 artifact

`/opt/data/agent-artifacts/local/2026-10-13-unsloth-decision-markdown/`
