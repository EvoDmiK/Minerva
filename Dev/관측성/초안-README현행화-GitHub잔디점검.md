---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "관측성"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-09-README현행화-GitHub잔디점검]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# README 현행화와 GitHub 기여도 누락 점검

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-09-README현행화-GitHub잔디점검]] · 분류 근거 {"인프라":3,"자동화":1,"관측성":6,"데이터":4}

## 1. 개요 및 목적

- 작업일: 2026-10-09
- 요청: 현재 구현에 맞게 README를 수정하고 GitHub 기여도 그래프에 커밋이 표시되지 않는 원인을 점검한다.
- 시작 기준: main·dev·origin/main·origin/dev가 `13b5361ff1a2b2cb943a478562f0b894200a11f1`로 일치하고 작업공간은 깨끗했다.

기존 README는 카드 뒷면에 출처·라이선스를 표시하고 `출처 보기 ↻` 버튼으로 뒤집는다고 설명했다. 일반 소개에 TOP 3를 자동 제공한다는 설명도 남아 있었다. 현재 구현은 카드 전체 영역의 드래그·스와이프, 답변의 통합 출처 토글, 첫 종 설명 뒤 선택적 관계 탐색을 제공한다. Jev 의도 분석과 MLflow 결과 구분, 최종 PC·모바일 카드 동작도 README에 충분히 반영되지 않았다.

## 2. 핵심 아키텍처 및 원칙

- 배경과 확인한 근거
- 변경 내용과 전후 동작
- README.md
- 저장소 Git 설정
- 협업 검토
- 실제 검증 결과
- 커밋·배포
- 남은 사항
- 최종 Git 반영 확인

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

- 작업일: 2026-10-09
- 요청: 현재 구현에 맞게 README를 수정하고 GitHub 기여도 그래프에 커밋이 표시되지 않는 원인을 점검한다.
- 시작 기준: main·dev·origin/main·origin/dev가 `13b5361ff1a2b2cb943a478562f0b894200a11f1`로 일치하고 작업공간은 깨끗했다.

graphify query로 관련 파일을 찾고 `src/robingraph/cli.py`, `api/app.py`, `api/jev_router.py`, `api/static/chat.js`, `api/static/styles.css`, `tracing.py`, 환경 변수 예시, CI workflow와 최신 검증 기록을 대조했다. 과거 설계 문서의 설명보다 실제 코드·최근 검증 기록을 우선했다.

따라서 기존 main의 **63개 커밋은 로컬 이메일 때문에 계정에 연결되지 않은 상태**다. 기본 브랜치 병합은 이미 끝났으므로 최근 커밋의 원인을 dev 미병합만으로 설명할 수 없다. GitHub 공식 문서는 계정에 연결된 이메일과 기본 브랜치 조건을 요구하고, `.local` 같은 일반 로컬 이메일을 계정에 추가할 수 없다고 설명한다. [누락된 기여도 문제 해결](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions).

로그인 계정 API의 ID는 `93193661`, login은 `EvoDmiK`였다. 기존 main 커밋 `834ddd28c12bda819209be3cda715076d773ffce`의 noreply 이메일이 실제로 EvoDmiK에 연결된 것도 REST API로 확인했다. 비공개 이메일 목록 API는 현재 토큰에 user scope가 없어 HTTP 404를 반환했다. 권한을 추가 요청하지 않았고, 공개 커밋 귀속 결과로 필요한 주소를 검증했다. API 토큰이나 인증 정보를 산출물에 저장하지 않았다.

- 목차를 추가하고 기능·빠른 실행·실제 데이터 환경·외부 API/MLflow·API·검색·배포·테스트·문서 안내로 나눴다.
- 초기 종 설명에 가용 사진과 추가 설명을 포함하고, `더 알아보기`는 관계 탐색 메뉴라는 현재 동작을 반영했다. 브라우저 요청의 `defer_discovery: true`와 서버 프로필 흐름을 대조했다.
- PC·모바일 카드 양면 드래그, 키보드 조작, 유광 반사, 화면 맞춤, 내부 스크롤 제거, 관찰 포인트, 체중 kg 표시, 두 도넛과 PC 호버를 설명했다. 삭제한 앞면·출처 버튼 안내를 제거했다.
- 출처를 답변 토글로 통합하는 정책과 국명 후보 우선·동일 그룹 점수순 TOP 3를 반영했다. 계통 50%·분류 30%·서식 10%·먹이 10% 및 점수 해석 한계를 설명했다.
- Jev, 임베딩, Gemini, MLflow 설정을 추가했다. LCEL autolog와 Jev의 명시적 자식 span을 구분하고 Gemini REST 경로에는 SDK가 필수가 아님을 명시했다.
- 합성 fixture와 실제 종 환경의 기능 범위를 구분했다. fixture gold 질문은 `/v1/answers` 예시로 안내하고, 실제 종 채팅에는 Neo4j 데이터와 PostgreSQL 활성 상태가 모두 필요함을 설명했다.
- NAS Compose가 기존 인프라를 전제로 한다는 점, Git push와 NAS 배포의 차이, 미구현 독립 설치 패키지·HippoRAG·한국 서식종 토글을 명시했다.
- 중복 NAS 런북과 과거 날짜별 작업 기록 나열을 분야별 문서 표로 정리했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-09-README현행화-GitHub잔디점검]]
- [[Dev/index|Dev 인덱스]]
