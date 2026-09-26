# -*- coding: utf-8 -*-
"""
XCONDA 블로킹 도구 (v9.3)
────────────────────────────────────────────────────────────
씬 JSON 하나를 받아서 두 가지를 한다.

  check   좌표가 물리적으로 말이 되는지 검사한다
          · 인물·카메라가 가구 안에 있지 않은가
          · 경로가 가구를 관통하지 않는가
          · 화각 안의 인물이 렌즈에서 1.2m보다 가깝지 않은가
          · 카메라가 피사체를 실제로 겨누고 있는가
          · 파트가 넘어갈 때 인물이 순간이동하지 않는가

  sync    좌표를 프롬프트 문장으로 옮긴다
          씨댄스는 JSON을 읽지 않는다. 좌표가 아무리 정확해도
          문장에 없으면 모델은 자기 마음대로 배치한다.
          각 컷 첫머리에 "첫 프레임 공간 — 누가 / 프레임 어디에 /
          렌즈에서 몇 미터 / 뒤에 무엇" 을 한 줄로 박는다.

사용법
    python3 blocking_tools.py check scene.json
    python3 blocking_tools.py sync  scene.json          # 파일을 덮어쓴다
    python3 blocking_tools.py sync  scene.json out.json

좌표 규약: 40px = 1m. 방 범위는 room.centerPx ± (widthPx, depthPx)/2.

v9.13: 정식 템플릿(xconda-scene-v1)의 room은 미터 기준(center/width/depth/obstacles)이라
이 도구가 읽는 px 필드(room.items 등)가 없다. scene_compat.normalize()가 px 필드를 채워준다.
"""
import json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene_compat import normalize          # 미터 room → px room.items (없으면 무변환 통과)

MIN_LENS = 1.20          # 화각 안의 인물이 렌즈에서 이보다 가까우면 샷이 성립하지 않는다 (OTS 앞 어깨는 예외)
TALL = {"사물함", "좌측 책장", "북측 책장", "창고 사물함", "창고 문", "입구 나무문"}   # 시선을 실제로 막는 것          # 화각 안의 인물이 렌즈에서 이보다 가까우면 샷이 성립하지 않는다
CLEAR    = 0.10          # 카메라가 가구에서 떨어져 있어야 할 여유
STEP     = 0.12          # 경로 충돌 검사 간격

NAME_KO = {"hyunwoo":"현우","daehan":"방대한","baksu":"박수","minhee":"민희",
           "kkangchul":"깡철이","chaokbun":"차옥분"}

def name_map(S):
    """씬 refs.characters의 id→이름을 먼저 쓰고, 없는 인물만 내장 NAME_KO로 채운다.
       이렇게 해야 이 스크립트가 S8 이외의 씬에서도 이름을 그대로 부른다."""
    m = dict(NAME_KO)
    for c in ((S.get("refs") or {}).get("characters") or []):
        if c.get("id") and c.get("name"):
            m[c["id"]] = c["name"]
    return m

def rects(S):
    return [(it["name"], it["x"]/40, it["y"]/40, it["w"]/40, it["h"]/40) for it in S["room"]["items"]]

def inside(R, x, y, pad=0.0, skip=()):
    return [n for n, ox, oy, w, h in R if n not in skip
            and abs(x-ox) <= w/2+pad and abs(y-oy) <= h/2+pad]

def crosses(R, p, q, skip=()):
    d = math.hypot(q[0]-p[0], q[1]-p[1]); hit = set()
    for i in range(int(d/STEP)+1):
        t = (i*STEP/d) if d else 0
        hit |= set(inside(R, p[0]+(q[0]-p[0])*t, p[1]+(q[1]-p[1])*t, 0, skip))
    return hit

