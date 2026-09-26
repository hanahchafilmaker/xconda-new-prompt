# -*- coding: utf-8 -*-
"""S#8 위장사무실 — 지오메트리(방·가구·배우·카메라) 빌더.
프롬프트 본문은 아직 비우고, blocking_tools.check 가 0건이 되는 좌표만 먼저 확정한다.
좌표 규약: room 은 미터, 배우/카메라는 px(40px=1m)."""
import json, math, os, sys

SKILL = "/home/user/xconda-new-prompt/xconda-new-prompt"
sys.path.insert(0, os.path.join(SKILL, "assets"))
import blocking_tools
from scene_compat import normalize

PX = 40.0

ROOM = {
    "id": "office_s8", "kind": "위장사무실", "name": "0과 위장사무실",
    "center": [0.0, 0.0], "width": 9.0, "depth": 7.0, "height": 2.6,
    "obstacles": [
        # name, center(m), w(m), d(m), blocksSight
        ("보조대",     (0.0, -2.15), 1.6, 0.7, False),   # 대한 책상(서류더미)
        ("북측 책장",  (-2.25, -3.25), 3.5, 0.6, True),
        ("좌측 책장",  (-4.25, -1.0), 0.6, 3.0, True),
        ("공동 데스크", (-2.75, -0.5), 2.5, 1.0, False),
        ("의자",       (-2.75, 0.75), 0.5, 0.5, False),
        ("복사기",     (3.75, -1.75), 0.8, 0.7, False),
        ("정수기",     (-4.0, 2.25), 0.4, 0.4, False),
        ("사물함",     (-2.25, 3.0), 2.2, 0.6, True),    # 현우 뒤쪽 — 박수가 나오는 곳
        ("창고 사물함", (2.75, 3.0), 2.4, 0.6, True),    # 민희가 나오고 다 같이 들어가는 통로
    ],
    "portals": [
        {"id": "door_entry", "kind": "doorway", "center": [0.0, 3.45], "width": 1.0, "hdg": 0, "state": "closed"},
        {"id": "door_storage", "kind": "doorway", "center": [2.75, 3.3], "width": 0.9, "hdg": 0, "state": "closed"},
    ],
}

def rect_list():
    return [{"id": n.replace(" ", "_"), "name": n, "kind": "furniture",
             "center": list(c), "width": w, "depth": d, "hdg": 0, "blocksSight": s}
            for (n, c, w, d, s) in ROOM["obstacles"]]

# 배우 위치(px) — 파트별. (start, [path...])
ACT = {
 "daehan":   {"A": ((0, -104), []), "B": ((0, -104), []), "C": ((0, -104), []),
              "D": ((0, -104), []), "E": ((0, -104), [])},
 "hyunwoo":  {"A": ((0, 70), [(0, 10)]), "B": ((0, 10), []), "C": ((0, 10), []),
              "D": ((0, 10), []), "E": ((0, 10), [(90, 80)])},
 "baksu":    {"C": ((-90, 96), [(-28, 38)]), "D": ((-28, 38), []), "E": ((-28, 38), [(100, 100)])},
 "kkangchul":{"C": ((-90, 96), [(-28, 38)]), "D": ((-28, 38), [(0, 10)]), "E": ((0, 10), [(-28, 38)])},
 "minhee":   {"E": ((110, 96), [(40, -60), (110, 100)])},
 "chaokbun": {"C": ((-140, 60), [])},   # 인서트 전용 — 환영(굿당)
}

POSE = {"daehan": "서다", "hyunwoo": "서다", "baksu": "서다", "kkangchul": "서다",
        "minhee": "서다", "chaokbun": "서다"}

# 카메라: cutRef, (x,y), fov, shotSize, subject, angle, ots?
CAM = {
 "A": [("CUT8-1",  (0, 120),    63, "와이드",        "daehan",  -90, False),
       ("CUT8-2",  (0, 30),     47, "미디엄",        "daehan",  -90, True),
       ("CUT8-3",  (10, -126),  47, "미디엄",        "hyunwoo",  94, True)],
 "B": [("CUT8-4",  (30, 26),    29, "바스트",        "daehan", -103, False),
       ("CUT8-5",  (0, -124),   29, "바스트",        "hyunwoo",  90, True),
       ("CUT8-6",  (-40, 34),   29, "바스트",        "daehan", -113, False)],
 "C": [("CUT8-7",  (44, -44),   47, "미디엄 투샷",   "hyunwoo", 129, False),
       ("CUT8-8",  (10, 80),    29, "타이트 바스트", "baksu",  -132, False),
       ("CUT8-9",  (-140, 110), 84, "타이트 바스트", "chaokbun", -90, False),
       ("CUT8-10", (10, 80),    29, "타이트 바스트", "baksu",  -132, False)],
 "D": [("CUT8-11", (30, 50),    29, "타이트 바스트", "hyunwoo", -127, False),
       ("CUT8-12", (0, -126),   47, "미디엄 투샷",   "hyunwoo",  90, True),
       ("CUT8-13", (30, 70),    29, "타이트",        "kkangchul", -151, False),
       ("CUT8-14", (-40, 40),   29, "타이트 바스트", "hyunwoo", -143, False),
       ("CUT8-15", (-70, 70),   29, "타이트 바스트", "baksu",   -135, False)],
 "E": [("CUT8-16", (60, 40),    29, "미디엄",        "minhee",   48, False),
       ("CUT8-17", (-40, 40),   29, "타이트 바스트", "hyunwoo", -143, False),
       ("CUT8-18", (60, -40),   29, "타이트 바스트", "minhee",  161, False),
       ("CUT8-19", (-40, 40),   29, "타이트 바스트", "hyunwoo", -143, False),
       ("CUT8-20", (20, 120),   63, "미디엄",        "minhee",  -15, False),
       ("CUT8-21", (70, 60),    29, "타이트 바스트", "hyunwoo", -140, False)],
}

