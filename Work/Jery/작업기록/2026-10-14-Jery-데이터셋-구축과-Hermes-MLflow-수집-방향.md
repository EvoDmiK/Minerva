---
created: 2026-10-14
date: 2026-10-14
project: Jery
type: worklog
status: in-progress
tags:
  - jery
  - mcp
  - dataset
  - hermes
  - mlflow
  - n8n
  - worklog
---
# Jery 데이터셋 구축과 Hermes·MLflow 수집 방향

## 요약

Jery는 MCP 도구 선택을 위한 경량 로컬 학습 결정 모델 프로젝트다. 오늘은 Hermes의 도구 구성을 확인하고, 실제 도구 명세 일부를 사용한 한국어 합성 데이터셋 130개를 만들었다. 프로젝트 README를 작성해 dev-codex에 커밋·푸시했다.

실제 사용 데이터 확보 방법으로 Hermes 로그 추출, n8n 수집 자동화, MLflow 요청·응답 및 도구 선택 추적을 논의했다. n8n 워크플로 JSON과 API 계약은 로컬 초안으로 만들었으며, 수집기 API와 MLflow 기록 기능은 아직 구현하지 않았다. 마지막 논의는 MLflow에 대화를 기록하면서 중간 도구 선택 단계도 함께 남기는 방향이었다. 운영 적용이나 최종 아키텍처 확정은 이루어지지 않았다.

이 문서는 2026-10-14 대화와 확인한 작업 결과를 요약한 기록이다. 전날의 프로젝트 소개·일반 데이터 수집 조언은 배경으로만 반영했다.

## 작업 및 논의 상태

| 항목 | 결과 | 상태 |
|---|---|---|
| Hermes MCP·기본 도구 조사 | 운영 프로필 hybrid-v2, MCP 서버 5개, 기본 도구 세트 11개 확인 | 조사 완료 |
| 초기 데이터셋 | 도구 10개, 한국어 합성 사례 130개 | 생성·형식 검증 완료, 사람 검토 필요 |
| Git 이메일 오류 | 저장소 이메일과 미푸시 커밋을 GitHub noreply 주소로 수정 | 해결 |
| 프로젝트 README | 목적, 현재 상태, 데이터 구성과 사용 방법 작성 | 커밋·푸시 완료 |
| 에이전트 역할 | Codex·Claude·Antigravity의 수정 범위와 보고 기준 정의 | AGENTS.md 작성·자식 워크트리 복사, 미커밋 |
| n8n 수집 흐름 | 실제 로그를 검토 대기로 저장하는 JSON과 API 계약 | 로컬 비활성 초안, 미커밋·미배포 |
| MLflow 추적 | 요청·응답과 중간 도구 선택·실행 기록 제안 | 논의 단계, 미구현 |

## 1. Hermes 도구 구성

현재 운영 프로필은 `hybrid-v2`다. 설정과 스키마 캐시를 확인했으며, 모든 MCP 도구를 직접 실행한 것은 아니다.

| 서버 | 용도 | 캐시에서 확인한 도구 |
|---|---|---:|
| obsidian_vault | 문서 검색·읽기·편집·링크 탐색·질의 | 8개 + 리소스 도구 2개 |
| korean_law | 법령·판례·결정문 검색과 분석 | 10개 |
| swallow_trader | 주가·뉴스·모의투자·백테스트 | 13개 |
| kestrel | Codex 사용량 리셋 현황 조회 | 1개 |
| grafana | 모니터링 데이터 조회, 쓰기 비활성 | 캐시 없음 |

Grafana는 10월 11일 로그에 `/usr/local/bin/uvx` 실행 파일이 없어 연결에 실패한 기록이 있었다. Korean Law 등에는 연결 오류·재연결 기록이 있어, 설정 등록과 현재 연결 상태를 구분해야 한다.

기본 도구 세트는 web, terminal, file, skills, todo, memory, session_search, clarify, code_execution, delegation, cronjob이다. 브라우저, 컴퓨터 조작, 이미지 인식·생성, TTS는 확인 당시 설정에서 비활성화되어 있었다.

## 2. 초기 데이터셋

`datasets/hermes-routing-v1/`에 실제 Hermes 도구 명세를 사용한 합성 사례를 저장했다. 실제 대화 로그·계좌 정보·문서 본문을 사용한 데이터는 아니다.

| 항목 | 내용 |
|---|---|
| 카탈로그 | `hermes-subset-10c30cef05cc` |
| 도구 | Obsidian 4개, Swallow 5개, Kestrel 1개 |
| 사례 | 원본 시나리오 65개 × 표현 변형 2개 = 130개 |
| 분할 | 학습 78개, 검증 26개, 평가 26개 |
| 결정 | select_tools 100개, no_tool·clarify·unsupported 각 10개 |
| 검토 | 모두 needs_human_review |
| 실행 | 모두 execution_verified: false |

