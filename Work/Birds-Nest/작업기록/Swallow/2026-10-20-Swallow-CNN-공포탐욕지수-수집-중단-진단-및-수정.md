---
created: 2026-10-20
date: 2026-10-20
project: Birds-Nest
type: worklog
status: verified_pending_deploy
task_id: SW-008
tags:
  - worklog
  - birds-nest
  - swallow
---

# [SW-008] Swallow CNN 공포·탐욕 지수 수집 중단 진단 및 전용 수집기 구현

## 요약

Swallow 대시보드의 CNN 공포·탐욕 지수(`FEAR_GREED`) 수집 중단 원인을 진단하고, 공식 CNN 데이터비즈 API 단독 검증 및 전용 n8n 수집 워크플로우(`n8n/Swallow/fear-greed.json`, 6노드, `active: false`)와 수동 동기화 스크립트(`scripts/sync-macro-indicators.js`) 정합성 보완을 구현·검증했다.

진단 결과 운영 `[Stock] Swallow - Watchlist Prices` (`Kt26XhwQEO2SuRtt`, 24노드)는 `KOSPI`, `KOSDAQ`, `USDKRW`만 정상 수집하고 있었으며, CNN 전용 노드나 활성 워크플로우가 없어 `FEAR_GREED`가 `45`(`2026-10-10T09:58:43Z` / `18:58:43 KST`), 이력 2행에 멈춰 있었다. 또한 수동 스크립트는 CNN 실패 시 암호화폐 공탐지수(`Alternative.me`)를 `FEAR_GREED` 코드와 `source='cnn'`으로 잘못 저장하는 폴백(SW-008)과 하드코딩된 DB 비밀번호 기본값(SW-003)을 포함하고 있었다.

이를 해결하기 위해 암호화폐 대체 폴백과 하드코딩 비밀번호 기본값을 제거하고(`PGPASSWORD` 또는 `SWALLOW_PGPASSWORD` 필수), 브라우저 전체 헤더를 사용한 공식 CNN API 호출, 0~100 점수·5종 등급·RFC3339 타임스탬프(96시간 이내·미래 10분 이내) 검증, 원천 시각(`providerTs`) 보존, 단일 CTE(워크플로우) 및 지표별 트랜잭션(스크립트) Upsert와 과거 replay 보호를 구현했다. 통합 검증(`66 passed, 0 failed, 1 skipped`, 격리 PG 멱등 검증 및 `n8n-test` 18160 실측 성공)을 완료했으며, **운영 n8n 등록·활성화·운영 DB 적재·Grafana 대시보드 새 값 확인은 아직 수행하지 않은 별도 요청 대기 상태**다.

