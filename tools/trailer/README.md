# Demo trailer

The trailer is built from the real game. Electron runs the game in a hidden window on a virtual clock (`vtime.js`), so every frame is captured exactly, with no dropped frames. The director (`director.js`) starts the scenes and plays the shots from `shots.js`. ffmpeg then cuts the shots into the trailer, adds the music, the camera moves and the titles (`edit.js`, `build.mjs`).

```sh
tools/trailer/capture.sh                 # all shots → out/shots/<id>.mkv (lossless, 1067×600, 60 fps), ~1 min
tools/trailer/capture.sh --only city,feral   # re-capture just some shots
tools/trailer/capture.sh --survey        # still + object dump of every demo scene → out/stills/
tools/trailer/capture.sh --screenshots   # Steam gallery screenshots (STILLS in shots.js) → out/screenshots/ (1920×1080)
tools/trailer/capture.sh --screenshots --lang cs   # the same in Czech → out/screenshots/<id>_czech.png (Steam's suffix)
python3 tools/trailer/titles.py          # titles → out/titles/<id>.png (1920×1080, transparent)
node tools/trailer/build.mjs --preview   # quick 540p check → out/preview-story.mp4
node tools/trailer/build.mjs             # story cut → out/upper-morkezela-demo-trailer.mp4 (1080p60, H.264 20 Mbps + AAC, Steam spec)
node tools/trailer/build.mjs --cut gameplay   # "10 tips for visiting Upper Morkezela" to Dr. Elphi's Lab → out/upper-morkezela-demo-trailer-gameplay.mp4
node tools/trailer/gifs.mjs              # Steam description GIFs (616 px, textless, each < 5 MB) → out/gifs/
node tools/trailer/build.mjs --cut announce           # the demo announcement (dev branch) → out/upper-morkezela-demo-announcement.mp4, end card "LATE NOVEMBER / EARLY DECEMBER"
node tools/trailer/build.mjs --cut announce_late_nov  # the same ending on "LATE NOVEMBER" → out/upper-morkezela-demo-announcement-late-nov.mp4
```

`out/` is git-ignored.

## Where to change what

| What | Where |
|---|---|
| What happens in a scene (where the protagonist walks, speech bubbles, dialog, G/D state, HUD on or off) | `shots.js` |
| Order, length, source in-point, post camera move (zoom/pan), dissolves | `edit.js` (`montage()`, the intro in `makeCut()`; cuts in `CUTS`) |
| Text and its look | `titles.py` (`TITLES`); when it appears: `edit.js` (`TITLES`), cards via `{ card: id }` |
| Music track and in-point | `edit.js` (`MUSIC_FILE`, `musicStart` per cut); the cut points come from the measured cues `CUE` in `upper-morkezela.mp3` |

## Notes

- `hook.js` forces English, `noAudio` (the music is muxed in post) and `fps.smoothStep: false`, so every step is exactly 1/60 s.
- The shots switch scene exits off with `scene.isTransitioning = true`; otherwise a walk that crosses an edge would leave the scene mid-shot.
- In cinematic shots `hideHud` hides everything at depth ≥ 100 plus the hotspot labels every frame. Objects a shot adds itself (speech bubbles) go in `ctx.keep`.
- Steam screenshots must show only gameplay, with no added text. The HUD stays on (`hud: 'quiet'`), and speech bubbles and dialogs are the game's own.
- A scene's create() `delayedCall`s are only pending until the clock's next update, so `time.removeAllEvents()` must wait one `frame()` (see the Feral Toast shots).
- Gameplay shots (`g_*`) drive the real UI with a drawn cursor: `makeCursor()` dispatches DOM mouse events on the canvas, so hovers, dialog options, the shop, the inventory and click-to-walk behave as for a player. `script([[t, fn]])` times the steps. `toText()` and `toSprite()` find their target at run time (case-insensitive, inside containers), and `toSprite()` follows NPCs that walk.
- `g_journal` is captured last, so the journal holds the real entries the other gameplay shots wrote. `after(ctx)` hooks undo state that would leak into later shots (Thorne-Still, the Oltrac effect).
- The VS Code terminal exports `ELECTRON_RUN_AS_NODE`; `capture.sh` clears it.
- The announcement cut is an invitation to the city: its texts only promise what the demo holds, and it shows no spoilers (no Bishop's body, nothing inside the Egg Cathedral). Capture it on the dev branch. Its music is two pieces with one transition: Flop (110 BPM, an 11-bar loop) under the opening and the city, then the entry theme (infinite_fold.mp3 here, the demo's entry-theme.mp3; 100 BPM, its fuller part, coming in on the accented beat 3) from the things to do to the end; every cut sits on a beat (`MUSIC` in edit.js is a list of passages that build.mjs mixes, loops and limits). For live recordings without a fixed tempo, `python3 tools/trailer/onsets.py <track> <from> <to>` lists the strong attacks to cut on. The release window is the end card: `cta_nov_dec` / `cta_late_nov` in titles.py.
