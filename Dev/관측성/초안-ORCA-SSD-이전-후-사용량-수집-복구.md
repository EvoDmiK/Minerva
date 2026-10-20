---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-08-ORCA-SSD-이전-후-사용량-수집-복구]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# ORCA SSD 이전 후 사용량 수집 복구

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-08-ORCA-SSD-이전-후-사용량-수집-복구]] · 분류 근거 {"인프라":0,"자동화":1,"관측성":18,"데이터":0}

## 1. 개요 및 목적

SSD 이전으로 변경된 작업 폴더를 수집 대상에 추가하고, ORCA 원본 파일 캐시를 초기화해 사용량 수집을 복구했다. 2026-10-08 10:13 KST 무렵 확인한 오늘 집계는 **70회 호출, 2,344,057토큰**이다. 이는 확인 시점의 집계이며 하루 최종 합계가 아니다.

- Grafana 서비스 모니터링의 ORCA 탭에서 오늘 총 토큰과 호출 수가 0, 모델별 사용량과 추이 패널은 데이터 없음으로 표시됐다. 집계 지연은 2일이었다.
- `hermes-telemetry` 컨테이너는 실행 중이었으나 ORCA 변경분이 0건이었다.
- 수집 대상 경로는 `/Users/kimdove/orca`와 `/Volumes/Dove-Nest-SSD/projects/orca-workspaces`였다.
- 실제 최신 Codex 세션의 작업 경로는 `/Volumes/Dove-Nest-SSD/projects/Birds-Nest`와 `/Volumes/Dove-Nest-SSD/app-data/orca/kimdove/home/workspaces/Gullinkambi/main` 등으로 변경돼 있었다. 경로 필터는 문자열 기준 하위 경로를 판별하므로 기존 심볼릭 링크 경로만 등록해서는 새 실제 경로가 포함되지 않는다.
- 기존 ORCA Antigravity·Claude 집계 JSON은 10월 6일 이후 갱신되지 않았고 Codex 집계 JSON도 오래된 상태였다. 이번 복구는 원본 세션 로그 수집 경로를 바로잡는 방식으로 진행했다.

## 2. 핵심 아키텍처 및 원칙

- 결과
- 증상과 원인
- 적용한 변경
- 검증과 한계
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
/Users/kimdove/orca
/Volumes/Dove-Nest-SSD/app-data/orca/kimdove/home/workspaces
/Volumes/Dove-Nest-SSD/projects
```

## 4. 검증 근거 및 트러블슈팅

SSD 이전으로 변경된 작업 폴더를 수집 대상에 추가하고, ORCA 원본 파일 캐시를 초기화해 사용량 수집을 복구했다. 2026-10-08 10:13 KST 무렵 확인한 오늘 집계는 **70회 호출, 2,344,057토큰**이다. 이는 확인 시점의 집계이며 하루 최종 합계가 아니다.

- 오늘 원본 파일 캐시에서 집계 행 5개, 호출 70회, 총 2,344,057토큰을 확인했다.
- 상태에 일별 사용량 항목 178개, 쓰레드별 항목 233개가 저장돼 있었다. 이 수는 오늘 값만의 행 수가 아니다.
- 커서의 성공 저장 시각은 `2026-10-08T01:13:39.938835+00:00`(10:13:39 KST)이었다.
- 수집기는 모든 webhook 전송이 성공한 뒤에만 커서를 저장하므로 전송 성공을 확인할 수 있다.
- Grafana 화면 및 DB를 직접 재조회한 검증은 수행하지 않았다. 사용자에게 대시보드 새로고침을 안내했다.
- Antigravity 집계 JSON 생성 작업이나 Codex 쓰레드 이름 스냅샷 작업의 정상화는 이번 변경에서 검증하지 않았다.
- 저장소 변경은 Compose 설정 1줄이며 커밋·푸시는 하지 않았다.

- [[Work/Gullinkambi/index|Gullinkambi 작업 기록]]
- [[Work/Gullinkambi/작업기록/2026-10-07-ORCA-최근7일-토큰-사용량-검증|ORCA 최근 7일 토큰 사용량 검증]]

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-08-ORCA-SSD-이전-후-사용량-수집-복구]]
- [[Dev/index|Dev 인덱스]]