def behind(R, cam, t, reach=6.5, own_chair=False):
    """카메라에서 피사체를 지나 계속 갔을 때 처음 만나는 가구 = 그 인물의 배경"""
    vx, vy = t[0]-cam[0], t[1]-cam[1]; n = math.hypot(vx, vy) or 1
    vx, vy = vx/n, vy/n; d = 0.25
    while d < reach:
        x, y = t[0]+vx*d, t[1]+vy*d
        for nm, ox, oy, w, h in R:
            if abs(x-ox) <= w/2 and abs(y-oy) <= h/2:
                if own_chair and nm == "의자" and math.hypot(ox-t[0], oy-t[1]) < 0.7:
                    continue                    # 앉은 사람이 깔고 앉은 의자는 배경이 아니다
                return nm, round(d, 1)
        d += 0.15
    return None, None

def pts_of(bl):
    return [(bl["x"]/40, bl["y"]/40)] + [(w["x"]/40, w["y"]/40) for w in bl.get("path", [])]

import re
CAM_TAG_KO = re.compile(r"카메라는[^.]{0,60}?@Image(\d+)")
CAM_TAG_EN = re.compile(r"camera (?:holds|stands|sits)[^.]{0,60}?@Image(\d+)", re.I)

def lint_prompt(S):
    """카메라가 '서 있는 자리'에 로케이션 태그를 붙이면 모델이 그 레퍼런스의 앵글을 재현한다.
       @태그는 프레임 '안에 보이는 것'에만 붙인다."""
    bg = {r["tag"].lower() for r in (S.get("refs", {}).get("backgrounds") or []) if r.get("tag")}
    out = []
    for p in S["parts"]:
        for c in (p.get("prompt") or {}).get("cuts", []):
            for col, rx in (("ko", CAM_TAG_KO), ("en", CAM_TAG_EN)):
                for mt in rx.finditer(c.get(col, "")):
                    tag = "@image" + mt.group(1)
                    if tag in bg:
                        out.append("%s %s(%s) 카메라 위치 설명에 로케이션 태그 %s — 그 이미지의 앵글이 그대로 재현된다"
                                   % (p["partId"], c.get("tc", ""), col, tag))
    return out

def lint_refs(S):
    """@Image 번호는 그 파트에 올린 장수만큼만 존재한다.
       3장 올리면 1~3, 7장 올리면 1~7. 건너뛴 번호는 모델이 해석하지 못한다."""
    out = []
    for p in S["parts"]:
        body = "\n".join([b.get("ko", "")+b.get("en", "")+b.get("headKo", "")+b.get("headEn", "")
                          for b in (p.get("prompt") or {}).get("blocks", [])]
                         + [c["ko"]+c["en"] for c in (p.get("prompt") or {}).get("cuts", [])])
        img = sorted({int(m) for m in re.findall(r"@Image(\d+)", body, re.I)})
        decl = [r for r in p.get("usesRefs", []) if r.startswith("@Image")]
        if not img:
            continue
        gaps = [i for i in range(1, max(img)+1) if i not in img]
        if gaps:
            out.append("%s @Image 번호를 건너뜀: %s — 업로드 순서가 곧 번호이므로 빈 번호는 존재할 수 없다"
                       % (p["partId"], gaps))
        if max(img) != len(decl):
            out.append("%s 선언 %d장인데 본문 최대 번호가 @Image%d — 장수와 번호가 어긋난다"
                       % (p["partId"], len(decl), max(img)))
    return out


def lint_cam_dup(S):
    """같은 파트에 좌표가 같은 카메라가 있으면 프롬프트의 '다가간다/물러난다'가 거짓이 된다.
       같은 피사체를 연속 컷에서 같은 거리로 잡는 것(타이트 정역숏 등)은 예외."""
    out = []
    for p in S["parts"]:
        cams = p.get("cameras", [])
        cam_by_ref = {c["cutRef"]: c for c in cams}
        seen = {}
        for cam in cams:
            key = (cam["x"], cam["y"])
            if key in seen:
                prev = cam_by_ref.get(seen[key], {})
                if cam.get("subject") and cam.get("subject") == prev.get("subject"):
                    pass     # 같은 인물 연속 컷 — 정상
                else:
                    out.append("%s %s 와 %s 가 같은 좌표 (%d,%d)"
                               % (p["partId"], seen[key], cam["cutRef"], key[0], key[1]))
            seen[key] = cam["cutRef"]
    return out

