---
created: 2026-10-02
date: 2026-10-02
type: reference
tags:
  - dev
  - homelab
  - cloudflare
  - tls
  - nginx-proxy-manager
  - tailscale
  - monitoring
---

# 홈랩 인증서·Cloudflare·접속 경로 비교 정리

## 요약

2026-10-02 Gullinkambi·NPM 작업 중 선택지를 비교했던 내용을 표로 모았다. 각 표의 **결정** 열은 이날 실제로 고른 것이다. 측정값은 NAS·Mac mini가 같은 집 내부망에 있고, Cloudflare 무료 요금제 트래픽이 홍콩(HKG) 데이터센터를 거치는 환경 기준이다.

## 1. 인증서

### Cloudflare Origin 인증서 vs Let's Encrypt

| 항목 | Cloudflare Origin | Let's Encrypt |
| --- | --- | --- |
| 유효 기간 | 최대 15년, 갱신 없음 | 90일, 자동 갱신 |
| 브라우저 신뢰 | 안 함 (Cloudflare만 신뢰) | 함 |
| 사용 가능한 경로 | Cloudflare 프록시 경유만 | 어디서나 (Cloudflare, Tailscale, 직접 접속) |
| NAS에 필요한 비밀값 | 없음 (인증서·개인키만) | DNS Challenge용 Cloudflare API 토큰 |
| 장애 위험 | 거의 없음 | 갱신 실패 시 만료 |
| 외부 의존 | Cloudflare | Let's Encrypt 서버, 발급 횟수 제한 |
| **결정** | **채택** (Cloudflare 경로만 쓰기로 함) | 와일드카드 발급 후 삭제 |

> Cloudflare 프록시만 쓰면 Origin이 관리 부담과 비밀값이 적다. 직접 접속 경로를 만들 계획이면 Let's Encrypt가 필요하다.

### Let's Encrypt 검증 방식: HTTP-01 vs DNS-01

| 항목 | HTTP-01 | DNS-01 (Cloudflare API) |
| --- | --- | --- |
| 검증 방법 | 80번 포트로 확인 파일 요청 | DNS TXT 레코드 생성 |
| 와일드카드 | 불가 | 가능 |
| Cloudflare 프록시·포트 설정 영향 | 받음 | 받지 않음 |
| 필요한 것 | 외부에서 80 접근 | DNS 편집 권한 토큰 |
| **결정** | — | **사용** (와일드카드 발급 시) |

### 키 타입: ECDSA vs RSA

| 항목 | ECDSA (P-256) | RSA (2048) |
| --- | --- | --- |
| TLS 연결 비용 | 낮음 | 높음 |
| 키 크기 대비 강도 | 256비트가 RSA 3072 수준 | 기준 |
| 호환성 | 최근 브라우저·휴대폰·Cloudflare·웹훅 호출 서비스 모두 지원 | 아주 오래된 기기까지 지원 |
| **결정** | **선택** | — |

### 와일드카드 1개 vs 호스트별 인증서

| 항목 | 와일드카드 `*.dove-nest.com` | 호스트별 |
| --- | --- | --- |
| 관리할 인증서 수 | 1개 | 호스트 수만큼 |
| 새 호스트 추가 | 기존 인증서 선택만 | 새로 발급 |
| 이번에 겪은 문제 | — | 일부만 갱신 실패해 85일간 만료 상태로 방치 |
| 루트 도메인 | 포함 안 됨 (`dove-nest.com` 별도 필요) | 해당 도메인만 |
| **결정** | **사용** (Origin도 와일드카드) | — |

## 2. Cloudflare SSL 모드

### Full vs Full (strict)

| 항목 | Full | Full (strict) |
| --- | --- | --- |
| Cloudflare ↔ 원본 암호화 | 함 | 함 |
| 원본 인증서 검증 | 안 함 (만료·도메인 불일치·자체 서명 통과) | 함 (유효 기간, 도메인, 신뢰된 발급자) |
| 중간자 공격 방어 | 약함 | 강함 |
| 인증서 문제 발견 | 조용히 넘어감 | 526 오류로 즉시 드러남 |
| 실제 사례 | 만료 인증서 3개가 85일간 정상처럼 동작 | 만료 당일 장애로 발견됐을 것 |
| **결정** | — | **권장** (Origin 인증서가 2041년까지 유효해 위험 낮음) |

