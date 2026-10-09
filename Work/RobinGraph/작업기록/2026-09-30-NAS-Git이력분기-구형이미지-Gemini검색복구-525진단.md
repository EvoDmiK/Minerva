---
date: 2026-09-30
project: RobinGraph
type: incident-and-deployment-log
status: resolved
deployment_target: test
branch: nas-test-20260930
commit: f3b77e5
tags:
  - project/robingraph
  - nas
  - docker
  - git
  - gemini
  - troubleshooting
updated: 2026-10-05
---

# RobinGraph — NAS Git 이력 분기·구형 이미지 교체·Gemini 검색 복구

## 요약

NAS에서 한국어 질문에 “일치하는 근거 문서를 확인하지 못했습니다”가 반복됐다. 실제 DB에는 PMC 문헌 청크 55개가 있었고 영어 검색도 정상이라 문헌 미적재 문제가 아니었다.

SSH로 확인한 결과, NAS의 Git 이력이 원격과 갈라져 **이전 코드와 Gemini 모듈이 없는 Docker 이미지가 실행 중**이었다. 기존 `dev`를 보존하고 최신 원격 코드의 새 배포 브랜치를 만든 뒤 TEST 컨테이너를 재빌드했다.

최종 확인에서 NAS 내부와 공용 도메인 모두 한국어 문헌 검색·Gemini 인용 답변이 정상 동작했다.

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| NAS 체크아웃 | `0b6ec18` | `f3b77e5` |
| Git 상태 | `dev...origin/dev [ahead 54, behind 59]` | 최신 원격 기준 새 배포 브랜치 |
| 실행 이미지의 Gemini 모듈 | 없음 | 있음 |
| 한국어 문헌 검색 | 결과 0개 | PMC 결과 3개 |
| 답변 | 근거 부족 | 한국어 설명·PMC 인용 |
| 공용 도메인 요청 | 진단 중 403·525 보고 | 최종 POST HTTP 200 |

> [!note] 이번 조치의 범위
> 기존 구현을 최신 버전으로 배포한 작업이다. 이번 장애 대응에서 새 애플리케이션 코드를 작성하거나 DB에 문헌을 다시 적재하지 않았다. TEST API를 재생성했고 PROD API 재배포는 수행하지 않았다.

이전 기록: [[Work/RobinGraph/작업기록/2026-09-30-한국어검색-Gemini-PostgreSQL-연결수정-NAS배포준비]]

## 1. 관찰한 증상과 원인 분리

### 한국어 검색 실패

UI의 근거 문서 모드에서 다음 질문이 보류됐다.

> 로스앤젤레스에서 기후 변화와 토지 이용 변화가 조류 다양성에 어떤 영향을 줬어?

영어 질문 `climate land use Los Angeles birds`는 PMC 문헌 3개를 반환했다. 한국어 질문은 결과가 없었으며 변환 성공·실패 경고도 없었다.

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

다음 사실을 구분했다.

- DB에는 `:PmcPilot:HybridSearchChunk` 55개가 있었다.
- 영어 fulltext 검색으로 실제 PMC 문단과 출처가 나왔다.
- 영어 응답은 생성된 설명 대신 기본 문구 “근거 문서를 확인했습니다”였다.
- 한국어 검색어 확장 경고가 없었다.

따라서 Gemini 설정 또는 실행 이미지의 구현 상태를 확인했다.

### 자동 분류 실패

별도 화면에서 자동 모드는 “질문의 종류를 판단하지 못했습니다”와 자동 분류 불확실 경고를 반환했다. 이것은 근거 모드의 검색 결과 없음과 다른 경로이다.

이번 복구 검증은 `intent: evidence`를 명시했다. **자동 분류 경로까지 정상이라고 검증한 것은 아니다.**

## 2. 도메인 525와 NPM 포트 확인

사용자는 공용 도메인 요청에서 403 이후 525를 관찰했다. 이 문제는 한국어 문헌 검색 실패와 따로 점검했다.

