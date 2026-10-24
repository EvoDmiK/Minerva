---
date: 2026-10-24
created: 2026-10-24
document_role: source
domain: article
tags:
  - llm-wiki
  - source
  - openenv
  - aaif
  - trl
  - hugging-face
  - reinforcement-learning
  - agent
  - mcp
source_url: https://discuss.pytorch.kr/t/openenv-aaif-trl-feat-hugging-face/12279
author: "박정환 (9bow)"
published_at: "2026-10-24T00:30:00.000Z"
collected: 2026-10-24
converter: "markdown-converter / markitdown"
---

# OpenEnv, AAIF 프로젝트로 합류: 에이전트 학습 환경을 과제 정의부터 TRL 학습까지 만드는 방법 (feat. Hugging Face)

> [!info] 원문 보관 범위
> 요청한 PyTorchKR 게시글의 본문 전체를 Markdown으로 변환한 원문 보관본입니다. 요약이나 해설로 대체하지 않았습니다. 표·코드·링크·이미지 URL을 보존했습니다. 변환 검증은 원문 주장이나 예제 코드 실행의 검증을 뜻하지 않습니다.

## 핵심 요약

* OpenEnv 메인테이너 9명이 [AAIF 블로그에 합류 글](https://aaif.io/blog/training-agents-for-real-world-tasks-with-openenv)을 썼습니다. 글은 에이전트 학습 환경을 만드는 순서를 여섯 단계로 정리합니다.
* [Agentic AI Foundation(AAIF)](https://aaif.io/news/agentic-ai-foundation-announces-four-new-projects)은 2026년 10월 22일 OpenEnv를 새 호스팅 프로젝트로 발표했습니다. AAIF 기술 위원회는 10월 6일 OpenEnv를 Growth 단계 프로젝트로 승인했습니다.
* 원문의 핵심 경고는 보상 점수가 올라도 모델이 의도한 행동을 배웠다는 보장이 없다는 것입니다. Pelican SVG 실험에서 Qwen3-1.7B는 자전거 모양의 구조 점수만 올렸고 새는 그리지 못했습니다.
* 원문은 Echo MCP 데모와 FinQA 코드를 v0.9.0(10월 15일) 태그로 링크합니다. 원문이 나온 10월 22일에 v0.10.0이 나왔고, [OpenEnv 저장소](https://github.com/openenv/OpenEnv)는 `openenv/OpenEnv` 조직으로 옮겨졌습니다.

[![OpenEnv의 AAIF 합류와 에이전트 학습 환경 만드는 법을 세 묶음으로 요약한 그림](https://discuss.pytorch.kr/uploads/default/optimized/3X/2/7/276666b39eba08e2157d4f8f19727b8147e66396_2_1028x685.jpeg)

OpenEnv의 AAIF 합류와 에이전트 학습 환경 만드는 법을 세 묶음으로 요약한 그림1536×1024 231 KB](https://discuss.pytorch.kr/uploads/default/original/3X/2/7/276666b39eba08e2157d4f8f19727b8147e66396.jpeg "OpenEnv의 AAIF 합류와 에이전트 학습 환경 만드는 법을 세 묶음으로 요약한 그림")

## OpenEnv 소개: 학습 환경을 여러 학습 시스템에서 다시 쓰기 위한 공통 인터페이스

[OpenEnv](https://huggingface.co/docs/openenv/index)는 에이전트를 **강화학습(Reinforcement Learning, RL)** 으로 학습시키고 평가할 환경을 위한 오픈소스 프레임워크입니다. 환경을 만들고 공유하고 학습 시스템에 연결하는 일을 맡습니다. 2025년 10월 PyTorch Conference에서 Hugging Face와 Meta(Meta-PyTorch)의 공동 프로젝트로 시작했습니다. 2026년 10월 22일에는 Linux Foundation 산하 [Agentic AI Foundation(AAIF)](https://aaif.io/)이 OpenEnv를 새 호스팅 프로젝트로 발표했습니다.

OpenEnv의 기본 API와 환경 구조, 보상 시스템은 [지난 9월의 OpenEnv 프로젝트 소개 글](https://discuss.pytorch.kr/t/openenv-feat-meta-hugging-face/11812)에서 자세히 다뤘습니다. Calendar Gym 실측과 RFC(Request for Comments, 설계 제안 문서) 로드맵도 그 글에 있습니다. 이 글은 그 뒤에 나온 AAIF 합류 글을 옮기고, 원문이 링크만 걸어 둔 문서와 코드에서 확인한 내용을 덧붙입니다.

[![AAIF 블로그 원문의 대표 그림. 격자 위 에이전트 큐브가 깃발 칸으로 이동하는 모습](https://discuss.pytorch.kr/uploads/default/optimized/3X/3/3/337ebcd4c36acd96e6e0d7a0db120631143f08be_2_1028x537.png)

AAIF 블로그 원문의 대표 그림. 격자 위 에이전트 큐브가 깃발 칸으로 이동하는 모습1200×627 395 KB](https://discuss.pytorch.kr/uploads/default/original/3X/3/3/337ebcd4c36acd96e6e0d7a0db120631143f08be.png "AAIF 블로그 원문의 대표 그림. 격자 위 에이전트 큐브가 깃발 칸으로 이동하는 모습")

원문은 OpenEnv 메인테이너 9명이 함께 썼습니다. Hugging Face의 Ben Burtenshaw, Sergio Paniego Blanco, Kashif Rasul, Reflection의 Zach Wentz, Sanyam Bhutani, Kai Wu, Joseph Spisak, Meta의 Davide Testuggine, Microsoft의 Govind Kamtamneni입니다. 소속은 [AAIF 합류 제안서](https://github.com/aaif/project-proposals/issues/50)의 메인테이너 표를 따랐습니다. 원문 첫머리의 요약은 다음과 같습니다.

> *"OpenEnv는 클라이언트와 환경 서버로 동작합니다. 클라이언트는 에피소드를 시작하고, 행동을 제출하고, 결과를 받습니다. 환경 작성자는 과제의 동작과 피드백을 정의한 뒤, 다른 사람이 실행할 수 있도록 환경을 패키징합니다."*
>
> > *"OpenEnv uses a client and environment server. The client starts an episode, submits actions, and receives results. Environment authors define the task behavior and feedback, then package the environment so others can run it."*

원문은 회의 일정 잡기 예시로 시작합니다. 에이전트가 회의를 잡으려면 어느 캘린더를 써야 하는지, 무엇을 바꿀 권한이 있는지, 어떤 작업을 먼저 해야 하는지를 스스로 판단해야 합니다. [Turing](https://www.turing.com/)은 다른 사용자의 캘린더를 일부만 볼 수 있는 조건에서 이 판단을 시험하려고 [Calendar Gym](https://huggingface.co/blog/openenv-turing)을 만들었습니다. Turing 팀의 보고에 따르면, 과제에 캘린더 식별자를 명시했을 때 성공률은 약 90%였습니다. 같은 과제를 자연어 설명으로 주었을 때는 약 40%였습니다. 쉬워 보이던 과제도 에이전트가 세부 사항을 직접 해석해야 하자 훨씬 어려워졌습니다.

이런 과제로 학습하려면 개발자에게 두 가지가 필요합니다. 첫째는 에이전트가 할 수 있는 일, 볼 수 있는 정보, 행동을 평가하는 방법을 정의한 환경입니다. 둘째는 그 환경을 학습 시스템에 연결하는 방법입니다. 메인테이너들은 OpenEnv의 [거버넌스 문서(GOVERNANCE.md)](https://github.com/openenv/OpenEnv/blob/main/GOVERNANCE.md)가 이 연결을 재사용하기 어려운 이유를 설명한다고 소개합니다. 학습 시스템, 평가 도구, 에이전트 하네스(Agent Harness, 모델을 감싸 도구 호출과 실행 루프를 관리하는 프로그램)가 저마다 다른 인터페이스를 쓰기 때문입니다. OpenEnv가 공통 인터페이스를 제공하면, 개발자는 연결 코드보다 과제 정의에 더 많은 시간을 쓸 수 있습니다.

## 보상을 고르기 전에 과제의 경계부터 정합니다

메인테이너들은 과제의 경계에서 시작한다고 씁니다. 어떤 행동이 유효한지, 에이전트가 어떤 정보를 받아야 하는지, 무엇을 완료로 볼지를 먼저 정합니다. OpenEnv는 이 선택을 [구조화된 행동(Action), 관찰(Observation), 상태(State) 타입](https://huggingface.co/docs/openenv/guides/first-environment)으로 표현합니다. 환경은 과제의 동작을 구현하고, 서버는 그 환경을 클라이언트에 제공합니다.

[Wordle 튜토리얼](https://huggingface.co/docs/openenv/tutorials/wordle-grpo)이 이 선택을 보여 주는 작은 예입니다. 에이전트는 다섯 글자 단어를 추측해 제출합니다. 환경은 글자마다 위치까지 맞음(GREEN), 단어에 있지만 위치가 틀림(YELLOW), 단어에 없음(GRAY)을 돌려줍니다. 정답 단어는 숨겨져 있고, 에이전트가 정답을 맞히거나 여섯 번의 기회를 모두 쓰면 게임이 끝납니다. 캘린더 과제에는 다른 행동과 관찰이 필요합니다. 그래도 작성자가 에이전트가 무엇을 볼 수 있는지, 언제 작업이 끝나는지를 정해야 한다는 점은 같습니다.

## 상호작용과 과제 로직을 분리합니다

경계가 정해지면 클라이언트가 과제를 실행할 방법이 필요합니다. 클라이언트는 `reset()`으로 에피소드를 시작하고, `step()`으로 행동을 제출하며, `state()`로 상태를 요청할 수 있습니다. 결과에는 관찰, 숫자 보상, 에피소드 종료 여부, 메타데이터가 들어 있습니다. OpenEnv는 이 상호작용을 위해 [동기와 비동기 클라이언트](https://huggingface.co/docs/openenv/guides/concepts)를 모두 제공합니다.

이 상호작용 방식은 과제가 바뀌어도 그대로입니다. Wordle의 추측과 캘린더 작업은 각자의 행동 타입으로 표현하고, 클라이언트는 같은 API로 에피소드를 관리합니다. 원문은 공통 인터페이스 덕분에 연동 코드는 재사용할 수 있지만, **동작과 채점은 여전히 환경마다 따로 정의해야 한다**고 강조합니다.

[Core Concepts 문서](https://huggingface.co/docs/openenv/guides/concepts)를 보면, 같은 `AutoEnv` API로 비동기 클라이언트와 동기 클라이언트를 모두 만들 수 있습니다. 다만 클라이언트 하나는 처음 쓴 방식에 고정되므로, 문서는 동기 방식에 별도 클라이언트를 만들라고 주석으로 안내합니다:

```
from openenv import AutoEnv

# Async
async with AutoEnv.from_env("coding") as client:
    result = await client.reset()
    result = await client.step(action)

# Sync, with its own client (a client is locked to the mode it is first used in)
with AutoEnv.from_env("coding").sync() as client:
    result = client.reset()
    result = client.step(action)
```

## MCP를 지원하는 환경에서는 도구 인터페이스를 재사용합니다

일부 환경은 [도구를 MCP로 노출](https://huggingface.co/docs/openenv/tutorials/mcp-environment)합니다. 그러면 같은 도구를 학습 중에도, 외부 에이전트에서도 쓸 수 있습니다. **MCP(Model Context Protocol)** 는 에이전트가 외부 도구의 목록과 입력 형식을 조회하고 호출하는 표준 프로토콜입니다. 학습 시스템은 `reset`, `step`, `state`로 에피소드를 관리하고, MCP는 에이전트가 호출할 도구를 설명합니다. 메인테이너들은 이렇게 하면 학습 실행을 제어하는 일과 과제 안에서 쓸 수 있는 행동이 분리된다고 설명합니다.

어느 경로를 쓸지는 환경 구현이 정합니다. OpenEnv v0.9.0에서 [FinQA 환경](https://github.com/openenv/OpenEnv/blob/v0.9.0/envs/finqa_env/server/finqa_environment.py)은 `MCPEnvironment` 기반 클래스를 상속합니다. [Echo 예제](https://github.com/openenv/OpenEnv/blob/v0.9.0/examples/echo_mcp_demo.py)는 `step()`을 통한 도구 탐색, 호출, 오류 처리를 보여 줍니다. 반면 Wordle은 [MCP 튜토리얼](https://huggingface.co/docs/openenv/tutorials/mcp-environment)의 설명대로 여전히 자체 행동 타입을 씁니다. 그래서 메인테이너들은 연동 방식을 고르기 전에 환경이 지원하는 인터페이스부터 확인한다고 씁니다.

### 원문이 링크한 문서에서 확인한 MCP 사용 범위

원문이 *"환경이 지원하는 인터페이스를 확인하라"* 고 말하는 이유는 MCP 튜토리얼에 나옵니다. 튜토리얼은 MCP를 모든 에이전트 행동의 표준 인터페이스로 삼자는 [RFC 003](https://github.com/openenv/OpenEnv/blob/main/rfcs/003-mcp-support.md)이 아직 검토 중(In Review)이라고 밝힙니다. RFC 003 문서 헤더도 In Review입니다. 반면 GOVERNANCE.md의 RFC 표와 AAIF 제안서는 RFC 003을 출시됨(Shipped)으로 적어, 문서마다 상태 표기가 다릅니다. 필자는 이를 MCP 지원 코드는 들어와 있지만, MCP를 모든 환경의 표준 인터페이스로 삼는 결정은 아직 승인되지 않은 상태로 해석합니다.

튜토리얼 기준으로 `MCPEnvironment`를 상속하는 환경은 `echo_env`와 `finqa_env`이고, `calendar_env`는 같은 형태의 자체 래퍼(Wrapper)를 씁니다. Wordle을 제공하는 `textarena_env`, `openspiel_env`, `chess_env`, `browsergym_env`를 비롯한 대부분의 환경은 MCP 없이 자체 행동 타입을 씁니다.

MCP 튜토리얼은 두 인터페이스의 역할도 나눠 설명합니다:

| 사용 주체 | 엔드포인트 | 하는 일 |
| --- | --- | --- |
| 학습, 오케스트레이션 인프라 | WebSocket `/ws` | `reset()`, `step()`, `state()`로 에피소드 진행, 보상 계산, 종료 판단 |
| 에이전트 | JSON-RPC `/mcp` | MCP 도구 호출 |

시뮬레이션 모드(학습)에서는 MCP 도구 호출도 `step()`을 거치므로, 학습기가 시간, 보상, 종료를 계속 제어합니다. 반대로 외부 에이전트가 `/mcp`를 직접 호출하면 보상 계산, 스텝 카운트, 에피소드 종료를 거치지 않습니다. 이때는 등록된 MCP 도구만 보이고 `reset`, `step`, `state`는 보이지 않습니다. 또 `reset`, `step`, `state`, `close`는 예약된 이름이라 도구 이름으로 쓸 수 없습니다.

FinQA는 이 구조를 실제 과제에 쓴 환경입니다. 과제는 미국 증권거래위원회(Securities and Exchange Commission, SEC)의 10-K 공시 데이터에 대한 질문에 답하는 것입니다. 에이전트는 `get_descriptions`, `get_table_info`, `sql_query`, `submit_answer` 네 도구를 씁니다. 표를 찾고 SQL을 실행한 뒤 답을 제출하는 순서입니다. 에피소드당 도구 호출은 기본 50번까지입니다.

### Echo MCP 데모를 v0.9.0에서 직접 실행한 결과

원문이 v0.9.0 기준으로 링크한 [`examples/echo_mcp_demo.py`](https://github.com/openenv/OpenEnv/blob/v0.9.0/examples/echo_mcp_demo.py)는 Echo 환경 하나로 도구 목록 조회, 도구 호출, 존재하지 않는 도구 호출까지 네 단계를 실행합니다. 핵심 부분은 다음과 같습니다:

```
from echo_env.server.echo_environment import EchoEnvironment
from openenv.core.env_server.mcp_types import (
    CallToolAction,
    CallToolObservation,
    ListToolsAction,
    ListToolsObservation,
)

# Create the environment
env = EchoEnvironment()
env.reset()

# Step 1: List available tools via ListToolsAction
obs = env.step(ListToolsAction())
assert isinstance(obs, ListToolsObservation)

# ...

# Step 2: Call echo_message tool via CallToolAction
obs = env.step(
    CallToolAction(
        tool_name="echo_message",
        arguments={"message": "Hello from MCP!"},
    )
)

# ... (Step 3: echo_with_length, assertions omitted)

# Step 4: Handle tool errors gracefully
obs = env.step(
    CallToolAction(
        tool_name="nonexistent_tool",
        arguments={},
    )
)
```

필자가 v0.9.0 태그를 받아 저장소 루트에서 파일에 적힌 명령(`PYTHONPATH=src:envs uv run python examples/echo_mcp_demo.py`)을 그대로 실행했습니다. 실행 환경은 macOS, Python 3.13.11, fastmcp 3.4.11이었고, `uv`가 의존 패키지 116개를 설치한 뒤 다음 결과를 냈습니다:

```
Step 1: List available MCP tools
----------------------------------------
Found 2 tools:
  - echo_message: Echo back the provided message.
  - echo_with_length: Echo back the message with its length.

Step 2: Call 'echo_message' tool
----------------------------------------
Tool: echo_message
Result: Hello from MCP!
Error: None

Step 3: Call 'echo_with_length' tool
----------------------------------------
Tool: echo_with_length
Result: {'message': 'Count my characters', 'length': 19}
Error: None

Step 4: Handle non-existent tool
----------------------------------------
Tool: nonexistent_tool
Result: None
Error: error_type=<ToolErrorType.TOOL_NOT_FOUND: 'tool_not_found'> message="Unknown tool: 'nonexistent_tool'"
```

4단계에서 오류가 예외로 터지지 않고 관찰의 `error` 필드로 돌아온다는 점이 학습 코드에 중요합니다. MCP 튜토리얼에 따르면 `error_type`은 `TOOL_NOT_FOUND`, `INVALID_ARGS`, `EXECUTION_ERROR`, `TRANSPORT_ERROR`, `TIMEOUT` 다섯 가지입니다. 튜토리얼은 이 구분으로 에이전트의 잘못, 환경의 버그, 일시적인 인프라 문제를 나눌 수 있고, 각 경우에 다른 보상 신호가 필요할 수 있다고 설명합니다. 반면 `MCPToolClient`의 비동기 `call_tool()` 헬퍼는 도구의 반환값만 돌려주고, 오류가 나면 `RuntimeError`를 던집니다. 보상이나 오류 종류가 필요하면 `step(CallToolAction(...))`을 써야 합니다.

## 피드백이 의도한 행동을 반영하게 합니다

에이전트가 어느 인터페이스를 쓰든, 피드백은 학습시키려는 과제를 반영해야 합니다. OpenEnv의 [보상 설계 문서](https://huggingface.co/docs/openenv/guides/rewards)는 과제 완료, 중간 진척, 감점을 다룹니다. 메인테이너들은 **점수를 올리는 것이 곧 의도한 행동을 더 잘하는 것일 때만 그 점수가 쓸모 있다**고 쓰고, 그래서 보상 곡선뿐 아니라 모델 출력도 직접 본다고 덧붙입니다.

보상 문서의 설계 원칙은 세 가지입니다. 성공과 실패만 주는 희소 보상(Sparse Reward)으로 시작해 에이전트가 성공 신호에 도달할 수 있는지부터 확인합니다. 중간 보상은 `WeightedSum`에서 작은 가중치를 준 구성 요소로 더하는 쪽을 권해, 실제 결과가 최종 점수를 좌우하게 합니다. 결과가 늦게 나오는 긴 과제에는 손으로 만든 밀집 보상(Dense Reward) 대신 `TrajectoryRubric`의 스텝별 기여도 할당(Credit Assignment)을 씁니다. 문서가 꼽는 함정 네 가지 중 첫 번째는 보상 해킹(Reward Hacking)입니다. 에이전트가 목표 대신 대리 지표를 최적화하는 현상입니다.

### Pelican SVG 실험: 구조 점수는 올랐지만 새는 그리지 못했습니다

원문은 [Pelican SVG 환경](https://huggingface.co/docs/openenv/environments/pelican_svg)을 예로 듭니다. 구조 검사가 자전거 같은 기하 구조에 보상을 주었는데, 모델은 새를 그리는 법을 배우지 못했습니다. 시각 판정 모델을 추가해도 보고된 실행에서는 문제가 풀리지 않았습니다. 그 모델에게 판정 모델의 피드백이 쓸 만한 신호를 거의 주지 못했기 때문입니다. 원문은 이 실험에서 더 정교한 채점기를 고르는 것만으로는 부족하고, 피드백이 모델의 학습을 실제로 도와야 한다는 결론을 냅니다.

Pelican SVG 환경 문서에 실험의 수치가 나옵니다. 이 환경은 [Simon Willison](https://simonwillison.net/)이 알린 *"자전거를 탄 펠리컨을 SVG로 그려라"* 과제를 반복 실행하고 학습에 쓸 수 있게 만든 것입니다. 모델은 그린 결과를 보지 못한 채 SVG 좌표를 출력합니다. 채점은 세 층입니다:

| 층 | 비용 | 가중치 | 검사 내용 |
| --- | --- | --- | --- |
| 게이트(Gate) | 무료 | 통과 또는 0점 | SVG 없음, 렌더링 실패, 이미지 삽입, `<text>`로 답 쓰기 같은 부정행위 차단 |
| 구조(Structure) | 무료 | 0.35 | 바퀴 수, 크기, 높이, 간격, 바퀴 사이 프레임, 탑승자 유무와 비율 등 기하 검사 7개 |
| 시각 판정(Vision Judge) | 판정 모델 호출 | 0.65 | 과제를 알려 주지 않은 캡션, 부리와 목주머니 같은 특징의 예/아니오 체크리스트 |

[![Pelican SVG 환경의 웹 플레이그라운드에서 step()으로 SVG를 제출한 화면. 자전거 위의 펠리컨 그림 옆에 reward 1.00, gate passed, structure 1.00, judge off가 표시됨](https://discuss.pytorch.kr/uploads/default/original/3X/0/0/00f66348af3ec7c3598599a154e42613d306c677.png)

Pelican SVG 환경의 웹 플레이그라운드에서 step()으로 SVG를 제출한 화면. 자전거 위의 펠리컨 그림 옆에 reward 1.00, gate passed, structure 1.00, judge off가 표시됨800×472 46 KB](https://discuss.pytorch.kr/uploads/default/original/3X/0/0/00f66348af3ec7c3598599a154e42613d306c677.png "Pelican SVG 환경의 웹 플레이그라운드에서 step()으로 SVG를 제출한 화면. 자전거 위의 펠리컨 그림 옆에 reward 1.00, gate passed, structure 1.00, judge off가 표시됨")

위 화면처럼 판정 모델을 끄면 구조 점수가 보상의 전부가 됩니다. 문서에 따르면 팀은 [TRL(Transformers Reinforcement Learning)](https://github.com/huggingface/trl)로 Qwen3-1.7B를 80스텝씩 네 번 **GRPO(Group Relative Policy Optimization)** 학습했습니다. 세 번은 판정 모델을 끄고, 한 번은 켰습니다. 그리고 체크포인트에서 판정 모델을 켠 채 새 샘플 24개를 다시 채점했습니다. 문서의 표에는 판정을 끈 실행 중 두 개의 결과가 실려 있습니다:

| 지표 | 학습 전 (5회 측정) | 판정 끄고 학습 | 판정 켜고 학습 |
| --- | --- | --- | --- |
| 구조 점수 | 0.374 ± 0.064 | 0.619, 0.643 | 0.321 |
| 판정 의미 점수 | 0.0049 ± 0.0042 | 0.0075, 0.0139 | 0.0023 |
| 게이트에서 거부된 제출 | 24개 중 3~13개 | 24개 중 1개, 2개 | 24개 중 11개 |

판정 모델을 끈 두 실행은 형식이 맞는 SVG와 자전거 같은 구조를 배웠지만 새는 배우지 못했습니다. 문서는 이를 모델이 목표를 속인 결과로 보지 않습니다. 판정 점수가 보상에 없었으므로 정책은 보상받은 것을 정확히 최적화했습니다. **결정적인 구조 검사만으로는 과제의 대리 지표로 부족하다**는 것이 문서의 결론입니다. 같은 높이에 놓인 같은 크기의 원 두 개, 그 사이의 막대, 축 위의 아무 덩어리만 있어도 구조 검사 7개를 모두 통과합니다.

판정 모델을 켠 실행은 학습 전 범위 안에서 끝났고, 의미 점수는 오히려 내려갔습니다. 판정 모델을 켜면 구조의 가중치가 1.0에서 0.35로 줄어듭니다. 그런데 1.7B 모델의 의미 점수는 거의 항상 0이었습니다.

학습 전 모델은 새 샘플 24개 중 2개에서만 0이 아닌 의미 점수를 받았습니다. 학습 전후 48개 그림 모두에서 판정 모델은 *"타고 있다"* 는 항목에 한 번도 예라고 답하지 않았습니다. GRPO는 한 그룹 안 응답들의 점수 차이로 그래디언트(Gradient)를 만드므로, 그룹 전체가 0인 항목은 가중치가 커도 학습에 기여하지 않습니다. 같은 판정 모델이 프론티어 모델 샘플 139개 중 138개에는 0이 아닌 점수를 주었습니다. 그래서 문서는 판정 기반 보상에 GPU 시간을 쓰기 전에, 학습할 기본 모델에서 그 보상이 얼마나 자주 0이 아닌지 먼저 측정하라고 권합니다.

### 수채화 학습 프로젝트: 인프라 실패를 0점으로 처리하지 않습니다

원문은 보상을 잘 골라도 보상을 계산하는 시스템의 실패가 그 보상을 망칠 수 있다고 이어 갑니다. OpenEnv 메인테이너 Sergio Paniego는 [수채화를 그리도록 코딩 모델을 학습시킨 프로젝트](https://huggingface.co/blog/train-to-paint-with-code#infra-is-hard)에서 렌더링 타임아웃과 응답하지 않는 채점기가 0점을 반환하는 것을 발견했습니다. 고장 난 인프라를 못 그린 그림처럼 처리한 것입니다. 그는 이 경로가 `None`을 반환하게 바꾸고, 해당 시도를 학습 그룹에서 제외했습니다. 그 뒤로는 시스템 장애가 모델 작업에 대한 잘못된 피드백이 되지 않았습니다.

프로젝트 글에 따르면 이런 인프라 실패는 전체 롤아웃의 약 1.5%였고, 가장 심한 실행에서는 5.2%였습니다. 같은 글은 OpenEnv 클라이언트의 버그도 보고합니다. 원격에서 닫힌 WebSocket이 캐시에 남아, 환경이 정상인데도 이후 호출이 모두 실패했습니다. 이 버그를 찾기까지 학습 두 번이 중간에 멈췄습니다. 수정은 [업스트림 PR #1103](https://github.com/openenv/OpenEnv/pull/1103)으로 제출되었고, 2026년 9월 9일 병합되었습니다.

Pelican SVG 환경도 같은 원칙을 따릅니다. 판정 모델이 설정됐는데 호출에 실패하면, 환경은 의미 점수를 0으로 두고 관찰의 `judged`를 false로 표시합니다. 그러면 하네스가 그 샘플을 버리거나 다시 시도할 수 있습니다. 실패 시 가중치를 재정규화하면 아무도 채점하지 못한 제출이 더 높은 점수를 받게 되고, 판정 모델을 고장 내는 것이 이기는 전략이 되기 때문입니다.

## 다른 개발자가 쓸 수 있게 환경을 패키징합니다

행동과 피드백이 의도대로 동작하면, 다음은 다른 사람이 그 환경을 쓸 수 있게 만드는 일입니다. OpenEnv의 빌더 워크플로우는 프로젝트 구조를 만들고 로컬 개발 서버를 지원합니다. 또 선언한 환경 계약을 검증하고, [작업을 배포용으로 패키징](https://huggingface.co/docs/openenv/getting_started/environment-builder)합니다. 배포 가이드는 Docker 설정과 [Hugging Face Spaces](https://huggingface.co/spaces) 게시를 다룹니다. 공식 문서(Your First Environment, Deploying an Environment)에 나오는 명령은 다음과 같습니다:

| 명령 | 하는 일 |
| --- | --- |
| `openenv init my_env` | 환경 패키지 골격 생성 (`openenv.yaml`, 모델, 클라이언트, `server/`) |
| `openenv import SOURCE --name my_env` | 기존 OpenReward(ORS)나 Prime Intellect Verifiers 환경을 OpenEnv 패키지로 감싸기 |
| `openenv build` | Docker 이미지 로컬 빌드 |
| `openenv validate --level static --skip-build` | `openenv.yaml`의 `validation:` 계약 검사 |
| `openenv push` | Hugging Face Space로 배포 (`--private`, `--registry ghcr.io/ORG` 등 지원) |

원문은 동작을 재현하려면 명확한 설치 안내와 고정된 의존성 버전도 필요하다고 씁니다. 그래서 [OpenEnv v0.9.0](https://github.com/openenv/OpenEnv/releases/tag/v0.9.0)의 Echo MCP 데모를 도구 탐색, 호출, 오류 처리 확인용으로, Wordle 튜토리얼을 TRL을 쓰는 더 완전한 학습 레시피로 함께 링크합니다. 그리고 독자가 예제가 어느 릴리스 기준인지, 실행하면 무엇이 나와야 하는지 알기를 바란다고 밝힙니다. main 브랜치 문서는 안정 릴리스와 다를 수 있기 때문입니다.

이 경고는 원문이 나온 날 바로 현실이 되었습니다. v0.10.0이 같은 날(2026년 10월 22일, UTC 기준) 나왔고, 문서 사이트는 이제 v0.10.0을 최신 안정판으로 안내합니다. OpenEnv는 매주 릴리스합니다. v0.7.0(10월 1일), v0.8.0(10월 8일), v0.9.0(10월 15일), v0.10.0(10월 22일) 순서이고, PyPI 패키지 [`openenv`](https://pypi.org/project/openenv/)도 0.10.0입니다. 지난 9월 소개 글을 쓸 때는 0.4.1이었습니다. 릴리스 노트에서 원문 예제와 관련된 변경은 다음과 같습니다:

* **v0.9.0**: `openenv push`가 Echo 같은 MCP 환경에서 `models.py`를 요구하지 않게 됐습니다(#1356). Wordle 튜토리얼용 예제 스크립트(`tutorial/examples/wordle.py`)에 `vllm serve`로 띄운 vLLM 서버를 쓰는 실행 방법이 들어갔습니다(#1082). 문서의 Wordle 튜토리얼 페이지는 여전히 colocate 모드를 씁니다. τ²-bench 고객 상담 환경 `tau2_env`가 추가됐고, `opencode_env`와 `pi_env`는 제거됐습니다.
* **v0.10.0**: 환경 검증에 공개 정책과 네트워크 차단 정책을 강제하고 측정하는 기능이 들어왔습니다(#1358). `dipg_safety_env`, `wildfire_env`, `kernrl`이 `reset(seed)`를 지키게 됐습니다(#1444). 동기 `forward()`가 반환한 비동기 자식 Rubric을 기다리지 않던 문제도 고쳐졌습니다(#1442). 참고로 v0.10.0 노트의 릴리스 PR 제목은 *"Release OpenEnv 0.9.1"* (#1454)입니다.

## 학습 시스템에 연결합니다: TRL과 Wordle

환경이 실행되면 학습 시스템이 그 피드백으로 모델을 갱신할 수 있습니다. [TRL의 OpenEnv 가이드](https://huggingface.co/docs/trl/main/en/openenv)는 여러 턴에 걸친 학습 방식을 설명합니다. 환경이 도구와 보상을 제공하고, 학습기가 모델 갱신을 맡습니다. Wordle 예제는 모델이 추측하고, 피드백을 받고, 다시 시도하는 동안 이 분업을 따릅니다. 원문은 그래도 모델, 학습 설정, 학습 결과를 확인할 평가 방법은 개발자가 골라야 한다고 덧붙입니다.

`GRPOTrainer`의 `environment_factory`로 Wordle 환경 클래스를 넘기는 코드는 [지난 소개 글의 TRL 절](https://discuss.pytorch.kr/t/openenv-feat-meta-hugging-face/11812)에 있습니다. 여기서는 그 글 이후 튜토리얼에서 확인한 학습 조건과 결과를 덧붙입니다. 튜토리얼은 `Qwen/Qwen3-1.7B`를 `chat_template_kwargs={"enable_thinking": False}`로 학습합니다. 사고(thinking) 모드를 꺼서 모델이 추론 토큰 없이 바로 도구를 호출하게 하는 설정입니다. 주요 설정값은 프롬프트 3,000개 데이터셋, 학습률 `1e-6`, `gradient_accumulation_steps=64`, `num_generations=2`, vLLM colocate 모드입니다. 튜토리얼은 호스팅된 [openenv/wordle Space](https://huggingface.co/spaces/openenv/wordle)의 동시 실행 수가 제한되어 있으므로, 실제 학습에서는 Space를 복제하거나 Docker로 로컬에서 실행하라고 권합니다.

결과에 대한 기대치도 TRL 가이드에 적혀 있습니다. 학습 후 같은 단어를 반복하는 추측은 줄고 맞힌 추측은 늘어납니다. 그래도 사고 모드를 끈 Qwen3-1.7B는 게임을 꾸준히 이기지 못합니다. 가이드는 더 나은 결과를 원하면 더 큰 모델을 쓰거나 사고 모드를 켜라고 안내합니다. 팀은 [gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)가 꾸준히 이겼지만 연산이 훨씬 많이 들었다고 적었습니다. 필자가 보기에, 원문이 모델과 평가 방법은 개발자가 골라야 한다고 한 이유를 이 결과가 보여 줍니다.

## AAIF에 합류하는 이유: 환경 인터페이스를 중립 재단에서 함께 관리하기

메인테이너들은 이 워크플로우를 재사용 가능하게 만들려면 과제, 학습 프레임워크, 에이전트를 만드는 사람들 사이의 조율이 필요하다고 씁니다. 환경 인터페이스가 바뀌면 그 인터페이스를 쓰는 시스템이 모두 영향을 받습니다. 그래서 이 기여자들에게는 호환성과 프로젝트 방향을 논의할 공동의 장소가 필요합니다.

OpenEnv에는 이미 [여러 회사가 참여하는 기술 위원회(Technical Committee)](https://github.com/openenv/OpenEnv/blob/main/GOVERNANCE.md)가 있습니다. [공개된 AAIF 합류 제안서](https://github.com/aaif/project-proposals/issues/50)는 이 협업을 바탕으로, 공동 환경 명세를 특정 기업에 속하지 않는 곳에 두고 MCP와 나란히 발전시키려 합니다. 원문은 AAIF 합류가 기존 작업에 재단이라는 집을 마련해 준다고 정리합니다.

> *"AAIF에 합류하면 이미 진행 중인 작업에 재단이라는 집이 생깁니다."*
>
> > *"Joining AAIF gives that existing work a foundation home."*

### 제안서와 발표문에서 확인한 합류 과정

원문에는 합류 절차와 날짜가 없어서, 제안서 이슈와 AAIF 발표문을 함께 읽었습니다:

| 날짜 (2026년) | 내용 |
| --- | --- |
| 9월 28일 | Ben Burtenshaw(Hugging Face)가 AAIF 저장소에 OpenEnv 프로젝트 제안서 이슈 #50을 올림. Growth 단계로 신청 |
| 10월 6일 | AAIF 기술 위원회가 OpenEnv를 Growth 단계 프로젝트로 승인. 이슈에는 계약서 작성 뒤 이사회(Governing Board)의 최종 검토와 표결이 남았다고 기록 |
| 10월 22일 | AAIF가 AGNTCon + MCPCon North America(산호세)에서 Agent Skills, Open Responses, OpenEnv, OpenSandbox 합류 발표. 같은 날 이 글과 v0.10.0 공개 |

제안서는 OpenEnv가 AAIF의 기존 프로젝트와 어떻게 이어지는지도 설명합니다. 제안서는 모델과 환경 사이의 인터페이스가 MCP이므로, 강화학습용으로 만든 환경이 배포 후 에이전트가 호출할 도구 인터페이스를 그대로 노출한다고 씁니다. 앞서 본 대로 지금 MCP 기반 환경은 일부이므로, 이것은 현재 상태라기보다 프로젝트가 지향하는 구조입니다. 제안서는 이를 에이전트를 학습시키는 방식과 실제로 실행하는 방식을 일치시키는 장점으로 듭니다.

OpenEnv는 MCP 위에 학습에 필요한 에피소드 수명 주기(`reset`, `step`), 보상과 Rubric, 격리, 패키징을 더합니다. AAIF의 또 다른 프로젝트인 [goose](https://discuss.pytorch.kr/t/goose-rust-mcp-ai-feat-block-linux-foundation/9777)는 OpenEnv가 지원하려는 에이전트 하네스 중 하나입니다. [RFC 005](https://github.com/openenv/OpenEnv/blob/main/rfcs/005-agentic-harnesses.md)는 하네스가 자기 실행 루프를 유지한 채 OpenEnv 환경에서 학습되고 평가받는 감싸기 방식을 정의합니다.

제안서에 적힌 운영 방식과 현황은 다음과 같습니다. 수치는 제안서 작성 시점(9월 28일)에 프로젝트가 스스로 밝힌 값입니다.

* **기술 위원회**: Meta-PyTorch, Reflection, NVIDIA, Microsoft, Prime Intellect, Mercor, Fleet AI, Modal, Unsloth, Hugging Face의 10개 조직이 한 명씩 대표를 두고 2주마다 회의합니다. GOVERNANCE.md도 같은 10곳을 적습니다. 지난 소개 글은 6월 발표를 따라 RadixArk까지 11곳으로 적었고, AAIF 발표문의 Ben Burtenshaw 인용에도 RadixArk가 나옵니다. Ben Burtenshaw(Hugging Face)가 기술 리드, Emre Guven(Reflection)이 사업(GTM) 리드입니다. 결정은 GitHub와 정기 회의에서 합의로 하고, 큰 기술 변경에는 승인된 RFC가 필요합니다.
* **후원자**: 제안서의 기술 위원회 후원자(Technical Committee Sponsor) 항목에는 Caitie McCaffrey(Microsoft)가 적혀 있습니다. 제안서는 승인되면 프로젝트의 상표와 계정을 모두 AAIF에 기증한다는 항목에 동의했습니다.
* **재정**: 직접적인 재정 후원은 없습니다. Hugging Face와 Meta가 엔지니어 시간을 대고, 기술 위원회 회원사가 엔지니어 시간과 연산 자원을 기여합니다.
* **채택 현황**: GitHub 스타 2,300개 이상, Hugging Face Hub의 환경 4,200개 이상, Discord 회원 21,000명 이상이라고 밝혔습니다. 이 글을 쓰는 10월 22일 기준 GitHub 스타는 2,744개입니다.
* **연동**: TRL, Unsloth, SkyRL(UC Berkeley), Axolotl, Lightning AI, vLLM, SGLang이 OpenEnv를 연동하거나 지원하고, Modal, Daytona, Azure Container Apps, Novita를 샌드박스 백엔드로 쓸 수 있습니다.

저장소 주소도 바뀌었습니다. GOVERNANCE.md에 따르면 OpenEnv 저장소는 2026년 6월 `huggingface/OpenEnv`로 옮겨졌습니다. 그 전 주소는 [지난 소개 글](https://discuss.pytorch.kr/t/openenv-feat-meta-hugging-face/11812)에 적은 대로 `meta-pytorch/OpenEnv`였습니다. `openenv/OpenEnv` 조직으로 옮긴 날짜는 확인한 자료에 나오지 않습니다. 지금은 `github.com/openenv/OpenEnv`가 정식 주소이고, `huggingface/OpenEnv`와 `meta-pytorch/OpenEnv` 주소는 모두 새 주소로 리다이렉트됩니다. 원문과 v0.9.0 릴리스 노트의 링크는 아직 `huggingface/OpenEnv`를 가리키지만, 리다이렉트 덕분에 그대로 열립니다.

AAIF가 같은 날 발표한 다른 세 프로젝트와 AAIF 전체 구성은 [AAIF 4개 신규 프로젝트 정리 글](https://discuss.pytorch.kr/t/aaif-agent-skills-open-responses-openenv-opensandbox-10/12275)에 있습니다. 발표문에서 Ben Burtenshaw는 강화학습 환경이 에이전트가 실제 세계에서 쓸 능력을 가르치므로 완전히 개방된 AI 스택의 기본 요소라고 말했습니다.

## 다음 단계: 환경을 쉽게 게시하는 단계에서 학습에 쓸모 있는지 검증하는 단계로

원문은 [로드맵](https://github.com/aaif/project-proposals/issues/50)이 같은 작업을 환경 게시에서 환경이 학습에 쓸모 있는지 확인하는 쪽으로 넓힌다고 씁니다. 제안된 우선순위는 에이전트 하네스와 학습 시스템 연결, 환경 검증, 학습 레시피 제공, 학습 중 과제 샘플링, 커리큘럼, 평가 지원입니다. 메인테이너들은 RFC마다 검토와 구현 단계가 다르므로, 이 우선순위는 다가올 한 릴리스가 아니라 작업의 방향이라고 밝힙니다.

제안서의 12개월 로드맵 표는 다음과 같습니다. 상태는 제안서 작성 시점(9월 28일) 기준입니다:

| RFC | 주제 | 분야 | 상태 |
| --- | --- | --- | --- |
| 005 | 에이전트 하네스 연동 | 하네스 | In review |
| 006 | 블랙박스 하네스의 토큰 캡처 계약 (캡처 프록시는 #1036으로 병합) | 하네스 | In review |
| 008 | 환경 자동 검증(`openenv validate`)과 학습 가능성 기준 | 보상과 검증 | In review |
| 009 | `openenvd`: 에이전트, 채점기, 원격 측정 영역을 나눈 권한 사이드카 | 보상과 검증 | Draft |
| 011 | 프레임워크별 GRPO 하네스 학습 레시피 | 학습 | Draft |
| 012 | Harbor 캡처 목적, 제공자 충실도, 라이브 세션 소유권 | 하네스 | In review |
| 013 | 과제 샘플링, 커리큘럼, 학습 중 평가 | 학습 | In review |

지난 소개 글은 9월 3일 기준으로 RFC 000~006, 008, 010의 상태를 정리했습니다. 이 표에서 그 글에 없던 번호는 009, 011, 012, 013입니다. 006은 번호가 같아도 주제가 바뀌었습니다. 지난 글의 006은 외부 환경 가져오기와 데이터셋 기반 환경 두 제안이었고, 지금 006은 블랙박스 하네스의 토큰 캡처 계약입니다. GOVERNANCE.md가 환경 데이터셋으로 적은 007은 제안서 로드맵에 없습니다.

10월 22일 기준 저장소 main을 보면 번호가 제안서와 일부 다릅니다. main의 `rfcs/011-ard-catalog-discovery.md`는 [ARD(Agentic Resource Discovery)](https://github.com/ards-project/ard-spec) 명세로 환경 카탈로그를 탐색하는 방법을 다루는 Draft 문서입니다. 제안서가 011로 적은 GRPO 레시피 RFC는 [PR #924](https://github.com/openenv/OpenEnv/pull/924)에 `011-recipes.md`로 열려 있습니다. RFC 013은 [PR #1256](https://github.com/openenv/OpenEnv/pull/1256)으로 열려 있고, RFC 009의 `openenvd` 구현은 PR #1354, #1355로 열려 있습니다. main에 문서가 있는 RFC 005, 006, 008, 012의 상태는 모두 In Review입니다. v0.10.0에는 환경 검증에 공개 정책과 네트워크 차단 정책을 강제하는 기능(#1358)이 들어갔지만, RFC 008 문서의 상태는 여전히 In Review입니다.

## OpenEnv 시작하기

원문은 [시작 가이드](https://huggingface.co/docs/openenv/getting-started)로 시작해 동작을 직접 확인할 수 있는 환경 하나를 실행해 보라고 권합니다. 큰 변경을 제안하기 전에는 [기여 절차](https://huggingface.co/docs/openenv/contributing)를 먼저 읽으라고 합니다. 시작 가이드의 첫 단계는 다음과 같습니다. 이 코드는 `AutoEnv`가 Echo 환경 패키지를 설치하기 전에 확인을 요청한 뒤, 이미 실행 중인 Hugging Face Space에 연결합니다:

```
pip install openenv
```

```
from openenv import AutoEnv

env = AutoEnv.from_env(
    "openenv/echo_env",
    base_url="https://openenv-echo-env.hf.space",
)

with env.sync() as client:
    result = client.reset()
    print(result.observation.metadata["message"])  # "Echo environment ready!"
    message = client.call_tool("echo_message", message="Hello, OpenEnv!")
    print(message)  # "Hello, OpenEnv!"
```

`base_url` 없이 `AutoEnv.from_env("echo")`처럼 부르면 로컬 Docker 컨테이너를 띄우므로 Docker와 환경 이미지가 필요합니다. 위 시작 가이드 예제는 v0.9.0, v0.10.0, main 문서에서 같습니다. 원문이 v0.9.0 태그로 링크한 Echo 데모와 FinQA 코드를 원문과 같은 결과로 확인하려면, 저장소를 v0.9.0 태그로 받아 실행합니다. 그 밖의 문서는 문서 사이트에서 v0.10.0 버전을 골라 읽을 수 있습니다.

## OpenEnv의 라이선스

OpenEnv는 [BSD 3-Clause License](https://github.com/openenv/OpenEnv/blob/main/LICENSE)로 배포됩니다. 저작권 표시와 면책 조항을 유지하면 연구 목적은 물론 상업적 용도로도 자유롭게 사용 및 수정이 가능합니다. 다만 저작권자나 기여자의 이름을 파생 제품의 홍보에 허락 없이 쓸 수 없습니다. 각 환경이 쓰는 데이터셋과 외부 모델(예: Pelican SVG의 판정 모델)에는 별도 라이선스가 적용될 수 있습니다.

## ![:scroll:](https://discuss.pytorch.kr/images/emoji/fluentui/scroll.png?v=15 ":scroll:") Training agents for real-world tasks with OpenEnv 원문 블로그

![](https://discuss.pytorch.kr/uploads/default/original/3X/3/0/30cb306603178a12c559fc08ba03d2d6e93fa6b7.png)
[Agentic AI Foundation (AAIF)](https://aaif.io/blog/training-agents-for-real-world-tasks-with-openenv)

![](https://discuss.pytorch.kr/uploads/default/original/3X/1/c/1c02d740b38f97472e23d0b9a37fd5cc13b515b2.jpeg)

### [Training Agents for Real-World Tasks with OpenEnv - Agentic AI Foundation (AAIF)](https://aaif.io/blog/training-agents-for-real-world-tasks-with-openenv)

Learn how OpenEnv provides a common interface for defining tasks, rewards, and environments to train AI agents on real-world challenges like calendar scheduling and more.

## ![:scroll:](https://discuss.pytorch.kr/images/emoji/fluentui/scroll.png?v=15 ":scroll:") Agentic AI Foundation 4개 신규 프로젝트 발표문

![](https://discuss.pytorch.kr/uploads/default/original/3X/3/0/30cb306603178a12c559fc08ba03d2d6e93fa6b7.png)
[Agentic AI Foundation (AAIF)](https://aaif.io/news/agentic-ai-foundation-announces-four-new-projects)

![](https://discuss.pytorch.kr/uploads/default/optimized/3X/4/6/46ca4e178ed7b0c89a36f856efb39f4e821d04cb_2_1028x539.png)

### [Agentic AI Foundation Announces Four New Projects: Agent Skills, Open...](https://aaif.io/news/agentic-ai-foundation-announces-four-new-projects)

AAIF reaches 10 projects in its first year, with new contributions from Alibaba, Anthropic, Hugging Face, and OpenAI

## ![:github:](https://discuss.pytorch.kr/uploads/default/original/2X/7/70a6220c603eed42089b4f67366225849e119e20.svg?v=15 ":github:") OpenEnv GitHub 저장소

[github.com](https://github.com/openenv/OpenEnv)

![](https://discuss.pytorch.kr/uploads/default/optimized/3X/b/2/b2cf1cbb5ec9d3b7b7f5008b20dad73e0a4b2538_2_695x347.png)

### [GitHub - openenv/OpenEnv: An interface library for RL post training with...](https://github.com/openenv/OpenEnv)

An interface library for RL post training with environments.
