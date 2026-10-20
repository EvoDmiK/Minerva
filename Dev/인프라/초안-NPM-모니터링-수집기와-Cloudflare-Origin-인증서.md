---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-02-NPM-모니터링-수집기와-Cloudflare-Origin-인증서]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# NPM 모니터링 수집기와 Cloudflare Origin 인증서

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-02-NPM-모니터링-수집기와-Cloudflare-Origin-인증서]] · 분류 근거 {"인프라":134,"자동화":2,"관측성":22,"데이터":0}

## 1. 개요 및 목적

Nginx Proxy Manager(NPM)를 Gullinkambi 인프라 모니터링에 추가했다. 인프라 대시보드에 `NPM` 탭과 알림 규칙 4개를 만들고, NPM 액세스 로그와 SQLite DB를 읽는 `npm-exporter`를 NAS에 배포했다.

수집기를 붙이자마자 일부 프록시 호스트의 원본 인증서가 만료된 상태라는 것이 드러났다. Cloudflare가 앞단에서 엣지 인증서를 제공하고 있어 사용자 영향은 없었지만, 근본 해결로 Cloudflare Origin 인증서(와일드카드, 15년)로 교체하는 작업을 진행 중이다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- 완료 결과
- NPM 모니터링 구성
- 대시보드
- 메트릭 규격
- 수집기 설계
- 알림 규칙
- 인증서 만료 발견과 대응
- 해결 방향: Cloudflare Origin 인증서
- AI 구독 탭: Claude 수집 지연 정리
- 검증
- 트러블슈팅 메모
- 주요 파일
- Git 기록
- 남은 일
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
NPM proxy-host-*_access.log ─┐
                             ├─▶ npm-exporter :9823 ─▶ NAS Prometheus ─▶ Grafana NPM 탭 / 알림
NPM database.sqlite ─────────┘
```

```text
브라우저 ──(Cloudflare 엣지 인증서: 유효)──▶ Cloudflare ──(NPM 원본 인증서: 만료)──▶ NAS
```

## 4. 검증 근거 및 트러블슈팅

| 작업 | 결과 |
| --- | --- |
| NPM 대시보드 | 인프라 모니터링에 `NPM` 탭 추가 (상태 요약·트래픽·오류와 인증서·컨테이너 자원) |
| NPM 알림 | 컨테이너 down, 5xx 비율, 인증서 만료 임박, 수집 지연 규칙 4개 |
| NPM 수집기 | `npm-exporter` 컨테이너 배포, NAS Prometheus `npm_exporter` job 연결 |
| AI 구독 탭 | 초기화 시각이 지난 구간을 숨기고 `초기화됨 · 갱신 대기` 표시 |
| 주간 사용률 알림 | 지난 구간을 제외하도록 쿼리 수정 |
| 문서 | Gullinkambi 영문·한국어 README에 수집 조건과 알림 표 추가 |

| 영역 | 패널 | 데이터 |
| --- | --- | --- |
| 상태 요약 | 컨테이너 상태, 요청/초, 5xx 비율, 최단 인증서 만료, 수집 지연, 메모리 | cAdvisor + `npm_*` |
| 트래픽 | 호스트별 요청/초, 상태 코드별 요청/초, 호스트별 응답 트래픽 | `npm_*` |
| 오류와 인증서 | 호스트별 5xx 비율, 도메인별 인증서 남은 일수 | `npm_*` |
| 컨테이너 자원 | CPU, 네트워크 | cAdvisor |

- 로그는 15초마다 이어서 읽는다. NPM logrotate는 rename 후 새 파일을 만들기 때문에 inode가 바뀌거나 파일이 줄어들면 처음부터 다시 읽는다.
- 시작할 때는 기존 로그를 건너뛰고 새로 쌓이는 요청부터 센다.
- `host` 레이블은 요청의 Host 헤더가 아니라 NPM DB에 등록된 프록시 호스트의 첫 번째 도메인을 쓴다. 스캐너가 임의의 Host 헤더를 보내도 레이블 수가 늘어나지 않는다.
- 인증서 만료일은 인증서 파일이 아니라 NPM DB의 `certificate.expires_on`에서 읽는다. 개인키가 있는 디렉터리는 마운트하지 않는다.
- 컨테이너는 읽기 전용 파일시스템, 모든 capability 제거, 비root 사용자, 메모리 64MB 제한으로 실행한다.
- 실제 로그 전체로 시험했을 때 파싱 오류는 0건이었다.

수집기를 연결하자 일부 프록시 호스트의 NPM 인증서가 7월에 이미 만료된 상태로 확인됐다. Let's Encrypt 자동 갱신이 해당 인증서에서만 실패한 것으로 보인다.

- Cloudflare SSL 모드가 Full이라 원본 인증서를 검증하지 않아 사용자는 정상 접속 중이었다.
- Full (strict)로 바꾸면 해당 호스트는 526 오류가 난다.
- NPM에 인증서가 연결되지 않은 호스트 일부는 이미 525 오류를 내고 있었다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-02-NPM-모니터링-수집기와-Cloudflare-Origin-인증서]]
- [[Dev/index|Dev 인덱스]]
