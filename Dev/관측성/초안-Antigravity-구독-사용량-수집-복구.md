---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-08-Antigravity-구독-사용량-수집-복구]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Antigravity 구독 사용량 수집 복구

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-08-Antigravity-구독-사용량-수집-복구]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":6,"데이터":0}

## 1. 개요 및 목적

Antigravity 구독 사용량 수집기의 잘못된 HOME 환경변수 지정을 제거하고 LaunchAgent를 재시작해 복구했다. 로컬 exporter 메트릭에서 Gemini·third_party 두 pool 모두 수집 성공을 확인했다. 마지막 성공 시각은 **2026-10-08 16:11:32 KST**다.

사용자가 대시보드에서 Antigravity의 마지막 수집이 약 9시간 전이라고 보고했다. 중단 기간 전체를 별도로 조회하지는 않았다.

## 2. 핵심 아키텍처 및 원칙

- 결과
- 증상과 원인
- 조치
- 검증
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
/usr/bin/env HOME=/Users/dovekim-32 /opt/homebrew/bin/agy
```

```text
Failed to start: mkdir /Users/dovekim-32: permission denied
Antigravity usage command exited 1
```

```text
/opt/homebrew/bin/agy
```

```sh
launchctl bootout gui/$(id -u)/com.gullinkambi.ai-subscription-exporter
launchctl bootstrap gui/$(id -u) /Users/kimdove/Library/LaunchAgents/com.gullinkambi.ai-subscription-exporter.plist
```

## 4. 검증 근거 및 트러블슈팅

Antigravity 구독 사용량 수집기의 잘못된 HOME 환경변수 지정을 제거하고 LaunchAgent를 재시작해 복구했다. 로컬 exporter 메트릭에서 Gemini·third_party 두 pool 모두 수집 성공을 확인했다. 마지막 성공 시각은 **2026-10-08 16:11:32 KST**다.

실제 실패 지점은 ORCA 대화별 토큰 집계 스크립트가 아니라 **AI 구독 사용량 exporter의 Antigravity CLI 실행 설정**이었다.

- LaunchAgent: `/Users/kimdove/Library/LaunchAgents/com.gullinkambi.ai-subscription-exporter.plist`
- 실행 코드: `/Volumes/Dove-Nest-SSD/projects/Birds-Nest/docker-compose/monitoring/ai-subscription-exporter/exporter.py`
- 오류 로그: `/Users/kimdove/Library/Logs/Gullinkambi/ai-subscription-exporter.error.log`

CLI는 `agy -p /usage --output-format json` 실행 중 해당 경로에 디렉터리를 만들려다 실패했다. 두 pool 모두 아래 오류가 반복됐다.

`http://127.0.0.1:9819/metrics`를 직접 조회해 확인했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-08-Antigravity-구독-사용량-수집-복구]]
- [[Dev/index|Dev 인덱스]]
