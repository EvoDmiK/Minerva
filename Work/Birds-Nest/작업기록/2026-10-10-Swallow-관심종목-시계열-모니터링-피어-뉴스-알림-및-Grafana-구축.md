---
updated: 2026-10-10
created: 2026-10-10
project: Birds-Nest
type: work-log
tags:
  - birds-nest
  - swallow
  - grafana
  - mcp
  - paper-trading
  - watchlist
  - toss
  - risk-management
  - mlflow
---

# 2026-10-10 — [Stock] Swallow 관심종목 시계열 모니터링, 토스·네이버 교차검증, 매크로 지표 및 리스크 관리 구축

## 1. 개요 및 배경

- **목적**:
  1. 사용자가 원하는 관심종목(Watchlist)을 등록하여 시계열 주가 데이터 수집·모니터링.
  2. 관심종목 직접 뉴스뿐만 아니라 **유사/경쟁사/공급망(피어, Peer) 종목 뉴스** 발생 시 Gemini AI 파급 효과 분석 및 Discord 실시간 알림.
  3. **토스증권 공식 Open API(OAuth2)**와 **네이버페이 증권**을 결합한 **이중 소스 교차검증(Cross-validation) 및 이상치 감지** 체계 구축.
  4. Grafana 대시보드에 **글로벌/국내 매크로 지표(코스피, 코스닥, 환율, Fear & Greed)**를 상단에 배치하고 주가 차트 위 뉴스 어노테이션(Annotation) 제공.
  5. 원칙 기반의 **모의투자 리스크 관리(자동 익절 +5%, 자동 손절 -3%, 급등 추격매수 +7% 차단)** 및 **MLflow 포트폴리오 트래킹** 연동.
- **협업 방식**: Claude Code CLI(`claude -p`)와 Antigravity가 페어 프로그래밍으로 DDL 설계, MCP 도구 검토, n8n 연동 및 검증을 공동 진행.

---

## 2. 데이터베이스 스키마 확장 (`mcp/swallow-mcp/schema.sql`)

NAS PostgreSQL `data` 데이터베이스에 구축된 핵심 스키마:

1. **`stock_watchlist` (관심종목 관리)**:
   - `ticker` (PK, 6자리 코드), `company_name`, `market`, `is_active`, `note`, `added_at`
   - ETF·신규 상장 종목 유연성을 위해 `companies` 외래키(FK) 해제.
2. **`stock_price_history` (시계열 주가 적재 & 교차검증)**:
   - 복합 PK: `(ticker, ts, source)` (토스 `'toss'`, 네이버 `'naver'` 분리 적재 및 멱등성 보장).
   - `close_price`, `open_price`, `high_price`, `low_price`, `change_amt`, `change_rate`, `volume`, `created_at`.
3. **`stock_news_alerts` (피어 뉴스 알림 & Grafana 어노테이션 소스)**:
   - `watch_ticker` (내 관심종목), `news_ticker` (기사 대상 종목), `relation_type` (`direct`, `peer`, `supply_chain`, `competitor`), `relation_reason`, `sentiment`, `importance` (1~5), `title`, `url`, `published_at`, `discord_sent_at`.
   - `UNIQUE (watch_ticker, url)`로 중복 알림 방지.
4. **`market_macro_indicators` (글로벌 매크로 & 국내 시장 지표)**:
   - `code` (PK: `'KOSPI'`, `'KOSDAQ'`, `'USDKRW'`, `'FEAR_GREED'`), `name`, `current_value`, `change_amt`, `change_rate`, `status`, `updated_at`.
5. **`paper_account`, `paper_positions`, `paper_trades` (모의투자 포트폴리오 원장)**:
   - 가상 예수금, 보유 종목 평단/수량, 체결 내역 및 실현 손익 추적.

---

## 3. 원칙 기반 투자 리스크 관리 엔진 (`execute_paper_trade`)

저장 프로시저 `execute_paper_trade`에 3대 원칙 기반 리스크 관리 알고리즘 내장:

1. **🎯 자동 익절 (Take-Profit: +5.0%)**:
   - 보유 종목 평가수익률이 `+5.0%` 이상 도달 시, AI 시그널과 무관하게 즉시 전량 자동 매도 청산.
   - 체결 로그에 `TARGET_TAKE_PROFIT` 기록 및 실현 손익 현금화.
2. **🛡️ 자동 손절 (Stop-Loss: -3.0%)**:
   - 보유 종목 손실률이 `-3.0%` 이하 도달 시 즉시 전량 자동 손절 매도하여 추가 손실 제한.
3. **⚠️ 급등 추격매수 방지 가드 (Chase Buy Guard: +7.0%)**:
   - 당일 등락률이 `+7.0%` 이상 급등한 과열 종목은 AI 시그널이 '매수'이더라도 `CHASE_BUY_GUARDED`로 체결 차단 (단, 수동 강제 주문은 허용).

