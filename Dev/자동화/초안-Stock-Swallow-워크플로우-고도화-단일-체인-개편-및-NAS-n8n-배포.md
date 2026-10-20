---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Swallow/2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# [Stock] Swallow 워크플로우 활성화 및 고도화 (단일 체인 개편, DB 캐싱, 실시간 시세 연동, Discord 발송)

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Swallow/2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포]] · 분류 근거 {"인프라":1,"자동화":17,"관측성":6,"데이터":6}

## 1. 개요 및 목적

미완성 및 비활성 상태(`active: false`, 32개 레거시 노드)로 방치되어 있던 Birds-Nest의 주식 파이프라인 워크플로우 **`[Stock] Swallow` (`smy9xPoHICCO69JF`)**를 전면 개편하여 활성화하고, NAS 운영 n8n 환경에 배포·검증을 완료했다.

기존의 비효율적인 3개 병렬 LLM 체인(Chain A/B/C) 구조와 DB 스키마 불일치(존재하지 않는 `instruments`/`listings` 조인 쿼리), 데이터 유실 버그(종목 분리 시 기사 메타데이터 증발), 종점 누락(토스 시세 조회 후 알림 노드 부재) 문제를 해결했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 완료 결과
- 1. 개편 배경 및 문제점 분석
- 기존 Swallow 워크플로우의 한계
- 2. 주요 개선 및 구현 내용
- 2.1 단일 체인 One-Shot LLM Triage
- 2.2 PostgreSQL `data.companies` 실시간 캐시 및 공공데이터 자동 폴백
- 2.3 토스증권 Open API 현재가 조회 및 Discord Rich Embed 브리핑 카드 발송
- 2.4 자체 가상 모의투자(Paper Trading) 장부 및 포트폴리오 엔진 구현
- 3. 실서비스 검증 결과 (모의투자 체결 및 Discord Rich Embed 발송)
- 3.1 DB 체결 결과
- 3.2 Discord Embed 카드 실제 수신 내용 예시
- 3.3 Swallow Trader MCP 서버 구축 및 전역 등록 (`swallow_trader`)
- 3.4 Hermes Agent 연동 및 Discord #주가-분석 채널 활성화
- 4. 관련 링크

## 3. 재사용 가능한 코드 스니펫 / 설정

  ```sql
  SELECT $1::text AS primary_stock, c.ticker, c.market, c.company_name
  FROM (SELECT $1::text AS qname) q
  LEFT JOIN companies c ON c.company_name = q.qname
  LIMIT 1;
  ```

  ```sql
  INSERT INTO companies (company_name, ticker, market)
  SELECT $1, $2, $3
  WHERE NULLIF($2, '') IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM companies WHERE ticker = $2)
  RETURNING company_id, ticker, market, company_name;
  ```

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

## 4. 검증 근거 및 트러블슈팅

미완성 및 비활성 상태(`active: false`, 32개 레거시 노드)로 방치되어 있던 Birds-Nest의 주식 파이프라인 워크플로우 **`[Stock] Swallow` (`smy9xPoHICCO69JF`)**를 전면 개편하여 활성화하고, NAS 운영 n8n 환경에 배포·검증을 완료했다.

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

- **2026-10-09 추가 업데이트**: 사용자 지정 Discord 채널(`1557990303535865916`)로 발송 대상 채널 변경 및 배포 완료. 테스트 실행(`Execution ID: 25135`, 18초 만에 성공)을 통해 해당 채널로 실시간 증권 브리핑 카드 전송을 최종 확인.
## 1. 개편 배경 및 문제점 분석

- [[Work/Birds-Nest/index|Birds-Nest 인덱스]]
- [[2026-10-08-Carrier-Pigeon-Gmail-바로가기-404-오류-수정과-NAS-n8n-배포|2026-10-08 — Carrier Pigeon Gmail 바로가기 404 오류 수정과 NAS n8n 배포]]
- [[Dev/n8n-워크플로우-신뢰성-및-에러-복구-패턴|n8n 워크플로우 신뢰성 및 에러 복구 설계 패턴]]

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Swallow/2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포]]
- [[Dev/index|Dev 인덱스]]
