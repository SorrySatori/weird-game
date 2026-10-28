/**
 * Ortolan's "extra arms" paperwork (quest `ortolan_arms`): which documents he accepts and what he gives
 * back for each. On Day 1 the player hands them over in ShedCourtyardScene (a reaction per form); on Day 2
 * he has moved to Burning Bear Street and takes whatever the player still carries (handOverArmsPaperwork).
 */
export const ARMS_PAPERWORK = [
    {
        form: 'artisan-exemption-form', growth: 5, decay: 0,
        reward: {
            id: 'game-prototype',
            name: "Sects & Stakes Prototype",
            description: "A prototype of Ortolan's game Sects & Stakes, in which you try to found your own sect. It looks great fun, but Ortolan hasn't quite balanced the part where your most devoted follower can split off and found an ultra-orthodox wing inside the sect. On the other hand, he nailed the feature where cats can become the main object of worship, which is a good strategy for winning.",
            stackable: false
        }
    },
    {
        form: 'special-dispensation', growth: 6, decay: 0,
        reward: {
            id: 'black-cactus-card',
            name: "Black Cactus Card",
            description: "A Black Cactus from Absolutely Profane Life: Normality, once the most expensive card in the game; collectors would pay millions of dinars for it at auction. Today it's worth nothing: the makers' greed annoyed everyone so much that they stopped playing. Ortolan kept it out of nostalgia.",
            stackable: false
        }
    },
    {
        form: 'deformity-form', growth: 4, decay: 0,
        reward: {
            id: 'probability-die',
            name: "Probability-Bending Die",
            description: "A strange die crafted by Ortolan that occasionally shows impossible numbers and seems to predict future rolls.",
            stackable: false
        }
    },
    {
        form: 'temporary-permit', growth: 3, decay: 0,
        reward: {
            id: 'hopsalot-figurine',
            name: "Collectible Maxim Hopsalot Figurine",
            description: "A collectible figurine of Maxim Hopsalot, patron of Lagerlandia. The original packaging came with a six-pack of beer, which Ortolan has apparently drunk.",
            stackable: false
        }
    },
    {
        form: 'forged-arms-permission', growth: 0, decay: 10,
        reward: {
            id: 'fate-altering-piece',
            name: "Fate-Altering Game Piece",
            description: "A special game piece crafted by Ortolan that seems to subtly influence probability and fate when carried. It glows with a faint, unsettling light.",
            stackable: false
        }
    },
];

/** A fresh copy of the gift Ortolan gives for `form` (inventory items get mutated, e.g. quantity). */
export function armsReward(form) {
    const entry = ARMS_PAPERWORK.find(p => p.form === form);
    return entry ? { ...entry.reward } : null;
}

/** The paperwork the player can still hand over (quest open + document in the pack), best first. */
export function heldArmsPaperwork(scene) {
    const quest = scene.questSystem?.getQuest('ortolan_arms');
    if (!quest || quest.isComplete) return null;
    return ARMS_PAPERWORK.find(p => scene.hasItem?.(p.form)) || null;
}

/** Day-2 hand-over: take the document, give the matching gift, close the quest. Idempotent. */
export function handOverArmsPaperwork(scene) {
    const paper = heldArmsPaperwork(scene);
    if (!paper) return false;
    scene.removeItemFromInventory(paper.form);
    scene.addItemToInventory(armsReward(paper.form));
    scene.modifyGrowthDecay?.(paper.growth, paper.decay);
    scene.questSystem.updateQuest('ortolan_arms', 'I brought Ortolan the paperwork for his extra arms. He gave me a gift as thanks.', 'completed');
    scene.questSystem.completeQuest('ortolan_arms');
    return true;
}
