---
created: 2026-10-06
date: 2026-10-06
project: Gullinkambi
type: worklog
status: in-progress
tags:
  - gullinkambi
  - grafana
  - openviking
  - hermes
  - mcp
  - monitoring
---

# OpenViking 탭 개선과 Hermes Grafana MCP 연결

## 요약

`Aviary Control Room`의 `OpenViking 모니터링` 탭을 읽기 쉽게 고치고, Hermes가 Grafana를 조회할 수 있도록 조회 전용 `grafana` MCP를 연결했다. 대시보드 변경은 `main`에 반영했고 NAS Grafana Git Sync가 받았다. Hermes MCP는 연결 시험까지 통과했지만, 실제 세션에서의 조회는 아직 확인하지 못했다.

## OpenViking 대시보드

### 별도 대시보드는 필요 없다

같은 패널 12개가 두 곳에 중복되어 있다.

- `Aviary Control Room`의 `OpenViking 모니터링` 탭 (Git Sync)
- 단독 대시보드 `provisioning/dashboards/openviking/openviking-overview.json` (file provisioning)

그래서 새 대시보드를 만들지 않고 탭을 고쳤다. 단독 대시보드는 아직 예전 방식 그대로다.

### 지표 종류 확인

exporter(`Birds-Nest/docker-compose/monitoring/openviking-exporter/exporter.py`)가 SQLite 전체 행을 `COUNT(*)`로 세어 내보내는 누적 counter였다. 이 값을 그대로 그려서 계속 올라가는 선만 보였다.

| 지표 | 종류 |
| --- | --- |
| `openviking_requests_total`, `openviking_usage_tokens_total` | counter (누적) |
| `openviking_request_duration_ms_avg`, `openviking_request_errors_last_hour`, `openviking_queue_messages` 등 | gauge |

### 수정 내용

| 패널 | 문제 | 수정 |
| --- | --- | --- |
| Token Usage, API Requests | 누적값을 그대로 표시 | `increase(...[$__rate_interval])`로 구간 증가량 표시, 막대 그래프, 범례 합계(`sum`) |
| Errors Last Hour | 80건에서야 빨간색 | 1건 노랑, 3건 빨강 (알람 기준 3건 이상과 동일) |
| Container Memory, Data Size, Session Files | 빨강 기준이 80이라 bytes 단위 패널이 항상 빨갛게 표시 | 빨강 기준 제거, 초록 하나 |
| Container Memory | 스파크라인이 숫자와 겹침 | `graphMode: none` |
| Queue Messages | 비어 있으면 `데이터 없음` | 문구를 `대기 중인 메시지 없음`으로 변경 |

Queue Messages는 고장이 아니다. exporter가 큐에 남은 행만 세어서 큐가 비면 시리즈가 사라진다. 최근 30일 안에 시리즈가 존재한 적이 있어 패널은 유지했다.

### Git 기록

| 커밋 | 내용 |
| --- | --- |
| `1ee29a9` | counter 증가량 표시와 임계값 정리 |
| `2441f77` | 큐 패널 빈 상태 문구 개선 |
| `32d94cd` | 메모리 패널 스파크라인 제거 |
| `6ca7243` | 토큰·요청 패널을 막대와 구간 합계로 변경 |

## 반영 경로

- **Git Sync:** `main`에 push하면 NAS Grafana(`192.168.219.99:3002`)가 60초 주기로 가져온다. Grafana 로그의 `r4l2wj-sync`와 커밋 SHA로 확인했다. 브라우저에 이전 화면이 남아 있어서 처음에는 그대로인 것처럼 보였다. 강제 새로고침이 먼저다.
- **file provisioning:** NAS의 `/volume3/Gullinkambi` checkout이 `provisioning/alerting`, `provisioning/dashboards`를 마운트한다. 이쪽은 자동 갱신되지 않아 `git pull --ff-only`가 필요하다. 이번에 `1ee29a9`, `6ca7243`까지 맞췄다.
- `ssh NAS`(kimdove, port 99)는 이날부터 접속된다.

## Hermes Grafana MCP

### 구성

| 항목 | 값 |
| --- | --- |
| 서버 | Grafana 공식 `mcp-grafana` (`uvx mcp-grafana --disable-write`) |
| 권한 | 서비스 계정 `hermes-dashboard-readonly` (Viewer) |
| 노출 도구 | 조회 도구 15개를 이름으로 지정 (대시보드 검색·조회, 데이터소스, Prometheus, 알림 규칙) |
| Grafana 주소 | `https://monitoring.dove-nest.com` |

