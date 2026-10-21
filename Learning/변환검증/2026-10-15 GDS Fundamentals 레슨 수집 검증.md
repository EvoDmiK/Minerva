---
date: 2026-10-15
tags: [verification, neo4j, graph-data-science, learning]
source_url: https://graphacademy.neo4j.com/courses/gds-fundamentals/
---

# GDS Fundamentals 레슨 수집 검증

## 결과

공식 과정 목차의 **4개 모듈·30개 레슨**에 해당하는 공개 GitHub 원본을 수집해 레슨별 Markdown과 통합 Markdown으로 변환했다. 저장소에만 있는 추가 Course summary 1개는 별도 extras로 분리했다. **이 노트는 검증 기록이며, 전체 레슨 본문을 Vault에 저장한 것은 아니다.** 실제 학습자료는 Discord에 전달하는 ZIP에 있다.

- 포함: 영어 원문 설명, 코드, 퀴즈 46개와 정답·해설, 본문에서 사용하는 그림 파일 58개.
- 구성: `README.md`(목차), `lessons/`(30개 레슨), `ALL-LESSONS.md`(합본), `extras/`(추가 레슨), `original/`(원문 AsciiDoc·Cypher 95개), `assets/`(그림), 검증·출처 메타데이터.
- 저장소: https://github.com/neo4j-graphacademy/courses
- 고정한 원본 커밋: `ead656478b8a66ae25cb1eafdd1ee74018541c3c`.
- 상위 `package.json`의 라이선스 표기: `ISC`. 실제 메타데이터를 ZIP의 `UPSTREAM-package.json`에 보존했다.

## 실제 검증

- 사이트 목차 30개 경로와 공개 저장소 레슨 30개를 일대일 매핑.
- 모듈별 레슨 수: 3 / 11 / 10 / 6.
- 다운로드한 원본 파일 182개의 Git blob SHA-1이 저장소 tree와 모두 일치.
- 원문과 변환문의 코드 블록 200개를 별도 대조해 줄바꿈·주석·공백 보존 확인.
- 퀴즈 46개 모두 레슨에 include 확장 및 질문 제목 포함 확인.
- 목차·합본·레슨의 로컬 링크 157건이 실제 파일로 연결됨을 확인.
- ZIP 189개 항목 CRC 검사 및 압축 전후 모든 파일의 바이트 일치 확인.
- 본문·주의문·코드·그림·퀴즈·정답 표본 직접 읽기 확인.

## 한계

- 로그인된 강의 본문을 추출한 것이 아니라 같은 경로의 공개 저장소 원본을 변환했다. 현재 사이트 배포본과 문장별 동일성은 미검증이다.
- 영상·자막, 온라인 채점·수강 진도, Neo4j 샌드박스와 실습 DB, 연결된 외부 문서는 미포함이다.
- 코드가 실제 DB에서 실행되는지 검증하지 않았다.
- 그림은 원래 픽셀 크기를 유지한 품질 85 WebP 재인코딩본이다. 원본 이미지 바이트는 로컬 원본 수집 디렉터리에 남아 있다.
- 원본의 `images/article_rank_header.png` 경로 1건은 존재하지 않아 해당 레슨에 경고로 표시했다. `article_rank_header.png.png`를 같은 그림으로 가정해 바꾸지 않았다.
- 파일 번호는 공개 원본의 order 메타데이터 기준이며, 사이트 목차의 첫 모듈 표시 순서와 일부 다르다.

## 산출물 위치

- 로컬 artifact 디렉터리: `/opt/data/agent-artifacts/local/2026-10-15-gds-fundamentals-lessons/`
- 배포용 ZIP: `gds-fundamentals-lessons.zip`
- ZIP 크기: 5,241,650 bytes.
- SHA-256: `7eafb8fe22d81085e29089160f398a2685a7d835ae6851129496744a32e7e336`.
- 상세 증거: `verification-evidence.json`, `conversion-results.json`, `source-tree.json`.

## 읽는 방법

ZIP을 풀고 `README.md`에서 레슨을 선택하거나 `ALL-LESSONS.md`를 연다. Obsidian에서 읽으려면 압축을 푼 `gds-fundamentals` 폴더 전체를 원하는 Vault 위치에 넣는다. `assets/`도 같이 옮겨야 그림이 보인다.
