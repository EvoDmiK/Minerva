---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-15-RG202-NAS-TEST-배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RG-202 변경 NAS TEST 배포 완료

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-15-RG202-NAS-TEST-배포]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":0,"데이터":6}

## 1. 개요 및 목적

사용자가 선행 감사 도구와 MRR 수정 결과를 NAS 테스트 서버에 올리도록 지시했다. NAS의 TEST 스택에만 배포하고 컨테이너 상태, 이미지 출처, 수정된 평가 계산 및 실제 검색 API를 확인하는 것이 목표다. 현재 Mac의 로컬 TEST 재배포로 대체하지 않는다. Production 반영은 승인되지 않았다.

NAS SSH의 기본 포트 접속은 Connection refused였다. 런북에 기록된 별도 SSH 포트에서는 서버 응답과 호스트 키 확인까지 성공했으나 키 인증과 기존 비밀번호 1회 인증이 실패했다. 사용자가 NAS 전용 인증 정보를 제공한 후 접속에 성공했다. 인증 정보는 기록하지 않는다.

## 2. 핵심 아키텍처 및 원칙

- 요청 배경과 목표
- 현재 상태와 접속 결과
- 배포 묶음과 변경 전후
- 검증 방법과 실제 결과
- 실제 배포와 검증 결과
- 배포·커밋·후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 선행 감사 도구와 MRR 수정 결과를 NAS 테스트 서버에 올리도록 지시했다. NAS의 TEST 스택에만 배포하고 컨테이너 상태, 이미지 출처, 수정된 평가 계산 및 실제 검색 API를 확인하는 것이 목표다. 현재 Mac의 로컬 TEST 재배포로 대체하지 않는다. Production 반영은 승인되지 않았다.

NAS SSH의 기본 포트 접속은 Connection refused였다. 런북에 기록된 별도 SSH 포트에서는 서버 응답과 호스트 키 확인까지 성공했으나 키 인증과 기존 비밀번호 1회 인증이 실패했다. 사용자가 NAS 전용 인증 정보를 제공한 후 접속에 성공했다. 인증 정보는 기록하지 않는다.

**NAS TEST 배포와 실제 검증을 완료했다.** NAS TEST 컨테이너만 교체했고 Production 컨테이너의 ID와 시작 시각은 배포 전후 동일함을 확인했다. 현재 Mac의 로컬 TEST는 재시작하지 않았다.

현재 작업 트리의 미커밋 변경을 누락하지 않도록 HEAD의 검증된 runtime allowlist 패키지를 만든 뒤 이번 작업의 두 파일만 덮어쓴 별도 스냅샷을 만들었다. 이전 AGENTS.md·MCP 설정·다른 작업 문서·비밀 환경 파일은 포함하지 않았다. 기본 환경 예제 파일은 포함한다.

- 기준 커밋: 434b6a4be8493f9b8bd85f477cbe8aca65ec7413.
- 덮어쓴 파일: src/robingraph/retrieval/evaluation.py, scripts/audit_retrieval_readiness.py.
- 변경 효과: 실패한 답변 가능 질문의 RR=0을 MRR 평균에 포함하고 TEST 전용 읽기 감사 스크립트를 이미지에 포함한다. HippoRAG/PPR 구현이나 화면 변경은 없다.
- 최종 아카이브: /tmp/robingraph-rg202-nas-package/robingraph-rg202-098d5f2da352.tar.gz.
- 최종 아카이브 SHA-256: 1b47a3b687e38f629d487b1a786da34d0bc0d8b2108ae0f8a6b91123f48e6f20.
- 파일 스냅샷 SHA-256: 098d5f2da352fdad80c5569e9114826f3401f7a41de99419e65fd8ac44ed364c.
- 실제 배포 이미지: robingraph-api:test-rg202-098d5f2da352.
- runtime 파일 135개의 해시와 기준 커밋·미커밋 덮어쓰기 목록을 SOURCE_MANIFEST.json에 보관했다. 이를 포함한 최종 tar의 각 파일 해시를 다시 검사해 모두 일치했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-15-RG202-NAS-TEST-배포]]
- [[Dev/index|Dev 인덱스]]
