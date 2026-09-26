#!/usr/bin/env python3
"""XCONDA 공간 배치 헬퍼 — 오브젝트 카탈로그를 불러와 인간 키 기준으로 가구를 배치한다.

사용법:
  from place_helper import Placer
  p = Placer('xconda_object_catalog.json', room_center=(640,360))
  desk = p.place('책상', name='방대한 책상', x=517, y=325)   # 크기는 카탈로그에서 자동
  # → {'type':'prop','layer':'space','kind':'책상','name':'방대한 책상','x':517,'y':325,'w':48,'h':28,'angle':0,...}

기준점(anchor): 인간 키. place() 결과의 px 크기는 40px=1m 고정.
검산: p.human_px() 로 사람 키 px(68)를 얻어 가구 옆에 두고 비율을 눈으로 확인.
"""
import json

class Placer:
    def __init__(self, catalog_path, room_center=(640,360), start_id=100):
        self.cat = json.load(open(catalog_path, encoding='utf-8'))
        self.ppm = self.cat['_meta']['pxPerMeter']          # 40
        self.anchor_h = self.cat['_meta']['anchor']['value'] # 1.70
        self.cx, self.cy = room_center
        self._id = start_id

    def human_px(self):
        """사람 키를 px로 (검산용). 1.7m → 68px"""
        return round(self.anchor_h * self.ppm)

    def spec(self, key):
        o = self.cat['objects'].get(key)
        if not o:
            raise KeyError(f"카탈로그에 '{key}' 없음. 가능한 키: {list(self.cat['objects'])[:8]}...")
        return o

    def place(self, key, name=None, x=0, y=0, angle=0, rotate=False, layer='space'):
        """가구 하나 배치. 크기는 카탈로그 표준(m→px). rotate=True면 가로/세로 치수 교환."""
        o = self.spec(key)
        w_m, d_m = (o['depth'], o['width']) if rotate else (o['width'], o['depth'])
        it = {
            "id": self._id, "type": "prop", "layer": layer,
            "kind": o['kind'], "name": name or key,
            "x": int(round(x)), "y": int(round(y)),
            "w": max(4, int(round(w_m * self.ppm))),
            "h": max(4, int(round(d_m * self.ppm))),
            "angle": angle, "motionMarkers": []
        }
        self._id += 1
        return it

    def scale_check(self, item):
        """가구 px가 사람 키 대비 합리적인지 한 줄 리포트"""
        # depth(h)로 대략 판단은 안 되고, 카탈로그 height와 비교
        return f"{item['name']}: {item['w']}x{item['h']}px ({item['w']/self.ppm:.2f}x{item['h']/self.ppm:.2f}m)"

if __name__ == '__main__':
    p = Placer('xconda_object_catalog.json')
    print("사람 키:", p.human_px(), "px (1.7m)")
    for k in ['책상','의자','캐비닛','L자소파_가로','문']:
        it = p.place(k, x=500, y=300)
        print(" ", p.scale_check(it))