NPM Proxy Host의 애플리케이션 연결 설정은 다음과 같았다.

```text
Domain: aviary-test.dove-nest.com
Scheme: http
Forward host: robingraph-api-test
Forward port: 8000
Access: Publicly Accessible
SSL certificate: aviary-test.dove-nest.com
```

### 처음 HTTPS 테스트가 향한 곳

NAS 호스트의 `127.0.0.1:443`으로 테스트했더니 UGREEN 자체 서명 인증서를 받았다.

```text
subject: CN=UGREEN
issuer: CN=UGREEN
curl: (60) SSL certificate problem: self-signed certificate
```

Docker 포트 확인 결과 NPM은 호스트의 다른 포트로 공개되고 있었다.

| NAS 호스트 포트 | 실제 서비스 |
|---|---|
| 443 | UGREEN 인증서를 제공하는 관리 서비스 |
| 14443 | NPM 컨테이너의 HTTPS 443 |
| 18080 | NPM 컨테이너의 HTTP 80 |
| 81 | NPM 관리 UI |

따라서 `127.0.0.1:443` 테스트는 NPM 인증서를 확인한 것이 아니었다.

### NPM에 직접 연결한 결과

```sh
curl -v --resolve aviary-test.dove-nest.com:14443:127.0.0.1 \
  https://aviary-test.dove-nest.com:14443/health
```

다음 결과를 확인했다.

- TLS 1.3 연결 성공.
- 인증서 도메인: `aviary-test.dove-nest.com`.
- 발급자: Let's Encrypt.
- 인증서 검증 성공.
- HTTP/2 200.
- 응답 `deployment_target: test`, `mode: neo4j`.

일반적인 공인 IP 포워딩 구성에서는 외부 TCP 443이 NAS 내부 `14443`으로, 외부 TCP 80이 내부 `18080`으로 연결되는지 확인하도록 안내했다.

> [!important] 525의 확인 범위
> NPM 직접 연결이 정상인 것은 확인했다. 실제 공유기·Cloudflare 설정 변경 내역을 직접 확인한 것은 아니므로 특정 포워딩 설정을 525의 확정 원인으로 기록하지 않는다. SSH 점검 당시 컨테이너의 공용 도메인 health도 200이었고, 재배포 후 외부 채팅 POST도 200이었다. 당시의 525는 최종 점검에서 재현되지 않았다.

Python 요청에는 명시적인 User-Agent를 넣었다. 403의 정확한 차단 규칙은 확정하지 않았으며, User-Agent 변경이 525를 해결했다는 의미도 아니다.

## 3. SSH로 확인한 실제 배포 상태

기본 SSH 인증은 거부됐으나 NAS 전용 키 `~/.ssh/nas_codex_ed25519`를 명시하자 접속됐다. 호스트 키 검증을 유지했다.

```text
NAS: DXP2800-B9B3
접속 경로: 100.93.181.111:99
배포 디렉터리: /volume3/RobinGraph
TEST 컨테이너: robingraph-api-test
이미지 태그: robingraph-api:test-local
```

비밀값을 출력하지 않고 실행 컨테이너를 진단했다.

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

변경 전 결과:

```text
Gemini key set: True
Gemini model: gemini-3.5-flash-lite
Gemini module: False
```

**키·모델은 이미 설정되어 있었으나 실행 코드에 Gemini 모듈이 없었다.** 환경 변수만 수정해도 기존 이미지에 새 기능이 생기지는 않는다.

### Git 상태

```sh
git -C /volume3/RobinGraph status --short --branch
git -C /volume3/RobinGraph log -1 --oneline
git -C /volume3/RobinGraph log -1 origin/dev --oneline
```

확인한 값:

```text
NAS HEAD: 0b6ec18 Prepare isolated NAS test and production API targets
Remote dev: f3b77e5 Improve Korean literature search and document NAS test deployment
Status: dev...origin/dev [ahead 54, behind 59]
Origin: https://github.com/EvoDmiK/RobinGraph.git
```