관련 오류 코드:

| 코드 | 의미 | 이날 사례 |
| --- | --- | --- |
| 525 | Cloudflare ↔ 원본 SSL 핸드셰이크 실패 | NPM 호스트에 인증서가 없던 `kis-mcp`, `mlflow-mcp` |
| 526 | 원본 인증서가 유효하지 않음 (strict에서만) | strict였다면 만료 인증서 호스트에서 발생 |

## 3. 접속 경로와 지연

### 측정값

| 대상 | 직접(내부망·Tailscale) | Cloudflare 경유 | 차이 |
| --- | --- | --- | --- |
| NAS 원본 응답 (TTFB) | 0.01~0.02초 | 0.24~0.50초 | 약 25배 |
| n8n API 1건 (`/rest/settings`) | 0.017초 | 0.35~0.46초 | 약 25배 |
| 12개 호스트 (Mac mini에서) | 0.016~0.028초 | 0.46~1.32초 | 30~100배 |
| 임베딩 API 1건 (RobinGraph → Mac mini) | 0.20초 | 0.79초 (중앙값) | 약 4배 |

- n8n 첫 화면은 API 약 40개가 단계별로 이어져서, 단계마다 홍콩 왕복이 쌓여 약 8초가 걸렸다.
- 임베딩은 계산 자체가 약 0.2초라 경로 비용(0.4~0.6초)이 상대적으로 작게 보이지만, 대량 적재에서는 호출 수만큼 쌓인다.

### Cloudflare 경로를 빠르게 하는 방법

| 방법 | 효과 | 비용·단점 | 결정 |
| --- | --- | --- | --- |
| Cloudflare Enterprise | 서울(ICN) 연결 가능성 높음 | 홈랩에는 비현실적인 비용 | — |
| Argo Smart Routing | 데이터센터 ↔ 원본 구간만 개선 | 월 $5~ + 트래픽, 효과 제한적 | — |
| DNS only (프록시 끔) + Let's Encrypt | 어디서나 직접 연결 | 집 IP 공개, DDoS·WAF 없음, 유동 IP면 DDNS 필요 | — |
| Tailscale Split DNS | Tailscale 기기만 직접 연결, IP 공개 없음 | `split-dns` 장애 시 Tailscale 기기에서 도메인 전체 불통 | 구축 후 **되돌림** |
| 내부 서비스는 내부 IP로 호출 | 집 안 서비스끼리 직접 연결 | 내부망 구간은 HTTP | **임베딩에 적용** |

### Cloudflare 프록시 켬 vs DNS only

