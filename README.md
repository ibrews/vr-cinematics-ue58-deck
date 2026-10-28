# VR Cinematics for UE 5.8: the class deck

The slides for **VR Cinematics for UE 5.8**, a live class by [Alex Coulombe Presents](https://alexcoulombepresents.com/classes/2026-10-28-vr-cinematics) (Wednesday, October 28, 2026). Record someone playing in VR, stabilize it, re-shoot it from new camera angles, render it, and see how the cameras of *A Christmas Carol VR* were built, from a keyboard-driven Blueprint in 2023 to a visitor-facing cinematographer build in 2026.

**▶ View the deck:** https://ibrews.github.io/vr-cinematics-ue58-deck/ &nbsp;·&nbsp; **Extended camera history (optional):** https://ibrews.github.io/vr-cinematics-ue58-deck/?talk=b

Built on [Spatial Deck](https://github.com/ibrews/spatial-deck), the single-file HTML presentation framework, on modular framework `14256be`, with reusable camera and timeline modules pulled from the PMRE deck.

## Quickstart

```bash
git clone https://github.com/ibrews/vr-cinematics-ue58-deck
cd vr-cinematics-ue58-deck
python -m http.server 8750   # then open http://localhost:8750/
```

Opening `index.html` directly also works. Edit `talk/pitch.json`, then run `python3 tools/bake_deck.py` to validate it and splice it into `index.html` (it also writes `TALKS.md`, the readable script).

## What is in it

| Part | What it covers |
|---|---|
| I · Raw VR footage looks bad | Shake, tilt, jump and FOV, and the numbers before and after on the class practice take |
| II · Capture it | Take Recorder, the Replay system and Meta XR Simulator |
| III · Stabilize it | Quaternion smoothing, never across a teleport, level the horizon |
| IV · Re-shoot it | Five camera rigs and a first edit cut on the teleports |
| V · Render it | Movie Render Queue draft and final, three silent traps, FRAME_OPEN shutter |
| VI · The cameras of A Christmas Carol VR | MagicCam (2023), the livestream desk (2025), replay, the 2026 cinematographer build and its title-card decisions |
| VII · Homework and next | Wrap |

The slides are anchor points for a live Unreal session; the minute-by-minute run of show lives in the class kit.

## Things to Try

1. Open the deck and press **→** to step through it; the first slide after the cover is the finished cut, played cold.
2. On the "Same Take, Two Cameras" slide, drag the line to compare the recorded head camera with the stabilized one.
3. Click through the five rigs on "Five Cameras, One Take".
4. On "Four Generations of Cameras", click a stop or drag the playhead to move from MagicCam to the 2026 cinematographer build.
5. Add `?talk=b` to the URL for the 14-slide conference cut of Part VI, then press **N** for speaker notes.

## Credits

**Alex Coulombe Presents** · framework: [Spatial Deck](https://github.com/ibrews/spatial-deck). *A Christmas Carol VR* performed live by Ari Tarr and Debbie Deer; adapted for VR by David Gochfeld, based on the adaptation by Robert Barry Fleming. Class practice-take footage is from the VR Cinematics kit.

## Live class, 2026-10-28

Alex teaches 10:00–12:00 ET. The CLASS CLOCK in each slide note includes demonstration, exercise and question time. Breaks: 10:45–10:50 and 11:25–11:30. The ACCVR case study is the going-further segment; skip history detail first if a core demo needs time. Every live demonstration is optional and has a `LIVE OPTION: <machine> — <steps>` cue. The recorded practice take is synthetic and labeled as such.

`talk/pitch.json` owns content, `talk/head.html` owns metadata, and `talk/class.css` owns class styles. `tools/framework.html` pins the unmodified modular framework source; `tools/bake_deck.py` regenerates the runtime and syncs the slide modules. Imported module folders carry `.pulled.json` provenance. The deck uses quiet chrome by default.

Migration review: [all slides and substeps](review/migration/report.json), [contact sheet](review/migration/contact-sheet-0.jpg). The initial migration sweep included 42 framework slides. The later two-hour class cut preserves the longer camera history in Talk B so hands-on capture and rendering retain their time.

## Talk-over videos

Eight embedded clips are now available across the class: the original practice edit, smoothing comparison, five-camera montage, the reused UOXR automated-menu demo, Carol replay, Carol angle/working-cut excerpt and full trailer. The additional UOXR pinch clip is included for optional use. [Video manifest](talk/video-manifest.json) records sources, durations and hashes. All start muted; the Carol trailer retains audio for optional playback. Original kit renders are from UE 5.8.2; the ACCVR prototype is UE 5.4.4. These clips do not establish a new same-session XR recording or Aura MetaHuman acceptance.
