# 미터 도면 → 블로킹 보드 임포트 스펙 (v1)

> **한 줄 요약**: Claude가 대본을 읽고 **미터 단위 평면도**(사람이 검증 가능한 단일 진실)를
> 만들면, 보드가 그것을 임포트해 3D로 세우고 드래그로 편집한다. 좌표 변환·크기 계산은
> **보드의 임포트 어댑터**가 담당한다(지금은 Claude가 임시로 대신하고 있다).

---

## 0. 왜 이 스펙이 필요한가

이번 S#8 작업에서 드러난 마찰:
- Claude가 도면→`state.items` 변환까지 하니, 문 위치·겹침·배우 이동을 **JSON 왕복으로 반복**
  편집하게 됐다. 그건 보드 드래그 한 번이면 될 일이었다.
- `state.items`(픽셀) 형식을 Claude가 직접 만들다 보니, 방 크기(420 vs 440)·좌표 기준이
  갈라지고 가구가 겹쳐 무너지는 사고가 났다.

**해결**: 교환 포맷을 **미터 도면**으로 통일한다. 미터가 단일 진실이 되고, SVG(사람용)와
`state.items`(기계용)는 그 파생물이 된다. 보드가 미터 도면을 직접 임포트하면 Claude는
좌표 픽셀 계산에서 손을 뗀다.

### 역할 분담

| 단계 | 담당 |
|---|---|
| 대본 → 미터 좌표 도면 (생성) | **Claude** |
| 미터 도면 → `state.items` 변환 | **보드 임포트 어댑터** (이 스펙) |
| 좌표 미세조정·겹침 해결·문 위치 | **보드** (드래그·스냅) |
| 파서 인물/배경 분류 | **보드** (코드) |

---

## 1. 입력 포맷 — 미터 평면도 JSON (`floorplan-v1`)

Claude가 넘기는 것. **모든 좌표는 미터, 실내 좌상단이 원점 (0,0), +x 오른쪽, +y 아래.**

```json
{
  "schema": "floorplan-v1",
  "room": { "widthM": 11.0, "depthM": 7.0, "heightM": 2.6, "kind": "사무실" },
  "objects": [
    { "kind": "책상", "name": "책상", "x0": 3.25, "y0": 1.5, "x1": 4.70, "y1": 2.75 },
    { "kind": "소파", "name": "L형 소파", "x0": 7.9, "y0": 1.8, "x1": 10.6, "y1": 2.55 }
  ],
  "openings": [
    { "kind": "문",  "name": "출입문", "wall": "south", "x0": 9.5, "y0": 6.95, "x1": 10.7, "y1": 7.0 },
    { "kind": "창문", "name": "격자창", "wall": "east",  "x0": 11.0, "y0": 3.0, "x1": 11.0, "y1": 3.6 }
  ],
  "actors": [
    { "id": "hyunwoo", "name": "Hyunwoo", "xM": 10.2, "yM": 6.6, "angle": -135,
      "pose": "stand", "path": [ {"xM": 5.5, "yM": 4.0}, {"xM": 4.6, "yM": 3.6} ] }
  ],
  "cameras": [
    { "cutRef": "CUT8-2", "xM": 5.2, "yM": 5.3, "angle": 133, "fov": 47,
      "shotSize": "medium", "subjectRef": "hyunwoo" }
  ]
}
```

- **`objects[]`** — 가구. `kind`는 카탈로그 매칭 키(§3). `x0,y0,x1,y1`은 도면상 사각(미터).
  크기는 이 사각을 쓰되, 보드가 카탈로그 표준으로 보정할 수 있다(§3).
- **`openings[]`** — 문·창. `wall`(north/south/east/west)로 어느 벽에 붙는지 명시.
- **`actors[]` / `cameras[]`** — 위치는 미터. `path`도 미터. 보드가 px로 변환.

---

## 2. 변환 규칙 (보드 어댑터가 구현)

### 2-1. 스케일 — 40px = 1m

```
px = meter × 40
```

방 픽셀 크기: `roomW_px = widthM × 40`, `roomH_px = depthM × 40`.

### 2-2. 좌표 원점 이동 — 실내 좌상단(0,0) → 보드 방 중심

보드는 방 중심을 기준으로 삼는다(예: 640,360). 변환:

```
boardX = CX - roomW_px/2 + xM × 40
boardY = CY - roomH_px/2 + yM × 40
```

(CX,CY = 보드가 방을 놓는 중심. 임의. 예 640,360)

### 2-3. 가구 사각 → 중심+크기

