# -*- coding: utf-8 -*-
"""S#8 씬 JSON + 편집기 빌더.
build_s8_geom.py(좌표) + s8_content.py(10블록 본문)를 합쳐 scene-v1 JSON을 만들고,
blocking_tools 로 검수한 뒤 편집기 .html 을 생성한다.

실행: python3 tools/build_s8.py
"""
import json, math, os, sys

ROOT = "/home/user/xconda-new-prompt"
SKILL = os.path.join(ROOT, "xconda-new-prompt")
sys.path.insert(0, os.path.join(SKILL, "assets"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import blocking_tools
from scene_compat import normalize
from build_s8_geom import build, CUTS, DUR, APPEARS, CAM, ACT
import s8_content as C

OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

# ── 영문 "FIRST FRAME SPACE" 줄 — blocking_tools 의 실제 지오메트리 함수를 그대로 재사용 ──
SHOT_EN = [(0.60, "a close-up filling frame with the face"), (1.00, "a bust framing, chest up"),
           (1.50, "a medium, waist up"), (2.20, "a medium long, knees up"),
           (3.20, "a full shot with the whole body in frame"),
           (99.0, "a wide where the body reads at less than half the frame height")]
BG_EN = {"사물함": "the steel lockers", "창고 사물함": "the storage lockers", "보조대": "the side desk",
         "북측 책장": "the file shelves", "좌측 책장": "the file shelves", "공동 데스크": "the shared desks",
         "의자": "an empty office chair", "복사기": "the copier", "정수기": "the water cooler",
         "창고 문": "the storage door", "입구 나무문": "the wooden entrance door"}

def en_spatial(S, part, cam):
    names = {c["id"]: C.NAME_EN.get(c["id"], c["id"]) for c in S["refs"]["characters"]}
    R = blocking_tools.rects(S)
    bl = {k: blocking_tools.pts_of(v)[0] for k, v in part.get("blocking", {}).items()}
    c = (cam["x"] / 40, cam["y"] / 40); ang = cam.get("angle", 0); fov = cam.get("fov", 47)
    vis = []
    for cid, t in bl.items():
        if cid in blocking_tools.INSERT_ONLY and cam["cutRef"] != blocking_tools.INSERT_ONLY[cid]:
            continue
        rel = ((math.degrees(math.atan2(t[1] - c[1], t[0] - c[0])) - ang + 180) % 360) - 180
        if abs(rel) > fov / 2 + 2:
            continue
        seated = part["blocking"].get(cid, {}).get("pose") in ("sit", "앉다")
        vis.append((math.hypot(t[0] - c[0], t[1] - c[1]), cid,
                    "center" if abs(rel) < 7 else ("right" if rel > 0 else "left"),
                    blocking_tools.behind(R, c, t, own_chair=seated)))
    vis.sort()
    if not vis:
        return None
    out = []
    for i, (d, cid, side, (bg, bd)) in enumerate(vis):
        if cid in blocking_tools.CREATURES:
            out.append("%s — a %s, framed %s of frame perched on Baksu's shoulder"
                       % (names.get(cid, cid), blocking_tools.CREATURES[cid], side))
            continue
        H = 2 * d * math.tan(math.atan(math.tan(math.radians(fov) / 2) * 9 / 16))   # 프레임이 담는 실제 높이(m)
        size = next(t for lim, t in SHOT_EN if H < lim)
        s = "%s — %s of frame, %s" % (names.get(cid, cid), side, size)
        if bg:
            s += ", with %s sitting out of focus %s" % (BG_EN.get(bg, bg), "right behind" if bd < 1.2 else "far behind")
        if i > 0 and vis[0][0] / d < 0.75:
            s += "; reading %s the height of the nearer figure" % ("about half" if vis[0][0] / d > 0.45 else "under a third of")
        out.append(s)
    return "FIRST FRAME SPACE — " + " / ".join(out) + "."

# ── 블록 조립 ──────────────────────────────────────────────────────────
def refs_block(pid):
    order = C.ORDER[pid]
    people = [k for k in order if k in C.PEOPLE]
    bgs = [k for k in order if k not in C.PEOPLE]
    ko = ["이 번호가 실제 프롬프트 본문의 @Image번호와 같습니다. 이 파트에는 아래 %d장을 이 순서로 올립니다 — 인물(%s) → 배경(%s)."
          % (len(order), "·".join(C.NAME[k] for k in people), "·".join(C.NAME[k] for k in bgs))]
    en = ["Upload order is the numbering — upload %d images in the order below; these are the same @Image numbers used in the prompt body. Part-level order — people (%s) → backgrounds (%s)."
          % (len(order), ", ".join(C.NAME_EN[k] for k in people), ", ".join(C.NAME_EN[k] for k in bgs))]
    for i, k in enumerate(order, 1):
        role_ko, role_en, duty_ko, duty_en = C.ROLE[k]
        ko.append("· @Image%d — %s(씬 전역 태그: %s): %s. %s" % (i, C.NAME[k], C.GLOBAL[k], duty_ko, role_ko))
        en.append("· @Image%d — %s (scene-wide tag: %s): %s. %s" % (i, C.NAME_EN[k], C.GLOBAL[k], duty_en, role_en))
    n1 = len(people) + 1
    ko += ["레퍼런스 역할 락 — @Image1~@Image%d는 인물, @Image%d~@Image%d는 배경 레퍼런스다. 배경 레퍼런스에서 인물을 만들지 않는다." % (len(people), n1, len(order)),
           "정체성 고정 — 각 인물의 얼굴·머리·의상은 오직 해당 @Image 레퍼런스를 따르고 컷마다 흔들리지 않는다."]
    en += ["REFERENCE ROLE LOCK — @Image1-@Image%d are character references; @Image%d-@Image%d are background references. Do not create actors from background references." % (len(people), n1, len(order)),
           "Identity lock — each person's face, hair, and wardrobe follow only their @Image reference and never drift between cuts."]
    return "\n".join(ko), "\n".join(en)

def cam_block(pid):
    ko = ["모드: 멀티컷. 구간 중 드리프트 없음. 컷당 무브는 정확히 하나."]
    en = ["Mode: multi-cut. No drift within the section. One move per cut."]
    for (ref, _xy, fov, size, subj, _a, _ots) in CAM[pid]:
        s, e = next((s, e) for (r, s, e) in CUTS[pid] if r == ref)
        mv_ko, mv_en = C.MOVE[ref]
        ko.append("%s: %d°, %s, %s [%g-%g초] — 피사체 %s" % (ref, fov, size, mv_ko, s, e, C.NAME[subj]))
        en.append("%s: %d°, %s, %s [%g-%gs] — subject %s" % (ref, fov, size, mv_en, s, e, C.NAME_EN[subj]))
    ko.append("말하는 인물의 얼굴은 매 컷 프레임 중앙에 크게 잡힌다.")
    en.append("The speaker's face stays large and centered in frame in every cut.")
    return "\n".join(ko), "\n".join(en)

def b01(pid, tag):
    dur = DUR[pid]
    ko = ("S8 Part %s — 0과 위장사무실, 아침. 창문 없는 낡은 실내에 형광등 푸른빛과 책상 위 노란 스탠드 불빛만 켜져 있다. "
          "%g초 구성. %s 지정된 인물만 등장하며 엑스트라는 없다." % (pid, dur, C.TITLE[pid]))
    en = ("S8 Part %s — Division Zero's cover office, morning. A windowless old interior lit only by blue fluorescent "
          "light and the yellow desk lamps. A %g-second sequence. %s Only named cast appears; there are no extras."
          % (pid, dur, {"A": "An iron door opens onto the office where a new recruit meets the section chief.",
                        "B": "The section chief brings up the recruit's missing mother.",
                        "C": "A colleague steps out of a cabinet with a lizard on his shoulder.",
                        "D": "The lizard crawls onto the recruit and he panics.",
                        "E": "A blunt colleague warns him and leads him toward the cabinets."}[pid]))
    return ko, en

def b07():
    return ("배경 인물 명세 — 무시트, 엑스트라 없음.\n"
            "정지 금지 — 배경에 군중이 없으므로 얼어붙을 인물 자체가 없다. 화면에 잡히는 인물들은 각자의 "
            "호흡·시선·손 움직임을 클립 내내 계속한다.",
            "Background cast — none, no extras.\n"
            "Never freezes — with no crowd in the background there is no one to freeze. Every character in frame "
            "keeps breathing, shifting gaze, and moving their hands throughout the clip.")

def b09(dur):
    return ("디지털 시네마 룩, 1990년대 후반 한국 관공서의 낡은 질감, 미세한 필름 그레인. "
            "형광등 푸른빛과 백열 스탠드의 노란빛이 화면 안에서 나뉘어 보인다. 화면비 16:9. "
            "BGM 없음 — 형광등 웅웅거림, 종이 넘기는 소리, 낡은 벽시계 초침, 대사와 효과음만. 총 %g초.\n"
            "정체성 고정 — 각 인물의 얼굴·머리·의상은 오직 해당 @Image 레퍼런스를 따르고 컷마다 흔들리지 않는다. "
            "표정과 자세는 레퍼런스가 아니라 타임라인 서술을 따른다." % dur,
            "Digital cinema look, the worn texture of a late-1990s Korean government office, fine film grain. "
            "The blue fluorescent light and the yellow incandescent lamps read as separate pools within the frame. "
            "Aspect ratio 16:9. No BGM — fluorescent hum, pages turning, an old wall clock ticking, dialogue and SFX only. "
            "%g seconds total.\n"
            "Identity lock — each person's face, hair, and wardrobe follow only their @Image reference and never drift "
            "between cuts. Expression and posture follow the timeline description, not the reference." % dur)

def b10(pid):
    base_ko = ["· 인서트 컷을 제외한 모든 컷에서 말하는 인물의 얼굴이 크고 프레임 중앙에 머문다.",
               "· 각 인물은 서로 다른 개인이고, 화면에 같은 얼굴이 두 번 나타나지 않는다.",
               "· 인물들은 파트 내내 서 있는 자세를 유지한다.",
               "· 형광등 푸른빛과 스탠드 노란빛의 두 광원이 처음부터 끝까지 같은 자리에서 같은 세기로 유지된다.",
               "· 룸톤(형광등 웅웅거림·벽시계 초침)이 컷이 바뀌어도 끊기지 않고 이어진다."]
    base_en = ["· In every cut except inserts, the speaker's face stays large and centered in frame.",
               "· Each person is a distinct individual; no face exists twice on screen.",
               "· All characters remain standing throughout the part.",
               "· The two light sources — blue fluorescents and yellow desk lamps — hold the same position and intensity from first frame to last.",
               "· Room tone (fluorescent hum, wall clock ticking) continues unbroken across every cut."]
    extra = {
     "A": ("· 방대한은 안쪽 가장 높은 책상 뒤, 현우는 출입문 쪽 통로에 머물며 두 사람의 좌우 위치가 파트 내내 유지된다.",
           "· Daehan stays behind the tallest desk at the far end and Hyunwoo in the aisle by the entrance; their screen-left and screen-right positions hold throughout the part."),
     "B": ("· 방대한은 책상 뒤, 현우는 통로에 머물며 두 사람의 좌우 위치가 파트 내내 유지된다.",
           "· Daehan stays behind the desk and Hyunwoo in the aisle; their screen-left and screen-right positions hold throughout the part."),
     "C": ("· 박수는 사물함 쪽에서, 현우는 통로 중앙에서 자리하며 깡철이는 박수의 어깨 위에 머문다.",
           "· Baksu holds his ground by the lockers, Hyunwoo in the middle of the aisle, and Kkangchul stays on Baksu's shoulder."),
     "D": ("· 깡철이는 현우의 몸 위를 벗어날 때에도 손바닥만 한 크기를 유지한다.",
           "· Kkangchul stays palm-sized even as it moves across Hyunwoo's body."),
     "E": ("· 민희는 캐비넷 쪽에서, 현우는 통로에 머물며 마지막에 인물들이 캐비넷 안쪽으로 사라진다.",
           "· Minhee holds her ground by the cabinets and Hyunwoo in the aisle; the characters disappear into the cabinets at the end."),
    }
    ko = base_ko[:1] + [extra[pid][0]] + base_ko[1:]
    en = base_en[:1] + [extra[pid][1]] + base_en[1:]
    ko += ["잔류 네거티브 — 화면 아티팩트만", "화면 내 자막·워터마크·로고 없음."]
    en += ["RESIDUAL NEGATIVE — screen artifacts only", "No on-screen captions, watermark, or logo."]
    return "\n".join(ko), "\n".join(en)

BLOCK_T = [("01", "장면 컨텍스트", "SCENE CONTEXT"), ("02", "레퍼런스 / 범례", "ACTIVE REFERENCES"),
           ("03", "시네마틱 셋업", "LOCATION MAP AND LIGHTING"), ("04", "옵틱스·카메라·포맷", "FORMAT MODE / OPTICS / CAMERA"),
           ("05", "텍스트 락·소품·의상", "PROP AND WARDROBE LOCK"), ("06", "퍼포먼스·상태 오버레이", "PERFORMANCE"),
           ("07", "배경 인물 명세", "BACKGROUND CAST"), ("08", "초 단위 타임라인", "ACTION TIMELINE"),
           ("09", "스타일 & 출력", "STYLE / OUTPUT SETTINGS"), ("10", "포지티브 락", "POSITIVE LOCKS")]

def assemble():
    S = build()
    # refs (씬 전역 태그)
    chars = []
    for pid in ["A", "B", "C", "D", "E"]:
        for k in C.ORDER[pid]:
            if k in C.PEOPLE and not any(c["id"] == k for c in chars):
                role_ko, role_en, _dk, _de = C.ROLE[k]
                chars.append({"tag": C.GLOBAL[k], "id": k, "name": C.NAME[k], "role": role_ko})
    S["refs"]["characters"] = chars
    S["refs"]["backgrounds"] = [
        {"tag": C.GLOBAL["office_wide"], "name": C.NAME["office_wide"], "refImage": "office_angle1_wide.jpg",
         "note": "창문 없는 낡은 사무실 전체 — 이 씬의 기준 공간·조명"},
        {"tag": C.GLOBAL["office_cabinets"], "name": C.NAME["office_cabinets"], "refImage": "office_angle2_cabinets.jpg",
         "note": "철제 캐비넷이 늘어선 통로 — 인물들이 들고나는 곳"}]
    S["refs"]["props"] = [
        {"tag": "@Image_docs", "name": "서류더미", "refImage": "【소품 레퍼런스 없음 — 텍스트로만 고정】",
         "note": "누렇게 변색된 갱지, 사람 키만큼 쌓임"}]

    for p in S["parts"]:
        pid = p["partId"]; dur = DUR[pid]; who = APPEARS[pid]
        p["title"] = C.TITLE[pid]
        p["usesRefs"] = ["@Image%d" % i for i in range(1, len(C.ORDER[pid]) + 1)]
        loc = "@Image%d" % (len([k for k in C.ORDER[pid] if k in C.PEOPLE]) + 1)   # 첫 배경 태그
        k03, e03 = C.b03(loc)
        k05, e05 = C.b05(who)
        k02, e02 = refs_block(pid)
        k04, e04 = cam_block(pid)
        k01, e01 = b01(pid, loc)
        k07, e07 = b07()
        k09, e09 = b09(dur)
        k10, e10 = b10(pid)
        body = {"01": (k01, e01), "02": (k02, e02), "03": (k03, e03), "04": (k04, e04),
                "05": (k05, e05), "06": C.PERF[pid], "07": (k07, e07), "09": (k09, e09), "10": (k10, e10)}
        blocks = []
        for (n, t, tEn) in BLOCK_T:
            if n == "08":
                blocks.append({"n": n, "t": t, "tEn": tEn, "cuts": True,
                               "headKo": "[초 단위 타임라인] 대사는 각 컷 안에 '대사 — 화자: {대사}' 라벨 줄로 표기하고, 대사 직후 0.5초 마이크로 파즈를 둔다.",
                               "headEn": "[ACTION TIMELINE] Dialogue is labeled inside each cut as 'Dialogue — Speaker: {line}'. A 0.5s micro-pause follows each line of dialogue."})
            else:
                blocks.append({"n": n, "t": t, "tEn": tEn, "ko": body[n][0], "en": body[n][1]})
        p["prompt"]["blocks"] = blocks
        for cut in p["prompt"]["cuts"]:
            ref = cut["lb"].split(" · ")[0].strip()
            ko, en = C.CUT_TEXT[ref]
            # 배경 태그는 파트마다 로컬 번호가 다르므로 여기서 확정한다 (§7-C ①)
            loc = "@Image%d" % (C.ORDER[pid].index("office_wide") + 1)
            cab = ("@Image%d" % (C.ORDER[pid].index("office_cabinets") + 1)
                   if "office_cabinets" in C.ORDER[pid] else "")
            ko = [l.replace("{LOC}", loc).replace("{CAB}", cab) for l in ko]
            en = [l.replace("{LOC}", loc).replace("{CAB}", cab) for l in en]
            cut["ko"] = "\n".join(ko); cut["en"] = "\n".join(en)
            for ln in ko:
                if ln.startswith("대사 — "):
                    cut["speaker"] = ln.split(" — ")[1].split(":")[0]
                    cut["dlg"] = cut["dlgPlain"] = ln.split("{")[1].rstrip("}")
        # 보드 익스포트용 — 원문이 아니라 치환 완료된 컷 본문을 쓴다 ({LOC}/{CAB} 잔존 방지)
        by_ref = {c["lb"].split(" · ")[0].strip(): c for c in p["prompt"]["cuts"]}
        p["actions"] = [{"cutRef": ref, "actorId": cam[4], "actionType": "see_timeline",
                         "start": s, "end": e,
                         "text": by_ref[ref]["ko"].split("\n")[-1][:60]}
                        for (ref, s, e), cam in zip(CUTS[pid], CAM[pid])]
        p["dialogueSchedule"] = [{"actorId": next((x["id"] for x in chars if x["name"] == c["speaker"]), None),
                                  "speakerName": c["speaker"], "line": c["dlgPlain"],
                                  "start": float(c["tc"].split("-")[0].replace("초", "")),
                                  "end": float(c["tc"].split("-")[1].replace("초", ""))}
                                 for c in p["prompt"]["cuts"] if c["dlgPlain"]]
        p["blockingBoard"] = [{"actorId": k, "x": v["x"], "y": v["y"], "angle": v["angle"],
                               "pose": v["pose"], "path": v["path"]} for k, v in p["blocking"].items()]
    return S

def main():
    S = normalize(assemble())
    # 영문 FIRST FRAME SPACE 를 먼저 넣고(검수와 무관), 한국어는 sync 가 좌표에서 생성
    for p in S["parts"]:
        cams = {c["cutRef"]: c for c in p["cameras"]}
        for cut in p["prompt"]["cuts"]:
            cam = cams.get(cut["lb"].split(" · ")[0].strip())
            if not cam:
                continue
            ln = en_spatial(S, p, cam)
            if not ln:
                continue
            body = [l for l in cut["en"].split("\n") if not l.startswith("FIRST FRAME SPACE —")]
            body.insert(1, ln)
            cut["en"] = "\n".join(body)
    scene_path = os.path.join(OUT, "S8_scene.json")
    json.dump(S, open(scene_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = blocking_tools.sync(S)                     # 한국어 공간 문장(좌표에서 계산)
    json.dump(S, open(scene_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bad = blocking_tools.check(S)
    print("한국어 공간 문장 %d컷 삽입" % n)
    print("blocking_tools check: 문제 %d건" % len(bad))
    for b in bad:
        print("  ⚠", b)

    tpl = open(os.path.join(SKILL, "assets", "xconda_engine.html"), encoding="utf-8").read()
    old = "const EMBEDDED_SCENE = {};"
    assert tpl.count(old) == 1
    html = tpl.replace(old, "const EMBEDDED_SCENE = " + json.dumps(S, ensure_ascii=False, indent=1) + ";")
    ed = os.path.join(OUT, "S8_xconda_editor.html")
    open(ed, "w", encoding="utf-8").write(html)
    print("편집기: %s (%d bytes)" % (ed, len(html)))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
