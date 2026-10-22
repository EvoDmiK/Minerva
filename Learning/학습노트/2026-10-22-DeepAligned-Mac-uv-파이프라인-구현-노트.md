---
date: 2026-10-22
created: 2026-10-22
updated: 2026-10-22
document_role: learning-note
note_kind: implementation-guide
language: ko
tags: [learning, implementation, deepaligned, mac, uv, pytorch, nlp, banking77, gcd, interview, mlflow, cross-validation]
paper_title: "Discovering New Intents with Deep Aligned Clustering"
paper_date: 2020-12-16
paper_id: "arXiv:2012.08987v7"
source_url: "https://arxiv.org/abs/2012.08987"
primary_text: "https://arxiv.org/html/2012.08987v7"
source_role: primary
code_repo: "gcd-baseline (로컬: ~/Desktop/Homework/gcd-baseline)"
capture_scope: "에이전트 비교용 DeepAligned 베이스라인·Mac M4 uv 구현·Known/Novel 클래스별 층화 분할·dev known-only 검증·조기 종료·Stratified k-Fold 교차검증·MLflow parent-child 트래킹·학습 없는 k-Means 하한선·t-SNE·시스템 점검"
paper_notes:
  - "[[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트]]"
source_notes:
  - "[[Learning/원문/2026-10-21-DeepAligned-원문]]"
---
# DeepAligned 파이프라인 구현 및 Mac uv 실행 가이드 (인터뷰 과제 대비)

> [!abstract] 개요
> 회사 인터뷰 사전 과제에서 **에이전트와 비교할 베이스라인**으로 **DeepAligned (AAAI 2021)** 를 Apple Silicon Mac(M4)에서 `uv` 기반으로 구현·재현한 엔지니어링 가이드입니다.
> 공식 레포의 레거시 종속성(`pytorch-pretrained-bert`)을 모던 `transformers`/`torch`로 리팩터링하고, **① Known/Novel 분할과 타깃 누수 방지**, **② dev 기반 Known-only 검증**, **③ All / Known / Novel 분리 평가**, **④ Stratified k-Fold 교차검증**, **⑤ MLflow 실험 트래킹**을 갖췄습니다.

