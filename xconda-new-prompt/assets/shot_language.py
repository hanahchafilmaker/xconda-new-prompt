# -*- coding: utf-8 -*-
"""좌표 → 샷 언어. 미터는 쓰지 않는다.
거리는 샷 사이즈로, 위치는 프레임 좌·중·우로, 깊이는 크기 비교와 가림 관계로 옮긴다.

사용법:  python3 shot_language.py scene.json [out.json]
         (경로를 안 주면 환경변수 XCONDA_SCENE, 그것도 없으면 예전 기본 경로를 쓴다)

주의: 이 스크립트는 S8 씬 기준으로 맞춰진 1회용 도구다 — 인물 id(hyunwoo/daehan/…),
`OVR` 컷 오버라이드, 하단 미리보기 컷(CUT8-*)이 그 씬에 고정돼 있다. 다른 씬에 쓰려면
그 세 곳을 먼저 고친다. 좌표 → 샷 언어 변환 규칙(shot/behind/line)은 그대로 재사용된다.
"""
import json, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_compat import normalize          # 미터 room → px room.items (없으면 무변환 통과)

DEFAULT_SCENE = os.environ.get("XCONDA_SCENE", "/home/claude/xconda_scene_s8.json")
SCENE_PATH = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCENE
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else SCENE_PATH
if not os.path.exists(SCENE_PATH):
    sys.exit("씬 파일을 찾을 수 없다: %s\n사용법: python3 shot_language.py scene.json [out.json]" % SCENE_PATH)

S = normalize(json.load(open(SCENE_PATH, encoding="utf-8")))
R = [(it["name"], it["x"]/40, it["y"]/40, it["w"]/40, it["h"]/40) for it in S["room"]["items"]]
PERSON = 1.70

KO_NAME = {"hyunwoo":"현우","daehan":["방대한","대한"],"baksu":"박수","minhee":"민희",
           "kkangchul":"깡철이","chaokbun":"차옥분"}
EN_NAME = {"hyunwoo":"Hyunwoo","daehan":"Daehan","baksu":"Baksu","minhee":"Minhee",
           "kkangchul":"Kkangchul","chaokbun":"Cha Okbun"}

def tag_map(part):
    """02번 선언에서 이 파트의 태그를 읽는다. 파트마다 번호가 다르므로 하드코딩하지 않는다."""
    b = [x for x in part["prompt"]["blocks"] if x["n"] == "02"][0]
    ko, en = {}, {}
    for line in b["ko"].split("\n"):
        m = re.match(r"· (@(?:Image|Video)\d+) — ([^ ·(]+)", line)
        if not m: continue
        tag, name = m.group(1), m.group(2)
        for cid, names in KO_NAME.items():
            for nm in ([names] if isinstance(names, str) else names):
                if name.startswith(nm):
                    ko[cid] = "%s의 %s" % (tag, nm); en[cid] = "%s %s" % (tag, EN_NAME[cid])
    return ko, en

BKO = {"사물함":"철제 사물함","서랍장":"서랍장","공동 데스크":"공동 데스크","보조대":"보조 책상","L형 소파":"L형 소파",
       "티 테이블":"금속 티 테이블","좌측 책장":"서류 책장","북측 책장":"서류 책장","게시판":"코르크보드",
       "의자":"빈 사무용 의자","복사기":"복사기","정수기":"정수기","창고 사물함":"창고 사물함",
       "입구 나무문":"나무 출입문","창고 문":"창고 문"}
BEN = {"사물함":"the steel lockers","서랍장":"the cabinet","공동 데스크":"the shared desks","보조대":"the side desk",
       "L형 소파":"the L-shaped sofa","티 테이블":"the metal coffee table","좌측 책장":"the file shelves",
       "북측 책장":"the file shelves","게시판":"the corkboard","의자":"an empty office chair","복사기":"the copier",
       "정수기":"the water cooler","창고 사물함":"the storage locker","입구 나무문":"the wooden entrance door",
       "창고 문":"the storage door"}

# 프레임 세로가 담는 높이 → 샷 사이즈 (16:9 기준)
def shot(d, hfov):
    vf = 2*math.atan(math.tan(math.radians(hfov)/2)*9/16)
    H = 2*d*math.tan(vf/2)
    if H < 0.60:  return "얼굴이 화면을 채우는 클로즈업", "a close-up filling frame with the face"
    if H < 1.00:  return "가슴 위까지 잡히는 바스트", "a bust framing, chest up"
    if H < 1.50:  return "허리 위까지 잡히는 미디엄", "a medium, waist up"
    if H < 2.20:  return "무릎 위까지 잡히는 미디엄 롱", "a medium long, knees up"
    if H < 3.20:  return "전신이 다 들어오는 풀샷", "a full shot with the whole body in frame"
    return "전신이 화면 높이의 절반 이하로 작게 들어오는 와이드", "a wide where the body reads at less than half the frame height"

