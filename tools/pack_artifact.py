"""Pack index.html into a single self-contained preview (all static assets
inlined as data URIs; episode replays dropped; wall sampled to ~2200).
Run: .venv python tools/pack_artifact.py <out.html>
"""
import base64, json, re, sys
from pathlib import Path
MIME = {".mp4": "video/mp4", ".png": "image/png", ".jpg": "image/jpeg",
        ".svg": "image/svg+xml"}
def du(p):
    p = Path(p)
    return f"data:{MIME[p.suffix]};base64," + base64.b64encode(p.read_bytes()).decode()
h = Path("index.html").read_text()
h = h.replace('const EPISODES = "static/episodes"', 'const EPISODES = null')
h = re.sub(r'(src|poster|data-vsrc|data-poster)="(static/[^"?]+)(\?v=\d+)?"',
           lambda m: (f'{m.group(1)}="{du(m.group(2))}"'
                      if not m.group(2).endswith(".js") else m.group(0)), h)
h = re.sub(r'\["(static/(?:pairs|dose)[^"]+)",', lambda m: '["' + du(m.group(1)) + '",', h)
h = re.sub(r'src: "(static/(?:pairs|dose)[^"]+)"', lambda m: 'src: "' + du(m.group(1)) + '"', h)
mani = Path("static/wall_manifest.js").read_text()
ws, gs = re.search(r"const WALL = (\[.*?\]);\nconst GALLERY = (\[.*?\]);", mani, re.S).groups()
wall, gal = json.loads(ws), json.loads(gs)
wall.sort(key=lambda e: (e["env"], e["rec"], e["ep"]))
meth = set(re.findall(r'\["((?:cube|scene|pusht|tworoom)[A-Za-z0-9_.]*)",\s*"', h))
keep = [e for e in wall if e["rec"] in meth]
rest = [e for e in wall if e["rec"] not in meth]
N = max(0, 2200 - len(keep))
idx = sorted(set(round(i * (len(rest) - 1) / (N - 1)) for i in range(N))) if N > 1 else []
s = keep + [rest[i] for i in idx]
for e in s:
    e["img"] = du(e["img"]); e.pop("clip", None)
for g in gal:
    g["file"] = du(g["file"])
h = re.sub(r'<script src="static/wall_manifest\.js[^"]*"></script>',
           "<script>const WALL = " + json.dumps(s) + ";\nconst GALLERY = "
           + json.dumps(gal) + ";</script>", h)
h = re.sub(r'<script src="static/charts\.js[^"]*"></script>',
           lambda m: "<script>" + Path("static/charts.js").read_text() + "</script>", h)
h = re.sub(r'<meta property="og:image"[^>]*>\n?', "", h)
out = Path(sys.argv[1]); out.write_text(h)
print(f"[pack] {out} {out.stat().st_size/1e6:.2f} MB, wall {len(s)}")
