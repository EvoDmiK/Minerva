---
created: 2026-10-18
updated: 2026-10-18
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/index]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# Birds-Nest 작업기록

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/index]] · 분류 근거 {"인프라":0,"자동화":9,"관측성":1,"데이터":0}

## 1. 개요 및 목적

작업기록을 **워크플로우·서비스·작업 주제별**로 분류한다. 워크플로우 이름이 있는 작업은 그 이름을 쓰고, Hermes·인프라처럼 워크플로우가 아닌 작업도 같은 수준에서 관리한다.

| 분류 | 범위 | 기존 기록 수 |
|---|---|---|
| [[Work/Birds-Nest/작업기록/Swallow/index\|Swallow]] | 주식·뉴스·모의투자·MCP·Grafana | 2 |
| [[Work/Birds-Nest/작업기록/Carrier-Pigeon/index\|Carrier-Pigeon]] | Gmail·커뮤니티 뉴스 분류와 알림 | 2 |
| [[Work/Birds-Nest/작업기록/Kestrel/index\|Kestrel]] | Codex 리셋 모니터링·MCP | 2 |
| [[Work/Birds-Nest/작업기록/Magpie/index\|Magpie]] | 볼트 Git 동기화·웹훅·알림 | 2 |
| [[Work/Birds-Nest/작업기록/Minerva/index\|Minerva]] | 지식 증류·문서 구조 | 1 |
| [[Work/Birds-Nest/작업기록/Hermes/index\|Hermes]] | 게이트웨이·모델·CLI | 1 |
| [[Work/Birds-Nest/작업기록/n8n-공통/index\|n8n-공통]] | 전체 워크플로우 신뢰성·실패율 검증 | 1 |
| [[Work/Birds-Nest/작업기록/인프라/index\|인프라]] | SSD 이전·NAS 백업·호스트 운영 | 1 |

## 2. 핵심 아키텍처 및 원칙

- 주제별 목록
- Swallow 작업 관리
- 신규 기록 규칙
- 분류 시 복합 기록 처리
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

| 분류 | 범위 | 기존 기록 수 |
|---|---|---|
| [[Work/Birds-Nest/작업기록/Swallow/index\|Swallow]] | 주식·뉴스·모의투자·MCP·Grafana | 2 |
| [[Work/Birds-Nest/작업기록/Carrier-Pigeon/index\|Carrier-Pigeon]] | Gmail·커뮤니티 뉴스 분류와 알림 | 2 |
| [[Work/Birds-Nest/작업기록/Kestrel/index\|Kestrel]] | Codex 리셋 모니터링·MCP | 2 |
| [[Work/Birds-Nest/작업기록/Magpie/index\|Magpie]] | 볼트 Git 동기화·웹훅·알림 | 2 |
| [[Work/Birds-Nest/작업기록/Minerva/index\|Minerva]] | 지식 증류·문서 구조 | 1 |
| [[Work/Birds-Nest/작업기록/Hermes/index\|Hermes]] | 게이트웨이·모델·CLI | 1 |
| [[Work/Birds-Nest/작업기록/n8n-공통/index\|n8n-공통]] | 전체 워크플로우 신뢰성·실패율 검증 | 1 |
| [[Work/Birds-Nest/작업기록/인프라/index\|인프라]] | SSD 이전·NAS 백업·호스트 운영 | 1 |

1. 해당 워크플로우·서비스 폴더에 `YYYY-MM-DD-주제-작업명.md`로 저장한다.
2. 작업 ID, 목적·변경 내용, 커밋, 실제 검증 결과, 미검증 사항, 남은 이슈를 기록한다.
3. 주제별 `index.md`와 관련 백로그에 문서 링크를 추가한다.
4. 여러 주제가 섞인 문서는 주된 작업 폴더에 한 번만 저장하고 다른 관련 인덱스에서 연결한다.
5. 날짜별 원문과 과거 검증 이력은 보존한다. 미실행 검증을 완료로 표시하지 않는다.
6. 새 주제가 생기면 같은 방식으로 폴더와 인덱스를 만든다. 상태·우선순위는 백로그에서 관리한다.

- Carrier-Pigeon 개편과 n8n 테스트베드 구축 기록은 주 작업인 Carrier-Pigeon에 보관한다.
- Minerva Git Sync 웹훅·NAS MCP 정리와 Birds Nest 후속 수정 기록은 Magpie 동기화 주제로 묶는다.
- Hermes Discord 설정·Orca SSD 이전·NAS 백업 기록은 인프라에 보관하고 Hermes 인덱스에서도 연결한다.
- 기존 12개 기록의 파일명과 본문 이력을 유지하고 참조 링크는 이동 경로에 맞게 갱신한다.

- [[Work/Birds-Nest/작업기록/지식연동/2026-10-17-Minerva-지식-증류-n8n-워크플로우-구현|BN-504 / DEV-202 Minerva 지식 증류 n8n 워크플로우]] — Claude 구현·Codex 통합/17계약테스트/n8n격리검증·dev-docs 가이드. 개발에2개inactive등록, 운영연동대기.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/index]]
- [[Dev/index|Dev 인덱스]]
