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
capture_scope: "DeepAligned Mac uv 파이프라인 구현·Known/Novel 분할 및 누수 방지 프로토콜·All/Known/Novel 분리 평가 메트릭·헝가리안 정렬 전체 코드·인터뷰 사전 과제 실행 가이드"
paper_notes:
  - "[[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트]]"
source_notes:
  - "[[Learning/원문/2026-10-21-DeepAligned-원문]]"
---
# DeepAligned 파이프라인 구현 및 Mac uv 실행 가이드 (인터뷰 과제 대비)

> [!abstract] 개요
> 본 문서는 **DeepAligned (AAAI 2021)** 알고리즘을 Apple Silicon Mac 환경에서 `uv` 기반으로 직접 구현하고 재현하기 위한 **엔드투엔드 파이프라인 코드 및 엔지니어링 가이드**입니다.
> 공식 레포의 구형 레거시 종속성(`pytorch-pretrained-bert`)을 모던 `transformers`와 `torch`로 리팩터링하고, 인터뷰 사전 과제 평가에서 핵심 검토 대상인 **① 학계 표준 Known/Novel 분할 및 타깃 누수(Target Leakage) 방지 프로토콜**, **② Known-only 검증셋(Validation) 구축**, **③ All / Known / Novel 세분화 헝가리안 매칭 평가 지표**, **④ 모델 한계점 및 후속 개선 방향**을 완전하게 보완하여 정리했습니다.

---

## 1. 개발 환경 구성 (Mac Apple Silicon & uv)

### 1.1 공식 레포 종속성 문제와 해결책
* **공식 레포(`thuiar/DeepAligned-Clustering`)의 한계:**
  - 2020~2021년에 작성되어 Python 3.6, PyTorch 1.7.0, 구형 `pytorch-pretrained-bert` 패키지에 고정되어 있습니다.
  - Mac arm64 환경에서는 컴파일 휠이 없어 `pip install -r requirements.txt` 실행 시 빌드 에러가 발생하며, AWS S3 버킷 만료로 BERT 가중치 자동 다운로드가 실패합니다.
* **해결책:**
  - Python 3.10 기반 `uv` 가상환경 구성
  - 모던 `transformers (>=4.30.0)` 및 최신 `torch`로 리팩터링
  - Apple Silicon GPU 가속(`mps`) 디바이스 자동 감지 적용

### 1.2 uv 가상환경 구축 명령어
```bash
# 1) 프로젝트 디렉터리 생성 및 이동
mkdir -p deepaligned-nid && cd deepaligned-nid

# 2) Python 3.10 기반 uv 가상환경 생성
uv venv --python 3.10
source .venv/bin/activate

# 3) 핵심 딥러닝 및 데이터 처리 패키지 설치
uv pip install torch torchvision
uv pip install transformers datasets
uv pip install scikit-learn scipy numpy pandas tqdm matplotlib
```

### 1.3 디바이스 자동 설정 (MPS / CUDA / CPU)
```python
import torch

def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")
```

---

## 2. 데이터 분할 및 타깃 누수 방지 프로토콜

인터뷰 사전 과제에서 가장 엄격하게 평가받는 부분은 **데이터셋 분할의 정당성과 데이터 누수(Data Leakage) 차단 여부**입니다.

### 2.1 Known / Novel 클래스 선정 기준
- **학계 표준 무작위 분할 (Uniform Random Split - 메인 베이스라인):**
  - 특정 도메인 편향이나 체리피킹을 배제하기 위해 고정된 시드(예: Seed 42, 0, 1)로 클래스 목록을 셔플한 뒤 분할합니다.
  - **Known 비율**: 통상 50% (38개 Known / 39개 Novel)를 메인 벤치마크로 사용하며, 필요시 25%와 75%를 비교군으로 둡니다.
- **실무 분석용 대안 기준 (Ablation / 심화 분석용):**
  - **도메인 계층(Prefix) 분할**: `card_*`, `transfer_*` 등 세부 의미 경계(Fine-grained) 분별력 검증.
  - **출현 빈도(Frequency) 분할**: 헤드(다빈도) 클래스를 Known, 롱테일(희귀) 클래스를 Novel로 두어 현실적 배포 환경 모사.

