# 레퍼런스 이미지 생성 프롬프트 작성법 (얼굴 락 스틸 · 탑뷰 공간)

> 목적: 씨댄스에 넣을 **인물 레퍼런스(@Image)를 이미지 생성기(Seedream 등)로 먼저 뽑는** 방법.
> 씨댄스 2.5는 학습된 얼굴 모델이 없어, 이 "깨끗한 레퍼런스 1장"의 품질이 얼굴 락을 좌우한다.

## 좋은 얼굴 락 레퍼런스의 5조건 (프롬프트에 반드시 반영)
1. **정면**(또는 살짝 3/4), 눈은 카메라 응시, 머리는 뒤로 넘겨 **얼굴 안 가림**
2. **부드럽고 균일한 정면광**, 강한 그림자 없음 (그림자가 얼굴 일부처럼 학습됨)
3. **중립 표정** (표정·감정은 나중에 영상 프롬프트가 담당)
4. **무배경/단색**(회색 등) — 배경이 정체성에 섞이지 않게
5. **눈높이·약 50mm·얼굴 선명·고해상도**, 필터·왜곡·모션블러 없음

## 프롬프트 골격 (영문, 빈칸만 채운다)
```
[전신 or 상반신] studio reference portrait of [나이대·성별·국적/역할], [분위기 한 줄].
Standing upright, front-facing, relaxed neutral pose, [손/팔 상태]. Calm neutral expression,
eyes open looking directly into the camera, mouth relaxed and closed. Clearly defined,
consistent identity features: [얼굴형]·[피부 결]·[머리(뒤로 넘김)]. Wardrobe: [의상 — 고정할 것].
Soft even frontal studio lighting, no harsh shadows, neutral seamless [배경색] background.
Eye-level camera, ~50mm lens, sharp focus on the face, [full body / head-and-shoulders] in frame,
photorealistic, high detail. No dramatic side lighting, no extreme angle, no motion blur, no props,
face never cropped or covered.
```

## 세팅
- 비율: 전신=세로(2:3/3:4), 얼굴 클로즈업=1:1 또는 4:5. 해상도는 2K 권장(얼굴 선명).
- 장수: 인물당 **정면 1장** 기본. 안정성 필요 시 **정면 1 + 얼굴 클로즈업 1**(같은 조명·같은 사람).

## 피할 것
단체/군중, 옆모습만, 극단 앵글, 짙은 분장·헬멧으로 이목구비 가림, 저화질·강한 필터,
서로 다른 사람 혼합, 얼굴에 이름/글자 새기기(화면에 글자로 찍힘).

## 뽑은 뒤
1. 이 스틸을 `@Image[N]` 인물 레퍼런스로 넣는다 (설명은 "얼굴·옷에만, 세트·빛은 안 가져옴" — `reference-numbering.md` §7-B, 분류 트리거 단어 금지).
2. 타임라인에서 **인물 나오는 매 컷** `@Image[N]의 [이름]…`으로 재호출(§7, 멀티컷).
3. 여러 클립에 걸쳐선 **같은 스틸을 그대로 재사용**해야 얼굴이 유지된다.
4. 가장 강한 락: 이 스틸을 키프레임으로 **i2v(이미지→영상)** 생성.


---

# 탑뷰 공간(블로킹) 레퍼런스 이미지

> 목적: 블로킹 보드/평면도 배경에 깔 **위에서 내려다본 공간 이미지**를 이미지 생성기로 뽑는다.
> 자동 회색 도식이 부정확할 때, 이 실사 탑뷰를 넣으면 동선·카메라를 그 위에 정확히 얹을 수 있다.

## 핵심 규칙
- **정투영 탑다운(직상방)** — 원근 기울기 없이 바로 위에서 내려다본 "돌하우스" 뷰
- **비율은 방의 가로:세로에 맞춘다** (예: 12m×8m 방 → 3:2). 어긋나면 좌표 박스와 안 맞아 늘어남
- 방 치수를 **미터로 명시** (가로·세로·천장)
- 가구는 **위치를 말로 배치**(좌측 벽·상단 벽·중앙·우측 코너 등)
- **사람 없음, 글자·치수선 없음** — 동선 마커를 얹을 자리이므로 깔끔하게
- 조명은 **부드럽고 균일**하게(그림자 과하면 배치 판독 방해)

## 프롬프트 골격 (영문, 빈칸만 채운다)
```
Top-down orthographic floor plan render of [공간 종류, 예: a modern office], dollhouse view
seen straight from above, no perspective tilt, aspect ratio [방 가로:세로, 예 3:2].
Room: rectangular, about [가로]m x [세로]m, [바닥 재질/색] floor, [벽 색] walls.
Layout (as seen from above):
- LEFT wall: [좌측 가구].
- TOP wall: [상단 가구].
- CENTER: [중앙 가구/구역].
- RIGHT wall/corner: [우측 가구].
- BOTTOM wall: [하단 가구]; [문/입구 위치].
- [기타: 화장실 코너·창문·특수 오브젝트].
Style: photorealistic 3D architectural render, soft even lighting, muted palette,
sharp clean edges, high detail. No people, no text labels, no measurement lines.
```

## 세팅
- 비율: 방 가로:세로와 동일하게 (3:2, 4:3 등). 해상도 2K 권장.
- 뽑은 뒤 → 편집기 「평면도 이미지 넣기」로 배경에 깔고, 그 위에 배우 동그라미·동선·카메라를 얹는다.

## 피할 것
비스듬한 3D 뷰(원근 기울기), 사람·글자·치수선 삽입, 방 비율과 다른 화면비(가구 위치 어긋남).