포함 도구:
- Obsidian: `vault`, `edit`, `view`, `graph`.
- Swallow: `swallow_get_stock_price`, `swallow_get_stock_news`, `swallow_get_price_history`, `swallow_get_portfolio`, `swallow_get_trades`.
- Kestrel: `get_codex_reset_status`.

도구 설명과 입력 스키마는 `tools.json`, 사례는 분할별 JSONL, 건수와 체크섬은 `manifest.json`에 저장했다. 동일 시나리오의 표현 변형은 같은 분할에 들어간다. 도구 action은 보조 라벨이며 전체 호출 인자를 생성하는 데이터셋은 아니다.

`unsupported`는 해당 사례의 후보 10개로 처리할 수 없다는 의미다. 전체 Hermes에는 초기화·주문 도구가 있어도 이 후보 목록에서 빠져 있으면 지원 불가로 분류한다.

검증 명령:

```sh
python3 scripts/validate_dataset.py
```

확인 결과:

```text
PASS: 130 examples, 10 tools, 65 isolated scenarios
```

중복, 도구 참조, action enum, 분할 간 시나리오 누출, 분할별 도구 커버리지와 체크섬을 확인했다. 사람의 의미적 정답 검토나 실제 운영 성능 검증은 별도 과제다.

## 3. 실제 로그를 학습 사례로 바꾸는 기준

Hermes `state.db`의 messages·sessions 테이블에서 대화 본문, 도구 호출, 결과 연결 ID, 세션과 시각을 확인했다. 실제 수집기는 아직 구현하지 않았다.

- 대화 전체를 복원한 뒤 도구 선택 시점마다 사례를 만든다.
- 입력에는 해당 선택 이전 정보만 넣고, 현재 호출 결과·이후 답변은 검토 근거로 분리한다.
- 기존 에이전트 선택은 관측값으로 보존하고, 검토 후 정답을 부여한다.
- 정상 실행과 적절한 도구 선택은 별개다. 타임아웃을 잘못된 선택으로 단정하지 않는다.
- 당시 후보 도구·카탈로그를 기록한다. 현재 캐시로 복원하면 복원 여부를 표시한다.
- 무호출 대화에서도 no_tool·clarify 사례를 확보한다.
- 개인정보와 인증 정보를 제거하고, 같은 세션·파생 대화를 같은 분할에 묶는다.

기존 텔레메트리 수집 스키마에는 성공 호출이 일부만 로그에 기록된다는 설명이 있어, 실행 로그만으로 완전한 사용 데이터셋을 구성하면 누락이 생길 수 있다.

## 4. 에이전트 역할

| 브랜치 | 에이전트 | 담당 |
|---|---|---|
| dev-codex | Codex | 합성 데이터 생성, 실제 로그 수집·정제, 계약·분할·검증, 최종 통합 |
| dev-claude | Claude | 기준 모델, 학습·평가, 로컬 예측 함수 |
| dev-agy | Antigravity | 사람이 정답을 검토·수정하는 도구, 결과 시각화 |

Orca에서 dev-codex 아래의 두 자식 워크트리를 확인했다. `Jery/main`은 dev-claude, `Jery/main-2`는 dev-agy다. 표시 이름 대신 브랜치로 역할을 구분한다.

루트 `AGENTS.md`를 작성해 두 워크트리에 동일하게 복사했다. 담당 파일 범위, 공통 스키마, 데이터 누출 방지, 테스트와 완료 보고 기준을 명시했다. 실제 작업 지시는 아직 보내지 않았다. 검토 결과를 최종 학습 데이터에 반영하는 일도 Codex가 맡는다.

## 5. n8n 워크플로 초안

생성 파일:
- `workflows/n8n/hermes-logs-to-review.json`
- `workflows/n8n/README.md`
- `docs/contracts/log-candidates-api-v1.md`

흐름:

```text
수동 실행 / 5분 주기
 → Configuration
 → 정제된 로그 배치 가져오기
 → 검토 후보 형식 검증
 → 검토 대기 저장·체크포인트 갱신
 → 저장 결과 확인
```

수집기는 DB 읽기 전용 접근, 호출 전 맥락 복원, 개인정보 제거를 맡는다. n8n은 주기 실행과 배치 전달을 맡는다. 저장 API는 동일 배치를 재시도해도 중복이 생기지 않게 하고, 영속 저장과 체크포인트 갱신을 한 트랜잭션에서 수행해야 한다.

