---
created: 2026-10-02
date: 2026-10-02
project: Gullinkambi
type: worklog
status: completed
tags:
  - nginx-proxy-manager
  - cloudflare
  - tailscale
  - dns
  - lets-encrypt
  - homelab
---

# Tailscale Split DNS와 와일드카드 인증서

## 요약

Cloudflare Origin 인증서로 교체한 뒤 n8n 접속이 느리다는 문제에서 시작했다. 원인은 인증서가 아니라 Cloudflare 경로였다. 국내 회선에서 Cloudflare 무료 요금제 트래픽이 홍콩(HKG) 데이터센터를 거쳐 NAS로 돌아오면서 요청마다 0.3~0.45초가 더해지고 있었다.

공개 경로(Cloudflare 프록시)는 그대로 두고, Tailscale에 연결된 기기만 NAS NPM으로 직접 가는 빠른 경로를 추가했다. 인증서는 Cloudflare 경로와 직접 경로에서 모두 유효한 Let's Encrypt 와일드카드(`*.dove-nest.com`, DNS Challenge)로 통일했다.

| 경로 | 응답 시간 |
| --- | --- |
| Tailscale 직접 | 0.016~0.028초 |
| Cloudflare 경유 | 0.46~1.32초 |

> [!warning] 같은 날 Tailscale 경로는 되돌림
> `split-dns`가 멈추면 Tailscale 기기에서 `*.dove-nest.com`이 아예 열리지 않는 위험을 질 만큼 필요하지 않다고 판단해 Tailscale 경로를 제거했다. 지금은 모든 기기가 Cloudflare 경로만 쓴다. Let's Encrypt 와일드카드 인증서는 Cloudflare 경로에서도 유효하고 자동 갱신되므로 유지했다. 자세한 내용은 아래 [[#되돌림]] 참고.

## n8n이 느렸던 이유

- NAS 원본에 직접 요청하면 n8n API 하나가 약 0.017초, Cloudflare를 거치면 0.35~0.46초였다.
- n8n 화면은 처음 열 때 API 요청을 약 40개 보내고, 이 요청들이 앞 단계가 끝나야 다음이 나가는 여러 단계로 이어진다. 단계마다 홍콩 왕복이 쌓여 첫 화면까지 약 8초가 걸렸다.
- API 응답은 사용자별이라 Cloudflare가 캐시할 수 없다. 캐시 규칙으로는 해결되지 않는다.
- 정적 파일(`/assets/*`)은 캐시되지만, n8n이 재시작·업데이트되면 파일 이름이 바뀌어 첫 접속에서 캐시가 다시 비어 있다.
- 접속 지역은 Cloudflare가 회선과 요금제에 따라 정하며 사용자가 고를 수 없다. 서울(ICN) 데이터센터는 주로 상위 요금제에 쓰인다고 알려져 있다.

## 검토한 선택지

| 방법 | 판단 |
| --- | --- |
| Cloudflare Enterprise | 서울 연결 가능성이 높지만 홈랩에는 비현실적인 비용 |
| Argo Smart Routing | 홍콩↔NAS 구간만 개선. 효과 제한적 |
| DNS only(회색 구름) + Let's Encrypt | 어디서나 빠르지만 집 IP 공개, DDoS·WAF 보호가 빠짐 |
| **Tailscale 기기만 직접 경로** | IP 공개 없이 빠름. Tailscale 앱이 있는 기기에만 적용 → **채택** |

DNS only를 쓰지 않은 이유는 보안이다. 다만 공유기가 443을 NAS로 포워딩하고 있어서, 지금도 IP를 아는 사람은 Cloudflare를 우회해 직접 접속할 수 있다. 원본 443을 Cloudflare IP 대역만 허용하도록 막는 것은 별도 강화 과제로 남긴다.

## 구성

```text
Tailscale 기기 ── Split DNS(dove-nest.com) ──▶ split-dns ──▶ NPM 호스트면 NAS Tailscale 주소
              └─ https :443 ──▶ tailscale-gateway serve ──▶ NPM :14443 ──▶ 각 서비스

그 외 기기·웹훅 ── 공개 DNS ──▶ Cloudflare(HKG) ──▶ NPM ──▶ 각 서비스
```

### NPM은 이미 Tailscale로 닿아 있었다

- `tailscale-gateway`가 NAS 내부망을 서브넷 라우터로 Tailscale에 광고하고 있었다.
- 다만 userspace 모드라 Tailscale 주소로는 NPM에 바로 닿지 않고, 내부망 IP로만 닿았다.
- 도메인을 입력하면 공개 DNS가 Cloudflare IP를 주기 때문에, 경로가 있어도 Cloudflare로 가고 있었다.

### split-dns

