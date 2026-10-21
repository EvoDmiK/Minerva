---
created: 2026-10-21
updated: 2026-10-21
type: reference
category: "관측성"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Hermes/2026-10-21-Hermes-프로필-Discord-MCP-메모리-논문스킬-구성]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# Hermes 프로필·Discord·MCP·메모리·논문 스킬 구성

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Hermes/2026-10-21-Hermes-프로필-Discord-MCP-메모리-논문스킬-구성]] · 분류 근거 {"인프라":2,"자동화":1,"관측성":3,"데이터":0}

## 1. 개요 및 목적

Hermes를 개인 비서와 모델별 분석 도구로 사용하기 위해 기존 프로필을 백업·정리하고, Antigravity 기반 researcher와 Claude Code 기반 analyst를 구성했다. 기존 hybrid-v2는 일반 비서 역할과 공유 Discord 봇 연결을 담당한다. 연구 채널 두 개는 researcher, 토이프로젝트 채널은 analyst가 응답하도록 분리했다.

researcher에는 Obsidian·Notion, analyst에는 Obsidian·Notion·Swallow MCP를 연결했다. hybrid-v2·researcher·analyst의 OpenViking 공급자 설치와 실제 인증·임시 메모 저장·읽기·검색 요청을 확인했다. 세 프로필은 동일 사용자 계정 아래 별도 assistant peer를 사용한다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 발생 현상 / 요구사항
- 원인 분석 / 설계 검토
- 2. 해결 방안 및 설계
- 프로필과 Discord 역할
- 지식·메모리 연결
- 논문 저장 방식
- 3. 주요 구현 내용
- 수정 및 추가 파일 목록
- 핵심 코드 / 설정 스니펫
- 런타임·비밀 설정
- 4. 검증 및 테스트 결과
- 자동화 테스트 (단위 / 회귀)
- 실서비스 / UI 검증 증거
- 로컬 증거 위치
- 5. 배포 및 형상 관리
- 복구 참고
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
확인한 오류·진단:
- Discord: interaction expired before defer
- Discord: heartbeat blocked
- hybrid-v2 memory status: OpenViking Plugin NOT installed
```

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

## 4. 검증 근거 및 트러블슈팅

researcher에는 Obsidian·Notion, analyst에는 Obsidian·Notion·Swallow MCP를 연결했다. hybrid-v2·researcher·analyst의 OpenViking 공급자 설치와 실제 인증·임시 메모 저장·읽기·검색 요청을 확인했다. 세 프로필은 동일 사용자 계정 아래 별도 assistant peer를 사용한다.

researcher의 논문 분석 스킬은 markdown-converter로 변환한 원문과 한국어 정리본을 별도 노트로 저장하도록 확장했다. 실제 vault의 현재 Learning 폴더 구조를 확인해 예전 경로를 수정했고, [[Templates/paper-notes|논문 원문·학습노트 템플릿]]을 Obsidian MCP로 생성·재조회했다. 설정 적용과 검증은 완료했으며, 실제 논문 한 편을 Discord에서 받아 두 노트와 인덱스까지 저장하는 전체 흐름은 아직 검증하지 않았다.

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| 원인 규명 / 요구사항 | 모델별 개인 비서 역할 분리 | researcher는 논문·자료 조사, analyst는 해석·기술 비교·독립 검토 담당 |
| 설계 및 해결 방안 | 단일 봇과 프로필별 라우팅 | hybrid-v2 소유 Discord 연결을 공유하며 채널별 실행 프로필 분리 |
| 코드 / 설정 수정 | 프로필·라우트·MCP·메모리·스킬 | 선언적 구성, 프로필 설정, SOUL, 논문 스킬과 포맷 참고본 수정 |
| 실서비스 반영 | 기존 Hermes Docker 게이트웨이 | 설정별 재시작 후 Discord 연결과 제공 프로필 확인 |
| 검증 및 테스트 | 구성 검사·MCP 읽기·메모리·스킬 테스트 | 설정 회귀 13건 통과, 실제 MCP 조회, 임시 메모 왕복, 합성 모델 사례 검증 |
| 형상 관리 | dev-codex 로컬 커밋 | 최종 관련 커밋 2d4ccbf. 원격 push/PR 완료는 확인되지 않음 |

- 동일 Discord 봇 계정과 응답을 생성하는 Hermes 프로필은 서로 다르다. 봇 계정을 채널에서 제거하는 방식 대신 실행 프로필 라우팅으로 해결했다.
- researcher의 /status에서 Connected Platforms가 비어 있어도 공유 봇 연결을 사용하는 구조에서는 단독 어댑터가 없다는 의미일 수 있다. 상태 명령은 모델 추론을 하지 않아 토큰 0으로 표시된다.
- analyst의 /status 시간 초과 당시 로그에는 researcher 이미지 처리 중 동기식 Antigravity 스트림 읽기로 이벤트 루프가 막히고 Discord heartbeat·interaction 처리가 지연된 흔적이 있었다. 이후 응답은 복구됐으나 이 차단 문제 자체를 수정한 것은 아니다.
- hybrid-v2는 OpenViking 설정만 존재하고 현재 버전에 필요한 공급자 플러그인이 누락돼 있었다.
- 논문 스킬 작성 시 저장소의 예전 위키 경로를 재사용한 오류가 있었다. 사용자 지적 후 실제 Obsidian의 Home·Learning 인덱스·템플릿·기존 논문 노트를 조회해 현재 구조로 수정했다.

1. 현재 Obsidian의 [[Templates/paper-notes]]와 Learning 인덱스를 MCP로 읽는다.
2. 기존 markdown-converter 스킬을 읽고 MarkItDown으로 원문 HTML/PDF를 변환한다.
3. 읽은 범위·추출 한계를 표시하고 근거와 분석자의 해석을 구분한다.
4. 저장 요청 시 원문과 학습노트를 각각 저장하고 상호 링크를 넣는다.
5. 각 노트와 변경한 인덱스를 다시 읽어 검증한다. 일부 실패는 부분 완료로 보고한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Hermes/2026-10-21-Hermes-프로필-Discord-MCP-메모리-논문스킬-구성]]
- [[Dev/index|Dev 인덱스]]
