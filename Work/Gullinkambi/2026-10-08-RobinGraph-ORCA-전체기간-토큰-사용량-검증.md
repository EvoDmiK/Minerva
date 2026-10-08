---
title: RobinGraph ORCA 전체 보존 기간 토큰 사용량 검증
date: 2026-10-08
tags: [orca, grafana, token-usage, robingraph, verification]
---

# RobinGraph ORCA 전체 보존 기간 토큰 사용량 검증

## 결론

Grafana의 `project_label = RobinGraph` 전체 보존 기간 **2026-09-05~2026-10-06** 합계는 **1,439,637,032토큰 (약 14.40억)**이다. 모델 호출 **12,165회**, 에이전트·쓰레드 조합 **134개**.

|에이전트|Grafana 총 토큰|모델 호출|쓰레드|
|---|---:|---:|---:|
|Codex|1,217,062,287|10,399|103|
|Claude|214,348,726|1,388|30|
|Antigravity|8,226,019|378|1|
|합계|1,439,637,032|12,165|134|

## 캐시와 집계 의미

Codex 캐시 읽기 1,184,624,256토큰은 입력에 포함된다. Claude 캐시 읽기 208,174,211토큰도 총 토큰에 포함된다. 반면 이번 Antigravity 4행에서는 총 토큰이 입력+출력이고 캐시 읽기 40,427,379가 별도다. 따라서 모든 제공자에 `total - cache_read`를 무조건 적용하면 Antigravity에서 음수가 되어 잘못된 계산이 된다.

제공자 구조를 반영해 **캐시 읽기를 제외한 입력·캐시 쓰기·출력**을 계산하면:

- Codex: 1,217,062,287 - 1,184,624,256 = **32,438,031**
- Claude: 214,348,726 - 208,174,211 = **6,174,515**
- Antigravity: 캐시 읽기가 총량에 포함되지 않으므로 **8,226,019** 그대로
- 합계: **46,838,565토큰 (약 4,684만)**

참고로 Antigravity 별도 캐시 읽기까지 포함한 처리 토큰 합계는 1,480,064,411이다. 사용자가 보는 Grafana `총 토큰` 합계 1,439,637,032와 구분한다. 비캐시 토큰량은 실제 비용이나 구독 한도 소진량이 아니다.

## 근거와 범위

- 조회 시각: 2026-10-08 18:47 KST
- Grafana MCP로 확인한 서비스 모니터링 대시보드 `dafsnnz67rw6ioc`, panel 46.
- 데이터소스 `Hermes Telemetry Ingest`, UID `ffskrzljzwr28b`, 테이블 `observability.orca_thread_usage_daily`.
- 같은 Grafana `/api/ds/query`에 인증된 읽기 전용 SELECT 실행. HTTP 200, 쿼리 오류 없음.
- 필터 `lower(project_label) = 'robingraph'`, 시간 필터 없음. 에이전트별 `sum(total_tokens)`, `sum(request_count)`, `count(DISTINCT thread_id)`와 전체 프로젝트 집계 교차 확인.
- RobinGraph 172행, event_id 중복 0건, collector_id 4개. 이는 event_id 중복 여부만 검사한 것으로 다른 ID를 가진 의미적 중복까지 완전히 배제한다는 주장은 아니다.
- Grafana 전체 데이터 최신일은 10-08, 마지막 관측 10-08 18:31:59 KST이나, RobinGraph로 식별된 데이터 최신일은 10-06.
- **ORCA의 실제 최초 사용부터 모두 보존되었다는 의미는 아니다.** 9월 5일 이전 누락 기록은 확인하지 않았으며 `kimdove`, `projects`, `orca` 등의 다른 프로젝트 라벨 행은 RobinGraph에 임의 합산하지 않았다.

[Grafana 쓰레드별 사용량](https://monitoring.dove-nest.com/d/dafsnnz67rw6ioc?viewPanel=46&from=now-90d&to=now)
