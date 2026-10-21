---
created: 2026-10-21
date: 2026-10-21
project: Birds-Nest
type: worklog
status: completed
tags:
  - worklog
  - birds-nest
  - hermes
  - discord
  - mcp
  - openviking
  - skills
---

# Hermes 프로필·Discord·MCP·메모리·논문 스킬 구성

## 요약

Hermes를 개인 비서와 모델별 분석 도구로 사용하기 위해 기존 프로필을 백업·정리하고, Antigravity 기반 researcher와 Claude Code 기반 analyst를 구성했다. 기존 hybrid-v2는 일반 비서 역할과 공유 Discord 봇 연결을 담당한다. 연구 채널 두 개는 researcher, 토이프로젝트 채널은 analyst가 응답하도록 분리했다.

researcher에는 Obsidian·Notion, analyst에는 Obsidian·Notion·Swallow MCP를 연결했다. hybrid-v2·researcher·analyst의 OpenViking 공급자 설치와 실제 인증·임시 메모 저장·읽기·검색 요청을 확인했다. 세 프로필은 동일 사용자 계정 아래 별도 assistant peer를 사용한다.

researcher의 논문 분석 스킬은 markdown-converter로 변환한 원문과 한국어 정리본을 별도 노트로 저장하도록 확장했다. 실제 vault의 현재 Learning 폴더 구조를 확인해 예전 경로를 수정했고, [[Templates/paper-notes|논문 원문·학습노트 템플릿]]을 Obsidian MCP로 생성·재조회했다. 설정 적용과 검증은 완료했으며, 실제 논문 한 편을 Discord에서 받아 두 노트와 인덱스까지 저장하는 전체 흐름은 아직 검증하지 않았다.

## 작업 및 변경 결과 요약

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| 원인 규명 / 요구사항 | 모델별 개인 비서 역할 분리 | researcher는 논문·자료 조사, analyst는 해석·기술 비교·독립 검토 담당 |
| 설계 및 해결 방안 | 단일 봇과 프로필별 라우팅 | hybrid-v2 소유 Discord 연결을 공유하며 채널별 실행 프로필 분리 |
| 코드 / 설정 수정 | 프로필·라우트·MCP·메모리·스킬 | 선언적 구성, 프로필 설정, SOUL, 논문 스킬과 포맷 참고본 수정 |
| 실서비스 반영 | 기존 Hermes Docker 게이트웨이 | 설정별 재시작 후 Discord 연결과 제공 프로필 확인 |
| 검증 및 테스트 | 구성 검사·MCP 읽기·메모리·스킬 테스트 | 설정 회귀 13건 통과, 실제 MCP 조회, 임시 메모 왕복, 합성 모델 사례 검증 |
| 형상 관리 | dev-codex 로컬 커밋 | 최종 관련 커밋 2d4ccbf. 원격 push/PR 완료는 확인되지 않음 |

---

## 1. 작업 배경 및 문제 분석

### 발생 현상 / 요구사항

- 기존 프로필을 목록에서 제거하되 데이터를 백업하고 hybrid-v2는 유지한다.
- researcher와 Claude 기반 별도 프로필을 Discord에서 사용할 수 있게 한다.
- 최초 Claude 프로필 이름 critic은 분석·의사결정까지 맡도록 analyst로 변경한다.
- 프로필별 MCP와 장기 기억을 연결한다.
- 논문 링크를 분석하고 요청 시 원문·정리본을 별도 Obsidian 노트로 저장한다.

### 원인 분석 / 설계 검토

- 동일 Discord 봇 계정과 응답을 생성하는 Hermes 프로필은 서로 다르다. 봇 계정을 채널에서 제거하는 방식 대신 실행 프로필 라우팅으로 해결했다.
- researcher의 /status에서 Connected Platforms가 비어 있어도 공유 봇 연결을 사용하는 구조에서는 단독 어댑터가 없다는 의미일 수 있다. 상태 명령은 모델 추론을 하지 않아 토큰 0으로 표시된다.
- analyst의 /status 시간 초과 당시 로그에는 researcher 이미지 처리 중 동기식 Antigravity 스트림 읽기로 이벤트 루프가 막히고 Discord heartbeat·interaction 처리가 지연된 흔적이 있었다. 이후 응답은 복구됐으나 이 차단 문제 자체를 수정한 것은 아니다.
- hybrid-v2는 OpenViking 설정만 존재하고 현재 버전에 필요한 공급자 플러그인이 누락돼 있었다.
- 논문 스킬 작성 시 저장소의 예전 위키 경로를 재사용한 오류가 있었다. 사용자 지적 후 실제 Obsidian의 Home·Learning 인덱스·템플릿·기존 논문 노트를 조회해 현재 구조로 수정했다.

