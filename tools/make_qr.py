#!/usr/bin/env python3
"""Pre-render the closing slide's QR codes as local SVGs (fork-local, MIA 2026 pitch).

The deck must run with no internet, so QR codes are files in assets/qr/ instead of
api.qrserver.com images. Each entry in talk/pitch.json close.qr names its url and img;
this script writes img from url. Needs the `segno` package (pip install segno), but only
when a QR changes: the SVGs are committed, and build_pitch.py just checks they exist.

    python tools/make_qr.py
"""
import json
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parent.parent
p = json.loads((ROOT / "talk" / "pitch.json").read_text(encoding="utf-8"))
for q in p["close"]["qr"]:
    out = ROOT / q["img"]
    out.parent.mkdir(parents=True, exist_ok=True)
    # Dark modules on a white quiet zone scan reliably from the back of a room
    segno.make(q["url"], error="m").save(str(out), kind="svg", scale=10, border=4, dark="#060810", light="#ffffff", xmldecl=False)
    # segno writes width/height only; a viewBox lets the <img> scale it to any card size
    svg = out.read_text(encoding="utf-8")
    w = svg.split('width="', 1)[1].split('"', 1)[0]
    out.write_text(svg.replace("<svg ", f'<svg viewBox="0 0 {w} {w}" ', 1), encoding="utf-8")
    print(f"wrote {q['img']} for {q['url']}")
