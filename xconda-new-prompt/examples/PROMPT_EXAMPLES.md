# 프롬프트 예제 — 10블록 뼈대와 카테고리 노트

> 완성 프롬프트를 통째로 외우기보다, 이 뼈대에 장면을 끼워 넣는 연습용입니다.
> 블록 규칙은 SKILL.md §5(10블록)·§6(포지티브 락)·§7(@태그)을 따릅니다.

> **정식 채우기용 템플릿**: `examples/template_10block_prompt.txt`(프롬프트) · `examples/template_scene_v1.json`(씬 JSON, v9.10). 아래 뼈대는 요약본이고, 실제 작업은 이 템플릿의 빈칸을 채운다.

## 공통 10블록 뼈대 (영문 열 기준)

```
01 SCENE CONTEXT     : one line — who / where / doing what / tone
02 ACTIVE REFERENCES : @Image1..N 인물 → 배경 → 소품, @Audio, @Video (번호 씬 고정)
03 LOCATION MAP/LIGHT: 미터 앵커 + 4단 깊이 + 광원 방향·색온도 (여기서만)
04 OPTICS/CAMERA     : 화각(°, 9단계 앵커) · 무브 · 얼굴 프레임 중앙 규칙 (컷 안엔 카메라 안 씀)
05 PROP/WARDROBE LOCK: 소품·의상 형태·재질·색 (여기서만)
06 PERFORMANCE       : 얼굴 정체성 유지 + 표정·상태 오버레이
07 BACKGROUND CAST   : 배경 인물 4요소(얼굴 다양성·복장·행동 루프·정지 금지)
08 ACTION TIMELINE   : 초 단위 비트, 액션·타이밍 (여기서만) · 대사는 화자 라벨 별도 줄
09 STYLE/OUTPUT      : 매체감·화질·정체성 고정 한 줄
10 POSITIVE LOCKS    : "유지할 상태"로. 잔류 네거티브 최대 3줄(화면 아티팩트만)
```

## 카테고리별 주의 노트

- **대화(dialogue)**: 08번 대사는 화자 라벨 별도 줄 + 직후 0.5s beat. 얼굴 프레임 중앙(§10-2).
- **액션(action)**: 유혈 등급 먼저 결정(기본 B) → `references/action-gore.md`. 컷 연결 6규칙(`cut-linking.md`).
- **넓은 공간(establishing)**: 03번 미터 앵커 + 4단 깊이 필수(`framing-and-scale.md`). 확립 컷 84°/107°.
- **군중(crowd)**: 07번 4요소 + 얼굴 다양성 5축. 앞줄만 얼굴 살리고 뒤는 흐림.
- **원테이크(oner)**: 04번 "하나의 연속 샷" 명시 + 08번 헤더에 "컷 아님, 시간 비트" 명시.

> 실제 완성 예제가 필요하면, 위 뼈대에 장면을 넣어 XCONDA로 생성한 결과물(.html)을 이 폴더에 보관하세요.
