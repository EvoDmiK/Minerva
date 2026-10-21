---
created: 2026-10-14
updated: 2026-10-20
project: Jery
type: index
tags: [jery, mcp, dataset, training, hyperopt]
---

# Jery

## 작업 백로그

- [[Work/Jery/Jery 작업 백로그|Jery 작업 백로그]] (`JR-1xx` ~ `JR-8xx`)

## 작업기록


- [[Work/Jery/작업기록/2026-10-21-Jery-LR외설정-lr1e3선택Child기준통일|2026-10-21 — 지정 lr1e3 Parent 최종 Child 기준으로 LR 외 전체 설정 통일, 학습 중단 유지]]



- [[Work/Jery/작업기록/2026-10-21-Jery-LR만20회-Stratified5Fold검증|2026-10-21 — 비-LR 조건 고정, LR20개 × 시나리오 보존 층화5-fold, 100회 학습]]



- [[Work/Jery/작업기록/2026-10-21-Jery-MLflow비교params-완료검증오류-복구|2026-10-21 — 비교 params backfill과 완료 key 검증 충돌 수정, 동일 Parent 재개]]



- [[Work/Jery/작업기록/2026-10-21-Jery-MLflow-비교파라미터-복원과-실시간동기화|2026-10-21 — Warmup·Clipping·Scheduler·WD·Smoothing params, 105개 Child에525개 복원]]



- [[Work/Jery/작업기록/2026-10-21-Jery-Warmup배치ClippingScheduler-공동탐색20회|2026-10-21 — LR·warmup·배치·clipping·scheduler 공동 Hyperopt20회, 실행기 확장과 전체171개 테스트]]



- [[Work/Jery/작업기록/2026-10-21-Jery-LR1e-3부터5e-3와-추가탐색후보|2026-10-21 — 다음20회 LR1e-3~5e-3, warmup·batch·clipping·scheduler 후보]]



- [[Work/Jery/작업기록/2026-10-21-Jery-다음20회-LR상한1e-3|2026-10-21 — 다음20회 LR 상한1e-3, 현재 학습 완료 뒤 자동 실행]]



- [[Work/Jery/작업기록/2026-10-21-Jery-train600-F1조건-범위축소-Hyperopt20회|2026-10-21 — test F1≥0.7·val F1≥0.75 실행6개 기반 범위 축소와 Hyperopt20회]]



- [[Work/Jery/작업기록/2026-10-20-Jery-train600-참고모델기반-Hyperopt20회|2026-10-20 — validation F1·과거 seed3407 성공 모델 참고, train600 Hyperopt20회 시작]]


- [[Work/Jery/작업기록/2026-10-20-Jery-train600-CUDA-Hyperopt-시작|2026-10-20 — train600 CUDA Hyperopt5회 시작, Parent–Child와 네트워크 복구]]


- [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-학습데이터600개-보강|2026-10-20 — 학습 240→600개, AI 공동 작성·검토와 native 형식 검증]]


- [[Work/Jery/작업기록/2026-10-20-Jery-실제요청-고정평가셋-준비와-협업|2026-10-20 — 실제 요청 수집·공동 검토·평가 게이트와 데이터 부족 확인]]


- [[Work/Jery/작업기록/2026-10-20-Jery-반복오류-검토와-데이터보강|2026-10-20 — 반복 오류·정답 대조, 기능 설명 보완과 train 240개]]
- [[Work/Jery/작업기록/2026-10-20-Jery-배치-시드-10회-비교|2026-10-20 — 배치 4·8 × 학습 시드 5개, 10회 비교]]
- [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-정규화-재학습|2026-10-20 — LR·정규화·콜백 조정 후 Hyperopt 재학습]]
- [[Work/Jery/작업기록/2026-10-20-Jery-10개-도구-단일선택-학습진단|2026-10-20 — 10개 고정 도구, 암기 진단 통과와 CUDA Hyperopt]]
- [[Work/Jery/작업기록/2026-10-19-Jery-LR-가중치-공동탐색과-데이터형식검증|2026-10-19 — 낮은 LR·가중치 Hyperopt 공동 탐색, Laya native 데이터 형식 검증]]
- [[Work/Jery/작업기록/2026-10-19-Jery-routing-v2-공동수정과-재학습|2026-10-19 — Claude·AGY 공동 수정, routing v2 검증과 전체 CUDA 재학습]]
- [[Work/Jery/작업기록/2026-10-19-Jery-CUDA-전체학습-검증과-실험-전환|2026-10-19 — CUDA 전체 한 에폭 검증과 Mac 이후 Hyperopt 전환]]
- [[Work/Jery/작업기록/2026-10-19-Jery-RTX5070Ti-CUDA-서버-실행-검증|2026-10-19 — RTX 5070 Ti CUDA 서버 환경과 32스텝 실행 검증]]
- [[Work/Jery/작업기록/2026-10-19-Jery-MLflow-연결-복구와-Hyperopt-재개|2026-10-19 — MLflow HTTPS 연결 복구, 완료 기록 동기화와 Hyperopt 재개]]
- [[Work/Jery/작업기록/2026-10-18-Jery-Laya-균형학습-Hyperopt-콜백과-MLflow|2026-10-18 — Laya 균형 학습, Hyperopt 탐색, 검증 콜백과 커밋·푸시]]
- [[Work/Jery/작업기록/2026-10-17-Jery-M4-학습-Gemma-실행과-MLflow-등록|2026-10-17 — M4 기준 모델 학습, Gemma 실행, MLflow 모델·데이터셋 등록]]
- [[Work/Jery/작업기록/2026-10-14-Jery-데이터셋-구축과-Hermes-MLflow-수집-방향|2026-10-14 — 초기 데이터셋 구축, 에이전트 역할, n8n 초안과 MLflow 수집 방향]]

