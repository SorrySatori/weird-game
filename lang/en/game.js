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
    },

    factions: {
        RustChoir: 'Rust Choir',
        PithReclaimers: 'Pith Reclaimers',
        LumenDirectorate: 'Lumen Directorate',
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