| 항목 | 프록시 켬 (주황 구름) | DNS only (회색 구름) |
| --- | --- | --- |
| DNS 응답 | Cloudflare IP | 집 공인 IP |
| 집 IP 노출 | 숨김 | 공개 (같은 IP의 다른 도메인도 노출) |
| DDoS·WAF·봇 차단 | 있음 | 없음 |
| 국내 접속 속도 | 홍콩 경유로 느림 | 빠름 |
| 해외 접속 속도 | 빠를 수 있음 | 느릴 수 있음 |
| 필요한 인증서 | Origin 또는 공인 | 공인 (Let's Encrypt) |
| **결정** | **유지** | — |

> 공유기가 443을 원본으로 포워딩하고 있으면, 프록시를 켜도 IP를 아는 사람은 직접 접속할 수 있다. 원본 443을 Cloudflare IP 대역만 허용하도록 막는 것이 다음 강화 과제다.

### Tailscale 직접 경로 유지 vs 제거

| 항목 | 유지 | 제거 |
| --- | --- | --- |
| Tailscale 켠 기기 | 빠름 (약 0.02초) | Cloudflare 경로 (약 0.5초) |
| 그 외 기기·웹훅 | Cloudflare 경로 | Cloudflare 경로 |
| 관리 요소 | `split-dns`, `tailscale serve`, 공인 인증서 갱신 | 없음 |
| 장애 영향 | `split-dns`가 멈추면 Tailscale 기기에서 `*.dove-nest.com` 불통 | 없음 |
| **결정** | — | **제거** (위험 부담 대비 필요성 낮음) |

### Split DNS 대상 범위

| 방식 | 장점 | 단점 | 결정 |
| --- | --- | --- | --- |
| `*.dove-nest.com` 전체 | 단순 | NPM을 거치지 않는 Mac mini 서비스까지 NAS로 보내 깨짐 | — |
| NPM에 등록된 호스트만 | NPM 밖 도메인은 공개 응답 유지, NPM 변경 자동 반영 | DNS 서버가 NPM DB를 읽어야 함 | 채택했다가 경로 전체 제거 |

Mac mini 서비스 중 NPM을 거치는 것(`hermes`, `viking`, `embed`)은 NAS로 보내도 앞부분 경로만 짧아지므로 포함해도 됐다.

### 임베딩 API 호출 주소

| 항목 | 공개 주소 `https://embed…` | Mac mini 내부 IP |
| --- | --- | --- |
| 경로 | NAS → Cloudflare(HKG) → NAS NPM → Mac mini | NAS → Mac mini |
| 응답 시간 | 0.79초 | 0.20초 |
| 암호화 | HTTPS | HTTP (집 내부망) |
| 집 밖에서 사용 | 가능 | 불가 |
| Cloudflare 정책 영향 | 받음 (예: `Python-urllib` UA는 403 차단) | 없음 |
| **결정** | 개발·외부용으로 유지 | **NAS 배포에 적용** |

> 인증서를 바꿔도 경로는 바뀌지 않는다. 경로는 DNS가 어디를 가리키는지(프록시 여부)로 정해진다.

## 4. Cloudflare 캐시

### 브라우저 캐시 vs Cloudflare 캐시

| 항목 | 브라우저 캐시 | Cloudflare 엣지 캐시 |
| --- | --- | --- |
| 위치 | 각 기기 | 데이터센터별 (HKG, NRT 등) |
| 생성 시점 | 그 기기에서 처음 받을 때 | 그 데이터센터에 첫 요청(MISS)이 올 때 |
| 공유 범위 | 그 기기만 | 같은 데이터센터로 오는 모든 사용자 |
| 유지 기간 | `Cache-Control: max-age` (n8n 자산 1일) | `max-age` 또는 Edge TTL, 요청이 적으면 더 일찍 삭제 |
| 다른 장소(회사 → 집) | 같은 기기면 유지 | 같은 데이터센터로 연결될 때만 유지 |
| 무효화 | 앱 업데이트로 파일 이름이 바뀔 때 | 같음 |

### 캐시되는 것

| 대상 | 기본 캐시 여부 |
| --- | --- |
| `.js`, `.css`, 이미지, 폰트 | 됨 |
| HTML 페이지 | 안 됨 |
| API 응답 (`/rest/...`, `/v1/embeddings`) | 안 됨 |
| `Cache-Control: no-store`/`private` 응답 | 안 됨 |

확인 방법: 응답 헤더 `cf-cache-status`(MISS/HIT), 연결된 데이터센터는 `https://<도메인>/cdn-cgi/trace`의 `colo=`.

개선 방법: Cache Rules로 `/assets/*` Edge TTL을 길게, Tiered Cache로 데이터센터 간 캐시 공유.

## 5. 모니터링 설계

### AI 구독 수집 방식

| 대상 | 수집 방식 | 갱신 시점 |
| --- | --- | --- |
| Codex | app-server 계정 endpoint 조회 | 주기적 |
| Antigravity | `agy -p "/usage"` CLI 실행 | 주기적 |
| Claude | Claude Code CLI status line 입력 캐시 | Claude Code를 쓸 때만 |

| Claude 수집 대안 | 장점 | 단점 | 결정 |
| --- | --- | --- | --- |
| status line (현행) | 공식 문서화된 경로 | CLI 사용 시에만 갱신, VS Code 확장에서는 실행 안 됨 | **유지** |
| claude.ai 웹 내부 API | 수시 조회 가능 | 비공식, 세션 쿠키 보관 위험, 약관 회색 지대 | — |
| 다른 서버에서 status line 푸시 | 여러 기기 사용분 반영 | NAS는 VS Code 확장이라 효과 없음 | — |

구독 한도는 계정 전체 기준이라, 다른 환경의 사용량도 다음 갱신 때 사용률에 함께 반영된다.

### 초기화 지난 구간 처리 위치

| 위치 | 장점 | 단점 | 결정 |
| --- | --- | --- | --- |
| exporter (Mac mini) | 데이터 자체가 정확해짐 | 별도 체크아웃·LaunchAgent 재배포 필요 | — |
| 대시보드 PromQL (`unless … reset <= time()`) | Gullinkambi만 배포 | 쿼리가 길어짐 | **채택** |

### NPM 수집기 설계 선택

| 항목 | 선택지 A | 선택지 B | 결정 |
| --- | --- | --- | --- |
| `host` 레이블 | 요청 Host 헤더 | NPM DB의 프록시 호스트 도메인 | **B** (스캐너가 임의 Host를 보내도 레이블 수 고정) |
| 인증서 만료일 | 인증서 파일 파싱 | NPM DB `expires_on` | **B** (개인키 디렉터리 마운트 불필요) |
| 인증서 레이블 | 인증서 도메인 목록 | NPM 인증서 이름 | **B** (Custom 인증서는 도메인이 `CloudFlare,`처럼 잘못 저장됨) |
| 시작 시 로그 | 처음부터 읽기 | 끝에서부터 | **끝에서부터** (과거 누적 방지) |
| 로그 로테이션 | 파일명 기준 | inode·크기 변화 감지 | **inode·크기** (NPM은 rename 후 새 파일 생성) |

### 알림 No data 처리

| 규칙 | No data 상태 | 이유 |
| --- | --- | --- |
| 컨테이너 down | Alerting | 수집이 끊긴 것 자체가 장애 |
| 5xx 비율, 인증서 만료 | OK | 트래픽·인증서가 없을 수 있음 |
| 수집 지연 | Alerting (수집기 배포 후) | 수집기 소멸도 감지 |

## 6. 운영 작업 방식

| 상황 | 선택지 A | 선택지 B | 결정 |
| --- | --- | --- | --- |
| NAS Birds-Nest가 원격보다 90커밋 뒤처짐 | 원격 병합 후 push | 새 브랜치로만 push | **B** (실행 중 서비스 설정 변경 회피) |
| RobinGraph 설정만 변경 | `deploy_nas.sh deploy` (재빌드) | `compose up -d --no-build` | **B** (미커밋 코드가 운영에 섞이지 않게) |
| 적용 순서 | prod 먼저 | test 먼저 | **test 먼저** |
| NPM 인증서 삭제 | DB 직접 수정 | NPM UI | **UI** (certbot 정리 등 앱 로직 유지) |
| Split DNS 제거 순서 | DNS 서버 먼저 끄기 | Tailscale 등록 먼저 삭제 | **등록 먼저** (반대면 도메인 전체 불통) |
| 수집기 배포 전 대시보드 | 빈 패널 미리 배포 | 수집기와 함께 배포 | 미리 배포함 → "아무것도 안 나온다"는 혼동 발생 |

## 관련

- [[Work/Gullinkambi/작업기록/2026-10-02-NPM-모니터링-수집기와-Cloudflare-Origin-인증서|NPM 모니터링 수집기와 Cloudflare Origin 인증서]]
- [[Work/Gullinkambi/작업기록/2026-10-02-Tailscale-Split-DNS와-와일드카드-인증서|Tailscale Split DNS와 와일드카드 인증서]]
- [[Dev/index|Dev — 개발 / 프로그래밍]]
- [[Home]]
