# xconda-new-prompt

XCONDA(엑스콘다) — Seedance 2.5/2.0 영상 프롬프트 에디터 스킬.
장면 설명만 주면 4인 감독 팀(총괄·촬영·조명·미술) 관점으로 분석해 **씨댄스에 그대로 붙여넣는
영문 10블록 프롬프트**를 만들고, 결과물을 **한/영 2열 편집기 `.html` + 씬 JSON** 두 짝으로 준다.

## 저장소 구성

| 경로 | 무엇 |
|---|---|
| `xconda-new-prompt.skill` | 배포용 패키지(폴더를 zip한 것). Claude 데스크톱 앱 스킬 폴더에 그대로 넣는 파일 |
| `xconda-new-prompt/` | 그 패키지를 풀어둔 작업 사본 — 실제로 읽고 실행하는 곳 |
| `tests/`, `Makefile` | 스킬 도구가 이 환경에서 도는지 확인하는 회귀 테스트와 명령 모음 |

## 바로 써보기

```bash
make check          # 스킬 무결성 + 회귀 테스트 (validate.py · python · node · UI 렌더)
make engine         # 편집기 UI를 http://localhost:8080/ 로  ← 저장소 루트가 곧 UI
make setup-web      # UI 테스트용 jsdom 설치 (처음 한 번)
make check-scene S=tests/fixtures/scene_v1_sample.json   # 예제 씬 블로킹 검수 → "문제 0건"
```

### Windows — `make` 없이 실행

`make` 가 없는 Windows 에서는 **`engine.bat`** 을 쓰면 된다 (Python 3 필요 — `py` → `python` → `python3`
순서로 자동 탐지). 탐색기에서 더블클릭하거나 PowerShell/cmd 에서:

```powershell
.\engine.bat            # 빌드 + http://localhost:8080/ 서버 시작 (브라우저 자동 열림)
.\engine.bat 3000       # 포트 지정
```

`make engine` 의 두 단계를 직접 실행하는 것과 동일하다:

```powershell
python tools\build_editor.py    # ① 편집기 UI 빌드 (output/ → index.html)
python tools\serve.py 8080      # ② 서버 실행 (정지: Ctrl+C)
```

`make engine` 을 띄우면 **루트(`/`)를 여는 것만으로 씬이 이미 심긴 편집기 화면이 나온다.**
씬 JSON을 직접 끌어다 넣고 싶을 때만 `/engine`(빈 편집기)을 연다.

| URL | 무엇 |
|---|---|
| `/` | 편집기 UI — S8 씬 내장, 열자마자 파트 5개·컷 패널·10블록 프롬프트가 보임 |
| `/engine` | 스킬 원본 편집기 템플릿 — 빈 화면, 씬 JSON 드롭용 |
| `/scene` | 현재 UI에 심긴 씬 JSON |
| `/__status` | 서버·파일 상태 (스크립트 점검용) |

## v9.13.1 — "웹에서 UI가 안 보임" 고친 것

**증상**: 브라우저를 열면 디렉터리 목록만 나오고 편집기 화면이 안 보였다.

**원인** (둘 다 실제 확인한 것):

1. 저장소 루트에 `index.html`이 없었다. 그래서 `/` 는 파일 목록이었고, UI는
   `xconda-new-prompt/assets/xconda_engine.html` 라는 깊은 경로에 있었다.
2. 그 원본 편집기는 `const EMBEDDED_SCENE = {};` — **씬이 비어 있다.** 열어도 드롭존뿐이라
   "화면이 없다"고 보이기 쉽다. 씬이 심긴 편집기는 `tools/build_s8.py`가 `output/`에 만드는데,
   `output/`은 `.gitignore` 대상이라 **클론하면 아예 존재하지 않았다.**

**조치**:

