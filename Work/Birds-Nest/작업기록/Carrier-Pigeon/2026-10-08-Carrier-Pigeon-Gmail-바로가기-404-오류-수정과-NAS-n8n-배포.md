---
created: 2026-10-08
date: 2026-10-08
project: Birds-Nest
type: worklog
status: completed
tags:
  - birds-nest
  - n8n
  - carrier-pigeon
  - gmail
  - discord
  - nas
  - homelab
  - bugfix
  - production
---

# Carrier Pigeon 워크플로우 Gmail 바로가기 404 오류 수정 및 NAS n8n 배포

## 요약

Discord `전서구` 채널로 발송되는 메일 알림 메시지의 `[Gmail 바로가기]` 링크 클릭 시, Google 웹 서버로부터 **`Gmail Temporary Error (404)`** 가 발생하며 메일 화면에 접속되지 않던 문제를 해결했다.

원인은 Gmail의 다중 계정 URL 구조상 URL 경로 세그먼트(`/mail/u/{id}/`)에 숫자 인덱스(0, 1...)가 아닌 이메일 주소(`.../u/kimhippowork@gmail.com/...`)가 전달되어 구글 프론트엔드 ESF에서 즉시 HTTP 404를 반환하고 클라이언트 라우팅이 차단되었기 때문이다.

이메일 주소를 경로가 아닌 **`?authuser=` 쿼리 파라미터**로 전달하는 표준 형식(`https://mail.google.com/mail/u/?authuser=kimhippowork@gmail.com#all/${threadId}`)으로 교체하고, 로컬 Git 저장소 반영 및 **NAS 운영 n8n (`workflow.dove-nest.com`)**에 REST API를 통해 실시간 업데이트 및 Publish(배포)를 완료했다. 이후 실제 메일 쓰레드 ID(`1a119fe62f575559`) 기반 테스트 메시지를 디스코드로 발송하여 정상 접속을 최종 검증했다.

## 완료 결과

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **원인 규명** | Gmail URL 경로 형식 오류 확인 | `/mail/u/이메일/` 형태는 구글 ESF 웹 서버에서 HTTP 404를 반환함을 curl 테스트로 입증 |
| **링크 표준화** | `?authuser=` 쿼리 파라미터 적용 | 브라우저 다중 계정 로그인 환경에서도 `kimhippowork@gmail.com` 세션을 자동으로 찾는 안정적인 URL로 전환 |
| **코드 수정** | `Prep Gmail Data` 노드 수정 | `n8n/carrier_pigeon/workflows.json` 및 활성 버전 스냅샷 내 `mailLink` 생성 코드 갱신 |
| **NAS n8n 실서버 배포** | n8n REST API 실시간 반영 & Publish | `[mail alarm] carrier pigeon`(`lAhoIgivFiB59z8p`)에 즉시 반영, `activeVersionId` 갱신 및 트리거 재활성화 |
| **실서비스 검증** | 실제 쓰레드 기반 Discord 테스트 | 실제 수신 메일(`1a119fe62f575559`) 링크를 디스코드 `전서구` 채널로 발송하여 정상 메일함 오픈 확인 |
| **형상 관리** | Git 커밋 및 원격 저장소 푸시 | 커밋 `efc6051` 작성 후 `origin/dev-mac`으로 푸시 완료 |

---

## 1. 문제 현상 및 원인 분석

### 발생 현상
Discord 채널(`전서구`)의 메일 알림 카드 하단 `[Gmail 바로가기]`를 클릭하면 브라우저에 다음과 같은 Google 서버 에러 페이지가 출력됨:
* **제목**: `Gmail Temporary Error (404)`
* **메시지**: `We're sorry, but your account is temporarily unavailable. We apologize for the inconvenience and suggest trying again in a few minutes.`

