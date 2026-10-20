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

진단 결과 운영 `[Stock] Swallow - Watchlist Prices` (24노드)는 `KOSPI`, `KOSDAQ`, `USDKRW`만 정상 수집하고 있었으며, CNN 전용 노드나 활성 워크플로우가 없어 `FEAR_GREED`가 `45`(`2026-10-10T09:58:43Z` / `18:58:43 KST`), 이력 2행에 멈춰 있었다. 또한 수동 스크립트는 CNN 실패 시 암호화폐 공탐지수(`Alternative.me`)를 `FEAR_GREED` 코드와 `source='cnn'`으로 잘못 저장하는 폴백(SW-008)과 하드코딩된 DB 비밀번호 기본값(SW-003)을 포함하고 있었다.

이를 해결하기 위해 암호화폐 대체 폴백과 하드코딩 비밀번호 기본값을 제거하고(`PGPASSWORD` 또는 `SWALLOW_PGPASSWORD` 환경변수 필수), 브라우저 5종 헤더를 사용한 공식 CNN API 호출, 0~100 점수·5종 등급·RFC3339 타임스탬프(96시간 이내·미래 10분 이내) 동일 검증 규칙, 원천 시각(`providerTs`) 보존, 단일 CTE(워크플로우) 및 지표별 트랜잭션(스크립트) Upsert와 과거 replay 보호를 구현했다. 계약·격리 PG 테스트(`66 passed, 0 failed, 1 skipped`), `syncMacroIndicators()` 격리 DB E2E 검증, `n8n-test` 2.15.0 최종 JSON 실행 `18161` 성공을 모두 완료했으며, **운영 n8n 등록·활성화·운영 DB 적재·수동 스크립트 운영 실행·Grafana 새 값 확인은 아직 수행하지 않은 별도 요청 대기 상태**다.

## 작업 및 변경 결과 요약

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **원인 규명 / 요구사항** | CNN 공탐지수 수집 중단 진단 및 오염 방지 (SW-008, SW-003) | 운영 24노드 시세 워크플로우에 CNN 수집 경로 부재(자동 호출 없음, DB `45` / `2026-10-10 18:58:43 KST` 정체). 짧은 헤더 요청 시 CNN `418` 차단 발생. 수동 스크립트의 `Alternative.me`(암호화폐 지수) `source='cnn'` 오적재 폴백 및 비밀번호 기본값 하드코딩 확인 |
| **설계 및 해결 방안** | 공식 CNN 단독 수집·원천 시각 보존·전용 비활성 워크플로우 분리 | 기존 관심종목(`watchlist-prices.json`)·뉴스(`workflows.json`) 무변경. 매일 `08:30` `Asia/Seoul` + 수동 실행 6노드 전용 워크플로우(`active: false`) 분리. 브라우저 5종 헤더, 15s timeout / 3 tries, 워크플로우·스크립트 동일 검증 규칙 적용, `providerTs` 보존 및 `updated_at <= EXCLUDED.updated_at` replay 보호 |
| **코드 / 설정 수정** | 워크플로우 신설, 스크립트 보안/정합성 수정, 계약 테스트 추가, 문서 갱신 | `n8n/Swallow/fear-greed.json` (6노드), `scripts/sync-macro-indicators.js` (`Alternative.me` 폴백·비밀번호 기본값 제거, 지표별 트랜잭션), `n8n/Swallow/tests/fear-greed.test.mjs`, Swallow README 3종 |
| **실서비스 배포** | **운영 미배포 (별도 요청 대기)** | 운영 n8n 워크플로우 등록·활성화, 운영 DB 적재(write 0건 유지), 수동 스크립트 운영 실행, Grafana 새 값 반영 모두 미수행. 운영 DB는 기존 `45` (`2026-10-10 18:58:43 KST`) 유지 |
| **검증 및 테스트** | 단위·계약·격리 PG SQL 66 pass (`CNN_LIVE` 포함 67 pass), `syncMacroIndicators()` 격리 DB E2E PASS, `n8n-test` 최종 실행 18161 성공 | `FNG_TEST_PG_CONTAINER=swallow-cnn-review-pg node --test n8n/Swallow/tests/*.test.mjs` 66 pass / 0 fail / 1 skip. 일회용 PG에서 `syncMacroIndicators()` HTTP fixture 실행으로 적재·`providerTs` 보존·재실행 중복 없음·418 시 기존 보존+`exitCode=1`·트리거 오류 시 `ROLLBACK` PASS. `n8n-test` 2.15.0 최종 JSON read-only 실행 `18161` success (`score=23`, `extreme_fear`, `providerTs=2026-10-20T00:00:00.000Z`) |
| **형상 관리** | `dev-claude` → `dev-codex` 통합 후 `dev-docs` 문서 반영 | 백엔드 `84c645737d75be440e7446926356b8d5f9082100`, 통합 `b9c7440b81223c9b45ab8ad61e1a166d54d28bca` (graph 갱신 `b122d1c`), `dev-docs` 문서 커밋·푸시 |

