---
created: 2026-10-09
date: 2026-10-09
project: Birds-Nest
type: worklog
status: completed
tags:
  - birds-nest
  - n8n
  - stock
  - swallow
  - gemini
  - discord
  - nas
  - homelab
  - production
---

# [Stock] Swallow 워크플로우 활성화 및 고도화 (단일 체인 개편, DB 캐싱, 실시간 시세 연동, Discord 발송)

## 요약

미완성 및 비활성 상태(`active: false`, 32개 레거시 노드)로 방치되어 있던 Birds-Nest의 주식 파이프라인 워크플로우 **`[Stock] Swallow` (`smy9xPoHICCO69JF`)**를 전면 개편하여 활성화하고, NAS 운영 n8n 환경에 배포·검증을 완료했다.

기존의 비효율적인 3개 병렬 LLM 체인(Chain A/B/C) 구조와 DB 스키마 불일치(존재하지 않는 `instruments`/`listings` 조인 쿼리), 데이터 유실 버그(종목 분리 시 기사 메타데이터 증발), 종점 누락(토스 시세 조회 후 알림 노드 부재) 문제를 해결했다.

**Gemini 3.5 Flash One-Shot Triage 단일 체인**으로 통합하여 속도 3배 향상 및 API 비용을 대폭 절감하고, PostgreSQL `data.companies` 테이블 연동과 공공데이터포털 KRX 상장정보 API를 통한 자동 동적 캐싱, 토스증권 Open API 실시간 시세 연동, 그리고 Discord `#전서구` 채널로 실시간 증권 브리핑 카드를 전송하는 완전한 파이프라인을 완성했다.

## 완료 결과

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **LLM 구조 경량화** | 3-Chain 병렬 분할 ➔ 단일 One-Shot Triage | 기사당 3회 호출하던 체인을 1회 단일 체인으로 통합(호출수 67% 절감, 토큰/비용 최적화, 속도 3배 향상) |
| **트리거 확장** | 수동 트리거만 존재 ➔ 3개 다중 진입점 구축 | 평일 08:30 KST Schedule Trigger, Webhook Trigger(`/webhook/swallow`), 수동 실행 트리거 지원 |
| **DB 스키마 정렬** | 가상 스키마 제거 ➔ 실제 `data.companies` 연동 | 미존재 테이블(`instruments`, `listings`) 쿼리를 `data.companies` 실 스키마에 맞춰 단일 쿼리로 정렬 |
| **동적 종목 캐싱** | 공공데이터포털 KRX API 자동 Fallback | DB 캐시 미스 시 공공데이터포털 API로 단축코드·시장 조회 후 `companies` 테이블에 자동 upsert 및 영구 캐싱 |
| **실시간 시세 조회** | 토스증권 Open API(`/api/v1/prices`) 결합 | 종목 티커 기준 실시간 현재가, 등락률, 변동폭 조회 및 장애 대응(`continueOnFail`) 구축 |
| **Discord 브리핑 발송** | 종점 부재 ➔ Discord 마크다운 브리핑 카드 전송 | 관련 종목, 현재가, 섹터, 투자 시그널(목표/근거), 2줄 핵심 요약, 원문 링크 포함 카드 실시간 발송 |
| **NAS 운영 배포** | NAS n8n REST API 배포 및 Activate | 워크플로우 `smy9xPoHICCO69JF` unarchive 후 32개 노드 업로드 및 실시간 활성화(`active: true`) 완료 |
| **실서비스 검증** | 실시간 뉴스 수집 및 Discord 발송 검증 | 한경·매경 RSS 수집 후 삼성전기(`009150`), 현대지에프홀딩스(`005440`), S-Oil(`010950`) 등 실제 브리핑 정상 발송 확인 |
| **형상 관리** | Git 커밋 & 원격 저장소 푸시 | 커밋 `bd0c10c` 작성 후 `origin/dev-mac`으로 푸시 완료 |

---




