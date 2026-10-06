---
created: 2026-10-01
date: 2026-10-01
project: Gullinkambi
type: worklog
status: completed
tags:
  - gullinkambi
  - orca
  - antigravity
  - hermes
  - telemetry
  - grafana
  - monitoring
---

# ORCA Antigravity 사용량 집계와 Hermes 인증 복구

## 요약

ORCA의 기존 Codex·Claude 일별 사용량 집계에 Antigravity agent 사용량을 추가했다. Mac mini에서 Antigravity 로컬 대화 DB를 읽되 토큰 숫자·모델·날짜·익명화한 프로젝트 정보만 privacy-safe JSON으로 변환하고, 기존 Hermes telemetry 경로를 통해 NAS TimescaleDB와 Gullinkambi Grafana 대시보드에 전달한다.

배포 점검 중 macOS LaunchAgent의 외장 볼륨 접근 제한과 Hermes의 이중 인증 저장소 drift도 발견했다. LaunchAgent 실행본을 사용자 Library로 옮겨 권한 문제를 해결했고, 새 OpenRouter 인증을 외부 Hermes 인증 저장소에 병합해 gateway를 정상 복구했다.

## 완료 결과

| 작업 | 결과 |
| --- | --- |
| Antigravity 사용량 추출 | ORCA worktree에 속한 대화의 일별 모델·토큰 수치 집계 |
| 개인정보 최소화 | 대화·reasoning·도구 본문, 경로, conversation ID를 전송하지 않음 |
| Telemetry 연결 | privacy-safe JSON을 `hermes-telemetry`가 기존 n8n webhook으로 전송 |
| TimescaleDB 저장 | `observability.orca_usage_daily`에 `agent='antigravity'`로 저장 |
| Grafana 표시 | ORCA 총 토큰·호출 수·모델별 사용량·일일 추이 패널에 포함 |
| LaunchAgent 복구 | 외장 SSD 실행 차단을 피하도록 사용자 Application Support에서 실행 |
| Hermes 복구 | OpenRouter 인증 병합, 기본 runtime 인증 제거, control-plane drift 해소 |
| 최종 상태 | Hermes `healthy`, telemetry 정상, LaunchAgent 마지막 종료 코드 `0` |

## 데이터 흐름

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

Antigravity 원본 DB는 container나 NAS에 마운트하지 않는다. Mac mini의 로컬 변환기만 원본을 읽고, telemetry container에는 결과 JSON 한 개만 읽기 전용으로 제공한다.

## Antigravity 집계 구현

### 데이터 선택

- Antigravity summary DB에서 ORCA가 관리하는 worktree에 속한 conversation만 선택한다.
- conversation별 생성 metadata에서 모델과 token usage를 읽는다.
- 날짜·모델·익명화한 프로젝트 ID 단위로 합산한다.
- ORCA 바깥에서 만든 검증용 conversation은 자동 제외된다.

### Token 필드

Antigravity headless JSON과 제어된 테스트 conversation을 대조해 내부 usage metadata를 확인했다.

| 내부 필드 | 집계 필드 |
| --- | --- |
| 2 | input token |
| 3 | output token |
| 5 | cache read token |
| 9 | thinking/reasoning token |

Antigravity의 output token에는 thinking token이 포함되며, total token은 input과 output의 합이다. Cache read는 별도 항목으로 표시하므로 total에 다시 더하지 않는다.

### Privacy-safe 출력

출력 파일에는 다음 항목만 포함한다.

- 사용 날짜
- agent: `antigravity`
- 모델
- 모델 호출 수
- input/cache read/output/reasoning/total token
- 마지막 경로 구성요소로 만든 화면용 프로젝트명
- 원래 프로젝트 식별자의 SHA-256 hash

다음 항목은 출력하지 않는다.

- 사용자 prompt와 assistant response
- reasoning·thinking 본문
- tool call 내용
- 로컬 전체 경로와 workspace URI
- conversation ID
- 로그인·인증 정보

