---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "Gullinkambi"
source_work_log: "[[Work/Gullinkambi/작업기록/2026-10-02-Tailscale-Split-DNS와-와일드카드-인증서]]"
tags:
  - dev
  - draft
  - "gullinkambi"
---

# Tailscale Split DNS와 와일드카드 인증서

> 자동 증류 초안 · 원천 [[Work/Gullinkambi/작업기록/2026-10-02-Tailscale-Split-DNS와-와일드카드-인증서]] · 분류 근거 {"인프라":211,"자동화":6,"관측성":20,"데이터":0}

## 1. 개요 및 목적

Cloudflare Origin 인증서로 교체한 뒤 n8n 접속이 느리다는 문제에서 시작했다. 원인은 인증서가 아니라 Cloudflare 경로였다. 국내 회선에서 Cloudflare 무료 요금제 트래픽이 홍콩(HKG) 데이터센터를 거쳐 NAS로 돌아오면서 요청마다 0.3~0.45초가 더해지고 있었다.

공개 경로(Cloudflare 프록시)는 그대로 두고, Tailscale에 연결된 기기만 NAS NPM으로 직접 가는 빠른 경로를 추가했다. 인증서는 Cloudflare 경로와 직접 경로에서 모두 유효한 Let's Encrypt 와일드카드(`*.dove-nest.com`, DNS Challenge)로 통일했다.

## 2. 핵심 아키텍처 및 원칙

- 요약
- n8n이 느렸던 이유
- 검토한 선택지
- 구성
- NPM은 이미 Tailscale로 닿아 있었다
- split-dns
- Tailscale 443 전달
- Tailscale 관리 화면
- Mac mini 서비스
- 인증서 정리
- Origin 인증서와 Let's Encrypt 비교
- 진행 내용
- 옛 인증서 자동 갱신이 실패한 원인
- 자동 갱신
- API 토큰 관리
- 기타 정리
- 검증
- 주요 파일
- 되돌림
- 인증서를 유지한 이유
- 남은 일
- 관련

## 3. 재사용 가능한 코드 스니펫 / 설정

```text
Tailscale 기기 ── Split DNS(dove-nest.com) ──▶ split-dns ──▶ NPM 호스트면 NAS Tailscale 주소
              └─ https :443 ──▶ tailscale-gateway serve ──▶ NPM :14443 ──▶ 각 서비스

그 외 기기·웹훅 ── 공개 DNS ──▶ Cloudflare(HKG) ──▶ NPM ──▶ 각 서비스
```

```bash
docker exec -it nginx-proxy-manager sh -c 'read -rsp "Cloudflare token: " T; echo; printf "# Cloudflare API token\ndns_cloudflare_api_token=%s\n" "$T" > /etc/letsencrypt/credentials/credentials-<ID>; chmod 600 /etc/letsencrypt/credentials/credentials-<ID>'
```

## 4. 검증 근거 및 트러블슈팅

Cloudflare Origin 인증서로 교체한 뒤 n8n 접속이 느리다는 문제에서 시작했다. 원인은 인증서가 아니라 Cloudflare 경로였다. 국내 회선에서 Cloudflare 무료 요금제 트래픽이 홍콩(HKG) 데이터센터를 거쳐 NAS로 돌아오면서 요청마다 0.3~0.45초가 더해지고 있었다.

- DNS → Nameservers → Custom → NAS 내부망 주소, **Restrict to domain**: `dove-nest.com`
- 기기에서는 Use Tailscale DNS와 서브넷 경로 사용이 켜져 있어야 한다.
- Windows에서 확인할 때는 Split DNS를 무시하는 `nslookup` 대신 `Resolve-DnsName`을 쓴다.

- NPM이 1시간마다 확인하고 만료 30일 전부터 자동 갱신한다.
- 갱신 시 Cloudflare DNS에 확인용 TXT 레코드를 만들고, Let's Encrypt 검증 후 nginx에 반영한다.
- staging 서버로 `certbot renew --dry-run`을 실행해 현재 토큰으로 갱신되는 것을 확인했다.
- 수동 갱신은 NPM Certificates → ⋮ → Renew로 한다.
- 갱신이 실패하면 NPM 모니터링의 인증서 만료 알림(14일 미만)이 Discord로 온다.

| 확인 항목 | 결과 |
| --- | --- |
| split-dns UDP·TCP 응답 | NPM 호스트 12개만 Tailscale 주소, 나머지는 공개 응답 |
| Tailscale 경로 엄격한 TLS 검증 | 12개 호스트 모두 통과 |
| Cloudflare 경로 | 12개 호스트 정상 |
| `nginx -t` | 성공 |
| 인증서 갱신 dry-run | 성공 |
| NPM 수집기 | `npm_collector_up 1`, 인증서 만료일 수집 |

| 항목 | 처리 |
| --- | --- |
| Tailscale 관리 화면 Split DNS | 삭제 |
| `tailscale-gateway` 443 전달 | `tailscale serve --tcp=443 off` |
| `split-dns` 컨테이너·이미지 | 중지 후 삭제, NAS LAN 53번 포트 닫힘 확인 |
| Birds-Nest 저장소 | `061d514`를 되돌리는 `58f0b98` 커밋을 `feat/npm-exporter`에 push |
| 인증서 | Let's Encrypt 와일드카드 유지 |

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/Gullinkambi/작업기록/2026-10-02-Tailscale-Split-DNS와-와일드카드-인증서]]
- [[Dev/index|Dev 인덱스]]
