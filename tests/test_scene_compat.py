# -*- coding: utf-8 -*-
"""XCONDA 스킬 — 씬 JSON 호환 어댑터 + 블로킹 검수 회귀 테스트.

실행:  python3 -m unittest discover -s tests -v      (저장소 루트에서)
또는  make test

정식 템플릿(v9.10)의 room은 미터 기준이고 도구는 px(40px=1m)를 읽는다.
이 테스트는 그 사이를 잇는 scene_compat.normalize()와, normalize를 거쳐 도는
blocking_tools.check()가 실제로 문제를 잡아내는지 확인한다.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "xconda-new-prompt")
sys.path.insert(0, os.path.join(SKILL, "assets"))

import blocking_tools                      # noqa: E402
import scene_compat                        # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "scene_v1_sample.json")


def load(name):
    with open(os.path.join(ROOT, "tests", "fixtures", name), encoding="utf-8") as f:
        return json.load(f)


class TestSceneCompat(unittest.TestCase):
    def test_meter_room_becomes_px(self):
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        room = S["room"]
        self.assertEqual(room["centerPx"], [0.0, 0.0])
        self.assertEqual(room["widthPx"], 320.0)      # 8m × 40px
        self.assertEqual(room["depthPx"], 240.0)      # 6m × 40px
        self.assertEqual(len(room["items"]), 2)
        desk = next(i for i in room["items"] if i["name"] == "공동 데스크")
        self.assertEqual((desk["x"], desk["y"], desk["w"], desk["h"]), (-40.0, -40.0, 64.0, 32.0))
        self.assertTrue(next(i for i in room["items"] if i["name"] == "북측 책장")["blocksSight"])

    def test_portals_are_not_obstacles(self):
        """문·창은 통로다 — items에 들어가면 동선 검수가 오탐을 낸다."""
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        names = [i["name"] for i in S["room"]["items"]]
        self.assertNotIn("door_e", names)
        self.assertEqual(len(S["room"]["portals"]), 1)

    def test_meter_fields_survive(self):
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        self.assertEqual(S["room"]["center"], [0.0, 0.0])
        self.assertEqual(S["room"]["width"], 8.0)
        self.assertIn("obstacles", S["room"])

    def test_legacy_px_room_untouched(self):
        S = scene_compat.normalize(load("scene_legacy_sample.json"))
        self.assertEqual(S["room"]["centerPx"], [320, 240])
        self.assertEqual(len(S["room"]["items"]), 1)
        self.assertNotIn("_itemsFrom", S["room"])
        self.assertFalse(scene_compat.needs_normalize(S))

    def test_idempotent(self):
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        once = json.dumps(S, sort_keys=True, ensure_ascii=False)
        twice = json.dumps(scene_compat.normalize(S), sort_keys=True, ensure_ascii=False)
        self.assertEqual(once, twice)


class TestBlockingCheckThroughAdapter(unittest.TestCase):
    """정식 템플릿 형식(미터 room) 씬이 검수 도구를 끝까지 통과하는가."""

    def test_clean_scene_passes(self):
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        self.assertEqual(blocking_tools.check(S), [])

    def test_detects_actor_inside_furniture(self):
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        S["parts"][0]["blocking"]["hyunwoo"]["x"] = -40     # 공동 데스크 한가운데
        S["parts"][0]["blocking"]["hyunwoo"]["y"] = -40
        bad = blocking_tools.check(S)
        self.assertTrue(any("시작 위치가 가구 안" in b for b in bad), bad)

    def test_detects_off_anchor_fov(self):
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        S["parts"][0]["cameras"][0]["fov"] = 50             # §16 — 50° 금지
        bad = blocking_tools.check(S)
        self.assertTrue(any("화각 50° 가 앵커 9단계 밖" in b for b in bad), bad)

    def test_detects_lens_too_close(self):
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        cam = S["parts"][0]["cameras"][0]
        cam["x"], cam["y"] = 60, 40                         # 현우(40,20)에서 0.56m
        cam["angle"] = -153
        bad = blocking_tools.check(S)
        self.assertTrue(any("렌즈에서" in b for b in bad), bad)

    def test_detects_skipped_image_number(self):
        """두 번째 레퍼런스를 @Image2 → @Image3으로 바꾸면 2번이 빈다(§7-C 파트 로컬 번호 규칙)."""
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        part = S["parts"][0]
        part["usesRefs"] = ["@Image1", "@Image3"]
        for b in part["prompt"]["blocks"]:
            for k in ("ko", "en"):
                if b.get(k):
                    b[k] = b[k].replace("@Image2", "@Image3")
        for cut in part["prompt"]["cuts"]:
            cut["ko"] = cut["ko"].replace("@Image2", "@Image3")
            cut["en"] = cut["en"].replace("@Image2", "@Image3")
        bad = blocking_tools.check(S)
        self.assertTrue(any("@Image 번호를 건너뜀" in b for b in bad), bad)

    def test_sync_inserts_spatial_line(self):
        S = scene_compat.normalize(load("scene_v1_sample.json"))
        n = blocking_tools.sync(S)
        self.assertEqual(n, 1)
        ko = S["parts"][0]["prompt"]["cuts"][0]["ko"]
        self.assertIn("첫 프레임 공간 —", ko)


class TestOfficialTemplateStillLoads(unittest.TestCase):
    """빈 템플릿도 예외 없이 읽힌다(예전엔 KeyError: 'items'로 죽었다)."""

    def test_template_does_not_crash(self):
        tpl = os.path.join(SKILL, "examples", "template_scene_v1.json")
        with open(tpl, encoding="utf-8") as f:
            S = scene_compat.normalize(json.load(f))
        bad = blocking_tools.check(S)          # placeholder라 문제는 나오되, 죽지 않아야 한다
        self.assertIsInstance(bad, list)
        self.assertTrue(bad)


if __name__ == "__main__":
    unittest.main()