---

## 4. Swallow MCP 도구 확장 (총 10종 도구 체제)

[`mcp/swallow-mcp/index.js`](file:///Volumes/Dove-Nest-SSD/projects/Birds-Nest/mcp/swallow-mcp/index.js) 도구 구성:

1. **`swallow_get_portfolio`**: 모의투자 총자산, 예수금, 종목별 평가손익 및 MLflow 스냅샷 자동 기록.
2. **`swallow_get_trades`**: 체결 이력 조회.
3. **`swallow_order`**: 수동 가상 주문.
4. **`swallow_check_stock`**: 종목별 보유 현황 단건 조회.
5. **`swallow_get_stock_price`**: 네이버페이/토스 실시간 시세 조회.
6. **`swallow_get_stock_news`**: 최신 뉴스 목록 조회.
7. **`swallow_watchlist`**: 관심종목 목록 조회 및 추가/삭제.
8. **`swallow_get_price_history`**: 소스별 시세 이력 및 교차검증 괴리율(±0.5%) 리포트.
9. **`swallow_get_news_alerts`**: 관심종목 관련 피어 뉴스 및 파급 영향 브리핑.
10. **`swallow_reset_portfolio`**: 모의투자 포트폴리오 초기화(기본 1,000만원) 및 MLflow에 `RESET` 이벤트 기록.

---

## 5. Grafana 대시보드 구성 & 쿼리 검증

- **접속 URL**: [Swallow 모니터링 대시보드](https://monitoring.dove-nest.com/d/swallow-stock-monitor) (UID: `swallow-stock-monitor`)
- **패널 레이아웃**:
  - **Row 1: 글로벌 매크로 & 국내 시장 지표** (신설)
    - 🇰🇷 코스피 (KOSPI Stat Panel)
    - 🇰🇷 코스닥 (KOSDAQ Stat Panel)
    - 💵 원/달러 환율 (USD/KRW Stat Panel)
    - 😨 공포 & 탐욕 지수 (Fear & Greed Gauge Panel, 0~100)
  - **Row 2: 관심종목 시계열 & 피어 분석**
    - `$ticker` 변수 기반 주가 시계열 차트 (토스 vs 네이버)
    - 실시간 교차검증 괴리율 게이지
    - 거래량 추이 바 차트
    - 차트 위 피어 뉴스 어노테이션(Annotation) 마커
    - 실시간 피어/연관 뉴스 타임라인 테이블
- **쿼리 자동 검증 ([`scripts/verify-swallow-queries.js`](file:///Volumes/Dove-Nest-SSD/projects/Birds-Nest/scripts/verify-swallow-queries.js))**:
  - 템플릿 변수, 어노테이션, 10개 패널 전 쿼리에 대해 PostgreSQL 실 DB 쿼리 실행 검증 완료 (10/10 성공, 0 실패).

---

## 6. MLflow MLOps 트래킹 연동

- **실시간 뉴스 Triage 실험 (Exp ID: 36, `swallow-stock-triage`)**:
  - Gemini AI 판단 감정/시그널, 신뢰도(`confidence`), 영향도(`impact_score`), 품질 점수(`evaluation_score`) 로깅.
- **모의투자 포트폴리오 실험 (Exp ID: 37, `swallow-paper-portfolio`)**:
  - 총자산(`total_asset`), 예수금(`cash_balance`), 주식평가액(`stock_valuation`), 실현손익, 보유종목수 등 시계열 메트릭 로깅.
  - 포트폴리오 리셋 및 스냅샷 이벤트 추적.

---

## 7. 검증 및 배포 현황

1. **PostgreSQL 실 DB 단위 테스트**:
   - 익절 테스트 (+6.0% 도달 시 `TAKE_PROFIT` 자동 전량 매도) 통과 ✅
   - 손절 테스트 (-4.0% 도달 시 `STOP_LOSS` 자동 전량 매도) 통과 ✅
   - 추격매수 방지 테스트 (+8.5% 급등 종목 매수 시 `CHASE_BUY_GUARDED` 차단) 통과 ✅
2. **Git Sync 및 리포지토리 반영**:
   - `Birds-Nest` 리포지토리 `dev-mac` 브랜치에 커밋 및 푸시 완료 (`c16f27e`).
   - `graphify update .` 지식 그래프 최신화 완료.

---

## 8. 관련 링크

- [[Work/Birds-Nest/index|Birds-Nest 인덱스]]
- [[Work/Birds-Nest/작업기록/2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포|2026-10-09 — [Stock] Swallow 워크플로우 고도화 (단일 체인 개편 및 NAS n8n 배포)]]
