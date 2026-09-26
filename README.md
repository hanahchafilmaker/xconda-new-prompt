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
make check          # 스킬 무결성 + 회귀 테스트 (validate.py · python 12건 · node 12건)
make engine         # 편집기를 http://localhost:8080/xconda-new-prompt/assets/xconda_engine.html 로
make check-scene S=tests/fixtures/scene_v1_sample.json   # 예제 씬 블로킹 검수 → "문제 0건"
```

에이전트가 이 저장소에서 스킬을 언제·어떻게 켜야 하는지는 [`AGENTS.md`](AGENTS.md)에 적어뒀다.

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
