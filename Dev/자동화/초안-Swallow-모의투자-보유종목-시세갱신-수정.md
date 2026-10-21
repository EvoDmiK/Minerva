---
created: 2026-10-21
updated: 2026-10-21
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Swallow/2026-10-21-Swallow-모의투자-보유종목-시세갱신-수정]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# [SW-014] Swallow 모의투자 보유 종목 시세(평가가격) 갱신 수정

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Swallow/2026-10-21-Swallow-모의투자-보유종목-시세갱신-수정]] · 분류 근거 {"인프라":1,"자동화":14,"관측성":7,"데이터":0}

## 1. 개요 및 목적

Swallow 모의투자 포트폴리오의 보유 종목 `현재가`(`paper_positions.last_price`)가 매수가에 고정되어 평가손익이 0으로 보였다. 원인은 관심종목 시세 수집기(`[Stock] Swallow - Watchlist Prices`)가 활성 관심종목만 수집하고 포지션 평가가격은 갱신하지 않았기 때문이다.

dev-claude `9fb5df3`에서 수집 대상을 **활성 관심종목 ∪ 관심목록 밖 보유 종목**으로 넓혔다. 검증된 시세를 적재하는 같은 SQL 문장에서 보유 포지션의 `last_price`·`updated_at`만 갱신한다. dev-codex `850da6a`에 통합되었다.

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
- 자동화 테스트 (단위 / 회귀) — root 독립 실행
- 실서비스 / UI 검증 증거
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```sql
), priced AS (
  SELECT DISTINCT ON (ticker) ticker, ts, close_price
  FROM input
  WHERE source IN ('naver', 'toss')
  ORDER BY ticker, CASE source WHEN 'naver' THEN 0 ELSE 1 END
), positions AS (
  UPDATE public.paper_positions p
  SET last_price = priced.close_price,
      updated_at = priced.ts
  FROM priced
  WHERE p.ticker = priced.ticker
    AND p.quantity > 0
    AND p.updated_at <= priced.ts
  RETURNING p.ticker
)
```

## 4. 검증 근거 및 트러블슈팅

Swallow 모의투자 포트폴리오의 보유 종목 `현재가`(`paper_positions.last_price`)가 매수가에 고정되어 평가손익이 0으로 보였다. 원인은 관심종목 시세 수집기(`[Stock] Swallow - Watchlist Prices`)가 활성 관심종목만 수집하고 포지션 평가가격은 갱신하지 않았기 때문이다.

dev-claude `9fb5df3`에서 수집 대상을 **활성 관심종목 ∪ 관심목록 밖 보유 종목**으로 넓혔다. 검증된 시세를 적재하는 같은 SQL 문장에서 보유 포지션의 `last_price`·`updated_at`만 갱신한다. dev-codex `850da6a`에 통합되었다.

**현재 상태:** 구현이 완료되었고 root의 자동 테스트(격리 PG 포함)를 통과했다. 실제 n8n 개발 노드 검증은 root가 진행 중이다. **운영 n8n 배포·운영 DB 변경·Grafana UI 확인은 하지 않았다.**

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **원인 규명 / 요구사항** | 보유 종목 평가가격 고정 | 보유 6종목의 `last_price`가 10/15~10/20 매수가에 고정되었다. 5종목은 관심목록 밖이라 시세 이력이 없었다 |
| **설계 및 해결 방안** | 수집 대상 확장 + 원자적 갱신 | 관심 ∪ 보유(`quantity > 0`)를 중복 없이 수집한다. 시세 upsert와 같은 CTE 문장에서 naver 우선·toss 대체 가격으로 갱신하고, `updated_at <= snapshotTs`일 때만 갱신한다 |
| **코드 / 설정 수정** | `n8n/Swallow/watchlist-prices.json` | `관심종목 조회`·`관심종목 정규화`·`시세 적재`·`수집 요약` 4개 노드(24노드 유지)와 테스트를 수정했다 |
| **실서비스 배포** | 미실시 | 운영 n8n·운영 DB·Grafana는 변경하지 않았다 |
| **검증 및 테스트** | 72건 중 71 pass / 0 fail / 1 skip | root가 독립 실행했다. 격리 PG에서 실제 SQL 시나리오를 통과했다. n8n 개발 노드 검증은 진행 중이다 |
| **형상 관리** | `9fb5df3` → `850da6a` | dev-claude 구현, dev-codex 통합(기준 HEAD `1c616fc`), 이 문서는 dev-docs에서 작성 |

* **수집 대상**: 활성 관심종목 `UNION ALL` 관심목록 밖 보유 종목(`quantity > 0`). 같은 티커는 `관심종목 정규화`에서 한 번만 조회한다. 회사명은 `paper_positions` → `companies` 순으로, 시장은 `companies`에서 채운다. **관심목록은 읽기만 하며 변경하지 않는다.**
* **원자적 갱신**: `stock_price_history` upsert와 같은 CTE 문장에서 `paper_positions.last_price`·`updated_at`을 스냅샷 가격·시각으로 갱신한다.
  * 가격 소스는 naver를 우선하고, 없으면 toss를 쓴다.
  * `quantity > 0 AND updated_at <= snapshotTs`인 행만 갱신하므로 더 새 체결이나 이후 스냅샷을 덮지 않는다.
  * 유효 시세가 없는 종목은 기존 가격·시각을 유지한다.
* **불변 범위**: 예수금, 수량, 평단, 원가, 거래 이력, 주문 키는 바꾸지 않는다. `execute_paper_trade` 등 자동매매 함수도 호출하지 않는다.
* **요약**: `positionsUpdated`를 따로 기록한다. 더 새 시각 보호로 0이 나올 수 있으며 실패로 판정하지 않는다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Swallow/2026-10-21-Swallow-모의투자-보유종목-시세갱신-수정]]
- [[Dev/index|Dev 인덱스]]
