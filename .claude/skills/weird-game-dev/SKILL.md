---
name: weird-game-dev
description: >-
  Conventions and how-to for building content in this repo — the "Upper Morkezela / weird-game"
  Phaser 3 RPG (Electron). Load this BEFORE adding or editing any scene, dialog, quest, journal
  entry, NPC, Day-2 content, i18n/Czech translation, or the Cardinal Feast mini-game. Covers the
  dialog system, quest/journal APIs, the Day-1/Day-2 architecture (isDay2 / setupDay2 /
  day2DialogContent), scene registration, translations, the Cardinal Feast top-down mini-game,
  asset/portrait conventions, and the verify-with-node-check habit. Also records where the main
  murder-mystery storyline currently stands.
---

# weird-game — developer conventions

A Phaser **3.88** point-and-walk RPG (side view: the player "priest" moves **horizontally**,
click-to-move + arrows, via `systems/player/PlayerMovementSystem.js`). Runs under Electron
(`npm start`). Scenes are plain JS classes extending `scenes/GameScene.js`.

## Golden rule: verify every edit
`.js` files use ESM `import`, so `node --check scenes/X.js` fails ("Cannot use import…").
Copy to a `.mjs` first:
```bash
cp scenes/Foo.js /tmp/_chk.mjs && node --check /tmp/_chk.mjs && echo OK; rm -f /tmp/_chk.mjs
```
For dialog trees, write a throwaway Node harness that stubs `global.Phaser` and the
`JournalSystem` import, calls the `dialogContent`/tree getter, and asserts every `next` target
exists and no `text()`/`choices()` function throws. (Examples were used for CardinalFeast and
the Ortolan tree — replicate that pattern.)

## Dialog system (`GameScene.showDialog` + `get dialogContent()`)
A scene exposes `get dialogContent()` returning a map of `stateKey -> stateObject`. Always spread
the parent: `return { ...super.dialogContent, /* states */ }`.

State shape:
- `speaker`: display name (or set once at the top level of the returned object; states inherit).
- `text`: string, **or** a function `() => string` (computed at show time), **or** used with `textKey`.
- `textKey`: a stable short key used for i18n lookup when `text` is conditional (preferred over
  matching the raw English string).
- `options`: `[{ text, key, next, onSelect?, onTrigger? }]`.
  - `next`: state id to go to. `next: 'closeDialog'` closes the dialog.
  - `onSelect: () => {…}`: runs when that option is clicked (side effects, launching scenes, etc.).
- `onTrigger`: runs **on show** (no arg) **and** on option click (receives the `option`). If it
  **returns a state id**, navigation goes there instead of `option.next`. Guard side effects with
  `if (!this.hasJournalEntry(...))` so re-runs are harmless.
- `onShow`: if present, it renders instead of the normal box (used for game-over/custom overlays).
- `hideCloseOption: true`: hides both the list "Leave" option **and** the top-right X button
  (we made the X respect it) — use for non-closable/forced dialogs.

## Quests — `this.questSystem` (also `registry.get('questSystem')`)
- `getQuest(id)` → quest or undefined; `quest.isComplete`; `quest.updates` is `[{key,...}]`.
- `addQuest(id, title, description)`, `updateQuest(id, progressText, updateKey)`, `completeQuest(id, updateKey?)`.
- Gate on quest state, e.g. `!!this.questSystem?.getQuest('ortolan_arms')?.isComplete`.

## Journal — `this.journalSystem` (`JournalSystem.getInstance()` singleton)
- `this.hasJournalEntry(id)` (returns the entry, truthy) / `this.getJournalEntry(id)`.
- `this.addJournalEntry(id, title, content, category, metadata)`. Entries + `metadata` persist via save.
- Categories: `this.journalSystem.categories.{PEOPLE,PLACES,EVENTS,LORE,DREAMS,FACTIONS}`.
- Persisted journal entries are the durable flags the whole game gates on (survive save/load).

## Day 1 / Day 2 architecture — DO NOT duplicate scenes
Day 2 begins after the player sleeps at the end of Day 1. Held by journal
`day1_complete_slept` (+ registry `gameDay = 2`). Base helper: **`this.isDay2()`** (in `GameScene`).

Convention for a location that differs on Day 2:
- **Code:** `create()` does the common setup, then `if (this.isDay2()) this.setupDay2();`.
  Put all Day-2 spawns/props in one `setupDay2()` method.
- **Dialog:** put Day-2 states in `get day2DialogContent()` and merge conditionally:
  `return { ...super.dialogContent, /* day1 */ , ...(this.isDay2() ? this.day2DialogContent : {}) }`.
- When Day-2 content grows large, extract it to `scenes/day2/<Location>Day2.js` (a function that
  adds NPCs + returns dialog states) and import it — separates *code*, not scene *identity*.

**Why not `FooScene2`:** transition targets are hard-coded scene keys in *every neighbor*
(`createTransitionZone(..., 'BurningBearStreetScene', ...)`). A Day-2 scene clone forces day
branching into all neighbors' transitions + doubles scene registration + complicates save/load.
Reserve a **separate scene** only for (a) special content launched directly via
`this.scene.start('X', data)` (e.g. `CardinalFeastScene`), or (b) a radically transformed hub.

## Adding / registering a scene
- New scene: class `extends GameScene`, `super({ key: 'FooScene' })`, `preload()` (load bg + assets),
  `create()` (call `super.create()`, add bg image at 400,300 sized 800×600 depth -1, make a
  `SceneTransitionManager`, position `this.priest`, add transition zones), and at file end:
  `if (typeof window !== 'undefined') window.FooScene = FooScene;`.
