---
created: 2026-10-24
date: 2026-10-24
project: Gullinkambi
type: worklog
status: completed
title: Mac mini 16 관측 추가와 Antigravity 할당량 대시보드
tags:
  - worklog
  - gullinkambi
  - grafana
  - prometheus
  - orca
  - antigravity
  - macmini
  - alerting
---
# Mac mini 16 관측 추가와 Antigravity 할당량 대시보드

ORCA에 Antigravity 사용량이 안 들어온다는 문제에서 출발했다. 원인은 Orca 원격 환경 "Macmini-16"에서 실행된 에이전트였다. 이 문제를 고치면서 Mac mini 16 시스템·Docker 관측을 추가했고, AI 구독 탭에 Antigravity 할당량과 429 거부 표시를 넣었다. 작업 전에 Gullinkambi를 ponytail 방식으로 정리했다.

## 결과
- 정리: 배포되지 않던 사본(`source/*`)과 참고 SQL을 삭제하고, dashboard provider yml 3개를 `dashboards.yml` 하나로 합쳤다. Jenkinsfile은 alerting이나 `provisioning/dashboards/*.yml`이 바뀌면 Grafana를 재시작한다(provider yml은 시작할 때만 읽힘).
- ORCA: Mac mini 16의 Claude·Codex·Antigravity 사용량이 수집된다. 10/11부터 소급 반영했다.
- Nest-Control-Room 탭: NPM / NAS Docker / Mac mini 32 Docker / **Mac mini 16 Docker** / NAS 시스템 / Mac mini 32 시스템 / **Mac mini 16 시스템** / 로그.
- AI 구독 탭에 다음을 추가했다.
  - `Antigravity Argon · 주간`
  - 출처별 Antigravity 토큰(Hermes researcher / Orca Mac mini 32 / Orca Mac mini 16)
  - 429 거부 횟수, 마지막 거부 시각
  - 초기화 패널에 Argon 주간 초기화
- 알림 `gk_ai_antigravity_rejected` 추가: 10분 안에 429 거부가 1건이라도 있으면 Discord로 보낸다. 주간 50/70/85/95% 알림은 Argon에도 자동으로 적용된다.

## 원인과 조치
### ORCA에 Antigravity가 안 보임
- 처음에는 Orca JSON이 오래돼서라고 잘못 진단했다(미push 커밋 되돌림). **교훈: DB의 일별 count부터 raw 로그와 비교할 것.**
- 실제 원인: 해당 작업이 Orca 원격 환경 **Macmini-16**(ssh `Macmini-16` → `dove-mini-16`, Tailscale)에서 돌아서 Mac mini 32 수집기가 볼 수 없었다.
- Mac mini 16에 ORCA 전용 수집기를 따로 띄웠다.
  - 컨테이너 `orca-telemetry`, compose는 Birds-Nest `hermes-telemetry/compose.macmini16.yml`
  - `collector_id=macmini-16`, namespace `orca-mac16`, worktree root `/Users/kimdove/orca`
  - Antigravity 집계 LaunchAgent `com.gullinkambi.antigravity-orca-usage`(시스템 python3 3.9)
  - 이미지는 `docker save | ssh docker load`로 복사한다. **hermes-telemetry 코드를 바꾸면 Mac mini 16에도 이미지와 스크립트를 다시 복사해야 한다.**
- 프로젝트 키(cwd)가 `/Users/kimdove/orca/...`와 `/Volumes/...`로 달라서 두 호스트 데이터가 충돌하지 않는다.
- 오늘(10/24) "빠진" Antigravity 작업은 수집 문제가 아니었다. **Argon 할당량 소진으로 429 거부**가 난 것이었다. Mac mini 32의 10/20·21·22·24 작업도 모두 거부됐다.
- Gemini 3.8 Flash를 쓰는 Hermes researcher(provider `antigravity-subscription-directsdk`)는 ORCA가 아니라 Hermes 테이블에 들어간다. 같은 Antigravity 할당량을 쓰므로 출처별 패널에서 함께 보여 준다.

### Mac mini 16 시스템·Docker
- Mac mini 16에 설치: node_exporter(brew services), macmon(:9091, `com.macmon`), macos-memory-exporter(:9092).
- Mac mini 32 Prometheus가 기존 `macmini_*` job에서 `dove-mini-16:{9100,9091,9092}`를 `instance: macmini-16`으로 수집한다.
- NAS Prometheus federation이 모든 instance를 `macmini`로 덮어쓰고 있었다. 이제 `macmini-16`은 유지한다(NAS에서 직접 수정, 백업 `.bak-20261024`).
- 기존 Mac mini 패널은 `instance="macmini"`로 고정했다. macmon 패널은 두 호스트 값이 섞이던 것을 고쳤다. `macmini_instance` 변수는 삭제했다. **Mac mini 쿼리는 job만으로 필터하지 말고 반드시 instance를 지정해야 한다.**
- 온도 알림을 `max by (instance)`로 바꿔 요약에 호스트 이름이 나오게 했다.
- cAdvisor: OrbStack에서는 컨테이너 ID가 이름으로 나온다. `--containerd-namespace=none`(실제 containerd 소켓 사용)을 주면 docker factory가 실제 이름을 찾는다. Mac mini 16은 `macmini16-cadvisor`(:9093, job `macmini16_cadvisor`)를 쓴다.

