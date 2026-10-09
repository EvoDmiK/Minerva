---
project: RobinGraph
type: dataset-design
tags:
  - robingraph
  - strands-decider
  - intent-classification
---

# Strands Decider — 한국어 의도 분류 데이터셋 설계

## 범위

의도 분류만 학습한다. 정답은 요청 기능이며 종 ID·DB 존재 여부·답변 내용·서버 장애는 다른 문제다. 예를 들어 종 이름이 없거나 DB에 아종 자료가 없어도 '아종 알려줘'의 의도는 subspecies_list다. 사용자 요청은 데이터셋 구성 방법 설명이며, 실제 학습 corpus·제품 코드·자동화 테스트는 만들거나 수정하지 않았다.

## 공식 저장 형식

고정 코드 `63d24ae286e50105fba0bd1db15b0e243aea4650`의 `data/format.py`에서 Example은 kind, state, instructions, options, label과 선택적 task, weight, instruction_variants를 읽는다. options는 [이름, 설명] 쌍의 목록, label은 저장된 선택지 순서의 0-based 인덱스다. API의 questions/criteria 객체 또는 생성 LLM의 messages 형식과 혼동하지 않는다. JSONL은 샘플당 실제 한 줄이다.

아래는 아종·일반 소개·계통을 구분하는 **합성 축약 예시**다. 실제 corpus나 모델 예측 결과가 아니다. 실전에서는 합의한 라벨 집합과 동일한 정책을 사용한다.

```json
{
  "kind": "choice",
  "state": "청둥오리 아종 알려줘",
  "instructions": "사용자 질문이 요청하는 조회 기능을 하나 고르세요. 독립적인 기능을 여러 개 요청하면 multi_request, 어떤 선택지에도 해당하지 않으면 other를 고르세요.",
  "options": [
    ["species_profile", "특정 조류의 전반적인 소개나 특징 요약"],
    ["subspecies_list", "특정 종에 속하는 아종 목록 조회"],
    ["taxonomy_lineage", "과·속·종 등 분류 계통이나 소속 조회"],
    ["multi_request", "서로 다른 조회 기능을 동시에 요청"],
    ["other", "어떤 선택지에도 해당하지 않는 요청"]
  ],
  "label": 1,
  "task": "robingraph_intent_v1",
  "weight": 1.0,
  "instruction_variants": ["질문에 맞는 조회 기능을 선택하세요. 독립적인 여러 기능은 multi_request, 해당 항목이 없으면 other입니다."]
}
```

### 예시 형식 확인 범위

공식 Example 클래스만 AST로 분리해 표준 라이브러리로 위 합성 예시의 from_dict와 JSON round-trip을 실행해 PASS를 확인했다. 초기 진단 환경에서 json/asdict import가 빠져 실패한 뒤 해당 표준 라이브러리 바인딩을 보완해 재실행했다. tokenizer·collator·모델·학습을 실행한 테스트가 아니며 전체 suite 통과를 뜻하지 않는다.

## 라벨 정의 제안

- species_profile: 전반적인 소개.
- subspecies_list: 특정 종의 아종 목록.
- diet/habitat/activity/appearance: 각각 먹이·일반 서식 환경·활동·외관.
- related_species: 관련 종·유사 종 요청. 세부 의미 차이는 필요시 별도 라벨로 분리한다.
- taxonomy_lineage: 과·속·종의 소속·분류 계통.
- observations: 특정 시점·지역의 관찰 기록.
- evidence_search: 논문·문헌 자체를 찾는 요청.
- multi_request: 독립 기능을 여러 개 동시에 요청.
- other: 확정한 선택지 어디에도 해당하지 않는 요청. 질문의 요청 자체가 모호한 경우는 별도 규칙/라벨로 합의하며, 모델이 자신 없다는 이유로 gold=other를 붙이지 않는다.

이는 현재 제품의 구현 계약이 아닌 제안이다. '아종이란 무엇인가'는 아종 목록 요청이 아니다. '어디 사는가'는 일반 habitat, '지난달 서울에서 관찰됐는가'는 observations. '먹이와 근거를 설명'은 주 기능 diet+근거 요구 정책, '먹이와 아종을 알려줘'는 multi_request로 보는 등 보조 요구와 독립 요구를 구분한다.