```text
확인한 오류·진단:
- Discord: interaction expired before defer
- Discord: heartbeat blocked
- hybrid-v2 memory status: OpenViking Plugin NOT installed
```

---

## 2. 해결 방안 및 설계

### 프로필과 Discord 역할

| 프로필 | 모델 / 공급자 | 역할·채널 |
| --- | --- | --- |
| hybrid-v2 | gpt-6.1-sol / openai-codex | 공유 Discord 봇 연결, 나머지 채널의 일반 비서 |
| researcher | gemini-3.8-flash-high / antigravity-subscription-directsdk | #llm-위키, #기술스택-공부와 하위 스레드 |
| analyst | claude-opus-4-8 / claude-subscription-directsdk-experimental | #토이프로젝트와 하위 스레드 |

- 호스트 게이트웨이는 default로 시작하고 hybrid-v2 소유 Discord 어댑터를 공유한다. default는 이 호스트 구성 때문에 남겨둔 인프라 프로필이다.
- researcher·analyst 전용 봇 토큰은 추가하지 않았다.
- 위 전용 채널에서 hybrid-v2가 답하지 않도록 라우팅과 중복 채널 지침을 정리했다.
- native delegation의 critic·researcher 역할 이름과 장기 실행 named profile은 별개다.

### 지식·메모리 연결

- researcher: Obsidian, Notion MCP.
- analyst: Obsidian, Notion, Swallow MCP.
- 문서 저장과 모의 주문·관심종목 변경은 해당 사용자 요청 범위에서 수행한다.
- OpenViking은 기존 서버와 birds-nest / kimdove 계정을 사용하며 assistant peer는 각 프로필 이름으로 구분한다.
- peer별 새 메모 저장 경로는 분리되지만 계정 권한까지 격리한 구성은 아니다. 공통 사용자 메모리에 접근할 수 있다.

### 논문 저장 방식

1. 현재 Obsidian의 [[Templates/paper-notes]]와 Learning 인덱스를 MCP로 읽는다.
2. 기존 markdown-converter 스킬을 읽고 MarkItDown으로 원문 HTML/PDF를 변환한다.
3. 읽은 범위·추출 한계를 표시하고 근거와 분석자의 해석을 구분한다.
4. 저장 요청 시 원문과 학습노트를 각각 저장하고 상호 링크를 넣는다.
5. 각 노트와 변경한 인덱스를 다시 읽어 검증한다. 일부 실패는 부분 완료로 보고한다.

---

## 3. 주요 구현 내용

### 수정 및 추가 파일 목록

- `config/hermes/gateway-routes.json` — 연구·토이프로젝트 채널의 실행 프로필 지정.
- `config/hermes/topology.toml`, `profiles/hybrid-v2.toml`, `personas/hybrid-v2.md` — 역할·채널 경계 정리.
- `config/hermes/run-control-plane.sh` — default 호스트 게이트웨이 실행.
- `config/hermes/specialist-plugins.lock.json` — 공급자 버전과 설치 대상 기록.
- `hermes/profiles/{researcher,analyst}/config.yaml`, `SOUL.md` — 모델·MCP·메모리·도구 및 역할.
- `hermes/profiles/researcher/skills/custom_skills/paper-analysis-to-obsidian/SKILL.md` — 원문 확인·분석·분리 저장·실패 처리.
- 같은 스킬의 `references/note-format.md` — 현재 Learning 형식의 참고본. 최신 vault 템플릿 우선.
- `config/hermes/README.md` — 실행·구성·검증·한계 문서.
- [[Templates/paper-notes]] — 원문·학습노트 두 서식을 담은 템플릿 하나.
- [[Templates/README]] — 새 템플릿 목록 등록.

### 핵심 코드 / 설정 스니펫

```yaml
# 프로필마다 agent 값을 해당 이름으로 지정
memory:
  memory_enabled: true
  user_profile_enabled: true
  provider: openviking
  openviking:
    account: birds-nest
    user: kimdove
    agent: researcher
```

현재 확인한 저장 위치:

