---
created: 2026-10-20
updated: 2026-10-20
type: reference
category: "인프라"
status: draft
source_project: "RobinGraph"
source_work_log: "[[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-10-dev-main-병합]]"
tags:
  - dev
  - draft
  - "robingraph"
---

# dev → main 병합 — 2026-10-10

> 자동 증류 초안 · 원천 [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-10-dev-main-병합]] · 분류 근거 {"인프라":4,"자동화":0,"관측성":0,"데이터":0}

## 1. 개요 및 목적

사용자가 오늘 수정한 내용을 main 브랜치에 병합하도록 요청했다. 이미 TEST와 Production에서 검증한 카드 수정, 그 근거 및 배포 기록을 기본 브랜치에서도 확인할 수 있도록 한다. 새로운 기능 구현이나 서버 재배포 요청은 아니다.

현재 작업 공간은 dev이며 main은 `/Volumes/Dove-Nest-SSD/projects/RobinGraph`의 기존 worktree에서 체크아웃되어 있었다. 두 작업 공간의 git status가 깨끗함을 확인했다. `git fetch origin` 후 main과 origin/main은 동일했고, main에만 있는 커밋 0개·dev에만 있는 커밋 15개였다. 따라서 충돌 해결이나 커밋 재작성 없이 fast-forward가 가능한 상태였다.

## 2. 핵심 아키텍처 및 원칙

- 요청과 목표
- 병합 전 확인과 범위
- 실제 수행과 결과
- 검증 범위와 구분
- 배포·한계·문서 보관

## 3. 재사용 가능한 코드 스니펫 / 설정

_원천 문서에 코드 블록 없음_

## 4. 검증 근거 및 트러블슈팅

사용자가 오늘 수정한 내용을 main 브랜치에 병합하도록 요청했다. 이미 TEST와 Production에서 검증한 카드 수정, 그 근거 및 배포 기록을 기본 브랜치에서도 확인할 수 있도록 한다. 새로운 기능 구현이나 서버 재배포 요청은 아니다.

현재 작업 공간은 dev이며 main은 `/Volumes/Dove-Nest-SSD/projects/RobinGraph`의 기존 worktree에서 체크아웃되어 있었다. 두 작업 공간의 git status가 깨끗함을 확인했다. `git fetch origin` 후 main과 origin/main은 동일했고, main에만 있는 커밋 0개·dev에만 있는 커밋 15개였다. 따라서 충돌 해결이나 커밋 재작성 없이 fast-forward가 가능한 상태였다.

- 카드 뒷면 토글을 열어도 카드 배율·너비가 유지되도록 수정한 `05ebc61`.
- 토글에 따른 소재 빛 무늬 이동을 막는 `a7f5e63`, 소재 레이어를 카드 안으로 자르고 반복 경계를 없앤 `3ac07e2`.
- 운영 이미지 승격과 실제 PC/모바일·픽셀 검증 기록 `5aee641` 및 관련 상세 문서·검증 JSON.
- 이전 카드 사진 확대·모바일 비율 자료 박스 정렬 `a2c8bcc`, 보전 등급 출처 연결 및 전종 검토 변경과 운영 DB 이관 기록.

전체 범위는 69개 파일이며 대다수 추가 줄은 검증 JSON이다. 인증 정보·환경 파일은 이번 병합에 새로 추가하지 않았다.

`git push origin main` 성공 후 `git ls-remote origin refs/heads/main refs/heads/dev`로 원격 두 브랜치가 모두 `5aee641ff1b64cc654ea02001fb94774a0e98747`임을 확인했다. 병합 직후 두 브랜치 tree ID는 `08b76734af59f224cf7a5b22096140e21e9c6184`로 동일했다. `git diff --check HEAD`도 통과했다.

## 5. 관련 Dev 가이드

- 원천 작업기록 [[Work/RobinGraph/작업기록/8xx 문서·개발환경/2026-10-10-dev-main-병합]]
- [[Dev/index|Dev 인덱스]]
