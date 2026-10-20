---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Swallow/2026-10-20-Swallow-CNN-공포탐욕지수-수집-중단-진단-및-수정]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# [SW-008] Swallow CNN 공포·탐욕 지수 수집 중단 진단 및 전용 수집기 구현

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Swallow/2026-10-20-Swallow-CNN-공포탐욕지수-수집-중단-진단-및-수정]] · 분류 근거 {"인프라":2,"자동화":29,"관측성":4,"데이터":4}

## 1. 개요 및 목적

Swallow 대시보드의 CNN 공포·탐욕 지수(`FEAR_GREED`) 수집 중단 원인을 진단하고, 공식 CNN 데이터비즈 API 단독 검증 및 전용 n8n 수집 워크플로우(`n8n/Swallow/fear-greed.json`, 6노드, `active: false`)와 수동 동기화 스크립트(`scripts/sync-macro-indicators.js`) 정합성 보완을 구현·검증했다.

진단 결과 운영 `[Stock] Swallow - Watchlist Prices` (`Kt26XhwQEO2SuRtt`, 24노드)는 `KOSPI`, `KOSDAQ`, `USDKRW`만 정상 수집하고 있었으며, CNN 전용 노드나 활성 워크플로우가 없어 `FEAR_GREED`가 `45`(`2026-10-10T09:58:43Z` / `18:58:43 KST`), 이력 2행에 멈춰 있었다. 또한 수동 스크립트는 CNN 실패 시 암호화폐 공탐지수(`Alternative.me`)를 `FEAR_GREED` 코드와 `source='cnn'`으로 잘못 저장하는 폴백(SW-008)과 하드코딩된 DB 비밀번호 기본값(SW-003)을 포함하고 있었다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 발생 현상 / 요구사항
- 원인 분석 / 설계 검토
- 2. 해결 방안 및 설계
- 3. 주요 구현 내용
- 수정 및 추가 파일 목록
- 핵심 코드 / 설정 스니펫
- 4. 검증 및 테스트 결과
- 자동화 테스트 (단위 / 회귀 / 격리 PG SQL)
- 개발 런타임(`n8n-test`) 검증 증거
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```sql
-- n8n/Swallow/fear-greed.json (공탐지수 적재 노드 단일 CTE)
WITH input AS (
  SELECT *
  FROM jsonb_to_recordset($1::jsonb) AS r(code text, name text, current_value numeric, status text)
  WHERE code = 'FEAR_GREED'
), latest AS (
  INSERT INTO public.market_macro_indicators (code, name, current_value, change_amt, change_rate, status, updated_at)
  SELECT code, name, current_value, NULL, NULL, status, $2::timestamptz FROM input
  ON CONFLICT (code) DO UPDATE
  SET name = EXCLUDED.name,
      current_value = EXCLUDED.current_value,
      change_amt = EXCLUDED.change_amt,
      change_rate = EXCLUDED.change_rate,
      status = EXCLUDED.status,
      updated_at = EXCLUDED.updated_at
  WHERE market_macro_indicators.updated_at <= EXCLUDED.updated_at
  RETURNING (xmax = 0) AS inserted
), history AS (
  INSERT INTO public.stock_price_history (ticker, ts, source, close_price, change_amt, change_rate)
  SELECT code, $2::timestamptz, 'cnn', current_value, NULL, NULL FROM input
  ON CONFLICT (ticker, ts, source) DO UPDATE
  SET close_price = EXCLUDED.close_price
  RETURNING (xmax = 0) AS inserted
)
SELECT 'latest' AS target,
       count(*) FILTER (WHERE inserted) AS inserted,
       count(*) FILTER (WHERE NOT inserted) AS updated
FROM latest
UNION ALL
SELECT 'history', count(*) FILTER (WHERE inserted), count(*) FILTER (WHERE NOT inserted)
FROM history;
```

  ```bash
  FNG_TEST_PG_CONTAINER=swallow-cnn-review-pg node --test n8n/Swallow/tests/*.test.mjs
  ```

## 4. 검증 근거 및 트러블슈팅