- **2026-10-09 추가 업데이트**: 사용자 지정 Discord 채널(`1557990303535865916`)로 발송 대상 채널 변경 및 배포 완료. 테스트 실행(`Execution ID: 25135`, 18초 만에 성공)을 통해 해당 채널로 실시간 증권 브리핑 카드 전송을 최종 확인.
## 1. 개편 배경 및 문제점 분석

### 기존 Swallow 워크플로우의 한계
1. **과도한 LLM 호출 비용 및 레이트 리밋 위험**:
   - 기사 1건당 Chain A(종목/섹터), Chain B(요약/감정/리스크), Chain C(시그널/전략) 등 3개의 Gemini LLM 체인을 병렬 호출함.
   - 1회 실행 시 15~20건의 기사가 유입되면 45~60회의 API 호출이 발생해 속도 저하 및 Google API 레이트 리밋 유발.
2. **PostgreSQL 스키마 불일치**:
   - `companies` ➔ `instruments` ➔ `listings` 조인 쿼리를 수행했으나, 실제 홈랩 `data` DB에는 `companies` 단일 테이블만 존재함.
3. **데이터 컨텍스트 유실 버그**:
   - `회사 이름만 가져오기`(Split Out) 노드를 거치며 기사 원문의 제목, 링크, 요약, 시그널 등의 정보가 모두 날아가고 티커명만 남음.
4. **목적지 부재 (파이프라인 미완결)**:
   - `현재가 조회` 노드 이후 저장이나 Discord/Slack 발송 노드가 전혀 연결되어 있지 않아 실행해도 아무런 알림을 받지 못함.
5. **자동화 트리거 부재 및 비활성 방치**:
   - 스케줄 트리거 없이 수동 버튼만 존재했으며, NAS 운영 환경에서는 아카이브/비활성화 상태로 방치되어 있었음.

---

## 2. 주요 개선 및 구현 내용

### 2.1 단일 체인 One-Shot LLM Triage
기존 3개 체인을 하나의 고성능 프롬프트와 Structured JSON Schema로 통합:
- **모델**: `models/gemini-3.5-flash` (`LdFPhSxQOLqZfRfx`, Gemni API 키 프로덕션)
- **추출 항목**:
  - `primary_stock`: 기사의 핵심 상장 종목명 (KRX 정식 종목명)
  - `related_stocks`: 추가 연관 종목명 목록
  - `sector`: 관련 산업 섹터 배열
  - `summary`: 시장 관점의 핵심 1~2문장 요약
  - `sentiment`: 긍정 / 중립 / 부정
  - `signal_action`: 매수 / 매도 / 관망
  - `signal_reason`: 투자 시그널 제시 근거
  - `impact_score`: 주가 및 섹터 영향도 (1~5 정수)
  - `confidence`: 분석 신뢰도 (0.0~1.0)

### 2.2 PostgreSQL `data.companies` 실시간 캐시 및 공공데이터 자동 폴백
- **DB 캐시 조회**:
  ```sql
  SELECT $1::text AS primary_stock, c.ticker, c.market, c.company_name
  FROM (SELECT $1::text AS qname) q
  LEFT JOIN companies c ON c.company_name = q.qname
  LIMIT 1;
  ```
- **캐시 미스 시**: 공공데이터포털 KRX 상장종목 정보 API(`GetKrxListedInfoService`)를 호출하여 단축코드(`srtnCd`)와 시장(`mrktCtg`)을 파싱.
- **자동 upsert**:
  ```sql
  INSERT INTO companies (company_name, ticker, market)
  SELECT $1, $2, $3
  WHERE NULLIF($2, '') IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM companies WHERE ticker = $2)
  RETURNING company_id, ticker, market, company_name;
  ```
  검증 실행 중 `삼성전기(009150)`, `현대지에프홀딩스(005440)`, `S-Oil(010950)`, `KT&G(033780)` 등이 DB에 자동으로 적재 및 캐싱됨을 확인.

