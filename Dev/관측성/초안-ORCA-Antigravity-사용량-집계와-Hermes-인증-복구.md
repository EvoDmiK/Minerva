---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# ORCA Antigravity 사용량 집계와 Hermes 인증 복구

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구]] · 분류 근거 {"인프라":1,"자동화":4,"관측성":56,"데이터":6}

## 1. 개요 및 목적

ORCA의 기존 Codex·Claude 일별 사용량 집계에 Antigravity agent 사용량을 추가했다. Mac mini에서 Antigravity 로컬 대화 DB를 읽되 토큰 숫자·모델·날짜·익명화한 프로젝트 정보만 privacy-safe JSON으로 변환하고, 기존 Hermes telemetry 경로를 통해 NAS TimescaleDB와 Gullinkambi Grafana 대시보드에 전달한다.

배포 점검 중 macOS LaunchAgent의 외장 볼륨 접근 제한과 Hermes의 이중 인증 저장소 drift도 발견했다. LaunchAgent 실행본을 사용자 Library로 옮겨 권한 문제를 해결했고, 새 OpenRouter 인증을 외부 Hermes 인증 저장소에 병합해 gateway를 정상 복구했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 완료 결과
- 데이터 흐름
- Antigravity 집계 구현
- 데이터 선택
- Token 필드
- Privacy-safe 출력
- 실제 집계 검증
- Grafana 대시보드
- LaunchAgent 권한 문제와 해결
- 증상
- 해결
- Hermes 인증 drift와 복구
- 원인
- 복구 절차
- 복구 검증
- 테스트와 검증
- 주요 파일
- Git 기록
- 운영 메모
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
Antigravity conversation DB
          │
          │ Mac mini 사용자 권한, ORCA worktree만 선택
          ▼
antigravity_orca_usage.py
          │
          │ 토큰·모델·날짜·project hash만 기록
          ▼
~/Library/Application Support/orca/orca-antigravity-usage.json
          │ read-only mount
          ▼
hermes-telemetry → n8n webhook → TimescaleDB
                                      │
                                      ▼
                         Gullinkambi / ORCA 모니터링
```

```text
python3: can't open file '.../antigravity_orca_usage.py': Operation not permitted
```

```text
~/Library/Application Support/Gullinkambi/antigravity_orca_usage.py
```

```text
docker-data/agents/secrets/backups/hermes-auth-before-merge-20261001-175559.json
docker-data/agents/secrets/backups/default-auth-migrated-20261001-175559.json
```

```text
control-plane: IN SYNC
credential_pool: openai-codex, openrouter
active_provider: preserved
default runtime auth: absent
Hermes container: running / healthy / restart 0
Telemetry container: running / restart 0
```

## 4. 검증 근거 및 트러블슈팅

- Antigravity summary DB에서 ORCA가 관리하는 worktree에 속한 conversation만 선택한다.
- conversation별 생성 metadata에서 모델과 token usage를 읽는다.
- 날짜·모델·익명화한 프로젝트 ID 단위로 합산한다.
- ORCA 바깥에서 만든 검증용 conversation은 자동 제외된다.

Antigravity headless JSON과 제어된 테스트 conversation을 대조해 내부 usage metadata를 확인했다.

2026-10-01 TimescaleDB에 다음 두 행이 저장된 것을 직접 확인했다.

Telemetry cursor에서도 Antigravity 집계 2개가 pending 없이 처리됐고, Mac mini의 `hermes-telemetry` container는 restart 없이 실행 중임을 확인했다.

Gullinkambi `main` push 후 Grafana API health가 정상이고 repository provisioning health check가 모두 성공했으며 incremental Git Sync가 실행된 것을 확인했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구]]
- [[Dev/index|Dev 인덱스]]
