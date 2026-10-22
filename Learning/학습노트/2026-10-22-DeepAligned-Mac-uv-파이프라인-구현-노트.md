---
date: 2026-10-22
created: 2026-10-22
updated: 2026-10-22
document_role: learning-note
note_kind: implementation-guide
language: ko
tags: [learning, implementation, deepaligned, mac, uv, pytorch, nlp, banking77]
paper_title: "Discovering New Intents with Deep Aligned Clustering"
paper_date: 2020-12-16
paper_id: "arXiv:2012.08987v7"
source_url: "https://arxiv.org/abs/2012.08987"
primary_text: "https://arxiv.org/html/2012.08987v7"
source_role: primary
capture_scope: "DeepAligned Mac uv 파이프라인 구현·PyTorch/MPS 패치·헝가리안 정렬 전체 코드·인터뷰 사전 과제 실행 가이드"
paper_notes:
  - "[[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트]]"
source_notes:
  - "[[Learning/원문/2026-10-21-DeepAligned-원문]]"
---
# DeepAligned 파이프라인 구현 및 Mac uv 실행 가이드 (인터뷰 과제 대비)

> [!abstract] 개요
> 본 문서는 **DeepAligned (AAAI 2021)** 알고리즘을 Apple Silicon Mac 환경에서 `uv` 기반으로 직접 구현하고 재현하기 위한 **엔드투엔드 파이프라인 코드 및 엔지니어링 가이드**입니다.
> 공식 레포의 구형 레거시 종속성(`pytorch-pretrained-bert`)을 모던 `transformers`와 `torch`로 리팩터링하고, 인터뷰 사전 과제 제출에 적합한 깔끔한 모듈러 구조로 정리했습니다.

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
uv pip install scikit-learn scipy numpy pandas tqdm
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

## 2. 핵심 파이프라인 구현 코드

인터뷰 과제 제출에 맞게 단일 또는 모듈러 스크립트(`deepaligned_pipeline.py`)로 바로 동작할 수 있는 완전한 코드베이스입니다.

### 2.1 모델 아키텍처 (BERT + Mean Pooling + Dense Layer)
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

### 2.2 헝가리안 정렬 (Hungarian Alignment) 모듈
```python
import numpy as np
from scipy.optimize import linear_sum_assignment

def hungarian_align(current_centroids, prev_centroids, current_labels):
    """
    이전 에포크의 클러스터 중심점(prev_centroids)과 
    현재 에포크의 클러스터 중심점(current_centroids) 간의 1:1 최적 매핑을 찾아
    현재 의사 라벨(current_labels)을 정렬합니다.
    
    Args:
        current_centroids: np.ndarray [K, D]
        prev_centroids: np.ndarray [K, D]
        current_labels: np.ndarray [N]
    Returns:
        aligned_labels: np.ndarray [N]
        aligned_centroids: np.ndarray [K, D]
    """
    if prev_centroids is None:
        return current_labels, current_centroids

    # 1) 유클리디안 비용 행렬 M_ij = ||c_i_curr - c_j_prev||_2
    cost_matrix = np.linalg.norm(
        current_centroids[:, None, :] - prev_centroids[None, :, :], axis=2
    )  # [K, K]

    # 2) 헝가리안 이분 매칭 최적화 (O(K^3))
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    # row_ind[i]번째 현재 클러스터가 col_ind[i]번째 이전 클러스터에 대응됨
    # 매핑 딕셔너리 생성
    mapping = {curr_idx: prev_idx for curr_idx, prev_idx in zip(row_ind, col_ind)}
    
    # 3) 현재 라벨 재정렬
    aligned_labels = np.array([mapping[l] for l in current_labels])
    
    # 4) 중심점 순서 정렬
    aligned_centroids = np.zeros_like(current_centroids)
    for curr_idx, prev_idx in mapping.items():
        aligned_centroids[prev_idx] = current_centroids[curr_idx]
        
    return aligned_labels, aligned_centroids
```

### 2.3 클래스 개수 ($K$) 자동 추정기
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

### 2.4 평가 메트릭 (Clustering ACC, NMI, ARI)
```python
from sklearn.metrics import normalized_mutual_info_score as NMI
from sklearn.metrics import adjusted_rand_score as ARI

def clustering_accuracy(y_true, y_pred):
    """헝가리안 매칭 기반 무작위 군집 인덱스를 Ground Truth와 매핑하여 ACC 산출"""
    y_true = np.array(y_true, dtype=np.int64)
    y_pred = np.array(y_pred, dtype=np.int64)
    assert y_pred.size == y_true.size
    
    D = max(y_pred.max(), y_true.max()) + 1
    w = np.zeros((D, D), dtype=np.int64)
    for i in range(y_pred.size):
        w[y_pred[i], y_true[i]] += 1
        
    ind = linear_sum_assignment(w.max() - w)
    return sum([w[i, j] for i, j in zip(*ind)]) * 1.0 / y_pred.size

def compute_metrics(y_true, y_pred):
    return {
        "ACC": round(clustering_accuracy(y_true, y_pred) * 100, 2),
        "NMI": round(NMI(y_true, y_pred) * 100, 2),
        "ARI": round(ARI(y_true, y_pred) * 100, 2)
    }
```

