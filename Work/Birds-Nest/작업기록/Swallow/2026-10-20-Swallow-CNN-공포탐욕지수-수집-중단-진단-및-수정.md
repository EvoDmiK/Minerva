---
created: 2026-10-20
date: 2026-10-20
project: Birds-Nest
task_id: SW-008
type: worklog
status: deployed_db_verified_pending_ui
tags:
  - worklog
  - birds-nest
  - swallow
---
# [SW-008] Swallow CNN 공포·탐욕 지수 수집 중단 진단 및 전용 수집기 구현·운영 배포

## 요약

Swallow 대시보드의 CNN 공포·탐욕 지수(`FEAR_GREED`) 수집 중단 원인을 진단하고, 공식 CNN 데이터비즈 API 단독 검증 및 전용 n8n 수집 워크플로우(`n8n/Swallow/fear-greed.json`, 6노드, ID `5mkkZfHRh1zFGuZZ`)와 수동 동기화 스크립트(`scripts/sync-macro-indicators.js`) 정합성 보완을 구현·검증한 뒤, 사용자 승인을 받아 운영 n8n 배포·활성화 및 첫 예약 실행(`44008`)·운영 DB 적재(`23`, `extreme_fear`)까지 완료했다.

진단 당시 운영 `[Stock] Swallow - Watchlist Prices` (24노드)는 `KOSPI`, `KOSDAQ`, `USDKRW`만 정상 수집하고 있었으며, CNN 전용 노드나 활성 워크플로우가 없어 `FEAR_GREED`가 `45`(`2026-10-10T09:58:43Z` / `18:58:43 KST`), 이력 2행에 멈춰 있었다. 또한 수동 스크립트는 CNN 실패 시 암호화폐 공탐지수(`Alternative.me`)를 `FEAR_GREED` 코드와 `source='cnn'`으로 잘못 저장하는 폴백(SW-008)과 하드코딩된 DB 비밀번호 기본값(SW-003)을 포함하고 있었다.

암호화폐 대체 폴백과 하드코딩 비밀번호 기본값을 제거하고(`PGPASSWORD` 또는 `SWALLOW_PGPASSWORD` 환경변수 필수), 브라우저 5종 헤더를 사용한 공식 CNN API 호출, 0~100 점수·5종 등급·RFC3339 타임스탬프(96시간 이내·미래 10분 이내) 동일 검증 규칙, 원천 시각(`providerTs`) 보존, 단일 CTE(워크플로우) 및 지표별 트랜잭션(스크립트) Upsert와 과거 replay 보호를 구현했다. 운영 배포 후 첫 예약 실행 `44008` (`2026-10-20 14:07 KST`)이 정상 성공하여 운영 DB `FEAR_GREED`가 `23` (`extreme_fear`, `2026-10-20T00:00:00Z`)으로 갱신되었고, 워크플로우 스케줄을 본래 일일 `08:30` (`30 8 * * *`, `Asia/Seoul`, `versionId = activeVersionId = 2d535038-5bf9-403b-9109-e9039227f343`)으로 확정했다. Grafana `/api/health`는 `200 OK`이나 API `401` 및 브라우저 로그인 페이지 상태여서 **실제 Grafana UI 렌더링 및 데이터소스 쿼리 확인은 사용자 로그인 대기 상태**다.

