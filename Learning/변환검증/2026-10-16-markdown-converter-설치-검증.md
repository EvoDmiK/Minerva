---
date: 2026-10-16
document_role: verification
tags:
  - hermes
  - skills
  - markdown-converter
status: installed-and-smoke-tested
profile: hybrid-v2
---

# markdown-converter 설치 및 실행 검증

## 결과

- 요청한 `markdown-converter` 스킬을 `hybrid-v2`에 설치했다.
- 설치 경로: `/opt/data/profiles/hybrid-v2/skills/document-conversion/markdown-converter/SKILL.md`.
- `skill_view(name='markdown-converter')`가 새 경로의 스킬을 정상 로드했다.
- MarkItDown 0.1.8의 HTML 및 단순 텍스트 PDF 변환을 실제 실행했고 종료 코드 0과 출력 내용을 확인했다.
- **논문 변환과 논문의 Obsidian 저장은 아직 실행하지 않았다. 수식 보존은 보장되지 않는다.**

## 설치 출처와 범위

- 기본 프로필 `/opt/data/skills/markdown-converter/SKILL.md`에는 기존 스킬이 있었지만 hybrid-v2 목록에서는 인식되지 않았다. 기존 파일은 수정하지 않았고 전후 SHA-256 일치를 확인했다.
- Hermes Skills Hub에서 `clawhub/markdown-converter` 검색·미리보기는 됐으나 설치는 upstream 파일 소실 오류로 실패했다.
- 기본 프로필의 스킬과 본문이 동일한 원저자 GitHub 소스를 확인하고 commit-pinned URL로 설치했다.
- 커뮤니티 스킬 출처: https://github.com/intellectronica/agent-skills/blob/9b0e00ad1b941165e2506545bbfddafa34cf2cb8/skills/markdown-converter/SKILL.md
- 공식 Hermes 설치 절차: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- 공식 MarkItDown 문서: https://github.com/microsoft/markitdown
- 공식 installer의 보안 검사 결과 `SAFE`, 허용 판정 후 설치했다. `--force`로 보안 검사를 우회하지 않았다. 이 검사는 무위험 보증이 아니다.

## 실행 검증

- 실제 Hermes 런타임에서는 CLI와 uv 실행 파일이 존재한다. 격리된 terminal 백엔드의 PATH 및 파일시스템과 달랐으며, terminal의 command-not-found를 전체 시스템의 미설치로 해석하지 않았다.
- 변환기는 gateway 가상환경에 설치하지 않았다. `UV_CACHE_DIR=/opt/data/profiles/hybrid-v2/cache/uv`를 지정한 uv 격리 환경에서 `uv tool run --from 'markitdown[pdf]' markitdown ...`을 실행했다.
- HTML 자체 작성 예제에서 제목, 한글, 굵게, 링크, 코드 보존을 확인했다.
- 직접 작성한 단순 PDF 예제의 `PDF converter smoke test` 문자열이 Markdown에 추출됐다.
- 브라우저·GUI·Azure·외부 LLM 호출과 유료 문서 업로드는 하지 않았다. 다른 프로필의 스킬, 설정, 게이트웨이 서비스는 변경하지 않았다.

## 수식 보존 한계 — 실제 발견

직접 작성한 HTML의 기존 LaTeX를 변환하는 테스트에서 다음 차이가 발생했다.

입력:

```latex
$$\int_0^1 x^2 \, dx = \frac{1}{3}$$
```

출력:

```latex
$$\int\_0^1 x^2 \, dx = \frac{1}{3}$$
```

- 인라인 `$x^2 + y^2 = z^2$`는 그대로였지만 독립 수식의 `_`가 `\_`로 바뀌어 원문 일치 검사는 실패했다.
- 따라서 전체 smoke test가 무조건 통과했다고 보고하지 않는다. 일반 문서 변환은 확인했고, 수식 정확 보존 테스트에는 실패 사례가 있다.
- 이는 HTML 안의 기존 LaTeX 테스트이며 PDF 수식을 LaTeX로 복구하는 능력을 검증한 것이 아니다.
- 실제 논문에서 수식을 보존하려면 원본 수식 또는 별도 수식 추출 결과와 대조해야 한다. Obsidian 앱의 렌더링은 점검하지 않았다.

## 절차 보완안

수식 escape, PDF extra, runtime/sandbox 구분 및 설치 검증 주의사항을 스킬 수정으로 제안했다. 기존 `skills.write_approval` 설정에 따라 **승인 대기**이며 현재 활성 스킬에 반영된 것으로 간주하지 않는다. pending ID: `1ec0c6b2`.

## 로컬 증거

`/opt/data/agent-artifacts/local/2026-10-16-markdown-converter-install/`

- `install-result.json`: ClawHub 원본 설치 실패 및 기본 프로필 파일 불변 확인
- `install-direct-source-result.json`: commit-pinned 직접 설치 및 보안 검사 결과
- `converter-help-result.json`: 변환기 실행과 PDF 의존성 준비
- `smoke-input.html`, `smoke-output.md`, `smoke-result.json`: 일반 HTML 보존 및 수식 불일치
- `smoke-input.pdf`, `smoke-pdf-output.md`, `smoke-pdf-result.json`: 단순 PDF 실제 변환

## 관련

- [[Learning/변환검증/index]]
- [[Learning/index]]
