# XCONDA NEW PROMPT 스킬 — 이 저장소에서 쓰는 명령 모음
#
#   make check    스킬 무결성 + 회귀 테스트 전부 (validate.py + python + node)
#   make validate 스킬 무결성만 (스킬 자체 점검기)
#   make test     파이썬 회귀 테스트 (씬 JSON 호환 · 블로킹 검수)
#   make test-js  편집기(xconda_engine.html) room 호환 블록 테스트
#   make check-scene S=path/to/scene.json   씬 JSON 블로킹 검수 (0건이 목표)
#   make sync-scene  S=path/to/scene.json   좌표 → "첫 프레임 공간" 문장 삽입
#   make engine   편집기를 브라우저에서 열 수 있게 로컬 서버 띄우기 (0.0.0.0:8080)
#   make repack   폴더 내용으로 xconda-new-prompt.skill 다시 만들기
#   make extract  .skill 압축을 xconda-new-prompt/ 로 풀기 (덮어씀)

SKILL   := xconda-new-prompt
ARCHIVE := xconda-new-prompt.skill
PORT    ?= 8080
S       ?= tests/fixtures/scene_v1_sample.json

.PHONY: check validate test test-js check-scene sync-scene engine repack extract clean-pyc

check: validate test test-js
	@echo "\n[확인 완료] 스킬 무결성 · 파이썬 · 편집기 JS 모두 통과"

validate:
	cd $(SKILL) && python3 scripts/validate.py

test:
	python3 -W ignore -m unittest discover -s tests -v

test-js:
	node tests/test_engine_room_compat.mjs

check-scene:
	python3 $(SKILL)/assets/blocking_tools.py check $(S)

sync-scene:
	python3 $(SKILL)/assets/blocking_tools.py sync $(S)

engine:
	@echo "편집기  : http://localhost:$(PORT)/$(SKILL)/assets/xconda_engine.html"
	@echo "예제 씬 : http://localhost:$(PORT)/tests/fixtures/scene_v1_sample.json"
	python3 -m http.server $(PORT) --bind 0.0.0.0

repack:
	@rm -f $(ARCHIVE)
	zip -r -q -X $(ARCHIVE) $(SKILL) -x '*/__pycache__/*' '*.pyc'
	@echo "$(ARCHIVE) 다시 만듦:"
	@unzip -l $(ARCHIVE) | tail -2

extract:
	unzip -o -q $(ARCHIVE)
	@echo "$(ARCHIVE) → $(SKILL)/ 풀림"

clean-pyc:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} + ; true
