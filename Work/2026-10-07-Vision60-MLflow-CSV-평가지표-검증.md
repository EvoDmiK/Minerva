---
title: Vision60 MLflow CSV 평가 지표와 이력서 정량 문구
date: 2026-10-07
tags: [career, resume, vision60, mlflow, verification]
---

# Vision60 MLflow CSV 평가 지표와 이력서 정량 문구

## 직접 확인한 범위

사용자 제공 runs.csv를 csv.reader로 직접 읽고 집계했다. 원본은 수정하지 않았으며 live MLflow 서버·시뮬레이터를 실행 검증한 것은 아니다. 이 파일이 프로젝트 전체 실험을 포함한다고 가정하지 않는다.

- 총 70 run 기록: parent 33개, passed가 기록된 trial 37건.
- 기록된 판정은 passed=1 10건, passed=0 27건. 후자에 MLflow 상태 RUNNING으로 남은 1건이 포함되며 cancel_reason=goal_timeout이다. FINISHED trial은 36건이다.
- FINISHED는 로깅 종료 상태이며 테스트 성공이 아니다. 테스트 실패 26건도 FINISHED 상태다.
- success_mode가 final_pose, arrival_radius_0.30m, arrival_radius_0.10m으로 섞여 있어 전체 통과 비율을 최종 설정 성공률로 쓰지 않는다.
- 중복 열 이름 forklift_speed_mps, success_mode, no_collision_detected를 열 위치로 구분해 값 덮어쓰기를 방지했다.
- check_ 열은 49종이다. 49개가 모두 기록된 trial은 3건이고 다른 34건은 상세 check 열이 비어 있으므로 모든 trial에서 49종을 측정했다고 주장하지 않는다.
- actual_position_error_m와 actual_yaw_error_rad는 37건, actual_max_tilt_deg/actual_max_speed_mps는 3건, zero_return_s는 29건에 기록됐다. 결측치를 0으로 채우지 않았다.

## 선정한 조건별 통과 사례

2026-09-18, 시드 103, final_pose 모드의 세 통과 run. 지게차 속도별로 선택된 통과 실행은 각 1회다.

| 지게차 속도(m/s) | 목표 위치 오차(m) | yaw 오차(rad) | 정지 명령 복귀(s, sim) | 기록 판정 |
|---|---:|---:|---:|---|
| 1.5 | 0.267 | 0.035 | 0.16 | PASS |
| 2.0 | 0.235 | 0.177 | 0.14 | PASS |
| 2.5 | 0.245 | 0.164 | 0.26 | PASS |

필드: actual_position_error_m, actual_yaw_error_rad, zero_return_s, passed.

- 1.5m/s의 앞선 시험은 passed=0이며 재시도가 포함됐다. 시간 예산 변경 240→900초는 9/18 속도 사다리 문서의 기록이고 선정 run의 CSV timeout 필드는 비어 있다.
- 세 run의 commit은 같지만 code_diff_hash는 1.5m/s와 나머지 둘이 다르다. 엄격한 동일 코드 A/B 비교로 주장하지 않는다.
- zero_return_s의 시뮬레이션 시간 기준은 9/17 LIO 좌표계 오류와 실제 도착 검증 수정 문서 L50–57에서 확인했다. 선정 run의 CSV 시간 기준 태그는 비어 있으므로 이 근거를 구분한다.
- zero_return_s는 목표 종료 후 속도 명령이 0으로 복귀하는 지표다. 9/17 게이트 정지 명령 누락과 수정 필요 사항 문서 L18–33, L56–60의 cmd_vel 출력 기준과 대조했다. 실제 몸체의 제동 시간·장애물 감지 반응 시간으로 표현하지 않는다.
- 단일 시드·각 속도 1회 통과 사례이며 100% 성공률·범용성·무접촉 보장으로 확대하지 않는다. 다른 시드와 조건 변경 실패도 CSV에 포함돼 있다.

## 이력서에 추가할 문구

- 목표 위치·방향 오차, 목표 종료 후 정지 명령 복귀 시간, 주행 자세·속도, odometry 연속성 및 점군 발행 주기를 평가 지표로 사용하여 AI 코딩 에이전트의 구현 결과를 검증함
- Isaac Sim ground truth와 위치 추정 결과를 분리하여 목표 도달 오차를 측정하고, 기동 실패·데이터 품질 문제·물리 이상을 구분해 실험 결과를 판정함
- MLflow에 기록된 개별 trial 결과 37건을 상위 실험과 구분하여 성공·실패 및 파라미터 변경 이력을 추적함
- 단일 시드의 지게차 속도 1.5·2.0·2.5m/s 시험에서 조건별 통과 사례를 확인하고, 해당 실행의 목표 위치 오차 0.235~0.267m와 목표 종료 후 정지 명령 복귀 시간 0.14~0.26초를 기록함

마지막 문구의 수치는 선정 통과 실행에 한정된다. 정지 명령 복귀는 시뮬레이션 시간 기준이며 1.5m/s 재시도가 포함됨을 포트폴리오·면접에서 함께 설명한다.

## 검증과 보관

ATE/RPE·p95 pipeline latency는 이 CSV에 없어 별도 8/14 문서 수치를 합쳐 한 캠페인의 성과로 쓰지 않았다. CSV는 MCP 서버 구현 기능의 증거도 아니다.

로컬 분석 코드 analyze_runs.py를 실제 실행해 exit code 0을 확인하고, 별도 csv.reader 집계로 trial·통과 수, RUNNING 상태, 선정 run 수치와 check 기록 범위를 재확인했다. 원본 경로·해시·run ID는 로컬 JSON에만 보존했다.

산출물: agent-artifacts/local/2026-10-07-vision60-csv-metrics/ — analyze_runs.py, csv-analysis.json, metrics-and-resume.md.

## 추가 ad-hoc verification

분석 스크립트 `analyze_runs.py`를 대상으로 OS-safe tempfile의 `/tmp/hermes-verify-*.py`를 생성해 unittest를 실행했다. 출력 JSON은 별도 임시 디렉터리로 격리하여 원본 CSV와 기존 결과를 덮어쓰지 않았다.

실제 실행 결과: **Ran 9 tests — OK, exit code 0**.

확인한 범위: CSV 크기·고유 run ID, parent/trial 및 성공/실패 집계, 중복 열의 모든 셀 보존, FINISHED와 통과 판정의 차이, 선정 지표의 원본 일치, 결측·비유한 값 처리, 49개 check의 기록 범위, 기존 JSON 결과의 정확한 재현, 원본 CSV·분석 스크립트·저장 JSON 불변. 임시 검증 파일 및 출력 디렉터리는 정리했다.

최초 임시 파일 작성은 도구의 /tmp 경로 제한으로 실패했다. 빈 파일 실행은 검증으로 인정하지 않았고 실제 코드를 생성한 재실행 결과로 정정했다.

이는 **일회성 분석 코드의 ad-hoc verification**이며 정식 프로젝트 테스트 스위트·빌드나 로봇 실험의 재실행 성공을 의미하지 않는다. 실제 출력 보관: `agent-artifacts/local/2026-10-07-vision60-csv-metrics/adhoc-verification.md`.
