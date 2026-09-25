/**
 * English game strings — notifications, quest descriptions, journal categories
 */
export default {
    cutscene: {
        stomach_clock: {
            title: 'The Stomach Clock turns over',
            caption: "At the townhall, the Stomach Clock finishes another digestion and, with a wet chime, begins the next.",
        },
    },
    shop: {
        balance: 'Dinar: {amount}',
        price: 'Price: {price} dinar',
        buy: 'Buy',
        sell: 'Sell',
        forSale: 'Items for Sale',
        yourItems: 'Your Items',
        noDescription: 'No description available.',
        names: {
            zerren: "Zerren's Curios",
            kloor: "Kloor's Oltrac Emporium",
            cork: 'Screaming Cork Shop',
        },
        items: {
            trinket_box: { name: 'Ornate Trinket Box', description: 'A small decorative box with intricate fungal patterns.' },
            crystal_vial: { name: 'Luminescent Crystal Vial', description: 'A vial containing glowing crystal fragments. Makes for pleasant ambient lighting.' },
            market_map: { name: 'Voxmarket Map', description: 'A detailed map of Voxmarket and surrounding areas.' },
            forgotten_elevator_button: { name: 'Forgotten Elevator Button', description: "An old elevator button with strange markings. It seems to be for a floor that doesn't officially exist." },
            grayOltrac: { name: 'Gray Oltrac', description: 'A common variant of Oltrac. Provides mild hallucinogenic effects.' },
            violetOltrac: { name: 'Violet Oltrac', description: 'A medium-strength variant of Oltrac. Enhances perception and provides vivid visions.' },
            amberOltrac: { name: 'Amber Oltrac', description: 'The rarest and most potent form of Oltrac. Said to allow glimpses beyond the veil of reality.' },
            pliers: { name: 'Pliers', description: 'A pair of pliers. Useful for repairing or extracting.' },
        },
    },
    notifications: {
        newQuest: 'New quest',
        questUpdated: 'Quest updated',
        questCompleted: 'Quest completed!',
        journalUpdated: 'Journal updated',
        reputationChange: '{faction} Reputation: {sign}{change}',
        moneyGain: '+{amount} dinar',
        moneyLoss: '-{amount} dinar',
        purchased: 'Purchased: {item}',
        sold: 'Sold: {item}',
        notEnoughMoney: 'Not enough dinar!',
        newItemAvailable: 'New item available: {item}',
        failedToSell: 'Failed to sell item',
        addedToInventory: 'Added to inventory: {item}',
        inventoryFull: 'Inventory is full!',
        sporeChange: '{sign}{amount} Spores',
        nemeSilenced: 'The rot rises — Neme falls silent.',
        nemeRecovered: 'The air clears — Neme can read again.',
        osswineSilenced: 'Too much life here — Osswine goes still.',
        osswineRecovered: 'The bloom recedes — the dead grow audible to Osswine.',
        growthIncreased: 'Growth increased!',
        growthDecreased: 'Growth decreased!',
        decayIncreased: 'Decay increased!',
        decayDecreased: 'Decay decreased!',
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
