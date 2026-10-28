#!/usr/bin/env python3
"""Build the VR Cinematics class deck from talk/pitch.json.

talk/pitch.json is the single source of truth: one shared slide pool plus two talks that
reference pool ids. This script
  1. validates it (ids unique and resolvable, every slide's talk tags match where it is used,
     pacing tag agrees with its seconds, no orphan pool slides, required fields present),
  2. splices it into index.html between the PITCH-JSON sentinels,
  3. writes TALKS.md: the readable script (pool table + both running orders + notes),
  4. prints each talk's running time against the two-hour slot.

Exit code is non-zero on any validation error, so a broken pool never reaches index.html.

    python tools/build_pitch.py            # validate + build
    python tools/build_pitch.py --check    # validate only, write nothing
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "talk" / "pitch.json"
HTML = ROOT / "index.html"
MD = ROOT / "TALKS.md"

SLOT_SEC = 7200         # a two-hour live class; the deck is the anchor points, not the whole session
TARGET_MAX = 590        # leave a few seconds for the walk-on and the moderator hand-off
TARGET_MIN = 510
FLASH_MAX_SEC = 15
DWELL_MIN_SEC = 30
FILL = re.compile(r"\[FILL:[^\]]*\]")
TRIMS = ("TRIM-1", "TRIM-2", "TRIM-3", "CORE")   # cut order: TRIM-1 goes first, CORE never
TRIM_TARGETS = (110, 100, 90)                         # minutes for the 'if you only have N minutes' guide
MEDIA_RE = re.compile(r"\.(jpe?g|png|webp|gif|svg|mp4|webm)$", re.I)
WORDS_PER_SEC = 2.5     # 150 wpm conversational delivery
START, END = "/* PITCH-JSON START */", "/* PITCH-JSON END */"


def fail(errors):
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)


def talk_ids(talk):
    # Fork-local: talk-level "intro" slides play between the cover and Act I (speaker + studio intro)
    yield from talk.get("intro", [])
    for act in talk["acts"]:
        if act.get("lesson"):  # an act may have no lesson slide (Talk A, 2026-10-22)
            yield act["lesson"]
        yield from act["cases"]


def validate(p):
    errors = []
    pool = {}
    for s in p["pool"]:
        sid = s.get("id")
        if not sid:
            errors.append(f"pool slide without id: {s.get('title')!r}")
            continue
        if sid in pool:
            errors.append(f"duplicate pool id {sid!r}")
        pool[sid] = s
        if s.get("talks") not in ("A", "B", "A+B"):
            errors.append(f"{sid}: talks must be A, B or A+B (got {s.get('talks')!r})")
        pace, sec = s.get("pace"), s.get("sec")
        if pace not in ("FLASH", "DWELL"):
            errors.append(f"{sid}: pace must be FLASH or DWELL")
        elif not isinstance(sec, (int, float)):
            errors.append(f"{sid}: sec must be a number")
        elif pace == "FLASH" and sec > FLASH_MAX_SEC:
            errors.append(f"{sid}: FLASH slides run <= {FLASH_MAX_SEC}s (got {sec}s); retag as DWELL or cut")
        elif pace == "DWELL" and sec < DWELL_MIN_SEC:
            errors.append(f"{sid}: DWELL slides run >= {DWELL_MIN_SEC}s (got {sec}s); retag as FLASH")
        if not s.get("notes"):
            errors.append(f"{sid}: speaker notes are required")
        # Image-only full-bleed beats are deliberate (spatial-deck conventions): no overlay text needed
        if not (s.get("title") or s.get("bigText") or (s.get("layout") == "full" and s.get("img"))
                or s.get("images") or s.get("placedImages") or s.get("placedItems")):
            errors.append(f"{sid}: needs a title (or bigText for layout 'big', or img for layout 'full')")
        if s.get("img") and not s["img"].startswith(("http", "IFRAME:")) and not (ROOT / s["img"]).exists():
            errors.append(f"{sid}: missing media file {s['img']}")
        if s.get("img", "").startswith("http"):
            errors.append(f"{sid}: media must be local so the deck runs offline ({s['img']})")
        # Clips need alt text and a credit line (fork-local video support)
        if re.search(r"\.(mp4|webm)$", s.get("img", ""), re.I):
            for k in ("alt", "credit"):
                if not s.get(k):
                    errors.append(f"{sid}: video slides need '{k}'")
        # every nested media path (phase-tour panes, replay stations, reel frames, compare pairs, door stills, bg images) must be local
        def walk(v, path):
            if isinstance(v, dict):
                for k, x in v.items():
                    walk(x, f"{path}.{k}")
            elif isinstance(v, list):
                for i, x in enumerate(v):
                    walk(x, f"{path}[{i}]")
            elif isinstance(v, str) and MEDIA_RE.search(v) and " " not in v and path != f"{sid}.img":
                if v.startswith("http"):
                    errors.append(f"{path}: media must be local so the deck runs offline ({v})")
                elif not (ROOT / v).exists():
                    errors.append(f"{path}: missing media file {v}")
        walk(s, sid)
        if s.get("trim") is not None and s["trim"] not in TRIMS:
            errors.append(f"{sid}: trim must be one of {', '.join(TRIMS)}")
        if s.get("layout") == "pipeline":
            phases = s.get("phases") or []
            if len(phases) != 3 or any(not ph.get("name") or not 1 <= len(ph.get("items") or []) <= 3 for ph in phases):
                errors.append(f"{sid}: pipeline slides take exactly 3 phases, each with a name and 1-3 items")
        if s.get("layout") == "ip-web":
            br = s.get("branches") or []
            if not 3 <= len(br) <= 5 or any(not b.get("t") for b in br) or not s.get("center"):
                errors.append(f"{sid}: ip-web slides need a center and 3-5 branches, each with a 't' label")
        if s.get("layout") == "rain":
            qs = s.get("quotes") or []
            if not 1 <= len(qs) <= 12:
                errors.append(f"{sid}: rain slides take 1-12 quotes (got {len(qs)})")
            for i, q in enumerate(qs):
                missing = [k for k in ("t", "who", "src", "year") if not q.get(k)]
                if missing:
                    errors.append(f"{sid}: quote {i + 1} is missing {', '.join(missing)} (every quote needs its attribution)")
                elif len(q["t"].split()) > 25:
                    errors.append(f"{sid}: quote {i + 1} runs {len(q['t'].split())} words; keep rain quotes to 25 or fewer")

    # The deck must run offline: closing QR codes are pre-rendered SVGs (tools/make_qr.py)
    for q in p.get("close", {}).get("qr", []):
        if not q.get("img") or not (ROOT / q["img"]).exists():
            errors.append(f"close.qr {q.get('url')!r}: missing local QR image (run python tools/make_qr.py)")

    used = {"A": set(), "B": set()}
    for key, talk in p["talks"].items():
        letter = key.upper()
        seen = set()
        for sid in talk_ids(talk):
            if sid not in pool:
                errors.append(f"talk {letter}: unknown pool id {sid!r}")
                continue
            if sid in seen:
                errors.append(f"talk {letter}: {sid!r} appears twice")
            seen.add(sid)
            if letter not in pool[sid]["talks"]:
                errors.append(f"talk {letter} uses {sid!r} but it is tagged [{pool[sid]['talks']}]")
            used[letter].add(sid)
            if not pool[sid].get("trim"):
                errors.append(f"talk {letter} uses {sid!r} without a trim priority ({', '.join(TRIMS)})")
        for act in talk["acts"]:
            if act.get("lesson") and pool.get(act["lesson"], {}).get("layout"):
                errors.append(f"talk {letter}: act lesson {act['lesson']!r} must be a plain slide, not layout {pool[act['lesson']]['layout']!r}")
    for sid, s in pool.items():
        for letter in ("A", "B"):
            # "parked" keeps a cut slide (and its tags) in the pool so it can be restored by adding its id back
            if letter in s["talks"] and sid not in used[letter] and not s.get("parked"):
                errors.append(f"{sid} is tagged [{s['talks']}] but talk {letter} never uses it (retag or drop it)")
    return pool, errors


def spoken_sec(s):
    """Seconds the speaker notes take to say aloud, ignoring [FILL] markers and stage directions."""
    text = FILL.sub("", s.get("notes", ""))
    # "ALEX TO CONFIRM: ..." is a note to the speaker, not a line to say; it always ends the notes
    text = text.split("ALEX TO CONFIRM:")[0]
    text = re.sub(r"^Pause\.[^:]*:", "", text)
    return len(text.split()) / WORDS_PER_SEC


def running_time(talk, pool):
    return sum(pool[sid]["sec"] for sid in talk_ids(talk)) + talk.get("cover_sec", 0)


def fmt(sec):
    return f"{int(sec) // 60}:{int(sec) % 60:02d}"


def strip_html(t):
    return re.sub(r"<[^>]+>", "", (t or "").replace("<br>", " ")).replace("\n", " ").strip()


def slide_lines(s):
    lines = []
    if s.get("subtitle"):
        lines.append(f"*{strip_html(s['subtitle'])}*")
    if s.get("bigText"):
        lines.append(f"**On screen:** {strip_html(s['bigText'])}")
    for b in s.get("bullets", []):
        lines.append(f"- {strip_html(b)}")
    for ph in s.get("phases", []):
        if "points" in ph:
            lines.append(f"- **{ph['name']}:** {'; '.join(strip_html(x) for x in ph['points'])} ({strip_html(ph.get('proof', ''))}) [{ph.get('media', '')}]")
            continue
        items = "; ".join(("\u25cf " if it.get("al") else "\u25cb ") + strip_html(it["t"]) for it in ph["items"])
        lines.append(f"- **{ph['name']}:** {items}")
    if s.get("output"):
        lines.append(f"- **Output:** {strip_html(s['output'])}")
    if s.get("center"):
        lines.append(f"- **Center:** {strip_html(s['center'])}")
    for b in s.get("branches", []):
        lines.append(f"- {'\u25cf' if b.get('al') else '\u25cb'} **{strip_html(b['t'])}:** {strip_html(b.get('d', ''))}"
                     + (f" ({strip_html(b['proof'])})" if b.get("proof") else ""))
    for st in s.get("stations", []):
        lines.append(f"- **{strip_html(st.get('when', ''))} {strip_html(st['t'])}:** {strip_html(st.get('d', ''))} [{st.get('img', '')}]")
    for f in s.get("frames", []):
        lines.append(f"- Frame: {f['img']} ({f.get('alt', '')})")
    if s.get("imgA"):
        lines.append(f"- Compare: {s.get('labelA')} [{s['imgA']}] / {s.get('labelB')} [{s['imgB']}]")
    if s.get("bgImg"):
        lines.append(f"- Background: {s['bgImg']}")
    if s.get("only"):
        lines.append(f"- **Only XR:** {' · '.join(s['only'])}")
    if s.get("legend"):
        lines.append(f"- *Legend:* \u25cf {s['legend'][0]}" + (f" · \u25cb {s['legend'][1]}" if len(s['legend']) > 1 else ""))
    for q in s.get("quotes", []):
        lines.append(f"- \u201c{q['t']}\u201d ({q['who']}, {q['src']}, {q['year']})")
    if s.get("credit"):
        lines.append(f"*Credit:* {strip_html(s['credit'])}")
    if s.get("tagline") and not s.get("bullets"):
        lines.append(f"- {strip_html(s['tagline'])}")
    return lines


def trim_guide(talk, pool):
    """Cut lists for TRIM_TARGETS minutes: drop TRIM-1 slides first (in running order), then TRIM-2, then TRIM-3, until the
    talk fits. Act lessons are never cut on their own: a lesson goes only when every slide in its act has gone."""
    rt = running_time(talk, pool)
    lessons = {a["lesson"] for a in talk["acts"] if a.get("lesson")}
    ids = [sid for sid in talk_ids(talk) if sid not in lessons]
    order = [sid for level in TRIMS[:-1] for sid in ids if pool[sid].get("trim") == level]
    out, cut, total = [], [], rt
    for mins in TRIM_TARGETS:
        new = []
        for sid in order:
            if total <= mins * 60:
                break
            if sid in cut:
                continue
            cut.append(sid); new.append(sid); total -= pool[sid]["sec"]
            for a in talk["acts"]:
                if a.get("lesson") and a["lesson"] not in cut and a["cases"] and all(c in cut for c in a["cases"]):
                    cut.append(a["lesson"]); new.append(a["lesson"]); total -= pool[a["lesson"]]["sec"]
        out.append((mins, new, total))
    return rt, out


def guide_text(talk, pool, md=False):
    rt, rows = trim_guide(talk, pool)
    name = lambda sid: (f"`{sid}`" if md else sid) + f" ({pool[sid]['sec']}s)"
    lines = [f"Full talk: {fmt(rt)}."]
    for mins, new, total in rows:
        lines.append(f"{mins} min ({fmt(total)}): " + ("cut " + ", ".join(name(s) for s in new) if new else "no further cuts") + ".")
    return lines


def write_md(p, pool):
    out = [
        f"# {strip_html(p['event_plain'])}: talk scripts",
        "",
        "Generated by `tools/build_pitch.py` from `talk/pitch.json`. Edit the JSON, not this file.",
        "",
        "Tags: **[A]** Talk A only, **[B]** Talk B only, **[A+B]** shared. "
        "**[FLASH]** is a ~10-second visual beat; **[DWELL]** is a ~1-minute story beat.",
        "",
    ]
    for key, talk in p["talks"].items():
        rt = running_time(talk, pool)
        out += [f"- **Talk {key.upper()}: {strip_html(talk['title'])}**, {fmt(rt)} planned "
                f"([open](https://ibrews.github.io/vr-cinematics-ue58-deck/{'' if key == 'a' else '?talk=b'}))"]
    out += ["", "## Running orders", ""]
    for key, talk in p["talks"].items():
        out += [f"### Talk {key.upper()}: {strip_html(talk['title'])}", "",
                f"Thesis: {talk['thesis']}", "",
                "| # | Act | Slide | Tags | Pace | Sec | Clock |", "|---|---|---|---|---|---|---|"]
        clock, n = talk.get("cover_sec", 0), 1
        out.append(f"| 0 | Cover | {strip_html(talk['title'])} | [{key.upper()}] | FLASH | {talk.get('cover_sec', 0)} | {fmt(clock)} |")
        for act in [{"year": "INTRO", "lesson": None, "cases": talk.get("intro", [])}, *talk["acts"]]:
            for sid in [x for x in [act["lesson"], *act["cases"]] if x]:
                s = pool[sid]
                clock += s["sec"]
                title = strip_html(s.get("title") or s.get("bigText"))
                out.append(f"| {n} | {act['year']} | {title} (`{sid}`) | [{s['talks']}] | {s['pace']} · {s.get('trim', '')} | {s['sec']} | {fmt(clock)} |")
                n += 1
        out += ["", f"Take-home line: **{strip_html(talk['takeaway'])}**", ""]
    out += ["## If you only have N minutes", "",
            "Generated from each slide's trim priority: `TRIM-1` slides go first, then `TRIM-2`, then `TRIM-3`; `CORE` slides stay. "
            "Each line adds cuts to the line above. The same guide is in each talk's cover-slide notes.", ""]
    for key, talk in p["talks"].items():
        out += [f"**Talk {key.upper()}:**", ""] + [f"- {l}" for l in guide_text(talk, pool, md=True)] + [""]
    parked = [s for s in p["pool"] if s.get("parked")]
    if parked:
        out += ["## Parked slides (in the pool, restorable)", "",
                "Cut for time or superseded. To restore one, add its id back to a talk's act (or `intro`) list in `talk/pitch.json`.", ""]
        for s in parked:
            idle = [k.upper() for k, t in p["talks"].items() if k.upper() in s["talks"] and s["id"] not in set(talk_ids(t))]
            out.append(f"- `{s['id']}` [{s['talks']}] {s['sec']}s, unused in Talk {' and '.join(idle) or '(none)'}: {s['parked']}")
        out.append("")
    out += ["## Shared slide pool", ""]
    for s in p["pool"]:
        title = strip_html(s.get("title") or s.get("bigText"))
        out += [f"### `{s['id']}`: {title}", "", f"**[{s['talks']}] [{s['pace']}] {s['sec']}s**", ""]
        out += slide_lines(s)
        out += ["", f"> **Notes:** {s['notes']}", ""]
    fills = sorted({m for s in p["pool"] for m in FILL.findall(json.dumps(s, ensure_ascii=False))})
    out += ["## Open [FILL] items", ""] + [f"- {f}" for f in fills] + [""]
    MD.write_text("\n".join(out), encoding="utf-8", newline="\n")
    return fills


def main():
    p = json.loads(SRC.read_text(encoding="utf-8"))
    pool, errors = validate(p)
    # Custom branding is required for every talk (tools/check_branding.py)
    sys.path.insert(0, str(ROOT / "tools"))
    from check_branding import check as check_branding
    errors += [f"branding: {e}" for e in check_branding()]
    if errors:
        fail(errors)
    for key, talk in p["talks"].items():
        rt = running_time(talk, pool)
        n = sum(1 for _ in talk_ids(talk))
        # per-talk target (minutes) when set: Alex speaks fast, so a talk may be budgeted long and trimmed with the guide
        lo, hi = (talk["target_min"] * 60 * .9, talk["target_min"] * 60 * 1.05) if talk.get("target_min") else (0, SLOT_SEC)
        flags = "" if lo <= rt <= hi else f"  <-- outside {fmt(lo)}-{fmt(hi)} target"
        spoken = sum(spoken_sec(pool[sid]) for sid in talk_ids(talk))
        print(f"Talk {key.upper()}: {n} slides + cover, {fmt(rt)} budgeted (slot {fmt(SLOT_SEC)}){flags}; notes read aloud ~{fmt(spoken)} at 150 wpm")
    for s in p["pool"]:
        if spoken_sec(s) > s["sec"] * 1.1:
            print(f"WARN: {s['id']} notes take ~{spoken_sec(s):.0f}s to say but the slide is budgeted {s['sec']}s")
    if "--check" in sys.argv:
        return
    html = HTML.read_text(encoding="utf-8")
    i, j = html.index(START) + len(START), html.index(END)
    for key, talk in p["talks"].items():  # the trim guide rides along in the cover slide's presenter notes
        talk["cover_notes"] = (talk.get("cover_spoken", "") + "\n\nIF YOU ONLY HAVE N MINUTES: " + " ".join(guide_text(talk, pool))).strip()
    blob = json.dumps({k: v for k, v in p.items()}, ensure_ascii=False, indent=1)
    HTML.write_text(html[:i] + "\n" + blob + "\n" + html[j:], encoding="utf-8", newline="\n")
    fills = write_md(p, pool)
    print(f"Wrote index.html and TALKS.md ({len(fills)} open [FILL] items)")


if __name__ == "__main__":
    main()