### 2.2 엄격한 데이터셋 분할 규칙
1. **Train Labeled ($\mathcal{D}_l$):**
   - Known 클래스 샘플 중 **10%**만 샘플링하여 초기 표현 학습(Supervised Pretraining)에 사용합니다.
2. **Train Unlabeled ($\mathcal{D}_u$):**
   - Known 클래스 샘플의 **나머지 90%** + Novel 클래스 샘플 **100%**를 병합합니다.
   - 레이블을 제거한 상태로 Deep Aligned Clustering 루프(k-Means + 헝가리안 정렬 재학습)에 투입합니다.
3. **Validation ($\mathcal{D}_{val}$):**
   - **절대 Novel 클래스 데이터가 포함되어서는 안 됩니다.**
   - Known Labeled 데이터 중 일부(예: 10~20%)를 떼어내어 검증셋으로 구성합니다.
   - *이유: 검증셋에 Novel 데이터가 유출되면 하이퍼파라미터 튜닝 시 미지의 클래스 분포에 사후 최적화(Target Leakage/Cheating)가 발생하여 GCD 문제 정의가 훼손됩니다.*
4. **Test ($\mathcal{D}_{test}$):**
   - 공식 Test 세트 전체(3,080개)를 사용하며, 사후 평가 시 Known과 Novel 마스크를 적용해 분리 평가합니다.

### 2.3 로컬 TSV 데이터 로더 및 분할 함수 구현 (`src/data.py`)
```python
import os
import csv
import json
import numpy as np
import pandas as pd
import torch
from torch.utils.data import TensorDataset

def load_tsv_file(file_path):
    """
    로컬 TSV 파일을 읽어 text와 label 컬럼을 정규화하여 반환합니다.
    - quoting=csv.QUOTE_NONE: 발화 내 쌍따옴표(")로 인한 멀티라인 병합 및 컬럼 밀림 방지
    - dtype=str: 숫자형 라벨 시 .str.strip() AttributeError 방지
    - dropna(subset=["text", "label"]): 결측치 행 사전 제거로 NaN 텐서 변환 에러 차단
    """
    df = pd.read_csv(file_path, sep="\t", quoting=csv.QUOTE_NONE, dtype=str)
    
    col_mapping = {
        "utterance": "text", "query": "text", "sentence": "text",
        "intent": "label", "category": "label", "class": "label"
    }
    df = df.rename(columns={c: col_mapping[c.lower()] for c in df.columns if c.lower() in col_mapping})
    
    if "text" not in df.columns or "label" not in df.columns:
        df = pd.read_csv(file_path, sep="\t", header=None, names=["text", "label"],
                         quoting=csv.QUOTE_NONE, dtype=str)
        
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip()
    df = df[(df["text"] != "") & (df["label"] != "")].reset_index(drop=True)
    return df

def prepare_gcd_dataset_from_tsv(
    tokenizer,
    train_path,
    test_path=None,
    known_ratio=0.5,
    labeled_ratio=0.1,
    max_length=64,
    seed=42,
    output_dir="outputs"
):
    """
    로컬 TSV 파일을 로드하여 GCD 데이터셋(Known/Novel 분할, Known-only Val)으로 구성합니다.
    - Known 클래스는 train 라벨에서만 추출 (test 전용 클래스가 known이 되어 라벨이 0개가 되는 현상 방지)
    - np.random.default_rng(seed) 격리 난수 발생기 사용 (전역 시드 오염 방지)
    - 불리언 마스크 기반 벡터화 인덱싱 (iterrows 연산 병목 제거)
    - 빈 validation subset 발생 시 방어 예외 처리
    - 정확한 GCD 용어: train_unlabeled (Known 비라벨 + Novel 전량 병합 풀)
    """
    rng = np.random.default_rng(seed)
    
    train_df = load_tsv_file(train_path)
    test_df = load_tsv_file(test_path) if test_path and os.path.exists(test_path) else None
    
    # 1) 전체 고유 라벨 수집 및 일관된 Label2ID 생성
    train_unique_labels = sorted(train_df["label"].unique())
    all_labels = list(train_unique_labels)
    if test_df is not None:
        test_only_labels = sorted(set(test_df["label"].unique()) - set(train_unique_labels))
        all_labels.extend(test_only_labels)
        
    label2id = {label: i for i, label in enumerate(all_labels)}
    id2label = {i: label for label, i in label2id.items()}
    
    # 사후 분석 및 라벨 복원을 위해 label2id.json 저장
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "label2id.json"), "w", encoding="utf-8") as f:
        json.dump(label2id, f, ensure_ascii=False, indent=2)
        
    train_df["label_id"] = train_df["label"].map(label2id).astype(int)
    if test_df is not None:
        test_df["label_id"] = test_df["label"].map(label2id).astype(int)
        
    num_total_classes = len(all_labels)
    
    # 2) [버그 수정] Known 클래스는 반드시 train 데이터셋에 실제 존재하는 라벨에서만 추첨
    train_label_ids = sorted(train_df["label_id"].unique())
    num_known = int(len(train_label_ids) * known_ratio)
    shuffled_train_classes = rng.permutation(train_label_ids)
    known_classes = set(shuffled_train_classes[:num_known])
    novel_classes = set(c_id for c_id in label2id.values() if c_id not in known_classes)
    
    # 3) [성능 개선] 벡터화 마스킹 분할 (iterrows 병목 제거)
    is_known = train_df["label_id"].isin(known_classes)
    r = rng.random(len(train_df))
    
    train_labeled_idx = train_df.index[is_known & (r < labeled_ratio * 0.8)]
    val_idx = train_df.index[is_known & (r >= labeled_ratio * 0.8) & (r < labeled_ratio)]
    train_unlabeled_idx = train_df.index[~train_df.index.isin(train_labeled_idx.union(val_idx))]
    
    # 4) [방어 코드] 빈 subset 예외 처리
    if len(val_idx) == 0:
        raise ValueError(
            f"Validation set이 비어있습니다. labeled_ratio({labeled_ratio})가 너무 작거나 "
            f"Known 샘플 수가 부족합니다. labeled_ratio를 높이거나 분할 비율을 조정하세요."
        )
    if len(train_labeled_idx) == 0:
        raise ValueError("Train Labeled set이 비어있습니다. known_ratio 또는 labeled_ratio를 확인하세요.")
        
    # 5) 토큰화 및 TensorDataset 변환
    def encode_df(df_subset):
        texts = df_subset["text"].tolist()
        labels = df_subset["label_id"].tolist()
        enc = tokenizer(texts, padding="max_length", truncation=True, max_length=max_length, return_tensors="pt")
        return TensorDataset(enc["input_ids"], enc["attention_mask"], torch.tensor(labels, dtype=torch.long))

    train_labeled_set = encode_df(train_df.loc[train_labeled_idx])
    train_unlabeled_set = encode_df(train_df.loc[train_unlabeled_idx])
    val_set = encode_df(train_df.loc[val_idx])
    test_set = encode_df(test_df) if test_df is not None else None

    return {
        "train_labeled": train_labeled_set,
        "train_unlabeled": train_unlabeled_set,
        "val": val_set,
        "test": test_set,
        "known_classes": known_classes,
        "novel_classes": novel_classes,
        "label2id": label2id,
        "id2label": id2label,
        "num_total_classes": num_total_classes
    }
```