Swallow 대시보드의 CNN 공포·탐욕 지수(`FEAR_GREED`) 수집 중단 원인을 진단하고, 공식 CNN 데이터비즈 API 단독 검증 및 전용 n8n 수집 워크플로우(`n8n/Swallow/fear-greed.json`, 6노드, `active: false`)와 수동 동기화 스크립트(`scripts/sync-macro-indicators.js`) 정합성 보완을 구현·검증했다.

진단 결과 운영 `[Stock] Swallow - Watchlist Prices` (`Kt26XhwQEO2SuRtt`, 24노드)는 `KOSPI`, `KOSDAQ`, `USDKRW`만 정상 수집하고 있었으며, CNN 전용 노드나 활성 워크플로우가 없어 `FEAR_GREED`가 `45`(`2026-10-10T09:58:43Z` / `18:58:43 KST`), 이력 2행에 멈춰 있었다. 또한 수동 스크립트는 CNN 실패 시 암호화폐 공탐지수(`Alternative.me`)를 `FEAR_GREED` 코드와 `source='cnn'`으로 잘못 저장하는 폴백(SW-008)과 하드코딩된 DB 비밀번호 기본값(SW-003)을 포함하고 있었다.

이를 해결하기 위해 암호화폐 대체 폴백과 하드코딩 비밀번호 기본값을 제거하고(`PGPASSWORD` 또는 `SWALLOW_PGPASSWORD` 필수), 브라우저 전체 헤더를 사용한 공식 CNN API 호출, 0~100 점수·5종 등급·RFC3339 타임스탬프(96시간 이내·미래 10분 이내) 검증, 원천 시각(`providerTs`) 보존, 단일 CTE(워크플로우) 및 지표별 트랜잭션(스크립트) Upsert와 과거 replay 보호를 구현했다. 통합 검증(`66 passed, 0 failed, 1 skipped`, 격리 PG 멱등 검증 및 `n8n-test` 18160 실측 성공)을 완료했으며, **운영 n8n 등록·활성화·운영 DB 적재·Grafana 대시보드 새 값 확인은 아직 수행하지 않은 별도 요청 대기 상태**다.

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **원인 규명 / 요구사항** | CNN 공탐지수 수집 중단 진단 및 오염 방지 (SW-008, SW-003) | 운영 24노드 시세 워크플로우에 CNN 수집 경로 부재(자동 호출 없음, DB `45` / `2026-10-10 18:58:43 KST` 정체). 짧은 헤더 요청 시 CNN `418` 차단 발생. 수동 스크립트의 `Alternative.me`(암호화폐 지수) `source='cnn'` 오적재 폴백 및 비밀번호 기본값 하드코딩 확인 |
| **설계 및 해결 방안** | 공식 CNN 단독 수집·원천 시각 보존·전용 비활성 워크플로우 분리 | 기존 관심종목(`watchlist-prices.json`)·뉴스(`workflows.json`) 무변경. 매일 `08:30` `Asia/Seoul` + 수동 실행 6노드 전용 워크플로우(`active: false`) 분리. 브라우저 5종 헤더, 15s timeout / 3 tries, 엄격한 스키마·시각 검증, `providerTs` 보존 및 `updated_at <= EXCLUDED.updated_at` replay 보호 |
| **코드 / 설정 수정** | 워크플로우 신설, 스크립트 보안/정합성 수정, 계약 테스트 추가, 문서 갱신 | `n8n/Swallow/fear-greed.json` (6노드), `scripts/sync-macro-indicators.js` (`Alternative.me` 폴백·비밀번호 기본값 제거, 지표별 트랜잭션), `n8n/Swallow/tests/fear-greed.test.mjs`, Swallow README 3종 |
| **실서비스 배포** | **운영 미배포 (별도 요청 대기)** | 운영 n8n 워크플로우 등록·활성화, 운영 DB 적재, Grafana 새 값 반영 모두 미수행. 운영 DB는 기존 `45` (`2026-10-10 18:58:43 KST`) 유지 |
| **검증 및 테스트** | 단위·계약·격리 PG SQL 66 pass (`CNN_LIVE` 포함 시 67 pass) 및 `n8n-test` 실행 18160 성공 | `FNG_TEST_PG_CONTAINER=swallow-cnn-review-pg node --test n8n/Swallow/tests/*.test.mjs` 66 pass / 0 fail / 1 skip. 격리 PG에서 최초 적재·재실행·과거 replay·0값·타 지표 보존 확인. `n8n-test` 2.15.0 임시 read-only 실행 `18160` success (`score=23`, `extreme_fear`, `providerTs=2026-10-20T00:00:00.000Z`) |
| **형상 관리** | `dev-claude` → `dev-codex` 통합 후 `dev-docs` 문서 반영 | 백엔드 `84c645737d75be440e7446926356b8d5f9082100`, 통합 `b9c7440b81223c9b45ab8ad61e1a166d54d28bca`, `dev-docs` 문서 커밋·푸시 |

