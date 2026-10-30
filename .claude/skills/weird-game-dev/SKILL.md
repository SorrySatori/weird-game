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
- `onTrigger`: runs **on show** (no arg). It runs again on an option click **only if it declares the parameter**
  (`onTrigger: (option) => { if (!option) return; … }`) — then a returned state id navigates there instead of
  `option.next`. A param-less `() => {}` handler is show-only, so its side effects (G/D, quest completion, item
  removal) happen once per showing. Re-showing a state still re-runs it: guard one-time effects
  (`if (!this.hasJournalEntry(...))`, `onceEver`).
- `onShow`: if present, it renders instead of the normal box (used for game-over/custom overlays).
- `hideCloseOption: true`: hides both the list "Leave" option **and** the top-right X button
  (we made the X respect it) — use for non-closable/forced dialogs.

## Quests — `this.questSystem` (also `registry.get('questSystem')`)
- `getQuest(id)` → quest or undefined; `quest.isComplete`; `quest.updates` is `[{key,...}]`.
- `addQuest(id, title, description)`, `updateQuest(id, progressText, updateKey)`, `completeQuest(id, updateKey?)`.
- Gate on quest state, e.g. `!!this.questSystem?.getQuest('ortolan_arms')?.isComplete`.
- Same no-spoiler rule as the journal: a quest description/update says only what the player knows when it
  is written; later reveals are NEW updates (new key) at the revealing state. Keys are often flags — never rename
  them or move when they're written. Translations: `quests.<id>.{title,description,updates.<key>}` in `lang/{en,cs}/quests.js`.
- **Runtime-built update text** (numbers, names, route variants): never bake it untranslatable — pass a 4th arg
  `updateQuest(id, englishText, key, { textKey, ...values })` (saved with the update). The quest log looks up
  `quests.<id>.updates.<textKey || key>` and fills `{name}` placeholders from the values. Pick the wording in code:
  counts via `countForm(n)` from `systems/LanguageSystem.js` → `'one'|'few'|'many'` (1 / 2–4 / 0,5+ — Czech forms;
  EN gives few+many the same text), e.g. `textKey: 'lamps_found_' + countForm(n)`. The English in code must equal the
  EN lang text with values filled. Old saves (no params) keep showing their stored text. Examples: `utils/GangOfLamps.js`.
- A dialog state with `onShow` is NOT rendered (GameScene runs it and returns) — use `onTrigger` for side effects
  of a state that has text/options; `onShow` is only for close/launch states.

## Journal — `this.journalSystem` (`JournalSystem.getInstance()` singleton)
- `this.hasJournalEntry(id)` (returns the entry, truthy) / `this.getJournalEntry(id)`.
- `this.addJournalEntry(id, title, content, category, metadata)`. Entries + `metadata` persist via save.
- Categories: `this.journalSystem.categories.{PEOPLE,PLACES,EVENTS,LORE,DREAMS,FACTIONS}`.
- Persisted journal entries are the durable flags the whole game gates on (survive save/load).
- **Never journal what the player hasn't learned yet.** An entry holds only what is known at the moment it is
  written; anything revealed later is a *fact* appended to it: `this.addJournalFact(id, factId, englishText)` in the
  onTrigger of the state where it is revealed (idempotent per factId; may fire before the entry exists — it shows once
  the entry is created; persisted in saves). Translations: `journal.<id>.facts.<factId>` in `lang/{en,cs}/journal.js`.
  The journal shows description + facts one per line; `journalSystem.hasFact(id, factId)` can gate on a fact.
  Don't move the creation point of an entry that is used as a flag; change its text and add facts instead.

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
- **Arrow keys + screen edges:** the priest stops at the screen edge; a `left`/`right` zone touching that edge is also
  taken by walking into it (registered automatically by createTransitionZone). A custom exit hotspot (not a
  transition zone) at an edge must register itself: `this.registerEdgeExit('left', () => this.leaveByEdge('left', 'TargetScene'), hotspot)`
  (examples: SkyshipBoardScene, ScraperInteriorScene).
