/**
 * English game strings — notifications, quest descriptions, journal categories
 */
export default {
    notifications: {
        newQuest: 'New quest',
        questUpdated: 'Quest updated',
        questCompleted: 'Quest completed!',
        journalUpdated: 'Journal updated',
        reputationChange: '{faction} Reputation: {sign}{change}',
        goldGain: '+{amount} gold',
        goldLoss: '-{amount} gold',
        purchased: 'Purchased: {item}',
        sold: 'Sold: {item}',
        notEnoughGold: 'Not enough gold!',
        failedToSell: 'Failed to sell item',
        addedToInventory: 'Added to inventory: {item}',
        inventoryFull: 'Inventory is full!',
        sporeChange: '{sign}{amount} Spores',
        nemeSilenced: 'The rot rises — Neme falls silent.',
        nemeRecovered: 'The air clears — Neme can read again.',
        osswineSilenced: 'Too much life here — Osswine goes still.',
        osswineRecovered: 'The bloom recedes — the dead grow audible to Osswine.',
    },

    factions: {
        RustChoir: 'Rust Choir',
        PithReclaimers: 'Pith Reclaimers',
        LumenDirectorate: 'Lumen Directorate',
    },

    mood: {
        verrik: {
            growthDominant: "The tendrils lean toward you before you've even spoken. Good — green things know their own.",
            decayDominant: "Stand back from the beds a moment. Something in your spores makes the young shoots curl away.",
        },
        angle_corrector: {
            growthDominant: "Your cadence has resolved toward growth. Cleaner. The measurement is a pleasure to take.",
            decayDominant: "Hold still. Your reading skews toward collapse — a fault I would rather not stand this close to.",
        },
        liris: {
            growthDominant: "You come aboard smelling of green weather. The deck ferns fair lean into you. Welcome.",
            decayDominant: "Something rides up with you — a rot on the wind. Keep it downwind of my rigging, if you please.",
        },
        gnur: {
            growthDominant: "Too much bloom on you, priest. Puts my wares off. Green don't sell down here.",
            decayDominant: "Heh. You've got the good rot in you now, outsider. We'll get along fine.",
        },
        brukk: {
            growthDominant: "You reek of sap and spring. The machines don't trust growing things. Nor do I.",
            decayDominant: "The corrosion in you sings, brother. The Choir hears its own.",
        },
        ravla: {
            growthDominant: "All that bloom on you makes me nervous. Growing things want, and want gets expensive.",
            decayDominant: "You wear decay well. Makes you easier to deal with — the greedy always are.",
        },
        kloor: {
            growthDominant: "My scales twitch — your spores are ripe, swollen with life. Prime stock, that.",
            decayDominant: "The counter smells you before you speak — rot, and plenty of it. Cheap goods.",
        },
        townsquare_citizen: {
            growthDominant: "The little cities in me hum — you carry a great deal of growing. Very... citizen-like. Very alive.",
            decayDominant: "My cities flinch. Something in you is coming apart. As a real citizen, I find this... normal. Totally normal.",
        },
    },

    journal: {
        categories: {
            EVENTS: 'EVENTS',
            PEOPLE: 'PEOPLE',
            PLACES: 'PLACES',
            LORE: 'LORE',
            DREAMS: 'DREAMS',
            FACTIONS: 'FACTIONS',
            CLUES: 'CLUES',
        },
    },

    sporeBar: {
        label: 'SPORES',
        tooltipTitle: 'Spore Energy',
        tooltipDesc: 'Used for fungal abilities and rituals.',
        tooltipCurrent: 'Current: {current}/{max}',
    },
};