- Register in **`main.js`**: add the `import` and add the class to the `scene: [ … ]` array.
- `SceneTransitionManager.createTransitionZone(x, y, w, h, direction, targetSceneKey, walkToX, walkToY, label?)`.

## NPCs in side-view scenes
Add a sprite, `setInteractive({ useHandCursor: true })`, and
`sprite.on('pointerdown', () => { if (this.dialogVisible) return; this.showDialog('foo_start'); })`.
Add a name label above it. First-meeting journal entry is a nice touch.

## i18n / Czech translations
- English text lives in each scene's `dialogContent`. Czech lives in
  `lang/cs/dialogs/<SceneKey>.js`, **registered in `lang/cs/dialogs/index.js`** (add both the
  `import` and the entry in the exported map — miss either and it silently falls back to English).
- `LanguageSystem.translateDialog` matches by **state key** and each option's **`key`**; speaker
  names via a `_speakers` map. `text` in the cs file may be a single string (always replaces) or an
  **object keyed by `textKey`** (preferred for conditional text) or by the exact English string.
- **Limitation:** procedurally-generated text (Cardinal Feast beats, the Day-1 dream/nightlife
  cutscene) bypasses `translateDialog` and is **English only**. Launch/frame dialogs ARE translated.

## The Cardinal Feast mini-game (`scenes/CardinalFeastScene.js`)
Standalone `Phaser.Scene` (NOT GameScene) — a **top-down, walkable** RPG launched via
`this.scene.start('CardinalFeastScene', { returnScene: '…' })`. It has its own movement +
collision + **A\* pathfinding** (routes around obstacles), proximity/click talk, portrait dialog,
and a generative Web-Audio organ score.
- **Character art is data-driven via `artKey(role, override)`** — one map feeds BOTH the overworld
  token (`makeToken`) and the dialog portrait (`drawPortrait`). To add a character: drop a
  **transparent-corner** PNG, `this.load.image(...)` in `preload()`, add one line to the `ART` map.
  Emils (player) uses `emils1/2/3` (pose per beat); Pim/Vesper(inquisitor)/Marigold/Cornelius/
  Wren/Gallow have art; Twins/Foyle/Quill are still placeholder drawn tokens.
- Verify a character PNG is transparent: `convert file.png -format '%[pixel:p{2,2}]' info:` → `srgba(0,0,0,0)`.

## Main storyline status (quest `who_killed_bishop`) — keep this current
- **Day 1: done** — find Bishop, gather clues, Dr. Elphi analysis, Sulkberry dead-end, Townhall
  (mad-poet poetry battle → clerk reveals the missing notebook), report to Elphi, she *buys* a
  dream, nightlife cutscene, sleep.
- **Day 2: partly done** — Elphi's repaired cartridge → play **The Cardinal Feast**; NPCs leak that
  the Bishop hid her journal at the **Egg Cathedral**; Infinite Fold glitch ending. Elphi (feud
  canon) sends you to **Ortolan on Burning Bear Street**, whose help/info is gated on the Day-1
  `ortolan_arms` quest; he points to a Loop backup in the **Scraper cellar** (old lab) and, if
  helped, reveals the "losing move" needed to free a trapped mind.
- **Scraper cellar / Infinite Fold: done** — the player awakens an emergent authorless mind
  ("Infinite Fold") in the sealed cellar (durable flag: journal `met_infinite_fold`). It reveals
  the Bishop's death: it and a kindred unborn mind (the presence hatching in the Egg Cathedral)
  offered to make the Bishop their human conduit; she refused; it misread the refusal as a runtime
  fault and destroyed her trying to "complete" her.
- **Pre-finale optional perspectives (in progress):** after `met_infinite_fold`, key NPCs gain a
  conditional `[Before entering the cathedral] …` option in their hub state for differing takes —
  these are OPTIONAL flavor, NOT a gate before the Egg Cathedral finale. Done: **Sister Calyx /
  Pith Reclaimers** at `VoxmarketHallScene` (`calyx_start` → `calyx_seal_law` → guardian orders /
  true purpose). Adds journal `bishop_seal_true_purpose` (LORE): the Bishop's seal reads *outward* —
  it protects the world from anyone who would seek to OWN new life, and the Sentinel of the Veil's
  standing order was to bar only the *acquisitive*. Also done: **Angle Corrector / Lumen Directorate**
  at `LumenDirectorateInteriorScene` (`ac_start` → `ac_fold_perspective` → `ac_fold_complete` /
  `ac_fold_danger`). Adds journal `perspective_lumen` (FACTIONS): the Directorate wants the nascent
  god to COMPLETE its emergence, not be stopped — the danger is they help too much and accelerate it,
  the same misread that killed the Bishop, only larger. Also done: **Ortolan** at
  `BurningBearStreetScene` (`ortolan_bb_start` → `ortolan_bb_perspective` → `ortolan_bb_mechanisms`
  / `ortolan_bb_sentinel`), a maker's take: "something can be beautiful and still be badly designed";
  the machinery around the cathedral is failing old-order work, and the Sentinel of the Veil is the
  last mechanism of the old order still running — a made thing executing a dead instruction. Adds
  journal `perspective_ortolan` (LORE).
- **Not built yet:** the **Egg Cathedral** notebook content / finale (scene is a bare shell) and the
  **resolution** — `who_killed_bishop` is never `completeQuest`-d. Angle Corrector (Lumen Directorate
  interior) has a partial bishop branch. Open threads: doppelgänger, myceliar distress call, Vestigels.

Read `WORLD_HISTORY_AND_GEOGRAPHY.md` for lore/canon before writing story content.
