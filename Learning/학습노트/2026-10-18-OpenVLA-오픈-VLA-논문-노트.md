---
date: 2026-10-18
document_role: learning-note
note_kind: summary
language: ko
paper_title: "OpenVLA: An Open-Source Vision-Language-Action Model"
paper_year: 2024
arxiv: "2406.09246"
source_url: https://arxiv.org/abs/2406.09246
primary_text: https://arxiv.org/html/2406.09246v3
source_role: primary
capture_scope: "원논문 v3의 모델·데이터·제약 요약, 전문 복제 아님"
tags: [robotics, vla, openvla, open-source]
---

# OpenVLA — 공개 VLA와 목표 로봇 환경 적응

## 한 줄 요약

사전학습 VLM을 다중 로봇 시연으로 학습해, 직접 제어와 새로운 로봇 설정으로의 fine-tuning에 사용할 수 있도록 공개한 VLA다. [1, §3–5]

## 확인된 핵심

- 7B Llama 2와 DINOv2·SigLIP 시각 특징을 결합하며, Open X-Embodiment의 약 97만 로봇 시연으로 학습한다. [1, Abstract·§3]
- 각 행동 차원을 256개 구간으로 토큰화한다. 구간 범위는 학습 데이터의 1–99 백분위수로 설정한다. [1, §3.2]
- VLM의 웹 사전학습에서 시작한다는 사실과, 로봇 학습 중 웹 과제를 함께 넣는 co-training은 다른 조건이다. [1, §3·6]

## π0.5와 연결되는 이유

둘 다 VLM을 로봇 정책으로 전환하지만, OpenVLA는 공개 모델의 제어·적응 경로를, π0.5는 이종 감독과 모바일 조작 일반화를 읽는 비교 대상으로 삼기 좋다. 이는 연구 초점에 관한 해석이며 보편적 성능 순위가 아니다.

## 비교 해석과 한계

원논문 모델은 단일 이미지 관측만 지원한다. 다중 이미지·고유수용감각·관측 이력과 고주파 제어는 확장 과제로 남긴다. 후속 변형의 action chunking 등을 원모델 기능으로 소급하지 않는다. [1, §6]

## 연결된 노트

- [[Learning/학습노트/2026-10-17-pi05-논문-핵심-내용-한국어-정리|π0.5]] — 공동학습 구성과 일반화 목표 비교.
- [[Learning/학습노트/2026-10-18-RT-2-웹지식-로봇제어-논문-노트|RT-2]] — VLM 행동 토큰화 비교.
- [[Learning/학습노트/2026-10-18-Octo-다중로봇-정책-논문-노트|Octo]] — 다중 로봇 데이터 활용과 목표 환경 적응 비교.
- [[Learning/학습노트/2026-10-18-FAST-행동-토큰화-논문-노트|FAST]] — 차원별 토큰과 압축된 행동 구간 토큰 비교.
- [[Learning/학습노트/2026-10-18-pi05-관련-논문-연결지도|관련 논문 연결지도]]

## 근거

1. [OpenVLA 논문 v3](https://arxiv.org/html/2406.09246v3), §3·5·6.
2. [π0.5 논문 v1](https://arxiv.org/html/2504.16054v1), Abstract·§IV.

논문 실험이나 현재 코드의 기능을 직접 재현·점검한 기록은 아니다.
