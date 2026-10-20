---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-시장지표-수집-및-가격표시-수정]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# Swallow 시장 지표 수집 및 가격 표시 수정

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-시장지표-수집-및-가격표시-수정]] · 분류 근거 {"인프라":0,"자동화":4,"관측성":12,"데이터":2}

## 1. 개요 및 목적

- 작업: SW-012
- 사용자 요청: KOSPI·KOSDAQ·환율 표시 복구, 가격에 K/M 축약 대신 천 단위 쉼표 적용.
- 담당: dev-claude 백엔드, dev-agy Grafana, dev-docs 문서, dev-codex 리뷰·통합·배포·검증.
- 코드: 백엔드 `053cb4ce4892b08e764c99f54473d64b88f66925`, Grafana `ce82f6e65b4430193ee1aaf7af3f115bcd623485`, 통합 `787f101892094e42cc3b2d370b4db25db13dd723`.
- [Draft PR #5](https://github.com/EvoDmiK/Birds-Nest/pull/5). main 최종 머지는 사용자 담당.

세 시장 지표는 DB 최신값과 시계열이 2026-10-10 18:58:43 KST 이후 갱신되지 않았다. 네이버 원본 응답은 정상이었으며 기존 대시보드 SQL 21개도 정상 실행됐다. 정기 지표 수집 경로가 없던 문제와 숫자 포맷 문제가 함께 있었다.

## 2. 핵심 아키텍처 및 원칙

- 원인과 변경
- 실제 검증
- 운영 설정과 복구
- 남은 범위
- 연결
- 최종 문서·통합 상태

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- 작업: SW-012
- 사용자 요청: KOSPI·KOSDAQ·환율 표시 복구, 가격에 K/M 축약 대신 천 단위 쉼표 적용.
- 담당: dev-claude 백엔드, dev-agy Grafana, dev-docs 문서, dev-codex 리뷰·통합·배포·검증.
- 코드: 백엔드 `053cb4ce4892b08e764c99f54473d64b88f66925`, Grafana `ce82f6e65b4430193ee1aaf7af3f115bcd623485`, 통합 `787f101892094e42cc3b2d370b4db25db13dd723`.
- [Draft PR #5](https://github.com/EvoDmiK/Birds-Nest/pull/5). main 최종 머지는 사용자 담당.

기존 workflow `Kt26XhwQEO2SuRtt`에 매크로 6개 노드를 추가해 총 22노드로 배포했다. 기존 장운영 달력과 캐시, 장중 1분·장외/휴장 5분 게이트를 그대로 재사용한다. 네이버 KOSPI/KOSDAQ/FX 응답 심볼과 유한 양수 가격을 검증하고, 최신값 `market_macro_indicators`와 시계열 `stock_price_history`를 한 CTE로 upsert한다. 스냅샷 시각과 원본 거래시각·장상태는 구분한다.

- 계약 테스트 39 pass / 0 fail / 0 skip. 기존 30개와 매크로 9개.
- dev-claude가 임시 PostgreSQL에서 최초 적재·같은 스냅샷 replay·과거 replay 최신값 보호·빈 입력을 검증했다.
- 예약 실행 `28370`(11:28 KST), `28373`(11:29 KST) 연속 success, 마지막 노드 `매크로 실패 확인`.
- 각 실행: 매크로 최신값 updated 3, 이력 inserted 3, 종목 toss 2/naver 2 inserted, errors/failures=[].
- DB에서 각 분 7행과 지표별 숫자·하락 부호를 직접 대조했다.
- 실행 순서는 매크로 요약 → 관심종목 조회 → 종목 요약 → 매크로 실패 확인으로 관측했다.
- 배포 후 active=true, 22노드, Asia/Seoul, 당일 달력 캐시 보존 확인.
- Grafana 동기화 성공 lastRef `787f101`; 세 대시보드 버전 10/5/2 및 모든 fieldConfig가 Git 파일과 일치했다.
- 실제 브라우저: KOSPI `6,471.58` / `-2.33%`, 환율 `1,334.7` / `-0.69%`, SK하이닉스 `₩1,632,000`, 삼성전자 `₩256,500`, 시계열 범례도 전체 금액 표시.
- 모의투자 화면 총자산·예수금 `₩10,000,000`, 뉴스 화면 뉴스 당시 주가 `₩263,000` 확인.
- 수정 후에도 실제 PostgreSQL SQL 21개 모두 성공.

Grafana 설정에는 관리자 이름 admin이 남아 있었지만 실제 계정은 kimdove였다. 실제 이름으로 인증해 200을 확인했으며 비밀번호를 변경하지 않았다. 일반 대시보드 저장 API는 Git 관리 때문에 400 Cannot save provisioned dashboard를 반환했다. DB 직접 수정 없이 native Git Sync를 사용했다.

- 활성 관심종목이 0이면 후속 매크로 실패 확인이 실행되지 않는다. 매크로 수집·적재 자체는 수행된다.
- 종목 실패 확인에서 먼저 error가 나면 매크로 최종 확인은 미실행이지만 매크로 요약·적재는 앞서 완료된다.
- 장외·휴장 실제 시간대는 이번에도 미관측이며 fixture와 장중 실환경 검증을 구분한다.
- CNN 공포탐욕 지수는 이번 세 지표 수집 대상에 포함하지 않아 이전 값·수집 시각이 남는다. SW-008, 뉴스 적재 SW-009 및 전체 PR 범위의 필수 검증은 별도 미완료.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-시장지표-수집-및-가격표시-수정]]
- [[Dev/index|Dev 인덱스]]