## 현재 상태


후속 학습 요청으로 새 [Parent675bf807](https://mlflow.dove-nest.com/#/experiments/47/runs/675bf807c9674425ba6f9de1ad536b91)에서 LR-only20조건×층화5-fold(총100회)를 시작했다. 기준Child c04cdad…의 비-LR 설정을 그대로 사용한다: warmup10,maxnorm1,linear,WD0.05,smoothing0.1,batch4,seed3407,최대32epoch. LR1e-3~5e-3. 기준4a98932/supervisor232533, 새 state로 시작하고 이전 중단 CV/삭제run은 복원하지 않았다. 아래 학습 중단/미실행 표시는 각 과거 시점 기록이다.



최신 준비 설정: 사용자 지정 laya-ten-tools-train600-lr1e3-20261021 Parent6261의 최종 선택 Child c04cdad0246b4d6896ef89e5f9032ce2(validation0.95) 기준으로 LR 외 전체 모델 설정을 복사했다. Warmup10/maxnorm1/linear/WD0.05/smoothing0.1, batch4/seed3407/최대32epoch. LR1e-3~5e-3 및 기존5-fold는 유지한다. 새 별도 config에 전체 reference_model_config를 보존하고 LR·결과 저장 경로 외 값이 달라지면 거부한다. 로컬/서버 검증4개와8개 실제 Hyperopt 후보 비-LR 불변식 PASS, 4a98932 push/서버 반영. 학습은 재개하지 않았으며 활성 Jery trainer0개·기존 state interrupted를 확인했다.



사용자 요청으로 LR-only5-fold 학습을 종료했다. 활성 CV 학습 프로세스0개 확인, 추가 trial/fold 시작 없음. 로컬 결과/checkpoint 보존, 서버 state interrupted 및 user-stop-record.json 기록. MLflow 항목은 이미 삭제된 상태여서 상태 갱신만 불가능했으며 복원하지 않았다. 자동 재개하지 않는다. 아래 학습 진행 표시는 과거 기록이다.



2026-10-21 최신 실행: 공동 탐색20회가 완료돼 validation 최고 run c0635c4c의 비-LR 설정(batch4,seed3407,warmup75,maxnorm2,cosine,WD0.1,smoothing0)을 고정했다. [LR-only CV Parent790b62ac](https://mlflow.dove-nest.com/#/experiments/47/runs/790b62ac777c43098b47cadd134d3a4e)에서 LR1e-3~5e-3만20회 TPE 탐색하고 각 조건을 같은 scenario-group 층화5-fold로 평가한다. Train600 pool→fold마다480/120, validation tool당12, group누수0/OOF coverage600정확히1회, test20고정·tuning배제. Parent→trial20→fold각5 구조이며 trial 평균/std는5fold 완료 후 표시한다. 첫fold CUDA429steps/3epoch와 MLflow 동기화 확인. 전체181테스트 PASS, 서버7e57349/supervisor230844. 총100회 학습 진행 중이며 원래 validation20은 CV에 사용하지 않는다.



2026-10-21 복구: 비교 params5개 backfill과 기존 exact-key 완료 검증의 충돌로 공동 탐색 supervisor가 Child10 업로드 뒤 종료된 것을 확인했다. 수정3ac42f4에서 승인된 비교 params만 추가 허용하고 필수/unknown/metrics 검증은 유지했다. 서버 테스트14개 PASS 후 같은 Parent3b7fd13f에서 supervisor229433 재개. Child10은 기존모델 SHA/mtime/steps/runner 목록 보존으로 재학습 없이 FINISHED, Child11 실제 CUDA750steps/5epoch를 확인했다. 기존20회가 이어 진행 중이다.



2026-10-21 최신: LR 외 warmup·effective batch·clipping·scheduler도 함께 탐색하도록 실행기를 확장했다. [공동 탐색 Parent3b7fd13f](https://mlflow.dove-nest.com/#/experiments/47/runs/3b7fd13fe2f74146a520fa64d0c2305d) 아래20회 TPE: LR1e-3~5e-3, WD[0,0.05,0.1], smoothing[0,0.1], warmup[10,75,150], accumulation[1,2,4]/micro4→batch[4,8,16], maxnorm[0.5,1,2], scheduler[linear,cosine]. 전체171개 테스트와 서버 통합18개 PASS. LR-only 대기 Parent8e27은 Child0 상태로 중단하고 공동 탐색으로 대체했다. 기존6261 Parent 학습은 유지하며 완료 뒤 새 탐색을 자동 시작한다. 아래는 각 과거 시점 기록이다.



2026-10-21 최신 상태: 이전 Parent dca0889273a641eaae6e4a92bfa9efc9의 20회 모두 완료됐다. 표 val F1≥0.75·test F1≥0.70 실행6개를 직접 찾아 report의 선택 head val F1도 확인했다. 이들의 모든 값을 포함하면서 LR을1.4e-4~4.2e-4, smoothing을[0,0.1]로 축소했다. WD[0,0.05,0.1]·seed3407·batch4·최대32epoch·최소8·patience6·train600/val20/test20 유지. [새 Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/6e2c92b081534cc8a8e3b1271e3c0e9c) 아래20회를 시작했다. 실행기 변경/추가 의존성 없고 데이터 검증·계획 테스트5개·threshold/범위 계약 PASS. f9b9ebc 푸시·서버 반영, supervisor222834. Test-informed 범위 설계이며 TPE/checkpoint는 validation accuracy만 사용한다. 아래 내용은 각 과거 시점 기록이다.



2026-10-20 최신 상태: 기존 train600 Hyperopt5회는 모두 완료됐다. Validation F1 표기0.8567 실행(선택 checkpoint F1 0.90) 및 seed3407·test acc/F1 모두0.7 초과인 과거2개 실행의 설정을 참고해 [새 Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/dca0889273a641eaae6e4a92bfa9efc9) 아래 Hyperopt20회를 시작했다. Train600/validation20/test20, LR8e-5~5e-4, WD/smoothing각[0,0.05,0.1], batch4·seed3407, 최대32epoch·최소8·patience6. 선택/TPE는 validation accuracy만 사용하고 과거 test에 근거한 범위 설정은 탐색 실험으로 명시했다. 코드/설정 fc1989d 푸시 및 서버 반영, supervisor209691, 첫 Child87e3fbaf6f3848b898e02a3ecf089551 실행 중이다. 아래 진행/미학습 표기는 각 과거 시점 기록이다.


사용자 요청으로 train600 CUDA Hyperopt 학습을 시작했다. [새 Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/88a5250cd54048d8a9593bab7e59d753) 아래 Child5회 순차 실행, LR1e-5~2e-4, batch4, 최대16에폭이다. PC 네트워크 복구 후 기존 Parent로 이어서 실행했다. 첫 Child의 실제 CUDA step·에폭 지표 동기화를 확인했으며 첫 조건은9에폭 후 초기 head보다 개선되지 않아 serving 초기 head를 유지했다. 첫 조건은 모델·상세결과27개 Artifact 업로드 검증까지 완료했고 두 번째 Child가 자동 실행됐다. 전체5회 탐색은 진행 중이며 detached supervisor가 이어 수행한다. 과거 '미학습' 표기는 데이터 준비 당시 기록이다.


고정 10개 도구 학습 데이터 v3를 train600개(도구당60), validation20/test20으로 준비했다. Claude·Antigravity가 신규 합성360개를 작성하고 Claude·Codex가 검토했다. AGY는 수정 후 quota 제한으로 상대 검토를 완료하지 못해 Codex가 이어받았다. 전체 테스트169개 및 최종 Laya native 검사640개에서 누락·잘림·특징/target 불일치0개. 기존 train240 prefix와 heldout 파일을 보존했다. dev-codex bf8ca94까지 푸시했고 MLflow training-data-v3-prepared/에 데이터·검토·검증 Artifact13개를 업로드했다. 새 학습은 실행하지 않았으며 사람 검토는 남아 있다.


등록 MCP 5개·도구 96개의 합성 데이터셋 v2(1,162개)와 학습·예측 가능한 선형 기준 모델을 구현하고 Mac mini M4에서 학습을 완료했다. MLflow에 학습 모델 Jery-LinearRouter v1, 데이터셋, 평가 결과와 코드를 등록했다. Gemma 4 E4B 4비트의 로컬 실행도 확인했지만 미세조정하지 않았으며, 6건의 탐색 결과는 기존 모델 대체를 뒷받침하지 못했다.

Laya multilingual은 인코더를 고정하고 결정 head를 학습한다. 배치·시드 10회와 반복 오류 감사, 기능 설명 보완·train 60→240개(도구당 24) 보강을 완료했다. Native 옵션당 24token 한도에 맞춘 명세를 사용하고 잘림·특징/target 불일치 0건, 전체 테스트 151개 통과를 확인했다. 설명만 보완한 모델의 검증은 60%, 데이터 보강 모델은 65%로 이전 최고 65%를 넘지 못했다. 같은 검증 20개를 반복 관찰한 회귀 결과이며 실제 성능 개선으로 단정하지 않는다. 같은 비교를 Parent 둘로 나눴던 구성을 정정해 [통합 Parent](https://mlflow.dove-nest.com/#/experiments/47/runs/5f64008a2b974b7f87fab5088bafcf8a) 아래 description-only-train60과 augmented-train240 Child 두 개를 직접 배치했다. 모두 FINISHED이며 모델 업로드도 완료됐다. Params·metrics·모델을 보존하고 재학습하지 않았다. 빈 중복 Parent는 metadata/artifact를 남기는 soft-delete로 보관했다. 데이터와 설정은 통합 Parent의 conditions/{condition}/, 현재 관계는 summary.json·comparison-plan.json을 따른다. 새 실제 요청 고정 평가셋 준비를 Claude·Antigravity와 함께 진행했다. 읽기 전용 수집·정제·동결 평가 게이트·독립 감사 구현과 전체 테스트 168개를 통과했다. 실제 후보 13개 중 두 AI가 단일 도구로 합의한 것은 1개이며 사람 검토 완료는 0개다. 추가 과거 출처가 없어 목표 100개 대비 AI 적격 기준 99개가 부족하다. 평가셋은 candidate 상태이며 동결·실제 모델 평가·추가 학습은 실행하지 않았다. 앞으로 실제 요청 누적과 정답 검토가 필요하다.

읽기 전용 Hermes 로그 수집기·검토 후보 API와 독립 데이터 감사 도구는 구현했다. 이번 학습에는 실제 대화 로그를 사용하지 않았고 합성 정답은 모두 미검토 상태다. 정답 검토와 실제 요청 평가, action·비선택 사례 보강이 남아 있다.

2026-10-18 전체 테스트 109개 및 v1/v2 데이터 검증을 통과하고, `dev-codex`의 [`f135208`](https://github.com/EvoDmiK/Jery/commit/f135208a6eeade7b33c286360f366b6b4157bfc1)을 `origin/dev-codex`에 푸시했다. 상세 설정·재현 방법과 시각별 학습 상태는 최신 작업기록을 따른다.

2026-10-19 학습용 Python의 내부 IP 연결 실패를 공개 HTTPS 주소로 우회하고, 첫 trial 결과를 재학습 없이 동기화해 두 번째 Hyperopt trial을 시작했다. 복구 코드는 `a8de267`로 커밋·푸시했다. 상세 검증과 시각별 상태는 2026-10-19 작업기록을 따른다.

2026-10-19 회사 RTX 5070 Ti에서 전체 한 에폭 학습·검증·checkpoint 저장은 4분 32초, 로드·최종 평가·복원까지 전체 CLI는 5분 56초였다. epoch 1 정확도는 하락해 초기 head를 복원했으며 정확도 개선을 주장하지 않는다. 당시 Mac 실험을 유지하면서 사용자 요청으로 CUDA Hyperopt 5회도 시작했으나, 이후 이번 routing v2 전환 요청에 따라 두 실행을 모두 중단했다. 현재 실행 상태는 위 routing v2 Parent와 최신 작업기록을 따른다. 전체 테스트 112개 통과, `1c0011f` 커밋·푸시 및 서버 반영 완료. 자세한 상태와 한계는 최신 CUDA 전체 학습 작업기록을 따른다.

## 관련

- [GitHub 저장소](https://github.com/EvoDmiK/Jery)
- [[Work/index|프로젝트 목록]]
- [[Work/Birds-Nest/작업기록/Hermes/index|Hermes 작업기록]]