## 작업 및 변경 결과 요약

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **원인 규명 / 요구사항** | CNN 공탐지수 수집 중단 진단 및 오염 방지 (SW-008, SW-003) | 운영 24노드 시세 워크플로우에 CNN 수집 경로 부재(자동 호출 없음, DB `45` / `2026-10-10 18:58:43 KST` 정체). 짧은 헤더 요청 시 CNN `418` 차단 발생. 수동 스크립트의 `Alternative.me`(암호화폐 지수) `source='cnn'` 오적재 폴백 및 비밀번호 기본값 하드코딩 확인 |
| **설계 및 해결 방안** | 공식 CNN 단독 수집·원천 시각 보존·전용 비활성 워크플로우 분리 | 기존 관심종목(`watchlist-prices.json`)·뉴스(`workflows.json`) 무변경. 매일 `08:30` `Asia/Seoul` + 수동 실행 6노드 전용 워크플로우(`active: false`) 분리. 브라우저 5종 헤더, 15s timeout / 3 tries, 엄격한 스키마·시각 검증, `providerTs` 보존 및 `updated_at <= EXCLUDED.updated_at` replay 보호 |
| **코드 / 설정 수정** | 워크플로우 신설, 스크립트 보안/정합성 수정, 계약 테스트 추가, 문서 갱신 | `n8n/Swallow/fear-greed.json` (6노드), `scripts/sync-macro-indicators.js` (`Alternative.me` 폴백·비밀번호 기본값 제거, 지표별 트랜잭션), `n8n/Swallow/tests/fear-greed.test.mjs`, Swallow README 3종 |
| **실서비스 배포** | **운영 미배포 (별도 요청 대기)** | 운영 n8n 워크플로우 등록·활성화, 운영 DB 적재, Grafana 새 값 반영 모두 미수행. 운영 DB는 기존 `45` (`2026-10-10 18:58:43 KST`) 유지 |
| **검증 및 테스트** | 단위·계약·격리 PG SQL 66 pass (`CNN_LIVE` 포함 시 67 pass) 및 `n8n-test` 실행 18160 성공 | `FNG_TEST_PG_CONTAINER=swallow-cnn-review-pg node --test n8n/Swallow/tests/*.test.mjs` 66 pass / 0 fail / 1 skip. 격리 PG에서 최초 적재·재실행·과거 replay·0값·타 지표 보존 확인. `n8n-test` 2.15.0 임시 read-only 실행 `18160` success (`score=23`, `extreme_fear`, `providerTs=2026-10-20T00:00:00.000Z`) |
| **형상 관리** | `dev-claude` → `dev-codex` 통합 후 `dev-docs` 문서 반영 | 백엔드 `84c645737d75be440e7446926356b8d5f9082100`, 통합 `b9c7440b81223c9b45ab8ad61e1a166d54d28bca`, `dev-docs` 문서 커밋·푸시 |

---

## 1. 작업 배경 및 문제 분석

### 발생 현상 / 요구사항
* Swallow 모니터링 대시보드의 공포 & 탐욕 지수(`FEAR_GREED`)가 `45`(`fear`)에서 더 이상 갱신되지 않는 현상이 보고됨.
* 기존 관심종목 및 뉴스 파이프라인에 영향을 주지 않으면서 수집 중단 원인을 정확히 규명하고, CNN 미국 증시 공포·탐욕 지수를 신뢰성 있게 수집하도록 수정할 것이 요구됨.

### 원인 분석 / 설계 검토
* **운영 워크플로우 및 DB 상태 확인**:
  * 운영 `[Stock] Swallow - Watchlist Prices` (`Kt26XhwQEO2SuRtt`, 24노드)는 `KOSPI`, `KOSDAQ`, `USDKRW` 3개 거시 지표와 관심종목 시세만 정상 수집 중이었으며, CNN 전용 노드나 활성화된 CNN 수집 워크플로우가 존재하지 않았다.
  * 저장소 내 `scripts/sync-macro-indicators.js`는 수동 실행 스크립트일 뿐 스케줄러나 워크플로우에서 자동 호출되지 않았다.
  * 운영 DB 확인 결과 `public.market_macro_indicators`의 `FEAR_GREED` 행은 `current_value = 45`, `status = 'fear'`, `updated_at = 2026-10-10T09:58:43Z` (`18:58:43 KST`)에 멈춰 있었고, `public.stock_price_history`의 `ticker = 'FEAR_GREED'` 이력은 2행뿐이었다.
* **CNN API 418 봇 차단 및 헤더 조건 규명**:
  * CNN 공식 엔드포인트(`https://production.dataviz.cnn.io/index/fearandgreed/graphdata`)는 기본/축약 헤더 요청에 대해 HTTP `418`로 봇 차단 응답을 반환함을 확인했다.
  * 반면 전체 브라우저 `User-Agent`, `Accept: application/json, text/plain, */*`, `Accept-Language: en-US,en;q=0.9`, `Origin: https://edition.cnn.com`, `Referer: https://edition.cnn.com/markets/fear-and-greed` 헤더를 모두 포함하면 공식 API가 정상 HTTP `200` (실측 `score: 22.9928571428571`, `rating: "extreme fear"`, `timestamp: "2026-10-20T00:00:00+00:00"`)을 반환함을 확인했다.
