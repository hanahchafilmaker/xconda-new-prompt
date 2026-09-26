# 얼굴 프레임 중앙·공간 스케일 락 (구 §10-2·§10-3)

> 이 파일은 SKILL.md에서 분리된 상세 규칙입니다. SKILL.md의 라우팅 표가 이 파일을 가리킬 때 엽니다.
> 규칙 내용은 원본 그대로이며 위치만 옮겼습니다.

## 10-2. 인물 컷은 얼굴을 프레임 중앙에 크게 둔다 (인서트 제외 · 기본값)

인서트(손·소품·디테일 클로즈업)가 아닌 **모든 인물·대사 컷의 기본값**은 화자의 얼굴을
프레임 중앙(눈높이가 화면 상단 1/3 지점)에 크게 두는 것입니다. 이건 특별 연출이 아니라
당연한 디폴트인데, 화각(47°/29° 등)만 지정하고 얼굴 위치를 명시하지 않으면 씨댄스가 특히
**오버숄더(OTS) 컷에서 얼굴을 구석·하단에 두거나 앞 인물의 어깨·소품에 가리는** 결과를
자주 냅니다.

작성 규칙 — **컷마다 반복하지 않는다**(§8-15 반복=충돌). 딱 두 곳에 한 번씩만 선언합니다.

