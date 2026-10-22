---
date: 2026-10-22
created: 2026-10-22
updated: 2026-10-22
document_role: learning-note
note_kind: implementation-guide
language: ko
tags: [learning, implementation, deepaligned, mac, uv, pytorch, nlp, banking77, gcd, interview]
paper_title: "Discovering New Intents with Deep Aligned Clustering"
paper_date: 2020-12-16
paper_id: "arXiv:2012.08987v7"
source_url: "https://arxiv.org/abs/2012.08987"
primary_text: "https://arxiv.org/html/2012.08987v7"
source_role: primary
code_repo: "gcd-baseline (로컬: ~/Desktop/Homework/gcd-baseline)"
capture_scope: "DeepAligned Mac uv 파이프라인 구현·Known/Novel 클래스별 층화 분할 및 누수 방지 프로토콜·All/Known/Novel 분리 평가 메트릭·헝가리안 정렬 전체 코드·t-SNE 시각화·인터뷰 사전 과제 실행 가이드"
paper_notes:
  - "[[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트]]"
source_notes:
  - "[[Learning/원문/2026-10-21-DeepAligned-원문]]"
---
# DeepAligned 파이프라인 구현 및 Mac uv 실행 가이드 (인터뷰 과제 대비)

> [!abstract] 개요
> 본 문서는 **DeepAligned (AAAI 2021)** 알고리즘을 Apple Silicon Mac 환경에서 `uv` 기반으로 직접 구현하고 재현하기 위한 **엔드투엔드 파이프라인 코드 및 엔지니어링 가이드**입니다.
> 공식 레포의 구형 레거시 종속성(`pytorch-pretrained-bert`)을 모던 `transformers`와 `torch`로 리팩터링하고, 인터뷰 사전 과제 평가에서 핵심 검토 대상인 **① 학계 표준 Known/Novel 분할 및 타깃 누수(Target Leakage) 방지 프로토콜**, **② Known-only 검증셋(Validation) 구축**, **③ All / Known / Novel 세분화 헝가리안 매칭 평가 지표**, **④ 모델 한계점 및 후속 개선 방향**을 정리했습니다.

