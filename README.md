# Minerva (Dove-Nest Knowledge Base)

김둘기(EvoDmiK)의 개인 엔지니어링 지식 베이스 및 홈랩 운영 볼트입니다.

Obsidian 스타일의 마크다운 노트로 관리되며, 노트 간에는 `[[위키링크]]`와 계층 태그(`#태그`)로 유기적으로 연결됩니다.  
Git 및 Webhook(Magpie, n8n, Obsidian Git)을 통해 Mac mini, MacBook, NAS, 모바일 환경 간 실시간 분산 동기화됩니다.

---

## 📂 저장소 구조

```
Minerva/
├── Home.md              # 볼트 전체 MOC (Map of Content) 메인 진입점
├── Inbox.md             # 빠른 캡처 메모장 및 인박스 대시보드
├── Inbox/               # 빠르게 캡처한 미정리 임시 메모 보관함
├── Dev/                 # 재사용 가능한 핵심 엔지니어링 상록수(Evergreen) 지식
│   ├── index.md         # Dev MOC 및 DEV-1xx~4xx 매핑 테이블
│   ├── 인프라/          # 네트워크, Cloudflare, Tailscale, SSL/TLS (DEV-1xx)
│   ├── 자동화/          # n8n 워크플로우 패턴, 안정성 설계, 웹훅 (DEV-2xx)
│   ├── 관측성/          # AI/LLM 토큰 모니터링, Loki, Grafana (DEV-3xx)
│   └── 데이터/          # Neo4j 지식그래프, Cypher, RDBMS 모델링 (DEV-4xx)
├── Work/                # 토이 프로젝트별 시계열 작업 일지 및 백로그
│   ├── index.md         # Work 전체 인덱스 및 활성 프로젝트 목록
│   ├── Birds-Nest/      # 홈랩 인프라·n8n 자동화·에이전트 게이트웨이 (BN-1xx~8xx)
│   ├── RobinGraph/      # 조류 지식 그래프·RAG·UI·배포 (RG-1xx~9xx)
│   ├── Gullinkambi/     # 모니터링·수집기·Grafana 대시보드 (GK-1xx~8xx)
│   └── Itzcuauhtli/     # Minerva 안전 읽기 전용 볼트 MCP 게이트웨이
├── Learning/            # 개인 학습, 독서 및 외부 자료 아카이브
│   ├── index.md         # Learning MOC
│   ├── 학습노트/        # 정제된 독서 및 스터디 노트
│   ├── 원문/            # 원문 텍스트 아카이브
│   └── 변환검증/        # 포맷 변환 및 검증 내역
├── scripts/             # 볼트 운영 유틸리티
│   └── distill_knowledge.py  # Work 일지에서 Dev 상록수 지식을 추출하는 CLI 도구
├── Templates/           # 새 노트 작성용 표준 템플릿 (Templater)
├── Attachments/         # 이미지 및 미디어 첨부 파일
└── Private/             # 로컬 전용 및 기밀 정보 (.gitignore 적용)
```

---

## 🏛️ 지식 거버넌스 및 운영 규칙

### 1. 작업 기록(Work)과 상록수 지식(Dev)의 분리
* **Work (`Work/<Project>/작업기록/`)**: 특정 시점, 특정 프로젝트 컨텍스트의 시계열 디버깅 로그, 배포 이력, 실험 과정을 가감 없이 기록합니다.
* **Dev (`Dev/<Domain>/`)**: Work 기록 중 다른 프로젝트나 미래의 나에게 반복해서 유용한 기술 패턴, 아키텍처 원칙, 재사용 스니펫을 추려내어 **독립적이고 영속적인 상록수 노트(Evergreen Note)**로 승격(Distill)합니다.
* **증류 자동화**: `scripts/distill_knowledge.py` 및 n8n 파이프라인([[Dev/자동화/n8n-지식-증류-워크플로우-작업-명세서|DEV-202]])을 통해 신규 작업 기록에서 자동으로 Dev 초안을 추천/생성합니다.

### 2. 표준 작업 백로그 ID 체계
* **RobinGraph**: `RG-1xx` ~ `RG-9xx`
* **Birds-Nest**: `BN-1xx` ~ `BN-8xx`
* **Gullinkambi**: `GK-1xx` ~ `GK-8xx`
* **Dev 상록수 지식**: `DEV-1xx` (인프라), `DEV-2xx` (자동화), `DEV-3xx` (관측성), `DEV-4xx` (데이터)

### 3. 인박스(Inbox) 처리 규칙
* 번뜩이는 아이디어와 임시 메모는 `Inbox.md` 또는 `Inbox/` 폴더에 즉시 캡처합니다.
* 주기적으로 인박스를 검토하여 적절한 영역(`Dev`, `Work`, `Learning`)으로 이동하고 인박스를 정리합니다.

### 4. 보안 및 커밋 가이드라인
* 이 저장소는 공개 저장소(Public Repository)입니다.
* API Key, Token, DB 비밀번호, SSH Private Key 및 회사/고용주 관련 민감 정보는 절대 커밋하지 않습니다.
* 모든 커밋 작성자는 `EvoDmiK <kimhippowork@gmail.com>`으로 통일합니다.