---

## 3. 핵심 파이프라인 구현 코드

### 3.1 모델 아키텍처 (BERT + Mean Pooling + Dense Layer) (`src/models.py`)
```python
import torch
import torch.nn as nn
from transformers import BertModel

class BertForDeepAligned(nn.Module):
    def __init__(self, pretrained_model_name="bert-base-uncased", num_classes=None, feat_dim=768):
        super().__init__()
        self.feat_dim = feat_dim
        self.bert = BertModel.from_pretrained(pretrained_model_name)
        self.dense = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, feat_dim),
            nn.Tanh()
        )
        # [개선] num_classes 동적 할당 지원 (로컬 TSV 클래스 수에 유연하게 대응)
        self.classifier = nn.Linear(feat_dim, num_classes) if num_classes is not None else None

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        # Mean Pooling over token embeddings (패딩 토큰 제외 평균 풀링)
        token_embeddings = outputs.last_hidden_state  # [B, L, H]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        mean_pooled = sum_embeddings / sum_mask  # [B, H]
        
        # Intent Representation 추출
        features = self.dense(mean_pooled)  # [B, feat_dim]
        logits = self.classifier(features) if self.classifier is not None else None  # [B, num_classes]
        return features, logits

    def reinit_classifier(self, num_classes):
        """
        [버그 차단] Stage 2 클러스터링 정렬 학습 시 클러스터 수(K)에 맞추어 분류 헤드 재할당
        - num_clusters != num_classes 일 때의 IndexError 및 CUDA/MPS assertion crash 원천 방지
        """
        device = next(self.parameters()).device
        self.classifier = nn.Linear(self.feat_dim, num_classes).to(device)

    def freeze_backbone_except_last_layer(self):
        """BERT 하위 레이어 동결 (Mac Apple Silicon에서의 학습 속도 향상 및 사전학습 표상 보존)"""
        for name, param in self.bert.named_parameters():
            if "encoder.layer.11" not in name and "pooler" not in name:
                param.requires_grad = False
```