> [!info] 코드 기준
> 이 노트의 코드는 실제 레포 `gcd-baseline`의 코드와 동일합니다 (2026-10-22 기준, 테스트 7개 통과).
> 변경 이력은 맨 아래 [[#5. 구현 중 발견한 버그와 수정 이력]]에 정리했습니다.

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
uv add numpy pandas scikit-learn scipy tqdm rich matplotlib
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

### 1.3 디바이스 자동 설정 (`src/config.py`)
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

---

## 2. 데이터 분할 및 타깃 누수 방지 프로토콜

인터뷰 사전 과제에서 가장 엄격하게 평가받는 부분은 **데이터셋 분할의 정당성과 데이터 누수(Data Leakage) 차단 여부**입니다.

### 2.1 Known / Novel 클래스 선정 기준
- **학계 표준 무작위 분할 (Uniform Random Split - 메인 베이스라인):**
  - 특정 도메인 편향이나 체리피킹을 배제하기 위해 고정된 시드(예: Seed 42, 0, 1)로 클래스 목록을 셔플한 뒤 분할합니다.
  - **Known 비율**: 통상 50% (38개 Known / 39개 Novel)를 메인 벤치마크로 사용하며, 필요시 25%와 75%를 비교군으로 둡니다.
  - Known 후보는 **train에 실제로 존재하는 클래스에서만** 뽑습니다. test에만 있는 클래스는 항상 Novel입니다.
- **실무 분석용 대안 기준 (Ablation / 심화 분석용):**
  - **도메인 계층(Prefix) 분할**: `card_*`, `transfer_*` 등 세부 의미 경계(Fine-grained) 분별력 검증.
  - **출현 빈도(Frequency) 분할**: 헤드(다빈도) 클래스를 Known, 롱테일(희귀) 클래스를 Novel로 두어 현실적 배포 환경 모사.

### 2.2 엄격한 데이터셋 분할 규칙 (코드 키 이름 기준)
1. **`train_known` (Train Labeled, $\mathcal{D}_l$):**
   - **Known 클래스마다** 샘플의 `labeled_ratio`(기본 10%)를 뽑고, 그중 80%를 지도 사전학습에 사용합니다.
2. **`valid` (Validation, $\mathcal{D}_{val}$):**
   - 위에서 뽑은 Known labeled 샘플의 나머지 20%입니다.
   - **절대 Novel 클래스 데이터가 포함되어서는 안 됩니다.**
   - *이유: 검증셋에 Novel 데이터가 유출되면 하이퍼파라미터 튜닝 시 미지의 클래스 분포에 사후 최적화(Target Leakage/Cheating)가 발생하여 GCD 문제 정의가 훼손됩니다.*
3. **`train_novel` (Train Unlabeled, $\mathcal{D}_u$):**
   - 라벨을 공개하지 않은 Known 샘플 + Novel 클래스 샘플 **100%**를 병합합니다.
   - 레이블을 제거한 상태로 Deep Aligned Clustering 루프(k-Means + 헝가리안 정렬 재학습)에 투입합니다.
   - 이름은 `train_novel`이지만 Known 클래스의 비라벨 샘플도 섞여 있다는 점에 유의합니다.
4. **`test` ($\mathcal{D}_{test}$):**
   - 공식 Test 세트 전체(3,080개)를 사용하며, 사후 평가 시 Known과 Novel 마스크를 적용해 분리 평가합니다.

> [!tip] 왜 클래스별 층화 분할인가
> 샘플마다 난수 하나로 labeled / valid / unlabeled를 정하면, 데이터가 작을 때 valid가 통째로 비거나 특정 Known 클래스의 labeled 샘플이 0개가 됩니다.
> 실제로 클래스당 2개짜리 테스트 데이터에서 **200개 시드 중 141개가 빈 valid**를 만들었습니다.
> 클래스마다 개수를 정해 뽑으면(클래스당 labeled 최소 2개 → train_known 1 + valid 1) 이런 경우가 사라집니다.

**Banking77 실제 분할 결과 (seed 42, known_ratio 0.5, labeled_ratio 0.1)**

| 분할 | 샘플 수 |
|---|---|
| 클래스 | 77 (Known 38 / Novel 39) |
| train_known | 360 |
| valid | 89 |
| train_novel | 8,554 |
| test | 3,080 |

### 2.3 로컬 TSV 데이터 로더 및 분할 함수 (`src/preprocessing.py`)
```python
import json
import csv
import os

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
        known_ratio: float   = 0.5,
        labeled_ratio: float = 0.1,
        max_length: int = 64,
        seed:int = 42,
        output_dir: str = 'outputs'
    ):

    ## GCD(Generalized Category Discovery)용 데이터셋 구성
    ##  - known_ratio   : train 클래스 중 known으로 사용할 클래스 비율
    ##  - labeled_ratio : known 클래스마다 라벨을 공개할 샘플 비율 (클래스별 층화)
    ##                    (이 중 80%는 train_known, 20%는 valid)
    ##  - 나머지 샘플(novel 클래스 + 라벨 미공개 known 샘플)은 train_novel

    ## 데이터 로드 (test 파일이 없으면 None)
    train_df = load_tsv_file(train_file_path)
    test_df  = load_tsv_file(test_file_path) \
                if test_file_path and os.path.exists(test_file_path) else None

    ## train/test label의 합집합 (정렬)
    label_series = [train_df['label']] if test_df is None \
                    else [train_df['label'], test_df['label']]
    all_labels = sorted(pd.concat(label_series).dropna().unique().tolist())

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


    num_classes = len(all_labels)
    rng = np.random.default_rng(seed)

    ## known 클래스는 train에 존재하는 클래스 중에서만 선택
    ## (test에만 있는 클래스는 항상 novel)
    train_classes    = sorted(train_df['label_idx'].unique().tolist())
    num_known        = int(len(train_classes) * known_ratio)
    shuffled_classes = rng.permutation(train_classes)

    known_classes = set(shuffled_classes[ :num_known].tolist())
    novel_classes = set(label2idx.values()) - known_classes

    ## known 클래스별 층화 분할: train_known / valid / train_novel
    ##  - 샘플 단위 난수 분할은 데이터가 적으면 valid가 비거나
    ##    특정 known 클래스의 라벨 샘플이 0개가 될 수 있어 클래스마다 개수를 정해서 뽑음
    ##  - 클래스당 labeled 최소 2개 -> train_known 1개 + valid 1개 보장
    label_idxs = train_df['label_idx'].to_numpy()
    train_known_idx, valid_idx = [], []
    for label_idx in sorted(known_classes):

        class_idx  = rng.permutation(np.flatnonzero(label_idxs == label_idx))
        num_label  = min(len(class_idx), max(2, round(len(class_idx) * labeled_ratio)))
        num_valid  = max(1, round(num_label * 0.2)) if num_label >= 2 else 0

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
    valid_set       = tokenize_df(train_df.loc[valid_idx])
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
```python
from transformers import BertModel
import torch.nn as nn
import torch


class BertForDeepAligned(nn.Module):

    def __init__(
            self,
            pretrained_model_name: str = 'bert-base-uncased',
            num_classes: int = None,
            feat_dim: int    = 768
        ):

        super().__init__()

        ## BERT 인코더 + Dense(Tanh) -> intent representation
        self.feat_dim = feat_dim
        self.bert     = BertModel.from_pretrained(pretrained_model_name)
        self.dense    = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, feat_dim),
            nn.Tanh()
        )

        ## num_classes가 없으면 분류 헤드 없이 feature만 사용
        self.classifier = nn.Linear(feat_dim, num_classes) \
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
- `estimate_cluster_num`: $K' = 2 \times$ expected_k로 k-Means 후, 평균 군집 크기($N/K'$) 미만인 군집을 제거하여 유효 $K$를 추정합니다.

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

