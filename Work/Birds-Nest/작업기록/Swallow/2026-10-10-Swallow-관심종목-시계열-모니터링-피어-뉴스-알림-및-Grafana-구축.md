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

## 4. Swallow MCP 도구 확장 (총 11종 도구 체제)

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
11. **`swallow_backtest`**: 과거 일봉 시세 기반 퀀트 전략(RSI 과매도 반등) 시뮬레이션 및 MLflow(Exp 39: `swallow-quant-backtest`) 자동 로깅.

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
- **퀀트 백테스트 실험 (Exp ID: 39, `swallow-quant-backtest`)**:
  - 전략 파라미터(`rsi_period`, `buy_threshold`, `take_profit_pct`, `stop_loss_pct`), 성과 지표(수익률, MDD, 승률, Profit Factor, 평균 보유일) 로깅.

---

## 7. 검증 및 배포 현황

1. **PostgreSQL 실 DB 단위 테스트**:
   - 익절 테스트 (+6.0% 도달 시 `TAKE_PROFIT` 자동 전량 매도) 통과 ✅
   - 손절 테스트 (-4.0% 도달 시 `STOP_LOSS` 자동 전량 매도) 통과 ✅
   - 추격매수 방지 테스트 (+8.5% 급등 종목 매수 시 `CHASE_BUY_GUARDED` 차단) 통과 ✅
2. **Git Sync 및 리포지토리 반영**:
   - `Birds-Nest` 리포지토리 `dev-mac` 및 운영 기준 `main` 브랜치에 최종 병합 및 푸시 완료 (`2c045da`).
   - `origin/main`과 `origin/dev-mac` 완전 동기화 달성.
   - `mcp/swallow-mcp/README.md` 및 `grafana/swallow/README.md` 상세 확충 완료.
   - `graphify update .` 지식 그래프 최신화 완료.

---

## 8. 모의투자 손실률 & 뉴스 영향도 분석 (News Impact Tracker) 및 2-Tab 대시보드 분리

- **배경 및 목적**:
  - 모의투자 시 단순 계좌 잔고뿐 아니라 누적 손실률(`%`), 보유 종목별 손익률(`%`), 실현 손익률을 정밀하게 가시화.
  - "어떤 뉴스를 보고 매매 판단을 내렸을 때 주가가 어떻게 변했는가?"에 대한 인과 관계(Causality)를 추적.
  - 대형 뉴스 영향도 분석 테이블의 가독성을 극대화하기 위해 독립된 전용 탭(대시보드)으로 분리.
- **주요 구현 내용**:
  1. **DB 스키마 및 저장 프로시저 확장**:
     - `paper_positions`에 `entry_news_title`, `entry_news_url` 추가.
     - `paper_trades`에 `news_title`, `news_url`, `pnl_rate`, `realized_pnl` 추가.
     - `execute_paper_trade` 저장 프로시저를 개선하여 익절(+5%), 손절(-3%), 일반 매도 시에도 진입을 유발했던 뉴스 정보와 최종 확정 손익률(`pnl_rate`)을 누락 없이 보존.
  2. **n8n 파이프라인 연계**:
     - `paper-trade-execute-swallow` 노드에서 뉴스 제목(`$json.title`)과 원문 링크(`$json.link`)를 프로시저 파라미터로 자동 전달.
  3. **MCP Tool 12 (`swallow_news_impact`) 추가 및 기존 툴 고도화**:
     - `swallow_get_portfolio`: 포트폴리오 누적 수익/손실률(`%`) 및 보유 종목의 진입 뉴스 링크 표기.
     - `swallow_get_trades`: 체결 건별 실현 손익률(`%`) 및 원인 뉴스 칼럼 추가.
     - `swallow_news_impact`: 뉴스 발행 당시 주가 vs 현재 주가 비교, 주가 변동률(`%`), AI 적중 여부(적중/미적중/보합), 모의투자 매수/익절/손절 체결 결과 및 손익률을 포괄적으로 분석하는 신규 도구 등록.
  4. **Grafana 2-Tab 대시보드 분리 및 상단 네비게이션 연동**:
     - **Tab 1: `Swallow 종목 실시간 모니터링` (`swallow-stock-monitor`)**: 글로벌 매크로, 수집 상태, 실시간 시세, 교차검증, 피어 뉴스, 모의투자 성과 요약.
     - **Tab 2: `Swallow 뉴스 영향도 분석 (News Impact)` (`swallow-news-impact`)**: AI 예측 적중률(%), 호재/악재 분포, 모의투자 자산, **뉴스 이벤트 반응 & 주가 변동 추적(News Impact Tracker 전면 테이블)**, 보유 포지션 상세.
     - **상단 탭 바 (Dashboard Links)**: 두 대시보드 상단에 탭 버튼이 연동되어 종목 필터(`$ticker`) 및 시간 범위를 유지한 채 1클릭 전환.
     - `scripts/verify-swallow-queries.js` 다중 대시보드 검증 통과 (총 24/24 쿼리 100% 성공).

---

## 9. 관련 링크

---



- [[Work/Birds-Nest/index|Birds-Nest 인덱스]]
- [[2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포|2026-10-09 — [Stock] Swallow 워크플로우 고도화 (단일 체인 개편 및 NAS n8n 배포)]]
