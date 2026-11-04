/**
 * Ortolan's "extra arms" paperwork (quest `ortolan_arms`): which documents he accepts and what he gives
 * back for each. The player hands them over in ShedCourtyardScene (a reaction per form).
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
            id: 'legged-shark-statuette',
            name: "Legged Shark Statuette",
            description: "A statuette of a shark with legs, almost finless. Ortolan no longer remembers exactly where he got it, but he says it's from some board game about vampires and demons.",
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
            id: 'apocalypse-cop-figure',
            name: "Apocalypse Cop Figure",
            description: "A figure of Apocalypse Cop, a detective holding a Tequila Sunrise. Ortolan is especially fond of him: he reminds him of the time after the fall of the Ludarchs, when he sank into drink. He's from a game Ortolan didn't make, someone else did. Ortolan has a feeling you'll need him more than he does.",
            stackable: false
        }
    },
];

/** A fresh copy of the gift Ortolan gives for `form` (inventory items get mutated, e.g. quantity). */
export function armsReward(form) {
    const entry = ARMS_PAPERWORK.find(p => p.form === form);
    return entry ? { ...entry.reward } : null;
}
