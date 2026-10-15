---
created: 2026-10-09
updated: 2026-10-09
project: RobinGraph
type: work-log
---

# README에 IUCN 등급별 카드 색 매핑 추가

## 요청 배경과 목표

사용자가 "IUCN 별로 카드 색이 다른데 README.md에 등급과 색을 매핑해서 추가해 달라"고 요청했다. 코드 변경 없이 문서(README)만 갱신하는 작업이다.

## 확인한 코드 근거

색이 어디서 정해지는지 코드를 읽어 확인했다. 표의 모든 값은 아래에서 옮겼고 추정한 값은 없다.

- `src/robingraph/api/static/chat.js`의 `CONSERVATION_CATEGORIES`: 등급 코드 → 한국어 표기와 `tier`(`lc`, `nt`, `vu`, `en`, `cr`, `ew`, `ex`, `unconfirmed`). DD·NE는 둘 다 `unconfirmed`.
- `conservationInfo()`: 등급 코드가 정확히 알려진 값이고 `source_name`(출처 이름)이 있을 때만 확인된 등급으로 취급한다. 아니면 "멸종위기 등급 미확인"(`unconfirmed`). 원자료의 `CR (PE)`·`CR (PEW)`는 CR로 정규화하고 배지에 "절멸 가능성"·"야생절멸 가능성"을 덧붙인다.
- 카드·팝업·채팅 버튼은 `risk-<tier>` 클래스를 받는다(`chat.js`).
- `src/robingraph/api/static/styles.css`의 `risk-*` 규칙: 프레임(`.species-popup.risk-*`), 카드 바탕(`.species-card.risk-*`), 배지(`.species-conservation-badge`), 채팅 버튼 왼쪽 테두리. LC의 프레임은 `.species-popup` 기본 은색 그라데이션이다.

## 변경 내용

README의 "PC·모바일 도감 카드" 섹션 끝에 `#### IUCN 등급별 카드 색`을 추가했다(22줄).

| 등급 | 한국어 | 프레임 | 카드 바탕 | 배지 |
|---|---|---|---|---|
| 🟩 LC | 관심대상 | 은색 `#959a95` | 연두 `#8fbb5c`→`#def19a` | `#e3f2c4` / `#7f9c55` |
| 🟦 NT | 준위협 | 청회색 은색 `#8fa7b2` | 민트 `#8fc7b0`→`#d8f1e6` | `#d3efe3` / `#4f8a75` |
| 🟨 VU | 취약 | 금색 `#c9a13b` | 노랑 `#e8c86a`→`#fbf0c4` | `#fbeab0` / `#a17a14` |
| 🟧 EN | 위기 | 주황 `#c4622c`, 사선 줄무늬 포일 | 주황 `#f2a774`→`#fde4cf` | `#fdd9bd` / `#a24a17` |
| 🟥 CR | 위급 | 분홍·자홍 홀로그램 `#c2185b`(움직임) | 분홍 `#f3a0b8`→`#fde3ea` | `#fcd3df` / `#9c1046` |
| 🟪 EW | 야생절멸 | 보라 홀로그램 `#5e35b1`(움직임) | 라벤더 `#c5b0ee`→`#efe7fd` | `#e4d8fa` / `#4a2d91` |
| ⬛ EX | 절멸 | 검정 홀로그램 `#1b1b1b`(움직임) | 회보라 `#b9b6c4`→`#ecebf1` | `#2a2a30`, 글씨 `#f4f2ff` |
| ⬜ DD·NE·기록 없음 | 정보부족·미평가·미확인 | 밝은 회색 `#b5b8b3` | 회녹색 `#d9ddd3`→`#eef0ea` | `#f1f2ee` |

표 아래에 다음을 설명으로 붙였다.

- LC만 기본 연두 카드를 쓰고 나머지 등급은 카드 바탕도 등급 색으로 바뀐다.
- CR·EW·EX 프레임은 천천히 움직이는 포일 효과이고 운영체제의 움직임 줄이기 설정이 켜지면 멈춘다.
- 출처 이름이 없거나 DD·NE이거나 등급이 없거나 인식할 수 없는 값이면 회색 "미확인"이다. `CR (PE)`·`CR (PEW)`는 CR 색이다. 색은 기록된 등급의 시각 표시일 뿐 지역 개체수 판단이 아니다.
- 등급 → 클래스 매핑은 `chat.js`, 색은 `styles.css`에 있고, 표의 색은 2026-10-09 기준 CSS에서 옮긴 값이다.

## 검증

- 표의 hex 값은 `styles.css`의 해당 규칙과 대조해 옮겼다. 프레임·카드 바탕은 실제로는 그라데이션이라 대표 색만 적었다.
- 처음 작성한 설명에서 "인식할 수 없는 값이면 미확인"이라고만 썼다가 `conservationInfo()`를 읽고 "출처 이름이 있어야 한다"와 `CR (PE)`·`CR (PEW)` 처리를 추가해 정정했다.
- 코드·테스트는 바꾸지 않았으므로 테스트는 실행하지 않았다. 병합 후 `main` CI 7개 job은 성공했다(문서 변경).
- GitHub에서 README 표가 실제로 어떻게 렌더링되는지는 확인하지 못했다.

## 커밋·배포

- README 커밋 `3770595`(`dev-claude`), `main` 병합 커밋 `25c4a7a`. 병합 후 `main` CI(run 37889510938)의 job 7개가 모두 성공했다.
- NAS 배포는 하지 않았다(README는 배포 이미지에 영향이 없는 문서 변경).

## 한계

- NT의 이모지 🟦는 실제 색(민트)에 가장 가까운 이모지일 뿐이다. 정확한 색은 hex를 따른다.
- 이 작업은 저장소에 별도 작업 기록 파일을 만들지 않았다. 산출물이 README 자체다.

- [[Work/RobinGraph/index|프로젝트 인덱스]]
- [[Work/RobinGraph/작업기록/index|작업기록 목록]]