- 원문: `Learning/원문/YYYY-MM-DD-<논문-slug>-원문.md`
- 정리본: `Learning/학습노트/YYYY-MM-DD-<논문-slug>-논문-노트.md`
- 원문은 `document_role: source`, 학습노트는 `document_role: learning-note`, `note_kind: summary`, `language: ko` 사용.
- 학습노트의 `source_notes`로 원문을 연결한다. 관련 인덱스는 [[Learning/원문/index]], [[Learning/학습노트/index]], [[Learning/index]]다.
- 경로를 기억에만 의존하지 않고 저장 전에 실제 MCP로 확인한다. 예전 폴더는 자동 재생성하지 않는다.

### 런타임·비밀 설정

- MarkItDown 0.1.8과 PDF 지원 의존성을 researcher 전용 uv tool 환경에 설치했다. Hermes 공용 Python 환경은 수정하지 않았다.
- researcher의 terminal 도구는 입력 준비·변환에 사용하고 최종 vault 저장은 Obsidian MCP로 한다.
- 공급자 로그인과 MCP 인증값은 기존 CLI 저장소·외부 비밀 파일에 유지한다. 이 작업기록에 인증값은 포함하지 않았다.
- retired 프로필 8개는 검증한 압축 백업으로 보관한 뒤 목록에서 제거했다. 백업 위치: `hermes/agent-artifacts/local/2026-10-21-profile-reset/legacy-profiles.tar.gz`.

---

## 4. 검증 및 테스트 결과

### 자동화 테스트 (단위 / 회귀)

| 검사 | 결과 | 확인 범위 |
| --- | --- | --- |
| `python3 -m unittest discover -s tests -p test_hermes_control_plane.py` | 13/13 통과 | 프로필·라우팅·MCP·메모리 설정을 반영한 구성 단계에서 실행 |
| `scripts/hermes-control-plane.py validate` | VALID | 선언적 구성 검사 |
| `scripts/hermes-control-plane.py render --check` | IN SYNC | 생성 설정과 선언적 구성의 일치 |
| `scripts/sync-hermes-custom-skills.py --check` | 통과 | 스킬 참조·길이·동기화 검사. 기존 hybrid-v2 SOUL 길이 경고는 남아 있음 |
| 스킬 제작 가이드 구조 검증기 | 통과 | Hermes YAML 파서를 재사용해 실행 |
| 합성 스킬 사례 3건 | 3/3 통과 | 초록만 제공, 원문 접근 실패, MCP 없는 저장 요청 |
| 현행 경로·부분 저장 모의 사례 | 5/5 출력 검사 통과 | 실제 researcher 모델, 모의 도구 결과 기반 계획·상태 보고 |

스킬 모델 테스트는 임시 home에서 OpenViking과 앱 MCP를 끄고 명시적으로 스킬을 preload해 실행했다. 실제 vault 쓰기나 자동 스킬 선택 성능을 검증한 결과로 확대하지 않는다.

### 실서비스 / UI 검증 증거

- 실제 Hermes 라우터에서 각 지정 채널과 하위 스레드가 researcher 또는 analyst를 선택하는지 확인했다.
- 사용자가 researcher와 analyst의 Discord /status 응답을 확인했다. analyst 상태의 모델은 claude-opus-4-8이었다.
- researcher Antigravity의 별도 실제 추론·웹 조사와 gateway profile scope 추론을 확인했다. /status 자체가 모델 추론을 검증하는 것은 아니다.
- Obsidian system info, Notion get-self, Swallow 매매 이력 조회로 analyst의 인증된 MCP 접근을 확인했다.
- OpenViking 세 프로필에서 각 assistant 경로에 임시 메모를 저장·읽기하고 scoped search 요청을 성공시킨 뒤 검증 파일만 삭제했다. 검색 요청 성공을 의미하며 장기 대화 추출·의미 기반 자동 회상 전반의 검증은 아니다.
- MarkItDown의 합성 HTML 변환에서 제목·본문·섹션 보존을 확인했다. PDF 추가 의존성은 설치했지만 실제 논문 PDF 변환 전체는 미검증이다.
- [[Templates/paper-notes]] 생성과 [[Templates/README]] 등록 후 두 문서를 각각 재조회해 저장 내용의 정확한 일치를 확인했다.
- 작업기록 작성 직전 게이트웨이 상태는 default·analyst·hybrid-v2·researcher 제공, hybrid-v2:discord 연결 상태였다.

### 로컬 증거 위치

리포지토리 기준이며 Git 추적 대상은 아니다.

