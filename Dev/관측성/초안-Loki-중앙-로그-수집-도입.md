---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-10-Loki-중앙-로그-수집-도입]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Loki 중앙 로그 수집 도입

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-10-Loki-중앙-로그-수집-도입]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":11,"데이터":0}

## 1. 개요 및 목적

여러 서비스 로그를 Grafana 한곳에서 보기 위해 NAS에 Loki, 각 호스트에 Alloy를 두었다.

## 2. 핵심 아키텍처 및 원칙

- 결과
- 구성
- 알아 둘 점
- 리소스 점검 (2026-10-10, 도입 직후)
- 남은 일
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```
Mac mini 컨테이너 로그 + Hermes 파일 로그 ┐
NAS 컨테이너 로그                          ├─ Alloy ─▶ Loki (NAS) ─▶ Grafana
```

## 4. 검증 근거 및 트러블슈팅

_작성 필요_

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-10-Loki-중앙-로그-수집-도입]]
- [[Dev/index|Dev 인덱스]]