---

## 1. 작업 배경 및 문제 분석

### 발생 현상 / 요구사항
* Swallow 모니터링 대시보드의 공포 & 탐욕 지수(`FEAR_GREED`)가 `45`(`fear`)에서 갱신되지 않는 원인을 진단하고, 기존 관심종목·뉴스 파이프라인을 변경하지 않으면서 공식 CNN 지수를 신뢰성 있게 수집하도록 수정.

### 원인 분석 / 설계 검토
* **자동 수집 경로 부재**: 운영 `[Stock] Swallow - Watchlist Prices` (24노드)는 `KOSPI`, `KOSDAQ`, `USDKRW`와 관심종목만 수집 중이었고 CNN 전용 노드나 활성 워크플로우가 없었다. 수동 스크립트(`scripts/sync-macro-indicators.js`)만 존재하고 자동 호출되지 않아 운영 DB `FEAR_GREED`는 `45` (`2026-10-10T09:58:43Z` / `18:58:43 KST`), `stock_price_history` 이력은 2행에 멈춰 있었다.
* **CNN API 418 차단 및 헤더 조건**: CNN 공식 엔드포인트(`https://production.dataviz.cnn.io/index/fearandgreed/graphdata`)는 짧은 헤더 요청에 HTTP `418` 봇 차단을 반환하며, 브라우저 전체 `User-Agent`, `Accept`, `Accept-Language`, `Origin: https://edition.cnn.com`, `Referer: https://edition.cnn.com/markets/fear-and-greed` 포함 시 정상 `200 OK`를 반환함을 확인했다.
* **잘못된 Fallback (SW-008) 및 하드코딩 비밀번호 기본값 (SW-003)**: 수동 스크립트는 CNN 실패 시 암호화폐 지수(`Alternative.me`)를 `FEAR_GREED` 및 `source='cnn'`으로 저장하는 잘못된 폴백과 DB 비밀번호 기본값 하드코딩을 포함하고 있었다.

---

## 2. 해결 방안 및 주요 구현 내용

* **`n8n/Swallow/fear-greed.json` (전용 6노드 워크플로우, `active: false`)**:
  * 수동 트리거 + 매일 `08:30` (`30 8 * * *`, `Asia/Seoul`) 스케줄 트리거 → 공식 CNN HTTP 조회(브라우저 5종 헤더, 15s timeout, 3 tries) → `CNN 검증 및 적재 준비` Code 노드(콜론 없는 오류 문구) → `공탐지수 적재` Postgres 노드(`데이터 DB` 자격증명 재사용, 단일 CTE로 `market_macro_indicators`·`stock_price_history` 원자적 Upsert 및 `updated_at <= EXCLUDED.updated_at` 과거 replay 보호) → `적재 확인` Code 노드.
* **`scripts/sync-macro-indicators.js` (수동 동기화 스크립트 정합성 및 보안)**:
  * `Alternative.me` 폴백 및 하드코딩 비밀번호 기본값 제거(`PGPASSWORD` 또는 `SWALLOW_PGPASSWORD` 환경변수 필수).
  * 워크플로우와 동일한 브라우저 헤더, 15s timeout, 동일 검증 규칙(`score` 0~100 숫자/비어 있지 않은 숫자 문자열, 5종 `rating`, 타임존 포함 RFC3339 `timestamp` 과거 96h·미래 10m 이내, 원천 시각 `providerTs` 보존)을 적용하고 지표별 `BEGIN ... COMMIT / ROLLBACK` 트랜잭션으로 묶음.
* **`n8n/Swallow/tests/fear-greed.test.mjs` 및 문서 3종 (`n8n/Swallow/README.md`, `mcp/swallow-mcp/README.md`, `grafana/swallow/README.md`)**:
  * 워크플로우 Code 노드와 스크립트 파서가 동일 입력에서 동일한 판정을 내리는지 계약 테스트로 검증하고, 격리 PostgreSQL SQL 멱등성·경계값 테스트 및 문서 반영 완료.

