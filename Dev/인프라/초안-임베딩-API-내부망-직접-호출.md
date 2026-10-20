---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-02-임베딩-API-내부망-직접-호출]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# 임베딩 API 내부망 직접 호출

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-02-임베딩-API-내부망-직접-호출]] · 분류 근거 {"인프라":24,"자동화":0,"관측성":3,"데이터":3}

## 1. 개요 및 목적

NAS의 RobinGraph가 Mac mini의 Jina 임베딩 서버를 공개 주소(`https://embed.dove-nest.com`)로 호출하고 있었다. 같은 집 안의 서버인데도 요청이 Cloudflare 홍콩(HKG) 데이터센터를 왕복해 호출마다 0.4~0.6초가 더해졌다. NAS 배포 설정만 Mac mini 내부망 주소로 바꿔 호출 시간을 약 4분의 1로 줄였다.

| 경로 | 질문 1건 임베딩 |
| --- | --- |
| 변경 전: NAS → Cloudflare(HKG) → NAS NPM → Mac mini | 0.79초 (중앙값), 최소 0.57초 |
| 변경 후: NAS → Mac mini 내부망 | 0.20~0.23초 |

## 2. 핵심 아키텍처 및 원칙

- 요약
- 왜 처음부터 공개 주소였나
- 인증서와 경로는 별개
- 변경
- 적용 방식
- 검증
- 트러블슈팅 메모
- 남은 일
- 관련
- 상세 보완 — 2026-10-05
- 측정 결과를 재사용할 때의 기준
- 설정 변경과 코드 배포의 차이
- 후속 기록과 미확인 항목

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

인증서를 Let's Encrypt로 바꿔도 Cloudflare 프록시가 켜져 있으면 똑같이 홍콩을 거친다. 경로는 DNS가 어디를 가리키느냐(프록시 여부)로 정해지고, 인증서는 그 경로의 암호화와 서버 확인만 맡는다.

| 파일 | 내용 |
| --- | --- |
| `.env.nas.prod`, `.env.nas.test` | `ROBINGRAPH_JINA_ENDPOINT`를 Mac mini 내부망 `:8765/v1/embeddings`로 변경 |
| `.env.nas.example` | 같은 값과 이유 주석 |
| `docs/nas-deployment.md` | 내부망 호출 이유, 측정값, healthz 확인 명령 갱신 |
| `.env.example` (개발용) | 공개 주소 유지 |

- `deploy_nas.sh deploy`·`update`는 이미지를 다시 빌드한다. 작업 폴더에 커밋되지 않은 코드가 있어 빌드하면 그 코드가 운영에 섞인다.
- 그래서 실행 중인 이미지와 태그가 같은지 확인한 뒤, 같은 이미지로 `docker compose up -d --no-build api`를 실행해 설정만 바꿔 컨테이너를 다시 만들었다.
- 배포 스크립트가 쓰는 대상별 값(`ROBINGRAPH_COMPOSE_PROJECT`, `ROBINGRAPH_API_CONTAINER`, `ROBINGRAPH_IMAGE` 등)을 직접 지정했다.
- test에 먼저 적용해 확인한 뒤 prod에 적용했다.

| 항목 | test | prod |
| --- | --- | --- |
| 컨테이너 health | healthy | healthy |
| `deploy_nas.sh verify` | 통과 (`deployment_target: test`) | 통과 (`deployment_target: prod`) |
| 앱 임베딩 클라이언트 `embed_query` | 512차원, 0.20초 | 512차원, 0.23초 |
| 32개 묶음 `embed_documents` | 1.39초 | 0.97초 |
| 임베딩 서버 healthz (내부망) | — | `ready`, `mps`, `float16` |
| 공개 사이트 | — | 200 |

| 검증 | 확인한 사실 |
|---|---|
| embed_query | 같은 애플리케이션 클라이언트가 512차원 결과를 받음 |
| embed_documents | 32개 묶음 요청의 반환과 소요 시간 확인 |
| healthz | 해당 시점 서버 준비 상태·가속 장치·정밀도 확인 |
| API health | TEST·PROD 프로세스의 정상 상태 확인 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-10-02-임베딩-API-내부망-직접-호출]]
- [[Dev/index|Dev 인덱스]]