| 바꾼 것 | 역할 |
|---|---|
| `index.html` (커밋됨) | 씬이 심긴 편집기 UI. `output/`이 아니라 루트에 두므로 클론해도 사라지지 않는다 |
| `tools/serve.py` | `/` → `index.html`, `/engine` → 빈 템플릿, `/scene`, `/__status` 를 주는 서버 (`0.0.0.0`) |
| `tools/build_editor.py` | `build_s8.py` 실행 → `output/` → `index.html` 로 복사 (`make engine-html`) |
| `tests/test_engine_ui_render.mjs` | 편집기를 jsdom에서 **실제로 실행**해 탭 5개·컷 패널·10블록·textarea가 그려지는지 검사 (`make test-ui`, `make check`에 포함) |
| `package.json` | 위 테스트의 dev 의존성 jsdom (`make setup-web`) |

UI 렌더 테스트는 빈 템플릿을 `index.html`에 덮어씌우면 15건이 실패하고 종료 1로 끝난다 —
"그냥 통과하는" 테스트가 아니라 실제로 화면을 본다.


에이전트가 이 저장소에서 스킬을 언제·어떻게 켜야 하는지는 [`AGENTS.md`](AGENTS.md)에 적어뒀다.

## v9.13.2 — 패널 위치가 씨댄스에서 옆으로 가던 것

컷 패널·프롬프트의 첫 프레임 줄은 앞뒤·중앙인데, 씨댄스에 붙는 영문이 그 자리를 다른 말로
적고 있었다. `right behind`(바로 뒤)는 화면 오른쪽으로, `is left standing`은 화면 왼쪽으로,
`screen-left and screen-right`는 같은 축의 앞뒤를 양옆으로 벌렸다. 첫 프레임 줄의 가구 이름은
그 가구를 인물의 자리로 읽혔다.

지금은 `blocking_tools.frame_space_pair`가 패널 좌표에서 **인물 / 프레임 좌·중·우 / 전경·중경·후경**
만 만들고, 복사 버튼이 남은 함정 단어를 한 번 더 걸러 낸다.

## v9.13 — 이 환경에 맞게 고친 것

스킬 v9.12는 문서·템플릿이 미터 기준 `room`으로 바뀌어 있었는데, 도구는 아직 예전 px 기준을 읽고
있어서 **이 저장소에서 그대로 실행하면 죽었다**. 실제로 재현한 증상과 조치:

| 증상 (수정 전 실제 출력) | 원인 | 조치 |
|---|---|---|
| `python3 scripts/validate.py` → `[경고] … name이 xconda-new-prompt가 아님`, 종료 1 | SKILL.md는 `name: "xconda-new-prompt"`(따옴표 있음)인데 점검기는 따옴표 없는 문자열만 찾음 | 따옴표 유무 둘 다 인정하도록 정규식 처리 + 어댑터 연결 상태 점검 추가 |
| `blocking_tools.py check examples/template_scene_v1.json` → `KeyError: 'items'` | 템플릿 `room`은 미터(`obstacles[]`), 도구는 px(`items[]`)를 읽음 | `assets/scene_compat.py` 신설 — 미터 → px(40px=1m) 자동 환산, 예전 px 씬은 무변환 통과 |
| 편집기에 정식 템플릿 씬을 넣으면 컷 패널이 안 나옴 (`room.centerPx` 없음) | 위와 같은 이유 (JS 쪽) | 편집기 `loadScene()`에 같은 규칙의 `normalizeRoom()` 추가 |
| `python3 assets/shot_language.py` → `FileNotFoundError: /home/claude/xconda_scene_s8.json` | 씬 경로가 그 머신 경로로 고정 | `python3 shot_language.py 씬.json [출력.json]` 또는 `XCONDA_SCENE` 환경변수로 받음 |

`make repack` 으로 위 수정이 들어간 `xconda-new-prompt.skill`을 다시 만들 수 있다.
`portals`(문·창)는 통로이므로 가구 목록에 넣지 않는다 — 넣으면 "동선이 가구를 관통한다"는 오탐이 난다.
