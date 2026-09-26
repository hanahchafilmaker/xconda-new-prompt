# -*- coding: utf-8 -*-
"""좌표 → 첫 프레임 공간 줄. 문구는 blocking_tools.frame_space_pair 한 곳만 쓴다.

사용법:  python3 shot_language.py scene.json [out.json]
         (경로를 안 주면 환경변수 XCONDA_SCENE, 그것도 없으면 예전 기본 경로를 쓴다)

담는 것은 인물 / 프레임 좌·중·우 / 전경·중경·후경 뿐이다.
가구 이름, "right behind", "reading ... the height" 는 씨댄스가 사람을 다른 곳으로 옮기므로 쓰지 않는다.

주의: OVR 컷 오버라이드와 미리보기 컷(CUT8-*)은 S8 기준이다.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_compat import normalize          # 미터 room → px room.items (없으면 무변환 통과)
import blocking_tools

DEFAULT_SCENE = os.environ.get("XCONDA_SCENE", "/home/claude/xconda_scene_s8.json")
SCENE_PATH = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCENE
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else SCENE_PATH
if not os.path.exists(SCENE_PATH):
    sys.exit("씬 파일을 찾을 수 없다: %s\n사용법: python3 shot_language.py scene.json [out.json]" % SCENE_PATH)

S = normalize(json.load(open(SCENE_PATH, encoding="utf-8")))

OVR = {("A","CUT8-2"):{"hyunwoo":(15.50,10.40)}, ("A","CUT8-3"):{"hyunwoo":(15.50,10.40)},
       ("E","CUT8-18"):{"minhee":(12.40,8.80)}, ("E","CUT8-19"):{"minhee":(12.40,8.80)},
       ("E","CUT8-20"):{"minhee":(12.40,8.80)}}

def line(part, cam):
    # 문구는 blocking_tools.frame_space_pair 한 곳만. 여기서 다시 쓰면 "right behind"가 되살아난다.
    return blocking_tools.frame_space_pair(S, part, cam, OVR)

n = 0
for p in S["parts"]:
    cams = {c["cutRef"]: c for c in p.get("cameras", [])}
    for cut in (p.get("prompt") or {}).get("cuts", []):
        cam = cams.get(cut["lb"].split(" · ")[0].strip())
        if not cam:
            continue
        ko, en = line(p, cam)
        if not ko:
            continue
        bko = [l for l in cut["ko"].split("\n") if not l.startswith("첫 프레임 공간 —")]
        ben = [l for l in cut["en"].split("\n") if not l.startswith("FIRST FRAME SPACE —")]
        bko.insert(1, ko); ben.insert(1, en)
        cut["ko"] = "\n".join(bko); cut["en"] = "\n".join(ben); n += 1
json.dump(S, open(OUT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("샷 언어로 교체: %d컷 → %s" % (n, OUT_PATH))
# 미리보기: S8 씬이면 그 대표 컷 3개, 아니면 공간 문장이 들어간 첫 3컷
PREVIEW = (("A", "CUT8-2"), ("C", "CUT8-7"), ("E", "CUT8-20"))
shown = 0
for pid, ref in PREVIEW:
    p = next((q for q in S["parts"] if q["partId"] == pid), None)
    if not p:
        continue
    for cut in (p.get("prompt") or {}).get("cuts", []):
        if cut.get("lb", "").startswith(ref):
            print("\n[%s %s]\n%s\n%s" % (pid, ref, cut["ko"].split("\n")[1], cut["en"].split("\n")[1]))
            shown += 1
if not shown:
    for p in S["parts"]:
        for cut in (p.get("prompt") or {}).get("cuts", []):
            kl = [l for l in cut.get("ko", "").split("\n") if l.startswith("첫 프레임 공간 —")]
            el = [l for l in cut.get("en", "").split("\n") if l.startswith("FIRST FRAME SPACE —")]
            if kl and el:
                print("\n[%s %s]\n%s\n%s" % (p["partId"], cut.get("lb", ""), kl[0], el[0]))
                shown += 1
            if shown >= 3:
                break
        if shown >= 3:
            break
