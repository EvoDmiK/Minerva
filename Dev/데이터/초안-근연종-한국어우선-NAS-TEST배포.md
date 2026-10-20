---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "데이터"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-08-근연종-한국어우선-NAS-TEST배포]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 근연종 탐색의 검증된 한국어 이름 우선 적용

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-08-근연종-한국어우선-NAS-TEST배포]] · 분류 근거 {"인프라":1,"자동화":0,"관측성":0,"데이터":9}

## 1. 개요 및 목적

작성일: 2026-10-08. 사용자 요청: 근연종 검색에도 생태 검색처럼 한국어 이름을 우선 적용한다. 대상은 같은 속·과 탐색 목록의 선택·정렬과 표시 일관성이다. 비교 후보 TOP 3의 가중 점수 순서는 유지한다.

기존 화면의 `speciesLabel`과 서버의 `with_korean_display_name`은 이미 검증 국명→원자료 영어 이름→학명 순으로 표시했다. 그러나 `related_species.py`의 Neo4j 쿼리는 원본 그래프의 한국어 `VernacularName`으로 먼저 정렬하고 `LIMIT 13`을 적용했다. 이후 Python이 12개를 선택하고 검증되지 않은 국명을 제거해 영어로 바꿨다. 그 결과 영어 이름 사이에 한국어 이름이 섞이고, 제한 밖의 검증 국명 후보를 되살릴 수 없었다.

## 2. 핵심 아키텍처 및 원칙

- 배경·원인·근거
- 변경 전후 동작·구현 파일
- 협업
- 검증 방법·실제 결과
- 커밋·배포
- 한계·후속 사항

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

기존 화면의 `speciesLabel`과 서버의 `with_korean_display_name`은 이미 검증 국명→원자료 영어 이름→학명 순으로 표시했다. 그러나 `related_species.py`의 Neo4j 쿼리는 원본 그래프의 한국어 `VernacularName`으로 먼저 정렬하고 `LIMIT 13`을 적용했다. 이후 Python이 12개를 선택하고 검증되지 않은 국명을 제거해 영어로 바꿨다. 그 결과 영어 이름 사이에 한국어 이름이 섞이고, 제한 밖의 검증 국명 후보를 되살릴 수 없었다.

실제 수정 전 NAS TEST의 청둥오리 같은 속 목록은 `고방오리, Laysan Duck, Red-billed Teal, 쇠오리, 흰뺨검둥오리, African Black Duck, 미국오리, …`였다. 곤줄박이 같은 과 목록도 `노랑배박새, Crested Tit, 쇠박새, 진박새, Eurasian Blue Tit, …`처럼 섞였다. 공개 API를 실제 Chrome에서 호출해 응답을 확보했으며 HTTP 모의 결과가 아니다.

- `src/robingraph/retrieval/related_species.py`: 생태 검색과 동일하게 기존 검증 국명표를 Cypher 매개변수로 전달한다. 종 ID로 참조표를 찾고 학명·원자료 영어 이름까지 정확히 일치할 때만 국명을 사용한다. 이 대조와 한국어 이름 우선 정렬을 `LIMIT 13` 전에 적용한다. 한국어 이름이 없는 후보는 영어 이름, 영어도 없으면 학명으로 정렬하며 종 ID로 동률을 해소한다.
- `_parse_lineage_items`의 기존 국명 재검증을 유지해 응답에 국명 출처 URL·`source-reference` 상태를 제공한다. 같은 속 12개·같은 과의 다른 속 12개, 추가 후보 유무, 대상 종 제외, 허용된 분류판·개념집합·관계 범위와 출처 검증은 유지한다.
- `tests/test_related_species.py`: 검증표 전달, 국명 없는 그래프의 검증 국명 표시, 학명 또는 영어 이름 불일치 시 영어 대체, 기존 오류·범위 계약을 검증한다.
- `tests/test_related_species_integration.py`: UUID로 격리한 실제 Neo4j 분류·후보를 생성해 `LIMIT 13` 이전 선택을 검증하고 `finally`에서 테스트 노드를 삭제한다. 검증 국명표는 합성 테스트 입력이며 Cypher 실행은 실제 DB다.
- `docs/korean-display-names.md`: 같은 속·과의 국명 우선 선택과 TOP 3 점수 순위 유지 정책을 명시했다.

주 담당이 원인 확인·서버 수정·모의 테스트·실제 NAS 전후 비교·배포·문서화를 담당했다. `progressive_review`가 독립 검토로 제한 이후 재정렬만으로 누락을 복구할 수 없음을 확인하고, 실제 Neo4j의 13개 제한 경계·잘못된 이름 참조·개념집합/관계 범위·같은 속 제외 통합 테스트를 작성했다. 실제 DB 전체 실행은 주 담당이 수행했다. 최종 커밋 독립 검토에서 배포 차단 문제가 없었으며 협업 담당의 별도 관련 단위 테스트 5개도 모두 통과했다.

- 관련 서버 모의 테스트: `python -m unittest tests.test_related_species tests.test_ecological_relations tests.test_similar_species -v` **19개 통과, 실패 0, 건너뛰기 0**. 국명 참조·영어 대체·기존 점수 순서·오류 처리를 확인했다. DB/API를 실제 호출한 결과는 아니다.
- 전체 Python: `/tmp/rg010-venv/bin/python /tmp/rg013-integration-rerun.py` **610개 통과, 실패 0, 건너뛰기 0**, 37.678초. `.env`에서 DB 설정만 테스트 프로세스에 주입하고 실제 전용 PostgreSQL/Neo4j 통합 검증을 활성화했다. 외부 모델 API 키는 이 실행에 주입하지 않아 Jev 호출은 모의 검증이다. UUID 임시 PostgreSQL 스키마는 실행 후 삭제했다.
- 새 실제 Neo4j 테스트: 14개 미검증 raw 국명 후보와 뒤쪽의 검증 국명 후보를 생성해 **검증 국명 1개 + 영어 후보 12개**가 실제 `LIMIT 13` 결과에 포함되는 것을 확인했다. 학명/영어 이름 불일치 2개는 국명 없이 영어를 유지한다. 대상 종·다른 개념집합·다른 개념집합 관계는 제외되고, 같은 과 탐색은 같은 속을 제외한 다른 속 후보 1개만 반환했다. UUID 테스트 노드는 `finally`에서 정리했다.
- 전체 프런트엔드: `node --test tests/frontend/*.test.js` **164개 통과, 실패 0, 건너뛰기 0**. 기존 국명 표시·비교 카드·분류 화면 회귀를 검증했다. 브라우저/DB 모의 테스트다.
- `graphify update .` AST 갱신 성공. 기존 SQL 추출 의존성 누락·기호 없는 파일·커뮤니티 이름 갱신 안내가 있었으며 실행 실패는 없었다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/2xx 검색·RAG·그래프 질의/2026-10-08-근연종-한국어우선-NAS-TEST배포]]
- [[Dev/index|Dev 인덱스]]
