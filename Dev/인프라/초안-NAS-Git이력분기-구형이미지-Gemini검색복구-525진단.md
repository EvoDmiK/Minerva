---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-09-30-NAS-Git이력분기-구형이미지-Gemini검색복구-525진단]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# RobinGraph — NAS Git 이력 분기·구형 이미지 교체·Gemini 검색 복구

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-09-30-NAS-Git이력분기-구형이미지-Gemini검색복구-525진단]] · 분류 근거 {"인프라":30,"자동화":0,"관측성":0,"데이터":3}

## 1. 개요 및 목적

NAS에서 한국어 질문에 “일치하는 근거 문서를 확인하지 못했습니다”가 반복됐다. 실제 DB에는 PMC 문헌 청크 55개가 있었고 영어 검색도 정상이라 문헌 미적재 문제가 아니었다.

SSH로 확인한 결과, NAS의 Git 이력이 원격과 갈라져 **이전 코드와 Gemini 모듈이 없는 Docker 이미지가 실행 중**이었다. 기존 `dev`를 보존하고 최신 원격 코드의 새 배포 브랜치를 만든 뒤 TEST 컨테이너를 재빌드했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 1. 관찰한 증상과 원인 분리
- 한국어 검색 실패
- 자동 분류 실패
- 2. 도메인 525와 NPM 포트 확인
- 처음 HTTPS 테스트가 향한 곳
- NPM에 직접 연결한 결과
- 3. SSH로 확인한 실제 배포 상태
- Git 상태
- 4. 실제 수정: 브랜치 보존 후 최신 이미지 재빌드
- 5. 복구 검증
- 새 컨테이너의 구현 확인
- NAS 내부 API 확인
- 공용 도메인 확인
- 6. 다음 배포 때 확인할 것
- 관련 기록
- 상세 보완 — 2026-10-05
- 장애를 구분하는 진단 순서
- Git 이력 보존과 현재 배포 방식
- 재현할 때 남길 증거

## 3. 재사용 가능한 코드 스니펫 / 설정

```json
{
  "answer_text": "일치하는 근거 문서를 확인하지 못했습니다.",
  "warnings": [],
  "result": {
    "kind": "evidence",
    "search": {
      "mode": "fulltext",
      "results": [],
      "warnings": []
    }
  }
}
```

```text
Domain: aviary-test.dove-nest.com
Scheme: http
Forward host: robingraph-api-test
Forward port: 8000
Access: Publicly Accessible
SSL certificate: aviary-test.dove-nest.com
```

```text
subject: CN=UGREEN
issuer: CN=UGREEN
curl: (60) SSL certificate problem: self-signed certificate
```

```sh
curl -v --resolve aviary-test.dove-nest.com:14443:127.0.0.1 \
  https://aviary-test.dove-nest.com:14443/health
```

```text
NAS: DXP2800-B9B3
접속 경로: <NAS-Tailscale-IP>:99
배포 디렉터리: /volume3/RobinGraph
TEST 컨테이너: robingraph-api-test
이미지 태그: robingraph-api:test-local
```

```python
import os
import importlib.util

print("Gemini key set:", bool(os.getenv("GEMINI_API_KEY")))
print("Gemini model:", os.getenv("ROBINGRAPH_GEMINI_MODEL"))
print(
    "Gemini module:",
    importlib.util.find_spec("robingraph.generation") is not None
)
```

```text
Gemini key set: True
Gemini model: gemini-3.5-flash-lite
Gemini module: False
```

```sh
git -C /volume3/RobinGraph status --short --branch
git -C /volume3/RobinGraph log -1 --oneline
git -C /volume3/RobinGraph log -1 origin/dev --oneline
```

```text
NAS HEAD: 0b6ec18 Prepare isolated NAS test and production API targets
Remote dev: f3b77e5 Improve Korean literature search and document NAS test deployment
Status: dev...origin/dev [ahead 54, behind 59]
Origin: https://github.com/EvoDmiK/RobinGraph.git
```

```sh
cd /volume3/RobinGraph

# 로컬 변경이 있으면 중단
test -z "$(git status --porcelain)"

git fetch origin dev
git switch -c nas-test-20260930 --track origin/dev

ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh deploy
```

```dotenv
GEMINI_API_KEY=<기존 설정 유지>
ROBINGRAPH_GEMINI_MODEL=gemini-3.5-flash-lite
```

```python
from robingraph.generation import GeminiAnswerer

print(hasattr(GeminiAnswerer, "english_search_terms"))
```

```text
Gemini key set: True
Gemini model: gemini-3.5-flash-lite
English search code: True
```

```json
{
  "question": "로스앤젤레스에서 기후 변화와 토지 이용 변화가 조류 다양성에 어떤 영향을 줬어?",
  "intent": "evidence",
  "filters": {
    "kind": "evidence",
    "limit": 3
  }
}
```

```python
import json
from urllib.request import Request, urlopen

payload = {
    "question": "로스앤젤레스에서 기후 변화와 토지 이용 변화가 조류 다양성에 어떤 영향을 줬어?",
    "intent": "evidence",
    "filters": {"kind": "evidence", "limit": 3},
}
request = Request(
    "https://aviary-test.dove-nest.com/v1/chat",
    data=json.dumps(payload).encode(),
    headers={
        "Content-Type": "application/json",
        "User-Agent": "RobinGraph-Deployment-Verifier/1.0",
    },
)
with urlopen(request, timeout=90) as response:
    result = json.load(response)
    print(response.status)
    print(result["answer_text"])
    print(result["warnings"])
```

```text
Public HTTP: 200
검색 결과 수: 3
한국어 검색어 변환 경고: 있음
한국어 생성 답변: 있음
PMC 인용: pmc-pilot:PMC9946348:p019
```

```sh
cd /volume3/RobinGraph
git switch nas-test-20260930
git pull --ff-only origin dev

ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh deploy
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh verify
```

```sh
git log -1 --oneline

docker exec robingraph-api-test python -c \
'from robingraph.generation import GeminiAnswerer; print(hasattr(GeminiAnswerer, "english_search_terms"))'
```

## 4. 검증 근거 및 트러블슈팅

NAS에서 한국어 질문에 “일치하는 근거 문서를 확인하지 못했습니다”가 반복됐다. 실제 DB에는 PMC 문헌 청크 55개가 있었고 영어 검색도 정상이라 문헌 미적재 문제가 아니었다.

SSH로 확인한 결과, NAS의 Git 이력이 원격과 갈라져 **이전 코드와 Gemini 모듈이 없는 Docker 이미지가 실행 중**이었다. 기존 `dev`를 보존하고 최신 원격 코드의 새 배포 브랜치를 만든 뒤 TEST 컨테이너를 재빌드했다.

최종 확인에서 NAS 내부와 공용 도메인 모두 한국어 문헌 검색·Gemini 인용 답변이 정상 동작했다.

> [!note] 이번 조치의 범위
> 기존 구현을 최신 버전으로 배포한 작업이다. 이번 장애 대응에서 새 애플리케이션 코드를 작성하거나 DB에 문헌을 다시 적재하지 않았다. TEST API를 재생성했고 PROD API 재배포는 수행하지 않았다.

영어 질문 `climate land use Los Angeles birds`는 PMC 문헌 3개를 반환했다. 한국어 질문은 결과가 없었으며 변환 성공·실패 경고도 없었다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/7xx 배포·인프라/2026-09-30-NAS-Git이력분기-구형이미지-Gemini검색복구-525진단]]
- [[Dev/index|Dev 인덱스]]