* **전용 비활성 워크플로우 분리 (`n8n/Swallow/fear-greed.json`, 6노드)**:
  * 기존 1분/5분 시세 수집기(`watchlist-prices.json`)와 뉴스 워크플로우(`workflows.json`)는 전혀 건드리지 않고, 미국 거래일 기준 하루 1회 갱신되는 CNN 지수 특성에 맞춰 매일 `08:30` (`30 8 * * *`, `Asia/Seoul`) 및 수동 실행 트리거를 가진 독립 워크플로우로 설계했다.
  * 운영 배포 승인 전까지 안전하게 관리하기 위해 `active: false` 상태로 커밋한다.
  * *참고*: 작업 지시 요약에 7노드로 언급된 바 있으나, 실제 `n8n/Swallow/fear-greed.json` 구현은 수동 트리거·스케줄 트리거·HTTP 조회·검증 및 적재 준비·Postgres 적재·적재 확인의 **총 6개 노드**로 구성되어 있다.
* **단일 공식 원천 강제 및 엄격한 유효성 검증**:
  * `Alternative.me` 폴백을 완전히 제거하고 CNN `fear_and_greed` 응답만 허용한다. 실패 시 예외를 발생시켜 기존 DB 값을 오염시키지 않고 보존한다.
  * `score`: 유한 숫자 또는 비어 있지 않은 숫자 문자열(`0 <= score <= 100`)만 허용하고 반올림 정수로 저장한다(`Number(' ')`, `Number([])`, `false` 등이 `0`으로 변환되는 현상 차단).
  * `rating`: `extreme fear`, `fear`, `neutral`, `greed`, `extreme greed` 5종만 허용하고 공백을 `_`로 치환(`extreme_fear` 등)한다.
  * `timestamp`: 타임존이 포함된 RFC3339 문자열만 허용하며, 미래 10분 초과(`> now + 10m`) 또는 과거 96시간 초과(`now - ts > 96h`, 미국 주말 ~72h 및 월요일 휴장 ~96h 고려) 시 거부한다.
  * n8n runner가 에러 메시지를 콜론(`:`) 기준으로 절단하는 문제를 방지하기 위해 워크플로우 Code 노드의 모든 `throw new Error(...)` 메시지에서 콜론을 제거했다.
* **원천 시각(`providerTs`) 보존 및 원자적 Upsert / Replay 보호**:
  * 실행 시각(`NOW()`) 대신 CNN 응답의 원천 `timestamp`(`providerTs`)를 `market_macro_indicators.updated_at`과 `stock_price_history.ts`에 그대로 기록한다.
  * 동일 원천 시각 재실행 시 `(ticker, ts, source)` PK 기준 멱등 Update로 행이 중복 증가하지 않으며, `WHERE market_macro_indicators.updated_at <= EXCLUDED.updated_at` 조건으로 과거 시각 데이터 replay 시 최신 상태값을 덮어쓰지 않도록 보호한다.
* **스크립트 자격증명 환경변수 강제 및 트랜잭션 분리**:
  * `scripts/sync-macro-indicators.js`에서 하드코딩 비밀번호 기본값을 제거하고 `PGPASSWORD` 또는 `SWALLOW_PGPASSWORD` 환경변수가 없으면 연결 전에 즉시 에러를 발생시킨다(SW-003 해소).
  * 지표별로 `BEGIN ... COMMIT / ROLLBACK` 트랜잭션을 수행해 최신값 테이블과 시계열 이력 테이블 간 정합성을 보장한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Swallow/2026-10-20-Swallow-CNN-공포탐욕지수-수집-중단-진단-및-수정]]
- [[Dev/index|Dev 인덱스]]