원격 참조에는 최신 커밋이 있었으나 현재 체크아웃은 예전 코드였다. NAS `dev`에만 있는 이력을 보존하면서 최신 원격 코드로 배포해야 했다.

## 4. 실제 수정: 브랜치 보존 후 최신 이미지 재빌드

사용자 승인 후 NAS에서 실행했다. 먼저 작업 트리가 깨끗한지 확인했고, 기존 `dev`를 재설정하지 않고 새 브랜치를 만들었다.

```sh
cd /volume3/RobinGraph

# 로컬 변경이 있으면 중단
test -z "$(git status --porcelain)"

git fetch origin dev
git switch -c nas-test-20260930 --track origin/dev

ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh deploy
```

결과:

- 기존 NAS `dev` 브랜치와 해당 이력 보존.
- 새 `nas-test-20260930` 브랜치는 `origin/dev` 추적.
- 최신 `f3b77e5`의 코드를 Docker 이미지에 포함.
- 기존 TEST 환경 파일과 `robingraph-api:test-local` 태그 재사용.
- `robingraph-api-test` 컨테이너 재생성.
- 배포 스크립트가 `RobinGraph API is healthy` 출력.

빌드 중 buildx 플러그인이 없다는 경고가 있었으나 classic Docker builder로 이미지 빌드와 배포가 성공했다. 이를 해결하기 위한 별도 플러그인 설치는 하지 않았다.

환경 설정은 그대로 사용했다.

```dotenv
GEMINI_API_KEY=<기존 설정 유지>
ROBINGRAPH_GEMINI_MODEL=gemini-3.5-flash-lite
```

API 키와 비밀번호는 노트에 기록하지 않았다.

## 5. 복구 검증

### 새 컨테이너의 구현 확인

```python
from robingraph.generation import GeminiAnswerer

print(hasattr(GeminiAnswerer, "english_search_terms"))
```

재배포 후:

```text
Gemini key set: True
Gemini model: gemini-3.5-flash-lite
English search code: True
```

### NAS 내부 API 확인

동일한 한국어 질문을 `http://127.0.0.1:8000/v1/chat`으로 호출했다.

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

결과:

- PMC 청크 `p005`, `p022`, `p019` 반환.
- 경고: “한국어 질문에 영어 검색어를 추가해 문헌을 검색했습니다.”
- 한국어 Gemini 답변 생성.
- 답변에 `[pmc-pilot:PMC9946348:p019]` 인용 포함.

답변은 로스앤젤레스의 건조화가 조류의 지속성과 정착을 낮추고, 도시화에 따른 감소를 증폭했다는 논문의 내용을 설명했다.

### 공용 도메인 확인

개발 환경에서 `https://aviary-test.dove-nest.com/v1/chat`을 직접 호출했다.

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

최종 출력 요약:

```text
Public HTTP: 200
검색 결과 수: 3
한국어 검색어 변환 경고: 있음
한국어 생성 답변: 있음
PMC 인용: pmc-pilot:PMC9946348:p019
```

브라우저에서는 새로고침 후 조회 유형을 **근거 문서**로 선택해 같은 질문을 입력하도록 안내했다.

> [!note] 검증의 한계
> 이번 NAS 복구 확인은 명시적 근거 모드, 해당 PMC 질문, 실제 인용 연결을 대상으로 했다. 전체 질문의 검색 품질·자동 의도 분류·간헐적인 525의 완전한 소멸까지 보증하는 검증은 아니다. 이번 재배포에서 새 전체 테스트 스위트를 실행한 것도 아니다.

## 6. 다음 배포 때 확인할 것

NAS 배포 브랜치에서 최신 원격을 받고 이미지를 다시 빌드한다.

```sh
cd /volume3/RobinGraph
git switch nas-test-20260930
git pull --ff-only origin dev

ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh deploy
ROBINGRAPH_DEPLOY_TARGET=test sh scripts/deploy_nas.sh verify
```