초안의 `http://jery-collector:8080`은 예시 주소다. API는 미구현이며 실제 n8n 가져오기·실행·활성화는 수행하지 않았다. 연결 참조와 JavaScript 검증·응답 확인 로직은 로컬 11개 체크를 통과했다.

현재 워크플로는 `decision: null`, `acceptable_choices: []`, `needs_human_review`인 검토 후보를 만든다. 사람이 검토하기 전에는 학습 데이터로 바로 사용하지 않는다.

## 6. MLflow 요청·응답 추적 제안

사용자가 Hermes의 요청–응답 쌍을 MLflow에 트래킹하는 방식을 제안했다. 요청과 최종 답변을 기록하고, Jery 학습용으로 중간 선택·실행 단계도 함께 추적하는 구조를 논의했다.

| 기록 단위 | 저장할 정보 |
|---|---|
| 요청 전체 trace | 정제된 사용자 요청, 최종 응답, 가명 세션 ID |
| 도구 선택 시점 | 호출 전 맥락, 후보 도구와 명세 버전, 관측된 도구·action |
| 실행 span | 정제된 입력·결과, 오류, 실행 시간 |
| 정답 검토 | 선택 적절성, 허용 정답과 수정 의견 |

```text
Hermes
 → MLflow trace/span 기록
 → 선택 정답 검토
 → 세션별 분할·JSONL 내보내기
 → Jery 학습·평가
```

요청–최종 응답만 저장하면 답변 기록은 확보할 수 있지만, 어떤 후보 중에서 어떤 도구를 골랐는지는 부족하다. 도구 선택 직전 정보까지 남겨야 다음 도구 선택 데이터로 전환하기 쉽다. n8n은 이후 주기적인 내보내기를 담당할 수 있다.

이 구성은 제안 단계이며 Hermes MLflow instrumentation, experiment 설정과 실제 데이터 적재는 수행하지 않았다. MLflow 장애가 Hermes 응답에 미치는 영향, 기존 추적과의 중복, 설치 버전·지원 API는 구현 전에 확인해야 한다.

## 7. 형상 관리와 확인 결과

GitHub 푸시는 커밋 작성자 이메일의 개인정보 보호 설정 때문에 거절되었다. 기존 커밋에서 확인한 GitHub noreply 주소를 이 저장소의 로컬 설정에 적용하고, 미푸시 커밋의 작성자·커미터 이메일을 수정했다. 수정 전후 파일 트리 해시는 같았다. 개인 이메일은 이 노트에 기록하지 않았다.

- 데이터셋 커밋: [86452ff — feat: Jery 학습 데이터 기획](https://github.com/EvoDmiK/Jery/commit/86452ff).
- README 커밋: [85b76a0 — docs: 프로젝트 개요와 데이터셋 사용 방법 작성](https://github.com/EvoDmiK/Jery/commit/85b76a0).
- README 커밋을 origin/dev-codex에 푸시하고 로컬·원격 동기화를 확인했다.
- 오늘 기록 시점에는 AGENTS.md, docs/, workflows/가 로컬 미추적 파일로 남아 있다.

## 8. 후속 과제

- [ ] MLflow 기록 방식의 적용 범위와 기존 Hermes 추적 상태 확인.
- [ ] 요청·최종 응답 및 도구 선택 직전 맥락을 정제해 기록하는 수집 기능 구현.
- [ ] 후보 명세의 버전 보관과 당시 후보 복원 기준 확정.
- [ ] 정답 검토 도구와 실제 사용 사례 평가 세트 구축.
- [ ] 합성 정답 검토 후 기준 모델 학습·평가.
- [ ] AGENTS.md와 n8n/API 초안 검토 후 커밋·푸시.
- [ ] n8n을 사용한다면 수집기 API 구현 후 수동 실행으로 통합 검증.

## 관련 문서와 출처

- [[Work/Jery/index|Jery 프로젝트 인덱스]]
- [[Work/index|프로젝트 목록]]
- [[Work/Birds-Nest/작업기록/Hermes/index|Hermes 작업기록]]
- [[Dev/자동화/n8n-워크플로우-신뢰성-및-에러-복구-패턴|n8n 신뢰성과 에러 복구]]
- [Jery GitHub 저장소](https://github.com/EvoDmiK/Jery).
- [MLflow span 문서](https://www.mlflow.org/docs/latest/genai/concepts/span/).
- [MLflow trace 검색](https://mlflow.org/docs/latest/genai/tracing/search-traces/).
- [MLflow trace 평가·피드백](https://www.mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/).

작업 사실은 오늘 대화와 로컬 저장소 확인 결과를 근거로 한다. 기술 문서 링크는 설계 참고 자료이며 운영 적용 증거는 아니다.
