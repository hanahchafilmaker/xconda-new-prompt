# AGENTS.md — 이 저장소에서 에이전트가 지켜야 할 것

이 저장소는 **XCONDA(엑스콘다) Seedance 영상 프롬프트 스킬** 자체다.
`xconda-new-prompt.skill`(배포용 zip)과 그것을 풀어둔 `xconda-new-prompt/`(작업 사본)가 한 짝으로 들어 있다.

## 1. 스킬을 켜는 조건 (트리거)

아래 중 하나라도 해당하면 **다른 어떤 습관보다 먼저** `xconda-new-prompt/SKILL.md`를 읽고 그 규칙을 따른다.

- 문장에 `엑스콘다` · `XCONDA` · `Xconda` · `xconda` 가 어디에든 나온다
- 트리거 없이 "씨댄스 프롬프트 만들어줘 / 고쳐줘", "이 장면 영상 프롬프트로",
  "스토리보드로 프롬프트 만들어줘" 같은 요청이 온다
- "블로킹 보드에 등록해줘", "프리셋 만들어줘", "1-Click 대본", "모션 ID" 를 묻는다

응답 언어는 트리거가 정한다 — `엑스콘다`(한글)면 한국어, `XCONDA`(영문)면 영어.
단 **Seedance에 붙여넣을 최종 프롬프트와 편집기 오른쪽 열은 언제나 영문**이다.

## 2. 읽는 순서

1. `xconda-new-prompt/SKILL.md` — 「지금 유효한 핵심 규칙 10가지」를 먼저. 본문 734줄 전체가 아니라
   필요한 조항만. 상세는 `xconda-new-prompt/references/*.md`(23개)를 그 조항이 가리킬 때만 연다.
2. 씬 JSON을 만들 때는 **`xconda-new-prompt/examples/template_scene_v1.json`의 빈칸만 채운다.**
   프롬프트 10블록 문장은 `xconda-new-prompt/examples/template_10block_prompt.txt` 뼈대를 쓴다.
   (`references/scene-json-schema.md`: "이 문서와 템플릿이 다르면 템플릿이 우선")
3. 산출물은 **항상 두 짝** — ① 편집 가능한 `.html` 편집기(`assets/xconda_engine.html` 바탕)
   ② 대화창 코드블록으로 주는 씬 JSON. 프롬프트 텍스트만 던지면 규칙 위반(§15·§16).

## 3. 출력 전에 반드시 돌리는 명령

```bash
make check                      # 스킬 무결성 + 회귀 테스트 (validate.py · python · node)
make check-scene S=<씬.json>    # 블로킹 검수 — "문제 0건"이 목표 (§16 체크리스트)
make sync-scene  S=<씬.json>    # 좌표 → "첫 프레임 공간 —" 문장을 컷에 삽입 (한국어만)
make engine-html                # 웹에 올릴 편집기 UI(index.html) 재생성
```

`make check` 에는 UI 렌더 검사(`make test-ui`)도 들어 있다 — 편집기를 jsdom에서 실제로 실행해
탭·컷 패널·10블록이 그려지는지 본다. (jsdom 설치: `make setup-web`)

`make engine` 을 띄우면 브라우저에서 **저장소 루트(`/`)가 곧 편집기 UI**다 — 씬이 이미 심겨 있어
열자마자 파트 탭·컷별 패널·10블록 프롬프트가 나온다. 씬 JSON을 직접 끌어다 넣을 때만
`/engine`(빈 템플릿)을 쓴다.

**"웹에서 UI가 안 보임" 이라고 하면** — 루트의 `index.html`이 없거나 낡은 것이다.
`make engine-html` 로 다시 만들고 `make test-ui` 로 렌더를 확인한다.

## 4. 좌표 규약 (헷갈리기 쉬움)

- **방(room)**: 정식 템플릿은 **미터** — `center` / `width` / `depth` / `obstacles[]`(미터) / `portals[]`.
- **배우 `blocking.x,y` · 카메라 `x,y` · 동선 `path`**: 스키마와 무관하게 **px, 40px = 1m**.
- 도구(`blocking_tools.py`, 편집기)는 예전 px 형식(`centerPx`/`widthPx`/`depthPx`/`items[]`)을 읽는다.
  그 사이는 `assets/scene_compat.py`(파이썬)와 편집기 안 `normalizeRoom()`(JS)이 자동으로 메꿔준다 —
  미터 room을 주면 px 필드를 채우고, 이미 px인 예전 씬은 그대로 통과한다. `portals`(문·창)는
  사람이 지나가는 통로이므로 `items`에 넣지 않는다.
- 좌표 숫자는 **프롬프트 본문에 절대 쓰지 않는다** — 씨댄스가 숫자를 연출로 오인한다.

## 5. 고치지 말 것

- `SKILL.md` frontmatter의 `name: "xconda-new-prompt"` — 스킬 인식에 쓰인다.
- 편집기의 v9.10 정책: 이미지 없음 · 좌표 드래그 편집 없음 · 하단 버튼은 프롬프트 복사 2개(영/한)뿐 ·
  씬 JSON 다운로드 버튼 없음.
- `assets/scene_compat.py`와 편집기 `__ROOM_COMPAT__` 블록의 40px=1m 환산 — 한쪽만 바꾸면
  파이썬 검수와 편집기 그림이 어긋난다 (`make test`, `make test-js`가 둘을 대조한다).

## 6. 파일 구조

```
index.html                       웹에 보이는 편집기 UI (씬 내장) — make engine-html 로 재생성
tools/serve.py                   편집기를 웹에 띄우는 서버 (/ · /engine · /scene · /__status)
tools/build_editor.py            build_s8.py → output/ → index.html
tools/build_s8.py                S#8 씬 JSON + 편집기 빌더
xconda-new-prompt.skill          배포용 패키지(폴더를 zip한 것) — make repack 으로 갱신
xconda-new-prompt/               스킬 작업 사본 (실제로 읽고 실행하는 곳)
  SKILL.md                       스킬 본문 — 트리거·규칙 전부
  APPLY.md                       교체·설치 안내
  assets/    xconda_engine.html  편집기(한/영 2열 + 컷별 패널)
             blocking_tools.py   check(블로킹 검수) · sync(좌표→공간 문장)
             scene_compat.py     미터 room ↔ px room 어댑터
             shot_language.py    좌표 → 샷 언어 (S8 기준 1회용, 경로 인자 받음)
             motion_index.json   모션 클립 사전 (§18)
  references/  조항별 상세 문서 23개
  examples/    정식 템플릿 2개 + 예제
  scripts/validate.py            스킬 자체 무결성 점검기
tests/                           위 어댑터·검수 회귀 테스트 (python + node)
  test_engine_ui_render.mjs      편집기를 jsdom에서 실제로 실행 — UI가 그려지는지 본다
Makefile                         make check / check-scene / sync-scene / engine / engine-html / repack
```