### 3.2 헝가리안 정렬 (Hungarian Alignment) 모듈
```python
import numpy as np
from scipy.optimize import linear_sum_assignment

def hungarian_align(current_centroids, prev_centroids, current_labels):
    """
    이전 에포크의 클러스터 중심점(prev_centroids)과 
    현재 에포크의 클러스터 중심점(current_centroids) 간의 1:1 최적 매핑을 찾아
    현재 의사 라벨(current_labels)을 정렬합니다.
    """
    if prev_centroids is None:
        return current_labels, current_centroids

    # 1) 유클리디안 비용 행렬 M_ij = ||c_i_curr - c_j_prev||_2
    cost_matrix = np.linalg.norm(
        current_centroids[:, None, :] - prev_centroids[None, :, :], axis=2
    )  # [K, K]

    # 2) 헝가리안 이분 매칭 최적화 (O(K^3))
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    mapping = {curr_idx: prev_idx for curr_idx, prev_idx in zip(row_ind, col_ind)}
    
    # 3) 현재 라벨 및 중심점 재정렬
    aligned_labels = np.array([mapping[l] for l in current_labels])
    aligned_centroids = np.zeros_like(current_centroids)
    for curr_idx, prev_idx in mapping.items():
        aligned_centroids[prev_idx] = current_centroids[curr_idx]
        
    return aligned_labels, aligned_centroids
```

### 3.3 클래스 개수 ($K$) 자동 추정기
```python
from sklearn.cluster import KMeans

def estimate_cluster_num(features, max_k_factor=2, true_k=77, random_state=42):
    """
    K' = 2 * K 로 설정하여 k-Means를 수행한 뒤, 
    평균 군집 크기 (N / K') 미만의 저신뢰도 군집을 제거하여 유효 K를 추정
    """
    k_prime = int(true_k * max_k_factor)
    kmeans = KMeans(n_clusters=k_prime, n_init=10, random_state=random_state).fit(features)
    cluster_sizes = np.bincount(kmeans.labels_, minlength=k_prime)
    
    threshold = len(features) / k_prime  # 평균 군집 크기
    estimated_k = int(np.sum(cluster_sizes >= threshold))
    return max(estimated_k, 2)
```

### 3.4 세분화 평가 메트릭 (All / Known / Novel ACC, NMI, ARI)
면접관이 가장 집중해서 보는 **All ACC, Known ACC, Novel ACC 분리 산출** 로직입니다.
```python
from sklearn.metrics import normalized_mutual_info_score as NMI
from sklearn.metrics import adjusted_rand_score as ARI

def compute_gcd_metrics(y_true, y_pred, known_classes):
    """
    헝가리안 최적 할당 후 All / Known / Novel ACC 및 NMI, ARI를 산출합니다.
    
    Args:
        y_true: Ground Truth 정답 레이블 (np.ndarray, [N])
        y_pred: 모델이 예측한 군집 클러스터 ID (np.ndarray, [N])
        known_classes: Known 클래스 ID들의 set 혹은 list
    """
    y_true = np.array(y_true, dtype=np.int64)
    y_pred = np.array(y_pred, dtype=np.int64)
    assert y_pred.size == y_true.size
    
    # 1) 전체 샘플에 대한 혼동 행렬(Cost Matrix) 구축 및 헝가리안 최적 매칭
    D = max(y_pred.max(), y_true.max()) + 1
    w = np.zeros((D, D), dtype=np.int64)
    for i in range(y_pred.size):
        w[y_pred[i], y_true[i]] += 1
        
    # 최대 일치를 위한 linear_sum_assignment (비용 최소화 문제로 변환)
    row_ind, col_ind = linear_sum_assignment(w.max() - w)
    pred_to_true_map = {r: c for r, c in zip(row_ind, col_ind)}
    mapped_preds = np.array([pred_to_true_map.get(p, -1) for p in y_pred])
    
    # 2) All ACC 계산
    correct_mask = (mapped_preds == y_true)
    all_acc = np.mean(correct_mask) * 100.0
    
    # 3) Known / Novel 마스크 기반 분리 ACC 계산
    known_mask = np.isin(y_true, list(known_classes))
    novel_mask = ~known_mask
    
    known_acc = np.mean(correct_mask[known_mask]) * 100.0 if np.sum(known_mask) > 0 else 0.0
    novel_acc = np.mean(correct_mask[novel_mask]) * 100.0 if np.sum(novel_mask) > 0 else 0.0
    
    # 4) 비지도 군집 평가 지표 (NMI, ARI)
    nmi_score = NMI(y_true, y_pred) * 100.0
    ari_score = ARI(y_true, y_pred) * 100.0
    
    return {
        "All_ACC": round(all_acc, 2),
        "Known_ACC": round(known_acc, 2),
        "Novel_ACC": round(novel_acc, 2),
        "NMI": round(nmi_score, 2),
        "ARI": round(ari_score, 2)
    }
```

