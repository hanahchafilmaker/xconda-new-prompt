# -*- coding: utf-8 -*-
"""패널 좌표와 씨댄스 영문이 같은 자리를 가리키는지.

예전 영문은 '바로 뒤'를 right behind 로 옮겨 화면 오른쪽으로 보냈고,
같은 축의 앞뒤를 screen-left/right 로 적어 양옆으로 벌렸다.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "xconda-new-prompt")
sys.path.insert(0, os.path.join(SKILL, "assets"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import blocking_tools  # noqa: E402
from scene_compat import normalize  # noqa: E402
from build_s8_geom import build  # noqa: E402

FURNITURE = ("side desk", "steel locker", "file shelf", "shared desk", "storage locker",
             "보조대", "사물함", "책장", "데스크")
TRAPS = ("right behind", "is left standing", "screen-left and screen-right", "; reading ")


def scene():
    return normalize(build())


class TestFrameSpaceMatchesPanel(unittest.TestCase):
    def test_same_axis_is_depth_not_left_right(self):
        S = scene()
        part = S["parts"][0]
        cam = next(c for c in part["cameras"] if c["cutRef"] == "CUT8-1")
        ko, en = blocking_tools.frame_space_pair(S, part, cam)
        self.assertIn("현우는 프레임 중앙 전경", ko)
        self.assertIn("방대한은 프레임 중앙 후경", ko)
        self.assertIn("Hyunwoo is at frame-center in the foreground", en)
        self.assertIn("Daehan is at frame-center in the background", en)
        self.assertNotIn("왼쪽", ko)
        self.assertNotIn("오른쪽", ko)
        self.assertNotRegex(en, r"\bleft\b")
        self.assertNotRegex(en, r"\bright\b")

    def test_spatial_line_has_no_furniture_or_shot_size(self):
        S = scene()
        for part in S["parts"]:
            for cam in part["cameras"]:
                ko, en = blocking_tools.frame_space_pair(S, part, cam)
                if not en:
                    continue
                for word in FURNITURE:
                    self.assertNotIn(word, ko, cam["cutRef"])
                    self.assertNotIn(word, en, cam["cutRef"])
                self.assertNotIn("right behind", en)
                self.assertNotIn("reading", en)
                self.assertNotIn("미터", ko)
                self.assertNotRegex(en, r"\d")

    def test_lizard_sits_on_whoever_shares_the_panel_spot(self):
        S = scene()
        part_e = next(p for p in S["parts"] if p["partId"] == "E")
        cam = next(c for c in part_e["cameras"] if c["cutRef"] == "CUT8-17")
        ko, en = blocking_tools.frame_space_pair(S, part_e, cam)
        self.assertIn("깡철이는 현우의 어깨 위에 있다", ko)
        self.assertIn("Kkangchul is on Hyunwoo's shoulder", en)
        self.assertNotIn("Baksu's shoulder", en)

        part_c = next(p for p in S["parts"] if p["partId"] == "C")
        cam = next(c for c in part_c["cameras"] if c["cutRef"] == "CUT8-7")
        ko, en = blocking_tools.frame_space_pair(S, part_c, cam)
        self.assertIn("깡철이는 박수의 어깨 위에 있다", ko)
        self.assertIn("Kkangchul is on Baksu's shoulder", en)

    def test_insert_does_not_pull_office_cast_into_the_vision(self):
        S = scene()
        part = next(p for p in S["parts"] if p["partId"] == "C")
        cam = next(c for c in part["cameras"] if c["cutRef"] == "CUT8-9")
        ko, en = blocking_tools.frame_space_pair(S, part, cam)
        self.assertIn("차옥분", ko)
        self.assertNotIn("방대한", ko)
        self.assertNotIn("Daehan", en)

    def test_ots_shoulder_stays_frame_right(self):
        S = scene()
        part = S["parts"][0]
        cam = next(c for c in part["cameras"] if c["cutRef"] == "CUT8-3")
        ko, en = blocking_tools.frame_space_pair(S, part, cam)
        self.assertIn("방대한은 프레임 오른쪽 전경", ko)
        self.assertIn("Daehan is at frame-right in the foreground", en)
        self.assertIn("현우는 프레임 중앙 후경", ko)
        self.assertNotIn("right behind", en)

    def test_trap_words_are_rewritten_before_seedance(self):
        src = "the desk sitting out of focus right behind. Hyunwoo is left standing. ; reading under a third of the height"
        out = blocking_tools.seedance_position_safe(src)
        self.assertNotIn("right behind", out)
        self.assertIn("directly behind", out)
        self.assertNotIn("is left standing", out)
        self.assertIn("stays standing", out)
        self.assertNotIn("reading", out)
        self.assertIn("at under a third of the height", out)
        # 패널이 실제로 가른 좌우는 지우면 안 된다
        kept = blocking_tools.seedance_position_safe("Daehan is at frame-right in the foreground")
        self.assertIn("frame-right", kept)


class TestBakedPromptDoesNotMovePeople(unittest.TestCase):
    def test_index_copy_matches_panel_language(self):
        with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
            html = f.read()
        start = html.find("const EMBEDDED_SCENE = ")
        end = html.find(";\n(function autoload", start)
        self.assertGreater(start, 0)
        scene = html[start:end]
        for trap in TRAPS:
            self.assertNotIn(trap, scene, trap)
        self.assertIn("Hyunwoo is at frame-center in the foreground", scene)
        self.assertIn("stacked in depth on the same center axis", scene)
        self.assertIn("Hyunwoo's back fills frame-center in the foreground", scene)
        self.assertNotIn("a 손바닥만 한", scene)