---

## 3. 검증 및 테스트 결과

### 자동화 계약 및 격리 PostgreSQL 검증
* **계약 및 SQL 멱등성 테스트**:
  * 명령어: `FNG_TEST_PG_CONTAINER=swallow-cnn-review-pg node --test n8n/Swallow/tests/*.test.mjs`
  * 결과: **총 67개 중 `66 passed, 0 failed, 1 skipped`** (`CNN_LIVE` 미설정 기본 스킵; `dev-claude`에서는 `CNN_LIVE=1` 포함 **67 passed**).
  * 격리 PostgreSQL(`swallow-cnn-review-pg`)에서 기존 `45`(`2026-10-10T09:58:43Z`) 상태 후 신규 `23`(`2026-10-20T00:00:00Z`) 최초 적재, 동일 원천 시각 재실행 시 이력 중복 없음, 과거 시각(`2026-10-13T00:00:00Z`) replay 시 최신값 보호(`keptNewer=1`), 경계값 `0` 적재, 타 지표(`KOSPI=2500`) 보존 전부 PASS.
* **스크립트 전체 DB 경로 격리 E2E 검증 (`syncMacroIndicators()`)**:
  * 별도 localhost 일회용 PostgreSQL에서 HTTP fixture와 함께 실제 `syncMacroIndicators()`를 실행하여 `latest`/`history` 적재, `providerTs` 보존, 동일 재실행 중복 없음, CNN HTTP `418` 응답 시 기존 `FEAR_GREED` 값 보존 및 `process.exitCode = 1` 설정, 이력 테이블 트리거 강제 오류 시 최신값까지 함께 `ROLLBACK`됨을 전부 검증 통과(실제 원천 HTTP 검증과 구분, 운영 DB write 0건 유지).

### `n8n-test` 실제 원천 HTTP 런타임 검증
* 대상 환경: `n8n-test` (`2.15.0`)
* 검증 결과:
  1. 초기 read-only 실행 `18160` (`2026-10-20T04:41:33Z`, HTTP 60ms + Code 340ms) 및 **최종 JSON 기준 read-only 실행 `18161`** (`2026-10-20T04:43:55.522Z~04:43:56.084Z` / `13:43 KST`, HTTP 72ms + Code 328ms) 모두 `status: success`: 실제 CNN 공식 API로부터 `current_value: 23` (`rawScore: 22.9928571428571`), `status: "extreme_fear"`, `providerTs: "2026-10-20T00:00:00.000Z"` 반환 확인.
  2. 첫 CLI 실행 `18159`는 외부 runner 미연결 대기 종료로 코드 결함과 구분했으며, 검증 완료 후 임시 실행(`18159`/`18160`/`18161`)과 임시 워크플로우를 모두 삭제 정리하고 호스트 로그 증거만 보관함.
  3. root에서 `graphify update .` AST 갱신 및 커밋(`b122d1c`) 완료.

---

## 4. 배포 현황 및 한계 (운영 미배포)

* **코드 통합**: 백엔드 `84c645737d75be440e7446926356b8d5f9082100` → 통합 `b9c7440b81223c9b45ab8ad61e1a166d54d28bca` (graph 갱신 `b122d1c`) → `dev-docs` 문서 반영 및 푸시.
* **운영 미배포 상태 (별도 요청 대기)**:
  * 운영 n8n 인스턴스에 `[Stock] Swallow - CNN Fear & Greed` 워크플로우 등록·활성화, 운영 DB 적재(운영 DB write 0건 유지), 수동 스크립트 운영 실행, Grafana 대시보드 새 값 반영 확인은 **모두 수행하지 않았으며 별도 요청 대기** 상태다.
  * 현재 운영 DB의 `FEAR_GREED` 값은 기존 `45` (`2026-10-10 18:58:43 KST`) 그대로 유지되고 있다.
* **백로그 연결**:
  * [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그#SW-008 — CNN·비트코인 공포탐욕 지수 분리|SW-008 — CNN·비트코인 공포탐욕 지수 분리]]
  * [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그#SW-003 — 매크로 수집기의 하드코딩 자격증명 제거|SW-003 — 매크로 수집기의 하드코딩 자격증명 제거]]

---

## 관련 문서

- [[Home|🏠 홈으로]]
- [[Work/Birds-Nest/index|Birds-Nest 프로젝트 인덱스]]
- [[Work/Birds-Nest/작업기록/Swallow/index|Swallow 작업 문서 목록]]
- [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그|Swallow 작업 백로그]]