### 3.5 엔드투엔드 학습 매니저 (Trainer Loop with Validation)
```python
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

class DeepAlignedTrainer:
    def __init__(self, model, device, lr=5e-5):
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()), lr=lr
        )
        self.prev_centroids = None

    def extract_features(self, dataloader):
        self.model.eval()
        all_feats, all_labels = [], []
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)
                feats, _ = self.model(input_ids, attention_mask)
                all_feats.append(feats.cpu().numpy())
                if len(batch) > 2:
                    all_labels.append(batch[2].numpy())
        all_feats = np.concatenate(all_feats, axis=0)
        all_labels = np.concatenate(all_labels, axis=0) if all_labels else None
        return all_feats, all_labels

    def pretrain_step(self, train_labeled_loader, val_loader, epochs=5):
        """1단계: Known 라벨 데이터로 표현 초기화 및 Known-only 검증"""
        print("\n=== [Stage 1] Supervised Pretraining on Known Labeled Data ===")
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0.0
            for batch in train_labeled_loader:
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                self.optimizer.zero_grad()
                _, logits = self.model(input_ids, attention_mask)
                loss = F.cross_entropy(logits, labels)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            
            # Validation (Known Accuracy 측정)
            val_acc = self.evaluate_classifier(val_loader)
            print(f"Epoch {epoch+1}/{epochs} | Train Loss: {total_loss/len(train_labeled_loader):.4f} | Val (Known) ACC: {val_acc:.2f}%")

    def evaluate_classifier(self, dataloader):
        self.model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for batch in dataloader:
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                _, logits = self.model(input_ids, attention_mask)
                preds = torch.argmax(logits, dim=-1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
        return (correct / total) * 100.0 if total > 0 else 0.0

    def cluster_and_align(self, all_features, num_clusters):
        """2단계: k-Means 수행 및 헝가리안 정렬"""
        kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=42).fit(all_features)
        current_centroids = kmeans.cluster_centers_
        current_labels = kmeans.labels_

        aligned_labels, self.prev_centroids = hungarian_align(
            current_centroids, self.prev_centroids, current_labels
        )
        return aligned_labels

    def train_aligned_clustering(self, train_unlabeled_loader, num_clusters, epochs=15, batch_size=128):
        """3단계: Deep Aligned Clustering 에포크 루프"""
        print("\n=== [Stage 2] Deep Aligned Clustering on Unlabeled Data ===")
        input_ids_all = train_unlabeled_loader.dataset.tensors[0]
        attention_mask_all = train_unlabeled_loader.dataset.tensors[1]
        
        for epoch in range(epochs):
            # 1) 전체 특징 추출
            eval_loader = DataLoader(
                TensorDataset(input_ids_all, attention_mask_all), batch_size=batch_size, shuffle=False
            )
            features, _ = self.extract_features(eval_loader)
            
            # 2) 군집화 및 헝가리안 정렬
            aligned_labels = self.cluster_and_align(features, num_clusters)
            
            # 3) 정렬된 의사 라벨로 데이터로더 재구성 후 재학습
            train_dataset = TensorDataset(
                input_ids_all, attention_mask_all, torch.tensor(aligned_labels, dtype=torch.long)
            )
            train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
            
            self.model.train()
            total_loss = 0.0
            for batch in train_loader:
                b_ids, b_mask, b_pseudo = [b.to(self.device) for b in batch]
                self.optimizer.zero_grad()
                _, logits = self.model(b_ids, b_mask)
                loss = F.cross_entropy(logits, b_pseudo)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
                
            print(f"[DAC] Epoch {epoch+1}/{epochs} | Clustering Loss: {total_loss/len(train_loader):.4f}")

    def evaluate_test(self, test_loader, num_clusters, known_classes):
        """최종 테스트 세트 평가 (All / Known / Novel 메트릭 리포트)"""
        print("\n=== [Final Evaluation] Test Set Metrics ===")
        features, y_true = self.extract_features(test_loader)
        
        # 테스트 세트 특성에 대해 최종 k-Means 군집화 수행
        kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=42).fit(features)
        y_pred = kmeans.labels_
        
        metrics = compute_gcd_metrics(y_true, y_pred, known_classes)
        print("Final Results:", metrics)
        return metrics
```

