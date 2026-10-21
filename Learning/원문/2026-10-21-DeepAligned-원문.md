---
date: 2026-10-21
created: 2026-10-21
collected: 2026-10-21
document_role: source
tags: [learning, source, paper, nid, deepaligned]
paper_title: "Discovering New Intents with Deep Aligned Clustering"
paper_date: 2020-12-16
paper_id: "arXiv:2012.08987v7"
source_url: "https://arxiv.org/abs/2012.08987"
primary_text: "https://arxiv.org/html/2012.08987v7"
source_role: primary
capture_scope: "초록 및 서론(HTML 발췌 원문), 전문 복제 아님"
converter: "web_extract / HTML"
learning_notes:
  - "[[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트]]"
---
# Discovering New Intents with Deep Aligned Clustering

> [!info] 원문 보관 범위
> arXiv HTML을 통해 수집한 저자, 초록 및 서론 핵심 원문 텍스트입니다.
> 변환 검증은 논문 주장에 대한 사실 검증이나 실험 재현을 뜻하지 않습니다.

**Authors:** Hanlei Zhang, Hua Xu, Ting-En Lin, Rui Lyu (Tsinghua University & Beijing University of Posts and Telecommunications)  
**Venue:** AAAI 2021 (Main Track, Long Paper)  
**Code:** https://github.com/thuiar/DeepAligned-Clustering

## Abstract
Discovering new intents is a crucial task in dialogue systems. Most existing methods are limited in transferring the prior knowledge from known intents to new intents. They also have difficulties in providing high-quality supervised signals to learn clustering-friendly features for grouping unlabeled intents. In this work, we propose an effective method, Deep Aligned Clustering, to discover new intents with the aid of the limited known intent data. Firstly, we leverage a few labeled known intent samples as prior knowledge to pre-train the model. Then, we perform k-means to produce cluster assignments as pseudo-labels. Moreover, we propose an alignment strategy to tackle the label inconsistency problem during clustering assignments. Finally, we learn the intent representations under the supervision of the aligned pseudo-labels. With an unknown number of new intents, we predict the number of intent categories by eliminating low-confidence intent-wise clusters. Extensive experiments on two benchmark datasets show that our method is more robust and achieves substantial improvements over the state-of-the-art methods.

## Introduction (Excerpt)
Discovering novel user intents is important to improve the service quality in dialogue systems. By analyzing the discovered new intents, we may find underlying user interests, which could provide business opportunities and guide the improvement direction. Many researchers regard it as an unsupervised clustering problem, and they manage to incorporate some weak supervised signals to guide the clustering process. However, all of the above methods fail to leverage the prior knowledge of known intents. A more common case is that some labeled data of known intents are accessible and the unlabeled data are mixed with both known and new intents...

## 관련

- [[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트|한국어 정리]]
- [[Learning/원문/index|원문 인덱스]]
