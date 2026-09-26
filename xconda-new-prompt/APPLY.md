# XCONDA 완전 교체용 폴더 (v9.9 슬림 + 개선 반영)

기존 xconda-new-prompt 스킬을 **통째로 교체**해도 되는 완전본입니다.

## 이번 세션 반영 내용
- SKILL.md 슬림화: 1,677줄 → 약 328줄 (상세는 references로 무손실 이동)
- 죽은 `@board 좌표 부록` 삭제
- 엔진(assets/xconda_engine.html): 회색 도식 제거 + 평면도/레퍼런스 이미지 직접 넣기
- ② 모델 사양 분리: `references/model-profile.md`
- ③ 문제 해결표 신설: `references/troubleshooting.md`
- ④ 프롬프트 예제: `examples/PROMPT_EXAMPLES.md`
- ⑤ 무결성 점검기: `scripts/validate.py`

## 적용
기존 xconda-new-prompt 폴더를 이 폴더로 교체. (실제 반영은 스킬/플러그인이 설치된 곳 — 보통 데스크톱 앱 — 에서)
불안하면 기존 폴더를 백업해두고 교체하세요.

## 교체 후 자가 점검
스킬 루트에서:  python3 scripts/validate.py
→ "[통과]" 나오면 필수 파일·references 링크 이상 없음.