* **잘못된 Fallback (SW-008) 및 하드코딩 자격증명 기본값 (SW-003)**:
  * 기존 `scripts/sync-macro-indicators.js`는 CNN 호출 실패 시 `https://api.alternative.me/fng/?limit=1` (암호화폐 공포·탐욕 지수)을 호출해 동일한 `code = 'FEAR_GREED'` 및 `source = 'cnn'`으로 DB에 저장하는 잘못된 fallback을 가지고 있었다.
  * 또한 DB 연결 설정에 비밀번호 문자열 기본값이 하드코딩되어 있었고, 적재 시 원천 시각이 아닌 실행 시각(`NOW()`)을 사용해 재실행 시 이력 중복 및 과거 데이터 역전 가능성이 있었다.

---

## 2. 해결 방안 및 설계

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

---

## 3. 주요 구현 내용

### 수정 및 추가 파일 목록
* `n8n/Swallow/fear-greed.json` — `[Stock] Swallow - CNN Fear & Greed` 전용 6노드 워크플로우 신설 (`active: false`, `Asia/Seoul`, 수동 + 매일 `08:30`, 15s timeout / 3 tries, 단일 CTE Upsert)
* `scripts/sync-macro-indicators.js` — `Alternative.me` 폴백 및 비밀번호 하드코딩 기본값 제거, `CNN_HEADERS`·`parseCnnFearGreed`·`fetchCnnFearGreed` export, 15s timeout, 원천 시각 보존 및 지표별 트랜잭션 적용
* `n8n/Swallow/tests/fear-greed.test.mjs` — 워크플로우 Code 노드와 스크립트 파서 동시 계약 테스트, 콜론 미포함 검증, 격리 PostgreSQL 컨테이너 SQL 멱등성·replay·경계값 테스트
* `n8n/Swallow/README.md` — 워크플로우 구성 표 및 섹션 8(CNN 공탐지수 전용 파이프라인 진단·설계·검증·미배포 상태) 추가
* `mcp/swallow-mcp/README.md` — `Alternative.me` 폴백 설명 제거, `PGPASSWORD`/`SWALLOW_PGPASSWORD` 필수 안내 및 전용 워크플로우(미배포 대기) 명시
* `grafana/swallow/README.md` — Panel ID 105 및 수집기 섹션에 전용 워크플로우/스크립트 변경 사항과 운영 미배포 상태(`45` 유지) 반영

### 핵심 코드 / 설정 스니펫
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

---

## 4. 검증 및 테스트 결과

### 자동화 테스트 (단위 / 회귀 / 격리 PG SQL)
* 실행 명령어 (root 통합 검증):
  ```bash
  FNG_TEST_PG_CONTAINER=swallow-cnn-review-pg node --test n8n/Swallow/tests/*.test.mjs
  ```
* 결과: **총 67개 중 `66 passed, 0 failed, 1 skipped`** (`CNN_LIVE` 미설정으로 라이브 단건 스킵; 구현 담당 `dev-claude`에서는 `CNN_LIVE=1` 활성화 포함 **67 passed** 확인).
* 격리 실제 PostgreSQL(`swallow-cnn-review-pg`) SQL 검증 항목:
  1. 기존 운영 형태 구 데이터(`45`, `2026-10-10T09:58:43Z`) 및 타 지표(`KOSPI = 2500`) 초기 상태에서 신규 값(`23`, `2026-10-20T00:00:00Z`) 최초 적재 성공 (`latest: 0 inserted, 1 updated`, `history: 1 inserted, 0 updated`).
  2. 동일 원천 시각(`2026-10-20T00:00:00Z`) 재실행 시 이력 행이 늘어나지 않고 1행 유지 (`history: 0 inserted, 1 updated`).
  3. 과거 원천 시각(`2026-10-13T00:00:00Z`, 값 `44`) replay 시 이력만 추가되고 최신값(`23`, `2026-10-20T00:00:00Z`)은 덮어쓰지 않고 보존 (`latest: 0 inserted, 0 updated`, `keptNewer = 1`).
  4. 경계값 `0`(`2026-10-21T00:00:00Z`) 정상 적재 확인.
  5. `FEAR_GREED` 외 코드(`KOSPI`) 입력 시 무시되어 기존 `KOSPI = 2500` 값 무결성 보존 확인.

