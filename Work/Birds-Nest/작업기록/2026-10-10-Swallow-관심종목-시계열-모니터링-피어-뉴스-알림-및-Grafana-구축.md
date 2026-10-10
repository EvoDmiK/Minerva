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
---

# 2026-10-10 — [Stock] Swallow 관심종목 시계열 모니터링, 토스·네이버 교차검증 및 Grafana 대시보드 구축

## 1. 개요 및 배경

- **목적**:
  1. 사용자가 원하는 종목(관심종목, Watchlist)을 등록하여 지속적으로 시계열 주가 데이터를 수집·모니터링.
  2. 관심종목 직접 뉴스뿐만 아니라 **유사/경쟁사/공급망(피어, Peer) 종목 뉴스** 발생 시 Gemini AI가 파급 효과를 분석하여 Discord 실시간 알림 발송.
  3. 시세 신뢰성을 극대화하기 위해 **토스증권 공식 Open API(OAuth2)**와 **네이버페이 증권**을 결합한 **이중 소스 교차검증(Cross-validation) 및 이상치 감지** 체계 구축.
  4. Grafana를 통해 관심종목의 시계열 주가 차트, 소스별 괴리율 게이지, 그리고 **차트 위 뉴스 이벤트 어노테이션(Annotation 마커)** 시각화 제공.
- **협업 방식**: Claude Code CLI(`claude -p`)와 Antigravity가 페어 프로그래밍으로 DDL 설계, MCP 도구 검토, n8n 연동을 공동 진행.

---

## 2. 데이터베이스 스키마 확장 (`mcp/swallow-mcp/schema.sql`)

NAS PostgreSQL `data` 데이터베이스에 3개 핵심 테이블 구축 완료:

1. **`stock_watchlist` (관심종목 관리)**:
   - `ticker` (PK, 6자리 코드), `company_name`, `market`, `is_active`, `note`, `added_at`
   - ETF·신규 상장 종목 등록의 유연성을 위해 `companies` 외래키(FK) 제약을 의도적으로 해제하고 애플리케이션 레벨에서 6자리 코드 검증.
2. **`stock_price_history` (시계열 주가 적재 & 교차검증)**:
   - 복합 PK: `(ticker, ts, source)` (토스 `'toss'`, 네이버 `'naver'` 분리 적재 및 멱등성 보장).
   - `close_price`, `open_price`, `high_price`, `low_price`, `change_amt`, `change_rate`, `volume`, `created_at`.
3. **`stock_news_alerts` (피어 뉴스 알림 & Grafana 어노테이션 소스)**:
   - `watch_ticker` (영향받는 내 관심종목), `news_ticker` (기사 주인공 종목), `relation_type` (`direct`, `peer`, `supply_chain`, `competitor`), `relation_reason` (AI 파급 영향 분석), `sentiment`, `importance` (1~5), `title`, `url`, `published_at`, `discord_sent_at`.
   - `UNIQUE (watch_ticker, url)`로 동일 기사의 중복 알림 원천 차단.

---

## 3. Swallow MCP 도구 확장 (총 10종 도구 체제)

[`mcp/swallow-mcp/index.js`](file:///Volumes/Dove-Nest-SSD/projects/Birds-Nest/mcp/swallow-mcp/index.js)에 신규 도구 3종 추가:

1. **`swallow_watchlist`**:
   - `action`: `list` (목록 조회), `add` (추가), `remove` (비활성화, 기존 시계열 보존).
   - 기업 마스터 자동 매핑 및 ETF용 `companyName` 직접 입력 지원.
2. **`swallow_get_price_history`**:
   - 종목별 일자별 종가 이력 조회.
   - `source: 'all'` 설정 시 토스증권과 네이버페이 종가를 대조하여 **괴리율(±0.5%) 및 이상치 교차검증 표** 리턴.
3. **`swallow_get_news_alerts`**:
   - 관심종목에 영향을 준 직접 뉴스 및 피어 뉴스 목록, AI 파급 영향 분석 브리핑.

---

## 4. Grafana 대시보드 프로비저닝 및 Gullinkambi 반영

- **실제 접속 URL**: [Swallow 관심종목 모니터링 & 피어 뉴스 대시보드](https://monitoring.dove-nest.com/d/swallow-stock-monitor) (폴더: `Swallow`)
- **데이터소스 등록**: Grafana의 기존 PostgreSQL 데이터소스(`데이터 DB`, uid: `efrgyfz5k7ldsb`, database: `data`)에 바인딩 완료.
- **대시보드 정의**: [`docker-data/monitoring/grafana/dashboards/swallow_stock_monitoring.json`](file:///Volumes/Dove-Nest-SSD/projects/Birds-Nest/docker-data/monitoring/grafana/dashboards/swallow_stock_monitoring.json)
  - `$ticker` 드롭다운 변수 (활성 관심종목 목록 자동 쿼리)
  - 시계열 주가 차트 (토스/네이버 라인 비교)
  - 차트 위 **뉴스 어노테이션(Annotation)** 마커 (피어 뉴스 발생 시점 플래그)
  - 소스 간 실시간 괴리율 게이지
  - 실시간 피어 뉴스 타임라인 테이블
- **Gullinkambi 리포지토리 동기화**:
  - 홈랩 Grafana 프로비저닝 전용 리포지토리인 `Gullinkambi`의 `provisioning/dashboards/`에 `swallow.yml` 프로바이더 및 `swallow/swallow-stock-monitoring.json` 추가 완료 (`dev` 브랜치 커밋 & 푸시 완료).

---

## 5. 검증 결과

1. **Hermes MCP 컨테이너 연동**:
   - `hermes -p hybrid-v2 mcp test swallow_trader`: 10개 도구 정상 검색 (응답 220ms).
2. **실시간 시세 및 피어 알림 테스트**:
   - 삼성전자(`005930`), SK하이닉스(`000660`) 관심종목 등록 완료.
   - 네이버페이 실시간 시세 연동 및 토스 교차검증 테이블 정상 출력 확인.
   - 피어 뉴스 알림 쿼리 정상 작동 검증.

---

## 6. 관련 링크

- [[Work/Birds-Nest/index|Birds-Nest 인덱스]]
- [[Work/Birds-Nest/작업기록/2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포|2026-10-09 — [Stock] Swallow 워크플로우 고도화 (단일 체인 개편 및 NAS n8n 배포)]]
