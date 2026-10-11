---
updated: 2026-10-11
type: moc
tags:
  - home
  - moc
  - index
---

# 🏠 Home — Minerva 지식 베이스

Dove-Nest의 중심 지식 베이스(MOC, Map of Content)입니다.  
엔지니어링 상록수 지식, 프로젝트 작업 기록, 개인 학습 및 자동화 파이프라인의 전체 진입점 역할을 합니다.

---

## 🗂️ 핵심 영역 (Domains)

| 영역 | MOC 인덱스 | 성격 및 주요 내용 |
|---|---|---|
| **Dev** | [[Dev/index|Dev — 개발 & 엔지니어링]] | 인프라, 자동화(n8n), AI 관측성, 지식그래프 등 재사용 가능한 상록수(Evergreen) 지식 (`DEV-1xx`~`DEV-4xx`) |
| **Work** | [[Work/index|Work — 프로젝트 & 작업기록]] | 토이 프로젝트 시계열 작업 일지, 기술 검증 로그, 운영 배포 기록 |
| **Learning** | [[Learning/index|Learning — 개인 학습 & 독서]] | 독서 요약, 기술 강의 정리, 논문 분석 (`학습노트/`, `원문/`, `변환검증/`) |
| **Inbox** | [[Inbox.md|Inbox — 임시 수집함]] | 빠르게 캡처한 미정리 아이디어, 메모, 웹 클리핑 임시 보관 |

---

## 🚀 활성 프로젝트 & 백로그 (Work)

각 프로젝트는 독립된 `작업기록/` 아카이브와 체계화된 작업 백로그(ID 체계)를 갖추고 있습니다.

* **[[Work/Birds-Nest/index|Birds-Nest]]** — 홈랩 인프라, n8n 자동화 파이프라인, 에이전트 게이트웨이 & MCP
  * 📋 [[Work/Birds-Nest/Birds-Nest 작업 백로그|Birds-Nest 작업 백로그]] (`BN-1xx` ~ `BN-8xx`)
* **[[Work/RobinGraph/index|RobinGraph]]** — 조류 지식 그래프, RAG, 계통 분류 탐색 및 프로덕션 웹 UI
  * 📋 [[Work/RobinGraph/RobinGraph 작업 백로그|RobinGraph 작업 백로그]] (`RG-1xx` ~ `RG-9xx`)
* **[[Work/Gullinkambi/index|Gullinkambi]]** — 시스템 모니터링, 메트릭 수집기, Grafana 대시보드 및 AI 사용량 분석
  * 📋 [[Work/Gullinkambi/Gullinkambi 작업 백로그|Gullinkambi 작업 백로그]] (`GK-1xx` ~ `GK-8xx`)
* **[[Work/Itzcuauhtli/index|Itzcuauhtli]]** — Minerva 볼트 안전 읽기 전용 Obsidian MCP 게이트웨이

---

## 📚 상록수 엔지니어링 지식 (Dev)

`Work/`에서 검증된 핵심 엔지니어링 패턴을 도메인별 하위 폴더와 ID 체계로 승격 관리합니다.

* **[[Dev/인프라/2026-10-02-홈랩-인증서·Cloudflare·접속-경로-비교-정리|DEV-101 홈랩 인증서·Cloudflare·접속 경로 비교 정리]]** (`Dev/인프라/`)
* **[[Dev/자동화/n8n-워크플로우-신뢰성-및-에러-복구-패턴|DEV-201 n8n 워크플로우 신뢰성 및 에러 복구 설계 패턴]]** (`Dev/자동화/`)
* **[[Dev/자동화/n8n-지식-증류-워크플로우-작업-명세서|DEV-202 Minerva 지식 증류 파이프라인 n8n 워크플로우 변환 작업 명세서]]** (`Dev/자동화/`)
* **[[Dev/관측성/LLM-토큰-사용량-및-관측성-파이프라인-설계|DEV-301 LLM 토큰 사용량 및 관측성 파이프라인 설계]]** (`Dev/관측성/`)
* **[[Dev/데이터/Neo4j-지식그래프-계통-모델링-및-근연관계-검색-패턴|DEV-401 Neo4j 지식 그래프 계통 모델링 및 근연관계 가중합 검색 패턴]]** (`Dev/데이터/`)

---

## 📥 빠른 캡처 & 인박스

* 미정리 메모는 [[Inbox.md|Inbox.md]] 또는 `Inbox/` 폴더에 작성합니다.
* [[Inbox/test-note|초기 설정 테스트 노트]]
* 주기적으로 메모를 검토하여 알맞은 영역(`Dev`, `Work`, `Learning`)으로 정리하고 인박스를 비웁니다.

---

## ⚙️ 자동화 및 시스템 도구

* **지식 증류 자동화 스크립트**: [`scripts/distill_knowledge.py`](file:///Volumes/Dove-Nest-SSD/knowledge/Minerva/scripts/distill_knowledge.py)
* **n8n 증류 웹훅 명세**: [[Dev/자동화/n8n-지식-증류-워크플로우-작업-명세서|DEV-202 명세서]] (BN-504)
* **새 노트 템플릿**: [[Templates/note|note 템플릿]]

---

## 🏷️ 태그 체계

* **영역 태그**: `#dev` `#work` `#learning` `#inbox`
* **도메인 태그**: `#infra` `#automation` `#n8n` `#observability` `#data` `#neo4j` `#agent`