### 개발 런타임(`n8n-test`) 검증 증거
* 실제 대상 환경: `n8n-test` (`2.15.0`)
* 검증 시나리오 및 결과:
  1. 임시 read-only 워크플로우(`Manual Trigger` → 공식 CNN HTTP → `CNN 검증 및 적재 준비` Code 노드) 실행 `18160` (`2026-10-20T04:41:33Z`): `status: success` (HTTP 60ms + Code 340ms), `current_value: 23` (`rawScore: 22.9928571428571`), `status: "extreme_fear"`, `providerTs: "2026-10-20T00:00:00.000Z"` 반환 확인 후 임시 워크플로우 삭제 완료 (최종 통합본에 대한 추가 재확인은 root에서 진행 예정).
  2. *실패 구분 기록*: 첫 CLI 실행 `18159`는 외부 task runner 미연결로 인한 대기 종료였으며 워크플로우/코드 실패가 아님을 구분 확인함.
  3. `graphify update .` AST 갱신은 root에서 정상 수행 완료.

---

## 5. 배포 및 형상 관리

* **대상 환경**: 개발 검증 완료 (`n8n-test` 및 격리 PostgreSQL). **NAS 운영 n8n 배포·활성화 및 운영 DB 적재는 미수행(별도 요청 대기)**.
* **Git 브랜치**: `dev-claude` → `dev-codex` → `dev-docs`
* **커밋 해시**:
  * 백엔드 구현 (`dev-claude`): `84c645737d75be440e7446926356b8d5f9082100` (`fix(swallow): collect CNN Fear & Greed from official source only`)
  * 코드 통합 (`dev-codex`): `b9c7440b81223c9b45ab8ad61e1a166d54d28bca` (`merge: restore CNN Fear and Greed collection with validated source data`)
* **원격 반영**: `origin/dev-docs` 문서 커밋 및 푸시 완료

---

## 6. 한계 및 후속 과제

* **운영 환경 미배포 / 미실행 항목**:
  * 운영 n8n 인스턴스에 `[Stock] Swallow - CNN Fear & Greed` (`n8n/Swallow/fear-greed.json`) 워크플로우 등록 및 활성화(`active: true`)는 아직 수행하지 않았다.
  * 운영 PostgreSQL DB에 새로운 `FEAR_GREED` 값을 적재하거나 Grafana 대시보드(`swallow-stock-monitor` Panel ID 105)에서 갱신된 값을 확인하는 작업도 별도 배포 승인 후 수행한다 (현재 운영 DB 값은 `45`, `2026-10-10 18:58:43 KST` 그대로 유지).
  * `scripts/sync-macro-indicators.js`의 전체 DB 적재 경로를 직접 실행하는 엔드투엔드 테스트는 운영 DB 보호를 위해 아직 실행하지 않았다.
* **백로그 연결**:
  * [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그#SW-008 — CNN·비트코인 공포탐욕 지수 분리|SW-008 — CNN·비트코인 공포탐욕 지수 분리]]
  * [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그#SW-003 — 매크로 수집기의 하드코딩 자격증명 제거|SW-003 — 매크로 수집기의 하드코딩 자격증명 제거]]

---

## 관련 문서

- [[Home|🏠 홈으로]]
- [[Work/Birds-Nest/index|Birds-Nest 프로젝트 인덱스]]
- [[Work/Birds-Nest/작업기록/Swallow/index|Swallow 작업 문서 목록]]
- [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그|Swallow 작업 백로그]]