- **Growth/Decay scenery:** `utils/GDProps.js` — `preloadGDProps(this)` in preload, then in create
  `applyGDBackground(this, bg, 'FooBg')` (swaps to `FooBg_growth`/`_decay` if that art exists) and
  `placeGDProps(this, { growth: [{prop,x,y}], decay: [...] })` (canvas coords, feet ≤ 520). Props: bush, vine (top anchor),
  mushrooms / trash, crate, rubble, fire (animated + glow). Tendency = `getGDTendency()` (≥65). Examples: Shed521Scene, CrossroadScene.
  Test keys (GameScene, `DEBUG_GD_KEYS`): F7 full Growth / F8 full Decay / F9 balanced → restarts the scene.
  **Scene instances are re-used:** reset per-run guards/cached objects at the top of `create()`.
- **State-dependent scenery is a sprite with frames, not alternate backgrounds.** Example: `CrossroadScene`
  loads `crossroad_corpse.png` as a 3-frame spritesheet (`CORPSE_FRAME` intact/cut/growth) and swaps
  `setFrame()` on the decision; the background never changes. Aseprite sources for redrawn art live in
  `assets/aseprite/`.

## NPCs in side-view scenes
Add a sprite, `setInteractive({ useHandCursor: true })`, and
`sprite.on('pointerdown', () => { if (this.dialogVisible) return; this.showDialog('foo_start'); })`.
Add a name label above it. First-meeting journal entry is a nice touch.