### 3.3 세분화 평가 메트릭 (All / Known / Novel ACC, NMI, ARI) (`src/metrics.py`)
면접관이 가장 집중해서 보는 **All ACC, Known ACC, Novel ACC 분리 산출** 로직입니다.
전체 샘플에 대해 한 번의 헝가리안 매칭을 구한 뒤, 정답 클래스가 Known인지 Novel인지로 나누어 정확도를 계산합니다.
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

### 3.4 엔드투엔드 학습 매니저 (`src/trainer.py`)
```python
from torch.utils.data import DataLoader, TensorDataset
from sklearn.cluster import KMeans
import torch.nn.functional as F
import numpy as np
import torch

from .clustering import hungarian_align
from .metrics import compute_gcd_metrics


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


    def pretrain_step(self, train_known_loader, valid_loader = None, epochs: int = 5):

        ## Stage 1: known 클래스 라벨 데이터로 지도 학습 + known-only 검증
        print('\n=== [Stage 1] Supervised Pretraining on Known Labeled Data ===')

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
            if valid_loader is not None:
                valid_acc = self.evaluate_classifier(valid_loader)
                print(f'Epoch {epoch + 1}/{epochs} | Train Loss: {avg_loss:.4f} | Valid (Known) ACC: {valid_acc:.2f}%')

            else:
                print(f'Epoch {epoch + 1}/{epochs} | Train Loss: {avg_loss:.4f}')


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

## 4. 인터뷰 사전 과제 실행 및 제출 팁

### 4.1 프로젝트 폴더 구조
```text
gcd-baseline/
├── pyproject.toml              # uv 의존성, [tool.uv] package = false, pytest pythonpath
├── uv.lock
├── .python-version             # 3.11
├── README.md                   # 환경 구축, 문제 정의, 실행법, All/Known/Novel 결과표, 한계 분석
├── baseline.py                 # 엔드투엔드 단일 실행 진입점
├── dataset/                    # train.tsv / dev.tsv / test.tsv (헤더: text, label)
├── src/
│   ├── __init__.py
│   ├── config.py               # 디바이스 설정 (MPS -> CUDA -> CPU)
│   ├── preprocessing.py        # TSV 로드, label2idx.json, Known/Novel 분할, 클래스별 층화 labeled/valid
│   ├── models.py               # BertForDeepAligned 아키텍처 및 레이어 동결
│   ├── clustering.py           # 헝가리안 정렬(Hungarian Alignment), K 추정
│   ├── metrics.py              # All / Known / Novel ACC, NMI, ARI
│   ├── trainer.py              # Supervised Pretraining -> Deep Aligned Clustering 루프
│   └── utils.py                # 시드 고정, t-SNE 시각화
├── tests/
│   └── test_leakage.py         # 누수 방지 · 분할 무결성 테스트 (7개)
└── outputs/                    # 실행 결과 (.gitignore 대상)
    ├── label2idx.json
    └── plots/cluster_tsne.png