def check(S):
    R = rects(S); bad = lint_prompt(S) + lint_refs(S) + lint_cam_dup(S)
    prev_end = {}
    for p in S["parts"]:
        pid = p["partId"]
        for cid, bl in p.get("blocking", {}).items():
            skip = ("의자",) if bl.get("pose") in ("sit", "앉다") else ()
            pts = pts_of(bl)
            if inside(R, pts[0][0], pts[0][1], 0, skip):
                bad.append("%s %s 시작 위치가 가구 안 (%s)" % (pid, cid, ",".join(inside(R, *pts[0], 0, skip))))
            for i in range(len(pts)-1):
                h = crosses(R, pts[i], pts[i+1], skip)
                if h:
                    bad.append("%s %s 경로 %d구간이 가구를 관통 (%s)" % (pid, cid, i+1, ",".join(sorted(h))))
            if cid in prev_end:
                gap = math.hypot(pts[0][0]-prev_end[cid][0], pts[0][1]-prev_end[cid][1])
                if gap > 0.5:
                    bad.append("%s %s 가 앞 파트 종착점에서 %.1fm 떨어져 시작 — 컷 사이 순간이동" % (pid, cid, gap))
            prev_end[cid] = pts[-1]
        bl_now = {k: pts_of(v)[0] for k, v in p.get("blocking", {}).items()}
        for cam in p.get("cameras", []):
            c = (cam["x"]/40, cam["y"]/40); ang = cam.get("angle", 0); fov = cam.get("fov", 47)
            if inside(R, c[0], c[1], CLEAR):
                bad.append("%s %s 카메라가 가구 안 (%s)" % (pid, cam["cutRef"], ",".join(inside(R, *c, CLEAR))))
            if cam.get("fov") and cam["fov"] not in (180,107,84,63,47,29,18,12,8):
                bad.append("%s %s 화각 %s° 가 앵커 9단계 밖" % (pid, cam["cutRef"], cam["fov"]))
            sub = cam.get("subject")
            if sub and sub in p.get("blocking", {}):
                # 이동하는 인물은 경로 위 어느 지점에서든 화각에 들어오면 통과시킨다
                cand = pts_of(p["blocking"][sub])
                offs = [abs(((math.degrees(math.atan2(t[1]-c[1], t[0]-c[0]))-ang+180) % 360)-180) for t in cand]
                if min(offs) > fov/2:
                    bad.append("%s %s 카메라가 피사체(%s)를 %d° 벗어나 겨눔 — 경로 전 구간에서 화면 밖"
                               % (pid, cam["cutRef"], sub, min(offs)))
            for cid, t in bl_now.items():
                rel = ((math.degrees(math.atan2(t[1]-c[1], t[0]-c[0]))-ang+180) % 360)-180
                d = math.hypot(t[0]-c[0], t[1]-c[1])
                # OTS 컷은 앞 어깨가 렌즈 가까이 오는 것이 정상이다
                if cam.get("ots") and d < MIN_LENS and d >= 0.5:
                    continue
                if abs(rel) <= fov/2 and d < MIN_LENS:
                    bad.append("%s %s 화각 안의 %s 가 렌즈에서 %.1fm — %.1fm 이상 띄울 것"
                               % (pid, cam["cutRef"], cid, d, MIN_LENS))
    return bad

def josa(w, a="이", b="가"):
    ch = w[-1]
    return w + (a if ("가" <= ch <= "힣" and (ord(ch)-0xAC00) % 28) else b)

def shot_size(d, hfov):
    """거리와 화각 → 샷 사이즈. 씨댄스는 미터를 해석하지 못하므로 화면이 담는 높이로 옮긴다."""
    vf = 2*math.atan(math.tan(math.radians(hfov)/2)*9/16)
    H = 2*d*math.tan(vf/2)                     # 프레임 세로가 담는 실제 높이(m)
    if H < 0.60: return "얼굴이 화면을 채우는 클로즈업"
    if H < 1.00: return "가슴 위까지 잡히는 바스트"
    if H < 1.50: return "허리 위까지 잡히는 미디엄"
    if H < 2.20: return "무릎 위까지 잡히는 미디엄 롱"
    if H < 3.20: return "전신이 다 들어오는 풀샷"
    return "전신이 화면 높이의 절반 이하로 작게 들어오는 와이드"

