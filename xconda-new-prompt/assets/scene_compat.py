# -*- coding: utf-8 -*-
"""
씬 JSON 호환 어댑터 (v9.13 추가)
────────────────────────────────────────────────────────────────────────────
왜 필요한가
  v9.10에서 정식 템플릿(`examples/template_scene_v1.json`)의 `room`이
  미터 기준(`center`/`width`/`depth`/`obstacles[]`/`portals[]`)으로 바뀌었다.
  그런데 도구는 아직 예전 px 기준(`centerPx`/`widthPx`/`depthPx`/`items[]`, 40px=1m)을 읽는다.
    · assets/blocking_tools.py  → room.items 가 없으면 KeyError
    · assets/xconda_engine.html → room.centerPx 가 없으면 패널 렌더가 멈춤
  이 어댑터가 미터 room을 px 필드로 **추가**해준다(원본 미터 필드는 지우지 않는다).
  이미 `room.items`가 있는 예전 씬은 그대로 통과시킨다(무변환).

규약
  · 40px = 1m (assets/xconda_object_catalog.json `_meta.pxPerMeter`와 동일)
  · `obstacles[]` → `items[]` 로 변환. 문·창(`portals[]`)은 사람이 지나가는 통로이므로
    `items`에 넣지 않는다(넣으면 "경로가 가구를 관통" 오탐이 난다).
  · 배우 `blocking.x/y`·카메라 `x/y`는 스키마와 무관하게 원래 px(40px=1m)다 → 손대지 않는다.

사용법
    from scene_compat import normalize
    S = normalize(json.load(open("scene.json", encoding="utf-8")))

    python3 scene_compat.py scene.json            # 변환 결과 확인(파일은 안 고침)
    python3 scene_compat.py scene.json out.json   # 변환본을 out.json으로 저장
"""
import json
import sys

PX_PER_M = 40.0
MARKER = "_itemsFrom"          # 이 room.items가 어디서 만들어졌는지 남기는 표식


def _px(meters):
    """미터 → px. float 잡음만 제거하고 반올림 오차는 남기지 않는다."""
    return round(float(meters or 0.0) * PX_PER_M, 3)


def needs_normalize(S):
    """이 씬이 변환을 필요로 하는가(room이 미터 기준이고 items가 없는가)."""
    room = (S or {}).get("room") or {}
    return "items" not in room and bool(room)


def normalize(S):
    """씬 JSON을 받아 px 기준 room 필드를 채워 넣는다(제자리 수정, 같은 객체 반환)."""
    if not isinstance(S, dict):
        return S
    room = S.get("room")
    if not isinstance(room, dict) or "items" in room:
        return S                      # 예전 px 스키마 — 건드리지 않는다

    center = room.get("center") or [0, 0]
    room["centerPx"] = [_px(center[0]), _px(center[1] if len(center) > 1 else 0)]
    room["widthPx"] = _px(room.get("width"))
    room["depthPx"] = _px(room.get("depth"))

    items = []
    for o in room.get("obstacles") or []:
        if not isinstance(o, dict):
            continue
        c = o.get("center") or [0, 0]
        items.append({
            "id": o.get("id"),
            "name": o.get("name") or o.get("id") or o.get("kind") or "obstacle",
            "kind": o.get("kind") or "furniture",
            "x": _px(c[0]),
            "y": _px(c[1] if len(c) > 1 else 0),
            "w": _px(o.get("width")),
            "h": _px(o.get("depth", o.get("height"))),
            "angle": o.get("hdg", o.get("angle", 0)),
            "blocksSight": bool(o.get("blocksSight", False)),
        })
    room["items"] = items
    room[MARKER] = "obstacles@%gpx/m(portals 제외)" % PX_PER_M
    return S


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[-3])
        return 2
    src = argv[1]
    S = json.load(open(src, encoding="utf-8"))
    before = needs_normalize(S)
    normalize(S)
    room = S.get("room") or {}
    print("입력: %s" % src)
    print("변환 필요: %s" % ("예" if before else "아니오(이미 px room.items 있음)"))
    print("centerPx=%s widthPx=%s depthPx=%s items=%d개"
          % (room.get("centerPx"), room.get("widthPx"), room.get("depthPx"), len(room.get("items") or [])))
    if len(argv) > 2:
        json.dump(S, open(argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("저장: %s" % argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