## 실제 집계 검증

2026-10-01 TimescaleDB에 다음 두 행이 저장된 것을 직접 확인했다.

| 모델 | 호출 수 | 입력 | 캐시 읽기 | 출력 | Reasoning | 총 토큰 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gemini-3.8-flash` | 197 | 4,151,348 | 19,482,513 | 52,649 | 27,788 | 4,203,997 |
| `gemini-3.8-flash-high` | 3 | 24,475 | 409,875 | 2,061 | 1,791 | 26,536 |
| **합계** | **200** | **4,175,823** | **19,892,388** | **54,710** | **29,579** | **4,230,533** |

Telemetry cursor에서도 Antigravity 집계 2개가 pending 없이 처리됐고, Mac mini의 `hermes-telemetry` container는 restart 없이 실행 중임을 확인했다.

## Grafana 대시보드

ORCA 패널 SQL은 특정 agent를 제한하지 않고 `observability.orca_usage_daily` 전체를 합산한다. 따라서 Antigravity 행이 저장되면 다음 패널에 자동 포함된다.

- Orca 총 토큰
- Orca 모델 호출 수
- Orca 모델별 사용량
- Orca 토큰 사용 추이

패널 설명도 Codex·Claude·Antigravity 지원 범위에 맞게 변경했다. Antigravity 변환기는 개인정보 보호를 위해 conversation ID를 내보내지 않으므로 **쓰레드별 사용량 패널은 Codex와 Claude만 지원**한다.

Gullinkambi `main` push 후 Grafana API health가 정상이고 repository provisioning health check가 모두 성공했으며 incremental Git Sync가 실행된 것을 확인했다.

## LaunchAgent 권한 문제와 해결

### 증상

최초 LaunchAgent는 외장 SSD의 Birds-Nest checkout에 있는 Python 파일을 직접 실행했다. macOS가 background process의 외장 볼륨 접근을 차단하면서 다음 오류와 종료 코드 `2`가 발생했다.

```text
python3: can't open file '.../antigravity_orca_usage.py': Operation not permitted
```

### 해결

실행본을 다음 사용자 Library 경로에 설치했다.

```text
~/Library/Application Support/Gullinkambi/antigravity_orca_usage.py
```

LaunchAgent plist도 이 경로를 사용하도록 수정했다. 이후 60초 주기 실행이 정상 종료됐고 집계 파일이 권한 `0600`으로 갱신됐다. 주기 작업 사이에는 LaunchAgent 상태가 `not running`으로 보일 수 있지만 마지막 종료 코드가 `0`이면 정상이다.

## Hermes 인증 drift와 복구

### 원인

Telemetry 배포 과정에서 Hermes container가 다시 생성되면서 기존 control-plane drift가 드러났다.

- 기본 runtime 저장소: 새 `openrouter` 인증
- 외부 활성 저장소: 기존 `openrouter`, `openai-codex`, `active_provider`

Control-plane은 기본 `HERMES_HOME`에 인증 상태가 남아 있으면 기동을 중단하므로 Hermes가 restart loop에 들어갔다.

### 복구 절차

1. 기본 저장소와 외부 저장소를 각각 권한 `0600`으로 백업했다.
2. 외부 저장소를 기준으로 새 `openrouter` 항목을 깊은 병합했다.
3. 기존 `openai-codex`와 `active_provider`가 그대로인지 비교 검증했다.
4. 병합 결과를 임시 파일에 기록하고 `fsync` 후 원자적으로 교체했다.
5. 기본 runtime의 중복 인증 파일을 제거했다.
6. Hermes를 재시작하고 control-plane과 container health를 확인했다.

백업 위치:

```text
docker-data/agents/secrets/backups/hermes-auth-before-merge-20261001-175559.json
docker-data/agents/secrets/backups/default-auth-migrated-20261001-175559.json
```

백업과 활성 인증 저장소는 모두 권한 `0600`이다. 노트에는 credential 값 자체를 기록하지 않는다.

### 복구 검증

```text
control-plane: IN SYNC
credential_pool: openai-codex, openrouter
active_provider: preserved
default runtime auth: absent
Hermes container: running / healthy / restart 0
Telemetry container: running / restart 0
```

기존 사용자 변경인 `hermes/profiles/hybrid-v2/config.yaml`은 건드리지 않았다.

## 테스트와 검증

- Antigravity headless JSON으로 제어된 2-turn token 증가량 대조
- Privacy-safe 변환기 단위 테스트 추가
- Hermes telemetry 전체 테스트 17개 통과
- 출력 JSON에서 경로·conversation ID·workspace URI 부재 확인
- 출력 파일 권한 `0600` 확인
- Telemetry cursor의 Antigravity 2개 처리와 pending 0 확인
- TimescaleDB 실제 행 조회
- 세 Grafana dashboard JSON 문법 검사
- Grafana Git Sync repository health 성공 확인
- Hermes control-plane `IN SYNC`와 container `healthy` 확인

## 주요 파일

| 저장소 | 파일 | 역할 |
| --- | --- | --- |
| Birds-Nest | `docker-compose/agents/hermes-telemetry/antigravity_orca_usage.py` | Antigravity 원본에서 privacy-safe 일별 집계 생성 |
| Birds-Nest | `docker-compose/agents/hermes-telemetry/com.gullinkambi.antigravity-orca-usage.plist` | macOS 60초 주기 실행 |
| Birds-Nest | `docker-compose/agents/hermes-telemetry/collector.py` | Antigravity 집계를 telemetry payload로 정규화 |
| Birds-Nest | `docker-compose/agents/docker-compose.yml` | 집계 JSON read-only mount |
| Gullinkambi | `provisioning/dashboards/git-sync/Aviary Control Room.json` | ORCA Antigravity 표시와 패널 설명 |

## Git 기록

| 저장소·브랜치 | 커밋 | 내용 |
| --- | --- | --- |
| Birds-Nest `dev-nas` | `51b955c` | Antigravity ORCA 사용량 집계 추가 |
| Birds-Nest `dev-mac` | `2984c15` | Mac mini에 동일한 집계 구현 배포 |
| Birds-Nest `dev-nas` | `e48bf0e` | LaunchAgent 실행본을 사용자 Library로 이동 |
| Birds-Nest `dev-mac` | `9807316` | Mac mini LaunchAgent 경로 수정 배포 |
| Gullinkambi `main` | `4f97d11` | ORCA 대시보드에 Antigravity 지원 범위 반영 |

Hermes 인증 병합은 비밀 저장소의 운영 복구 작업이므로 Git에 credential이나 변경값을 커밋하지 않았다.

## 운영 메모

- LaunchAgent가 종료 코드 `2`를 남기면 외장 볼륨 경로를 다시 가리키는지 먼저 확인한다.
- 스크립트를 갱신하면 저장소 파일뿐 아니라 `~/Library/Application Support/Gullinkambi/`의 실행본도 다시 설치한다.
- Antigravity 집계가 보이지 않으면 LaunchAgent → privacy-safe JSON → telemetry cursor → TimescaleDB 순서로 확인한다.
- Antigravity total token에 cache read를 다시 합산하지 않는다.
- 원본 conversation DB를 telemetry container나 NAS에 직접 마운트하지 않는다.
- Hermes 인증 변경은 외부 저장소를 먼저 백업하고 `openai-codex`와 `active_provider` 보존 여부를 검증한다.

## 관련

- [[Work/Gullinkambi/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축|AI 구독 사용량 수집기·Grafana 대시보드 구축]]
- [[Work/Gullinkambi/2026-10-01-Grafana-알람과-Discord-연결|Grafana 알람과 Discord 연결]]
- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
