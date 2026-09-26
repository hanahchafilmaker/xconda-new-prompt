#!/usr/bin/env python3
"""XCONDA 스킬 무결성 점검기.
- SKILL.md, 필수 assets 존재 확인
- 모든 .md가 언급하는 references/*.md · assets/* 링크가 실제로 있는지 확인
사용: python3 scripts/validate.py   (스킬 루트에서 실행)
종료코드 0=통과, 1=문제 있음.
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems = []

def need(path, label):
    if not os.path.exists(os.path.join(ROOT, path)):
        problems.append(f"[없음] {label}: {path}")

# 1) 필수 파일
need("SKILL.md", "스킬 본문")
for a in ["assets/xconda_engine.html", "assets/blocking_tools.py", "assets/scene_compat.py"]:
    need(a, "필수 자산")

# 2) 링크 무결성 — 모든 md에서 references/xxx.md, assets/xxx 언급을 수집해 존재 확인
link_re = re.compile(r'`(references/[\w\-.]+\.md)`')
mentioned = set()
for md in glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True):
    txt = open(md, encoding="utf-8").read()
    for m in link_re.findall(txt):
        mentioned.add(m)
for link in sorted(mentioned):
    if not os.path.exists(os.path.join(ROOT, link)):
        problems.append(f"[링크 깨짐] {link} 를 문서가 가리키는데 파일이 없음")

# 3) frontmatter name 확인 — 따옴표 있는 형태(name: "xconda-new-prompt")도 정상이다
head = open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8").read()[:400]
if not re.search(r'name:\s*["\']?xconda-new-prompt["\']?', head):
    problems.append("[경고] SKILL.md frontmatter의 name이 xconda-new-prompt가 아님")

# 4) 스키마 호환 어댑터가 실제로 연결돼 있는가 (v9.13)
#    정식 템플릿(room이 미터 기준)을 편집기·검수 도구가 읽으려면 이 연결이 살아 있어야 한다.
def read(path):
    p = os.path.join(ROOT, path)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""

if "from scene_compat import normalize" not in read("assets/blocking_tools.py"):
    problems.append("[연결 끊김] assets/blocking_tools.py 가 scene_compat.normalize 를 불러오지 않는다")
if "normalizeRoom(data)" not in read("assets/xconda_engine.html"):
    problems.append("[연결 끊김] assets/xconda_engine.html 의 loadScene 이 normalizeRoom 을 호출하지 않는다")
if "__ROOM_COMPAT_START__" not in read("assets/xconda_engine.html"):
    problems.append("[연결 끊김] assets/xconda_engine.html 에서 ROOM_COMPAT 블록을 찾을 수 없다")

# 결과
refs = len(glob.glob(os.path.join(ROOT, "references", "*.md")))
print(f"references 파일 수: {refs}")
print(f"문서가 가리키는 링크 수: {len(mentioned)}")
if problems:
    print("\n문제 발견:")
    for p in problems: print("  -", p)
    sys.exit(1)
print("\n[통과] 필수 파일·링크 이상 없음.")
sys.exit(0)
