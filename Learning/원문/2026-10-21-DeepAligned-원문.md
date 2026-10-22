---
date: 2026-10-21
created: 2026-10-21
collected: 2026-10-21
updated: 2026-10-22
document_role: source
tags: [learning, source, paper, nid, deepaligned]
paper_title: "Discovering New Intents with Deep Aligned Clustering"
paper_date: 2020-12-16
paper_id: "arXiv:2012.08987v7"
source_url: "https://arxiv.org/abs/2012.08987"
primary_text: "https://arxiv.org/html/2012.08987v7"
source_role: primary
capture_scope: "arXiv:2012.08987v7 HTML 전문 변환 (markdown-converter / MarkItDown)"
converter: "markdown-converter (markitdown via arXiv HTML)"
learning_notes:
  - "[[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트]]"
---
# Discovering New Intents with Deep Aligned Clustering

> [!info] 원문 보관 범위
> arXiv:2012.08987v7 HTML 원본을 `markdown-converter`(MarkItDown)를 통해 변환한 원문 전문입니다.
> 변환 검증은 논문 주장에 대한 사실 검증이나 실험 재현을 뜻하지 않습니다.

**Authors:** Hanlei Zhang, Hua Xu, Ting-En Lin, Rui Lyu (Tsinghua University & Beijing University of Posts and Telecommunications)  
**Venue:** AAAI 2021 (Main Track, Long Paper)  
**Code:** https://github.com/thuiar/DeepAligned-Clustering  
**arXiv:** https://arxiv.org/abs/2012.08987 (v7)

## 관련 링크

- [[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트|한국어 정리]]
- [[Learning/원문/index|원문 인덱스]]

---

# Discovering New Intents with Deep Aligned Clustering

Hanlei Zhang

Hua Xu

Ting-En Lin
††thanks: Hua Xu is the corresponding author.

Rui Lyu

###### Abstract

Discovering new intents is a crucial task in dialogue systems. Most existing methods are limited in transferring the prior knowledge from known intents to new intents. They also have difficulties in providing high-quality supervised signals to learn clustering-friendly features for grouping unlabeled intents. In this work, we propose an effective method, Deep Aligned Clustering, to discover new intents with the aid of the limited known intent data. Firstly, we leverage a few labeled known intent samples as prior knowledge to pre-train the model. Then, we perform k-means to produce cluster assignments as pseudo-labels. Moreover, we propose an alignment strategy to tackle the label inconsistency problem during clustering assignments. Finally, we learn the intent representations under the supervision of the aligned pseudo-labels. With an unknown number of new intents, we predict the number of intent categories by eliminating low-confidence intent-wise clusters. Extensive experiments on two benchmark datasets show that our method is more robust and achieves substantial improvements over the state-of-the-art methods. The codes are released at https://github.com/thuiar/DeepAligned-Clustering.

1State Key Laboratory of Intelligent Technology and Systems,

Department of Computer Science and Technology, Tsinghua University, Beijing 100084, China,

2 Beijing National Research Center for Information Science and Technology (BNRist), Beijing 100084, China

3 Beijing University of Posts and Telecommunications University, Beijing 100876, China

zhang-hl20@mails.tsinghua.edu.cn, xuhua@tsinghua.edu.cn, ting-en.lte@alibaba-inc.com, lvrui2017@bupt.edu.cn

## Introduction