### 2.3 토스증권 Open API 현재가 조회 및 Discord Rich Embed 브리핑 카드 발송
- 토스증권 Open API(`/api/v1/prices`)를 통해 실시간 종가와 등락률을 조회하고, `continueOnFail: true`를 적용해 API 장애 시에도 안전하게 폴백.
- Grafana/Pigeon 카드 레이아웃을 벤치마킹하여 Discord **Rich Embed** 카드로 전면 개편:
  - **좌측 컬러 바**: 투자 시그널(매수: `🟢 0x2ECC71`, 매도: `🔴 0xE74C3C`, 관망: `🟡 0xF1C40F`, 중립: `0x3498DB`)에 따른 동적 색상 매핑.
  - **헤더 & 본문**: 종목명 및 티커 클릭 시 기사 링크 연결, `>>>` 인용구 블록 요약.
  - **인라인 필드**: 📊 현재가(등락률), 🎯 투자 시그널(영향도/신뢰도), 🏷️ 섹터.
  - **상세 필드**: 💡 시그널 분석 및 근거, 📰 출처 및 원문 링크.
  - **푸터 & 타임스탬프**: Birds-Nest 브랜딩 및 기사 작성 시각.
- 수신 채널을 사용자 지정 채널(`1557990303535865916`)로 적용.

### 2.4 자체 가상 모의투자(Paper Trading) 장부 및 포트폴리오 엔진 구현
- **배경**: 토스증권 Open API는 실거래 전용으로 별도의 샌드박스/모의투자 환경이 부재하므로, 실제 자금 손실 리스크 없이 AI 시그널 수익률을 검증할 수 있는 **PostgreSQL 기반 원자적 가상 모의투자 장부 엔진** 구축.
- **DB 테이블 및 스키마 (`data` 데이터베이스)**:
  - `paper_account`: 계좌 잔고(초기 시드 1,000만 원), 실현 손익 누적 관리 (`swallow-main`).
  - `paper_positions`: 종목별 보유 수량, 총 매수원금, 평균단가, 최근 시세.
  - `paper_trades`: 모든 매수/매도 주문의 체결 시각, 체결 단가, 수량, 실현 손익 및 시그널 근거 로그.
- **원자적 체결 프로시저 (`execute_paper_trade`)**:
  - `🟢 매수 & 신뢰도 >= 80%`: 예수금 확인 후 1주 가상 매수 체결, 분할 매수 시 평단가 및 수량 재계산.
  - `🔴 매도`: 보유 종목인 경우 보유 수량 전량 시장가 매도 청산, 실현 손익(`realized_pnl`, `pnl_rate`) 산출 후 예수금 회수.
  - `관망 / 기존 보유`: 보유 평가손익 및 평가수익률 실시간 계산 후 반환.
- **n8n 워크플로우 통합**:
  - `가상 모의투자 체결` (Postgres 노드) 및 `모의투자 결과 병합` (Code 노드) 추가.
  - `브리핑 카드 작성`에 `🎮 Swallow 모의투자 포트폴리오` 필드를 연동하여 체결 내역/보유 현황/잔여 예수금을 Discord 카드로 직관적 표시.

---

## 3. 실서비스 검증 결과 (모의투자 체결 및 Discord Rich Embed 발송)

실제 실행 결과(`Execution ID: 25197`, 18초 소요, 성공 완료), PostgreSQL DB 체결 및 Discord 지정 채널(`1557990303535865916`)에 정상 발송된 결과:

### 3.1 DB 체결 결과
- `paper_account`: 초기 10,000,000원 -> 삼성전기 1주 매수 후 잔여 예수금 `8,441,000원`
- `paper_positions`: `009150 (삼성전기)` 1주 보유, 평단가 `1,559,000원`
- `paper_trades`: `BUY` 1주 체결 (1,559,000원), 사유 기록 완료