### 원인 분석
기존 `Prep Gmail Data` 노드의 링크 생성 로직:
```javascript
const mailLink = threadId ? `https://mail.google.com/mail/u/kimhippowork@gmail.com/#all/${threadId}` : '';
```
* Google Gmail 웹 서버의 라우팅 규칙상 `/mail/u/{인덱스번호}/` (예: `/mail/u/0/`, `/mail/u/1/`) 형식만 지원됨.
* 경로 세그먼트에 이메일 주소(`.../u/kimhippowork@gmail.com/...`)를 직접 넣을 경우 Google ESF 서버가 URL을 해석하지 못하고 즉시 HTTP 404를 반환함. 뒤의 `#all/...` 클라이언트 해시가 브라우저 SPA로 전달되기 전에 서버 레벨에서 튕기는 현상.

### HTTP 상태 코드 검증 (curl)
```bash
$ curl -s -o /dev/null -w "%{http_code}\n" "https://mail.google.com/mail/u/kimhippowork@gmail.com/"
404

$ curl -s -o /dev/null -w "%{http_code}\n" "https://mail.google.com/mail/u/?authuser=kimhippowork@gmail.com"
302 (정상 계정 라우팅)
```

---

## 2. 해결 방안: URL 구조 변경

구글 계정이 여러 개 로그인되어 있는 환경에서도 특정 계정의 메일함으로 바로 연결되도록 이메일을 경로가 아닌 `?authuser=` 쿼리 파라미터로 전달:

```javascript
// 변경 전 (오류 발생)
const mailLink = threadId ? `https://mail.google.com/mail/u/kimhippowork@gmail.com/#all/${threadId}` : '';

// 변경 후 (정상 동작)
const mailLink = threadId ? `https://mail.google.com/mail/u/?authuser=kimhippowork@gmail.com#all/${threadId}` : '';
```

* 브라우저에 여러 구글 계정이 로그인되어 있어도 `kimhippowork@gmail.com` 세션을 자동으로 매칭하여 해당 메일 쓰레드로 바로 이동.

---

## 3. 적용 및 배포 과정

### 1) 로컬 Git 저장소 파일 수정
* 파일: `n8n/carrier_pigeon/workflows.json`
* 메인 노드 정의(Line 110) 및 `activeVersion` 스냅샷(Line 1288)의 `Prep Gmail Data` 노드 코드 수정.

### 2) NAS n8n 실서버 반영 및 Publish
* 대상: `https://workflow.dove-nest.com` (`lAhoIgivFiB59z8p` - `[mail alarm] carrier pigeon`)
* n8n Public REST API(`PUT /api/v1/workflows/lAhoIgivFiB59z8p`)를 통해 `Prep Gmail Data` 노드 코드를 실시간 업데이트.
* `POST /api/v1/workflows/lAhoIgivFiB59z8p/activate` 엔드포인트를 호출하여 트리거 리스너(`Unread Gmail Trigger`) 재등록 및 `activeVersionId`(`e35a4619-a29b-4a25-94ed-eed2ffe17270`) 배포 상태 확정.
* 로컬 테스트베드 `n8n-test` 데이터베이스에도 동일한 변경 사항 동기화.

---

## 4. 실운영 검증

실제 수신되었던 메일의 쓰레드 ID(`1a119fe62f575559`)를 사용하여 Discord `전서구` 채널에 테스트 메시지 발송:

```markdown
🔒 [인증/알림 메일 수신 - 실제 메일 테스트]
• 발신자: "Dove. J. Kim" <notifications@github.com>
• 제목: [EvoDmiK/RobinGraph] Run failed: Tests - dev (66bef27)
• 내용 요약:
>>> EvoDmiK/RobinGraph 저장소의 Tests 워크플로우 실패 알림 (Fixture windows-latest 실패)

[Gmail 바로가기]
- https://mail.google.com/mail/u/?authuser=kimhippowork@gmail.com#all/1a119fe62f575559
```

* **검증 결과**: 링크 클릭 시 404 오류 없이 대상 메일 상세 화면으로 즉시 정상 오픈됨을 확인.

---

## 5. Git 형상 관리

* **브랜치**: `dev-mac`
* **커밋**: `efc6051` (`fix(n8n): use authuser query param for Gmail thread links in carrier_pigeon`)
* **원격 반영**: `origin/dev-mac`으로 push 완료.

---

## 관련

- [[Home]]
- [[Work/Birds-Nest/index]]
- [[2026-10-02-Jev-AI-기반-carrier-pigeon-개편과-n8n-테스트베드-구축]]
