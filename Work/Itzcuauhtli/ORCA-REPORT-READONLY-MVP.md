# Itzcuauhtli 읽기 전용 MCP MVP 실행 보고서

작성일: 2026-09-29 (Asia/Seoul)  
검토 대상: Dovie  
판정: **PASS_WITH_ISSUES** — 아래 검증 항목은 통과했으며, 동시 파일 교체 경합은 남은 제한으로 기록한다. ORCA 판정은 Dovie의 최종 수용을 대신하지 않는다.

```text
task_id: itzcuauhtli-readonly-mvp
status: PASS_WITH_ISSUES
repository_path: /Users/kimdove/orca/workspaces/Itzcuauhtli/https-github.com-EvoDmiK-Itzcuauhtli
base_sha: 2b5fdb1408beceb3b27416a40b122a61840d59ae
final_sha: 5c45bdea8f9eddb2a48fb258e7638bc0e0453b1a
branch: EvoDmiK/https-github.com-EvoDmiK-Itzcuauhtli
```

## 구현 결과

Node.js 24, TypeScript strict, pnpm lockfile, 공식 MCP TypeScript SDK v2, Zod v4로 로컬 HTTP 서버를 만들었다. 서버는 `127.0.0.1`의 `/mcp`에서 Streamable HTTP를 제공하고, `list_notes`, `read_note`, `search_notes` 세 도구만 등록한다. `/health`는 Vault가 사용 가능한지 확인해 준비 상태를 반환한다. 모든 도구는 읽기 전용이며 합성 fixture Vault만으로 검증했다.

Vault 상대경로의 traversal·절대경로·Windows 경로·NUL·숨김 디렉터리 접근을 거부한다. symlink 파일과 디렉터리는 읽거나 탐색하지 않는다. Markdown 읽기는 1 MiB로 제한하고 UTF-8 오류 및 binary control byte를 거부한다. 검색은 정규식 없는 대소문자 무관 문자열 검색이며, 최대 10,000개 파일시스템 항목을 스캔하고 결과 snippet을 300자로 제한한다.

## 변경 파일과 최종 diff

| 구분 | 파일 |
|---|---|
| 설정·문서 | `.gitignore`, `.node-version`, `README.md`, `eslint.config.js`, `package.json`, `pnpm-lock.yaml`, `tsconfig.json` |
| 구현 | `src/config.ts`, `src/errors.ts`, `src/index.ts`, `src/server.ts`, `src/vault.ts` |
| 테스트 | `tests/mcp.test.ts`, `tests/security.test.ts`, `tests/vault.test.ts` |
| 합성 fixture | `tests/fixtures/vault/README.md`, `tests/fixtures/vault/Notes/alpha.md`, `tests/fixtures/vault/Notes/beta.md`, `tests/fixtures/vault/Korean/한글-노트.md`, `tests/fixtures/vault/.obsidian/ignored.md` |

총 20개 파일, `2692 insertions(+), 2 deletions(-)`이다. 최종 diff는 다음 명령으로 확인한다.

```bash
git show --format= --binary 5c45bdea8f9eddb2a48fb258e7638bc0e0453b1a
```

검증 당시 저장한 diff는 `/tmp/itzcuauhtli-readonly-mvp-final.diff`였으며 SHA-256은 `058a464be3918034729544767cd679aa534a699018a8d4c0559a3cc1a79dc330`이다. 영속적인 원본은 위 Git commit이다. 검증 후 `git status --porcelain=v1` 출력은 비어 있었다.

## 명령과 exit code

기본 셸에는 `corepack`과 `pnpm`이 없어 `npm exec`로 Node **24.21.0**과 pnpm **10.34.6**을 지정했다. `node_modules`를 다른 위치로 옮겨 비운 뒤 frozen install을 실행했다.

| 실행한 명령 | exit code | 결과 |
|---|---:|---|
| `npm exec --yes --package=node@24 --package=pnpm@10 -- pnpm install --frozen-lockfile` | 0 | 빈 `node_modules`에서 lockfile 설치 |
| `npm exec --yes --package=node@24 --package=pnpm@10 -- pnpm lint` | 0 | ESLint 통과 |
| `npm exec --yes --package=node@24 --package=pnpm@10 -- pnpm typecheck` | 0 | TypeScript strict 통과 |
| `npm exec --yes --package=node@24 --package=pnpm@10 -- pnpm test` | 0 | Vitest 3개 파일, 30개 테스트 통과 |
| `ITZCUAUHTLI_VAULT_ROOT=./tests/fixtures/vault PORT=31247 npm exec --yes --package=node@24 --package=pnpm@10 -- pnpm dev` | 기동 및 SIGINT 종료 0 | Obsidian·GUI 없이 실행 |
| `curl --silent --show-error --include http://127.0.0.1:31247/health` | 0 | HTTP 200, `{"status":"ok","readOnly":true,"vaultReady":true}` |
| `lsof -nP -iTCP:31247 -sTCP:LISTEN` | 0 | `127.0.0.1:31247 (LISTEN)`만 표시 |
| `env -u ITZCUAUHTLI_VAULT_ROOT npm exec --yes --package=node@24 --package=pnpm@10 -- pnpm dev` | 1 | root 미설정 기동 거부 |
| `ITZCUAUHTLI_VAULT_ROOT=./README.md npm exec --yes --package=node@24 --package=pnpm@10 -- pnpm dev` | 1 | 일반 파일을 root로 지정한 기동 거부 |

