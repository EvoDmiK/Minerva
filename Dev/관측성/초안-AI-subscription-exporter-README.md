---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-03-AI-subscription-exporter-README]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# AI subscription exporter

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-03-AI-subscription-exporter-README]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":28,"데이터":0}

## 1. 개요 및 목적

Codex, Claude Code, Google Antigravity의 개인 구독 사용률을 Prometheus 형식으로 노출하는 macOS용 로컬 exporter입니다. 로그인 토큰이나 설정 파일 자체는 노출하지 않습니다.

- Codex: `codex app-server`의 `account/rateLimits/read`와 `account/usage/read`
- Claude: Claude Code status line 입력의 `rate_limits.five_hour`와 `rate_limits.seven_day`
- Antigravity: `agy -p "/usage" --output-format json`의 Gemini·Claude/GPT 5시간·주간 quota
- HTTP: `0.0.0.0:9819/metrics`

## 2. 핵심 아키텍처 및 원칙

- 데이터 경로
- Mac mini 설치
- 환경 변수
- Grafana 알람
- 검증
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```bash
cd /Volumes/Dove-Nest-SSD/Birds-Nest/docker-compose/monitoring/ai-subscription-exporter
python3 install.py --configure-claude-statusline
```

```bash
curl http://127.0.0.1:9819/metrics
launchctl print gui/$(id -u)/com.gullinkambi.ai-subscription-exporter
```

```bash
python3 install.py --uninstall
```

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/gullinkambi-ai-subscription-pycache \
  python3 -m py_compile exporter.py claude_statusline_capture.py claude_statusline_mux.py install.py
```

## 4. 검증 근거 및 트러블슈팅

Claude는 실제 메시지 처리 시 status line이 갱신되므로 15분 stale 규칙을 적용하지 않습니다. 대신 마지막 유효 캐시를 보존하고 기본 24시간 만료 여부를 `ai_subscription_collector_up`에 반영합니다. 빈 `rate_limits` 입력 때문에 collector down 알람이 발생한다면 실행 중인 파일에 캐시 보존 수정이 배포됐는지 확인하세요.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-03-AI-subscription-exporter-README]]
- [[Dev/index|Dev 인덱스]]
