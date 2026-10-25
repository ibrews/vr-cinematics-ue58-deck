# VR Cinematics for UE 5.8: the class deck

The slides for **VR Cinematics for UE 5.8**, a live class by [Alex Coulombe Presents](https://alexcoulombepresents.com/classes/2026-10-28-vr-cinematics) (Wednesday, October 28, 2026). Record someone playing in VR, stabilize it, re-shoot it from new camera angles, render it, and see how the cameras of *A Christmas Carol VR* were built, from a keyboard-driven Blueprint in 2023 to a visitor-facing cinematographer build in 2026.

**▶ View the deck:** https://ibrews.github.io/vr-cinematics-ue58-deck/ &nbsp;·&nbsp; **Camera case study only (conference cut):** https://ibrews.github.io/vr-cinematics-ue58-deck/?talk=b

Built on [Spatial Deck](https://github.com/ibrews/spatial-deck), the single-file HTML presentation framework, with fork-local layouts ported from the [MIA 2026 Collective Pitch deck](https://github.com/ibrews/mia-2026-collective-pitch).

## Quickstart

```bash
git clone https://github.com/ibrews/vr-cinematics-ue58-deck
cd vr-cinematics-ue58-deck
python -m http.server 8750   # then open http://localhost:8750/
```

Opening `index.html` directly also works. Edit `talk/pitch.json`, then run `python tools/build_pitch.py` to validate it and splice it into `index.html` (it also writes `TALKS.md`, the readable script).

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
