---
applyTo: "scenes/**/*.js,systems/**/*.js"
---

# Faction Reputation — Weird Game

## Overview
Faction standing is managed by `FactionReputation` (singleton, `systems/FactionReputation.js`), accessible in scenes via `this.factionSystem` or `this.registry.get('factionSystem')`.

## Factions
| Key | Display Name | Theme |
|-----|-------------|-------|
| `RustChoir` | Rust Choir | Decay, machine hunger, corroded iron |
| `PithReclaimers` | Pith Reclaimers | Fungal essence extraction |
| `LumenDirectorate` | Lumen Directorate | Growth, all life |

## Key Methods

### Modifying reputation (use via GameScene helper)
```js
this.modifyFactionReputation('RustChoir', 10);   // increase
this.modifyFactionReputation('RustChoir', -5);   // decrease
```
This calls `factionSystem.modifyReputation(faction, amount)` and automatically:
- Discovers the faction (marks it as known to the player)
- Emits `reputationChanged` event
- Shows a notification in the UI

### Reading reputation
```js
const rep = this.factionSystem.getReputation('RustChoir'); // returns number
```

### Checking if discovered
```js
this.factionSystem.isFactionDiscovered('RustChoir'); // boolean
```

## Reputation scale guidance
| Amount | Meaning |
|--------|---------|
| +15 | Major positive act (e.g. full Rust Feast) |
| +5 | Minor positive act (e.g. meager feast) |
| -5 | Betrayal / offence (e.g. sparing the redmass) |
| -15 | Major betrayal |

## Events emitted
- `reputationChanged(factionDisplayName, amount)` — handled in `GameScene.initSystems()` with automatic notification

## Rust Choir — specific context
The Rust Choir values:
- The feeding/maintenance of machines
- Redmass as a sacred ingredient (living metal)
- Acceptance of decay as natural process

Key reputation milestones with Ravla:
- Complete `rust_feast` quest with full living redmass → **+15 RustChoir**
- Complete `rust_feast` quest with illusory redmass (Ulvarex Mirage Weave) → **+10 RustChoir** (then **-20** when machines die in RustDomainScene)
- Complete `rust_feast` quest with voluntary shard → **+5 RustChoir**
- Spare the redmass when confronted by Ravla → **-5 RustChoir**

## Password: Lift Mother
The password to the Lift Mother elevator is **"Corrode"**. It is revealed by Ravla upon completing the `rust_feast` quest (either outcome). Stored as a journal entry (`rust_feast_completed_full` or `rust_feast_completed_shard`).