---

## 4. 인터뷰 사전 과제 실행 및 제출 팁

### 4.1 권장 프로젝트 폴더 구조 (모듈러 & 단일 실행 지원)
면접관이 코드를 클론받아 바로 파악하고 재현할 수 있도록, **모듈화된 표준 구조**와 **원클릭 실행 스크립트**를 함께 구성하는 것이 가장 이상적입니다.

```text
deepaligned-nid/
├── pyproject.toml              # uv 기반 의존성 및 프로젝트 메타데이터 (PEP 621)
├── README.md                   # 환경 구축, 문제 정의, 실행법, All/Known/Novel 실험 결과표, 한계 분석
├── deepaligned_pipeline.py     # 면접관의 빠른 재현을 위한 엔드투엔드 단일 스크립트
├── configs/                    # 하이퍼파라미터 및 실행 설정
│   └── default.yaml            # known_ratio(0.5), labeled_ratio(0.1), seed, lr, epochs 등
├── src/                        # 핵심 모듈
│   ├── __init__.py
│   ├── data.py                 # 로컬 TSV 로드, Label Encoding(label2id.json), Known/Novel 50:50 분할, Known-only Val 구축
│   ├── models.py               # BertForDeepAligned 아키텍처 및 레이어 동결
│   ├── clustering.py           # k-Means, 헝가리안 정렬(Hungarian Alignment), K 추정
│   ├── metrics.py              # All / Known / Novel ACC, NMI, ARI 분리 산출
│   ├── trainer.py              # Supervised Pretraining -> Deep Aligned Clustering 루프
│   └── utils.py                # 디바이스 설정(MPS/CUDA), 시드 고정, 로깅
├── tests/                      # [가산점] 데이터 무결성 및 누수 방지 테스트
│   └── test_leakage.py         # Val에 Novel 클래스가 없는지, Unlabeled/Labeled 분할 검증
└── outputs/                    # 실행 결과 저장 디렉터리 (.gitignore 대상)
    ├── checkpoints/            # 학습된 모델 가중치 (.pt)
    ├── logs/                   # 에포크별 Loss 및 성능 로그
    └── plots/                  # t-SNE 잠재공간 시각화 이미지 (cluster_tsne.png)
```

### 4.2 단일 스크립트 실행 (`uv run`)
```bash
# 로컬 TSV 기반 50% Known 세팅 단일 실행
uv run python deepaligned_pipeline.py \
  --train_path data/train.tsv \
  --test_path data/test.tsv \
  --known_ratio 0.5 \
  --labeled_ratio 0.1 \
  --epochs_pretrain 5 \
  --epochs_dac 15 \
  --batch_size 64
```

