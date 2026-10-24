---
created: 2026-10-25
updated: 2026-10-25
type: reference
category: "관측성"
status: draft
source_project: "Jery"
source_work_log: "[[Work/Jery/작업기록/2026-10-24-Jery-도구경계-데이터v4와-MLflow저장]]"
tags:
  - dev
  - draft
  - "jery"
---

# 도구 경계 데이터 v4 · 학습800개와 설명 개선

> 자동 증류 초안 · 원천 [[Work/Jery/작업기록/2026-10-24-Jery-도구경계-데이터v4와-MLflow저장]] · 분류 근거 {"인프라":0,"자동화":0,"관측성":9,"데이터":0}

## 1. 개요 및 목적

기존 학습600개에 새 합성200개를 추가했다. 도구마다80개로 수량을 맞추고, 읽기/수정·조회/주문·과거/현재 가격·Bases/Dataview 경계를 구분하도록 설명을 개선했다. 이번 작업은 데이터 준비이며 새 모델 학습이나 성능 측정은 실행하지 않았다.

[MLflow 데이터 Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/ff162f7af7d64c05bd2a9fde44d9d8bd)

## 2. 핵심 아키텍처 및 원칙

- 저장 구성
- 변경과 보존
- 검증 결과
- 재현과 다음 학습의 조건

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

| Child | Train | Validation | Test | 설명 |
|---|---:|---:|---:|---|
| baseline | 600 | 20 | 20 | 기존 |
| description_only | 600 | 20 | 20 | 개선 |
| data_only | 800 | 20 | 20 | 기존 |
| combined | 800 | 20 | 20 | 개선 |

각 Child의 `data/train.json`, `data/validation.json`, `data/test.json`은 실제 데이터 전체를 담은 JSON 배열이다. `data/native-export.zip`은 기존 실행기가 읽는 JSONL 세 파일과 manifest를 묶은 재현용 자료다. `catalog/tools.json`, `catalog/criteria.json`, native 형식 감사도 함께 저장한다. JSON 배열은 MLflow Dataset 입력으로 등록해 split·digest·원본 Artifact 위치를 연결한다. 이 등록 방식은 [MLflow Log Inputs API](https://mlflow.org/docs/latest/api_reference/rest-api.html)에 따른다.

params는 profile·dataset_version·catalog_version·train_rows만 기록한다. 상세 건수·검증·해시·정책은 JSON Artifact로 보관한다. Parent에는 추가200개 원문, 이전/새 설명, 데이터 및 감사 manifest와 업로드 검증 내역을 남긴다. Artifact는 업로드 후 다시 내려받아 SHA-256을 비교한다.

- 신규200개: 한국어 합성, 120개 시나리오, 24개 문맥 사례. 작성자는 Codex이고 독립/사람 검토를 완료했다고 표시하지 않는다.
- 기존 요청·맥락·정답·alias를 보존했다. 기존 설명 비교군의 validation/test는 바이트도 동일하다. 설명 개선 비교군은 criteria와 카탈로그 연결만 갱신했다.
- 도구 ID·원래 설명·input_schema를 보존하고 모델용 `routing_description`을 새 카탈로그에 추가했다. export criteria와 동일한 내용이다.
- 신규 카탈로그는 `hermes-ten-tools-0b320e20bf3f`; 기존 설명 비교군은 `hermes-ten-tools-2289142ab57a`다. 라벨·`decision-export-v2` 계약은 유지한다.

데이터 테스트37개, 기존 데이터 검증130개 사례/10개 도구/65개 시나리오가 통과했다. 새800개 구성은 도구당80개, 전체475개 시나리오다. 동일 입력으로 재생성한 export 해시가 같고, 원본 파일 보존·분할 간 시나리오/입력 중복·후보/정답/action 매핑을 검사했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Jery/작업기록/2026-10-24-Jery-도구경계-데이터v4와-MLflow저장]]
- [[Dev/index|Dev 인덱스]]
