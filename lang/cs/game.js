/**
 * Czech game strings — oznámení, popisy úkolů, kategorie deníku
 */
export default {
    notifications: {
        newQuest: 'Nový úkol',
        questUpdated: 'Úkol aktualizován',
        questCompleted: 'Úkol dokončen!',
        journalUpdated: 'Deník aktualizován',
        reputationChange: '{faction} Reputace: {sign}{change}',
        goldGain: '+{amount} zlatých',
        goldLoss: '-{amount} zlatých',
        purchased: 'Zakoupeno: {item}',
        sold: 'Prodáno: {item}',
        notEnoughGold: 'Nedostatek zlata!',
        failedToSell: 'Nepodařilo se prodat předmět',
        addedToInventory: 'Přidáno do inventáře: {item}',
        inventoryFull: 'Inventář je plný!',
        sporeChange: '{sign}{amount} Spor',
    },

    factions: {
        RustChoir: 'Chór Rzi',
        PithReclaimers: 'Dřeňoví Reklamátoři',
        LumenDirectorate: 'Lumen Direktorát',
    },

    journal: {
        categories: {
            EVENTS: 'UDÁLOSTI',
            PEOPLE: 'POSTAVY',
            PLACES: 'MÍSTA',
            LORE: 'HISTORIE',
            DREAMS: 'SNY',
            FACTIONS: 'FRAKCE',
            CLUES: 'STOPY',
        },
    },

    sporeBar: {
        label: 'SPORY',
        tooltipTitle: 'Sporová Energie',
        tooltipDesc: 'Používá se pro houbové schopnosti a rituály.',
        tooltipCurrent: 'Aktuálně: {current}/{max}',
    },
};
