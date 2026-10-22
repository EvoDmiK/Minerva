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

### 2.3 데이터 전처리 및 분할 함수 구현
```python
import numpy as np
from datasets import load_dataset
from torch.utils.data import TensorDataset

def prepare_gcd_dataset(tokenizer, dataset_name="banking77", known_ratio=0.5, labeled_ratio=0.1, max_length=64, seed=42):
    """
    Banking77 데이터셋을 학계 표준 GCD 프로토콜에 따라 분할합니다.
    - Known / Novel 클래스 무작위 분할
    - Known 클래스 내 Labeled / Unlabeled 분할 (Labeled Ratio 10%)
    - Known-only 검증셋 구축 (Target Leakage 차단)
    """
    raw_datasets = load_dataset(dataset_name)
    train_data = raw_datasets["train"]
    test_data = raw_datasets["test"]
    
    unique_labels = sorted(list(set(train_data["label"])))
    num_total_classes = len(unique_labels)
    
    np.random.seed(seed)
    num_known = int(num_total_classes * known_ratio)
    shuffled_labels = np.random.permutation(unique_labels)
    known_classes = set(shuffled_labels[:num_known])
    novel_classes = set(shuffled_labels[num_known:])
    
    # 1) Train 데이터 분할 인덱스 생성
    train_labeled_idx, train_unlabeled_idx, val_idx = [], [], []
    
    for idx, sample in enumerate(train_data):
        label = sample["label"]
        if label in known_classes:
            rand_val = np.random.rand()
            if rand_val < labeled_ratio * 0.8: # 8%는 학습용 Labeled
                train_labeled_idx.append(idx)
            elif rand_val < labeled_ratio:     # 2%는 Known-only Validation
                val_idx.append(idx)
            else:                              # 90%는 Unlabeled 풀
                train_unlabeled_idx.append(idx)
        else:
            # Novel 클래스는 100% Unlabeled 풀로 진입
            train_unlabeled_idx.append(idx)
            
    # 2) 토큰화 헬퍼
    def encode_samples(indices, dataset_split):
        texts = [dataset_split[i]["text"] for i in indices]
        labels = [dataset_split[i]["label"] for i in indices]
        enc = tokenizer(texts, padding="max_length", truncation=True, max_length=max_length, return_tensors="pt")
        return TensorDataset(enc["input_ids"], enc["attention_mask"], torch.tensor(labels, dtype=torch.long))

    train_labeled_set = encode_samples(train_labeled_idx, train_data)
    train_unlabeled_set = encode_samples(train_unlabeled_idx, train_data)
    val_set = encode_samples(val_idx, train_data)
    test_set = encode_samples(range(len(test_data)), test_data)
    
    return {
        "train_labeled": train_labeled_set,
        "train_unlabeled": train_unlabeled_set,
        "val": val_set,
        "test": test_set,
        "known_classes": known_classes,
        "novel_classes": novel_classes,
        "num_total_classes": num_total_classes
    }
```

---

## 3. 핵심 파이프라인 구현 코드

### 3.1 모델 아키텍처 (BERT + Mean Pooling + Dense Layer)
```python
import torch
import torch.nn as nn
from transformers import BertModel

class BertForDeepAligned(nn.Module):
    def __init__(self, pretrained_model_name="bert-base-uncased", num_classes=77, feat_dim=768):
        super().__init__()
        self.bert = BertModel.from_pretrained(pretrained_model_name)
        self.dense = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size, feat_dim),
            nn.Tanh()
        )
        self.classifier = nn.Linear(feat_dim, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        # Mean Pooling over token embeddings
        token_embeddings = outputs.last_hidden_state  # [B, L, H]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        mean_pooled = sum_embeddings / sum_mask  # [B, H]
        
        # Intent Representation
        features = self.dense(mean_pooled)  # [B, feat_dim]
        logits = self.classifier(features)  # [B, num_classes]
        return features, logits

    def freeze_backbone_except_last_layer(self):
        """BERT 하위 레이어를 동결하여 Mac에서의 학습 속도 및 수렴 안정화"""
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

### 4.1 단일 스크립트 실행 (`uv run`)
```bash
# 기본 50% Known 세팅 단일 실행
uv run python deepaligned_pipeline.py \
  --dataset banking77 \
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
- [[Learning/학습노트/2026-10-21-SimGCD-파라메트릭-분류-카테고리-발견-논문-노트|SimGCD (ICCV 2023)]]
- [[Learning/학습노트/index|학습노트 인덱스]]