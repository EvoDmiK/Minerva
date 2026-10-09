---
date: 2026-10-08
project: Gullinkambi
type: troubleshooting
status: resolved
tags:
  - gullinkambi
  - antigravity
  - monitoring
  - grafana
---

# Antigravity 구독 사용량 수집 복구

## 결과

Antigravity 구독 사용량 수집기의 잘못된 HOME 환경변수 지정을 제거하고 LaunchAgent를 재시작해 복구했다. 로컬 exporter 메트릭에서 Gemini·third_party 두 pool 모두 수집 성공을 확인했다. 마지막 성공 시각은 **2026-10-08 16:11:32 KST**다.

## 증상과 원인

사용자가 대시보드에서 Antigravity의 마지막 수집이 약 9시간 전이라고 보고했다. 중단 기간 전체를 별도로 조회하지는 않았다.

실제 실패 지점은 ORCA 대화별 토큰 집계 스크립트가 아니라 **AI 구독 사용량 exporter의 Antigravity CLI 실행 설정**이었다.

- LaunchAgent: `/Users/kimdove/Library/LaunchAgents/com.gullinkambi.ai-subscription-exporter.plist`
- 실행 코드: `/Volumes/Dove-Nest-SSD/projects/Birds-Nest/docker-compose/monitoring/ai-subscription-exporter/exporter.py`
- 오류 로그: `/Users/kimdove/Library/Logs/Gullinkambi/ai-subscription-exporter.error.log`

`EnvironmentVariables.ANTIGRAVITY_BIN`에 예전 사용자 홈 경로가 남아 있었다.

```text
/usr/bin/env HOME=/Users/dovekim-32 /opt/homebrew/bin/agy
```

CLI는 `agy -p /usage --output-format json` 실행 중 해당 경로에 디렉터리를 만들려다 실패했다. 두 pool 모두 아래 오류가 반복됐다.

```text
Failed to start: mkdir /Users/dovekim-32: permission denied
Antigravity usage command exited 1
```

## 조치

LaunchAgent의 `ANTIGRAVITY_BIN` 값을 다음과 같이 변경해 HOME 강제 지정을 제거했다.

```text
/opt/homebrew/bin/agy
```

이후 사용자 GUI 도메인에서 LaunchAgent를 다시 등록했다.

```sh
launchctl bootout gui/$(id -u)/com.gullinkambi.ai-subscription-exporter
launchctl bootstrap gui/$(id -u) /Users/kimdove/Library/LaunchAgents/com.gullinkambi.ai-subscription-exporter.plist
```

저장소 소스 코드는 수정하지 않았다. 변경 대상은 로컬 LaunchAgent 설정이다.

## 검증

`http://127.0.0.1:9819/metrics`를 직접 조회해 확인했다.

| pool | collector_up | 마지막 성공 시각 KST | 5시간 사용률 | 주간 사용률 |
| --- | --- | --- | --- | --- |
| gemini | 1 | 2026-10-08 16:11:32 | 19.53% | 55.69% |
| third_party | 1 | 2026-10-08 16:11:32 | 0% | 0% |

두 pool의 `ai_subscription_last_success_timestamp_seconds`는 `1791443492.59`였다. 사용률과 초기화 시각 메트릭도 반환됐다.

로컬 수집 성공까지 검증했다. Prometheus의 다음 scrape와 Grafana 화면 반영은 별도로 확인하지 않았다.

## 관련 문서

- [[Work/Gullinkambi/작업기록/2026-10-03-AI-subscription-exporter-README]]
- [[Work/Gullinkambi/작업기록/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축]]
- [[Work/Gullinkambi/작업기록/2026-10-08-ORCA-SSD-이전-후-사용량-수집-복구]]