**Ambient people** (figures you can't talk to — queues, clerks, passers-by): don't bake them into the background, use
`createAmbientNpc(scene, { id, key, x, y, holds, top })` from `utils/AmbientNpc.js` — an animated feet-anchored sprite
(depth 6) whose click shows one line in a speech bubble (cycling `ambient.<id>.lines`, hover label `ambient.<id>.name`,
both in `lang/en/ambient.js` + `lang/cs/ambient.js`). Example: Shed521FloorsScene (`FLOORS_FOLK`).

## Inventory items (`systems/inventory/InventorySystem.js`)
- **No capacity limit.** The panel is a paged 6×3 grid (arrows + mouse wheel); `addItemToInventory` never
  fails for being "full", so quest items can always be handed out without checking the return value.
- Display order is a stable group sort on `item.type`: `key_item` → `tool` → `drug`/`consumable` →
  untyped (pickup order) → `recording` → `decoration`. Give purchasable sounds `type: 'recording'`.
- `useItem(index)` / `removeItemFromInventory(index)` take the REAL index into `inventory.items`; slots carry
  it as `slot.itemIndex`, so never use a slot position as an item index.
- **Sound ampules (Voxmarket):** `utils/Recordings.js` is the catalogue — one entry = one playable item sold by
  Zerren (`VoxmarketMarketScene.initShopSystem` spreads `recordingShopStock()`). Add a recording: normalized mp3
  into `assets/sounds/recordings/`, entry in `RECORDINGS` (id, file, price, tint), `items.<id>` in
  `lang/en/game.js` + `lang/cs/game.js`. LoadingScene preloads them; the inventory plays/stops on click
  (`toggleRecording`, music ducked to 0.25 meanwhile). Shared icon `ampule` tinted per item.

## i18n / Czech translations
- English text lives in each scene's `dialogContent`. Czech lives in
  `lang/cs/dialogs/<SceneKey>.js`, **registered in `lang/cs/dialogs/index.js`** (add both the
  `import` and the entry in the exported map — miss either and it silently falls back to English).
- `LanguageSystem.translateDialog` matches by **state key** and each option's **`key`**; speaker
  names via a `_speakers` map. `text` in the cs file may be a single string (always replaces) or an
  **object keyed by `textKey`** (preferred for conditional text) or by the exact English string.
- **Limitation:** procedurally-generated text (Cardinal Feast beats, the Day-1 dream/nightlife
  cutscene) bypasses `translateDialog` and is **English only**. Launch/frame dialogs ARE translated.

## Edgar's book (`utils/EdgarBook.js`, quest `edgar_book` in ScreamingCorkScene)
The player's picks (≤3 topics, tone, genre, protagonist, setting) generate a whole book: title + "aneb …"/"or, …"
subtitle, blurb, three excerpts, reviews (only from NPCs the player has met — journal ids), a thank-you to the 3rd topic.
- Every pick is a POOL drawn with a seed fixed at quest start (`registry.edgarBookDraft`, persisted in saves; the
  finished draft is copied to journal `edgar_book_completed.metadata.book_draft`) → `composeBook(draft, lang, knows)`.
- Picks bend each other: genre `funny animals` swaps hero + villain pools for animals (political → the Fascist Stag),
  `SPECIAL_TITLES` for genre|tone pairs, genre picks the MacGuffin, topics become cameo characters (`CAMEOS`).
- Czech is native and declined: entities carry cases `n g d a i l` (+ places `in to from`) and a gender class;
  templates use `{P.a}`, agreement `{P:m|f|n|pl}` / `{P:sg|pl}`, `{^…}` capitalises; relative-clause tails get their
  closing comma automatically. Validate new content by rendering all combinations (no `{`/`undefined` left).
- Dynamic texts are localized in the scene (`cs ? … : …`); the cs dialog file only translates option keys there.

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
  Ink Tribunal** at `VoxmarketHallScene` (`calyx_start` → `calyx_seal_law` → guardian orders /
  true purpose). Adds journal `bishop_seal_true_purpose` (LORE): the Bishop's seal reads *outward* —
  it protects the world from anyone who would seek to OWN new life; the Sentinel of the Veil's
  standing order (bar only the *acquisitive*) is a fact added in `calyx_seal_guardian_orders`. Also done: **Angle Corrector / Lumen Directorate**
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
- **Brine Scripture "Salt Recall" lore probes (optional flavor):** if the player carries the
  `brine-scripture` symbiont, certain scenes offer a gated `[Salt Recall] Read …` dialog option
  whose lore state (`speaker: 'Brine Scripture'`) reads the salt/mineral place-memory of a thing and
  writes a once-only `LORE` journal entry (`{ via: 'brine-scripture' }`). Done in: **CrossroadScene**
  (`salt_recall_crossroad_corpse`), **GodgraveyardScene** (Hvétrdjaana's unreadable grave →
  `salt_recall_hvetrdjaana`), **AbandonedBusScene** (the bus is a Before-Time dead spot the mycelial
  signal never reached → `salt_recall_abandoned_bus`), **RustDomainScene** (the machines' corrosion
  remembers Nexicorp → the Emergence → the feasts → `salt_recall_rust_machines`). Pattern is easy to
  replicate in more scenes; not a quest gate.
- **Osswine "Grave-Sense" death-reading probes (optional flavor):** the mirror of Salt Recall. If the
  player carries the `osswine` symbiont (the "late mourner," bonded at **GodgraveyardScene**'s ossuary
  niche), certain scenes gate a `[Grave-Sense]` option (Czech `[Hrobový smysl]`) whose lore state
  (`speaker: 'Osswine'`) reads the ENDING of a dead/decayed thing — HOW it died, its last intent, what
  it was before it stopped — and writes a once-only `LORE` journal entry (`{ via: 'osswine' }`).
  Distinct from Brine's place/salt reading. Done in: **CrossroadScene** (the giant corpse chose to stop
  → `grave_sense_crossroad_corpse`), **RustDomainScene** (a buried/silenced machine ended mid-memory,
  gated in `brukk_machines_status` → `grave_sense_rust_machine`), **GodgraveyardScene** (Vhorn the
  Tally-Keeper died the instant a follower proved the sums never balanced → `grave_sense_vhorn`),
  **AbandonedBusScene** (the Bishop's body: read via the `dead_bishop_start` exam hub — deliberately
  EVOCATIVE & AMBIGUOUS, a mind ended over and over in a doorless loop, does NOT name Infinite Fold/the
  cause → `grave_sense_bishop_body`), **EggCathedralInteriorScene** (the cathedral's servants did not
  die but dissolved willingly into the growing god, read at `priests_look` → `grave_sense_servants`).
  Speaker cs is `'Osswine': 'Osswine'`. Idempotent; not a quest gate.