### 4.2 정성적 분석 및 시각화 (t-SNE)
과제 제출물에 t-SNE 시각화가 포함되면 분석의 깊이가 크게 돋보입니다. Known 클래스와 Novel 클래스를 시각적으로 구분하여 표상 분리도를 보여줄 수 있습니다.
```python
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

def plot_tsne(features, labels, known_classes, save_path="cluster_tsne.png"):
    tsne = TSNE(n_components=2, random_state=42)
    embeds_2d = tsne.fit_transform(features)
    
    plt.figure(figsize=(10, 8))
    # Known 클래스는 원형(o), Novel 클래스는 삼각형(^)으로 구분 표시
    is_known = np.isin(labels, list(known_classes))
    
    plt.scatter(embeds_2d[is_known, 0], embeds_2d[is_known, 1], c=labels[is_known], 
                cmap="tab20", marker="o", s=15, alpha=0.6, label="Known")
    plt.scatter(embeds_2d[~is_known, 0], embeds_2d[~is_known, 1], c=labels[~is_known], 
                cmap="tab20", marker="^", s=25, alpha=0.8, edgecolor="black", linewidth=0.5, label="Novel")
    
    plt.title("DeepAligned Latent Space (Known vs Novel)")
    plt.legend()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

### 4.3 모델 한계점 및 후속 개선 방향 (보고서/README 필수 항목)
보고서나 README에 아래 한계점과 극복 방안을 명시하면 높은 가산점을 받을 수 있습니다.
1. **k-Means의 등방성(Spherical) 군집 가정의 한계:**
   - Banking77과 같은 자연어 발화는 의도에 따라 분산과 밀도가 매우 불균일합니다. 유클리디안 거리 기반 k-Means는 동일한 분산의 구형 군집을 가정하므로, 롱테일 인텐트나 복합 의도에서 군집이 쪼개지거나 왜곡됩니다.
   - *개선안:* 밀도 기반 군집화(HDBSCAN) 또는 그래프 기반 $K$-최근접 이웃(KNN) 대조학습 도입.
2. **표상 학습(Feature Learning)과 군집화(Clustering)의 분리:**
   - 매 에포크 k-Means를 거쳐 이산적인(discrete) 의사 레이블을 생성하고 다시 분류기를 학습시키는 과정에서 오분류된 레이블의 확증 편향(Confirmation Bias)이 누적됩니다.
   - *개선안:* SimGCD처럼 파라메트릭 분류기(Softmax 프로토타입)를 도입하여 종단간(End-to-End) 학습으로 전환하거나, MTP-CLNN처럼 대조 학습으로 인코더를 정밀하게 사전 정렬.

### 4.4 면접 예상 질문 & 방어 논리 요약
1. **Q. Validation Set에 Novel 클래스를 넣지 않은 이유는 무엇인가요?**
   - *답변 논리:* GCD 문제의 기본 전제는 운영/배포 전까지 미지의 클래스를 모른다는 점입니다. Validation Set에 Novel 클래스를 포함시키면 하이퍼파라미터 튜닝 시 정답 Novel 분포에 오버피팅되는 **타깃 누수(Target Leakage/Cheating)**가 발생합니다. 따라서 실제 운영 환경과 동일하게 **Known 클래스로만 검증셋을 구성**하고, 기존 지식의 보존력(Known ACC)을 모니터링하여 체크포인트를 선정했습니다.
2. **Q. Known과 Novel의 비율은 왜 50:50으로 두었나요?**
   - *답변 논리:* 학계 표준 벤치마크(DeepAligned, USNID, SimGCD 등)와의 공정하고 객관적인 성능 비교를 위해 50%를 메인 베이스라인으로 채택했습니다. 사람이 임의로 라벨을 선정할 경우 체리피킹 위험이 있어 Random Uniform Split(Seed 고정)을 따랐습니다.
3. **Q. 매 에포크 k-Means를 수행하는 연산 병목은 어떻게 해결할 수 있나요?**
   - *답변 논리:* 데이터 규모가 커질 경우 `FAISS` GPU k-Means 라이브러리를 활용하거나, SimGCD처럼 프로토타입 기반 파라메트릭 헤드를 두어 k-Means 연산 자체를 제거하는 방향으로 경량화할 수 있습니다.

---

## 관련 링크

- [[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트|DeepAligned 논문노트]]
- [[Learning/원문/2026-10-21-DeepAligned-원문|변환 원문 전문]]
- [[Learning/학습노트/2026-10-21-MTP-CLNN-사전학습-대조학습-인텐트발견-논문-노트|MTP-CLNN (ACL 2022)]]
- [[Learning/학습노트/2026-10-21-SimGCD-파라메트릭-분류-GCD-논문-노트|SimGCD (ICCV 2023)]]
- [[Learning/학습노트/index|학습노트 인덱스]]