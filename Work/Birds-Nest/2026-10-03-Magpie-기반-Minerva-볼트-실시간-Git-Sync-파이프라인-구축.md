---
title: Magpie 기반 Minerva 볼트 실시간 Git Sync 파이프라인 구축 및 검증
date: 2026-10-03
author: 로빈 (Robin / Antigravity) with 둘기 (Dove), Claude (Opus 5.5), Codex (GPT-6.1)
category: Infra/Wiki
tags:
  - infra
  - birds-nest
  - obsidian
  - git-sync
  - inotify
  - magpie
  - n8n
  - discord
  - multi-agent
---

# 🕊️ Magpie 기반 Minerva 볼트 실시간 Git Sync 파이프라인 구축 및 검증

## 1. 개요 및 배경
- **목적**: 다른 AI 에이전트(Hermes, Codex, Antigravity 등) 및 둘기님이 옵시디언 볼트(`Minerva`)에 문서를 생성하거나 수정할 때, 실시간으로 원격 저장소(`EvoDmiK/Minerva`)로 Git 백업을 수행하고 n8n `[LLM-Wiki] Magpie` 워크플로우를 트리거하여 Discord `#llm-위키`로 동기화 현황 카드를 실시간 전송.
- **주요 요구사항**:
  1. Claude (Opus 5.5) 및 Codex (GPT-6.1)와의 멀티 에이전트 기술 검토를 통한 아키텍처 수렴.
  2. 파일 시스템 레벨 실시간 감시(`inotifywait`) 및 연타/작성 중 쪼개기 방지 디바운스(15초) 적용.
  3. Git 다중 프로세스 충돌 방지 및 단일 Git Writer(`obsidian-git-sync`) 체계 확립.
  4. n8n Magpie 파이프라인 확장: 웹훅 수신 -> Rich Embed 카드 포맷팅 -> 디스코드 알림 발행.

---

## 2. 멀티 에이전트 기술 검토 및 역할 분담
- **Claude (Opus 5.5)**:
  - n8n `Minerva Sync Webhook` 노드 및 Discord Embed 카드 포맷팅 아키텍처 제안.
  - 옵시디언 내부 플러그인(`github-sync`)과 호스트 사이드카 간 동시 푸시 시 발생하는 `.git/index.lock` 충돌 위험 경고 및 단일 Writer 원칙 강조.
- **Codex (GPT-6.1)**:
  - `inotifywait` 기반 파일 이벤트 감시 루프 설계.
  - 15초 Quiet Period(디바운스)와 최대 60초 대기 시간(`GIT_SYNC_MAX_WAIT`)을 통한 커밋 최적화 제안.
  - 감시 제외 필터(`--exclude '(\.git|\.trash|\.obsidian/workspace\.json)'`)를 통한 무한 루프 차단 설계.
- **로빈 (Robin / Antigravity)**:
  - 전체 파이프라인 오케스트레이션 및 코드 구현, n8n 프로덕션 DB 배포.
  - Docker tmpfs 권한 이슈 및 인증 트러블슈팅, E2E 실시간 검증 총괄.

---

## 3. 핵심 아키텍처 및 구현 내역

### 3.1 obsidian-git-sync 사이드카 개선 (`docker-compose/homelab/obsidian-git-sync/`)
- **`Dockerfile`**: `inotify-tools`, `curl` 패키지 추가 탑재.
- **`sync.sh` 실시간 루프 및 디바운스**:
  - `inotifywait -qq -r -t $interval -e close_write,create,delete,moved_to,moved_from` 감시.
  - 파일 변경 감지 시 15초간 추가 변경 여부를 확인하는 디바운스 루프 진입.
- **자격증명 무결성 (`credential.helper store`)**:
  - Docker `/tmp`의 `noexec` 마운트 특성으로 인한 `git-askpass` 실행 실패 문제를 해결하기 위해, Git 표준 `credential.helper "store --file ..."` 방식으로 전환.
  - HTTPS Token 및 SSH Key(`id_ed25519`) 이중 인증 지원 체계 완성.
- **웹훅 연동**:
  - Push 완료 즉시 `send_webhook "pushed" "$new_head" "$files_json"` 실행 (`http://n8n:5678/webhook/minerva-sync`).

### 3.2 n8n [LLM-Wiki] Magpie 워크플로우 확장
- **Minerva Sync Webhook 노드**: `POST /webhook/minerva-sync` 엔드포인트 수신.
- **Format Minerva Card 노드**:
  - 커밋 해시 링크(`https://github.com/EvoDmiK/Minerva/commit/{sha}`), 브랜치, 동기화된 파일 목록 파싱.
  - 성공(초록/0x10A37F), 충돌(빨강/0xE74C3C), 오류(주황/0xE67E22) 상태별 Discord Embed 카드 동적 생성.
- **Minerva Discord Alert 노드**:
  - 대상 채널: `#llm-위키` (`1509539778775744633`).

### 3.3 Semantic Notes Vault MCP 활성화
- 볼트 내 `semantic-vault-mcp` 플러그인 활성화 및 Streamable HTTP MCP 엔드포인트(`https://wiki.dove-nest.com/mcp`) 정상 가동.
- 에이전트들이 MCP 도구(`vault`, `edit`, `view` 등)를 통해 볼트 문서를 직접 열람/수정/생성 가능.

---

## 4. 트러블슈팅 및 해결
1. **GitHub 인증 자격증명 누락**:
   - 증상: `fatal: could not read Username for 'https://github.com': terminal prompts disabled`.
   - 해결: NAS의 `/volume3/Birds-Nest/docker-data/homelab/obsidian/git-sync/`에 GitHub 사용자명 및 토큰, SSH 키 구성.
2. **Alpine tmpfs noexec 권한 이슈**:
   - 증상: `fatal: cannot exec '/tmp/obsidian-git-sync/git-askpass': Permission denied`.
   - 해결: 셸 스크립트 실행 방식 대신 Git 내장 `credential.helper store`를 사용하여 파일 직접 파싱 방식으로 전격 교체.
3. **MCP 502 Bad Gateway 에러**:
   - 증상: `https://wiki.dove-nest.com/mcp` 호출 시 502 반환.
   - 해결: `community-plugins.json`에 `semantic-vault-mcp`를 등록하고 옵시디언 컨테이너를 재시작하여 포트 3443 정상 리스닝 확인.

---

## 5. 최종 검증 결과
- **테스트 케이스**: MCP 클라이언트를 통한 실시간 문서 작성.
- **이벤트 추적**:
  1. MCP 문서 생성 감지: `inotifywait` 포착 -> 15초 디바운스.
  2. 일괄 Git Commit 및 GitHub 원격 저장소(`EvoDmiK/Minerva`) 푸시 성공.
  3. Magpie 웹훅 수신 및 n8n 실행(ID: 22154 등) 성공.
  4. Discord `#llm-위키` 채널에 실시간 Embed 카드 알림 정상 발행 확인.
  5. Mac 로컬 옵시디언 볼트(`/Volumes/Dove-Nest-SSD/Minerva`) 동기화 확인.