- **04번 [카메라]** 에 규칙 한 줄:
  "인서트를 제외한 모든 인물·대사 컷은 화자의 얼굴을 프레임 중앙(눈높이 상단 1/3)에 크게 둔다."
  (영문: "In every character/dialogue cut except inserts, the speaker's face is placed large
  and centered in frame, eyeline on the upper third.")
- **10번 [포지티브 락]** 에 유지 상태 한 줄:
  "인서트를 제외한 모든 컷에서 화자의 얼굴은 프레임 중앙에 크게 유지되고, 어깨나 소품에
  가려지지 않는다."
  (영문: "In every cut except inserts, the speaker's face stays large and centered in frame,
  not masked by a shoulder or a prop.")

인서트 컷은 피사체(손·펜·서류 등)가 주역이므로 이 규칙을 적용하지 않습니다 — 08번 인서트
비트에는 "얼굴 중앙" 문구를 넣지 않습니다. 부정문("얼굴 가리지 마")이 아니라 위처럼 **유지할
상태(포지티브 락)** 로 씁니다(§6).

---


## 10-3. 공간 스케일 락 — 공간이 좁게 나오는 것을 막는다 (03번 소유)

가장 자주 나오는 불만이 **"공간이 항상 작게 나온다"** 입니다. 화각을 넓혀도 잘 안 고쳐지는데,
원인이 화각이 아니기 때문입니다. 씨댄스는 공간 크기를 **문장에서 읽습니다.** 그런데 우리가
쓰는 말은 대부분 상대 표현입니다.

```
deeper in the alley / at the far end / a long corridor / 골목 안쪽 / 저 끝에
```

모델은 "deeper"가 3m인지 30m인지 모릅니다. 기준이 없으면 **가장 흔한 학습값 = 좁은 공간**으로
떨어집니다. 그래서 아무리 84°를 써도 가까운 벽이 넓게 보일 뿐, 공간이 깊어지지 않습니다.

### 원칙 세 가지

**① 거리는 미터로 못 박는다 — 상대 표현만으로는 절대 전달되지 않는다**

로케이션의 **깊이·폭**을 03번에 숫자로 씁니다. 이게 없으면 나머지를 다 해도 소용없습니다.

| ❌ 상대 표현만 | ⭕ 미터 앵커 |
|---|---|
| a long alley, the house deeper in | a straight corridor roughly 24 meters deep from the alley mouth to the house, about 6 meters wide |
| 넓은 강당 | 가로 40미터·세로 25미터의 강당, 천장 높이 12미터 |
| 저 멀리 산 | 카메라에서 능선까지 약 3킬로미터 |

**② 후경 랜드마크는 "끝"이 아니라 "경유점"으로 쓴다**

이게 제일 자주 놓치는 부분입니다. 랜드마크를 공간의 끝으로 서술하면 모델은 거기서 시선을
닫아버리고, **그 거리가 곧 공간 전체 크기**가 됩니다.

```
❌ Deeper in, the one intact two-story house.
   → 폐가가 벽이 됨. 폐가까지 짧게 잡히면 골목 전체가 짧아진다

⭕ The intact house stands at 24 meters, and the demolition zone continues
   past it for another 20 meters, so the far end stays open and hazed
   rather than walled off.
   → 폐가가 경유점이 됨. 시선이 그 너머로 빠져나가며 공간이 열린다
```

실내도 같습니다. 문·창·복도 입구 하나만 열어두면 방이 훨씬 커 보입니다.

**③ 4단 깊이 레이어를 쓴다 — 넓이는 화각이 아니라 겹으로 만들어진다**

공간이 넓어 보이는 진짜 이유는 **전경·중경·후경·원경이 동시에 보일 때**입니다. 레이어마다
거리와 물체를 하나씩 지정합니다.

```
Depth layers: foreground — collapsed brick wall and rubble within 3 meters of camera.
Mid-ground — the parked van and a leaning utility pole at roughly 8 meters.
Background — the intact two-story house at 24 meters, its cracked mark readable but small.
Far background — rooftops and crane silhouettes of the wider district beyond, fading into overcast haze.
```

원근선을 만드는 연속 요소(전선·가로등·기둥·타일 줄눈·레일)가 있으면 한 줄 더 붙입니다 —
**"전선이 24미터 전 구간에 걸쳐 먼 끝으로 수렴한다"** 는 화각 지시보다 강하게 먹습니다.

### 어디에 쓰는가 — 블록별 분담 (§5 준수, 반복 금지)

| 블록 | 넣을 것 |
|---|---|
| **03번** (주 담당) | 미터 앵커 + 4단 깊이 레이어 + 후경 개방 문장 + 원근선 요소 |
| **04번** | 확립·이동 컷의 화각을 84° 또는 107°로. 인물 컷은 건드리지 않는다 |
| **08번** | 이동 컷에만 — 이동 거리(m) + 랜드마크 크기 변화 |
| **10번** | 유지할 상태 한 줄 |

**08번 이동 컷 작성법 — 정적 선언보다 크기 변화가 강하다**

```
❌ Hyunwoo walks from the alley mouth to the house deeper in.

⭕ Hyunwoo covers the full 24 meters from the alley mouth to the intact house,
   the wall mark growing from small to filling the upper frame as he closes in,
   and stops in front of it.
```

랜드마크가 **작은 것에서 큰 것으로 변하면** 모델은 그 사이에 거리를 만들어 넣을 수밖에
없습니다. 거리를 한 번 선언하는 것보다 이쪽이 훨씬 확실합니다.

**10번 포지티브 락 예시** (부정문이 아니라 유지 상태로 — §6)

```
· The alley reads as a deep 24-meter corridor: foreground rubble, the van at mid-ground,
  the intact house far back, and the demolition district continuing past it into haze.
```

### 주의 — 화각으로 해결하려 들지 않는다

- 84°/107°는 **확립 컷과 이동 컷에만** 씁니다. 인물·대사 컷까지 넓히면 §10-2(얼굴 프레임
  중앙 크게)와 정면으로 충돌합니다.
- 넓은 화각 + 가까운 거리 = **압박감**입니다(§8 느낌→카메라 번역표). 넓혀 보이려면 화각과
  함께 카메라를 뒤로 빼는 거리도 같이 써야 합니다.
- 우선순위는 **03번 미터 앵커 > 08번 크기 변화 > 04번 화각** 순입니다. 시간이 없으면
  앞의 둘만 해도 8할이 해결됩니다.

### 좁아 보이는 게 맞는 연출일 때

폐소공포·취조실·관 속처럼 **좁은 게 의도**인 씬에서는 이 조항을 적용하지 않습니다. 대신
같은 방식으로 작은 숫자를 못 박습니다 — "가로 2미터·세로 3미터, 천장 2.1미터, 출구 없음".
숫자를 쓰는 것 자체가 원칙이고, 숫자가 크냐 작냐는 연출 판단입니다.

---

