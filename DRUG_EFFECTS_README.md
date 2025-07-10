# Oltrac Drug Effects System

This document explains the implementation of drug effects in the game, specifically for the Oltrac items that can be purchased from Kloor Venn in the VoxMarket scene.

## Overview

The drug effects system creates immersive visual experiences when the player uses Oltrac drugs from their inventory. Each variant of Oltrac (Gray, Violet, and Amber) produces different visual effects that match its description in the game's lore.

## Drug Types and Effects

### Gray Oltrac
- **Description**: A common variant of Oltrac with mild hallucinogenic effects
- **Visual Effects**: 
  - Light gray overlay with subtle pulsating opacity
  - Floating gray particles that drift slowly
  - Faint image of the drug in the background
  - Duration: 3 minutes

### Violet Oltrac
- **Description**: A medium-strength variant that enhances perception
- **Visual Effects**:
  - Purple-tinted overlay with pulsating opacity
  - More vivid and numerous floating particles in violet hues
  - Subtle camera shake effect
  - Drug image with rotation and scaling effects
  - Duration: 3 minutes

### Amber Oltrac
- **Description**: The rarest and most potent form that allows glimpses beyond reality
- **Visual Effects**:
  - Amber-tinted overlay with stronger pulsating
  - Intense particle effects with stars and circles in amber/gold colors
  - Camera shake and flash effects
  - Reality-warping effect that subtly distorts game objects
  - Duration: 3 minutes

## Implementation Details

The drug effects system consists of:

1. **EffectsSystem.js** - Core system that manages visual effects
   - Creates and manages a high-depth container for visual effects
   - Implements specific effect methods for each drug type
   - Handles cleanup and duration timing
   - Persists effects across scene transitions using the game registry

2. **InventorySystem Integration** - Detects when Oltrac items are used
   - Identifies drug items by ID
   - Triggers appropriate effects via the EffectsSystem
   - Closes inventory when drugs are used
   - Consumes the item after use

3. **GameScene Integration** - Ensures effects work in any scene
   - Initializes EffectsSystem in all scenes
   - Preserves active effects when changing scenes
   - Restores effects when entering a new scene

## Testing

A test script is included (`test-drug-effects.js`) that can be run in the browser console when in the VoxMarket scene. It adds buttons to manually trigger each drug effect for testing purposes.

## Future Enhancements

Possible future enhancements could include:

- Gameplay effects beyond visual (temporary stat boosts, special abilities)
- Sound effects specific to each drug type
- More advanced shader-based visual effects
- Integration with the Growth/Decay system (drugs affecting balance)
- Quest-related drug effects for specific storylines
