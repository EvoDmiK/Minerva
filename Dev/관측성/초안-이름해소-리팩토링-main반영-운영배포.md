---
created: 2026-10-27
updated: 2026-10-27
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-이름해소-리팩토링-main반영-운영배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 이름 해소 리팩토링 main 반영·운영 배포 — 2026-10-26

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-이름해소-리팩토링-main반영-운영배포]] · 분류 근거 {"인프라":4,"자동화":0,"관측성":5,"데이터":1}

## 1. 개요 및 목적

사용자가 이름 해소 리팩토링의 운영 배포와 브랜치 병합을 명시적으로 승인했다. 리팩토링 commit `9df92886cac349e346b6197085d4dfc9031ff614`를 main에 fast-forward하고 origin/dev-codex·origin/main으로 push했다. 이전 리팩토링 문서의 “당시 배포·commit/push 미실행” 기록은 보존하고 이번 후속 작업을 별도로 기록한다.

실제 Jenkins job은 저장소 파일과 별개인 inline definition을 사용했다. 이전 lexical 정의를 현재 commit의 `ci/Jenkinsfile.production`과 동기화하고 job properties를 보존했다. 운영 교체 전 input 대기 중이던 이전 PROD #10은 ABORTED로 취소했고 stale queue 78도 취소했다. 새 PROD #11은 SUCCESS로 완료됐고 실제 운영에서 healthy·active/semantic·tracing true·실험 50을 확인했다. 공개 4 POST·3 GET은 모두 200이었고, 고유 trace 4개가 질문·마스킹된 응답·태그와 일치했다. TEST 컨테이너는 변경하지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 2. 해결 방안 및 설계
- 3. 변경 범위 및 증거
- 4. 검증 및 테스트 결과
- 선행 리팩토링 검사 — 이번 빌드와 구분
- 실제 Jenkins 작업
- 이번 Jenkins 검사
- 독립 배포 후 검토
- 실제 공개 질의와 trace
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
검증 리팩토링 commit → main fast-forward / push
→ 실제 inline 정의 동기화 → stale 실행 취소 → PROD #11
→ 운영 이미지·runtime·동일 요청 trace 검증
```

## 4. 검증 근거 및 트러블슈팅

실제 Jenkins job은 저장소 파일과 별개인 inline definition을 사용했다. 이전 lexical 정의를 현재 commit의 `ci/Jenkinsfile.production`과 동기화하고 job properties를 보존했다. 운영 교체 전 input 대기 중이던 이전 PROD #10은 ABORTED로 취소했고 stale queue 78도 취소했다. 새 PROD #11은 SUCCESS로 완료됐고 실제 운영에서 healthy·active/semantic·tracing true·실험 50을 확인했다. 공개 4 POST·3 GET은 모두 200이었고, 고유 trace 4개가 질문·마스킹된 응답·태그와 일치했다. TEST 컨테이너는 변경하지 않았다.

| 구분 | 현재 확인 상태 | 범위 |
| --- | --- | --- |
| 요구사항 | 운영 배포·브랜치 반영 명시 승인 | 기존 이름 해소 리팩토링 |
| Git | 9df92886 commit·main fast-forward·두 원격 push 완료 | 최신 검증 소스를 일반 배포 경로로 연결 |
| Jenkins | 실제 inline 정의를 committed production 파일과 동기화 | properties 보존 |
| 이전 실행 | #10 ABORTED·queue 78 취소 | 운영 교체 전 stale lexical 실행 중단 |
| 새 실행 | PROD #11 SUCCESS·운영 교체 완료 | runtime·공개 계약·trace 검증 완료 |
| 기능 상태 | RG-212 진행 중 유지 | 리팩토링 배포가 질의 정확도 개선을 뜻하지 않음 |

이름 해소 리팩토링은 graph/profile 두 경로의 공통 resolver·identity 검증을 helper로 모으고 외부 응답을 유지하는 변경이었다. 사용자는 해당 변경의 운영 배포와 브랜치 반영을 승인했다.

- 이미 검증한 리팩토링 commit을 main에 fast-forward하고 원격 두 브랜치에 push했다.
- 실제 inline 정의를 현재 committed `ci/Jenkinsfile.production`으로 동기화했다. job properties를 보존하고 이전 문서의 당시 상태는 수정하지 않았다.
- 이전 정의로 실행돼 input 대기 중인 #10과 stale queue를 취소한 뒤 새 #11을 시작했다.
- 새 빌드의 검사·이미지·운영 runtime·실제 trace를 확인해 배포 완료를 확정했다. 앞선 로컬 리팩토링 검사와 이번 Jenkins 검사 시간을 분리해 기록했다.

- `src/robingraph/api/services.py` — 앞서 검증한 `_resolve_taxon_name` 공통화. 이번 배포에서 추가 질의 로직을 개발하는 작업이 아니다.
- `tests/test_entity_resolution_api.py` — 앞선 invalid identity 회귀 검사.
- `ci/Jenkinsfile.production` — 실제 inline job 정의 동기화의 committed 원본.
- 증거 경로: `docs/verification/assets/2026-10-26-name-resolution-production/`.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-이름해소-리팩토링-main반영-운영배포]]
- [[Dev/index|Dev 인덱스]]