```

### 4.2 데이터 누수 방지 유닛 테스트 (`tests/test_leakage.py`)
가짜 tokenizer를 사용하므로 BERT 다운로드 없이 1초 안에 실행됩니다. 검증 항목은 다음과 같습니다.
- 헤더 줄이 `label` 클래스로 들어가지 않는지
- Known과 Novel 클래스가 겹치지 않고, 합치면 전체 클래스인지
- `train_known`과 `valid`에 Novel 클래스가 섞이지 않는지 (**타깃 누수 차단**)
- test에만 있는 클래스가 Novel로 들어가는지
- 모든 Known 클래스가 `train_known`과 `valid`에 각각 들어가는지 (층화 분할)
- 클래스당 샘플이 2개뿐이어도 시드 20개 모두 valid가 비지 않는지
- train 샘플이 세 분할 중 정확히 한 곳에만 들어가는지

```python
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


def test_splits_cover_train_once(tmp_path):

    ## train 샘플은 train_known / valid / train_novel 중 정확히 한 곳에만 들어가야 함
    data  = make_dataset(tmp_path)
    total = len(data['train_known']) + len(data['valid']) + len(data['train_novel'])
    assert total == 6 * 40
```

### 4.3 시드 고정 및 t-SNE 시각화 (`src/utils.py`)
과제 제출물에 t-SNE 시각화가 포함되면 분석의 깊이가 크게 돋보입니다. Known 클래스는 원(o), Novel 클래스는 삼각형(^)으로 그리고, 색은 정답 클래스를 따릅니다.
- 77개 클래스에서도 색이 구분되도록 흰색 계열이 없는 `turbo` colormap 사용 (`gist_ncar`는 끝 색이 흰색이라 한 클래스가 보이지 않았음)
- 범례 마커는 `Line2D`로 회색 고정 (scatter의 label을 쓰면 임의의 클래스 색이 범례에 찍힘)
- `matplotlib.use('Agg')`로 GUI 없이 파일로만 저장

```python
import random
import os

from sklearn.manifold import TSNE
import matplotlib
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

### 4.4 엔드투엔드 단일 실행 진입점 (`baseline.py`)
TSV 로드 → Known/Novel 분할 → 사전학습 → DAC 군집화 → All/Known/Novel 평가 → t-SNE 시각화를 한 번에 실행합니다.
```python
import argparse
import os

from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from src.preprocessing import prepare_gcd_dataset_from_tsv
from src.models import BertForDeepAligned
from src.trainer import DeepAlignedTrainer
from src.config import get_device
from src.utils import set_seed, plot_tsne


def parse_args():

    parser = argparse.ArgumentParser(description = 'DeepAligned GCD baseline')
    parser.add_argument('--train_file_path', type = str,   default = 'dataset/train.tsv')
    parser.add_argument('--test_file_path',  type = str,   default = 'dataset/test.tsv')
    parser.add_argument('--model_name',      type = str,   default = 'bert-base-uncased')
    parser.add_argument('--known_ratio',     type = float, default = 0.5)
    parser.add_argument('--labeled_ratio',   type = float, default = 0.1)
    parser.add_argument('--max_length',      type = int,   default = 64)
    parser.add_argument('--epochs_pretrain', type = int,   default = 5)
    parser.add_argument('--epochs_dac',      type = int,   default = 15)
    parser.add_argument('--batch_size',      type = int,   default = 64)
    parser.add_argument('--lr',              type = float, default = 5e-5)
    parser.add_argument('--lr_dac',          type = float, default = 1e-5)
    parser.add_argument('--output_dir',      type = str,   default = 'outputs')
    parser.add_argument('--seed',            type = int,   default = 42)
    return parser.parse_args()


def main():

    args = parse_args()

    ## 모델 초기화, DataLoader 셔플 등 PyTorch 난수까지 재현되도록 시드 고정
    set_seed(args.seed)
    device = get_device()
    print(f'[*] device: {device}')

    ## 1. 데이터셋 구성 (known / novel 분할)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    data      = prepare_gcd_dataset_from_tsv(
        tokenizer,
        train_file_path = args.train_file_path,
        test_file_path  = args.test_file_path,
        known_ratio     = args.known_ratio,
        labeled_ratio   = args.labeled_ratio,
        max_length      = args.max_length,
        seed            = args.seed,
        output_dir      = args.output_dir
    )

    num_classes   = data['num_classes']
    known_classes = data['known_classes']
    print(f'[*] classes: {num_classes} | known: {len(known_classes)} | novel: {len(data["novel_classes"])}')

    ## 2. DataLoader
    train_known_loader = DataLoader(data['train_known'], batch_size = args.batch_size, shuffle = True)
    train_novel_loader = DataLoader(data['train_novel'], batch_size = args.batch_size, shuffle = False)
    valid_loader       = DataLoader(data['valid'],       batch_size = args.batch_size, shuffle = False)

    ## test가 없으면 train_novel로 평가
    test_loader = DataLoader(data['test'], batch_size = args.batch_size, shuffle = False) \
                    if data['test'] is not None else train_novel_loader

    ## 3. 모델 (마지막 BERT 레이어만 학습)
    model = BertForDeepAligned(args.model_name, num_classes = num_classes)
    model.freeze_backbone_except_last_layer()

    trainer = DeepAlignedTrainer(model, device, lr = args.lr, seed = args.seed)

    ## 4. Stage 1: known 라벨 데이터로 지도 학습
    trainer.pretrain_step(train_known_loader, valid_loader, epochs = args.epochs_pretrain)

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

    ## 7. 잠재 공간 시각화 (t-SNE)
    if features is not None and y_true is not None:
        plot_path = os.path.join(args.output_dir, 'plots', 'cluster_tsne.png')
        plot_tsne(features, y_true, known_classes, save_path = plot_path, seed = args.seed)


if __name__ == '__main__':
    main()
```