- `hermes/agent-artifacts/local/2026-10-21-researcher-discord-mcp/`
- `hermes/agent-artifacts/local/2026-10-21-analyst-mcp/`
- `hermes/agent-artifacts/local/2026-10-21-specialist-openviking/provider-checks.json`
- `hermes/agent-artifacts/local/2026-10-21-hybrid-openviking/verification.json`
- `hermes/agent-artifacts/local/2026-10-21-paper-skill/verification.json`
- `hermes/agent-artifacts/local/2026-10-21-paper-converter/vault-path-check.json`
- `hermes/agent-artifacts/local/2026-10-21-paper-converter/iteration-3/verification.json`

---

## 5. 배포 및 형상 관리

- **대상 환경**: 기존 Mac 호스트의 Hermes Docker 컨테이너.
- **Git 브랜치**: dev-codex. main 직접 반영이나 PR 머지는 수행하지 않았다.
- **런타임 반영**: 관련 설정 변경 후 게이트웨이 재시작·Discord 연결 복구 확인.
- **원격 반영**: 로컬 커밋 완료. 앞선 원격 인증 오류로 push·PR 완료는 확인되지 않았으며 완료로 보고하지 않는다.
- **기존 변경 보존**: 사용자 변경이 있던 루트 `hermes/config.yaml`은 별도 보존하고 이번 커밋에 포함하지 않았다.

| 커밋 | 내용 |
| --- | --- |
| 954bd3d | Claude Code 구독 기반 비교 경로 |
| 1c616fc | 기존 프로필 백업·정리 |
| d03555b / 5fda20e | critic·researcher 추가, 실제 사용 가능한 Antigravity 모델 확인 |
| 6589ae6 / 13b1a63 | 연구 채널 라우팅·지식 MCP·프로필 응답 경계 |
| 0a35a46 / f2913ae | critic → analyst, 토이프로젝트 채널 배치 |
| 9ed4db9 | analyst Obsidian·Notion·Swallow MCP |
| 967e3ec / 9316bb5 | 세 프로필 OpenViking 공급자 구성·복구 |
| 087b715 / a1e8bd2 | 논문 스킬, 변환·현행 Learning 구조의 두 노트 저장 |
| 2d4ccbf | 실제 Obsidian 템플릿을 읽는 스킬 연결 |

### 복구 참고

선언적 구성과 프로필 파일을 변경 전 커밋·보관본으로 되돌린 뒤 materializer와 게이트웨이에 반영하는 방식으로 복구한다. 프로필 전체 복구 자료는 별도 백업에 있다. 이 작업에서는 복구 연습이나 기존 장기 메모리 삭제·이전을 수행하지 않았다.

---

## 6. 한계 및 후속 과제

- 실제 공개 논문 한 편을 Discord에서 받아 변환 → 원문 저장 → 학습노트 저장 → 인덱스 반영 → 각 경로 재조회까지 수행하는 통합 검증이 필요하다.
- researcher의 이미지 처리로 공유 Discord 이벤트 루프가 막힌 문제는 재발 가능성이 남아 있다. 현재 텍스트 논문 변환과 별개로 추적해야 한다.
- OpenViking peer 분리는 계정별 접근 제어가 아니다. 장기 대화의 자동 추출·회상 품질은 추가 확인이 필요하다.
- 기존 Grafana MCP 실행 파일 경로 누락과 Docker bind mount의 SQLite WAL 경고는 이번 범위에서 해결하지 않았다.
- Claude Code·Antigravity 로그인은 각 CLI가 관리한다. 재시작마다 로그인이 필요한 구성은 아니지만 만료·철회·갱신 실패 시 재인증이 필요할 수 있다.
- 원격 인증을 복구한 뒤 dev-codex push와 PR 상태를 확인해야 한다.
- 후속 항목의 신규 작업 ID는 발급하지 않았다. 추적 위치: [[Work/Birds-Nest/Birds-Nest 작업 백로그]].

---

## 관련 문서

- [[Home|홈]]
- [[Work/Birds-Nest/index|Birds-Nest 프로젝트]]
- [[Work/Birds-Nest/Birds-Nest 작업 백로그|프로젝트 작업 백로그]]
- [[Work/Birds-Nest/작업기록/Hermes/index|Hermes 작업기록]]
- [[Templates/worklog|작업기록 템플릿]]
- [[Templates/paper-notes|논문 원문·학습노트 템플릿]]
- [[Learning/index|Learning 전체 목록]]
