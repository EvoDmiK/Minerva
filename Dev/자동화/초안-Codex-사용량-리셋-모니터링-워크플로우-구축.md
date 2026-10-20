---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Kestrel/2026-10-03-Codex-사용량-리셋-모니터링-워크플로우-구축]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# OpenAI Codex 사용량 리셋 모니터링 워크플로우 (Kestrel) 구축

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Kestrel/2026-10-03-Codex-사용량-리셋-모니터링-워크플로우-구축]] · 분류 근거 {"인프라":1,"자동화":16,"관측성":1,"데이터":1}

## 1. 개요 및 목적

OpenAI Codex의 사용량(한도) 리셋 정보를 제공하는 `https://codex-resets.com/api/v1/status` API를 연동하여, 리셋 완료 및 일정 예고 발생 시 Discord `모니터링-알림` 채널로 실시간 알림을 발송하는 n8n 자동화 워크플로우 `[Monitor] Kestrel`을 구축했다. Birds-Nest의 새(bird) 테마 규칙에 따라, 공중에 정지 비행(호버링)하며 지상을 날카롭게 주시하고 감시하는 황조롱이(**Kestrel**)를 워크플로우 및 디렉터리 명칭으로 적용했다.

n8n의 정적 상태 저장소(`$getWorkflowStaticData('global')`)를 활용하여 신규 리셋 이벤트 발생 시에만 알림을 발송하도록 중복 알림을 방지했으며, 첫 기동 시 현재 최신 현황 카드를 즉시 발송하여 채널 연동을 검증했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 아키텍처 및 파이프라인
- 주요 구성 요소
- 디스코드 메시지 포맷 (Discord Embed 카드)
- 배포 및 검증 결과
- 관련 링크
- 후속

## 3. 재사용 가능한 코드 스니펫 / 설정

```mermaid
flowchart LR
    A["Schedule Trigger<br/>(5분 주기)"] --> B["HTTP Request<br/>(codex-resets.com/api/v1/status)"]
    B --> C["Detect New Events<br/>(Static Data 기반 중복 방지)"]
    C --> D["Discord Alert<br/>(NestControl #모니터링-알림)"]
```

```json
{
  "title": "⚡ [Kestrel] OpenAI Codex 사용량 리셋 완료",
  "url": "https://codex-resets.com",
  "color": 1090431,
  "description": "> Reset all propagated. Enjoy.",
  "fields": [
    { "name": "🏷️ 리셋 유형", "value": "정기 리셋 (`regular`)", "inline": true },
    { "name": "🕒 공지 일시", "value": "2026. 10. 03. 06:18 KST", "inline": true },
    { "name": "📊 통계 현황", "value": "• 평균 주기: **6.8일**\\n• 직전 리셋 후: **0.3일 경과**", "inline": false },
    { "name": "🔗 관련 링크", "value": "[공식 X(트위터) 공지](<https://x.com/...>) • [Codex Resets 대시보드](<https://codex-resets.com>)", "inline": false }
  ],
  "footer": { "text": "Codex Resets Tracker • Monitored by Kestrel 🦅" }
}
```

## 4. 검증 근거 및 트러블슈팅

n8n의 정적 상태 저장소(`$getWorkflowStaticData('global')`)를 활용하여 신규 리셋 이벤트 발생 시에만 알림을 발송하도록 중복 알림을 방지했으며, 첫 기동 시 현재 최신 현황 카드를 즉시 발송하여 채널 연동을 검증했다.

| 노드명 | 노드 타입 | 역할 및 동작 상세 |
| --- | --- | --- |
| **Schedule Trigger** | `n8n-nodes-base.scheduleTrigger` (v1.2) | 5분 간격 주기적 트리거 (Cloudflare 엣지 캐시와 조화) |
| **Fetch Reset Status** | `n8n-nodes-base.httpRequest` (v4.2) | `GET https://codex-resets.com/api/v1/status` 호출 (무료, 무인증) |
| **Detect New Events** | `n8n-nodes-base.code` (v2) | • `latest_reset`: 신규 리셋 완료 감지 (`lastResetId` 추적)<br>• `scheduled_reset`: 리셋 예정 공지 감지 (`lastScheduledId` 추적)<br>• `active_watch`: 리셋 확률 상승 감시 (`lastWatchKey` 추적)<br>• 일시 한국 시간(KST) 변환 포맷팅 |
| **Discord Alert** | `n8n-nodes-base.discord` (v2) | `NestControl` 서버의 `모니터링-알림`(`1555400525904617542`) 채널로 Nesty 봇 메시지 전송 |

* **워크플로우명:** `[Monitor] Kestrel`
* **워크플로우 ID:** `NbuvdYcU7vd5pRnp`
* **파일 경로:** `n8n/Kestrel/workflows.json`
* **배포 환경:** NAS PostgreSQL DB (`postgres-n8n`, `n8n` 데이터베이스)
* **상태:** `Active: True`
* **테스트 발송 검증:** `모니터링-알림` 채널에 초기 현황 카드 발송 성공 확인 완료.

- [[Work/Birds-Nest/index|Birds-Nest 프로젝트 인덱스]]
- [[2026-10-02-Jev-AI-기반-carrier-pigeon-개편과-n8n-테스트베드-구축|이전 작업: carrier-pigeon 개편]]
- [[Home]]

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Kestrel/2026-10-03-Codex-사용량-리셋-모니터링-워크플로우-구축]]
- [[Dev/index|Dev 인덱스]]