### 4.5 실행 명령어 (`uv run`)
```bash
# 1) 데이터 누수 방지 유닛 테스트 (BERT 다운로드 불필요)
uv run pytest

# 2) 엔드투엔드 파이프라인 실행
uv run python baseline.py \
  --train_file_path dataset/train.tsv \
  --test_file_path dataset/test.tsv \
  --known_ratio 0.5 \
  --labeled_ratio 0.1 \
  --epochs_pretrain 5 \
  --epochs_dac 15 \
  --batch_size 64
```

### 4.6 모델 한계점 및 후속 개선 방향 (보고서/README 필수 항목)
보고서나 README에 아래 한계점과 극복 방안을 명시하면 높은 가산점을 받을 수 있습니다.
1. **k-Means의 등방성(Spherical) 군집 가정의 한계:**
   - Banking77과 같은 자연어 발화는 의도에 따라 분산과 밀도가 매우 불균일합니다. 유클리디안 거리 기반 k-Means는 동일한 분산의 구형 군집을 가정하므로, 롱테일 인텐트나 복합 의도에서 군집이 쪼개지거나 왜곡됩니다.
   - *개선안:* 밀도 기반 군집화(HDBSCAN) 또는 그래프 기반 $K$-최근접 이웃(KNN) 대조학습 도입.
2. **표상 학습(Feature Learning)과 군집화(Clustering)의 분리:**
   - 매 에포크 k-Means를 거쳐 이산적인(discrete) 의사 레이블을 생성하고 다시 분류기를 학습시키는 과정에서 오분류된 레이블의 확증 편향(Confirmation Bias)이 누적됩니다.
   - *개선안:* SimGCD처럼 파라메트릭 분류기(Softmax 프로토타입)를 도입하여 종단간(End-to-End) 학습으로 전환하거나, MTP-CLNN처럼 대조 학습으로 인코더를 정밀하게 사전 정렬.
3. **Stage 2 학습 데이터 범위:**
   - 현재 구현은 Stage 2(DAC)에서 `train_novel`(비라벨 데이터)만 클러스터링합니다. 원 논문 공식 구현은 labeled 데이터까지 포함한 train 전체를 클러스터링하는 것으로 알려져 있으나 직접 확인하지 않았습니다. README에 설계 선택으로 명시해 두는 것이 좋습니다.

### 4.7 면접 예상 질문 & 방어 논리 요약
1. **Q. Validation Set에 Novel 클래스를 넣지 않은 이유는 무엇인가요?**
   - *답변 논리:* GCD 문제의 기본 전제는 운영/배포 전까지 미지의 클래스를 모른다는 점입니다. Validation Set에 Novel 클래스를 포함시키면 하이퍼파라미터 튜닝 시 정답 Novel 분포에 오버피팅되는 **타깃 누수(Target Leakage/Cheating)**가 발생합니다. 따라서 실제 운영 환경과 동일하게 **Known 클래스로만 검증셋을 구성**하고, 기존 지식의 보존력(Known ACC)을 모니터링하여 체크포인트를 선정했습니다.
