---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-06-아종목록-카드디자인-영어표시명-NAS배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 2026-10-06 아종 목록 카드와 출처 확인 표시명

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-06-아종목록-카드디자인-영어표시명-NAS배포]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":0,"데이터":17}

## 1. 개요 및 목적

사용자는 `추가 정보 → 이 종의 아종 살펴보기`를 연 화면을 제시했다. 화면에는 긴 학명 버튼과 `AviList global avian checklist` 링크가 한 줄에 붙어 있었으며, 아종 이름도 학명 위주였다. 요청은 목록을 보기 좋게 정리하고, 주요 이름에 한국어 이름 또는 영어 이름을 쓰는 것이다.

이번 작업에서는 아종 목록을 카드로 나누고 이름·분포·보기 버튼·접힌 학명 및 출처를 구분했다. 한국어 이름이 확인되지 않은 청둥오리 두 아종에는 기관 자료에서 확인한 영어 이름을 사용한다. 부모 종의 국명을 아종의 새 국명으로 만들지 않는다.

## 2. 핵심 아키텍처 및 원칙

- 1. 요청 배경과 작업 범위
- 2. 변경 전 문제와 원인
- 3. 이름 조사와 적용 기준
- 3.1 출처에서 확인한 이름
- 3.2 이름을 적용하는 조건
- 4. 화면 변경 전후
- 4.1 아종 목록
- 4.2 데스크톱과 좁은 화면
- 4.3 도감 카드
- 5. 변경 파일
- 6. 검증 범위와 실제 결과
- 6.1 Python 전체 실행
- 6.2 아종 관련 테스트
- 6.3 프런트엔드 전체
- 6.4 실제 NAS DB 읽기 검증
- 6.5 실제 브라우저 레이아웃 확인
- 6.6 저장소 확인
- 7. 남은 한계와 적용 범위
- 8. 배포 기록
- 8.1 커밋과 산출물
- 8.2 배포 명령과 상태
- 8.3 공개 서비스 확인
- 9. 문서와 후속 관리

## 3. 재사용 가능한 코드 스니펫 / 설정

```sh
uv run --locked --extra test --extra tracing python -m unittest discover -s tests -v
```

```sh
uv run --locked --extra test --extra tracing \
  python -m unittest discover -s tests -p test_subspecies.py -v
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

이번 작업에서는 아종 목록을 카드로 나누고 이름·분포·보기 버튼·접힌 학명 및 출처를 구분했다. 한국어 이름이 확인되지 않은 청둥오리 두 아종에는 기관 자료에서 확인한 영어 이름을 사용한다. 부모 종의 국명을 아종의 새 국명으로 만들지 않는다.

실제 분류 연결, 학명에 따른 자료 조회, 부모·아종 taxon ID와 활성 분류판 확인은 유지한다. 근연 관계의 가중치와 생태 후보 정렬은 변경 대상이 아니다.

실제 활성 아종 데이터의 한국어 이름과 영어 이름도 비어 있었다. 앞선 작업에서 소속 종을 한국어로 설명했지만, 아종 자체의 별도 표시 이름을 확인해 넣는 처리는 없었다.

| 활성 taxon ID | 학명 | 표시할 영어 이름 | 확인 자료 |
| --- | --- | --- | --- |
| `avilist-taxon:v2025b:546` | Anas platyrhynchos conboschas | Greenland Mallard | Dansk Ornitologisk Forening의 2019 세계 조류 이름 자료 |
| `avilist-taxon:v2025b:545` | Anas platyrhynchos platyrhynchos | Northern Mallard | NCBI Taxonomy ID 8840의 common name |

NCBI 페이지에는 GenBank 이름으로 common mallard, 다른 common name으로 northern mallard가 기록돼 있다. 이 자료는 표시 이름 참고에 사용하고, 아종의 채택 여부나 부모 관계를 결정하는 분류 근거로 사용하지 않는다. 서비스의 분류 연결은 기존 AviList 그래프에서 확인한다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/4xx 채팅 UI·카드/2026-10-06-아종목록-카드디자인-영어표시명-NAS배포]]
- [[Dev/index|Dev 인덱스]]