def josa(w, a="이", b="가"):
    ch = w[-1]
    return w + (a if ("가" <= ch <= "힣" and (ord(ch)-0xAC00) % 28) else b)

def behind(cam, t, reach=6.5, own=None):
    vx, vy = t[0]-cam[0], t[1]-cam[1]; n = math.hypot(vx, vy) or 1
    vx, vy = vx/n, vy/n; d = 0.25
    while d < reach:
        x, y = t[0]+vx*d, t[1]+vy*d
        for nm, ox, oy, w, h in R:
            if abs(x-ox) <= w/2 and abs(y-oy) <= h/2:
                if own and nm == "의자" and math.hypot(ox-t[0], oy-t[1]) < 0.7:
                    continue          # 앉은 사람이 깔고 앉은 의자는 배경이 아니다
                return nm, d
        d += 0.15
    return None, None

OVR = {("A","CUT8-2"):{"hyunwoo":(15.50,10.40)}, ("A","CUT8-3"):{"hyunwoo":(15.50,10.40)},
       ("E","CUT8-18"):{"minhee":(12.40,8.80)}, ("E","CUT8-19"):{"minhee":(12.40,8.80)},
       ("E","CUT8-20"):{"minhee":(12.40,8.80)}}

def line(part, cam):
    NKO, NEN = tag_map(part)
    bl = {k: (v["x"]/40, v["y"]/40) for k, v in part["blocking"].items()}
    bl.update(OVR.get((part["partId"], cam["cutRef"]), {}))
    c = (cam["x"]/40, cam["y"]/40); ang = cam.get("angle", 0); fov = cam.get("fov", 47)
    vis = []
    for cid, t in bl.items():
        if cid == "chaokbun" and cam["cutRef"] != "CUT8-9":
            continue          # 인서트 전용 인물 — 본편 컷의 공간 계산에 넣지 않는다
        rel = ((math.degrees(math.atan2(t[1]-c[1], t[0]-c[0]))-ang+180) % 360)-180
        if abs(rel) > fov/2+2:
            continue
        vis.append((math.hypot(t[0]-c[0], t[1]-c[1]), cid,
                    "중앙" if abs(rel) < 7 else ("오른쪽" if rel > 0 else "왼쪽"),
                    "center" if abs(rel) < 7 else ("right" if rel > 0 else "left"),
                    behind(c, t, own=(part["blocking"].get(cid, {}).get("pose") in ("sit", "앉다")))))
    vis.sort()
    if not vis:
        return None, None
    ko, en = [], []
    for i, (d, cid, sko, sen, (bg, bd)) in enumerate(vis):
        if cid == "kkangchul":
            k = "%s — 손바닥만 한 도마뱀, 프레임 %s에서 박수의 어깨 위에 올라앉은 채 함께 잡힌다" % (NKO[cid], sko)
            e = "%s — a palm-sized lizard perched on Baksu's shoulder, framed with him %s of frame" % (NEN[cid], sen)
            ko.append(k); en.append(e); continue
        k1, e1 = shot(d, fov)
        k = "%s — 프레임 %s, %s" % (NKO.get(cid, cid), sko, k1)
        e = "%s — %s of frame, %s" % (NEN.get(cid, cid), sen, e1)
        if bg:
            near = bd < 1.2
            k += ", %s %s 초점이 풀린 채 놓인다" % ("바로 뒤에" if near else "그 너머 깊은 곳에", josa(BKO.get(bg, bg)))
            e += ", with %s sitting out of focus %s" % (BEN.get(bg, bg), "right behind" if near else "far behind")
        if i > 0:
            ratio = vis[0][0]/d
            if ratio < 0.75:
                k += "; 앞의 인물보다 키가 %s 작게 보이는 깊이" % ("절반쯤" if ratio > 0.45 else "3분의 1 이하로")
                e += "; reading %s the height of the nearer figure" % ("about half" if ratio > 0.45 else "under a third of")
        ko.append(k); en.append(e)
    return ("첫 프레임 공간 — " + " / ".join(ko) + ".",
            "FIRST FRAME SPACE — " + " / ".join(en) + ".")

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
