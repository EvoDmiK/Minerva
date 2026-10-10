---
created: 2026-10-09
updated: 2026-10-10
project: Gullinkambi
type: backlog
tags:
  - gullinkambi
  - backlog
  - monitoring
  - grafana
---

# Gullinkambi 작업 백로그

Grafana와 Prometheus를 중심으로 홈랩 서비스·인프라·AI 모델 사용량을 관찰하고 추적하는 모니터링 프로젝트의 작업 목록이다.
작업 진행 지시를 받은 뒤 착수하며, 작업별 목적·범위·완료 기준을 바탕으로 진행하고 완료 시 체크 표시와 검증 기록을 남긴다.

## 목차

- [[#작업 ID 체계|작업 ID 체계와 카테고리별 보기]]
- [[#작업 현황 대시보드|작업 현황 대시보드]]
- 작업 상세 — 카테고리별
  - 1xx 수집기·Exporter
    - [[#GK-101 — AI 구독 사용량 수집기와 Grafana 대시보드 구축|GK-101 — AI 구독 사용량 수집기와 Grafana 대시보드 구축]] · 완료
    - [[#GK-102 — NPM 모니터링 수집기와 Cloudflare Origin 인증서|GK-102 — NPM 모니터링 수집기와 Cloudflare Origin 인증서]] · 완료
    - [[#GK-103 — Claude 사용량 계정 전체 수집과 서비스 모니터링 개편|GK-103 — Claude 사용량 계정 전체 수집과 서비스 모니터링 개편]] · 완료
    - [[#GK-104 — ORCA SSD 이전 후 사용량 수집 복구|GK-104 — ORCA SSD 이전 후 사용량 수집 복구]] · 완료
    - [[#GK-105 — Antigravity 구독 사용량 수집 복구|GK-105 — Antigravity 구독 사용량 수집 복구]] · 완료
    - [[#GK-106 — ORCA 개발 세션 토큰·성과 수집기 (1차 필수 구현)|GK-106 — ORCA 개발 세션 토큰·성과 수집기 (1차 필수 구현)]] · 착수 대기
  - 2xx Grafana 대시보드·패널
    - [[#GK-201 — Claude·Antigravity 초기화 패널 5시간·주간 통합|GK-201 — Claude·Antigravity 초기화 패널 5시간·주간 통합]] · 완료
    - [[#GK-202 — OpenViking 탭 개선과 Hermes Grafana MCP 연결|GK-202 — OpenViking 탭 개선과 Hermes Grafana MCP 연결]] · 완료
    - [[#GK-203 — Aviary Control Room 대시보드에 ORCA 쓰레드별 패널 추가|GK-203 — Aviary Control Room 대시보드에 ORCA 쓰레드별 패널 추가]] · 착수 대기
  - 3xx 알림·Discord 연동
    - [[#GK-301 — Grafana 알람과 Discord 연결|GK-301 — Grafana 알람과 Discord 연결]] · 완료
    - [[#GK-302 — Grafana Discord 알림 단일 카드 개선|GK-302 — Grafana Discord 알림 단일 카드 개선]] · 완료
    - [[#GK-303 — GitHub 커밋 작성자 이상 및 잔디 누락 감시 알림 구축|GK-303 — GitHub 커밋 작성자 이상 및 잔디 누락 감시 알림 구축]] · 착수 대기
  - 4xx 네트워킹·인증서·DNS
    - [[#GK-401 — Tailscale Split DNS와 와일드카드 인증서 구축|GK-401 — Tailscale Split DNS와 와일드카드 인증서 구축]] · 완료
  - 5xx AI 사용량 분석·성능 진단
    - [[#GK-501 — ORCA Antigravity 사용량 집계와 Hermes 인증 복구|GK-501 — ORCA Antigravity 사용량 집계와 Hermes 인증 복구]] · 완료
    - [[#GK-502 — ORCA 쓰레드 이름 복구와 Birds-Nest 브랜치 정리|GK-502 — ORCA 쓰레드 이름 복구와 Birds-Nest 브랜치 정리]] · 완료
    - [[#GK-503 — Claude 사용량 캐시 회귀 원인 진단|GK-503 — Claude 사용량 캐시 회귀 원인 진단]] · 완료
    - [[#GK-504 — ORCA 쓰레드별 토큰 사용량 검증|GK-504 — ORCA 쓰레드별 토큰 사용량 검증]] · 완료
    - [[#GK-505 — ORCA 최근 7일 토큰 사용량 검증|GK-505 — ORCA 최근 7일 토큰 사용량 검증]] · 완료
    - [[#GK-506 — Gemini 세션 주간 사용률 차이 진단|GK-506 — Gemini 세션 주간 사용률 차이 진단]] · 완료
    - [[#GK-507 — RobinGraph ORCA 전체기간 토큰 사용량 검증|GK-507 — RobinGraph ORCA 전체기간 토큰 사용량 검증]] · 완료
  - 6xx MLflow 연동·Run Tracing
    - [[#GK-601 — MLflow Tracing 연동 및 Run 추적 검증|GK-601 — MLflow Tracing 연동 및 Run 추적 검증]] · 착수 대기
  - 8xx 문서·기획 명세
    - [[#GK-801 — AI subscription exporter README 작성|GK-801 — AI subscription exporter README 작성]] · 완료
    - [[#GK-802 — ORCA 개발 사용량·성과 Grafana/MLflow 작업 명세 v2 작성|GK-802 — ORCA 개발 사용량·성과 Grafana/MLflow 작업 명세 v2 작성]] · 완료
- 상태별 본문 섹션
  - [[#신규 착수 대기 작업|신규 착수 대기 작업]]
  - [[#완료 작업 상세 (검증 이력 보존)|완료 작업 상세 (검증 이력 보존)]]
- [[#관련 문서 및 링크|관련 문서 및 링크]]

---

## 작업 ID 체계

작업 ID는 카테고리 번호로 매긴다. **첫 자리가 카테고리, 뒤 두 자리가 순번**이다 (`GK-101`, `GK-201` 등).

| 카테고리 | 범위 | 예시 |
|---|---|---|
| **1xx 수집기·Exporter** | Python exporter, 수집 데몬, CLI 로그 파서 | AI subscription exporter, ORCA telemetry |
| **2xx Grafana 대시보드·패널** | 대시보드 JSON, 패널 쿼리, 시각화 | Aviary Control Room, 초기화 패널, 게이지 |
| **3xx 알림·Discord 연동** | 알람 룰, Contact Points, 웹훅 카드 포맷 | Discord 알림, 단일 카드 포맷, 잔디 경고 |
| **4xx 네트워킹·인증서·DNS** | Tailscale, Split DNS, Cloudflare, TLS | 와일드카드 인증서, Origin 프록시 |
| **5xx AI 사용량 분석·진단** | 캐시 적중률, 토큰 집계, 회귀 진단 | Claude 캐시 회귀, 쓰레드별 사용량 분석 |
| **6xx MLflow 연동·Run Tracing** | Tracing, Run 생성, Artifact 연동 | MLflow Tracking, SDK 연동 |
| **7xx 인프라·시계열 DB** | Prometheus, TimescaleDB, 보존 정책 | 하이퍼테이블, 연속 집계 뷰 |
| **8xx 문서·기획 명세** | README, 구현 명세서, 가이드 | 작업 명세, 운영 가이드 |

---

## 작업 현황 대시보드

| ID | 작업명 | 카테고리 | 상태 | 우선순위 | 검증/결과 문서 |
|---|---|---|---|---|---|
| **GK-101** | AI 구독 사용량 수집기와 Grafana 대시보드 구축 | 1xx 수집기 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축\|기록]] |
| **GK-102** | NPM 모니터링 수집기와 Cloudflare Origin 인증서 | 1xx 수집기 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-02-NPM-모니터링-수집기와-Cloudflare-Origin-인증서\|기록]] |
| **GK-103** | Claude 사용량 계정 전체 수집과 서비스 모니터링 개편 | 1xx 수집기 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-03-Claude-사용량-계정-전체-수집과-서비스-모니터링-개편\|기록]] |
| **GK-104** | ORCA SSD 이전 후 사용량 수집 복구 | 1xx 수집기 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-08-ORCA-SSD-이전-후-사용량-수집-복구\|기록]] |
| **GK-105** | Antigravity 구독 사용량 수집 복구 | 1xx 수집기 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-08-Antigravity-구독-사용량-수집-복구\|기록]] |
| **GK-106** | ORCA 개발 세션 토큰·성과 수집기 (1차 필수 구현) | 1xx 수집기 | ✅ 완료 (Antigravity 도구 호출 제외) | — | [[Work/Gullinkambi/작업기록/2026-10-10-ORCA-호출별-관측-구현과-운영-반영\|기록]] · [[Work/Gullinkambi/2026-10-09-ORCA-Grafana-MLflow-Claude-작업명세\|명세서 v2]] |
| **GK-201** | Claude·Antigravity 초기화 패널 5시간·주간 통합 | 2xx 대시보드 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-05-Claude-Antigravity-초기화-패널-5시간·주간-통합\|기록]] |
| **GK-202** | OpenViking 탭 개선과 Hermes Grafana MCP 연결 | 2xx 대시보드 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-06-OpenViking-탭-개선과-Hermes-Grafana-MCP-연결\|기록]] |
| **GK-203** | Aviary Control Room 대시보드에 ORCA 쓰레드별 패널 추가 | 2xx 대시보드 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-10-ORCA-호출별-관측-구현과-운영-반영\|기록]] · [[Dev/관측성/LLM-토큰-사용량-및-관측성-파이프라인-설계\|패턴 가이드]] |
| **GK-301** | Grafana 알람과 Discord 연결 | 3xx 알림 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-01-Grafana-알람과-Discord-연결\|기록]] |
| **GK-302** | Grafana Discord 알림 단일 카드 개선 | 3xx 알림 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-02-Grafana-Discord-알림-단일-카드-개선\|기록]] |
| **GK-303** | GitHub 커밋 작성자 이상 및 잔디 누락 감시 알림 구축 | 3xx 알림 | ⏳ 착수 대기 | 높음 | — |
| **GK-401** | Tailscale Split DNS와 와일드카드 인증서 구축 | 4xx 네트워킹 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-02-Tailscale-Split-DNS와-와일드카드-인증서\|기록]] |
| **GK-501** | ORCA Antigravity 사용량 집계와 Hermes 인증 복구 | 5xx 분석진단 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구\|기록]] |
| **GK-502** | ORCA 쓰레드 이름 복구와 Birds-Nest 브랜치 정리 | 5xx 분석진단 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-02-ORCA-쓰레드-이름-복구와-Birds-Nest-브랜치-정리\|기록]] |
| **GK-503** | Claude 사용량 캐시 회귀 원인 진단 | 5xx 분석진단 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-07-Claude-사용량-캐시-회귀-진단\|기록]] |
| **GK-504** | ORCA 쓰레드별 토큰 사용량 검증 | 5xx 분석진단 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-쓰레드별-토큰-사용량-검증\|기록]] |
| **GK-505** | ORCA 최근 7일 토큰 사용량 검증 | 5xx 분석진단 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-최근7일-토큰-사용량-검증\|기록]] |
| **GK-506** | Gemini 세션 주간 사용률 차이 진단 | 5xx 분석진단 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-08-Gemini-세션-주간-사용률-차이-진단\|기록]] |
| **GK-507** | RobinGraph ORCA 전체기간 토큰 사용량 검증 | 5xx 분석진단 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-08-RobinGraph-ORCA-전체기간-토큰-사용량-검증\|기록]] |
| **GK-601** | MLflow Tracing 연동 및 Run 추적 검증 | 6xx MLflow | 🔄 부분 완료 (Run 생성·내부 URL 전환 완료, 공개 라우트 보호 미완) | 보통 | [[Work/Gullinkambi/작업기록/2026-10-10-ORCA-호출별-관측-구현과-운영-반영\|기록]] · [[Work/Gullinkambi/2026-10-09-ORCA-Grafana-MLflow-Claude-작업명세\|명세서 v2]] |
| **GK-801** | AI subscription exporter README 작성 | 8xx 문서 | ✅ 완료 | — | [[Work/Gullinkambi/작업기록/2026-10-03-AI-subscription-exporter-README\|기록]] |
| **GK-802** | ORCA 개발 사용량·성과 Grafana/MLflow 작업 명세 v2 작성 | 8xx 문서 | ✅ 완료 | — | [[Work/Gullinkambi/2026-10-09-ORCA-Grafana-MLflow-Claude-작업명세\|명세서 v2]] |

---

## 신규 착수 대기 작업

### GK-106 — ORCA 개발 세션 토큰·성과 수집기 (1차 필수 구현)
- **목적**: ORCA에서 Codex·Claude 등을 사용한 개발 작업을 호출별 privacy-safe 메타데이터 수집, 제공자별 토큰 정규화, n8n ingest 연동으로 추적한다.
- **범위**: 
  - `docker-compose/agents/hermes-telemetry/collector.py` 확장
  - 세션별 `uncached_prompt_tokens`, `cache_read_tokens`, `cache_write_tokens`, `output_tokens` 정규화
  - n8n ingest 및 TimescaleDB 적재
- **완료 기준**: ORCA 세션 실행 시 TimescaleDB에 토큰 이벤트가 누락 없이 기록됨.
- **참조 문서**: [[Work/Gullinkambi/2026-10-09-ORCA-Grafana-MLflow-Claude-작업명세|작업 명세 v2]]

### GK-303 — GitHub 커밋 작성자 이상 및 잔디 누락 감시 알림 구축
- **목적**: 모바일 또는 신규 환경에서 커밋이 `@local`이나 등록되지 않은 이메일로 push될 경우 즉시 Discord 알림을 보내 잔디 누락을 조기 감지한다.
- **완료 기준**: `@local` 커밋 push 시 1분 내 Discord 알림 도착.

### GK-601 — MLflow Tracing 연동 및 Run 추적 검증
- **목적**: `https://mlflow.dove-nest.com` 서버에 Tracing 및 Run 생성 가능 여부를 실측 검증하고 인증/SDK 권한을 확인한다.
- **완료 기준**: 테스트 스크립트에서 MLflow HTTP 200 및 Run 생성 확인.

---

## 완료 작업 상세 (검증 이력 보존)

* **GK-106 · GK-203 (2026-10-10)**: ORCA 호출별 관측 구현·운영 반영(수집→n8n→TimescaleDB→Grafana 패널, 도구 호출 집계). 남은 일: Antigravity 도구 호출. [[Work/Gullinkambi/작업기록/2026-10-10-ORCA-호출별-관측-구현과-운영-반영|상세 기록]].
* **GK-601 부분 완료 (2026-10-10)**: MLflow Run 자동 생성 확인. 남은 일: 공개 라우트 인증 보호, DB 비밀번호 로테이션. [[Work/Gullinkambi/작업기록/2026-10-10-ORCA-호출별-관측-구현과-운영-반영|상세 기록]].
* **GK-802 (2026-10-09)**: ORCA 개발 사용량·성과 추적 Grafana/MLflow 작업 명세 v2 작성. [[Work/Gullinkambi/2026-10-09-ORCA-Grafana-MLflow-Claude-작업명세|명세서 v2]].
* **GK-105 (2026-10-08)**: Antigravity 구독 사용량 수집 복구. [[Work/Gullinkambi/작업기록/2026-10-08-Antigravity-구독-사용량-수집-복구|상세 기록]].
* **GK-506 (2026-10-08)**: Gemini 세션 주간 사용률 차이 진단. [[Work/Gullinkambi/작업기록/2026-10-08-Gemini-세션-주간-사용률-차이-진단|상세 기록]].
* **GK-104 (2026-10-08)**: ORCA SSD 이전 후 사용량 수집 복구. [[Work/Gullinkambi/작업기록/2026-10-08-ORCA-SSD-이전-후-사용량-수집-복구|상세 기록]].
* **GK-507 (2026-10-08)**: RobinGraph ORCA 전체기간 토큰 사용량 검증. [[Work/Gullinkambi/작업기록/2026-10-08-RobinGraph-ORCA-전체기간-토큰-사용량-검증|상세 기록]].
* **GK-503 (2026-10-07)**: Claude 사용량 캐시 회귀 원인 진단. [[Work/Gullinkambi/작업기록/2026-10-07-Claude-사용량-캐시-회귀-진단|상세 기록]].
* **GK-504 (2026-10-07)**: ORCA 쓰레드별 토큰 사용량 검증. [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-쓰레드별-토큰-사용량-검증|상세 기록]].
* **GK-505 (2026-10-07)**: ORCA 최근 7일 토큰 사용량 검증. [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-최근7일-토큰-사용량-검증|상세 기록]].
* **GK-202 (2026-10-06)**: OpenViking 탭 개선과 Hermes Grafana MCP 연결. [[Work/Gullinkambi/작업기록/2026-10-06-OpenViking-탭-개선과-Hermes-Grafana-MCP-연결|상세 기록]].
* **GK-201 (2026-10-05)**: Claude·Antigravity 초기화 패널 5시간·주간 통합. [[Work/Gullinkambi/작업기록/2026-10-05-Claude-Antigravity-초기화-패널-5시간·주간-통합|상세 기록]].
* **GK-103 (2026-10-03)**: Claude 사용량 계정 전체 수집과 서비스 모니터링 개편. [[Work/Gullinkambi/작업기록/2026-10-03-Claude-사용량-계정-전체-수집과-서비스-모니터링-개편|상세 기록]].
* **GK-801 (2026-10-03)**: AI subscription exporter README 작성. [[Work/Gullinkambi/작업기록/2026-10-03-AI-subscription-exporter-README|상세 기록]].
* **GK-401 (2026-10-02)**: Tailscale Split DNS와 와일드카드 인증서 구축. [[Work/Gullinkambi/작업기록/2026-10-02-Tailscale-Split-DNS와-와일드카드-인증서|상세 기록]].
* **GK-502 (2026-10-02)**: ORCA 쓰레드 이름 복구와 Birds-Nest 브랜치 정리. [[Work/Gullinkambi/작업기록/2026-10-02-ORCA-쓰레드-이름-복구와-Birds-Nest-브랜치-정리|상세 기록]].
* **GK-102 (2026-10-02)**: NPM 모니터링 수집기와 Cloudflare Origin 인증서. [[Work/Gullinkambi/작업기록/2026-10-02-NPM-모니터링-수집기와-Cloudflare-Origin-인증서|상세 기록]].
* **GK-302 (2026-10-02)**: Grafana Discord 알림 단일 카드 개선. [[Work/Gullinkambi/작업기록/2026-10-02-Grafana-Discord-알림-단일-카드-개선|상세 기록]].
* **GK-501 (2026-10-01)**: ORCA Antigravity 사용량 집계와 Hermes 인증 복구. [[Work/Gullinkambi/작업기록/2026-10-01-ORCA-Antigravity-사용량-집계와-Hermes-인증-복구|상세 기록]].
* **GK-301 (2026-10-01)**: Grafana 알람과 Discord 연결. [[Work/Gullinkambi/작업기록/2026-10-01-Grafana-알람과-Discord-연결|상세 기록]].
* **GK-101 (2026-10-01)**: AI 구독 사용량 수집기와 Grafana 대시보드 구축. [[Work/Gullinkambi/작업기록/2026-10-01-AI-구독-사용량-수집기와-Grafana-대시보드-구축|상세 기록]].

---

## 관련 문서 및 링크

- [[Work/Gullinkambi/index|Gullinkambi 인덱스]]
- [[Work/index|Work 전체 인덱스]]
- [[Work/RobinGraph/RobinGraph 작업 백로그|RobinGraph 작업 백로그]]
- [[Work/Birds-Nest/Birds-Nest 작업 백로그|Birds-Nest 작업 백로그]]
- [[Dev/index|Dev 인덱스]]