## 작업 및 변경 결과 요약

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **원인 규명 / 요구사항** | CNN 공탐지수 수집 중단 진단 및 오염 방지 (SW-008, SW-003) | 운영 24노드 시세 워크플로우에 CNN 수집 경로 부재(자동 호출 없음, 진단 당시 DB `45` / `2026-10-10 18:58:43 KST` 정체). 짧은 헤더 요청 시 CNN `418` 차단 발생. 수동 스크립트의 `Alternative.me`(암호화폐 지수) `source='cnn'` 오적재 폴백 및 비밀번호 기본값 하드코딩 확인 |
| **설계 및 해결 방안** | 공식 CNN 단독 수집·원천 시각 보존·전용 워크플로우 분리 | 기존 관심종목(`watchlist-prices.json`)·뉴스(`workflows.json`) 무변경. 매일 `08:30` `Asia/Seoul` + 수동 실행 6노드 전용 워크플로우(`fear-greed.json`, 이식 보호용 파일 `active: false`) 분리. 브라우저 5종 헤더, 15s timeout / 3 tries, 워크플로우·스크립트 동일 검증 규칙 적용, `providerTs` 보존 및 `updated_at <= EXCLUDED.updated_at` replay 보호 |
| **코드 / 설정 수정** | 워크플로우 신설, 스크립트 보안/정합성 수정, 계약 테스트 추가, 문서 갱신 | `n8n/Swallow/fear-greed.json` (6노드), `scripts/sync-macro-indicators.js` (`Alternative.me` 폴백·비밀번호 기본값 제거, 지표별 트랜잭션), `n8n/Swallow/tests/fear-greed.test.mjs`, Swallow README 3종 |
| **실서비스 배포** | **운영 n8n 배포·활성화 및 첫 예약 실행·DB 적재 완료** | 신규 워크플로우 ID `5mkkZfHRh1zFGuZZ` (6노드, `active: true`, 최종 `versionId = activeVersionId = 2d535038-5bf9-403b-9109-e9039227f343`, `Asia/Seoul`, cron `30 8 * * *` 확정, 운영 `nodes`/`connections`가 repo `fear-greed.json`과 완전 일치). 운영 DB write는 CNN 워크플로우만 수행 |
| **검증 및 테스트** | 개발 검증(66 pass / 67 pass, 격리 DB E2E, `n8n-test` 18161) + **운영 예약 실행 `44008` 및 운영 DB 검증 완료** (Grafana UI 확인 대기) | 운영 단발 예약(`7 14 20 10 *`) 실행 `44008` (`2026-10-20 14:07 KST`, `05:07:00.040Z~00.281Z`) `status: success` → `value=23`, `extreme_fear`, `providerTs=2026-10-20T00:00:00Z`, `latest.updated=1`, `history.inserted=1`. 운영 DB 독립 조회로 `FEAR_GREED=23` 및 이력 3행(신규 `10/20` 1행 + 기존 `10/10` 2행 보존), 타 지표(`KOSPI 5512.03`, `KOSDAQ 781.79`, `USDKRW 1328`) 정상 확인. Grafana `/api/health` 200이나 API 401/로그인 페이지로 UI·쿼리 확인은 로그인 대기 |
| **형상 관리** | `dev-claude` → `dev-codex` 통합 후 `dev-docs` 문서 반영 | 백엔드 `84c6457`, 통합 `b9c7440` → `b5e518a` (graph `b122d1c` 및 이전 docs `359984c` 포함), `dev-docs` 운영 결과 문서 커밋·푸시 |

---

## 1. 작업 배경 및 문제 분석

### 발생 현상 / 요구사항
* Swallow 모니터링 대시보드의 공포 & 탐욕 지수(`FEAR_GREED`)가 `45`(`fear`)에서 갱신되지 않는 원인을 진단하고, 기존 관심종목·뉴스 파이프라인을 변경하지 않으면서 공식 CNN 지수를 신뢰성 있게 수집하도록 수정 및 운영 반영.

### 원인 분석 / 설계 검토
* **자동 수집 경로 부재**: 운영 `[Stock] Swallow - Watchlist Prices` (24노드)는 `KOSPI`, `KOSDAQ`, `USDKRW`와 관심종목만 수집 중이었고 CNN 전용 노드나 활성 워크플로우가 없었다. 수동 스크립트(`scripts/sync-macro-indicators.js`)만 존재하고 자동 호출되지 않아 진단 시점 운영 DB `FEAR_GREED`는 `45` (`2026-10-10T09:58:43Z` / `18:58:43 KST`), `stock_price_history` 이력은 2행에 멈춰 있었다.
* **CNN API 418 차단 및 헤더 조건**: CNN 공식 엔드포인트(`https://production.dataviz.cnn.io/index/fearandgreed/graphdata`)는 짧은 헤더 요청에 HTTP `418` 봇 차단을 반환하며, 브라우저 전체 `User-Agent`, `Accept`, `Accept-Language`, `Origin: https://edition.cnn.com`, `Referer: https://edition.cnn.com/markets/fear-and-greed` 포함 시 정상 `200 OK`를 반환함을 확인했다.
* **잘못된 Fallback (SW-008) 및 하드코딩 비밀번호 기본값 (SW-003)**: 수동 스크립트는 CNN 실패 시 암호화폐 지수(`Alternative.me`)를 `FEAR_GREED` 및 `source='cnn'`으로 저장하는 잘못된 폴백과 DB 비밀번호 기본값 하드코딩을 포함하고 있었다.