배포 전후의 코드·기능 상태를 함께 확인한다.

```sh
git log -1 --oneline

docker exec robingraph-api-test python -c \
'from robingraph.generation import GeminiAnswerer; print(hasattr(GeminiAnswerer, "english_search_terms"))'
```

- `git pull`만으로 실행 컨테이너가 바뀌지 않는다. 이미지 빌드·컨테이너 교체까지 필요하다.
- `/health` 200만으로 Gemini 기능이 최신인지 확인할 수 없다. 실제 검색·생성 요청을 검증한다.
- `ahead/behind`가 동시에 나타나면 이력 분기를 확인하고 기존 작업을 보존한다.
- NPM TLS 테스트는 NAS의 실제 호스트 매핑 포트 `14443`을 사용한다.
- 자동 모드 문제는 명시적 근거 모드와 별도로 평가한다.

## 관련 기록

- [[Work/RobinGraph/작업기록/2026-09-30-한국어검색-Gemini-PostgreSQL-연결수정-NAS배포준비]]
- [[Work/RobinGraph/작업기록/2026-09-29-CI-수정-Gemini-연동-PMC-문헌파일럿]]
- [[Work/index|Work — 토이 프로젝트]]
- [배포에 사용한 커밋 f3b77e5](https://github.com/EvoDmiK/RobinGraph/commit/f3b77e5)

## 상세 보완 — 2026-10-05

### 장애를 구분하는 진단 순서

| 확인 층 | 판단 근거 | 이 결과만으로 판단할 수 없는 것 |
|---|---|---|
| 실행 코드 | 컨테이너에 Gemini 모듈·검색어 확장 메서드가 있는지 | 설정된 API 키의 유효성 |
| 컨테이너 내부 API | 명시적 근거 질문의 검색 청크·인용 답변 | 외부 TLS 경로 |
| NPM 직접 연결 | 올바른 호스트 포트·인증서·SNI·HTTP 응답 | Cloudflare의 모든 요청 경로 |
| 공용 도메인 | 실제 채팅 POST와 답변 내용 | 모든 의도 분류와 모든 검색어의 품질 |

환경 변수에 키가 존재하는 것과 해당 기능을 구현한 이미지가 실행되는 것은 별개다. 구형 이미지는 설정을 바꾸는 것만으로 최신 검색어 확장 기능을 얻지 못한다. health 200도 검색·생성 기능 검증을 대신하지 못한다.

### Git 이력 보존과 현재 배포 방식

당시 NAS checkout의 분기된 이력을 보존한 채 최신 원격 코드로 새 배포 브랜치를 만들었다. 이후 작업에서는 커밋 기준 릴리스 아카이브를 별도 디렉터리에 풀어 TEST 이미지를 빌드하는 방식으로 진행했다. 과거 checkout을 현재 배포 기준으로 간주하거나 원격에 맞춰 강제로 초기화하지 않는다.

배포 식별자는 커밋·이미지 태그·릴리스 경로를 함께 기록한다. TLS 장애와 검색 실패도 별개로 기록해, 이미지 교체가 525의 모든 원인을 해결했다는 주장으로 확대하지 않는다.

### 재현할 때 남길 증거

- 요청의 의도와 질문, HTTP 상태, 실제 근거 ID와 생성 답변의 인용.
- 확인한 컨테이너·이미지 태그와 배포 커밋.
- TLS 요청이 NPM으로 향했는지 확인한 포트와 서버 이름.
- 정상으로 확인한 경로 및 확인하지 못한 경로.

현재 TEST 배포 기록은 [[Work/RobinGraph/작업기록/2026-10-05-RG003-생태관계탐색-NAS배포|RG-201 생태 관계 탐색·NAS TEST 검증]], 전체 구조는 [[Work/RobinGraph/RobinGraph 구현·데이터·검증 가이드|구현·데이터·검증 가이드]]에서 이어서 확인한다. 이 보완에서 NAS나 TLS를 새로 점검한 것은 아니다.
