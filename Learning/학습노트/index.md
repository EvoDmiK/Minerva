---
date: 2026-10-21
created: 2026-10-21
updated: 2026-10-22
document_role: index
title: "학습노트 인덱스"
tags: [learning, index]
---
# 학습노트 인덱스

> [!info] 안내
> [[Learning/원문/index|원문]]을 바탕으로 핵심 구조, 수식, 벤치마크, 실무 적용점을 한국어로 분석·정리한 학습노트 모음입니다.

```dataview
TABLE date as "작성일", paper_title as "논문 제목", tags as "태그"
FROM "Learning/학습노트"
WHERE document_role = "learning-note"
SORT file.name DESC
```

## 최근 학습노트

- [[Learning/학습노트/2026-10-22-DeepAligned-Mac-uv-파이프라인-구현-노트|DeepAligned: Mac uv 파이프라인 구현 및 인터뷰 과제 실행 가이드]]
- [[Learning/학습노트/2026-10-21-SimGCD-파라메트릭-분류-카테고리-발견-논문-노트|SimGCD: Parametric Classification for Generalized Category Discovery (ICCV 2023)]]
- [[Learning/학습노트/2026-10-21-MTP-CLNN-사전학습-대조학습-인텐트발견-논문-노트|MTP-CLNN: Multi-Task Pre-training with Contrastive Learning for Novel Intent Discovery (ACL 2022)]]
- [[Learning/학습노트/2026-10-21-GCD-Vaze-일반화-카테고리-발견-논문-노트|Generalized Category Discovery (Vaze et al., CVPR 2022)]]
- [[Learning/학습노트/2026-10-21-DeepAligned-신규-인텐트-발견-논문-노트|DeepAligned: Deep Aligned Clustering for New Intent Discovery (AAAI 2021)]]

## 관련 인덱스

- [[Learning/원문/index|원문 인덱스]]
- [[Learning/index|Learning 인덱스]]
- [[Home]]
