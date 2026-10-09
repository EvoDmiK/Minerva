---
created: 2026-10-09
updated: 2026-10-09
project: Birds-Nest
type: work-record
tags:
  - birds-nest
  - minerva
  - pkm
  - knowledge-distillation
  - architecture
---

# Minerva 지식 증류(Distillation) 파이프라인 구축 및 Dev 구조 개편

- **작업일**: 2026-10-09
- **목표**: `Work/`에 88% 편중되어 있던 Minerva 볼트 구조를 개선하여, 프로젝트 작업 기록에서 재사용 가능한 핵심 기술 지식을 `Dev/` 상록수 노트로 정제(증류)하고 폴더 위계를 정비한다.

## 1. 배경 및 문제 진단

기존 Minerva 볼트는 전체 106개 마크다운 문서 중 `Work/`에 93개(87.7%)가 집중되어 있었다.
* **장점**: 개발·배포 실행력과 세부 근거 보존력은 최상 수준.
* **한계 (병목)**:
  1. **지식의 매몰**: n8n 웹훅 노하우, Tailscale DNS, Neo4j 튜닝, Grafana 쿼리 등 범용 기술이 특정 프로젝트의 날짜별 일지(`2026-10-xx-*.md`) 속에 갇혀 재사용성이 떨어짐.
  2. **시계열 기록 편중**: 영구적 개념/패턴(Evergreen Notes)이 부족하고 시계열적 사건 기록에 편중됨.
  3. **Dev/Learning 공동화**: 초기 아키텍처에 정의된 `Dev/`에 문서가 1개뿐이었음.

## 2. 수행한 변경 내용

### 2.1 [1단계] Work → Dev 핵심 지식 증류 (Distillation)
프로젝트 작업 기록에서 검증된 범용 기술 지식을 선별하여 `Dev/` 하위에 3편의 상록수 가이드를 독립 작성하고 [[Dev/index]]에 분류 배치함.

1. [[Dev/n8n-워크플로우-신뢰성-및-에러-복구-패턴]]:
   * 웹훅 페이로드 스키마 방어, 비동기 타임아웃, 멱등성 보장, n8n PostgreSQL 모니터링 쿼리.
2. [[Dev/LLM-토큰-사용량-및-관측성-파이프라인-설계]]:
   * Claude/Codex/Gemini 토큰 정규화 스키마, 프롬프트 캐시 적중률 계산식, TimescaleDB 하이퍼테이블 및 Grafana 시각화 패턴.
3. [[Dev/Neo4j-지식그래프-계통-모델링-및-근연관계-검색-패턴]]:
   * 9,500종 조류 분류 계통수 스키마, Cypher 계통 거리 탐색, 4속성 가중합(0.5 계통 + 0.3 분류 + 0.1 서식 + 0.1 먹이) 랭킹 알고리즘.

### 2.2 [2단계] Work 폴더 내부 위계 정돈 (Core vs Logs)
* `Work/RobinGraph`의 모범 사례(`index.md` + `작업기록/`)를 따라 `Work/Birds-Nest`와 `Work/Gullinkambi`의 날짜별 일지들을 각각 `작업기록/` 하위 폴더로 이동.
* 프로젝트 루트에는 프로젝트 인덱스(`index.md`)와 핵심 명세(`ORCA-Grafana-MLflow-Claude-작업명세.md`, `AI-subscription-exporter-README.md` 등)만 유지하여 가시성 확보.
* 볼트 전체(25개 이상 파일)에서 변경된 경로에 맞춰 `[[위키링크]]`를 전수 자동 갱신.

### 2.3 [3단계] 지식 증류 자동화 스크립트 구축
* `scripts/distill_knowledge.py` 구현:
  * `Work/` 하위 작업기록을 스캔하여 기술 도메인(n8n, LLM 관측성, 네트워크, 그래프, 에이전트) 및 코드 블록 분석.
  * `--create-draft` 플래그로 `Dev/` 상록수 노트 템플릿 자동 생성 지원.
  * 향후 n8n 웹훅 또는 Hermes 에이전트와 연동 가능한 기반 마련.

## 3. 검증 결과

* `Dev/` 내 상록수 가이드 4편 등록 및 `Dev/index` 정상 렌더링 확인.
* `Work/Birds-Nest/index.md`, `Work/Gullinkambi/index.md`, `Work/index.md`의 모든 위키링크 유효성 검증.
* Python 지식 증류 도구 실행 검증: 77개 작업기록 정상 스캔 및 도메인 태깅 확인.

## 4. 관련 문서

* [[Dev/index|Dev 인덱스]]
* [[Work/index|Work 인덱스]]
* [[Work/Birds-Nest/index|Birds-Nest 인덱스]]
* [[Work/Gullinkambi/index|Gullinkambi 인덱스]]
* [[Work/RobinGraph/index|RobinGraph 인덱스]]