- **Palinode "Seam-Sense" traversal hooks (optional flavor):** if the player carries the `palinode`
  symbiont (the unsaying; bonded at **EchoDrainDeltaScene**), certain scenes gate a `[Seam-Sense]`
  hook (`speaker: 'Palinode'`; Czech `[Smysl pro švy]`) that OPENS a hidden/sealed way others can't —
  a passage where one fits, else a lore pocket/cache. Idempotent, no quest completion; persisted via a
  registry flag and/or a once-only journal entry (`{ via: 'palinode' }`). Done in: **EchoDrainDeltaScene**
  (alt crossing, registry `delta_seam_opened`, journal `delta_seam_crossing`), **EggCatedralScene**
  (alternate way to Edgar's study gap WITHOUT Edgar — the gap transition is now created if Edgar's
  path OR Palinode; Palinode-found adds journal `seam_sense_cathedral_gap`), **ScraperInteriorScene**
  (Lift-Mother `lift_mother_start` → `seam_scraper_prompt` → `seam_scraper_open`; unseals a "dead
  floor" lore pocket, registry `scraper_deadfloor_opened`, journal `seam_sense_scraper_floors`, +12
  spores), **ShedAbandonedOfficeScene** (hotspot reveal of a bricked tunnel toward the Living Core —
  registry `shed_tunnel_opened` restored in `create()`, journal `seam_sense_shed_tunnel`, +12 spores;
  hotspot+notification instead of a dialog tree since this scene has no cs file). Speaker cs is
  `'Palinode': 'Palinode'`. Pattern easy to replicate; not a quest gate.
- **The Gang of Lamps questline (`gang_of_lamps`) — COMPLETE (L1+L2+systems+betrayals+CZ):** four disguised
  sentient street-lamps, IMMOVABLE and out of contact, who use the player as courier. Shared mechanic lives in
  **`utils/GangOfLamps.js`** (moved off GameScene): `createStreetLamp(scene,texKey,x,y,scale,dialogKey,depth)`
  (returns null once the Gang is destroyed), `meetLamp(scene,id,name)` (idempotent; writes `met_lamp_<id>`,
  starts/advances `gang_of_lamps`), `lampsFoundCount(scene)`, plus L2 helpers `GANG_QUEST_IDS`,
  `gangQuestStatus`, `spyFragmentCount`/`recordSpyFragment`, `spyReportable`/`eavesdropReportable`/`smuggleReportable`,
  `gangDeceived`, `destroyGangLamps`, `grantGangVestigel`. Scenes `import {…} from '../utils/GangOfLamps.js'` and pass `this`.
  **Placements:** **Don Girandole** (`don`, **ScraperScene**, `lamp_don`), **Chandelier** (`chandelier`,
  **TownSquareScene**, `lamp_chandelier`), **Sconce** (`sconce`, **TownhallScene EXTERIOR**, `lamp_sconce`),
  **Torchère** (`torchere`, HarborScene, `lamp_torchere`). Each `<id>_lamp_start` switches `textKey` among
  `_first`/`_first_some`/`_first_last`/`_searching`/`_connected` (progress-aware) and calls `meetLamp` in `onTrigger`.
  **L2:** once all four connected, each lamp offers a quest → all done → Don gives a real `'vestigel'`. Don=spy
  the Rust Choir (Brukk/Gnur/Ravla), Torchère=smuggle Wickmilk+Gloamdust to a dead-drop, Chandelier=eavesdrop at
  the Lumen vent, Sconce=recover a misfiled dossier. Each quest uses **G/D** (`this.modifyGrowthDecay`) and offers
  optional **symbiont routes** (Neme/Osswine/Ulvarex/Brine/Palinode, gated by G/D silence thresholds). **Betrayals:**
  tell the target faction (false intel + rep + G/D), fence/divert the drugs; giving drugs to the Lumen is TERMINAL —
  `destroyGangLamps` removes all lamps forever (no Vestigel). Full detail in memory `gang-of-lamps-quest.md`.
  **CZ:** done — all states in `lang/cs/dialogs/*` (incl. new `ScraperScene.js`, registered in `dialogs/index.js`);
  13 fixed journal ids in en+cs; route-variant journals intentionally EN-only.

Read `WORLD_HISTORY_AND_GEOGRAPHY.md` for lore/canon before writing story content.
