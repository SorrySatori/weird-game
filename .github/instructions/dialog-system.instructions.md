---
applyTo: "scenes/**/*.js"
---

# Dialog System — Weird Game

## Overview
Dialogs are defined in each scene's `dialogContent` getter, which returns a dictionary of dialog state keys to dialog objects. The base dialog system lives in `GameScene.js`.

## Dialog Content Getter Pattern
```js
get dialogContent() {
    // Compute state conditions ONCE at the top
    const hasQuest = !!(this.questSystem?.getQuest('quest_id') && !this.questSystem.getQuest('quest_id').isComplete);
    const hasItem = !!(this.hasItem && this.hasItem('item_id'));
    const alreadyDone = !!this.hasJournalEntry('some_entry');

    return {
        ...super.dialogContent,  // ALWAYS spread super first

        npc_start: {
            speaker: 'NPC Name',
            text: `Dialog text here.`,
            options: [
                { text: "Option text", next: "npc_next_state" },
                ...(hasQuest ? [{ text: "Quest option", next: "npc_quest" }] : []),
            ]
        },
        npc_next_state: {
            speaker: 'NPC Name',
            text: `More dialog.`,
            options: []
        }
    };
}
```

## Dialog Object Shape
```js
{
    speaker: 'Name',       // Shown in yellow above dialog text. Optional if inherited.
    text: `Dialog text`,   // Shown in green (#7fff8e). Supports template literals.
    options: [],           // Array of option objects (see below)
    hideCloseOption: true, // Optional. Suppresses the auto-added "I should go" close button.
    onTrigger: () => {},   // Optional. Runs when dialog is SHOWN (before rendering). For side effects.
    onShow: () => {},      // Optional. Replaces dialog rendering entirely. Dialog never displays.
}
```

## Option Object Shape
```js
{
    text: "Display text",     // Shown as clickable option
    next: "dialog_state_key", // Key of the next dialog to show
    onSelect: () => {}        // Optional. Runs when option is clicked, before navigation.
}
```

## Key Rules

### 1. Always spread `super.dialogContent`
The base `GameScene` defines the special `closeDialog` state. Without spreading super, dialogs cannot close.

### 2. State key naming convention
Use `lowercase_snake_case`. Prefix with NPC/context name: `brukk_start`, `ravla_feast_cook`, `lift_mother_building`.

### 3. Default "I should go" close option
A close option ("I should go" → `closeDialog`) is **automatically appended** to every dialog's options unless `hideCloseOption: true` is set. You do NOT need to manually add a leave/farewell option.

### 4. `closeDialog` special key
Use `next: "closeDialog"` to close the dialog. This is defined in the base `GameScene.dialogContent` and calls `this.hideDialog()`.

### 5. Speaker inheritance
- A top-level `speaker` in the returned object applies to ALL dialogs in the scene.
- Per-dialog `speaker` overrides the top-level one.
- If no speaker is found, the system infers from the dialog key prefix using a built-in `speakerMap` or parent dialog group.

### 6. Conditional options with spread
Use the spread + ternary pattern to conditionally include options:
```js
options: [
    { text: "Always visible", next: "some_dialog" },
    ...(condition ? [{ text: "Conditional", next: "cond_dialog" }] : []),
]
```
Never use `if` statements inside the options array.

### 7. Conditional text with ternary
Use ternary operators in the `text` field for state-dependent dialog text:
```js
text: isAngry
    ? `"You dare return?!"`
    : `"Welcome back, friend."`,
```

### 8. `onTrigger` for side effects
Use `onTrigger` on the **dialog node** (not on options) for effects that should fire when the dialog is shown:
- Inventory changes (`this.removeItemFromInventory`, `this.addItemToInventory`)
- Quest updates (`this.questSystem.updateQuest`, `this.questSystem.completeQuest`)
- Journal entries (`this.addJournalEntry`)
- Faction reputation (`this.modifyFactionReputation`)
- Growth/Decay changes (`this.modifyGrowthDecay`)
- Notifications (`this.showNotification`)
- Registry flags (`this.registry.set`)
- Scene transitions (`this.scene.start`)

`onTrigger` can optionally return a dialog state key to override the next navigation.

### 9. `onSelect` for option-specific logic
Use `onSelect` on individual options when logic should run on that specific choice (vs. `onTrigger` which runs for the whole dialog state).

### 10. `onShow` replaces the dialog
If a dialog has `onShow`, **the dialog box never renders**. The callback runs instead. Used for:
- Auto-redirect based on conditions (e.g., money check → branch to different dialog)
- Immediate scene transitions

### 11. Options pagination
If a dialog has more than 3 options, the system auto-paginates with arrow navigation.

### 12. Used options tracking
Options are automatically tracked as "used" and grayed out (`#5a8c6b` instead of `#7fff8e`) on subsequent visits. The system uses `createDialogOptionKey(dialogState, optionText)` internally. This persists via registry.

### 13. Triggering dialogs from NPCs
Create interactive NPCs and bind dialog start:
```js
this.npc = this.add.image(x, y, 'npc_texture');
this.npc.setInteractive({ useHandCursor: true });
this.npc.on('pointerdown', () => {
    if (this.dialogVisible) return;  // Prevent double-opening
    this.showDialog('npc_start');
});
```

### 14. Persistence — use journal entries, not registry
For state that must survive save/load, check `this.hasJournalEntry('id')` rather than `this.registry.get('flag')`. The registry is in-memory only and not saved by `SaveSystem`. Journal entries, quests, faction reputation, and symbiont data ARE persisted.

### 15. Sound effects
- `dialogMurmur` plays automatically when an option is selected
- `clickSound` plays on UI interactions (close button, scroll, pagination)
- No manual sound handling needed in dialog definitions

## Common Patterns

### NPC with multiple conversation topics (post-quest)
```js
npc_start: {
    speaker: 'NPC',
    text: alreadyHelped
        ? `"Good to see you again."`
        : `"Who are you?"`,
    options: [
        ...(alreadyHelped ? [
            { text: "Tell me about X.", next: "npc_topic_x" },
            { text: "Tell me about Y.", next: "npc_topic_y" },
        ] : []),
        ...(!alreadyHelped ? [
            { text: "I need help.", next: "npc_help" },
        ] : []),
    ]
},
```

### Linear dialog chain (lore dump)
```js
npc_history: {
    speaker: 'NPC',
    text: `First part of the story...`,
    options: [
        { text: "What happened next?", next: "npc_history_2" },
    ]
},
npc_history_2: {
    speaker: 'NPC',
    text: `Second part of the story...`,
    options: [
        { text: "And then?", next: "npc_history_3" },
    ]
},
npc_history_3: {
    speaker: 'NPC',
    text: `Conclusion.`,
    options: []  // Auto "I should go" will appear
},
```

### Dialog with side effects on trigger
```js
npc_give_item: {
    speaker: 'NPC',
    text: `"Here, take this."`,
    options: [
        { text: "Thank you.", next: "closeDialog" }
    ],
    onTrigger: () => {
        this.addItemToInventory({ id: 'item', name: 'Item', description: '...' });
        this.showNotification('Received: Item');
        this.addJournalEntry('got_item', 'Got the Item', 'Description.', this.journalSystem.categories.EVENTS);
    }
},
```
