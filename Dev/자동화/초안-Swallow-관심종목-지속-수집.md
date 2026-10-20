---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-관심종목-지속-수집]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# Swallow 관심종목 지속 수집

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-관심종목-지속-수집]] · 분류 근거 {"인프라":0,"자동화":9,"관측성":4,"데이터":0}

## 1. 개요 및 목적

작업 ID: SW-010 완료, SW-009의 시세 경로 검증 완료(뉴스 적재 검증은 별도 미완료).

사용자가 NAS SSH를 열고 관심종목을 계속 수집하도록 요청했다. NAS n8n에 가격 전용 workflow `Kt26XhwQEO2SuRtt` — `[Stock] Swallow - Watchlist Prices`를 배포하고 활성화했다.

## 2. 핵심 아키텍처 및 원칙

- 요청과 결과
- 확인한 원인과 구현
- 직접 실행한 검증
- 남은 한계와 복구
- 후속 예약 실행 확인
- 후속 수집주기 변경

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

작업 ID: SW-010 완료, SW-009의 시세 경로 검증 완료(뉴스 적재 검증은 별도 미완료).

- 매 5분, 24시간, `Asia/Seoul`, cron `*/5 * * * *`.
- 매 실행 `data.public.stock_watchlist`의 `is_active=true`만 조회한다. 현재 `000660` SK하이닉스와 `005930` 삼성전자.
- 관심종목 추가·비활성화는 다음 실행부터 반영된다.
- 토스는 활성 종목 전체를 한 요청으로 조회하고 symbol로 연결한다. 네이버는 종목별 조회 후 itemCode를 대조한다.
- `stock_price_history`에 source별로 적재한다. `ts`는 실제 조회 스냅샷 시각(UTC timestamptz)이며 provider 거래시각과 구분한다.
- 잘못된 가격과 실패 응답은 적재하지 않는다. 일부 실패에도 정상 행은 적재하고, 상세 요약과 짧은 오류 문구를 남겨 실행 실패를 표시한다.
- 반복 수집은 뉴스 분석·모의매매·Discord 발송과 분리했다.

- 최초 구현 `a84dfeab534bca571251841e8f104888b35dc9e0`.
- 첫 실행에서 토스 종목별 OAuth 요청 중 `401 token-revoked`가 발생했다. 토스 일괄 조회·symbol 매핑·오류 요약 보완 `ce682d2cd6504b6fe0e856765abe6be370c69921`.
- dev-codex 통합 기준 `9e744c857bb476b46807b7bced9749572107f329`.
- 스키마 변경 없이 기존 DB·토스 자격증명 참조를 재사용했다. 비밀값은 문서나 workflow JSON에 기록하지 않았다.

- `node --test n8n/Swallow/tests/watchlist-prices.test.mjs`: 최종 18개 통과, 실패·skip 0개.
- n8n Public API 생성·활성화·수정 배포 후 GET으로 활성 상태, timezone, 12개 노드 및 토스 `executeOnce=true` 확인.
- `28230` (10:15 KST): 네이버 2행·토스 1행 적재, 토스 삼성전자 인증 실패로 error. 초기 실패 이력은 보존했다.
- `28244` (10:20 KST): 최초 구현에서 두 종목·두 소스 4행 적재, success.
- `28253` (10:25 KST): 보완본에서 토스 응답 item 1개/result 2심볼, 네이버 2종목, 총 4행 inserted, errors/failures 빈 배열, `실패 확인`까지 success.
- NAS `postgres-n8n`의 `data` DB 직접 조회: 두 종목 × 두 소스의 최신 `ts` 모두 2026-10-12 10:25(KST).
- 실제 10:25의 4행을 같은 workflow upsert SQL로 재처리한 트랜잭션에서 inserted 0 / updated 2(각 source), 총 행 4개 유지. ROLLBACK으로 검증 변경을 폐기했다.
- 실제 `grafana.resource`의 패널 8 SQL을 `data` DB에서 실행: 토스·네이버 수집 경과 약 0.50분(30초). 실제 대시보드 refresh는 1분.

- Grafana HTTP API는 401을 반환해 브라우저 렌더링은 직접 확인하지 못했다. DB 및 실제 패널 SQL 검증과 구분한다.
- CNN/거시경제 지표는 이번 관심종목 가격 수집 대상이 아니다. 해당 지표의 과거 시각은 남아 있다.
- 토스 다종목 API는 최대 200개이다. 현재 대상은 2개이며, 기존 뉴스 workflow와 동시에 토큰을 재발급하면 외부 경쟁이 발생할 가능성은 남아 있다.
- 장애 시 신규 workflow `Kt26XhwQEO2SuRtt`만 deactivate하고 수집 이력은 보존한다.
- [Draft PR #5](https://github.com/EvoDmiK/Birds-Nest/pull/5)에 코드·문서 통합을 반영했다. 최종 dev-codex `b010e3a`를 push했다. main 최종 머지는 사용자 담당이다.
- [토스 공식 시세 계약](https://openapi.tossinvest.com/openapi-docs/latest/openapi.json)
- [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그|Swallow 작업 백로그]]

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-관심종목-지속-수집]]
- [[Dev/index|Dev 인덱스]]