서버가 제공하는 도구는 62개지만, 에이전트가 고르기 쉽도록 조회 도구만 `include`로 남겼다. 쓰기 도구는 `--disable-write`와 Viewer 권한으로 이중으로 막았다.

### 설정 위치

실제 Hermes는 이 Mac의 `~/.hermes`가 아니라 Mac mini Docker 컨테이너 `hermes`다.

- `HERMES_HOME=/opt/data` = `/Volumes/Dove-Nest-SSD/Birds-Nest/hermes`
- 활성 프로필은 `hybrid-v2`이고 자체 `mcp_servers`를 가진다. 그래서 `hermes/profiles/hybrid-v2/config.yaml`에 `grafana` 블록을 추가했다. 루트 `config.yaml`만 고치면 적용되지 않는다.
- 토큰은 `Birds-Nest/docker-data/agents/secrets/grafana-mcp-token`(권한 600)에서 읽는다. `docker-data/*`가 git 무시 대상이고, 컨테이너가 `/Volumes/Dove-Nest-SSD` 전체를 같은 경로로 마운트해서 재생성 없이 읽힌다. 설정 파일에는 토큰을 넣지 않았다.
- 이 Mac의 `~/.hermes/config.yaml`에 먼저 추가했던 항목은 쓰이지 않아 삭제했다.

### 시행착오

1. **기존 토큰 재사용 보류:** `hermes-dashboard-import`는 Editor 역할이고 만료가 없으며 다른 용도로 쓰이고 있어서 MCP에 쓰지 않았다. 새 Viewer 계정의 토큰을 발급했다.
2. **글롭 필터 오작동:** `include`에 `get_dashboard_*` 같은 글롭을 쓰자 Hermes가 `7 selected`로만 잡았다. 또 `*alert*`에는 라우팅을 바꾸는 `alerting_manage_routing`도 걸렸다. 이름 15개를 직접 적어 `15 selected`로 맞췄다.
3. **컨테이너에서 LAN IP 접속 불가:** 컨테이너에서 `192.168.219.99:3002`는 응답하지 않고(`000`), `https://monitoring.dove-nest.com`은 200이었다. 접속 주소를 도메인으로 바꿨다.
4. **토큰 저장 명령 잘림:** 클립보드를 파일로 저장하는 명령이 입력 도중 잘려 빈 파일이 생겼다. 토큰 파일은 600 권한으로 정리했다.

### 검증

- 컨테이너 안에서 토큰이 `hermes-dashboard-readonly`로 인증됨을 확인했다.
- `hermes -p hybrid-v2 mcp test grafana`가 1.6초 만에 연결됐고 도구 62개를 확인했다. `mcp list`에는 `15 selected`로 표시된다.

## 남은 일

- Hermes 세션에서 `/reload-mcp` 실행 후 실제 조회 확인. Discord 등 gateway 세션은 컨테이너 재시작이 필요할 수 있다.
- 단독 `OpenViking Overview`를 지울지, 같은 수정을 적용할지 결정.
- `README.md`, `docs/README_KO.md`에 OpenViking 패널 변경과 Claude·Antigravity 초기화 패널 통합 반영.
- `hybrid-v2/config.yaml`에는 이번 작업 전부터 커밋되지 않은 큰 변경이 있다. 이번 추가분은 그 위에 한 덩어리만 얹었으므로, 같은 파일을 만지는 다른 작업과 충돌하지 않는지 확인한다.

## 운영 메모

- Grafana 토큰은 Viewer 계정만 쓴다. Editor 토큰은 MCP에 연결하지 않는다.
- 토큰 파일 권한은 600으로 유지하고, 저장소나 설정 파일에 값을 넣지 않는다.
- 다른 프로필(`analyzer`, `critic` 등)과 루트 `config.yaml`에는 추가하지 않았다.

## 관련

- [[Work/Gullinkambi/2026-10-05-Claude-Antigravity-초기화-패널-5시간·주간-통합|Claude·Antigravity 초기화 패널 5시간·주간 통합]]
- [[Work/Gullinkambi/2026-10-03-AI-subscription-exporter-README|AI subscription exporter README]]
- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