## 수집과 검수

먼저 CSV/시트로 sample_id, raw_question, gold_intent, group_id, source(real/manual/synthetic), 검수 상태, label/schema version을 관리한다. 보안·동의를 확인한 실제 질문을 우선하고, 사람이 만든 경계 사례와 LLM 패러프레이즈를 보완한다. 모델 생성 라벨은 후보일 뿐이며 사람 검수를 통과해야 gold가 된다. 최종 테스트는 실제 사용자 스타일과 사람이 작성한 새 질문 중심으로 구성한다.

라벨별로 여러 종 이름·학명·통칭·오타·짧은 표현·존대·구어·부정·다중 대상·복합·범위 밖을 넣는다. 같은 종의 최소 대조 질문을 만든다: '청둥오리 아종 목록' vs '청둥오리 분류 계통' vs '청둥오리는 무엇을 먹나'. 이런 의미 변형/패러프레이즈 가족은 같은 group에 보관하고 분할 간 누출을 막는다. 패러프레이즈를 대량 생성한 뒤 무작위 행 분할하지 않는다. 일부 종 이름·문장 틀을 아예 최종 평가에서만 사용한다.

## 권장 규모·분할 — 제안이지 공식 필수 조건 아님

초기에는 자주 쓰는 라벨당 30–50개 고품질 원본으로 정의·baseline을 확인하고, 오류를 보고 100–200개 수준으로 확장한다. 표현 바꾸기만 한 문항 수는 독립 원본 수가 아니다. 설명용 2,000행 규모의 분할 제안은 train 70%=1,400 / validation 10%=200 / calibration 10%=200 / final test 10%=200이며 Python으로 계산했다. 실전은 group 단위 분할이라 정확한 행 비율보다 누출 방지·라벨 커버리지·유효 표본 수를 우선한다.

validation은 모델·설정 선택, calibration은 temperature/확신 임계값 조정, 최종 test는 고정 후 한 번 판단하는 용도다. test를 보고 라벨·모델을 조정하면 그 세트는 개발용으로 바뀌므로 새 독립 평가가 필요하다. 공식 calibrate/eval에는 calib/test 분할이 있으므로 수동 파일 분할과 도구의 split 옵션을 맞추고 같은 행으로 보정·평가하지 않는다. task 필드만으로 paraphrase group이 보호된다고 가정하지 않는다.

## Strands 특이사항

- 학습용 option 순서 변경은 collator가 gold index도 함께 remap한다. 데이터 파일의 순서를 수동 변경할 때는 label도 다시 계산한다.
- instruction_variants는 같은 정책을 다른 말로 표현한 것만 넣는다. 서로 다른 분류 정책을 섞지 않는다.
- state·선택지 설명은 추론 때 실제로 제공할 형식과 맞추고 정답·DB 결과를 입력에 누출하지 않는다.
- 공식 teacher/replay targets는 corpus 행 순서에 결합돼 있다. 임의 RobinGraph 데이터에 기존 teacher_file을 붙이지 않는다.
- 초기 도메인 학습에는 choice 예시와 사람 검수한 hard labels로 데이터 준비부터 시작할 수 있다. 전체 공개 recipe와 장문 teacher distillation을 재현해야 한다는 의미는 아니다. Mac 학습 지원 제약은 별개로 남는다.

## 출처

- [공식 Example/JSONL reader](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/src/strands_decider/data/format.py)
- [선택지 permutation과 label remap](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/src/strands_decider/data/collate.py)
- [학습·보정·평가 절차](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/training/steps.md)
- [데이터 및 teacher 파일 정합성](https://github.com/strands-labs/strands-decider/blob/63d24ae286e50105fba0bd1db15b0e243aea4650/data/README.md)

관련: [[Work/RobinGraph/검토자료/Strands-Decider-2B-의도분류와-Mac-학습-검토]] · [[RobinGraph 작업 백로그]]