### 2.5 엔드투엔드 학습 매니저 (Trainer Loop)
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
        all_feats = []
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)
                feats, _ = self.model(input_ids, attention_mask)
                all_feats.append(feats.cpu().numpy())
        return np.concatenate(all_feats, axis=0)

    def pretrain_step(self, dataloader, epochs=5):
        """1단계: Known 라벨 데이터로 표현 초기화"""
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0.0
            for batch in dataloader:
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                self.optimizer.zero_grad()
                _, logits = self.model(input_ids, attention_mask)
                loss = F.cross_entropy(logits, labels)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            print(f"[Pretrain] Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(dataloader):.4f}")

    def cluster_and_align(self, all_features, num_clusters):
        """2단계: k-Means 수행 및 헝가리안 정렬"""
        kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=42).fit(all_features)
        current_centroids = kmeans.cluster_centers_
        current_labels = kmeans.labels_

        aligned_labels, self.prev_centroids = hungarian_align(
            current_centroids, self.prev_centroids, current_labels
        )
        return aligned_labels

    def train_aligned_clustering(self, input_ids_all, attention_mask_all, num_clusters, epochs=15, batch_size=128):
        """3단계: Deep Aligned Clustering 에포크 루프"""
        eval_loader = DataLoader(
            TensorDataset(input_ids_all, attention_mask_all), batch_size=batch_size, shuffle=False
        )
        
        for epoch in range(epochs):
            # 1) 전체 특징 추출
            features = self.extract_features(eval_loader)
            
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
                
            print(f"[DAC] Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(train_loader):.4f}")
```

---

## 3. 인터뷰 사전 과제 실행 및 제출 팁

### 3.1 단일 스크립트 실행 (`uv run`)
```bash
# 단일 시드 빠른 동작 검증
uv run python deepaligned_pipeline.py \
  --dataset banking77 \
  --known_ratio 0.75 \
  --epochs 10 \
  --batch_size 64
```

### 3.2 정성적 분석 및 시각화 (t-SNE)
과제 제출물에 t-SNE 시각화가 포함되면 분석의 깊이가 크게 돋보입니다.
```python
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

def plot_tsne(features, labels, save_path="cluster_tsne.png"):
    tsne = TSNE(n_components=2, random_state=42)
    embeds_2d = tsne.fit_transform(features)
    plt.figure(figsize=(10, 8))
    plt.scatter(embeds_2d[:, 0], embeds_2d[:, 1], c=labels, cmap="tab20", s=10, alpha=0.7)
    plt.title("DeepAligned Feature Space t-SNE")
    plt.colorbar()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

### 3.3 면접 예상 질문 & 방어 논리 요약
1. **Q. k-Means는 구형 군집만 가정하는데, 실제 인텐트 데이터의 불균일한 분산은 어떻게 처리하나?**
   - *답변 논리:* DeepAligned는 k-Means 자체를 바꾸기보다, **신경망 인코더(BERT)의 표현 공간을 k-Means가 분리하기 쉬운 구형 등방성 공간으로 역으로 변형**시키는 방식을 취합니다. 다만 복합 의도(Multi-intent)나 극단적 긴 꼬리 분포에서는 왜곡이 생기므로, 후속 개선안으로 밀도 기반 군집화(HDBSCAN)나 MTP-CLNN식 대조학습 $K$-NN 그래프를 도입하는 것이 이상적입니다.
2. **Q. 매 에포크 k-Means를 돌리는 병목을 실무에서 어떻게 개선할 것인가?**
   - *답변 논리:* CPU k-Means 대신 `FAISS` GPU k-Means를 사용하거나, SimGCD처럼 클러스터 중심점을 학습 가능한 파라메트릭 분류 헤드로 치환하여 전체 k-Means 단계를 제거할 수 있습니다.

---

## 관련 링크

- [[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트|DeepAligned 논문노트]]
- [[Learning/원문/2026-10-21-DeepAligned-원문|변환 원문 전문]]
- [[Learning/학습노트/2026-10-21-MTP-CLNN-사전학습-대조학습-인텐트발견-논문-노트|MTP-CLNN (ACL 2022)]]
- [[Learning/학습노트/2026-10-21-SimGCD-파라메트릭-분류-카테고리-발견-논문-노트|SimGCD (ICCV 2023)]]
- [[Learning/학습노트/index|학습노트 인덱스]]