```
item.x = (boardX(x0) + boardX(x1)) / 2
item.y = (boardY(y0) + boardY(y1)) / 2
item.w = |boardX(x1) - boardX(x0)|
item.h = |boardY(y1) - boardY(y0)|
```

### 2-4. 출력 — `state.items[]`

각 object → `{id, type:"prop", layer:"space", kind, name, x, y, w, h, angle:0, motionMarkers:[]}`
방 → `{id, type:"room", layer:"space", kind, name, x:CX, y:CY, w:roomW_px, h:roomH_px, angle:0}`
actor → `{id, type:"actor", name, x, y, angle, pose, path:[{x,y,pause:0}], ...}`
camera → `{id, type:"camera", cutRef, x, y, angle, fov, shotSize, subjectId, ...}`

---

## 3. 카탈로그 보정 — 인간 키를 기준점으로

가구 크기가 도면 사각과 다르거나 누락되면, 보드는 **오브젝트 카탈로그**
(`xconda_object_catalog.json`)의 표준 치수를 쓴다.

- 기준점: **사람 키 1.70m = 68px**. 가구 높이 비율로 검산
  (책상 0.75m≈배꼽 44%, 캐비닛 1.90m≈사람보다 큼 112%).
- `kind` → catalogKey 매칭: `책상|desk`·`의자|chair`·`소파|sofa`·`책장|bookcase`·
  `수납장|옷장|cabinet`·`테이블|table`·`문`·`창문`·`전면유리창`.
- 도면 사각과 카탈로그 표준이 다르면: **위치는 도면, 크기는 카탈로그**를 기본으로 하되,
  도면 사각이 명시적이면 그대로 존중(감독이 일부러 크게 그린 경우).

---

## 4. layer 처리 — perf 유령 방지

- 임포트로 생성되는 가구는 전부 `layer:"space"`.
- **`layer:"perf"`는 임포트가 만들지 않는다.** 현재 보드에 프롬프트의 PERFORMANCE·소품
  언급을 가구로 오인해 `perf`에 중복 생성하는 버그가 있다 — 임포트 경로에서는 이 분기를
  타지 않도록 한다.
- 재임포트 시: 기존 `layer:"perf"` prop을 먼저 제거하고 `space`만 교체한다. 사용자가
  드래그로 확정한 좌표(별도 저장 상태)는 덮어쓰지 않는다.

---

## 5. 재임포트·편집 보존 규칙

- **방·가구**는 미터 도면이 소스다. 도면이 바뀌면 space 가구를 새로 깐다.
- **배우 위치·문 위치**는 사용자가 보드에서 확정한 값을 우선한다. 도면의 actor 좌표는
  "초안"이고, 사용자가 옮겼으면 그 값을 유지한다(임포트가 되돌리지 않는다).
- 겹침·벽 통과는 보드가 임포트 직후 검증해 경고한다(Claude가 JSON으로 확인하지 않는다).

---

## 6. 파서 분류 — 인물/배경 (별도 이슈, 함께 고칠 것)

임포트와 별개로, 프롬프트 텍스트에서 레퍼런스를 분류할 때 **설명 문장의 단어**
(`background`/`lighting`)로 분류하면 인물이 배경으로 빠진다(배우 0명 사고). 분류는
**`· 이름 — 설명`의 대시 앞 대상**으로만 판단하도록 고친다. → 그러면 Claude가 인물
설명에 어떤 단어를 써도 안전해지고, 이 스펙의 actor 임포트와도 일관된다.

---

## 7. 마이그레이션 — 지금 → 목표

| 지금 (임시) | 목표 |
|---|---|
| Claude가 `plan_to_board.py`로 미터→px 변환 | 보드 어댑터가 `floorplan-v1`을 직접 임포트 |
| Claude가 `state.items` JSON을 만들어 전달 | Claude는 `floorplan-v1`(미터)만 전달 |
| 문·겹침·배우이동을 JSON 왕복 편집 | 보드에서 드래그로 편집 |
| Claude가 평면도 PNG로 검증 | 보드 3D 뷰가 실시간 검증 |

이 스펙을 보드에 구현하면, Claude의 산출물은 **`floorplan-v1` 미터 도면 하나**로
단순해지고, 픽셀·겹침·편집은 전부 보드가 맡는다.

---

## 부록 A. 레퍼런스 구현 (`plan_to_board.py`)

이번 세션에서 만든 `plan_to_board.py`가 §2 변환의 동작하는 예시다(미터 사각 → px 중심·크기,
중심 이동, room/prop/actor/camera 생성). 보드 어댑터는 이 로직을 서버/클라이언트 코드로
옮기면 된다. 단, §3 카탈로그 보정과 §4 layer 처리는 그 위에 추가한다.