---

## 2. 해결 방안 및 주요 구현 내용

* **`n8n/Swallow/fear-greed.json` (전용 6노드 워크플로우, ID `5mkkZfHRh1zFGuZZ`)**:
  * 수동 트리거 + 매일 `08:30` (`30 8 * * *`, `Asia/Seoul`) 스케줄 트리거 → 공식 CNN HTTP 조회(브라우저 5종 헤더, 15s timeout, 3 tries) → `CNN 검증 및 적재 준비` Code 노드(콜론 없는 오류 문구) → `공탐지수 적재` Postgres 노드(`데이터 DB` 자격증명 재사용, 단일 CTE로 `market_macro_indicators`·`stock_price_history` 원자적 Upsert 및 `updated_at <= EXCLUDED.updated_at` 과거 replay 보호) → `적재 확인` Code 노드. 저장소 JSON 파일의 `active: false`는 이식 보호 설정으로 유지한다.
* **`scripts/sync-macro-indicators.js` (수동 동기화 스크립트 정합성 및 보안)**:
  * `Alternative.me` 폴백 및 하드코딩 비밀번호 기본값 제거(`PGPASSWORD` 또는 `SWALLOW_PGPASSWORD` 환경변수 필수).
  * 워크플로우와 동일한 브라우저 헤더, 15s timeout, 동일 검증 규칙(`score` 0~100 숫자/비어 있지 않은 숫자 문자열, 5종 `rating`, 타임존 포함 RFC3339 `timestamp` 과거 96h·미래 10m 이내, 원천 시각 `providerTs` 보존)을 적용하고 지표별 `BEGIN ... COMMIT / ROLLBACK` 트랜잭션으로 묶음.
* **`n8n/Swallow/tests/fear-greed.test.mjs` 및 문서 3종 (`n8n/Swallow/README.md`, `mcp/swallow-mcp/README.md`, `grafana/swallow/README.md`)**:
  * 워크플로우 Code 노드와 스크립트 파서가 동일 입력에서 동일한 판정을 내리는지 계약 테스트로 검증하고, 격리 PostgreSQL SQL 멱등성·경계값 테스트 및 운영 배포 결과 문서 반영 완료.

---

## 3. 검증 및 테스트 결과

### 3.1 개발 및 격리 환경 검증
* **계약 및 SQL 멱등성 테스트**:
  * 명령어: `FNG_TEST_PG_CONTAINER=swallow-cnn-review-pg node --test n8n/Swallow/tests/*.test.mjs`
  * 결과: **총 67개 중 `66 passed, 0 failed, 1 skipped`** (`CNN_LIVE` 미설정 기본 스킵; `dev-claude`에서는 `CNN_LIVE=1` 포함 **67 passed**). 최초 적재, 동일 원천 시각 재실행 이력 중복 없음, 과거 시각 replay 시 최신값 보호(`keptNewer=1`), 경계값 `0` 적재, 타 지표(`KOSPI=2500`) 보존 전부 PASS.
* **스크립트 전체 DB 경로 격리 E2E 검증 (`syncMacroIndicators()`)**:
  * 별도 localhost 일회용 PostgreSQL에서 HTTP fixture와 함께 실제 `syncMacroIndicators()`를 실행하여 `latest`/`history` 적재, `providerTs` 보존, 동일 재실행 중복 없음, CNN HTTP `418` 시 기존 `FEAR_GREED` 보존 및 `process.exitCode = 1`, 이력 트리거 강제 오류 시 최신값까지 `ROLLBACK` 전부 PASS (수동 스크립트의 운영 DB 직접 실행은 미수행).
* **`n8n-test` (`2.15.0`) 실제 원천 HTTP 검증**:
  * read-only 실행 `18160` 및 최종 JSON 실행 `18161` (`2026-10-20T04:43:55.522Z~04:43:56.084Z` / `13:43 KST`, HTTP 72ms + Code 328ms) `status: success` → `current_value: 23` (`rawScore: 22.9928571428571`), `status: "extreme_fear"`, `providerTs: "2026-10-20T00:00:00.000Z"` 확인 후 임시 실행(`18159`/`18160`/`18161`, `18159`는 외부 runner 미연결 대기 종료로 구분) 및 임시 워크플로우 삭제 정리 완료.

