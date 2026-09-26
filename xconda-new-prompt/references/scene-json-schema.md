# XCONDA 씬 JSON 스키마 (scene-v1 · v9.10)

> **한 줄로**: 편집기 `.html`은 사람이 읽는 UI, 씬 `.json`은 기계(블로킹 보드)가 읽는 데이터.
> 씬 JSON은 좌표·동선·시간 데이터를 담고, 프롬프트 문장은 `prompt` 블록에만 사본으로 둔다.

## ★ 정식 템플릿이 유일한 기준
**씬 JSON을 만들 때는 `examples/template_scene_v1.json`(v9.10)의 빈칸 `[ ]`만 채운다.**
이 문서와 템플릿이 다르면 **템플릿이 우선**한다. `_comment*` 키는 설명용이므로 실제 파일에 넣지 않는다.

## 구조 요약 (template_scene_v1.json 기준)
- `schema`: `"xconda-scene-v1"` 고정 · `sceneId` · `title` · `model`("Seedance 2.5"/"2.0")
- `room`: 공유 공간 — `kind`·`name`·`center/width/depth/height`(미터) · `obstacles[]`(가구) · `portals[]`(문·창, `state`)
- `refs`: 씬 전체 레퍼런스(번호 고정, 인물→배경→소품→오디오→비디오)
  - `characters[]`{tag,id,name} · `backgrounds[]`{tag,name,refImage} · `props[]`{tag,name,refImage,note} · `audio[]` · `video[]`
- `parts[]`: 30초 제한으로 나눈 파트. 공간·인물은 공유, 파트는 "누가·어디·카메라·프롬프트"만.
  - `partId`·`title`·`duration`·`mode`("멀티컷"/"원테이크")·`appears[]`·`usesRefs[]`
  - `blocking`: {actorId:{x,y,angle,pose,path[]}} — 좌표·동선
  - `cameras[]`: {cutRef,x,y,target,fov,shotSize,subject,angle}
  - `prompt`: {meta, blocks[10], cuts[]} — 프롬프트 사본(문장은 여기만)

## v9.10 보드 익스포트 확장 필드 (parts[] 안, 추가 필드 — 기존 blocking/prompt를 대체하지 않음)
- `dialogueSchedule[]`: {actorId|null, speakerName, line(중괄호 제외), start, end}
- `actions[]`: {cutRef, actorId|null, actionType(동사형 태그), start, end, text}
- `blockingBoard[]`: {actorId, x, y, angle, pose, path[]}

## 채우기 규칙
- 대사는 `prompt.cuts`/타임라인 안에서 한/영 모두 `대사 — 화자: {대사}` 라벨 줄로. 대사 원문은 `{중괄호}`.
- 좌표는 JSON에만, 프롬프트 문장은 편집기 HTML에만(§13-B 역할 분리).
- 번호(@Image)는 씬 전체 고정 → `references/reference-numbering.md`.
- 프롬프트 10블록 문장 템플릿은 `examples/template_10block_prompt.txt`.
