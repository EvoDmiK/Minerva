---
created: 2026-10-02
date: 2026-10-02
project: Gullinkambi
type: worklog
status: completed
tags:
  - gullinkambi
  - grafana
  - alerting
  - discord
  - monitoring
---

# Grafana Discord 알림 단일 카드 개선

## 요약

Grafana가 Discord로 보내는 기본 알림이 여러 텍스트 블록으로 길게 표시되던 문제를 개선했다. Gullinkambi 전용 notification template을 추가하고 Discord embed description을 활성화해, 같은 알림 그룹의 발생·복구 항목을 한 개의 색상 카드로 묶어 전송한다.

`Source`, `Silence`, `Dashboard`, `Panel` 링크는 가능한 경우 카드 하단에 배치하며, 외부 기준 주소는 `https://monitoring.dove-nest.com`을 유지한다.

## 변경 전 문제

- Antigravity의 `gemini`, `third_party` 같은 pool별 알림이 각각 긴 기본 메시지로 표시됐다.
- `Value`, `Labels`, `Annotations`가 그대로 출력돼 모바일 Discord에서 읽기 어려웠다.
- 복구 알림도 여러 블록으로 나뉘어 한눈에 상태를 파악하기 어려웠다.

## 적용한 형식

알림 상태에 따라 제목과 카드 색상이 바뀐다.

```text
🚨 [FIRING] Gullinkambi Grafana 알림
✅ [RESOLVED] Gullinkambi Grafana 알림
```

본문은 다음 순서로 구성한다.

1. 공통 alert name과 description
2. 발생 건수와 각 알림의 summary
3. 복구 건수와 각 알림의 summary
4. Source · Silence · Dashboard · Panel 링크

같은 `alertname`, `service`, `severity`로 그룹화된 여러 pool은 카드 한 장 안에서 목록으로 표시한다.

## 구현

`provisioning/alerting/notifications.yml`에 `Gullinkambi Discord card` template group을 추가했다.

Discord contact point에는 다음 핵심 설정을 적용했다.

```yaml
settings:
  url: $GF_DISCORD_WEBHOOK_URL
  use_discord_username: false
  use_embed_description: true
  title: '{{ template "gullinkambi.discord.title" . }}'
  message: |
    {{ template "gullinkambi.discord.message" . }}
```

`use_embed_description: true`가 메시지 본문을 Discord embed 내부에 넣어 단일 카드로 표시한다. Webhook URL은 계속 환경변수로만 전달하며 저장소나 노트에 실제 값을 기록하지 않았다.

## 외부 링크

Grafana 컨테이너의 외부 URL 설정을 확인했다.

```dotenv
GF_SERVER_DOMAIN=monitoring.dove-nest.com
GF_SERVER_ROOT_URL=https://monitoring.dove-nest.com/
```

따라서 `Source`와 `Silence` 링크는 `localhost:3000`이 아니라 `monitoring.dove-nest.com`을 사용한다.

## 검증

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

## 주요 파일

| 파일 | 역할 |
| --- | --- |
| `provisioning/alerting/notifications.yml` | Discord 카드 template, contact point, notification policy |
| `README.md` | 영문 운영 문서 |
| `docs/README_KO.md` | 한국어 운영 문서 |

## Git 기록

| 저장소 | 브랜치 | 커밋 | 내용 |
| --- | --- | --- | --- |
| Gullinkambi | `main` | `494ba89` | Discord 알림을 단일 compact card로 변경 |

변경 사항은 GitHub 원격 `main` 브랜치에 push했다.

## 운영 메모

- 알림 그룹 기준은 `alertname`, `service`, `severity`다.
- 같은 그룹의 여러 pool은 한 카드에 발생·복구 목록으로 합쳐진다.
- `disableResolveMessage: false`이므로 복구 카드도 전송된다.
- Dashboard 또는 Panel URL이 없는 규칙은 해당 링크만 생략된다.
- 실제 Webhook URL은 `GF_DISCORD_WEBHOOK_URL`로만 관리한다.

## 관련

- [[Work/Gullinkambi/작업기록/2026-10-01-Grafana-알람과-Discord-연결|Grafana 알람과 Discord 연결]]
- [[Work/Gullinkambi/작업기록/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축|AI 구독 사용량 수집기·Grafana 대시보드 구축]]
- [[Work/Gullinkambi/작업기록/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구|ORCA Antigravity 사용량 집계와 Hermes 인증 복구]]
- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
