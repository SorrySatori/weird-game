---
applyTo: "scenes/**/*.js,systems/**/*.js"
---

# Quest System — Weird Game

## Overview
Quests are managed by `QuestSystem` (singleton, `systems/QuestSystem.js`), accessible in any scene via `this.questSystem` or `this.registry.get('questSystem')`.

## Quest Object Shape
```js
{
  id: string,          // e.g. 'rust_feast'
  title: string,
  description: string,
  updates: [{ text, key, date }],
  isComplete: boolean,
  dateStarted: Date,
  dateCompleted: Date  // only when complete
}
```

## Key Methods

### Adding a quest
```js
this.questSystem.addQuest('quest_id', 'Quest Title', 'Initial description shown in log.');
```

### Updating progress
```js
this.questSystem.updateQuest('quest_id', 'New journal-style update text.', 'unique_update_key');
```
**Always** provide a unique `key` so updates can be checked with `.some(u => u.key === 'key')`.

### Completing a quest
```js
this.questSystem.completeQuest('quest_id');
```

### Checking quest state
```js
const quest = this.questSystem.getQuest('quest_id');
if (quest && !quest.isComplete) { ... }
if (quest?.updates.some(u => u.key === 'talked_to_ravla')) { ... }
```
> ⚠️ There is no `hasQuest()` method — always use `getQuest()` and null-check.

## Events emitted
- `questAdded(questId, title)`
- `questUpdated(questId, title)`
- `questCompleted(questId, title)`

These are handled in `GameScene.initSystems()` which shows notifications and marks unread indicators automatically.

## Conditional dialog options pattern
Define boolean variables at the top of the `dialogContent` getter, then spread options conditionally:
```js
get dialogContent() {
    const hasMyQuest = !!(this.questSystem?.getQuest('my_quest') && !this.questSystem.getQuest('my_quest').isComplete);
    return {
        ...super.dialogContent,
        npc_start: {
            text: "Hello.",
            options: [
                { text: "Normal option", next: "npc_generic" },
                ...(hasMyQuest ? [{ text: "Quest option", next: "npc_quest_branch" }] : [])
            ]
        }
    };
}
```

## Existing quests (as of March 2026)
| ID | Title | Giver / Scene | Notes |
|----|-------|---------------|-------|
| `find_bishop` | Find the Bishop of Threshold | Master Thaal — EntryScene (also re-added in CathedralEntrance) | Main story opener; Bishop found dead in AbandonedBusScene |
| `who_killed_bishop` | Who Killed the Bishop? | Auto-triggered — AbandonedBusScene | Investigation quest; evidence: neural trauma, Cardinal Feast dream device |
| `excavation_permit` | Divinography | Phor Calesta (archaeologist) — TownhallScene | Help Phor obtain excavation permits for the Godgraveyard |
| `ortolan_arms` | Extra Arms for Ortolan | Ortolan Šmelc — ShedCourtyardScene | Bureaucratic puzzle; multiple completion variants (artisan, deformity, dispensation, temporary, proxy, fungal) |
| `rust_reclamation` | Rust Reclamation | Gnur — Shed521Scene | Recover a living core from Shed 521 tunnels; keys: `core_delivered`, `quest_refused` |
| `edgar_book` | Help Edgar to write a book | Edgar Eskola — ScreamingCorkScene | Can be triggered via vestigel negotiation or book offer; reward is Writer's Vestigel |
| `the_three_vestigels` | The Three Vestigels | Kloor Venn — VoxMarket | Collect any vestigel from Zerren, Liss, Dovan, or Edgar; reward is info about Bishop + Dr. Elphi |
| `find_rust_choir` | Find the Rust Choir | Lift-Mother (elevator) — ScraperInteriorScene | Leads to Ravla at ScreamingCork; update keys: `talk_to_ravla`, `feast_complete` |
| `level_177_access` | Access to Level 177 | Lift-Mother (elevator) — ScraperInteriorScene | Reach Dr. Elphi Quarn's studio; paths: `button_path`, `repair_path`, `confession_path` |
| `rust_feast` | Rust Feast | Ravla — ScreamingCorkInteriorScene | Triggered after accepting `find_rust_choir` task; requires oil + metal_scrap + redmass (or Ulvarex illusion) |

### Quest chain relationships
- **Main story arc:** `find_bishop` → `who_killed_bishop` → `the_three_vestigels` → `level_177_access`
- **Rust Choir arc:** `find_rust_choir` → `rust_feast`
- **Bureaucracy arc:** `ortolan_arms`, `excavation_permit` (independent)
- **Side quests:** `edgar_book`, `rust_reclamation`

## Journal integration
Quest-related discoveries are often also logged as journal entries:
```js
this.addJournalEntry('unique_id', 'Title', 'Content text.', this.journalSystem.categories.EVENTS);
```
Check with `this.hasJournalEntry('unique_id')` before adding to avoid duplicates.