Discovering novel user intents is important to improve the service quality in dialogue systems. By analyzing the discovered new intents, we may find underlying user interests, which could provide business opportunities and guide the improvement direction ([Lin and Xu 2019](#bib.bib20)).

Intent discovery has attracted much attention in recent years ([Perkins and Yang 2019](#bib.bib26); [Min et al. 2020](#bib.bib23); [Vedula et al. 2020](#bib.bib32)). Many researchers regard it as an unsupervised clustering problem, and they manage to incorporate some weak supervised signals to guide the clustering process. For example, [Hakkani-Tür et al. (2013)](#bib.bib13) propose a hierarchical semantic clustering model and collect web page clicked information as implicit supervision for intent discovery. [Hakkani-Tür et al. (2015)](#bib.bib12) utilize a semantic parsing graph as extra knowledge to mine novel intents during clustering. [Padmasundari and Bangalore (2018)](#bib.bib24) benefit from the consensus predictions of multiple clustering techniques to discover similar semantic intent-wise clusters. [Haponchyk et al. (2018)](#bib.bib15) cluster questions into user intent categories under the supervision of structured outputs. [Shi et al. (2018)](#bib.bib31) extract intent features with an autoencoder and automatically label the intents with a hierarchical clustering method.

Figure 1:  An example for our task. We use limited known intent labeled data as a guide to discover new intents.

Figure 2: The model architecture of our approach. Firstly, we extract intent features with BERT. We pre-train the model under the supervision of few labeled samples, and predict the cluster number KK if we do not know in advance. Then, we perform k-means to produce cluster centroids and use cluster assignments as pseudo-labels. Next, we align the obtained centroids in the current training epoch {cic}i=1K\{c\_{i}^{c}\}\_{i=1}^{K} with the saved centroids in the last epoch {cil}i=1K\{c\_{i}^{l}\}\_{i=1}^{K}, and produce the alignment projection GG. Finally, we use GG on the pseudo-labels to produce the aligned labels for self-supervised learning.

However, all of the above methods fail to leverage the prior knowledge of known intents. These methods assume that the unlabeled samples are only composed of undiscovered new intents. A more common case is that some labeled data of known intents are accessible and the unlabeled data are mixed with both known and new intents. As illustrated in Figure [1](#Sx1.F1 "Figure 1 ‣ Introduction ‣ Discovering New Intents with Deep Aligned Clustering"), we may have a few labeled samples (e.g., with a labeled proportion of 10%) of known intents in advance. The remaining known and new intent samples are all unlabeled. Our goal is to find known intents and discover new intents with the prior knowledge of limited labeled data. Our previous work CDAC+ ([Lin, Xu, and Zhang 2020](#bib.bib21)) directly tackles this problem. Nevertheless, it uses pairwise similarities as weak supervised signals, which are ambiguous to distinguish a mixture of unlabeled known and new intents. Thus, the performance drops with more new intents.

To summarize, there are two main difficulties in our task. On the one hand, it is challenging to effectively transfer the prior knowledge from known intents to new intents with limited labeled data. On the other hand, it is hard to construct high-quality supervised signals to learn friendly representations for clustering both unlabeled known and new intents.

To solve these problems, we propose an effective method to leverage the limited prior knowledge of known intents and provide high-quality supervised signals for feature learning. As illustrated in Figure [2](#Sx1.F2 "Figure 2 ‣ Introduction ‣ Discovering New Intents with Deep Aligned Clustering"), we firstly use the pre-trained BERT model ([Devlin et al. 2019](#bib.bib7)) to extract deep intent features. Then, we pre-train the model with the limited labeled data under the supervision of the softmax loss. We retain the pre-trained parameters and use the learning information to obtain well-initialized intent representations. Next, we perform clustering on the extracted intent features and estimate the cluster number KK (unknown beforehand) by eliminating the low-confidence clusters.

As most of the training samples are unlabeled, we propose an original alignment strategy to construct high-quality pseudo-labels as supervised signals for learning discriminative intent features. For each training epoch, we firstly perform k-means on the extracted intent features, and then use the produced cluster assignments as pseudo-labels for training the neural network. However, the inconsistent assigned labels cannot be directly used as supervised signals, so we use the cluster centroids as the targets to obtain the alignment mapping between pseudo-labels in consequent epochs. Finally, we perform k-means again for inference. Benefit from the relatively consistent aligned targets, our method can inherit the history learning information and boost the clustering performance.

We summarize our contributions as follows. Firstly, we propose a simple and effective method that successfully generalizes to mass of new intents and estimate the number of novel classes with limited prior knowledge of known intents. Secondly, we propose an effective alignment strategy to obtain high-quality self-supervised signals by learning discriminative features to distinguish both known and new intents. Finally, extensive experiments on two benchmark datasets show our approach yields better and more robust results than the state-of-the-art methods.

## Related Work

### Intent Modeling

Many researchers try modeling user intents in dialogue systems in recent years. A line for these works is to enrich the intent information jointly with other tasks, such as sentiment classification ([Qin et al. 2020](#bib.bib28)), slot filling ([Qin et al. 2019](#bib.bib29); [Goo et al. 2018](#bib.bib9); [Wang, Shen, and Jin 2018](#bib.bib34)) and so on. Another line is to
leverage hidden semantic information to construct supervised signals for intent feature learning ([Shi et al. 2018](#bib.bib31); [Brychcin and Král 2017](#bib.bib3); [Hakkani-Tür et al. 2013](#bib.bib13)). In this work, we follow the second line to model intents.

### Unsupervised Clustering

There are many classical unsupervised clustering methods, such as partition-based methods ([MacQueen et al. 1967](#bib.bib22)), hierarchical methods ([Gowda and Krishna 1978](#bib.bib11)) and density-based methods ([Ester et al. 1996](#bib.bib8)). However, the high-dimensional pattern representations suffer from high computational complexity and poor performance. Though some feature dimensionality reduction ([Gowda 1984](#bib.bib10)) and data transformation methods ([Wold, Esbensen, and Geladi 1987](#bib.bib35)) have been proposed, these methods still can not capture high-level semantics of intent features ([Lin and Xu 2019](#bib.bib20)).

#### Deep Clustering

With the development of deep learning, researchers adopt deep neural networks (DNNs) to extract friendly features for clustering. The joint unsupervised learning (JULE) ([Yang, Parikh, and Batra 2016](#bib.bib39)) combines deep feature learning with hierarchical clustering but needs huge computational and memory cost on large-scale datasets. Deep Embedded Clustering (DEC) ([Xie, Girshick, and Farhadi 2016](#bib.bib37)) trains the autoencoder with the reconstruction loss and iteratively refines the cluster centers by optimizing KL-divergence with an auxiliary target distribution. Compared with DEC, Deep Clustering Network (DCN) ([Yang et al. 2017](#bib.bib38)) further introduces a k-means loss as the penalty term to reconstruct the clustering loss. Deep Adaptive Image Clustering (DAC) ([Chang et al. 2017](#bib.bib6)) utilizes the pairwise similarities as the learning targets and adopts an adaptive learning algorithm to select samples for training. However, all these clustering methods cannot provide specific supervised signals for representation learning.

DeepCluster ([Caron et al. 2018](#bib.bib4)) benefits from the structured outputs to boost the discriminative power of the convolutional neural network (CNN). It alternately performs k-means and representation learning. It considers the cluster assignments as pseudo-labels, which are explicit supervised signals for grouping each class. However, it needs to reinitialize the classifier parameters randomly before each training epoch. To deal with this issue, we propose an alignment strategy to produce aligned pseudo-labels for self-supervised learning without reinitialization.

### Semi-supervised Clustering

Although there are various unsupervised clustering methods, the performances of these methods are still limited without the prior knowledge for guiding the clustering process. Therefore, researchers perform semi-supervised clustering with the aid of some labeled data.

Classical constrained clustering methods use the pairwise information as constraints for guiding the representation learning and clustering process. COP-KMeans ([Wagstaff et al. 2001](#bib.bib33)) uses instance-level constraints (must-link and cannot-link) and modifies k-means to satisfy these constraints. PCK-means ([Basu, Banerjee, and Mooney 2004](#bib.bib1)) presents a framework for pairwise constrained clustering, and it further selects informative pairwise constraints with an active learning method. MPCK-means ([Bilenko, Basu, and Mooney 2004](#bib.bib2)) incorporates the metric-learning approach into PCK-means and combined the centroid-based methods and metric-based methods into a unified framework. However, these methods need huge computational cost by enumerating pairwise conditions.

KCL ([Hsu, Lv, and Kira 2018](#bib.bib16)) uses deep neural networks to perform pairwise constraint clustering. It firstly trains an extra network for binary similarity classification with a labeled auxiliary dataset. Then, it transfers the prior knowledge of pairwise similarity to the target dataset and uses KL-divergence to evaluate the pairwise distance. MCL ([Hsu et al. 2019](#bib.bib17)) uses the meta classification likelihood as the criterion to learn pairwise similarities. However, the domain adaptation methods are still limited in our task. CDAC+ ([Lin, Xu, and Zhang 2020](#bib.bib21)) is specifically designed for discovering new intents. It uses limited labeled data as a guide to learn pairwise similarities. However, it is limited in providing specific supervised signals and fails to estimate the number of novel classes. DTC ([Han, Vedaldi, and Zisserman 2019](#bib.bib14)) is a method for discovering novel classes in computer vision. It improves the DEC algorithm and transfers the knowledge of labeled data to estimate the number of novel classes. However, the amount of the labeled data has a great influence on its performance.

| Dataset | #Classes (Known + Unknown) | #Training | #Validation | #Test | Vocabulary | Length (max / mean) |
| --- | --- | --- | --- | --- | --- | --- |
| CLINC | 150 (113 + 37) | 18,000 | 2,250 | 2,250 | 7,283 | 28 / 8.31 |
| BANKING | 77 (58 + 19) | 9,003 | 1,000 | 3,080 | 5,028 | 79 / 11.91 |

Table 1:  Statistics of CLINC and BANKING datasets. # indicates the total number of sentences. In each run of the experiment, we randomly select 75% intents as known intents. Taking the CLINC dataset as an example, we randomly select 113 known intents and treat the remaining 37 intents as new intents.
