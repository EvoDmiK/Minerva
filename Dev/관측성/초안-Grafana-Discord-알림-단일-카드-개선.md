---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-02-Grafana-Discord-알림-단일-카드-개선]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Grafana Discord 알림 단일 카드 개선

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-02-Grafana-Discord-알림-단일-카드-개선]] · 분류 근거 {"인프라":0,"자동화":6,"관측성":17,"데이터":0}

## 1. 개요 및 목적

Grafana가 Discord로 보내는 기본 알림이 여러 텍스트 블록으로 길게 표시되던 문제를 개선했다. Gullinkambi 전용 notification template을 추가하고 Discord embed description을 활성화해, 같은 알림 그룹의 발생·복구 항목을 한 개의 색상 카드로 묶어 전송한다.

`Source`, `Silence`, `Dashboard`, `Panel` 링크는 가능한 경우 카드 하단에 배치하며, 외부 기준 주소는 `https://monitoring.dove-nest.com`을 유지한다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 변경 전 문제
- 적용한 형식
- 구현
- 외부 링크
- 검증
- 주요 파일
- Git 기록
- 운영 메모
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
🚨 [FIRING] Gullinkambi Grafana 알림
✅ [RESOLVED] Gullinkambi Grafana 알림
```

```yaml
settings:
  url: $GF_DISCORD_WEBHOOK_URL
  use_discord_username: false
  use_embed_description: true
  title: '{{ template "gullinkambi.discord.title" . }}'
  message: |
    {{ template "gullinkambi.discord.message" . }}
```

```dotenv
GF_SERVER_DOMAIN=monitoring.dove-nest.com
GF_SERVER_ROOT_URL=https://monitoring.dove-nest.com/
```

## 4. 검증 근거 및 트러블슈팅

Grafana 컨테이너의 외부 URL 설정을 확인했다.

| 확인 항목 | 결과 |
| --- | --- |
| alerting YAML 파싱 | 성공 |
| `git diff --check` | 통과 |
| Grafana 13.2.1 재시작 | 정상 |
| notification template 로드 | 1개 로드 확인 |
| Discord contact point 설정 | `use_embed_description=true` 확인 |
| Grafana 외부 URL | `https://monitoring.dove-nest.com/` 확인 |
| Discord 단일 카드 테스트 | Webhook HTTP 204 |

Grafana 13의 contact point 테스트 API는 컨테이너 환경변수의 관리자 자격 증명과 실제 자격 증명이 달라 HTTP 401이 발생했다. 대신 Grafana 컨테이너에 설정된 동일 Discord Webhook으로 단일 embed 테스트를 전송해 HTTP 204를 확인했다. 비밀 URL은 출력하거나 파일에 저장하지 않았다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-02-Grafana-Discord-알림-단일-카드-개선]]
- [[Dev/index|Dev 인덱스]]