- Birds-Nest `docker-compose/npm/split-dns/`에 Python 표준 라이브러리만 쓰는 작은 DNS 서버를 만들었다.
- NPM SQLite DB에서 활성 프록시 호스트 도메인을 30초마다 읽어, 그 이름만 NAS Tailscale 주소로 답한다.
- 나머지 `*.dove-nest.com`과 외부 도메인은 업스트림(1.1.1.1) 응답을 그대로 전달한다. NPM을 거치지 않는 Mac mini 서비스는 영향을 받지 않는다.
- AAAA 질의는 빈 응답(NODATA)으로 돌려 IPv4로 연결되게 했다.
- NAS 내부망 주소의 53번 포트에만 열었다. DSM이 localhost 53을 쓰고 있어 그 주소만 피했다.
- 컨테이너는 읽기 전용, capability 제거, 비root 사용자로 실행한다.

### Tailscale 443 전달

- NAS 443은 DSM이 쓰고 있어서, `tailscale-gateway`에서 Tailscale 주소의 443을 NPM 14443으로 넘겼다.
- `tailscale serve --bg --tcp 443 tcp://<NAS LAN>:14443`. 게이트웨이를 재시작하지 않고 적용했고, 설정은 Tailscale 상태 볼륨에 저장된다.

### Tailscale 관리 화면

- DNS → Nameservers → Custom → NAS 내부망 주소, **Restrict to domain**: `dove-nest.com`
- 기기에서는 Use Tailscale DNS와 서브넷 경로 사용이 켜져 있어야 한다.
- Windows에서 확인할 때는 Split DNS를 무시하는 `nslookup` 대신 `Resolve-DnsName`을 쓴다.

### Mac mini 서비스

`hermes`, `viking`, `embed`는 원래 NAS NPM을 거쳐 Mac mini로 간다. NAS까지 가는 앞부분만 짧아지므로 Split DNS 대상에 포함했다. NPM에 없는 도메인은 공개 DNS 응답을 그대로 받는다.

## 인증서 정리

### Origin 인증서와 Let's Encrypt 비교

| 항목 | Cloudflare Origin | Let's Encrypt 와일드카드 |
| --- | --- | --- |
| 유효 기간 | 15년, 갱신 불필요 | 90일, NPM 자동 갱신 |
| 브라우저 신뢰 | 안 함 (Cloudflare만 신뢰) | 함 |
| Tailscale 직접 경로 | 인증서 경고로 막힘 | 사용 가능 |
| NAS에 API 토큰 필요 | 아니오 | 예 (DNS 편집 권한) |

Tailscale 직접 경로를 쓰기로 했으므로 Let's Encrypt 와일드카드로 통일했다. Cloudflare 경로만 쓴다면 Origin 인증서가 관리하기 더 편하다.

### 진행 내용

- NPM Certificates에서 `*.dove-nest.com`을 Let's Encrypt DNS Challenge(Cloudflare)로 발급했다. 키 타입은 ECDSA를 골랐다.
- 프록시 호스트 12개 모두 새 인증서로 교체했다.
- NPM 2.15 UI에는 Advanced 글자 탭이 없고, 호스트 편집 창 오른쪽 끝 톱니바퀴(Settings) 탭이 사용자 지정 Nginx 설정이다.
- `mlflow-mcp`는 사용자 지정 Nginx 설정에 줄바꿈이 `\n` 글자로 들어가 nginx가 거부하고 있었다. 두 줄로 고쳐 복구했다.
- 사용하지 않는 Let's Encrypt 인증서 11개를 NPM에서 삭제했다.
- NPM이 지우지 못한 옛 인증서 파일(live, archive, renewal)과 이전 credentials 파일을 정리했다.

### 옛 인증서 자동 갱신이 실패한 원인

certbot 로그에 `live/npm-N/cert.pem`이 심볼릭 링크가 아니라 갱신 설정이 깨졌다고 나왔다. 인증서 폴더를 복사하거나 옮기는 과정에서 링크가 일반 파일로 바뀐 것으로 보인다. 새 인증서는 링크가 정상이다.

### 자동 갱신

- NPM이 1시간마다 확인하고 만료 30일 전부터 자동 갱신한다.
- 갱신 시 Cloudflare DNS에 확인용 TXT 레코드를 만들고, Let's Encrypt 검증 후 nginx에 반영한다.
- staging 서버로 `certbot renew --dry-run`을 실행해 현재 토큰으로 갱신되는 것을 확인했다.
- 수동 갱신은 NPM Certificates → ⋮ → Renew로 한다.
- 갱신이 실패하면 NPM 모니터링의 인증서 만료 알림(14일 미만)이 Discord로 온다.

### API 토큰 관리

- DNS Challenge 토큰은 NPM 컨테이너의 credentials 파일에 `0600` 권한으로 저장된다.
- 토큰은 `dove-nest.com` 한 zone의 DNS 편집 권한으로만 만든다.
- 토큰을 교체할 때는 Cloudflare에서 새 토큰을 만들고, NAS에서 토큰이 화면과 셸 기록에 남지 않게 입력받아 credentials 파일을 다시 쓴다. 그다음 이전 토큰을 삭제한다.