### 3.2 Discord Embed 카드 실제 수신 내용 예시
```
🟢 [매수] 삼성전기 (009150) | KOSPI
“241층 구조대 오나요?”…고점서 36% 빠진 삼성전기, 증권가 전망은
>>> 삼성전기가 글로벌 대형 기업과 AI 서버용 MLCC 대규모 공급 계약을 체결하며...

📊 현재가: 1,559,000원
🎯 투자 시그널: 🟢 매수 (영향도: 3/5 • 신뢰도: 90%)
🏷️ 섹터: IT/인터넷, 반도체
🎮 Swallow 모의투자 포트폴리오: 
🟢 **1주 가상 매수 체결** (1,559,000원)
• 보유: **1주** (평단: 1,559,000원)
• 잔여 예수금: **8,441,000원**
💡 시그널 분석 및 근거: 고점 대비 36% 수준의 주가 조정이 진행된 상태에서, 고부가가치 AI 서버용 MLCC 수주 본격화로 실적 반등 모멘텀이 유효합니다.
📰 출처 및 원문: 매일경제 • [기사 바로가기](https://www.mk.co.kr/news/stock/12172221)
```

### 3.3 Swallow Trader MCP 서버 구축 및 전역 등록 (`swallow_trader`)
- **목적**: Antigravity, Mac mini Hermes, Claude 등 대화형 AI가 실시간으로 Swallow 모의투자 포트폴리오를 확인하고, 주문을 실행하며, 파이프라인을 트리거할 수 있는 Model Context Protocol (MCP) 서버 구현.
- **구현 위치**: `mcp/swallow-mcp/index.js` (Node.js `@modelcontextprotocol/sdk` 기반 Stdio 서버)
- **제공 도구 (Tools)**:
  1. `swallow_get_portfolio`: 총 평가자산, 예수금, 보유 종목, 평균단가, 실시간 평가손익 마크다운 테이블 리턴.
  2. `swallow_get_trades`: 체결 이력, 체결단가, 실현 손익 로그 조회 (`limit`, `ticker` 지원).
  3. `swallow_check_stock`: 특정 종목의 모의투자 보유 여부 및 개별 평가손익 조회.
  4. `swallow_order`: 가상 매수/매도 수동 주문 실행 (`execute_paper_trade` 연동).
  5. `swallow_trigger_pipeline`: n8n Swallow 웹훅 즉시 호출 및 비동기 실행.
- **전역 설정 등록**: `~/.gemini/config/mcp_config.json`에 `swallow_trader` 추가 완료 및 로컬 stdio 통신 검증 완료.

### 3.4 Hermes Agent 연동 및 Discord #주가-분석 채널 활성화
- **Hermes MCP 연동**:
  - `config/hermes/integrations.toml`에 `swallow_trader` (Stdio MCP 서버) 추가.
  - Hermes 컨트롤 플레인(`hermes-control-plane.py apply`)을 통해 `hybrid-v2` 프로필에 반영.
  - 컨테이너 내부 `hermes -p hybrid-v2 mcp test swallow_trader` 실행 결과: 5개 도구 정상 검색 및 통신(167ms) 확인.
- **Discord 채널 활성화**:
  - 신규 채널 `#주가-분석` (`1557998164970315786`)을 `config/hermes/profiles/hybrid-v2.toml`의 `allowed_channels` 및 `channel_prompts`에 등록.
  - 프롬프트: *"이 채널(#주가-분석)에서는 Swallow 모의투자 포트폴리오 조회, 종목별 주가 분석 및 매매 시그널을 확인하고 가상 주문을 수행한다."*
  - Hermes 컨테이너 재시작 후 정상 상주 확인 완료.

---

## 4. 관련 링크

- [[Work/Birds-Nest/index|Birds-Nest 인덱스]]
- [[Work/Birds-Nest/작업기록/2026-10-08-Carrier-Pigeon-Gmail-바로가기-404-오류-수정과-NAS-n8n-배포|2026-10-08 — Carrier Pigeon Gmail 바로가기 404 오류 수정과 NAS n8n 배포]]
- [[Dev/n8n-워크플로우-신뢰성-및-에러-복구-패턴|n8n 워크플로우 신뢰성 및 에러 복구 설계 패턴]]