### 3.2 운영 배포 및 라이브 예약 실행·운영 DB 검증 (`44008`)
* **운영 워크플로우 등록 및 최초 예약 실행**:
  * 사용자 운영 배포 승인 후 신규 워크플로우 `[Stock] Swallow - CNN Fear & Greed` (`5mkkZfHRh1zFGuZZ`, 6노드, `active: true`, 초기 `versionId: a9efde06-0585-46ae-a543-15b1e14a642e`)를 생성하고, 최초 예약 검증을 위해 단발 cron(`7 14 20 10 *`)으로 시작했다.
  * **실행 `44008`** (`2026-10-20 14:07 KST`, `05:07:00.040Z~05:07:00.281Z`, `mode: trigger`, **`status: success`**):
    * 노드별 소요 시간: `Schedule Trigger` 1ms → `CNN 공탐지수 조회` 131ms → `CNN 검증 및 적재 준비` 34ms → `공탐지수 적재` 39ms → `적재 확인` 12ms.
    * 요약 결과: `value: 23`, `rawScore: 22.9928571428571`, `status: "extreme_fear"`, `providerTs: "2026-10-20T00:00:00.000Z"`, `latest.updated: 1`, `history.inserted: 1`.
* **본래 일일 스케줄 확정 및 정합성 재확인**:
  * 실행 `44008` 확인 직후 검증용 단발 cron을 제거하고 본래 일일 스케줄(`30 8 * * *`, `timezone: Asia/Seoul`)로 PUT 자동 게시 및 GET 재확인을 완료했다.
  * 최종 `versionId = activeVersionId = 2d535038-5bf9-403b-9109-e9039227f343`, `active: true` 상태이며, 운영 `nodes` 및 `connections`가 저장소 `n8n/Swallow/fear-greed.json`과 완전히 일치함을 검증했다.
* **운영 PostgreSQL DB 독립 조회 검증**:
  * `public.market_macro_indicators`: `FEAR_GREED`가 `current_value = 23`, `status = 'extreme_fear'`, `updated_at = 2026-10-20T00:00:00Z`로 갱신됨을 확인(과거 진단 시점의 `45` / `2026-10-10 18:58:43 KST`는 당시 진단 기록으로 보존).
  * `public.stock_price_history`: `2026-10-20 00:00:00Z` (`source='cnn'`, `close_price=23`) 신규 1행이 추가되고, 기존 `2026-10-10`의 `45` 2행이 그대로 보존됨을 확인.
  * 타 거시 지표 지속 수집 정상 확인: `KOSPI 5512.03`, `KOSDAQ 781.79`, `USDKRW 1328` (`updated_at 05:07Z`). 운영 DB write는 CNN 워크플로우만 수행했다.

---

## 4. 배포 현황 및 남은 확인 항목

* **코드 및 문서 형상**: 백엔드 `84c6457` → 통합 `b9c7440` → `b5e518a` (graph `b122d1c` 및 이전 docs `359984c` 포함) → `dev-docs` 운영 배포·검증 결과 문서 커밋 및 푸시.
* **남은 확인 항목 (Grafana UI/데이터소스 쿼리 확인 대기)**:
  * Grafana `/api/health`는 `200 OK`이나 API `401` 및 브라우저 로그인 페이지 상태여서 실제 Grafana 대시보드(`swallow-stock-monitor` Panel ID 105) 화면 렌더링 및 데이터소스 쿼리 확인은 사용자 비동기 로그인 응답 대기 중이다.
  * `SW-003`의 코드상 하드코딩 비밀번호 기본값 제거는 완료되었으나, 운영 자격증명 교체 및 과거 Git 이력 정리는 별도 범위로 미수행 유지한다.
* **백로그 연결**:
  * [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그#SW-008 — CNN·비트코인 공포탐욕 지수 분리|SW-008 — CNN·비트코인 공포탐욕 지수 분리]]
  * [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그#SW-003 — 매크로 수집기의 하드코딩 자격증명 제거|SW-003 — 매크로 수집기의 하드코딩 자격증명 제거]]

---

## 관련 문서

- [[Home|🏠 홈으로]]
- [[Work/Birds-Nest/index|Birds-Nest 프로젝트 인덱스]]
- [[Work/Birds-Nest/작업기록/Swallow/index|Swallow 작업 문서 목록]]
- [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그|Swallow 작업 백로그]]