`HOST=0.0.0.0`을 지정해 다시 기동했을 때도 `lsof -nP -iTCP:31248 -sTCP:LISTEN`은 `127.0.0.1:31248 (LISTEN)`만 표시했다. 종료 후 해당 포트의 listener는 없었다. 최종 코드 변경 후 lint·typecheck·test 게이트를 각각 1회 다시 실행해 모두 exit 0을 확인했다. 개발 중에는 누락된 ESLint 의존성으로 lint 1회, SDK와 Node의 요청 타입 차이로 typecheck 3회가 실패했으나 수정했다. 최종 테스트 실패는 없다.

## 실제 MCP 통합 결과

`tests/mcp.test.ts`는 공식 `@modelcontextprotocol/client`의 `Client`와 `StreamableHTTPClientTransport`로 실제 loopback HTTP 연결을 생성한다. `pnpm test` 통과는 health 응답만 확인한 결과가 아니다. 별도로 실행한 공식 클라이언트 호출의 결과는 다음과 같다.

```json
{
  "initialize": { "name": "itzcuauhtli", "version": "0.1.0" },
  "tools": ["list_notes", "read_note", "search_notes"],
  "listCount": 4,
  "readPath": "Notes/alpha.md",
  "readHasApple": true,
  "searchCount": 3,
  "invalid": { "error": true, "body": { "code": "INVALID_PATH", "message": "Path is not allowed" } }
}
```

클라이언트는 `terminateSession()`과 `close()`를 호출했고 서버도 종료됐다. 서버의 도구 로그는 request ID, 도구명, 성공 여부, 실행 시간, 오류 코드만 담았다. MCP 응답 및 서버 자체 로그에서 호스트 절대경로, stack trace, 문서 전체 내용을 확인하지 못했다. `pnpm dev` 자체의 실행 배너는 작업 디렉터리를 표시하므로 README는 배너를 억제하는 `pnpm --silent dev`를 안내한다.

## 외부 sentinel과 접근 경계

테스트 중 임시 디렉터리에 합성 sentinel을 만들고 Vault 안에 그 파일을 향하는 symlink를 만들었다. 읽기는 `SYMLINK_FORBIDDEN`으로 실패했다. sentinel의 읽기 전후 SHA-256은 모두 다음 값이었다.

```text
6005a436f6d91e67791b15ff08551d18adc69aa6ccf2d2468ba532b68f4d880b
```

실제 Minerva 저장소, 실제 Obsidian Vault, NAS는 열거나 변경하지 않았다. remote Git fetch·push·PR·release도 실행하지 않았다. 검증 범위는 이 저장소의 합성 fixture, 테스트 중 생성한 임시 합성 파일, Node/pnpm 패키지 설치와 공식 SDK 문서 확인이었다. 브라우저 또는 GUI 자동화는 사용하지 않았다.

## 12개 수용 기준

| 번호 | 판정 | 근거 |
|---:|---|---|
| 1 | PASS | 빈 설치 디렉터리에서 frozen lockfile 설치 성공 |
| 2 | PASS | lint, strict typecheck, Vitest 30개 테스트 성공 |
| 3 | PASS | Obsidian 앱·GUI 없이 서버 실행 |
| 4 | PASS | loopback listener 확인; `HOST=0.0.0.0` 무시 |
| 5 | PASS | 공식 MCP 클라이언트 initialize, tools/list 성공 |
| 6 | PASS | 도구 정확히 3개 |
| 7 | PASS | fixture에서 list/read/search 실제 호출 성공 |
| 8 | PASS | traversal, 절대경로, symlink, dot-directory 접근 거부 테스트 |
| 9 | PASS | 비 Markdown 및 1 MiB 초과 파일 읽기 거부 |
| 10 | PASS | MCP 응답과 서버 자체 로그에 호스트 절대경로·stack trace·문서 전체 로그 없음 |
| 11 | PASS | 실제 Minerva·Vault·NAS·remote Git 접근/변경 없음 |
| 12 | PASS | 하나의 clean candidate commit과 실행 증거 제공 |

## 남은 제한과 다음 단계

서버는 인증이 없고 loopback 전용이다. NAS나 외부 네트워크에 배포하면 안 된다. symlink와 경로의 정적 접근 및 일반적인 재검사는 검증했지만, 다른 프로세스가 디렉터리를 검사와 열기 사이에 계속 교체하는 극단적인 경합까지 원자적으로 차단했다고 증명하지는 못했다. 이 잔여 위험 때문에 전체 판정을 `PASS_WITH_ISSUES`로 표시한다.

Dovie가 commit과 이 보고서를 검토해 첫 MVP 수용 여부를 결정한다. 수용 뒤에는 **안전한 쓰기**, **NAS 실행 기반**, **Obsidian 구조** 중 하나만 별도 작업으로 선택한다.
