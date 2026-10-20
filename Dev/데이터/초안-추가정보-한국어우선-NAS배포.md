---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-06-추가정보-한국어우선-NAS배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 2026-10-06 추가 정보 한국어 우선 표시 · 구현 및 NAS TEST 배포

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-06-추가정보-한국어우선-NAS배포]] · 분류 근거 {"인프라":1,"자동화":1,"관측성":0,"데이터":19}

## 1. 개요 및 목적

사용자는 새 이름을 한국 도감과 확인 가능한 국명 자료에 따라 표시하고, 한국어 이름을 확인하지 못한 종은 영어로 남기기를 요청했다. 이어서 답변의 `추가 정보` 토글을 열었을 때 나오는 정보도 한국어를 우선하도록 요청했다.

이번 작업의 범위는 다음 세 항목이다.

## 2. 핵심 아키텍처 및 원칙

- 1. 요청 배경과 목표
- 2. 확인한 문제와 원인
- 2.1 생태 후보를 먼저 제한한 뒤 국명을 교정하던 순서
- 2.2 관계 목록의 중복 이름과 학명 제목
- 2.3 국명이 없는 아종의 선택 안내
- 3. 구현 변경
- 3.1 생태 관계: 국명 검증을 후보 제한보다 먼저 수행
- 3.2 통칭·가축형 관계: 한국어 이름과 학명 중심으로 표시
- 3.3 아종 목록: 한국어 소속 종 안내 추가
- 4. 한국어 이름 적용 기준과 종 구분
- 5. 변경 파일
- 6. 실행한 검증과 결과
- 6.1 Python 생태 관계 테스트
- 6.2 프런트엔드 전체 검증
- 6.3 NAS 실제 TEST DB 읽기 검증
- 6.4 저장소 확인
- 7. NAS TEST 배포와 공개 서비스 확인
- 7.1 커밋과 배포 산출물
- 7.2 배포 명령과 상태
- 7.3 공개 API와 프런트엔드 확인
- 8. 남은 한계와 후속 사항
- 9. 작업 문서 작성 기준 보강

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
uv run --locked --extra test --extra tracing \
  python -m unittest discover -s tests -p test_ecological_relations.py -v
```

```sh
node --test tests/frontend/*.test.js
```

```sh
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh update
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh verify
```

```sh
uv run --locked --extra test --extra tracing \
  python scripts/verify_api_deployment.py \
  --base-url https://robingraph-test.dove-nest.com --json
```

## 4. 검증 근거 및 트러블슈팅

사용자는 새 이름을 한국 도감과 확인 가능한 국명 자료에 따라 표시하고, 한국어 이름을 확인하지 못한 종은 영어로 남기기를 요청했다. 이어서 답변의 `추가 정보` 토글을 열었을 때 나오는 정보도 한국어를 우선하도록 요청했다.

1. 같은 서식 환경·먹이 생태의 새 살펴보기: 국명이 확인된 후보를 먼저 선택하고 한국어 이름으로 표시한다.
2. 이 종의 아종 살펴보기: 아종 자체의 국명이 없더라도 한국어로 소속 종을 안내한다.
3. 통칭·가축형 관계 알아보기: 관계 제목과 관련 종의 이름을 한국어 우선으로 표시하고 중복 영문명을 줄인다.

근연 관계 가중합 점수와 TOP3 정렬 규칙은 이번 변경 대상이 아니다. 검증되지 않은 번역을 추가하거나, 서로 다른 종을 같은 국명으로 합치는 작업도 포함하지 않는다.

기존 `ecological_relations.py`의 `PEERS_QUERY`는 Neo4j의 한국어 이름을 기준으로 후보를 정렬하고 `LIMIT 4`를 적용했다. 반환된 후보에 Python의 `with_korean_display_name()`을 적용해 검증된 국명으로 다시 표시한 뒤 처음 3종을 노출했다.

그래프에 한국어 이름이 있더라도 별도 국명 표에서 확인하지 못하면 표시 단계에서 영어로 바뀐다. 반대로 국명 표에 한국어 이름이 있는 종이 처음 4개 후보에 포함되지 않으면 표시 단계에서 그 종을 다시 선택할 수 없다. 따라서 화면의 이름 선택은 한국어 우선이었지만 후보 선택은 검증된 국명 우선이 아니었다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-06-추가정보-한국어우선-NAS배포]]
- [[Dev/index|Dev 인덱스]]
