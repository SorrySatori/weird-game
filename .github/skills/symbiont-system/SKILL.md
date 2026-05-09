---
name: symbiont-system
description: 'Use when explaining, implementing, balancing, or reviewing Weird Game symbionts, symbiont powers, symbiont dialog, ability checks, growth/decay/spore scaling, or NPC interactions unlocked by Thorne-Still, Neme, or Ulvarex.'
argument-hint: 'Describe the symbiont task, power, scene interaction, or balance question'
user-invocable: true
---

# Symbiont System Skill

Use this skill when working with symbionts in Weird Game: explaining existing powers, adding symbiont dialog, wiring scene-specific ability options, balancing power thresholds, or checking how growth, decay, and spores affect symbionts.

## Current Symbionts

The game currently has three symbionts:

| Symbiont | ID | Ability | Power Source | Main Use |
|---|---|---|---|---|
| Thorne-Still | `thorne-still` | Brain Rot | Decay | Confuse, destabilize, or weaken NPC reasoning |
| Neme of the Crownmire | `neme-crownmire` | Photosentience | Growth | Read bio-signals, hidden motives, and emotional truth |
| Ulvarex the Borrowed Horizon | `ulvarex-borrowed-horizon` | Mirage Weave | Spores | Create illusions and false sensory context |

## Power Scaling

### Thorne-Still — Brain Rot

- **Power source:** Decay.
- **Formula:** `power = min(100, decay)`.
- **Removal condition:** if Growth rises above `80`, Thorne-Still leaves the player.
- **Ability threshold:** `Brain Rot` is available only when Thorne-Still power is above `30`.

**What Brain Rot does:**
Brain Rot releases cognitive decay into a target during dialog. It is used to make NPCs confused, forgetful, suggestible, poorly coordinated, or less effective as rivals. It should feel intrusive and risky, not like ordinary persuasion.

**Typical scene uses:**
- Make a rival bidder forget their goal.
- Break a coordinated performance or negotiation tactic.
- Cause a guard, bureaucrat, or faction agent to misremember details.
- Open a shortcut by degrading someone’s certainty.

**Tone guidance:**
Brain Rot is decay-aligned. It should feel corrosive, unfair, and slightly grotesque. Use it for manipulation through mental fraying, not for physical attacks.

### Neme of the Crownmire — Photosentience

- **Power source:** Growth.
- **Formula:** `power = min(100, growth)`.
- **Silence condition:** if Decay rises above `70`, Neme becomes `silenced`.
- **Recovery condition:** when Decay returns to `70` or below, Neme recovers.
- **Active ability cooldown:** `usePhotosentience()` has a one-minute cooldown.

**What Photosentience does:**
Photosentience reads living signals beneath speech: fear, guilt, pressure, concealed motives, biological stress, emotional residue, and truths the target is trying not to reveal. It does not simply say “this NPC is lying”; it should reveal the living shape of the lie or need.

**Typical scene uses:**
- Detect a hidden motive in dialog.
- Reveal what an NPC actually values.
- Identify pressure, fear, illness, or emotional leverage.
- Add a compassionate or exploitative branch based on revealed truth.

**Tone guidance:**
Photosentience is growth-aligned. It should feel organic, sensory, and interpretive: roots, pulses, sap, breath, filaments, blooming signals. It reveals truth through life-patterns rather than logic.

### Ulvarex the Borrowed Horizon — Mirage Weave

- **Power source:** Spores.
- **Formula:** `power = min(100, floor(sporeLevel / 2))`.
- **Resource dependency:** low spore reserves make illusions weaker or unreliable.

**What Mirage Weave does:**
Mirage Weave creates convincing illusions anchored to existing sensory material: shadows, reflections, memories, visible objects, or expectations. It does not create real matter from nothing. It bends perception to make NPCs believe something plausible, useful, frightening, beautiful, or strategically misleading.

**Typical scene uses:**
- Create a distraction.
- Fake a message, object, threat, creature, or environmental clue.
- Mislead a rival about an item’s condition or value.
- Let an NPC reveal themselves by reacting to a fabricated perception.

**Tone guidance:**
Mirage Weave is perception-aligned rather than growth/decay-aligned. It should feel theatrical, elegant, unreliable, and clever. Good illusions exploit what the target already expects or wants to believe.

## Implementation Workflow

When adding a symbiont interaction to a scene:

1. Check whether the scene already computes the needed symbiont flags near the top of `dialogContent`.
2. Use existing checks such as:
   - `this.symbiontSystem?.hasSymbiont('thorne-still')`
   - `this.symbiontSystem?.hasSymbiont('neme-crownmire')`
   - `this.symbiontSystem?.hasSymbiont('ulvarex-borrowed-horizon')`
3. Add a conditional dialog option with a stable `key`.
4. Put the result in a dedicated dialog state.
5. Use persisted journal entries for lasting story state, not transient registry flags.
6. Add Czech translations in the matching `lang/cs/dialogs/<SceneName>.js` file.
7. If conditional dialog text has multiple variants, use stable `textKey` IDs rather than English prose as translation keys.
8. Validate the edited scene and translation file.

## Dialog Option Patterns

Use ability labels consistently:

```js
...(hasThorne ? [{
    text: "[Brain Rot] Confuse them.",
    key: 'brain_rot_confuse_them',
    next: "npc_brain_rot"
}] : [])
```

```js
...(hasNeme ? [{
    text: "[Photosentience] Read their bio-signals.",
    key: 'photosentience_read_their_biosignals',
    next: "npc_neme_read"
}] : [])
```

```js
...(hasUlvarex ? [{
    text: "[Mirage Weave] Create a distraction.",
    key: 'mirage_weave_create_a_distraction',
    next: "npc_mirage"
}] : [])
```

## State and Persistence

Use journal entries for symbiont-driven outcomes that must persist:

```js
this.addJournalEntry(
    'npc_confused_by_thorne',
    'Thorne-Still Confused the Negotiator',
    'Used Brain Rot to scramble the negotiator’s prepared argument.',
    this.journalSystem.categories.EVENTS,
    { character: 'NPC Name' }
);
```

Then check that entry at the top of `dialogContent`:

```js
const npcConfused = !!this.hasJournalEntry('npc_confused_by_thorne');
```

## Balance Guidance

- Thorne-Still should solve problems by damaging certainty, memory, or cognition.
- Neme should solve problems by revealing living truth, motive, or vulnerability.
- Ulvarex should solve problems by changing what others believe they perceive.
- Avoid making all three powers interchangeable.
- Avoid using symbiont powers as generic win buttons; each should produce story consequences or altered NPC behavior.
- If an ability weakens an auction rival, guard, or faction agent, record the result with a journal entry so later scenes can react.

## Source Files to Check

- `systems/SymbiontSystem.js` — symbiont data, power scaling, dialogs, ambient messages.
- `scenes/**/*.js` — scene-specific symbiont options and outcomes.
- `lang/cs/dialogs/**/*.js` — Czech dialog translations for symbiont options and outcomes.
- `.github/instructions/symbiont-system.instructions.md` — baseline repository rules for symbiont implementation.
