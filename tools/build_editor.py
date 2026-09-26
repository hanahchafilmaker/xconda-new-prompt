# -*- coding: utf-8 -*-
"""웹에 올릴 편집기 UI 파일을 만든다.

tools/build_s8.py 를 실행해 output/S8_scene.json + output/S8_xconda_editor.html 을 만들고,
그 편집기를 **저장소 루트의 index.html** 로 복사한다. 루트에 두는 이유:
output/ 은 .gitignore 대상이라 새로 클론하면 사라지고, 그러면 웹에서 UI가 안 보인다.

실행: python3 tools/build_editor.py    (또는 make engine-html)
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "output", "S8_xconda_editor.html")
DST = os.path.join(ROOT, "index.html")


def main():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_s8.py")], cwd=ROOT)
    if r.returncode != 0:
        print("build_s8.py 가 실패했습니다 (블로킹 검수 문제 있음)")
        return r.returncode
    if not os.path.exists(SRC):
        print("편집기 산출물이 없습니다:", SRC)
        return 1
    shutil.copyfile(SRC, DST)
    print("편집기 UI: %s (%d bytes)" % (DST, os.path.getsize(DST)))
    print("→ 웹에서 저장소 루트(/)를 열면 이 화면이 바로 나온다 (tools/serve.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
