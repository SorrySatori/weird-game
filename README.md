# Upper Morkezela: A Weird Game

A 2D point-and-walk adventure / RPG set in Upper Morkezela — a city grown over by fungus, run by a Stomach Clock, and haunted by the gods that came there to die. You play an apprentice of the Obazoba church sent to find the Bishop; you find her dead, and the rest of the game is working out who — or what — killed her.

Built with **Phaser 3** and shipped as an **Electron** desktop app. Fully bilingual: **English** and **Czech**.

## Running the game

Requirements: Node.js (developed on v24) and npm.

```bash
npm install
npm start          # Electron app via Electron Forge
npm run dev        # plain Electron with --dev flags
```

The game also runs in a normal browser — serve the repo root and open `index.html` (for example `npx http-server -p 8080`). Saves then fall back to `localStorage` instead of the Electron save files.

### Packaging

Two pipelines are configured:

```bash
npm run package    # Electron Forge — unpacked app
npm run make       # Electron Forge — deb / rpm / zip / squirrel installers
npm run dist       # electron-builder — AppImage + deb (Linux), NSIS (Windows), DMG (macOS)
```

Output goes to `out/` and `dist/`, both git-ignored. The `steam-build-*` and `weird-game-neutralino/` folders are local packaging experiments, not part of the build.

## Controls

| Input | Action |
|---|---|
| Mouse click | Walk to a spot, talk to a character, examine an object |
| Arrow keys | Move |
| **J** | Journal |
| **Q** | Quest log |
| **M** | Map |
| **Esc** | Game menu — save / load, settings, language |

Language can also be switched from the main menu. The choice is remembered between sessions.

## Project layout

```
main.js                 Phaser config (1067×600, 16:9, FIT scaling, pixelArt) + scene registry
index.html              loads Phaser from node_modules, game-api.js and main.js
electron-main.js        Electron window, save-file IPC
preload.js / game-api.js
                        save/load API (saves live in localStorage) + the Exit-game IPC bridge
scenes/                 46 scenes; every location extends scenes/GameScene.js
systems/                LanguageSystem, SaveSystem, QuestSystem, JournalSystem,
                        GrowthDecaySystem, SporeSystem, SymbiontSystem, FactionReputation,
                        EffectsSystem, inventory/ + items/, player/ (movement)
ui/                     journal, quest log, map, game menu, spore bar, Growth/Decay indicator
utils/                  scene transitions, dialog layouts, background fitting, item icons,
                        equipment tutorial, the Gang of Lamps questline helpers
lang/en/                journal, quests, observe, ui, game notifications, intro, location names
lang/cs/                the same, plus dialogs/ — one Czech file per scene
assets/                 images (backgrounds, characters, items, effects, ui), sounds, icons
scripts/                one-off tooling for dialog/translation keys (add, migrate, verify)
```

`GameScene` provides the shared mechanics every location builds on: click-to-move, the dialog system (`get dialogContent()` state trees with options, `onTrigger`, `textKey` variants), quests and journal, the Growth/Decay balance, symbionts, the examine/observe speech bubbles, notifications and the save hooks.

## Localization

English is the source language and lives in the scene code; Czech lives in `lang/cs/`. Dialog translations are matched by **state key** and each option's **`key`**, never by English text, so rewording a line never breaks its translation. Speaker names go through a `_speakers` map; conditional lines use a `textKey`. Journal entries, quests, observe lines, notifications and UI strings are keyed by id in the corresponding `lang/*` files and looked up with `this.t('…')`.

Text that is assembled at runtime (generated book titles, procedural appraisals, dynamic journal entries) is localized inside the scene that builds it — the translation layer can't template. The house rule is simple: **if the game has two languages, everything gets translated.**

The `scripts/*.mjs` tools were used to migrate option keys and can verify that every Czech file still matches its scene.

## Content and design docs

- `WORLD_HISTORY_AND_GEOGRAPHY.md` — world canon (English). Read before writing story content.
- `PROLOG.md` — the prologue, *Noc Pálení medvědů* (Czech).
- `MUSIC_BRIEF.md` — music brief per demo location, in the order the player visits them (Czech).
- `DRUG_EFFECTS_README.md` — the Oltrac drug-effects system (Kloor Venn's stall at the Voxmarket).
- `.claude/skills/weird-game-dev/SKILL.md` — developer conventions: dialog/quest/journal APIs, the Day 1 / Day 2 architecture, adding scenes, translations, and where the main storyline currently stands.

## Development notes

- Scene files are ES modules, so `node --check scenes/X.js` fails on the `import`. Copy to a `.mjs` first:
  `cat scenes/X.js > /tmp/x.mjs && node --check /tmp/x.mjs`
- When adding a scene: extend `GameScene`, register it in `main.js`, and add its Czech dialog file to `lang/cs/dialogs/index.js` — miss the latter and the scene silently falls back to English.
- Keep dialog option `key`s stable; they are the anchors for translations.
- Durable game state is journal entries (they survive save/load); gate content on those rather than on transient registry flags.

## Status

The demo (Day 1 and the first part of Day 2 of the murder mystery) is playable in both languages; its dialogs are being rewritten NPC by NPC. The Egg Cathedral finale is not built yet — see the storyline section of the skill file for the current state.