DUR = {"A": 15.0, "B": 18.0, "C": 12.0, "D": 19.5, "E": 26.0}
CUTS = {   # cutRef -> (시작, 끝)
 "A": [("CUT8-1", 0, 5), ("CUT8-2", 5, 10), ("CUT8-3", 10, 15)],
 "B": [("CUT8-4", 0, 6), ("CUT8-5", 6, 11), ("CUT8-6", 11, 18)],
 "C": [("CUT8-7", 0, 5.5), ("CUT8-8", 5.5, 8.5), ("CUT8-9", 8.5, 9), ("CUT8-10", 9, 12)],
 "D": [("CUT8-11", 0, 3), ("CUT8-12", 3, 9), ("CUT8-13", 9, 13), ("CUT8-14", 13, 16.5), ("CUT8-15", 16.5, 19.5)],
 "E": [("CUT8-16", 0, 5), ("CUT8-17", 5, 9), ("CUT8-18", 9, 14), ("CUT8-19", 14, 18), ("CUT8-20", 18, 23), ("CUT8-21", 23, 26)],
}
APPEARS = {"A": ["daehan", "hyunwoo"], "B": ["daehan", "hyunwoo"],
           "C": ["daehan", "hyunwoo", "baksu", "kkangchul", "chaokbun"],
           "D": ["daehan", "hyunwoo", "baksu", "kkangchul"],
           "E": ["daehan", "hyunwoo", "baksu", "kkangchul", "minhee"]}

def ang(cam, tgt):
    return round(math.degrees(math.atan2(tgt[1] - cam[1], tgt[0] - cam[0])))

def build(with_prompt=True):
    room = dict(ROOM); room["obstacles"] = rect_list()
    parts = []
    for pid in ["A", "B", "C", "D", "E"]:
        who = APPEARS[pid]
        blocking = {}
        for cid in who:
            (sx, sy), path = ACT[cid][pid]
            blocking[cid] = {"x": sx, "y": sy, "angle": 0, "pose": POSE[cid],
                             "path": [{"x": x, "y": y} for (x, y) in path]}
        cams = []
        for (ref, (cx, cy), fov, size, subj, a, ots) in CAM[pid]:
            c = {"cutRef": ref, "x": cx, "y": cy,
                 "target": list(blocking[subj]["x"] and [blocking[subj]["x"], blocking[subj]["y"]] or [0, 0]),
                 "fov": fov, "shotSize": size, "subject": subj,
                 "angle": ang((cx, cy), (blocking[subj]["x"], blocking[subj]["y"]))}
            if ots:
                c["ots"] = True
            cams.append(c)
        cuts = [{"tc": "%g-%g초" % (s, e), "lb": "%s · %s %d°" % (ref, size, fov),
                 "dlg": "", "speaker": "", "dlgPlain": "", "ko": "", "en": ""}
                for (ref, s, e) in CUTS[pid]]
        parts.append({"partId": pid, "title": "", "duration": DUR[pid], "mode": "멀티컷",
                      "appears": who, "usesRefs": [], "blocking": blocking, "cameras": cams,
                      "prompt": {"meta": {"ver": "v1", "level": "LEVEL 2"}, "blocks": [], "cuts": cuts}})
    return {"schema": "xconda-scene-v1", "sceneId": "S8",
            "title": "0과 위장사무실 — 신입 이현우의 첫날 아침", "model": "Seedance 2.5",
            "room": room, "refs": {"characters": [], "backgrounds": [], "props": [], "audio": [], "video": []},
            "parts": parts}

if __name__ == "__main__":
    S = normalize(build())
    bad = blocking_tools.check(S)
    print("문제 %d건" % len(bad))
    for b in bad:
        print("  ⚠", b)