> [!info] 코드 기준
> 이 노트의 코드는 실제 레포 `gcd-baseline`과 동일합니다 (2026-10-22 기준, 테스트 10개 통과).
> 버그와 변경 이력은 [[#7. 구현 중 발견한 버그와 수정 이력]]에 정리했습니다.

---

## 0. 비교 실험 설계 (에이전트 vs 베이스라인)

| 방법 | 학습 | 역할 |
|---|---|---|
| BERT + k-Means (`--method kmeans`) | 없음 | 하한선 (lower bound) |
| DeepAligned (`--method deepaligned`) | Stage 1 + Stage 2 | 기존 GCD 방법 (베이스라인) |
| 에이전트 | (본인 방법) | 비교 대상 |

**공정 비교 조건**: 세 방법 모두 **같은 known/novel 분할, 같은 test 셋(3,080개), 같은 지표**로 평가합니다.
- 분할 정보는 `known_novel_split.json`(seed, known/novel 클래스 이름)으로 저장되며, 에이전트도 이 파일을 읽어 같은 분할을 사용합니다.
- 지표는 `compute_gcd_metrics`(헝가리안 매칭 후 All / Known / Novel ACC, NMI, ARI)를 공통으로 사용합니다.

**왜 학습 없는 k-Means를 넣었나**: 결과표에 "학습 없음 vs DeepAligned"를 나란히 두면 학습이 실제로 얼마나 기여하는지 보여 줄 수 있습니다. 학습을 빼면 DeepAligned라고 부를 수 없으므로 베이스라인 자체는 학습을 포함합니다.

---

## 1. 개발 환경 구성 (Mac Apple Silicon & uv)

### 1.1 공식 레포 종속성 문제와 해결책
* **공식 레포(`thuiar/DeepAligned-Clustering`)의 한계:**
  - 2020~2021년에 작성되어 Python 3.6, PyTorch 1.7.0, 구형 `pytorch-pretrained-bert` 패키지에 고정되어 있습니다.
  - Mac arm64 환경에서는 컴파일 휠이 없어 `pip install -r requirements.txt` 실행 시 빌드 에러가 발생하며, AWS S3 버킷 만료로 BERT 가중치 자동 다운로드가 실패합니다.
* **해결책:**
  - Python 3.11 기반 `uv` 프로젝트 구성
  - 모던 `transformers (>=5.20)` 및 최신 `torch (>=2.14)`로 리팩터링
  - Apple Silicon GPU 가속(`mps`) 디바이스 자동 감지 적용

### 1.2 uv 프로젝트 구성
```bash
# 1) 프로젝트 생성 (Python 3.11)
uv init gcd-baseline --python 3.11 && cd gcd-baseline

# 2) 의존성 추가 (pyproject.toml / uv.lock에 기록됨)
uv add torch torchvision transformers datasets evaluate
uv add numpy pandas scikit-learn scipy tqdm rich matplotlib mlflow python-dotenv
uv add --dev pytest
```

`pyproject.toml`에 아래 설정을 추가합니다.
```toml
## 설치용 패키지가 아닌 실행용 프로젝트이므로 uv가 프로젝트 자체를 빌드하지 않도록 함
## (기본 uv_build 설정은 src/gcd_baseline/__init__.py를 요구하여 uv add / uv run이 실패함)
[tool.uv]
package = false

## uv run pytest 실행 시 루트의 src 패키지를 import할 수 있도록 함
[tool.pytest.ini_options]
pythonpath = ["."]
```

### 1.3 환경변수 (`.env`, git 제외)
`baseline.py`가 시작할 때 `load_dotenv()`로 읽습니다. 셸에 이미 설정된 값이 있으면 셸 값을 우선합니다.
```bash
## MLflow 트래킹 서버 (baseline.py 실행 시 자동 로드)
MLFLOW_TRACKING_URI=https://mlflow.dove-nest.com

## MLflow 설치본이 출력하는 에이전트 안내 메시지 끄기
MLFLOW_DISABLE_AGENT_HINT=1
```
- 서버 주소를 코드 기본값으로 넣지 않은 이유: 과제 제출 시 평가자는 이 서버에 접속할 수 없으므로, 코드 기본값은 로컬 `./mlflow.db`(SQLite)로 둡니다.
- `.gitignore`에 `.env`, `outputs/`, `mlflow.db`, `.venv/` 등을 포함합니다.

### 1.4 디바이스 자동 설정 (`src/config.py`)
```python
import torch


def get_device() -> torch.device:

    ## 학습에 사용할 디바이스 선택 (MPS -> CUDA -> CPU 순)
    if torch.backends.mps.is_available():
        return torch.device('mps')

    elif torch.cuda.is_available():
        return torch.device('cuda')

    else:
        return torch.device('cpu')
```

> [!warning] MPS에서는 eager attention 필요
> transformers 기본 어텐션(SDPA)은 MPS에서 **학습 중 dropout을 지원하지 않아** `NotImplementedError: scaled_dot_product_attention for MPS does not support dropout`이 발생합니다.
> MPS일 때 `BertModel.from_pretrained(..., attn_implementation='eager')`로 로드합니다. (가짜 tokenizer를 쓰는 단위 테스트로는 잡히지 않고, 실제 bert-base 실행에서 발견)

### 1.5 시스템 점검 결과 (Apple M4)
| 항목 | 값 |
|---|---|
| 칩 | Apple M4 (CPU 10코어: 성능 4 + 효율 6, GPU 10코어) |
| 메모리 | 16GB 통합 메모리 |
| 디스크 여유 | 115GB (bert-base 캐시 421MB) |
| 소프트웨어 | macOS 26.5.1, torch 2.14.1, MPS 사용 가능 |

**실측 속도** (bert-base, batch 64, max_length 64, MPS)

| 작업 | 속도 | GPU 메모리 |
|---|---|---|
| feature 추출 (추론) | 281 ms/batch | — |
| 학습: 마지막 층만 (현재 설정) | 357 ms/step | 약 1.0GB |
| 학습: 전체 파인튜닝 | 959 ms/step | 약 5.0GB |
| k-Means (8,554 × 768, K=77, n_init=10) | 3.2초 | — |

- **추정 시간**: Stage 1 에포크당 약 5초, Stage 2 에포크당 약 1.5분 → 단일 실행 약 25분, 5-fold 교차검증 약 2시간
- **실행 중 메모리**: 학습 프로세스 전체 점유 약 2.9GB (GPU 약 2.1GB), 메모리 압력 Normal
- 전체 파인튜닝은 2.7배 느리고 메모리 여유가 적어, 마지막 층만 학습하는 현재 설정을 유지합니다.
- 장시간 실행 시 잠자기 방지: `caffeinate -i uv run python baseline.py ...`

---

## 2. 데이터 분할 및 타깃 누수 방지 프로토콜

### 2.1 Known / Novel 클래스 선정 기준
- **학계 표준 무작위 분할 (Uniform Random Split):** 고정 시드로 클래스 목록을 셔플한 뒤 50%를 Known으로 사용 (38 Known / 39 Novel).
- Known 후보는 **train에 실제로 존재하는 클래스에서만** 뽑습니다. test·dev에만 있는 클래스는 항상 Novel입니다.
- **실무 분석용 대안 (Ablation):** 도메인 계층(Prefix) 분할, 출현 빈도(Frequency) 분할.

### 2.2 데이터셋 분할 규칙 (코드 키 이름 기준)
1. **`train_known` (Train Labeled, $\mathcal{D}_l$):** Known 클래스마다 샘플의 `labeled_ratio`(10%)를 뽑아 지도 사전학습에 사용합니다.
2. **`valid` (Validation, $\mathcal{D}_{val}$):**
   - **dev.tsv가 있으면 dev 중 Known 클래스 샘플만** 사용합니다 (498개). 이 경우 labeled 샘플은 전부 `train_known`으로 갑니다.
   - dev.tsv가 없으면 labeled 샘플의 20%를 떼어 valid로 씁니다.
   - **절대 Novel 클래스 데이터가 포함되어서는 안 됩니다.** dev에는 77개 클래스가 모두 있으므로 그대로 쓰면 누수입니다.
3. **`train_novel` (Train Unlabeled, $\mathcal{D}_u$):** 라벨 미공개 Known 샘플 + Novel 클래스 샘플 100%. 이름과 달리 Known 클래스의 비라벨 샘플도 섞여 있습니다.
4. **`test`:** 공식 Test 세트 전체(3,080개)를 사용하며, Known/Novel 마스크로 분리 평가합니다.

**Banking77 실제 분할 (seed 42, known_ratio 0.5, labeled_ratio 0.1, dev 사용)**

| 분할 | 샘플 수 |
|---|---|
| 클래스 | 77 (Known 38 / Novel 39) |
| train_known | 449 (교차검증 fold당 450) |
| valid (dev 중 Known) | 498 |
| train_novel | 8,554 |
| test | 3,080 |

> [!tip] 왜 클래스별 층화 분할인가
> 샘플마다 난수 하나로 labeled / valid / unlabeled를 정하면, 데이터가 작을 때 valid가 통째로 비거나 특정 Known 클래스의 labeled 샘플이 0개가 됩니다.
> 클래스당 2개짜리 테스트 데이터에서 **200개 시드 중 141개가 빈 valid**를 만들었습니다. 클래스마다 개수를 정해 뽑으면 이 문제가 사라집니다.

### 2.3 Stratified k-Fold 교차검증
- **측정 대상**: "어떤 샘플이 labeled로 뽑혔는가"에 따른 성능 편차.
- **방법**: Known 샘플을 `1/labeled_ratio` = **10개 층화 fold**로 나누고, 그중 `--n_folds`개(5개)를 차례로 labeled 셋으로 사용합니다.
  - 그냥 5-fold로 나누면 fold 하나가 20%라 labeled 비율이 원래 설정의 두 배가 되므로, 10개로 나누고 5개를 씁니다.
  - fold마다 labeled 비율 10% 유지, 다섯 labeled 셋은 서로 겹치지 않음, 모든 fold에 Known 38개 클래스 전부 포함 (fold당 450개).
- **고정 조건**: Known/Novel 클래스 분할, dev(valid), test, 시드.
- **k-Means 하한선은 교차검증 제외**: labeled 셋을 쓰지 않아 fold마다 결과가 같습니다.

### 2.4 데이터 로더 및 분할 함수 (`src/preprocessing.py`)
```python
import json
import csv
import os

from sklearn.model_selection import StratifiedKFold
from torch.utils.data import TensorDataset
import pandas as pd
import numpy as np
import torch


def load_tsv_file(file_path: str) -> pd.DataFrame:

    ## tsv 파일을 읽어 text와 label 컬럼을 정규화하여 반환
    
    ## QUOTE_NONE: 텍스트 안의 따옴표를 인용 부호로 해석하지 않도록 함
    ## header=0  : 첫 줄(text, label 헤더)을 데이터로 읽지 않도록 건너뜀
    df = pd.read_csv(file_path, sep='\t', header=0, names=['text', 'label'],
                     quoting=csv.QUOTE_NONE, dtype=str)
    df['text']  = df['text'].str.strip()
    df['label'] = df['label'].str.strip()

    ## label이 없는 행 제거
    df = df.dropna(subset=['label'])
    df = df[df['label'] != ''].reset_index(drop=True)
    return df


def prepare_gcd_dataset_from_tsv(
        tokenizer,
        train_file_path: str = None,
        test_file_path: str  = None,
        dev_file_path: str   = None,
        fold: int            = None,
        known_ratio: float   = 0.5,
        labeled_ratio: float = 0.1,
        max_length: int = 64,
        seed:int = 42,
        output_dir: str = 'outputs'
    ):

    ## GCD(Generalized Category Discovery)용 데이터셋 구성
    ##  - known_ratio   : train 클래스 중 known으로 사용할 클래스 비율
    ##  - labeled_ratio : known 클래스마다 라벨을 공개할 샘플 비율 (클래스별 층화)
    ##  - valid         : dev 파일이 있으면 dev 중 known 클래스 샘플만 사용 (novel 누수 방지)
    ##                    dev 파일이 없으면 labeled 샘플의 20%를 떼어 사용 (나머지 80%는 train_known)
    ##  - fold          : 교차검증용 labeled fold 번호 (None이면 labeled_ratio만큼 무작위 층화 추출)
    ##  - 나머지 샘플(novel 클래스 + 라벨 미공개 known 샘플)은 train_novel

    ## 데이터 로드 (test 파일이 없으면 None)
    train_df = load_tsv_file(train_file_path)
    test_df  = load_tsv_file(test_file_path) \
                if test_file_path and os.path.exists(test_file_path) else None
    dev_df   = load_tsv_file(dev_file_path) \
                if dev_file_path and os.path.exists(dev_file_path) else None

    ## train/test/dev label의 합집합 (정렬)
    label_series = [df['label'] for df in [train_df, test_df, dev_df] if df is not None]
    all_labels   = sorted(pd.concat(label_series).dropna().unique().tolist())

    ## label <-> index 매핑
    label2idx = {lb : idx for idx, lb in enumerate(all_labels)}
    idx2label = {idx: lb for lb, idx in label2idx.items()}

    ## 추론 시 재사용할 수 있도록 매핑을 json으로 저장
    os.makedirs(output_dir, exist_ok = True)
    file_path = os.path.join(output_dir, 'label2idx.json')

    with open(file_path, 'w', encoding = 'utf-8') as f:

        json.dump(label2idx, f, ensure_ascii = False, indent = 2)

    ## 문자열 label을 정수 index로 변환
    train_df['label_idx'] = train_df['label'].map(label2idx)
    if test_df is not None:
        test_df['label_idx'] = test_df['label'].map(label2idx)
    if dev_df is not None:
        dev_df['label_idx'] = dev_df['label'].map(label2idx)


    num_classes = len(all_labels)
    rng = np.random.default_rng(seed)

    ## known 클래스는 train에 존재하는 클래스 중에서만 선택
    ## (test에만 있는 클래스는 항상 novel)
    train_classes    = sorted(train_df['label_idx'].unique().tolist())
    num_known        = int(len(train_classes) * known_ratio)
    shuffled_classes = rng.permutation(train_classes)

    known_classes = set(shuffled_classes[ :num_known].tolist())
    novel_classes = set(label2idx.values()) - known_classes

    ## 다른 방법(예: 에이전트)도 같은 known / novel 분할로 평가할 수 있도록 저장
    split_path = os.path.join(output_dir, 'known_novel_split.json')
    with open(split_path, 'w', encoding = 'utf-8') as f:

        json.dump({
            'seed'          : seed,
            'known_ratio'   : known_ratio,
            'known_classes' : sorted(idx2label[idx] for idx in known_classes),
            'novel_classes' : sorted(idx2label[idx] for idx in novel_classes)
        }, f, ensure_ascii = False, indent = 2)

    ## known 클래스별 층화 분할: train_known / valid / train_novel
    ##  - 샘플 단위 난수 분할은 데이터가 적으면 valid가 비거나
    ##    특정 known 클래스의 라벨 샘플이 0개가 될 수 있어 클래스마다 개수를 정해서 뽑음
    ##  - dev가 없을 때 클래스당 labeled 최소 2개 -> train_known 1개 + valid 1개 보장
    label_idxs = train_df['label_idx'].to_numpy()

    ## fold 지정 시 (교차검증): known 샘플을 1/labeled_ratio개의 층화 fold로 나누고
    ## fold번째 fold를 labeled 샘플로 사용 -> fold마다 labeled 비율은 유지되고 labeled 셋은 서로 겹치지 않음
    if fold is not None:
        num_splits = round(1 / labeled_ratio)
        assert 0 <= fold < num_splits, f'fold는 0 ~ {num_splits - 1} 범위여야 합니다 (labeled_ratio {labeled_ratio})'

        known_idx   = np.flatnonzero(np.isin(label_idxs, list(known_classes)))
        skf         = StratifiedKFold(n_splits = num_splits, shuffle = True, random_state = seed)
        _, fold_pos = list(skf.split(known_idx, label_idxs[known_idx]))[fold]
        fold_idx    = known_idx[fold_pos]

    train_known_idx, valid_idx = [], []
    for label_idx in sorted(known_classes):

        ## 이 클래스의 labeled 후보 (fold 지정 시 해당 fold 샘플 전부, 아니면 전체 샘플 중 labeled_ratio만큼)
        if fold is not None:
            class_idx = rng.permutation(fold_idx[label_idxs[fold_idx] == label_idx])
            num_label = len(class_idx)

        else:
            class_idx = rng.permutation(np.flatnonzero(label_idxs == label_idx))
            min_label = 1 if dev_df is not None else 2
            num_label = min(len(class_idx), max(min_label, round(len(class_idx) * labeled_ratio)))

        ## dev가 있으면 valid를 dev에서 만들므로 labeled 샘플은 전부 train_known
        if dev_df is not None:
            num_valid = 0

        else:
            num_valid = max(1, round(num_label * 0.2)) if num_label >= 2 else 0

        ## labeled 샘플 중 20% -> 검증 데이터, 나머지 80% -> 라벨 있는 학습 데이터
        valid_idx.extend(class_idx[ :num_valid].tolist())
        train_known_idx.extend(class_idx[num_valid:num_label].tolist())

    train_known_idx = sorted(train_known_idx)
    valid_idx       = sorted(valid_idx)

    ## 라벨 미공개 known 샘플 + novel 클래스 샘플 전부 -> 라벨 없는 학습 데이터
    labeled_idx     = set(train_known_idx) | set(valid_idx)
    train_novel_idx = [idx for idx in range(len(train_df)) if idx not in labeled_idx]


    ## DataFrame을 토크나이즈하여 (input_ids, attention_mask, label) TensorDataset으로 변환
    def tokenize_df(df_subset):
        texts  = df_subset['text'].tolist()
        labels = df_subset['label_idx'].tolist()

        toks   = tokenizer(
            texts, padding = 'max_length', truncation = True,
            max_length = max_length, return_tensors = 'pt'
        ) 

        return TensorDataset(
            toks['input_ids'], toks['attention_mask'],
            torch.tensor(labels, dtype = torch.long)
        )


    ## 분할별 TensorDataset 생성 (test는 known/novel 클래스를 모두 포함)
    train_known_set = tokenize_df(train_df.loc[train_known_idx])
    train_novel_set = tokenize_df(train_df.loc[train_novel_idx])
    valid_set       = tokenize_df(dev_df[dev_df['label_idx'].isin(known_classes)]) \
                        if dev_df is not None else tokenize_df(train_df.loc[valid_idx])
    test_set        = tokenize_df(test_df) if test_df is not None else None

    return {
        'train_known'   : train_known_set,
        'train_novel'   : train_novel_set,
        'valid'         : valid_set,
        'test'          : test_set,
        'known_classes' : known_classes,
        'novel_classes' : novel_classes,
        'label2idx'     : label2idx,
        'idx2label'     : idx2label,
        'num_classes'   : num_classes
    }
```

---

## 3. 핵심 파이프라인 구현 코드

### 3.1 모델 아키텍처 (BERT + Mean Pooling + Dense Layer) (`src/models.py`)
- `feat_dim=None`이면 Dense 없이 mean pooling 결과를 그대로 씁니다 (학습 없는 k-Means 하한선에서 랜덤 초기화된 Dense가 feature를 왜곡하지 않도록).
- `attn_implementation`: MPS에서는 `'eager'`를 넘깁니다.

```python
from transformers import BertModel
import torch.nn as nn
import torch


class BertForDeepAligned(nn.Module):

    def __init__(
            self,
            pretrained_model_name: str = 'bert-base-uncased',
            num_classes: int = None,
            feat_dim: int    = 768,
            attn_implementation: str = None
        ):

        super().__init__()

        ## BERT 인코더 + Dense(Tanh) -> intent representation
        ## attn_implementation: MPS에서는 SDPA가 학습 중 dropout을 지원하지 않으므로 'eager' 사용
        self.bert = BertModel.from_pretrained(
            pretrained_model_name, attn_implementation = attn_implementation
        )

        ## feat_dim이 None이면 Dense 없이 mean pooling 결과를 그대로 사용
        ## (학습 없는 k-Means 베이스라인에서 랜덤 초기화된 Dense가 feature를 왜곡하지 않도록)
        hidden_size = self.bert.config.hidden_size
        if feat_dim is None:
            self.feat_dim = hidden_size
            self.dense    = nn.Identity()

        else:
            self.feat_dim = feat_dim
            self.dense    = nn.Sequential(
                nn.Linear(hidden_size, feat_dim),
                nn.Tanh()
            )

        ## num_classes가 없으면 분류 헤드 없이 feature만 사용
        self.classifier = nn.Linear(self.feat_dim, num_classes) \
                            if num_classes is not None else None


    def forward(self, input_ids, attention_mask):

        outputs = self.bert(input_ids = input_ids, attention_mask = attention_mask)

        ## 패딩 토큰을 제외한 mean pooling
        token_embeddings = outputs.last_hidden_state                          # [B, L, H]
        mask_expanded    = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings   = torch.sum(token_embeddings * mask_expanded, 1)
        sum_mask         = torch.clamp(mask_expanded.sum(1), min = 1e-9)
        mean_pooled      = sum_embeddings / sum_mask                          # [B, H]

        features = self.dense(mean_pooled)                                    # [B, feat_dim]
        logits   = self.classifier(features) if self.classifier is not None else None
        return features, logits


    def reinit_classifier(self, num_classes: int):

        ## Stage 2에서 클러스터 수(K)에 맞춰 분류 헤드를 새로 생성
        ## (num_clusters != num_classes일 때 cross_entropy index 에러 방지)
        device = next(self.parameters()).device
        self.classifier = nn.Linear(self.feat_dim, num_classes).to(device)


    def freeze_backbone_except_last_layer(self):

        ## BERT 마지막 레이어(layer 11)와 pooler만 학습, 나머지는 동결
        for name, param in self.bert.named_parameters():
            if 'encoder.layer.11' not in name and 'pooler' not in name:
                param.requires_grad = False
```

### 3.2 헝가리안 정렬 & 클래스 개수($K$) 추정 (`src/clustering.py`)
- `hungarian_align`: 매 에포크 k-Means의 클러스터 번호가 임의로 바뀌므로, 이전 에포크 중심점과 1:1 매칭하여 pseudo label 번호를 고정합니다.
- `estimate_cluster_num`: $K' = 2 \times$ expected_k로 k-Means 후, 평균 군집 크기($N/K'$) 미만인 군집을 제거하여 유효 $K$를 추정합니다. (현재 파이프라인은 oracle K = 전체 클래스 수 사용)

```python
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
import numpy as np


def hungarian_align(current_centroids, prev_centroids, current_labels):

    ## 이전 epoch 중심점과 현재 중심점을 1:1 매칭하여 pseudo label 번호를 정렬
    ## (매 epoch k-Means 결과의 클러스터 번호가 바뀌는 문제 해결)
    if prev_centroids is None:
        return current_labels, current_centroids

    assert current_centroids.shape == prev_centroids.shape, \
        f'centroid shape 불일치: {current_centroids.shape} vs {prev_centroids.shape}'

    ## 유클리디안 거리 비용 행렬 [K, K]
    cost_matrix = np.linalg.norm(
        current_centroids[:, None, :] - prev_centroids[None, :, :], axis = 2
    )
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    ## 현재 클러스터 번호 -> 이전 클러스터 번호 매핑
    mapping = np.empty(len(current_centroids), dtype = int)
    mapping[row_ind] = col_ind
    aligned_labels   = mapping[current_labels]

    ## 다음 epoch 비교를 위해 중심점도 같은 순서로 재정렬
    aligned_centroids = np.zeros_like(current_centroids)
    aligned_centroids[col_ind] = current_centroids[row_ind]

    return aligned_labels, aligned_centroids


def estimate_cluster_num(features, expected_k: int, max_k_factor: int = 2, seed: int = 42):

    ## K' = expected_k * max_k_factor로 k-Means 수행 후
    ## 평균 군집 크기(N / K') 미만인 군집을 제거하여 유효 K 추정
    k_prime = int(expected_k * max_k_factor)
    kmeans  = KMeans(n_clusters = k_prime, n_init = 10, random_state = seed).fit(features)

    cluster_sizes = np.bincount(kmeans.labels_, minlength = k_prime)
    threshold     = len(features) / k_prime
    estimated_k   = int(np.sum(cluster_sizes >= threshold))

    return max(estimated_k, 2)
```

### 3.3 세분화 평가 메트릭 (`src/metrics.py`)
전체 샘플에 대해 한 번의 헝가리안 매칭을 구한 뒤, 정답 클래스가 Known인지 Novel인지로 나누어 정확도를 계산합니다. 에이전트 평가에도 이 함수를 그대로 사용합니다.
```python
from sklearn.metrics import normalized_mutual_info_score as NMI
from sklearn.metrics import adjusted_rand_score as ARI
from scipy.optimize import linear_sum_assignment
import numpy as np


def compute_gcd_metrics(y_true, y_pred, known_classes) -> dict:

    ## 헝가리안 매칭 후 All / Known / Novel ACC와 NMI, ARI 계산
    ## (y_pred 클러스터 번호와 y_true 클래스 번호는 임의로 다르므로 최적 매칭 필요)
    if hasattr(y_true, 'cpu'):
        y_true = y_true.cpu().numpy()
    if hasattr(y_pred, 'cpu'):
        y_pred = y_pred.cpu().numpy()

    y_true = np.asarray(y_true, dtype = np.int64)
    y_pred = np.asarray(y_pred, dtype = np.int64)
    assert y_pred.size == y_true.size, \
        f'크기 불일치: pred ({y_pred.size}) vs true ({y_true.size})'

    ## 예측-정답 혼동 행렬 (클러스터 수와 클래스 수가 달라도 정사각 행렬로 생성)
    D = max(y_pred.max(), y_true.max()) + 1
    w = np.zeros((D, D), dtype = np.int64)
    np.add.at(w, (y_pred, y_true), 1)

    ## 일치 수 최대화 -> 비용 최소화 문제로 변환
    row_ind, col_ind = linear_sum_assignment(w.max() - w)
    mapping = np.empty(D, dtype = np.int64)
    mapping[row_ind] = col_ind

    correct_mask = mapping[y_pred] == y_true

    ## known / novel 클래스별 정확도
    known_mask = np.isin(y_true, list(known_classes))
    novel_mask = ~known_mask

    all_acc   = correct_mask.mean() * 100.0
    known_acc = correct_mask[known_mask].mean() * 100.0 if known_mask.any() else 0.0
    novel_acc = correct_mask[novel_mask].mean() * 100.0 if novel_mask.any() else 0.0

    return {
        'all_acc'   : round(float(all_acc), 2),
        'known_acc' : round(float(known_acc), 2),
        'novel_acc' : round(float(novel_acc), 2),
        'nmi'       : round(NMI(y_true, y_pred) * 100.0, 2),
        'ari'       : round(ARI(y_true, y_pred) * 100.0, 2)
    }
```

### 3.4 학습 매니저 (`src/trainer.py`)
- **Stage 1 조기 종료**: 최대 100에포크, valid 정확도가 `patience`(10) 에포크 동안 오르지 않으면 종료하고 최고 시점 가중치로 복원 (best 가중치는 CPU에 복사해 GPU 메모리를 늘리지 않음).
- 에포크별 loss / valid 정확도를 MLflow에 기록합니다 (`log_metrics`는 활성 run이 없으면 아무것도 하지 않음).

```python
from torch.utils.data import DataLoader, TensorDataset
from sklearn.cluster import KMeans
import torch.nn.functional as F
import numpy as np
import torch

from .clustering import hungarian_align
from .metrics import compute_gcd_metrics
from .utils import log_metrics


class DeepAlignedTrainer:

    def __init__(self, model, device, lr: float = 5e-5, seed: int = 42):

        self.model  = model.to(device)
        self.device = device
        self.seed   = seed

        self.optimizer      = self._build_optimizer(lr)
        self.prev_centroids = None


    def _build_optimizer(self, lr: float):

        ## 동결된 파라미터는 제외하고 학습 가능한 파라미터만 등록
        params = [p for p in self.model.parameters() if p.requires_grad]
        return torch.optim.AdamW(params, lr = lr)


    def extract_features(self, dataloader):

        ## dataloader 전체의 feature와 (있다면) label 추출
        self.model.eval()
        all_feats, all_labels = [], []

        with torch.no_grad():
            for batch in dataloader:
                input_ids      = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)

                feats, _ = self.model(input_ids, attention_mask)
                all_feats.append(feats.cpu().numpy())

                if len(batch) > 2:
                    all_labels.append(batch[2].numpy())

        all_feats  = np.concatenate(all_feats, axis = 0) if all_feats else None
        all_labels = np.concatenate(all_labels, axis = 0) if all_labels else None
        return all_feats, all_labels


    def pretrain_step(
            self,
            train_known_loader,
            valid_loader  = None,
            epochs: int   = 100,
            patience: int = 10
        ):

        ## Stage 1: known 클래스 라벨 데이터로 지도 학습 + known-only 검증
        ##  - valid 정확도가 patience epoch 동안 개선되지 않으면 조기 종료
        ##  - 종료 후 valid 정확도가 가장 높았던 시점의 가중치로 복원
        print('\n=== [Stage 1] Supervised Pretraining on Known Labeled Data ===')

        best_acc, best_epoch, best_state, wait = -1.0, 0, None, 0

        for epoch in range(epochs):

            ## evaluate_classifier()가 eval 모드로 바꾸므로 매 epoch train 모드로 복귀
            self.model.train()
            total_loss = 0.0

            for batch in train_known_loader:
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch[:3]]

                self.optimizer.zero_grad()
                _, logits = self.model(input_ids, attention_mask)
                loss      = F.cross_entropy(logits, labels)
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / max(len(train_known_loader), 1)
            if valid_loader is None:
                print(f'Epoch {epoch + 1}/{epochs} | Train Loss: {avg_loss:.4f}')
                log_metrics({'stage1_train_loss': avg_loss}, step = epoch + 1)
                continue

            valid_acc = self.evaluate_classifier(valid_loader)
            print(f'Epoch {epoch + 1}/{epochs} | Train Loss: {avg_loss:.4f} | Valid (Known) ACC: {valid_acc:.2f}%')
            log_metrics({'stage1_train_loss': avg_loss, 'stage1_valid_acc': valid_acc}, step = epoch + 1)

            ## best 가중치는 CPU에 복사해 두어 GPU 메모리 사용을 늘리지 않음
            if valid_acc > best_acc:
                best_acc, best_epoch, wait = valid_acc, epoch + 1, 0
                best_state = {k: v.detach().cpu().clone() for k, v in self.model.state_dict().items()}

            else:
                wait += 1
                if wait >= patience:
                    print(f'[Stage 1] early stopping at epoch {epoch + 1} (patience {patience})')
                    break

        if best_state is not None:
            self.model.load_state_dict(best_state)
            print(f'[Stage 1] best valid ACC {best_acc:.2f}% at epoch {best_epoch} -> 가중치 복원')
            log_metrics({'stage1_best_valid_acc': best_acc, 'stage1_best_epoch': best_epoch})


    def evaluate_classifier(self, dataloader) -> float:

        ## 분류 헤드 기준 정확도 (known-only valid 평가용)
        self.model.eval()
        correct, total = 0, 0

        with torch.no_grad():
            for batch in dataloader:
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch[:3]]

                _, logits = self.model(input_ids, attention_mask)
                preds     = torch.argmax(logits, dim = -1)

                correct += (preds == labels).sum().item()
                total   += labels.size(0)

        return correct / total * 100.0 if total > 0 else 0.0


    def cluster_and_align(self, features, num_clusters: int):

        ## k-Means로 pseudo label 생성 후 이전 epoch 기준으로 헝가리안 정렬
        kmeans = KMeans(n_clusters = num_clusters, n_init = 10, random_state = self.seed).fit(features)

        aligned_labels, self.prev_centroids = hungarian_align(
            kmeans.cluster_centers_, self.prev_centroids, kmeans.labels_
        )
        return aligned_labels


    def train_aligned_clustering(
            self,
            train_novel_loader,
            num_clusters: int,
            epochs: int     = 15,
            batch_size: int = 64,
            lr_dac: float   = 1e-5
        ):

        ## Stage 2: Deep Aligned Clustering
        ##  - 매 epoch feature 추출 -> k-Means -> 헝가리안 정렬 -> pseudo label로 재학습
        print('\n=== [Stage 2] Deep Aligned Clustering on Unlabeled Data ===')

        ## 분류 헤드 차원을 클러스터 수에 맞추고 optimizer 재생성
        if self.model.classifier is None or self.model.classifier.out_features != num_clusters:
            print(f'[DAC] classifier head -> {num_clusters} classes')
            self.model.reinit_classifier(num_clusters)
        self.optimizer = self._build_optimizer(lr_dac)

        input_ids_all, attention_mask_all = train_novel_loader.dataset.tensors[:2]
        eval_loader = DataLoader(
            TensorDataset(input_ids_all, attention_mask_all),
            batch_size = batch_size, shuffle = False
        )

        for epoch in range(epochs):

            ## 1) feature 추출 및 pseudo label 생성
            features, _    = self.extract_features(eval_loader)
            aligned_labels = self.cluster_and_align(features, num_clusters)

            ## 2) 정렬된 pseudo label로 재학습
            train_loader = DataLoader(
                TensorDataset(input_ids_all, attention_mask_all,
                              torch.tensor(aligned_labels, dtype = torch.long)),
                batch_size = batch_size, shuffle = True
            )

            self.model.train()
            total_loss = 0.0

            for batch in train_loader:
                input_ids, attention_mask, pseudo = [b.to(self.device) for b in batch]

                self.optimizer.zero_grad()
                _, logits = self.model(input_ids, attention_mask)
                loss      = F.cross_entropy(logits, pseudo)
                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / max(len(train_loader), 1)
            print(f'[DAC] Epoch {epoch + 1}/{epochs} | Clustering Loss: {avg_loss:.4f}')
            log_metrics({'stage2_train_loss': avg_loss}, step = epoch + 1)


    def evaluate_test(self, test_loader, num_clusters: int, known_classes):

        ## test feature에 k-Means 적용 후 All / Known / Novel 지표 계산
        print('\n=== [Final Evaluation] Test Set Metrics ===')

        features, y_true = self.extract_features(test_loader)
        if y_true is None:
            print('Warning: test 데이터에 label이 없어 지표를 계산할 수 없습니다.')
            return None, features, None

        kmeans  = KMeans(n_clusters = num_clusters, n_init = 10, random_state = self.seed).fit(features)
        metrics = compute_gcd_metrics(y_true, kmeans.labels_, known_classes)

        print('Final Results:', metrics)
        return metrics, features, y_true
```

---

## 4. MLflow 실험 트래킹

### 4.1 기록 항목
| 종류 | 내용 |
|---|---|
| 파라미터 | 실행 설정 전체(`vars(args)`), 분할 크기(`size_train_known` 등), `num_known`/`num_novel`, fold 번호 |
| 태그 | `device`, 교차검증 시 `cv=stratified_kfold`, `cv_num_splits` |
| 에포크별 지표 | `stage1_train_loss`, `stage1_valid_acc`, `stage2_train_loss` |
| 요약 지표 | `stage1_best_valid_acc`, `stage1_best_epoch`, `test_all_acc`, `test_known_acc`, `test_novel_acc`, `test_nmi`, `test_ari` |
| 파일 | `metrics_{method}.json`, `known_novel_split.json`, `label2idx.json`, `plots/cluster_tsne_{method}.png` |

### 4.2 교차검증 parent-child 구조
```text
deepaligned_cv5 (parent)  ← 설정 전체, test_*_mean / test_*_std, cv_summary_deepaligned.json
 ├─ fold_0 (child)        ← 학습 곡선, test 지표, 지표 json, 분할 파일, t-SNE
 ├─ fold_1
 ├─ fold_2
 ├─ fold_3
 └─ fold_4
```
- 서버: `https://mlflow.dove-nest.com`, 실험 이름 `gcd-baseline`
- 짧은 확인 실행(2 fold, 각 1에포크)으로 child run이 parent를 가리키고 parent에 평균·표준편차가 기록되는 것을 확인했습니다.

> [!warning] 트래킹 서버 보안
> 확인 당시 서버가 **인증 없이** 다른 프로젝트의 실험 목록까지 읽을 수 있는 상태였습니다. 의도한 설정이 아니라면 인증 추가를 검토합니다.

---

## 5. 실행 및 제출

### 5.1 프로젝트 폴더 구조
```text
gcd-baseline/
├── pyproject.toml              # uv 의존성, [tool.uv] package = false, pytest pythonpath
├── uv.lock
├── .python-version             # 3.11
├── .env                        # MLFLOW_TRACKING_URI 등 (git 제외)
├── .gitignore
├── README.md
├── baseline.py                 # 엔드투엔드 실행 진입점 (단일 실행 / 교차검증, MLflow)
├── dataset/                    # train.tsv(9,003) / dev.tsv(1,000) / test.tsv(3,080), 헤더: text, label
├── src/
│   ├── __init__.py
│   ├── config.py               # 디바이스 설정 (MPS -> CUDA -> CPU)
│   ├── preprocessing.py        # TSV 로드, Known/Novel 분할, 층화 labeled, dev valid, CV fold
│   ├── models.py               # BertForDeepAligned (eager attention, Identity feature 옵션)
│   ├── clustering.py           # 헝가리안 정렬, K 추정
│   ├── metrics.py              # All / Known / Novel ACC, NMI, ARI
│   ├── trainer.py              # Stage 1(조기 종료) -> Stage 2(DAC) 루프, MLflow 기록
│   └── utils.py                # 시드 고정, MLflow 기록 헬퍼, t-SNE
├── tests/
│   └── test_leakage.py         # 누수 방지 · 분할 · 교차검증 테스트 (10개)
└── outputs/                    # 실행 결과 (git 제외)
    ├── label2idx.json, known_novel_split.json, metrics_{method}.json
    ├── plots/cluster_tsne_{method}.png
    └── cv/fold_{n}/..., cv/cv_summary_deepaligned.json
```

### 5.2 실행 진입점 (`baseline.py`)
```python
import argparse
import json
import os

from torch.utils.data import DataLoader
from transformers import AutoTokenizer
from dotenv import load_dotenv
import numpy as np
import mlflow

from src.preprocessing import prepare_gcd_dataset_from_tsv
from src.models import BertForDeepAligned
from src.trainer import DeepAlignedTrainer
from src.config import get_device
from src.utils import set_seed, plot_tsne, log_metrics


def parse_args():

    parser = argparse.ArgumentParser(description = 'DeepAligned GCD baseline')
    ## deepaligned: Stage 1 + Stage 2 학습 / kmeans: 학습 없이 사전학습 BERT feature에 k-Means (하한선)
    parser.add_argument('--method',          type = str,   default = 'deepaligned',
                        choices = ['deepaligned', 'kmeans'])
    parser.add_argument('--train_file_path', type = str,   default = 'dataset/train.tsv')
    parser.add_argument('--test_file_path',  type = str,   default = 'dataset/test.tsv')
    parser.add_argument('--dev_file_path',   type = str,   default = 'dataset/dev.tsv')
    parser.add_argument('--model_name',      type = str,   default = 'bert-base-uncased')
    parser.add_argument('--known_ratio',     type = float, default = 0.5)
    parser.add_argument('--labeled_ratio',   type = float, default = 0.1)
    parser.add_argument('--max_length',      type = int,   default = 64)
    ## Stage 1은 최대 epoch까지 학습하되 valid 정확도 기준으로 조기 종료
    parser.add_argument('--epochs_pretrain', type = int,   default = 100)
    parser.add_argument('--patience',        type = int,   default = 10)
    parser.add_argument('--epochs_dac',      type = int,   default = 15)
    parser.add_argument('--batch_size',      type = int,   default = 64)
    parser.add_argument('--lr',              type = float, default = 5e-5)
    parser.add_argument('--lr_dac',          type = float, default = 1e-5)
    parser.add_argument('--output_dir',      type = str,   default = 'outputs')
    parser.add_argument('--seed',            type = int,   default = 42)
    ## 교차검증 fold 수 (1이면 교차검증 없이 단일 실행)
    ## known 샘플을 1/labeled_ratio개 층화 fold로 나누고 그중 n_folds개를 각각 labeled 셋으로 사용
    parser.add_argument('--n_folds',         type = int,   default = 1)
    ## MLflow: tracking_uri를 지정하지 않으면 MLFLOW_TRACKING_URI 환경변수(.env 포함) 또는 기본값(./mlflow.db) 사용
    parser.add_argument('--mlflow_experiment',   type = str, default = 'gcd-baseline')
    parser.add_argument('--mlflow_tracking_uri', type = str, default = None)
    parser.add_argument('--run_name',            type = str, default = None)
    return parser.parse_args()


def run(args, fold: int = None) -> dict:

    ## 모델 초기화, DataLoader 셔플 등 PyTorch 난수까지 재현되도록 시드 고정
    ## (fold마다 같은 시드 -> labeled 셋 외의 조건은 동일)
    set_seed(args.seed)
    device = get_device()
    print(f'[*] device: {device}' + (f' | fold: {fold}' if fold is not None else ''))

    ## fold별 결과 파일은 output_dir/fold_{n}에 저장
    output_dir = args.output_dir if fold is None else os.path.join(args.output_dir, f'fold_{fold}')

    mlflow.log_params(vars(args))
    mlflow.set_tag('device', device.type)
    if fold is not None:
        mlflow.log_param('fold', fold)

    ## 1. 데이터셋 구성 (known / novel 분할)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    data      = prepare_gcd_dataset_from_tsv(
        tokenizer,
        train_file_path = args.train_file_path,
        test_file_path  = args.test_file_path,
        dev_file_path   = args.dev_file_path,
        known_ratio     = args.known_ratio,
        labeled_ratio   = args.labeled_ratio,
        max_length      = args.max_length,
        seed            = args.seed,
        fold            = fold,
        output_dir      = output_dir
    )

    num_classes   = data['num_classes']
    known_classes = data['known_classes']
    print(f'[*] classes: {num_classes} | known: {len(known_classes)} | novel: {len(data["novel_classes"])}')

    ## 분할 크기 기록 (실행 간 분할이 같은지 확인용)
    mlflow.log_params({
        'num_classes'      : num_classes,
        'num_known'        : len(known_classes),
        'num_novel'        : len(data['novel_classes']),
        'size_train_known' : len(data['train_known']),
        'size_train_novel' : len(data['train_novel']),
        'size_valid'       : len(data['valid']),
        'size_test'        : len(data['test']) if data['test'] is not None else 0
    })

    ## 2. DataLoader
    train_known_loader = DataLoader(data['train_known'], batch_size = args.batch_size, shuffle = True)
    train_novel_loader = DataLoader(data['train_novel'], batch_size = args.batch_size, shuffle = False)
    valid_loader       = DataLoader(data['valid'],       batch_size = args.batch_size, shuffle = False)

    ## test가 없으면 train_novel로 평가
    test_loader = DataLoader(data['test'], batch_size = args.batch_size, shuffle = False) \
                    if data['test'] is not None else train_novel_loader

    ## 3. 모델
    ##    MPS는 SDPA attention의 dropout을 지원하지 않아 eager attention 사용
    attn_implementation = 'eager' if device.type == 'mps' else None

    if args.method == 'kmeans':
        ## 학습 없음: Dense / 분류 헤드 없이 mean pooling feature 사용
        model   = BertForDeepAligned(args.model_name, num_classes = None, feat_dim = None,
                                     attn_implementation = attn_implementation)
        trainer = DeepAlignedTrainer(model, device, lr = args.lr, seed = args.seed)

    else:
        ## 마지막 BERT 레이어만 학습
        model = BertForDeepAligned(args.model_name, num_classes = num_classes,
                                   attn_implementation = attn_implementation)
        model.freeze_backbone_except_last_layer()
        trainer = DeepAlignedTrainer(model, device, lr = args.lr, seed = args.seed)

        ## 4. Stage 1: known 라벨 데이터로 지도 학습 (valid 기준 조기 종료)
        trainer.pretrain_step(train_known_loader, valid_loader,
                              epochs = args.epochs_pretrain, patience = args.patience)

        ## 5. Stage 2: Deep Aligned Clustering (클러스터 수 = 전체 클래스 수, oracle K)
        trainer.train_aligned_clustering(
            train_novel_loader,
            num_clusters = num_classes,
            epochs       = args.epochs_dac,
            batch_size   = args.batch_size,
            lr_dac       = args.lr_dac
        )

    ## 6. 평가 (All / Known / Novel ACC, NMI, ARI)
    metrics, features, y_true = trainer.evaluate_test(
        test_loader, num_clusters = num_classes, known_classes = known_classes
    )

    ## 비교표 작성을 위해 지표와 실행 설정을 json으로 저장
    if metrics is not None:
        log_metrics({f'test_{k}': v for k, v in metrics.items()})

        metrics_path = os.path.join(output_dir, f'metrics_{args.method}.json')
        with open(metrics_path, 'w', encoding = 'utf-8') as f:

            json.dump({'method': args.method, 'fold': fold, 'metrics': metrics, 'args': vars(args)},
                      f, ensure_ascii = False, indent = 2)

        print(f'[*] metrics saved -> {metrics_path}')
        mlflow.log_artifact(metrics_path)

    ## 다른 방법(에이전트)과 같은 분할을 쓰도록 분할 정보도 함께 보관
    mlflow.log_artifact(os.path.join(output_dir, 'known_novel_split.json'))
    mlflow.log_artifact(os.path.join(output_dir, 'label2idx.json'))

    ## 7. 잠재 공간 시각화 (t-SNE)
    if features is not None and y_true is not None:
        plot_path = os.path.join(output_dir, 'plots', f'cluster_tsne_{args.method}.png')
        plot_tsne(features, y_true, known_classes, save_path = plot_path, seed = args.seed)
        mlflow.log_artifact(plot_path, artifact_path = 'plots')

    return metrics


def run_cv(args):

    ## Stratified k-Fold 교차검증 (MLflow parent-child 구조)
    ##  - parent run : 전체 설정 + fold 평균 / 표준편차
    ##  - child run  : fold별 학습 곡선, 지표, 결과 파일
    num_splits = round(1 / args.labeled_ratio)
    assert args.n_folds <= num_splits, \
        f'n_folds({args.n_folds})는 1/labeled_ratio({num_splits}) 이하여야 합니다'

    mlflow.log_params(vars(args))
    mlflow.set_tags({'cv': 'stratified_kfold', 'cv_num_splits': num_splits})

    fold_metrics = []
    for fold in range(args.n_folds):
        with mlflow.start_run(run_name = f'fold_{fold}', nested = True):
            fold_metrics.append(run(args, fold = fold))

    ## fold 평균 / 표준편차를 parent run에 기록
    summary = {}
    for key in fold_metrics[0]:
        values = np.array([m[key] for m in fold_metrics])
        summary[f'{key}_mean'] = round(float(values.mean()), 2)
        summary[f'{key}_std']  = round(float(values.std(ddof = 1)), 2) if len(values) > 1 else 0.0

    log_metrics({f'test_{k}': v for k, v in summary.items()})
    print('\n=== [CV Summary] ===')
    for key in fold_metrics[0]:
        print(f'{key:>10}: {summary[key + "_mean"]:.2f} ± {summary[key + "_std"]:.2f}')

    summary_path = os.path.join(args.output_dir, f'cv_summary_{args.method}.json')
    with open(summary_path, 'w', encoding = 'utf-8') as f:

        json.dump({'method': args.method, 'n_folds': args.n_folds, 'num_splits': num_splits,
                   'summary': summary, 'folds': fold_metrics, 'args': vars(args)},
                  f, ensure_ascii = False, indent = 2)

    mlflow.log_artifact(summary_path)


def main():

    ## .env의 환경변수 로드 (이미 셸에 설정된 값이 있으면 그 값을 우선)
    load_dotenv()
    args = parse_args()

    if args.mlflow_tracking_uri:
        mlflow.set_tracking_uri(args.mlflow_tracking_uri)
    mlflow.set_experiment(args.mlflow_experiment)

    ## k-Means는 labeled 셋을 쓰지 않아 fold마다 결과가 같으므로 교차검증하지 않음
    use_cv = args.n_folds > 1 and args.method != 'kmeans'
    if args.n_folds > 1 and not use_cv:
        print('[*] kmeans는 labeled 셋을 사용하지 않아 교차검증 없이 1회만 실행합니다.')

    default_name = f'{args.method}_cv{args.n_folds}' if use_cv else args.method
    with mlflow.start_run(run_name = args.run_name or default_name):
        run_cv(args) if use_cv else run(args)


if __name__ == '__main__':
    main()
```

### 5.3 시드 고정 · MLflow 헬퍼 · t-SNE (`src/utils.py`)
- t-SNE: Known은 원(o), Novel은 삼각형(^), 색은 정답 클래스. 77개 클래스에서도 구분되도록 흰색 계열이 없는 `turbo` colormap 사용, 범례는 `Line2D`로 회색 고정.

```python
import random
import os

from sklearn.manifold import TSNE
import matplotlib
import mlflow
import numpy as np
import torch

## GUI 없이 파일로만 저장 (서버/터미널 환경 대응)
matplotlib.use('Agg')
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt


def set_seed(seed: int = 42):

    ## 재현성을 위한 전역 시드 고정 (Python / NumPy / PyTorch)
    ## torch.manual_seed는 CUDA, MPS 시드도 함께 설정함
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def log_metrics(metrics: dict, step: int = None):

    ## 실행 중인 MLflow run이 있을 때만 기록 (테스트 등 run 없이 호출해도 동작)
    if mlflow.active_run() is not None:
        mlflow.log_metrics(metrics, step = step)


def plot_tsne(
        features,
        labels,
        known_classes,
        save_path: str = 'outputs/plots/cluster_tsne.png',
        seed: int      = 42
    ):

    ## feature를 2D t-SNE로 축소하여 known(원) / novel(삼각형) 분리도 시각화
    ## 색은 정답 클래스 기준
    if hasattr(features, 'cpu'):
        features = features.cpu().numpy()
    if hasattr(labels, 'cpu'):
        labels = labels.cpu().numpy()

    labels = np.asarray(labels)

    dir_name = os.path.dirname(save_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok = True)

    embeds_2d = TSNE(n_components = 2, random_state = seed, init = 'pca').fit_transform(features)
    is_known  = np.isin(labels, list(known_classes))

    ## 클래스 수가 많아도(예: 77개) 색이 덜 겹치도록 연속 colormap 사용
    ## (turbo는 흰색 계열이 없어 배경과 구분됨)
    num_colors = max(int(labels.max()) + 1, 1)
    cmap       = plt.get_cmap('turbo', num_colors)

    plt.figure(figsize = (10, 8))
    plt.scatter(embeds_2d[is_known, 0], embeds_2d[is_known, 1], c = labels[is_known],
                cmap = cmap, vmin = 0, vmax = num_colors - 1,
                marker = 'o', s = 12, alpha = 0.6)
    plt.scatter(embeds_2d[~is_known, 0], embeds_2d[~is_known, 1], c = labels[~is_known],
                cmap = cmap, vmin = 0, vmax = num_colors - 1,
                marker = '^', s = 20, alpha = 0.8, edgecolor = 'black', linewidth = 0.3)

    plt.title('DeepAligned Latent Space (Known vs Novel)')

    ## 범례 마커는 클래스 색이 아닌 회색으로 고정 (모양만 구분)
    plt.legend(handles = [
        Line2D([], [], marker = 'o', linestyle = '', color = 'gray', label = 'Known'),
        Line2D([], [], marker = '^', linestyle = '', color = 'gray',
               markeredgecolor = 'black', label = 'Novel')
    ])
    plt.tight_layout()
    plt.savefig(save_path, dpi = 300)
    plt.close()

    print(f'[Visualization] t-SNE plot saved -> {save_path}')
```

### 5.4 단위 테스트 (`tests/test_leakage.py`, 10개)
가짜 tokenizer를 쓰므로 BERT 다운로드 없이 1초 안에 실행됩니다. 단, 모델 학습·MPS 동작은 검증하지 않으므로 실제 bert-base 짧은 실행으로 따로 확인합니다.

| 테스트 | 확인 내용 |
|---|---|
| `test_header_is_not_a_class` | 헤더 줄이 `label` 클래스로 들어가지 않음 |
| `test_known_novel_disjoint` | Known·Novel이 겹치지 않고 합치면 전체 클래스 |
| `test_no_novel_leakage` | `train_known`, `valid`에 Novel 클래스 없음 (**타깃 누수 차단**) |
| `test_test_only_class_is_novel` | test에만 있는 클래스는 Novel |
| `test_every_known_class_has_labeled_and_valid` | 모든 Known 클래스가 `train_known`, `valid`에 각각 존재 |
| `test_small_data_valid_not_empty` | 클래스당 2개뿐이어도 시드 20개 모두 valid가 비지 않음 |
| `test_split_file_saved` | `known_novel_split.json`의 클래스가 실제 분할과 일치 |
| `test_dev_used_as_known_only_valid` | dev 사용 시 valid = dev의 Known 샘플, labeled 전부 `train_known` |
| `test_cv_folds_are_disjoint_and_stratified` | fold마다 Known 분할 동일, labeled 셋 비율 유지·서로 겹치지 않음 |
| `test_splits_cover_train_once` | train 샘플이 세 분할 중 정확히 한 곳에만 들어감 |

```python
import json

import torch

from src.preprocessing import prepare_gcd_dataset_from_tsv


def dummy_tokenizer(texts, max_length = 8, **kwargs):

    ## 모델 다운로드 없이 분할 로직만 검증하기 위한 가짜 tokenizer
    n = len(texts)
    return {
        'input_ids'      : torch.zeros((n, max_length), dtype = torch.long),
        'attention_mask' : torch.ones((n, max_length), dtype = torch.long)
    }


def make_dataset(tmp_path, num_classes: int = 6, samples_per_class: int = 40):

    ## 헤더(text, label)가 있는 모의 train/test tsv 생성
    ## test에는 train에 없는 클래스(test_only) 하나를 추가
    rows = ['text\tlabel'] + [f'utterance {i} of class {c}\tclass_{c}'
                              for c in range(num_classes) for i in range(samples_per_class)]

    train_path = tmp_path / 'train.tsv'
    test_path  = tmp_path / 'test.tsv'
    train_path.write_text('\n'.join(rows) + '\n', encoding = 'utf-8')
    test_path.write_text('text\tlabel\nhello "world\tclass_0\nnew intent\ttest_only\n', encoding = 'utf-8')

    return prepare_gcd_dataset_from_tsv(
        dummy_tokenizer,
        train_file_path = str(train_path),
        test_file_path  = str(test_path),
        known_ratio     = 0.5,
        labeled_ratio   = 0.5,
        seed            = 42,
        output_dir      = str(tmp_path)
    )


def labels_of(dataset) -> set:
    return set(dataset.tensors[2].tolist())


def test_header_is_not_a_class(tmp_path):

    ## 헤더 줄이 'label' 클래스로 들어가지 않아야 함
    data = make_dataset(tmp_path)
    assert 'label' not in data['label2idx']
    assert data['num_classes'] == 6 + 1


def test_known_novel_disjoint(tmp_path):

    data = make_dataset(tmp_path)
    assert not data['known_classes'] & data['novel_classes']
    assert data['known_classes'] | data['novel_classes'] == set(data['label2idx'].values())


def test_no_novel_leakage(tmp_path):

    ## train_known, valid에는 novel 클래스가 절대 포함되면 안 됨 (target leakage 방지)
    data  = make_dataset(tmp_path)
    novel = data['novel_classes']

    assert len(data['valid']) > 0
    assert not labels_of(data['train_known']) & novel
    assert not labels_of(data['valid']) & novel


def test_test_only_class_is_novel(tmp_path):

    ## test에만 있는 클래스는 항상 novel
    data = make_dataset(tmp_path)
    assert data['label2idx']['test_only'] in data['novel_classes']


def test_every_known_class_has_labeled_and_valid(tmp_path):

    ## 층화 분할: 모든 known 클래스가 train_known, valid에 최소 1개씩 있어야 함
    data  = make_dataset(tmp_path)
    known = data['known_classes']

    assert labels_of(data['train_known']) == known
    assert labels_of(data['valid']) == known


def test_small_data_valid_not_empty(tmp_path):

    ## 클래스당 샘플이 2개뿐이어도 valid가 비지 않아야 함 (여러 시드에서 확인)
    rows = ['text\tlabel'] + [f'u{i} c{c}\tclass_{c}' for c in range(4) for i in range(2)]
    train_path = tmp_path / 'small.tsv'
    train_path.write_text('\n'.join(rows) + '\n', encoding = 'utf-8')

    for seed in range(20):
        data = prepare_gcd_dataset_from_tsv(
            dummy_tokenizer, train_file_path = str(train_path),
            known_ratio = 0.5, labeled_ratio = 0.5, seed = seed, output_dir = str(tmp_path)
        )
        assert len(data['valid']) > 0
        assert len(data['train_known']) > 0


def test_split_file_saved(tmp_path):

    ## 다른 방법도 같은 분할을 쓰도록 known / novel 클래스 이름이 저장되어야 함
    data  = make_dataset(tmp_path)
    split = json.loads((tmp_path / 'known_novel_split.json').read_text(encoding = 'utf-8'))

    assert {data['label2idx'][lb] for lb in split['known_classes']} == data['known_classes']
    assert {data['label2idx'][lb] for lb in split['novel_classes']} == data['novel_classes']


def test_dev_used_as_known_only_valid(tmp_path):

    ## dev 파일이 있으면 valid는 dev의 known 클래스 샘플만으로 구성되고
    ## train의 labeled 샘플은 전부 train_known으로 사용
    dev_rows = ['text\tlabel'] + [f'dev {i} of class {c}\tclass_{c}' for c in range(6) for i in range(3)]
    dev_path = tmp_path / 'dev.tsv'
    dev_path.write_text('\n'.join(dev_rows) + '\n', encoding = 'utf-8')

    make_dataset(tmp_path)
    data = prepare_gcd_dataset_from_tsv(
        dummy_tokenizer,
        train_file_path = str(tmp_path / 'train.tsv'),
        dev_file_path   = str(dev_path),
        known_ratio     = 0.5,
        labeled_ratio   = 0.5,
        seed            = 42,
        output_dir      = str(tmp_path)
    )
    known = data['known_classes']

    assert labels_of(data['valid']) == known
    assert len(data['valid']) == len(known) * 3
    assert len(data['train_known']) == len(known) * 20
    assert len(data['train_known']) + len(data['train_novel']) == 6 * 40


def test_cv_folds_are_disjoint_and_stratified(tmp_path):

    ## 교차검증: fold마다 known/novel 분할은 같고, labeled 셋은 서로 겹치지 않으며
    ## 모든 known 클래스가 labeled_ratio 비율로 들어가야 함
    make_dataset(tmp_path)
    folds = [prepare_gcd_dataset_from_tsv(
                dummy_tokenizer,
                train_file_path = str(tmp_path / 'train.tsv'),
                known_ratio     = 0.5,
                labeled_ratio   = 0.25,
                seed            = 42,
                fold            = fold,
                output_dir      = str(tmp_path)
             ) for fold in range(4)]

    assert all(f['known_classes'] == folds[0]['known_classes'] for f in folds)

    ## 더미 tokenizer는 텍스트 정보를 잃으므로 샘플 수로 확인
    ## known 3개 클래스 x 40개 x 0.25 = 30개 (train_known + valid)
    for f in folds:
        assert len(f['train_known']) + len(f['valid']) == 30
        assert labels_of(f['train_known']) == f['known_classes']

    ## 4개 fold의 labeled 셋을 합치면 known 샘플 전체 (= 서로 겹치지 않음)
    total_labeled = sum(len(f['train_known']) + len(f['valid']) for f in folds)
    assert total_labeled == 3 * 40


def test_splits_cover_train_once(tmp_path):

    ## train 샘플은 train_known / valid / train_novel 중 정확히 한 곳에만 들어가야 함
    data  = make_dataset(tmp_path)
    total = len(data['train_known']) + len(data['valid']) + len(data['train_novel'])
    assert total == 6 * 40
```

### 5.5 실행 명령어
```bash
# 1) 단위 테스트 (BERT 다운로드 불필요)
uv run pytest

# 2) 학습 없는 k-Means 하한선 (약 1~2분)
uv run python baseline.py --method kmeans

# 3) DeepAligned 단일 실행 (약 25분)
caffeinate -i uv run python baseline.py --method deepaligned

# 4) DeepAligned 5-fold 교차검증 (약 2시간, parent-child run)
caffeinate -i uv run python baseline.py --method deepaligned --n_folds 5 --output_dir outputs/cv
```

---

## 6. 실험 결과 (test 3,080개, seed 42)

| 방법 | All ACC | Known ACC | Novel ACC | NMI | ARI | 비고 |
|---|---|---|---|---|---|---|
| BERT + k-Means (학습 없음) | 27.44 | 29.67 | 25.26 | 50.16 | 14.69 | 하한선 |
| **DeepAligned (5-fold, mean ± std)** | **52.11 ± 2.53** | **59.83 ± 2.21** | **44.59 ± 4.13** | **72.23 ± 0.90** | **40.72 ± 1.96** | MLflow `deepaligned_cv5` |
| 에이전트 | — | — | — | — | — | 같은 `known_novel_split.json`으로 평가 |

- 단일 실행(`deepaligned`)은 중단하고 5-fold 교차검증으로 대체했습니다 (MLflow 상태 KILLED, 태그로 사유 기록).
- 실행 시간: 2026-10-22 18:10 ~ 20:30 (약 2시간 20분, M4 MPS)
- MLflow: https://mlflow.dove-nest.com/#/experiments/48/runs/bfe0abd8d64844ce84cc47aa8ddac0b9

**fold별 결과**

| fold | Stage 1 조기 종료 | best valid ACC (epoch) | All ACC | Known ACC | Novel ACC | NMI | ARI |
|---|---|---|---|---|---|---|---|
| 0 | 56 | 85.14 (46) | 54.64 | 60.00 | 49.42 | 73.24 | 43.30 |
| 1 | 63 | 86.75 (53) | 49.48 | 60.72 | 38.53 | 71.36 | 39.13 |
| 2 | 45 | 86.55 (35) | 49.42 | 56.25 | 42.76 | 71.33 | 38.43 |
| 3 | 70 | 86.14 (60) | 54.25 | 62.24 | 46.47 | 73.04 | 41.64 |
| 4 | 62 | 86.75 (52) | 52.76 | 59.93 | 45.77 | 72.20 | 41.11 |

**해석**
- 학습 없는 k-Means 대비 All ACC **+24.7%p**, NMI **+22.1%p**로 DeepAligned 학습의 기여가 뚜렷합니다.
- Stage 1은 모든 fold에서 35~60 에포크에 valid 최고점(85~87%)에 도달했습니다. 기존 고정 5에포크로는 크게 부족했음을 확인했습니다.
- labeled 셋 선택에 따른 편차는 Novel ACC(±4.13)가 가장 크고, NMI(±0.90)는 안정적입니다.
- Known ACC(약 60%)가 Stage 1 valid ACC(약 86%)보다 낮은 이유: valid는 분류 헤드로 Known 클래스만 맞히는 문제이고, test는 77개 전체를 k-Means로 군집화한 뒤 헝가리안 매칭하는 문제라 난이도가 다릅니다.

> [!note] 동작 확인용 짧은 실행은 성능 결과가 아님
> 각 단계 1에포크 실행(All ACC 25.97)은 동작 확인용입니다. 당시 Stage 1 loss가 4.29로 77개 클래스 무작위 추측 값(약 4.34)과 거의 같아 학습이 거의 되지 않은 상태였고, 이 때문에 조기 종료(최대 100에포크)를 도입했습니다.

---

## 7. 구현 중 발견한 버그와 수정 이력

| 위치 | 문제 | 수정 |
|---|---|---|
| `load_tsv_file` | `header=None`으로 읽어 헤더 줄이 데이터가 됨 → 가짜 `label` 클래스로 **78개 클래스** | `header=0` → 77개 정상 |
| `load_tsv_file` | 기본 quoting 때문에 문장 속 `"`에서 여러 줄이 합쳐지거나 컬럼이 밀림 | `quoting=csv.QUOTE_NONE`, `dtype=str` |
| `load_tsv_file` | 라벨이 빈 행이 남아 `torch.long` 변환 에러 | `dropna` + 빈 문자열 제거 |
| Known 클래스 선택 | 전체 라벨(train ∪ test)에서 뽑아 test 전용 클래스가 Known이 될 수 있음 | train 라벨에서만 선택 |
| labeled / valid 분할 | 샘플 단위 난수 분할 → 작은 데이터에서 200개 시드 중 141개가 빈 valid | Known 클래스별 층화 분할 |
| valid | train labeled의 20%를 떼어 사용 (labeled 샘플 손실) | dev.tsv의 Known 샘플을 valid로 사용 |
| 시드 | `np.random.seed` 전역 변경, PyTorch 시드 미고정 | `np.random.default_rng(seed)` + `set_seed()` |
| `pretrain_step` | `model.train()`이 루프 밖에 1번 → 검증 후 eval 모드로 학습 (Dropout 꺼짐) | 매 에포크 시작 시 `model.train()` |
| `pretrain_step` | 고정 5에포크로는 학습 부족 (1에포크 loss ≈ 무작위 수준) | 최대 100에포크 + valid 기준 조기 종료 + best 가중치 복원 |
| BERT 로드 (MPS) | SDPA가 MPS 학습 중 dropout 미지원 → `NotImplementedError` | MPS에서 `attn_implementation='eager'` |
| k-Means 하한선 | 랜덤 초기화된 Dense가 feature를 왜곡 | `feat_dim=None` → `nn.Identity()` |
| 분할 재현 | 어떤 클래스가 Known인지 저장하지 않아 에이전트가 같은 분할을 쓸 수 없음 | `known_novel_split.json` 저장 |
| `compute_gcd_metrics` | 혼동 행렬을 Python 루프로 생성 | `np.add.at`으로 벡터화 |
| `pyproject.toml` | uv_build가 `src/gcd_baseline/`를 요구해 `uv add` / `uv run` 실패 | `[tool.uv] package = false` |
| t-SNE | `gist_ncar` 끝 색이 흰색, 범례에 임의 클래스 색 표시 | `turbo` colormap, `Line2D` 회색 범례 |

---

## 8. 한계점 및 면접 대비

### 8.1 모델 한계점 및 후속 개선 방향
1. **k-Means의 등방성(Spherical) 군집 가정의 한계:** 자연어 발화는 의도별 분산·밀도가 불균일하여 롱테일 인텐트에서 군집이 쪼개지거나 왜곡됩니다. *개선안:* HDBSCAN, KNN 기반 대조학습.
2. **표상 학습과 군집화의 분리:** 매 에포크 이산 pseudo label을 다시 학습하면서 확증 편향이 누적됩니다. *개선안:* SimGCD식 파라메트릭 분류기, MTP-CLNN식 대조 사전학습.
3. **Stage 2 학습 데이터 범위:** 현재는 `train_novel`(비라벨)만 클러스터링합니다. 원 논문 공식 구현은 labeled까지 포함한 train 전체를 쓰는 것으로 알려져 있으나 직접 확인하지 않았습니다. README에 설계 선택으로 명시합니다.
4. **oracle K 사용:** 클러스터 수를 실제 클래스 수(77)로 줍니다. 에이전트가 K를 모르는 설정이라면 `estimate_cluster_num`으로 추정한 K로도 비교해야 공정합니다.

### 8.2 면접 예상 질문 & 방어 논리
1. **Q. Validation Set에 Novel 클래스를 넣지 않은 이유는?**
   - GCD의 전제는 배포 전까지 Novel 클래스를 모른다는 점입니다. Novel이 검증셋에 들어가면 하이퍼파라미터 튜닝이 Novel 분포에 맞춰지는 **타깃 누수**가 생깁니다. 그래서 dev에서도 **Known 클래스 샘플만** 검증에 사용했습니다.
2. **Q. Known/Novel 비율은 왜 50:50인가?**
   - 학계 표준 벤치마크(DeepAligned, USNID, SimGCD 등)와의 비교를 위해서이며, 체리피킹을 피하려고 시드 고정 무작위 분할을 따랐습니다.
3. **Q. labeled / valid는 왜 클래스별로 층화 분할했나?**
   - 샘플 단위 난수 분할은 특정 Known 클래스의 labeled 샘플이 0개가 되거나 valid가 비는 문제가 있습니다. 층화하면 모든 Known 클래스가 지도 학습에 반드시 포함됩니다.
4. **Q. 교차검증은 무엇을 측정하나? 왜 5-fold인데 10개로 나눴나?**
   - "어떤 샘플이 labeled로 뽑혔는가"에 따른 편차를 mean ± std로 보고합니다. labeled 비율 10%를 유지하려고 Known 샘플을 10개 층화 fold로 나누고 그중 5개를 각각 labeled 셋으로 썼습니다. Known/Novel 분할·dev·test는 고정해 에이전트와 같은 조건을 유지했습니다.
5. **Q. 학습 없는 k-Means를 왜 넣었나?**
   - 하한선으로서 DeepAligned 학습이 실제로 얼마나 기여하는지, 에이전트가 하한선 대비 얼마나 나은지를 함께 보여 주기 위해서입니다.
6. **Q. 매 에포크 k-Means 연산 병목은?**
   - 현재 규모(8,554 × 768, K=77)에서는 에포크당 3초 수준이라 병목이 아닙니다. 규모가 커지면 FAISS GPU k-Means나 SimGCD식 파라메트릭 헤드로 대체할 수 있습니다.

---

## 관련 링크

- [[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트|DeepAligned 논문노트]]
- [[Learning/원문/2026-10-21-DeepAligned-원문|변환 원문 전문]]
- [[Learning/학습노트/2026-10-21-MTP-CLNN-사전학습-대조학습-인텐트발견-논문-노트|MTP-CLNN (ACL 2022)]]
- [[Learning/학습노트/2026-10-21-SimGCD-파라메트릭-분류-GCD-논문-노트|SimGCD (ICCV 2023)]]
- [[Learning/학습노트/index|학습노트 인덱스]]