### Antigravity 할당량
- `agy -p /usage`에는 일반 Gemini와 별개로 **Gemini 4 Argon 주간 할당량**(`gemini-argon-wtu-weekly`)이 있다.
- exporter가 둘을 같은 `gemini` pool로 묶어서 Argon 값이 Gemini 주간 값을 덮어썼다. 그래서 Gemini 주간이 0%로 보였고(실제 3.8%), Argon 소진은 어디에도 나오지 않았다.
- `pool="argon"`을 분리했다. Argon이 응답에 있을 때만 내보낸다.
- 429 카운터 `ai_subscription_rejections_total`, `ai_subscription_last_rejection_timestamp_seconds`:
  - `~/.gemini/antigravity-cli/log`에서 `agent executor error` + `RESOURCE_EXHAUSTED` 줄을 센다.
  - 첫 스캔에서는 기준 offset만 잡고, 그 뒤에 새로 생긴 줄만 센다.

### Claude 5시간 패널 공백 (10/25 추가)
- 키체인에 `Claude Code-credentials` 항목이 여러 개 있다. exporter가 계정을 지정하지 않고 읽어서 10/8에 만료된 항목을 가져왔다. 그 뒤로 사용량 API는 한 번도 쓰이지 않았고 상태줄 캐시로만 동작했다.
- 상태줄 캐시는 Claude 세션 사이에 5시간 값이 빠질 수 있다. 그래서 "초기화됨 · 갱신 대기"가 나왔고, 주간 값도 낮게 보였다(8% vs 실제 10%).
- `security find-generic-password -a <현재 사용자>`로 Claude Code가 실제로 쓰는 `kimdove` 항목을 읽게 고쳤다(Birds-Nest `f69bf30`).

## 배포
| 대상 | 커밋 / 방법 |
|---|---|
| Gullinkambi `dev`·`main` | `53af215`(정리), `7cb9bc2`·`6ef3624`(Mac mini 16 시스템), `fb59f6f`(Mac mini 16 Docker), `3409e33`(AI 구독·429 알림) |
| Birds-Nest `dev-codex` | `2b4aa7a`(Mac mini 16 ORCA 수집기), `bcfec7f`(Mac mini 16 exporter 수집), `75dc0f6`(cAdvisor), `ab62a40`(Argon pool·429 카운터) |
| Birds-Nest `dev-nas` | `fab607c`(federation instance 유지) |
| exporter | LaunchAgent `com.gullinkambi.ai-subscription-exporter` 재시작(`launchctl kickstart -k`) |
| NAS Grafana | Jenkins `Gullinkambi-NAS-Deploy`가 `main`을 반영(alert 변경으로 재시작) |

## 알아 둘 점
- "ORCA 사용량 누락"이 보이면 먼저 어느 호스트에서 실행됐는지 확인한다: `orca search ... --environment Macmini-16 --agent antigravity`.
- 429 집계는 Mac mini 32의 agy 로그만 보고, exporter 시작 이후 거부만 센다. 오늘 13:21 거부는 숫자에 없다. 가짜 로그로 테스트하면 실제 Discord 알림이 가므로 단위 테스트로만 검증했다.
- Hermes 사용량은 샘플 사이 증가분으로 계산한다. 그래서 수집을 켜기 전(10/21)에 있던 세션은 빠진다.
- exporter가 매분 `agy -p /usage`를 실행하면서 Antigravity 로그 폴더에 파일이 약 6,835개(168MB) 쌓였다.
- Mac mini 16 SSH: 호스트 키는 신뢰된 IP 항목과 일치하는지 확인한 뒤 추가했다. 공개키는 사용자가 직접 등록했다.

## 남은 일
- Antigravity 로그 누적(`agy /usage` probe) 정리 방법 결정.
- Hermes researcher Antigravity 사용량을 ORCA 탭에도 합칠지 결정.
- Mac mini 32 cAdvisor도 `--containerd-namespace=none`으로 바꿀지 결정. 그러면 이미지→이름 매핑을 없앨 수 있지만, 대시보드·알림에 쓰는 이름이 바뀌는지 먼저 확인해야 한다.
- 다음 대시보드 후보: 수집 상태(collector health) 대시보드.

## 관련
- [[Work/Gullinkambi/작업기록/2026-10-22-Mac-mini-본체-지표-전환과-앱별-메모리|Mac mini 본체 지표 전환과 앱별 메모리]]
- [[Work/Gullinkambi/작업기록/2026-10-08-Antigravity-구독-사용량-수집-복구|Antigravity 구독 사용량 수집 복구]]
- [[Work/Gullinkambi/작업기록/2026-10-10-ORCA-호출별-관측-구현과-운영-반영|ORCA 호출별 관측 구현과 운영 반영]]
- [[Work/Gullinkambi/Gullinkambi 작업 백로그|작업 백로그]]