CREATURES = {"kkangchul": "손바닥만 한 도마뱀"}
INSERT_ONLY = {"chaokbun": "CUT8-9"}

def spatial_line(S, part, cam, override):
    R = rects(S); names = name_map(S)
    bl = {k: pts_of(v)[0] for k, v in part.get("blocking", {}).items()}
    bl.update(override.get((part["partId"], cam["cutRef"]), {}))
    c = (cam["x"]/40, cam["y"]/40); ang = cam.get("angle", 0); fov = cam.get("fov", 47)
    vis = []
    for cid, t in bl.items():
        if cid in INSERT_ONLY and cam["cutRef"] != INSERT_ONLY[cid]:
            continue                            # 인서트 전용 인물은 본편 컷에 넣지 않는다
        rel = ((math.degrees(math.atan2(t[1]-c[1], t[0]-c[0]))-ang+180) % 360)-180
        if abs(rel) > fov/2+2:
            continue
        seated = (part["blocking"].get(cid, {}).get("pose") in ("sit", "앉다"))
        vis.append((math.hypot(t[0]-c[0], t[1]-c[1]), cid,
                    "중앙" if abs(rel) < 7 else ("오른쪽" if rel > 0 else "왼쪽"),
                    behind(R, c, t, own_chair=seated)))
    vis.sort()
    if not vis:
        return None
    out = []
    for i, (d, cid, side, (bg, bd)) in enumerate(vis):
        if cid in CREATURES:
            out.append("%s — %s, 프레임 %s에서 사람의 어깨 위에 올라앉은 채 함께 잡힌다"
                       % (names.get(cid, cid), CREATURES[cid], side))
            continue
        s = "%s — 프레임 %s, %s" % (names.get(cid, cid), side, shot_size(d, fov))
        if bg:
            s += ", %s %s 초점이 풀린 채 놓인다" % ("바로 뒤에" if bd < 1.2 else "그 너머 깊은 곳에", josa(bg))
        if i > 0:
            r = vis[0][0]/d
            if r < 0.75:
                s += "; 앞의 인물보다 키가 %s 작게 보이는 깊이" % ("절반쯤" if r > 0.45 else "3분의 1 이하로")
        out.append(s)
    return "첫 프레임 공간 — " + " / ".join(out) + "."

def sync(S, override=None):
    override = override or {}
    n = 0
    for p in S["parts"]:
        cams = {c["cutRef"]: c for c in p.get("cameras", [])}
        for cut in (p.get("prompt") or {}).get("cuts", []):
            cam = cams.get(cut.get("lb", "").split(" · ")[0].strip())
            if not cam:
                continue
            ln = spatial_line(S, p, cam, override)
            if not ln:
                continue
            body = [l for l in cut["ko"].split("\n") if not l.startswith("첫 프레임 공간 —")]
            body.insert(1, ln)
            cut["ko"] = "\n".join(body); n += 1
    return n

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    path = sys.argv[2]
    S = normalize(json.load(open(path, encoding="utf-8")))
    if cmd == "check":
        bad = check(S)
        print("문제 %d건" % len(bad))
        for b in bad:
            print("  ⚠", b)
    else:
        n = sync(S)
        out = sys.argv[3] if len(sys.argv) > 3 else path
        json.dump(S, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("공간 문장 %d컷 삽입 → %s" % (n, out))
        print("※ 한국어만 갱신된다. 영문은 편집기의 자동 갱신이나 Claude가 맞춘다.")
        if (S.get("room") or {}).get("_itemsFrom"):
            print("※ room이 미터 기준이라 px 필드(centerPx/widthPx/depthPx/items)를 채워 저장했다 — 편집기·검수가 읽는 형식.")
