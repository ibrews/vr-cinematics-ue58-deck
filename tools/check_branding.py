#!/usr/bin/env python3
"""Fail if this talk still ships Spatial Deck's default branding (fork-local, MIA 2026).

Rule (Alex, 2026-10-22): every presentation gets its own custom social card and favicon; never ship the
Spatial Deck defaults. Checks: favicon.svg / social.png must differ from the template's files (hashes below,
from ibrews/spatial-deck main, and from a local template checkout when present), the icon/card files must exist,
og:image / twitter:image must point at this talk's own social.png, and no <title> or meta tag may say
"Spatial Deck". build_pitch.py runs this and refuses to build on failure.

    python tools/check_branding.py
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_MD5 = {"favicon.svg": {"d58951081dfd95ec7ce14890cbcb81ec"}, "social.png": {"5599df306a11e9e8f54abebaa894f7d1"}}
TEMPLATE_REPO = Path.home() / "GH" / "spatial-deck"
REQUIRED = ["favicon.svg", "favicon-32.png", "favicon.ico", "apple-touch-icon.png", "social.png", "social.html"]


def md5(b):
    return hashlib.md5(b).hexdigest()


def check():
    errs = []
    for f in REQUIRED:
        if not (ROOT / f).exists():
            errs.append(f"missing {f}")
    for f, known in TEMPLATE_MD5.items():
        known = set(known)
        if TEMPLATE_REPO.exists():
            try:
                known.add(md5(subprocess.run(["git", "-C", str(TEMPLATE_REPO), "show", f"HEAD:{f}"], capture_output=True, check=True).stdout))
            except Exception:
                pass
        if (ROOT / f).exists() and md5((ROOT / f).read_bytes()) in known:
            errs.append(f"{f} is still the Spatial Deck template file: make a custom one for this talk")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    head = html[: html.find("</head>")] if "</head>" in html else html[:20000]
    for tag in re.findall(r"<title>.*?</title>|<meta[^>]+>", head, re.S):
        if re.search(r"spatial[ -]?deck", tag, re.I):
            errs.append(f"head still says Spatial Deck: {tag[:120]}")
    for prop in ("og:image", "twitter:image"):
        m = re.search(rf'<meta (?:property|name)="{prop}" content="([^"]+)"', head)
        if not m:
            errs.append(f"no {prop} meta tag")
        elif "spatial-deck/" in m.group(1) or not m.group(1).endswith("social.png"):
            errs.append(f"{prop} points at {m.group(1)}, not this talk's social.png")
    if re.search(r'<div id="brand">\s*Spatial Deck', html, re.I):
        errs.append("corner #brand label still says Spatial Deck")
    if re.search(r"<title>[^<]*Spatial Deck", (ROOT / "social.html").read_text(encoding="utf-8"), re.I):
        errs.append("social.html is still the template card")
    return errs


if __name__ == "__main__":
    e = check()
    for x in e:
        print(f"BRANDING: {x}", file=sys.stderr)
    print("branding OK" if not e else f"{len(e)} branding problem(s)")
    sys.exit(1 if e else 0)
