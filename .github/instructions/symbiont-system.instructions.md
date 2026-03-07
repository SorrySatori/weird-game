---
applyTo: "scenes/**/*.js,systems/**/*.js"
---

# Symbiont System — Weird Game

## Overview
Symbionts are parasitic/mutualistic entities that bond with the player and grant special abilities. Managed by `SymbiontSystem` (singleton, `systems/SymbiontSystem.js`), accessible in scenes via `this.symbiontSystem` or `this.registry.get('symbiontSystem')`.

## Symbiont Data Structure
```js
{
  id: string,           // e.g. 'thorne-still'
  name: string,         // Display name
  power: number,        // 0-100, scales with growth or decay
  ability: string,      // Ability name shown in UI
  lastSpoke: number,    // Timestamp, set automatically
  silenced: boolean,    // Optional, some symbionts can be silenced
  lastAbilityUse: number // Timestamp of last ability activation
}
```

## Key Methods

### Adding a symbiont (in scene code)
```js
const success = this.symbiontSystem.addSymbiont('symbiont-id', {
    name: 'Symbiont Name',
    power: 0,
    ability: 'Ability Name'
});
if (success) {
    this.showNotification('Gained Symbiont: Symbiont Name');
    this.addSymbiontIcon('symbiont-id', {
        name: 'Symbiont Name',
        power: 0,
        ability: 'Ability Name'
    });
}
```
> Adding fails if all unlocked slots are full. Player starts with 1 slot (max 3).

### Checking symbiont presence
```js
this.symbiontSystem.hasSymbiont('thorne-still') // boolean
```

### Removing a symbiont
```js
this.symbiontSystem.removeSymbiont('symbiont-id')
```

### Unlocking slots
Slot unlock is available at ShedRegistrationScene for 50 gold:
```js
this.symbiontSystem.unlockSlot()
```

## Growth/Decay Interactions
`checkDecayGrowthEffects(decay, growth)` is called when growth/decay changes. Each symbiont has an affinity:

| Symbiont | Affinity | Power Source | Removal Condition | Special |
|----------|----------|-------------|-------------------|---------|
| Thorne-Still | Decay | `power = decay` | Growth > 80 | — |
| Neme of the Crownmire | Growth | `power = growth` | Never removed | Silenced when decay > 70 |
| Ulvarex the Borrowed Horizon | Neither | `power = sporeLevel / 2` | Never removed | Illusions fail if spores < 10 |

## Registering a New Symbiont

To add a new symbiont, update these locations:

1. **SymbiontSystem.js** — Add to:
   - `this.symbiontPhrases['new-id']` — ambient messages array
   - `this.symbiontDialogs['new-id']` — dialog tree (main, ability, about states)
   - `checkDecayGrowthEffects()` — growth/decay behavior
   - `getSporeChangeMessage()` — optional spore change commentary

2. **Scene where obtained** — Add:
   - Dialog tree for encounter/accept/decline
   - `this.symbiontSystem.addSymbiont(id, data)` call
   - `this.addSymbiontIcon(id, data)` call
   - Journal entry for obtaining it
   - Registry flag to prevent re-encounter (e.g. via `hasJournalEntry`)

3. **Scenes where ability is used** — Add conditional dialog options:
   ```js
   ...(this.symbiontSystem?.hasSymbiont('new-id') ? [{
       text: "[Use Ability]", next: "ability_result"
   }] : [])
   ```

## Existing Symbionts

| ID | Name | Ability | Obtained | Affinity |
|----|------|---------|----------|----------|
| `thorne-still` | Thorne-Still | Brain Rot (confuse NPCs) | CrossroadScene (corpse) | Decay |
| `neme-crownmire` | Neme of the Crownmire | Photosentience (detect lies) | AbandonedBusScene (Bishop's body) | Growth |
| `ulvarex-borrowed-horizon` | Ulvarex the Borrowed Horizon | Mirage Weave (create illusions) | HarborScene (water mirage) | Spores |

## UI Integration
- Symbiont icons appear bottom-left in GameScene (60px spacing)
- Click icon → shows symbiont dialog (from `symbiontDialogs`)
- Tooltip on hover: name, power, ability
- Pulsing glow animation on icon

## Persistence
- `getSerializableData()` — returns data for SaveSystem
- `loadFromData(data)` — restores on load

## Messages
- `getRandomMessage(id)` — 20% chance ambient messages, 30s cooldown
- `getSporeChangeMessage(old, new)` — triggered by SporeSystem when spores change by ≥5
