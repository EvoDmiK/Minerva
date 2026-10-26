---
created: 2026-10-27
updated: 2026-10-27
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-Git정리-main병합-원격동기화]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# Git 변경 정리·main 병합·후속 운영 배포 설정 동기화 — 2026-10-26

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-Git정리-main병합-원격동기화]] · 분류 근거 {"인프라":10,"자동화":1,"관측성":7,"데이터":1}

## 1. 개요 및 목적

사용자 승인에 따라 검증한 코드·평가 자료·문서·증거를 commit하고 origin/main의 변경을 병합했다. 작업 commit은 `e74aaa4eb38cd4bcfa2b6ec206ca637b99981291`, 최종 merge commit은 `cf52e1dc0c9439ebb7b8b579f9fc5ed2dcc117f4`다. Desktop의 main을 fast-forward하고 `git push origin dev-codex main`을 완료해 두 원격 브랜치가 cf52e1d를 가리키게 했다.

저장소의 두 Jenkinsfile은 semantic·tracing 활성화·Production 실험 50으로 맞췄다. 실제 Jenkins job은 inline definition을 사용하며 이번 Git 작업에서 설정 API를 호출하지 않아 변경되지 않았다. 향후 inline 정의 동기화와 다음 운영 배포 승인이 별도로 필요하다. 병합 후 Python 1,326 실행·1,286 통과·40 skip·0 실패와 Node 322 통과를 확인했다. 현재 운영을 재배포하지 않았고, 이전 운영 배포 기록의 당시 main/lexical 상태는 보존했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 작업 및 변경 결과 요약
- 1. 작업 배경 및 문제 분석
- 2. 해결 방안 및 설계
- 3. 주요 변경 내용
- 대상 파일 및 자료
- 평가 CSV의 원본 바이트 보존
- main에 반영한 설정
- 4. 검증 및 테스트 결과
- 완료된 사전 검사
- 실제 병합과 source 동일성 검증
- 5. 배포 및 형상 관리
- 6. 한계 및 후속 과제
- 관련 문서

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
graph interpreter = semantic
MLflow tracing = true
MLflow experiment ID = 50
MLflow experiment name = robingraph-prod
```

## 4. 검증 근거 및 트러블슈팅

사용자 승인에 따라 검증한 코드·평가 자료·문서·증거를 commit하고 origin/main의 변경을 병합했다. 작업 commit은 `e74aaa4eb38cd4bcfa2b6ec206ca637b99981291`, 최종 merge commit은 `cf52e1dc0c9439ebb7b8b579f9fc5ed2dcc117f4`다. Desktop의 main을 fast-forward하고 `git push origin dev-codex main`을 완료해 두 원격 브랜치가 cf52e1d를 가리키게 했다.

저장소의 두 Jenkinsfile은 semantic·tracing 활성화·Production 실험 50으로 맞췄다. 실제 Jenkins job은 inline definition을 사용하며 이번 Git 작업에서 설정 API를 호출하지 않아 변경되지 않았다. 향후 inline 정의 동기화와 다음 운영 배포 승인이 별도로 필요하다. 병합 후 Python 1,326 실행·1,286 통과·40 skip·0 실패와 Node 322 통과를 확인했다. 현재 운영을 재배포하지 않았고, 이전 운영 배포 기록의 당시 main/lexical 상태는 보존했다.

Git 통합은 RG-212 전체 완료가 아니다. V2-07A·V2-10B 잔여 실패와 최초 평가·gold 작성 한계는 그대로 남는다.

| 구분 | 현재 확인 사항 | 범위 |
| --- | --- | --- |
| 요구사항 | 사용자 Git 정리·병합 승인 | 검증 소스·자료·기록 통합 |
| 변경 정리 | dirty 1,943파일·약 191MB | 코드·dataset·docs/evidence 포함 |
| 제외 | species_profile.py.orig 백업을 /tmp에 보존 이동 | 백업 제외, 원본 삭제로 기록하지 않음 |
| 비밀 점검 | 실제 runtime 비밀값 대조 scan 0건 | generic token scan은 fixture만 확인 |
| Jenkins 설정 | 저장소 두 Jenkinsfile을 semantic·tracing true·실험 50에 맞춤 | 실제 inline job 정의는 미변경; 별도 동기화 필요 |
| 검증 | helper mock 16 통과·코드 diff check 통과 | 기존 Markdown hardbreak·원본 patch 공백 보존 |
| Git | e74aaa4 작업 commit → cf52e1d merge | origin/dev-codex·origin/main push 완료 |

직전 배포는 TEST 검증 소스 SHA를 불변 snapshot으로 고정해 운영에 반영했지만 Git에는 미커밋 상태가 남았다. origin/main은 이전 릴리스 revision `33c0b67`, dev 작업의 기준은 `834c535`였다. 일반 main 배포 정의가 lexical을 유지하면 향후 배포가 현재 승인된 semantic 설정을 덮어쓸 수 있었다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-26-Git정리-main병합-원격동기화]]
- [[Dev/index|Dev 인덱스]]
