---
created: 2026-10-11
updated: 2026-10-12
project: Birds-Nest
component: Swallow
type: component-index
tags: [birds-nest, swallow]
---

# Swallow 작업 문서

Swallow의 n8n 워크플로우, 주식·뉴스 DB, 모의투자, MCP 도구와 Grafana 대시보드 작업을 함께 관리한다.

## 작업 관리

- [[Work/Birds-Nest/작업기록/Swallow/Swallow 작업 백로그|Swallow 작업 백로그]] — 검토 항목과 관심종목 정기 수집의 최신 진행 상태·검증 결과.

## 기록

- [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-시장지표-수집-및-가격표시-수정|2026-10-12 Swallow 시장 지표 수집 및 가격 표시 수정]]

- [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-장중-장외-수집주기-조정|2026-10-12 Swallow 장중 1분·장외 5분 수집주기 조정]]


- [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-관심종목-지속-수집|2026-10-12 Swallow 관심종목 지속 수집]]


- [[Work/Birds-Nest/작업기록/Swallow/2026-10-10-Swallow-관심종목-시계열-모니터링-피어-뉴스-알림-및-Grafana-구축|2026-10-10-Swallow-관심종목-시계열-모니터링-피어-뉴스-알림-및-Grafana-구축]]
- [[Work/Birds-Nest/작업기록/Swallow/2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포|2026-10-09-Stock-Swallow-워크플로우-고도화-단일-체인-개편-및-NAS-n8n-배포]]

## 기록 규칙

Swallow 관련 신규 문서는 이 폴더에 `YYYY-MM-DD-Swallow-작업명.md`로 기록하고, SW 작업 ID와 검증 결과를 연결한다. 과거 기록은 당시 상태이며 현재 수정·검증 완료의 근거로 대신 사용하지 않는다.

- [[Work/Birds-Nest/작업기록/index|전체 작업기록 분류]]
- [[Work/Birds-Nest/index|Birds-Nest 프로젝트]]

- [[Work/Birds-Nest/작업기록/Swallow/2026-10-12-Swallow-뉴스-적재-및-평가-백로그-구현|뉴스 적재 및 평가 백로그 구현]] — SW-001/002/004/005/006/007/009 구현·개발 검증 완료, 운영 승인 대기. 최종 84ff835.

- [[Work/Birds-Nest/작업기록/Swallow/2026-10-13-Swallow-거래량-수집-및-표시-수정|2026-10-13 거래량 수집 및 표시 수정 (SW-013, 개발검증 완료·운영 반영 대기)]]

- 2026-10-13 SW-013 거래량 운영배포 및 검증 완료: [[Work/Birds-Nest/작업기록/Swallow/2026-10-13-Swallow-거래량-수집-및-표시-수정|거래량 수집 및 표시 수정]]. PR7 main4f16b69, 24노드 active, 30393/30398 예약 성공과 실제Grafana누적선그래프확인. 앞의배포대기상태갱신.

- [[Work/Birds-Nest/작업기록/Swallow/2026-10-20-Swallow-CNN-공포탐욕지수-수집-중단-진단-및-수정|2026-10-20 Swallow CNN 공포·탐욕 지수 수집 중단 진단 및 수정 (SW-008/SW-003, 운영 수집기 `5mkkZfHRh1zFGuZZ` 배포·첫 실행 `44008`·DB `23` 검증 완료, Grafana UI 확인 대기)]]

- [[Work/Birds-Nest/작업기록/Swallow/2026-10-21-Swallow-모의투자-보유종목-시세갱신-수정|2026-10-21 Swallow 모의투자 보유 종목 시세(평가가격) 갱신 수정 (SW-014, 구현 `9fb5df3`·통합 `850da6a`, root 테스트 72건 중 71 pass/0 fail/1 skip, 격리 n8n-test 노드 검증 PASS(`positionsUpdated = 5`)·운영 미배포)]]
