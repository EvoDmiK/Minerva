---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Swallow/2026-10-13-Swallow-거래량-수집-및-표시-수정]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# [SW-013] Swallow 거래량 수집 및 표시 수정

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Swallow/2026-10-13-Swallow-거래량-수집-및-표시-수정]] · 분류 근거 {"인프라":1,"자동화":12,"관측성":9,"데이터":1}

## 1. 개요 및 목적

한화 종목 모니터링 점검 후 거래량 패널이 비어 있다는 사용자 보고로 확인했다. 가격 수집은 정상이나 최근1시간 stock_price_history.volume은 모든 종목/소스에서NULL이었다. 현재 Toss quote/Naver basic 응답에는 거래량 필드가 없고 수집기/적재 SQL도 volume을 쓰지 않았다.

네이버 integration의 totalInfos.accumulatedTradingVolume을 사용해 당일 누적 거래량을 저장하도록 구현했다. Grafana 패널4는 네이버 당일 누적 거래량임을 명시하고 가격 source 필터와 독립적으로 조회하며 쉼표 전체 숫자로 표시한다. 구현·개발 통합 검증 완료, 운영 수집기/대시보드 적용은 별도 승인 대기다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 원인 및 설계
- 2. 구현
- 3. 검증
- 4. 형상 및 적용·복구
- 5. 한계
- 관련 문서
- 2026-10-13 기업명 범례 추가 및 main 머지
- 2026-10-13 거래량 수집기 운영 배포 및 검증 완료

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

한화 종목 모니터링 점검 후 거래량 패널이 비어 있다는 사용자 보고로 확인했다. 가격 수집은 정상이나 최근1시간 stock_price_history.volume은 모든 종목/소스에서NULL이었다. 현재 Toss quote/Naver basic 응답에는 거래량 필드가 없고 수집기/적재 SQL도 volume을 쓰지 않았다.

네이버 integration의 totalInfos.accumulatedTradingVolume을 사용해 당일 누적 거래량을 저장하도록 구현했다. Grafana 패널4는 네이버 당일 누적 거래량임을 명시하고 가격 source 필터와 독립적으로 조회하며 쉼표 전체 숫자로 표시한다. 구현·개발 통합 검증 완료, 운영 수집기/대시보드 적용은 별도 승인 대기다.

| 구분 | 결과 |
|---|---|
| 백엔드 | 22→24노드, 거래량 조회/병합2노드 추가. 기존volume BIGINT 컬럼 재사용, schema migration 불필요 |
| 거래량 계약 | 네이버 당일 누적 거래량(분당 거래량 아님). itemCode로 연결, basic 체결일과snapshot의KST날짜가 일치할 때만 저장 |
| 실패 처리 | 없거나 잘못된 값/전일·휴장자료는NULL, 실제0유지. 거래량실패시가격수집은유지. Upsert NULL이 기존volume을지우지않음 |
| Grafana | panel4 source=naver 고정, ticker/기간 필터 유지, NULL제외, 선그래프 및 locale/decimals0로 축약 없는 숫자 |
| 검증 | Node52pass, 실제 Naver API read-only 응답 정규화(담당검증), root격리n8n2success 및 SQL5queries PASS |
| 운영 | 아직 미적용. 현재 운영22노드/기존panel4. 보호된 workflow 백업준비 완료 |

운영 최근1시간 volume 전부NULL을 직접조회하고 실행30280의 공급자원본응답에 거래량필드없음을 확인했다. 공개 네이버 integration 응답의 accumulatedTradingVolume 실제 값 확인. 새의존성/테이블 없이 기존시세 이력에저장한다. 토스거래량은근거없으므로NULL을유지하고 과거누락이력을소급하여꾸미지않는다.

- n8n/Swallow/watchlist-prices.json: 네이버 거래량조회/병합2개추가, Merge3입력대기, itemCode매핑, 정수/숫자·비음수검증, 기본 체결일에 근거한 전일누적값 배제, volume바인딩/upsert COALESCE.
- n8n/Swallow/tests/watchlist-prices.test.mjs: volume정상/누락/0/음수·비정수/중복/순서/자정리셋/실패 검증.
- grafana/swallow/Swallow-Stock-Monitor.json: panel4만 변경. 가격source독립 네이버누적조회, NULL제외, 제목/설명/단위/선그래프정정.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Swallow/2026-10-13-Swallow-거래량-수집-및-표시-수정]]
- [[Dev/index|Dev 인덱스]]
