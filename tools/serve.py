# -*- coding: utf-8 -*-
"""XCONDA 편집기를 웹에서 보이게 띄우는 로컬 서버.

`make engine` 이 이 스크립트를 돌린다. 브라우저에서 저장소 루트(`/`)를 열면
**씬이 이미 심겨 있는 편집기 UI**가 바로 나온다 — 디렉터리 목록이나 빈 드롭존이 아니다.

실행:
    python3 tools/serve.py [포트]        # 기본 8080, 0.0.0.0 바인딩

라우트:
    /                 index.html — 씬이 심긴 편집기 UI (tools/build_editor.py 로 생성·커밋됨)
    /engine           스킬 원본 편집기 템플릿 (씬 JSON을 직접 끌어다 넣을 때)
    /scene            현재 편집기에 심긴 씬 JSON
    /__status         서버·파일 상태 점검용 JSON (스크립트/회귀 테스트에서 사용)
    그 외             저장소 파일 그대로 (tests/fixtures/*.json 등)
"""
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "xconda-new-prompt")
EDITOR = os.path.join(ROOT, "index.html")                       # 커밋된 편집기 UI
EDITOR_SRC = os.path.join(ROOT, "output", "S8_xconda_editor.html")  # 빌드 산출물 원본
SCENE = os.path.join(ROOT, "output", "S8_scene.json")

MISSING = """<!doctype html>
<meta charset="utf-8"><title>XCONDA ENGINE — 빌드 필요</title>
<body style="background:#0A0A0A;color:#F2F2F0;font:14px/1.7 -apple-system,'Apple SD Gothic Neo',sans-serif;padding:40px">
<h2 style="color:#FFC800">편집기 UI 파일이 아직 없습니다</h2>
<p>저장소 루트에서 아래를 실행한 뒤 새로고침하세요.</p>
<pre style="background:#121212;border:1px solid #2A2A2A;padding:12px">make engine-html   # tools/build_s8.py → output/ → index.html</pre>
<p>씬 JSON만 직접 넣으려면 <a style="color:#FFC800" href="/engine">/engine</a> (빈 편집기)을 여세요.</p>
</body>"""


class Handler(SimpleHTTPRequestHandler):
    """저장소 파일을 그대로 주되, `/` 는 편집기 UI로 치환한다."""

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html", "/editor"):
            return self._send_file(EDITOR, "text/html; charset=utf-8", fallback=MISSING)
        if path == "/engine":
            return self._send_file(os.path.join(SKILL, "assets", "xconda_engine.html"),
                                   "text/html; charset=utf-8")
        if path == "/scene":
            return self._send_file(SCENE, "application/json; charset=utf-8")
        if path == "/__status":
            body = json.dumps({
                "editor_html": os.path.exists(EDITOR),
                "editor_bytes": os.path.getsize(EDITOR) if os.path.exists(EDITOR) else 0,
                "scene_json": os.path.exists(SCENE),
                "engine_template": os.path.exists(os.path.join(SKILL, "assets", "xconda_engine.html")),
            }, ensure_ascii=False)
            return self._send_bytes(body.encode("utf-8"), "application/json; charset=utf-8")
        return super().do_GET()

    # 프리뷰 iframe/다른 오리진에서도 fetch가 되게 열어둔다.
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def _send_file(self, path, ctype, fallback=None):
        if not os.path.exists(path):
            if fallback is None:
                return self.send_error(404, "not found: %s" % os.path.basename(path))
            return self._send_bytes(fallback.encode("utf-8"), ctype, 200)
        with open(path, "rb") as f:
            data = f.read()
        return self._send_bytes(data, ctype, 200)

    def _send_bytes(self, data, ctype, code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        sys.stderr.write("[serve] " + (fmt % args) + "\n")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8080))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print("XCONDA 편집기  : http://0.0.0.0:%d/          (씬이 심긴 UI)" % port)
    print("빈 편집기      : http://0.0.0.0:%d/engine    (씬 JSON 드롭용)" % port)
    print("상태 점검      : http://0.0.0.0:%d/__status" % port)
    if not os.path.exists(EDITOR):
        print("※ index.html 없음 — make engine-html 를 먼저 실행하세요")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
