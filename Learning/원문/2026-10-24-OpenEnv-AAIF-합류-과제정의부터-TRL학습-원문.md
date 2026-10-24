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
