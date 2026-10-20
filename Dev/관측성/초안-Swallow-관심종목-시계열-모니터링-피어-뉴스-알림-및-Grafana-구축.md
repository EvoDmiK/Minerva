---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Swallow/2026-10-10-Swallow-관심종목-시계열-모니터링-피어-뉴스-알림-및-Grafana-구축]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# 2026-10-10 — [Stock] Swallow 관심종목 시계열 모니터링, 토스·네이버 교차검증, 매크로 지표 및 리스크 관리 구축

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Swallow/2026-10-10-Swallow-관심종목-시계열-모니터링-피어-뉴스-알림-및-Grafana-구축]] · 분류 근거 {"인프라":2,"자동화":5,"관측성":14,"데이터":3}

## 1. 개요 및 목적

- **목적**:
  1. 사용자가 원하는 관심종목(Watchlist)을 등록하여 시계열 주가 데이터 수집·모니터링.
  2. 관심종목 직접 뉴스뿐만 아니라 **유사/경쟁사/공급망(피어, Peer) 종목 뉴스** 발생 시 Gemini AI 파급 효과 분석 및 Discord 실시간 알림.
  3. **토스증권 공식 Open API(OAuth2)**와 **네이버페이 증권**을 결합한 **이중 소스 교차검증(Cross-validation) 및 이상치 감지** 체계 구축.
  4. Grafana 대시보드에 **글로벌/국내 매크로 지표(코스피, 코스닥, 환율, Fear & Greed)**를 상단에 배치하고 주가 차트 위 뉴스 어노테이션(Annotation) 제공.
  5. 원칙 기반의 **모의투자 리스크 관리(자동 익절 +5%, 자동 손절 -3%, 급등 추격매수 +7% 차단)** 및 **MLflow 포트폴리오 트래킹** 연동.
- **협업 방식**: Claude Code CLI(`claude -p`)와 Antigravity가 페어 프로그래밍으로 DDL 설계, MCP 도구 검토, n8n 연동 및 검증을 공동 진행.

---

## 2. 핵심 아키텍처 및 원칙

- 1. 개요 및 배경
- 2. 데이터베이스 스키마 확장 (`mcp/swallow-mcp/schema.sql`)
- 3. 원칙 기반 투자 리스크 관리 엔진 (`execute_paper_trade`)
- 4. Swallow MCP 도구 확장 (총 11종 도구 체제)
- 5. Grafana 대시보드 구성 & 쿼리 검증
- 6. MLflow MLOps 트래킹 연동
- 7. 검증 및 배포 현황
- 8. 모의투자 손실률 & 뉴스 영향도 분석 (News Impact Tracker) 및 2-Tab 대시보드 분리
- 9. 관련 링크

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- **목적**:
  1. 사용자가 원하는 관심종목(Watchlist)을 등록하여 시계열 주가 데이터 수집·모니터링.
  2. 관심종목 직접 뉴스뿐만 아니라 **유사/경쟁사/공급망(피어, Peer) 종목 뉴스** 발생 시 Gemini AI 파급 효과 분석 및 Discord 실시간 알림.
  3. **토스증권 공식 Open API(OAuth2)**와 **네이버페이 증권**을 결합한 **이중 소스 교차검증(Cross-validation) 및 이상치 감지** 체계 구축.
  4. Grafana 대시보드에 **글로벌/국내 매크로 지표(코스피, 코스닥, 환율, Fear & Greed)**를 상단에 배치하고 주가 차트 위 뉴스 어노테이션(Annotation) 제공.
  5. 원칙 기반의 **모의투자 리스크 관리(자동 익절 +5%, 자동 손절 -3%, 급등 추격매수 +7% 차단)** 및 **MLflow 포트폴리오 트래킹** 연동.
- **협업 방식**: Claude Code CLI(`claude -p`)와 Antigravity가 페어 프로그래밍으로 DDL 설계, MCP 도구 검토, n8n 연동 및 검증을 공동 진행.

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
11. **`swallow_backtest`**: 과거 일봉 시세 기반 퀀트 전략(RSI 과매도 반등) 시뮬레이션 및 MLflow(Exp 39: `swallow-quant-backtest`) 자동 로깅.

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

- **실시간 뉴스 Triage 실험 (Exp ID: 36, `swallow-stock-triage`)**:
  - Gemini AI 판단 감정/시그널, 신뢰도(`confidence`), 영향도(`impact_score`), 품질 점수(`evaluation_score`) 로깅.
- **모의투자 포트폴리오 실험 (Exp ID: 37, `swallow-paper-portfolio`)**:
  - 총자산(`total_asset`), 예수금(`cash_balance`), 주식평가액(`stock_valuation`), 실현손익, 보유종목수 등 시계열 메트릭 로깅.
  - 포트폴리오 리셋 및 스냅샷 이벤트 추적.
- **퀀트 백테스트 실험 (Exp ID: 39, `swallow-quant-backtest`)**:
  - 전략 파라미터(`rsi_period`, `buy_threshold`, `take_profit_pct`, `stop_loss_pct`), 성과 지표(수익률, MDD, 승률, Profit Factor, 평균 보유일) 로깅.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Swallow/2026-10-10-Swallow-관심종목-시계열-모니터링-피어-뉴스-알림-및-Grafana-구축]]
- [[Dev/index|Dev 인덱스]]