2. **Q. Known과 Novel의 비율은 왜 50:50으로 두었나요?**
   - *답변 논리:* 학계 표준 벤치마크(DeepAligned, USNID, SimGCD 등)와의 공정하고 객관적인 성능 비교를 위해 50%를 메인 베이스라인으로 채택했습니다. 사람이 임의로 라벨을 선정할 경우 체리피킹 위험이 있어 Random Uniform Split(Seed 고정)을 따랐습니다.
3. **Q. labeled / valid는 왜 클래스별로 층화 분할했나요?**
   - *답변 논리:* 샘플 단위 난수 분할은 데이터가 작거나 `labeled_ratio`가 작을 때 특정 Known 클래스의 labeled 샘플이 0개가 되거나 valid가 비는 문제가 생깁니다. 클래스마다 개수를 정해 뽑으면 모든 Known 클래스가 지도 학습과 검증에 반드시 포함되어, Known ACC가 일부 클래스에 치우치지 않습니다.
4. **Q. 매 에포크 k-Means를 수행하는 연산 병목은 어떻게 해결할 수 있나요?**
   - *답변 논리:* 데이터 규모가 커질 경우 `FAISS` GPU k-Means 라이브러리를 활용하거나, SimGCD처럼 프로토타입 기반 파라메트릭 헤드를 두어 k-Means 연산 자체를 제거하는 방향으로 경량화할 수 있습니다.

---

## 5. 구현 중 발견한 버그와 수정 이력

| 위치 | 문제 | 수정 |
|---|---|---|
| `load_tsv_file` | `header=None`으로 읽어 헤더 줄(`text`, `label`)이 데이터가 됨 → 가짜 `label` 클래스가 생겨 **78개 클래스**로 잡힘 | `header=0`으로 헤더 건너뜀 → 77개 정상 |
| `load_tsv_file` | 기본 quoting 때문에 문장 속 `"`에서 여러 줄이 합쳐지거나 컬럼이 밀림 | `quoting=csv.QUOTE_NONE`, `dtype=str` |
| `load_tsv_file` | 라벨이 빈 행이 남아 `torch.long` 변환 에러 | `dropna` + 빈 문자열 제거 |
| Known 클래스 선택 | 전체 라벨(train ∪ test)에서 뽑아 test 전용 클래스가 Known이 될 수 있음 → 라벨 데이터 0개 | train 라벨에서만 선택, test 전용은 항상 Novel |
| labeled / valid 분할 | 샘플 단위 난수 분할 → 작은 데이터에서 200개 시드 중 141개가 빈 valid | Known 클래스별 층화 분할 |
| 시드 | `np.random.seed` 전역 변경, PyTorch 시드 미고정 | `np.random.default_rng(seed)` + `set_seed()` |
| `pretrain_step` | `model.train()`이 루프 밖에 1번 → 검증 후 eval 모드 그대로 학습 (Dropout 꺼짐) | 매 에포크 시작 시 `model.train()` |
| `compute_gcd_metrics` | 혼동 행렬을 Python 루프로 생성 | `np.add.at`으로 벡터화 |
| `pyproject.toml` | uv_build가 `src/gcd_baseline/`를 요구해 `uv add` / `uv run` 실패 | `[tool.uv] package = false` |
| t-SNE | `gist_ncar` 끝 색이 흰색, 범례에 임의 클래스 색 표시 | `turbo` colormap, `Line2D` 회색 범례 |

---

## 관련 링크

- [[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트|DeepAligned 논문노트]]
- [[Learning/원문/2026-10-21-DeepAligned-원문|변환 원문 전문]]
- [[Learning/학습노트/2026-10-21-MTP-CLNN-사전학습-대조학습-인텐트발견-논문-노트|MTP-CLNN (ACL 2022)]]
- [[Learning/학습노트/2026-10-21-SimGCD-파라메트릭-분류-GCD-논문-노트|SimGCD (ICCV 2023)]]
- [[Learning/학습노트/index|학습노트 인덱스]]
