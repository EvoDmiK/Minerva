---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "자동화"
status: draft
source_project: "Birds-Nest"
source_work_log: "[[Work/Birds-Nest/작업기록/Carrier-Pigeon/2026-10-08-Carrier-Pigeon-Gmail-바로가기-404-오류-수정과-NAS-n8n-배포]]"
tags:
  - dev
  - draft
  - "birds-nest"
---

# Carrier Pigeon 워크플로우 Gmail 바로가기 404 오류 수정 및 NAS n8n 배포

> 자동 증류 초안 · 원천 [[Work/Birds-Nest/작업기록/Carrier-Pigeon/2026-10-08-Carrier-Pigeon-Gmail-바로가기-404-오류-수정과-NAS-n8n-배포]] · 분류 근거 {"인프라":2,"자동화":21,"관측성":0,"데이터":0}

## 1. 개요 및 목적

Discord `전서구` 채널로 발송되는 메일 알림 메시지의 `[Gmail 바로가기]` 링크 클릭 시, Google 웹 서버로부터 **`Gmail Temporary Error (404)`** 가 발생하며 메일 화면에 접속되지 않던 문제를 해결했다.

원인은 Gmail의 다중 계정 URL 구조상 URL 경로 세그먼트(`/mail/u/{id}/`)에 숫자 인덱스(0, 1...)가 아닌 이메일 주소(`.../u/user@example.com/...`)가 전달되어 구글 프론트엔드 ESF에서 즉시 HTTP 404를 반환하고 클라이언트 라우팅이 차단되었기 때문이다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 완료 결과
- 1. 문제 현상 및 원인 분석
- 발생 현상
- 원인 분석
- HTTP 상태 코드 검증 (curl)
- 2. 해결 방안: URL 구조 변경
- 3. 적용 및 배포 과정
- 1) 로컬 Git 저장소 파일 수정
- 2) NAS n8n 실서버 반영 및 Publish
- 4. 실운영 검증
- 5. Git 형상 관리
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```javascript
const mailLink = threadId ? `https://mail.google.com/mail/u/user@example.com/#all/${threadId}` : '';
```

```bash
$ curl -s -o /dev/null -w "%{http_code}\n" "https://mail.google.com/mail/u/user@example.com/"
404

$ curl -s -o /dev/null -w "%{http_code}\n" "https://mail.google.com/mail/u/?authuser=user@example.com"
302 (정상 계정 라우팅)
```

```javascript
// 변경 전 (오류 발생)
const mailLink = threadId ? `https://mail.google.com/mail/u/user@example.com/#all/${threadId}` : '';

// 변경 후 (정상 동작)
const mailLink = threadId ? `https://mail.google.com/mail/u/?authuser=user@example.com#all/${threadId}` : '';
```

```markdown
🔒 [인증/알림 메일 수신 - 실제 메일 테스트]
• 발신자: "Dove. J. Kim" <notifications@github.com>
• 제목: [EvoDmiK/RobinGraph] Run failed: Tests - dev (66bef27)
• 내용 요약:
>>> EvoDmiK/RobinGraph 저장소의 Tests 워크플로우 실패 알림 (Fixture windows-latest 실패)

[Gmail 바로가기]
- https://mail.google.com/mail/u/?authuser=user@example.com#all/<threadId>
```

## 4. 검증 근거 및 트러블슈팅

원인은 Gmail의 다중 계정 URL 구조상 URL 경로 세그먼트(`/mail/u/{id}/`)에 숫자 인덱스(0, 1...)가 아닌 이메일 주소(`.../u/user@example.com/...`)가 전달되어 구글 프론트엔드 ESF에서 즉시 HTTP 404를 반환하고 클라이언트 라우팅이 차단되었기 때문이다.

이메일 주소를 경로가 아닌 **`?authuser=` 쿼리 파라미터**로 전달하는 표준 형식(`https://mail.google.com/mail/u/?authuser=user@example.com#all/${threadId}`)으로 교체하고, 로컬 Git 저장소 반영 및 **NAS 운영 n8n (`workflow.dove-nest.com`)**에 REST API를 통해 실시간 업데이트 및 Publish(배포)를 완료했다. 이후 실제 메일 쓰레드 ID(`<threadId>`) 기반 테스트 메시지를 디스코드로 발송하여 정상 접속을 최종 검증했다.

| 구분 | 변경 사항 | 상세 내용 |
| --- | --- | --- |
| **원인 규명** | Gmail URL 경로 형식 오류 확인 | `/mail/u/이메일/` 형태는 구글 ESF 웹 서버에서 HTTP 404를 반환함을 curl 테스트로 입증 |
| **링크 표준화** | `?authuser=` 쿼리 파라미터 적용 | 브라우저 다중 계정 로그인 환경에서도 `user@example.com` 세션을 자동으로 찾는 안정적인 URL로 전환 |
| **코드 수정** | `Prep Gmail Data` 노드 수정 | `n8n/carrier_pigeon/workflows.json` 및 활성 버전 스냅샷 내 `mailLink` 생성 코드 갱신 |
| **NAS n8n 실서버 배포** | n8n REST API 실시간 반영 & Publish | `[mail alarm] carrier pigeon`(`lAhoIgivFiB59z8p`)에 즉시 반영, `activeVersionId` 갱신 및 트리거 재활성화 |
| **실서비스 검증** | 실제 쓰레드 기반 Discord 테스트 | 실제 수신 메일(`<threadId>`) 링크를 디스코드 `전서구` 채널로 발송하여 정상 메일함 오픈 확인 |
| **형상 관리** | Git 커밋 및 원격 저장소 푸시 | 커밋 `efc6051` 작성 후 `origin/dev-mac`으로 푸시 완료 |

실제 수신되었던 메일의 쓰레드 ID(`<threadId>`)를 사용하여 Discord `전서구` 채널에 테스트 메시지 발송:

* **검증 결과**: 링크 클릭 시 404 오류 없이 대상 메일 상세 화면으로 즉시 정상 오픈됨을 확인.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Birds-Nest/작업기록/Carrier-Pigeon/2026-10-08-Carrier-Pigeon-Gmail-바로가기-404-오류-수정과-NAS-n8n-배포]]
- [[Dev/index|Dev 인덱스]]
