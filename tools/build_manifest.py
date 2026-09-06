"""Build static/thumbs + static/wall_manifest.js from the workspace
page-asset tree (wall_manifest.json written by make_wall_thumbs.py).

Wall entries whose episodes appear in a curated composed clip get a
`clip` field so the lightbox plays the full comparison video.

Run: python3 tools/build_manifest.py
"""
import json
import shutil
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1]
SRC = Path("/home/rongxuan/idea/le-wm-workspace/wm-horizon/figs/page_assets")
TH = PAGE / "static" / "thumbs"
TH.mkdir(parents=True, exist_ok=True)

CLIPS = {  # (record stem, episode) -> shipped comparison clip
    ("cube_default_N300_s0", 7): "static/pairs/cube_s0_e07.mp4",
    ("cube_row_N300_s0_act4", 7): "static/pairs/cube_s0_e07.mp4",
    ("cube_default_N300_s0", 25): "static/pairs/cube_s0_e25.mp4",
    ("cube_row_N300_s0_act4", 25): "static/pairs/cube_s0_e25.mp4",
    ("cube_default_N300_s0_xproj", 25): "static/dose_ladder_e25.mp4",
    ("cube_default_N300_s0_inj4", 25): "static/dose_ladder_e25.mp4",
    ("cube_double_default_N300_s0", 16): "static/pairs/double_s0_e16.mp4",
    ("cube_double_row_N300_s0_act3", 16): "static/pairs/double_s0_e16.mp4",
    ("cube_double_default_N300_s0", 43): "static/pairs/double_s0_e43.mp4",
    ("cube_double_row_N300_s0_act3", 43): "static/pairs/double_s0_e43.mp4",
    ("cube_double_default_N300_s0", 2): "static/pairs/double_s0_e02_reverse.mp4",
    ("cube_double_row_N300_s0_act3", 2): "static/pairs/double_s0_e02_reverse.mp4",
    ("cube_default_N300_s0_mppi", 25): "static/pairs/sampler_e25_mppi.mp4",
    ("cube_row_N300_s0_act4_mppi", 25): "static/pairs/sampler_e25_mppi.mp4",
    ("cube_default_N300_s0_icem", 25): "static/pairs/sampler_e25_icem.mp4",
    ("cube_row_N300_s0_act4_icem", 25): "static/pairs/sampler_e25_icem.mp4",
    ("cube_default_N300_s0_K1_T1", 25): "static/pairs/sampler_e25_shooting.mp4",
    ("cube_row_N300_s0_K1_T1_act4", 25): "static/pairs/sampler_e25_shooting.mp4",
}

manifest = json.loads((SRC / "wall_manifest.json").read_text())
out = []
for m in manifest:
    src = SRC / "wall_thumbs" / f"{m['id']}.jpg"
    dst = TH / f"{m['id']}.jpg"
    if not dst.exists():
        shutil.copy2(src, dst)
    e = dict(id=m["id"], rec=m["rec"], ep=m["ep"], env=m["env"],
             tags=m["tags"], ok=m["ok"], img=f"static/thumbs/{m['id']}.jpg")
    clip = CLIPS.get((m["rec"], m["ep"]))
    if clip:
        e["clip"] = clip
    out.append(e)
gal = json.loads((SRC / "gallery_manifest.json").read_text())
GD = PAGE / "static" / "gallery"
GD.mkdir(parents=True, exist_ok=True)
for g in gal:
    src = SRC / g["file"]
    dst = GD / Path(g["file"]).name
    if not dst.exists():
        shutil.copy2(src, dst)
    g["file"] = f"static/gallery/{Path(g['file']).name}"

js = ("const WALL = " + json.dumps(out) + ";\n"
      + "const GALLERY = " + json.dumps(gal) + ";\n")
(PAGE / "static" / "wall_manifest.js").write_text(js)
kb = sum(f.stat().st_size for f in TH.glob("*.jpg")) / 1e6
print(f"[manifest] {len(out)} entries ({sum(1 for e in out if 'clip' in e)} "
      f"with clips), thumbs {kb:.1f} MB")