```bash
docker exec -it nginx-proxy-manager sh -c 'read -rsp "Cloudflare token: " T; echo; printf "# Cloudflare API token\ndns_cloudflare_api_token=%s\n" "$T" > /etc/letsencrypt/credentials/credentials-<ID>; chmod 600 /etc/letsencrypt/credentials/credentials-<ID>'
```

## 기타 정리

- NPM 수집기의 인증서 레이블을 NPM 인증서 이름으로 바꿨다. NPM이 Custom 인증서 도메인을 주체에서 `CloudFlare,`처럼 잘못 읽어 두는 경우가 있었다.
- `kis-mcp` 프록시 호스트는 NPM에서 삭제됐다.

## 검증

| 확인 항목 | 결과 |
| --- | --- |
| split-dns UDP·TCP 응답 | NPM 호스트 12개만 Tailscale 주소, 나머지는 공개 응답 |
| Tailscale 경로 엄격한 TLS 검증 | 12개 호스트 모두 통과 |
| Cloudflare 경로 | 12개 호스트 정상 |
| `nginx -t` | 성공 |
| 인증서 갱신 dry-run | 성공 |
| NPM 수집기 | `npm_collector_up 1`, 인증서 만료일 수집 |

## 주요 파일

| 저장소 | 파일 | 역할 |
| --- | --- | --- |
| Birds-Nest | `docker-compose/npm/split-dns/server.py` | Split DNS 서버 |
| Birds-Nest | `docker-compose/npm/split-dns/Dockerfile` | 컨테이너 이미지 |
| Birds-Nest | `docker-compose/npm/docker-compose.yml` | `split-dns` 서비스 |
| Birds-Nest | `docker-compose/npm/.env.example` | Split DNS 환경변수 |
| Birds-Nest | `docker-compose/monitoring/npm-exporter/exporter.py` | 인증서 레이블 수정 |

## 되돌림

| 항목 | 처리 |
| --- | --- |
| Tailscale 관리 화면 Split DNS | 삭제 |
| `tailscale-gateway` 443 전달 | `tailscale serve --tcp=443 off` |
| `split-dns` 컨테이너·이미지 | 중지 후 삭제, NAS LAN 53번 포트 닫힘 확인 |
| Birds-Nest 저장소 | `061d514`를 되돌리는 `58f0b98` 커밋을 `feat/npm-exporter`에 push |
| 인증서 | Let's Encrypt 와일드카드 유지 |

Split DNS 등록을 먼저 지운 뒤 DNS 서버를 껐다. 순서를 반대로 하면 Tailscale 기기에서 `*.dove-nest.com`을 찾지 못해 접속이 끊긴다.

되돌린 뒤 12개 호스트 모두 Cloudflare 경로에서 정상 응답(0.40~0.55초)하고, DNS도 Cloudflare 주소를 돌려주는 것을 확인했다.

### 인증서를 유지한 이유

| | Let's Encrypt (유지) | Cloudflare Origin |
| --- | --- | --- |
| 갱신 | 90일 자동, dry-run 확인 | 필요 없음 |
| NAS 비밀값 | DNS 편집 토큰 | 없음 |
| 지금 추가 작업 | 없음 | 12개 호스트 재교체 |
| 구조 변경 여지 | Tailscale·직접 접속에도 사용 가능 | Cloudflare 프록시에 묶임 |

Cloudflare 경로만 쓰는 구조에서는 Origin 인증서가 관리 부담과 비밀값이 더 적다. 다만 이미 동작하는 Let's Encrypt를 다시 바꿀 이점이 크지 않아 우선 유지했다.

## 남은 일

- [x] Birds-Nest 변경 커밋·push
- [x] Tailscale 경로 제거
- [x] 인증서 최종 선택: Cloudflare Origin으로 통일, Let's Encrypt 와일드카드와 NAS 토큰 파일 삭제
- [ ] Cloudflare에서 와일드카드 발급용 API 토큰 삭제
- [ ] Cloudflare SSL 모드 Full (strict) 적용 여부 확인
- [ ] 원본 443을 Cloudflare IP 대역만 허용하도록 제한 검토

후속 정리는 [[Work/Gullinkambi/작업기록/2026-10-02-ORCA-쓰레드-이름-복구와-Birds-Nest-브랜치-정리|ORCA 쓰레드 이름 복구와 Birds-Nest 브랜치 정리]]에 이어서 기록했다.

## 관련

- [[Work/Gullinkambi/작업기록/2026-10-02-NPM-모니터링-수집기와-Cloudflare-Origin-인증서|NPM 모니터링 수집기와 Cloudflare Origin 인증서]]
- [[Work/Gullinkambi/index|Gullinkambi 프로젝트 노트]]
- [[Work/index|토이 프로젝트 목록]]
- [[Home]]
