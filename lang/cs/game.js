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
        nemeSilenced: 'Hniloba sílí — Neme utichá.',
        nemeRecovered: 'Vzduch se čistí — Neme opět čte.',
        osswineSilenced: 'Zde je příliš mnoho života — Osswine strne.',
        osswineRecovered: 'Květ ustupuje — mrtví jsou pro Osswine opět slyšitelní.',
    },

    factions: {
        RustChoir: 'Chór Rzi',
        PithReclaimers: 'Dřeňoví Reklamátoři',
        LumenDirectorate: 'Lumen Direktorát',
    },

    mood: {
        verrik: {
            growthDominant: "Úponky se k tobě naklánějí dřív, než promluvíš. Dobře — zelené věci poznají svoje.",
            decayDominant: "Ustup na chvíli od záhonů. Něco v tvých sporách nutí mladé výhonky se schoulit.",
        },
        angle_corrector: {
            growthDominant: "Tvá kadence se ustálila k růstu. Čistší. Je potěšením ji měřit.",
            decayDominant: "Stůj klidně. Tvé měření se chýlí ke kolapsu — vada, u níž bych nerad stál tak blízko.",
        },
        liris: {
            growthDominant: "Vstupuješ na palubu a voníš po zeleném počasí. Palubní kapradí se k tobě naklání. Vítej.",
            decayDominant: "Něco s tebou stoupá nahoru — hniloba ve větru. Drž to po větru dál od mého lanoví, buď tak laskav.",
        },
        gnur: {
            growthDominant: "Moc květu na tobě, knězi. Kazí mi to zboží. Zelené se tady dole neprodává.",
            decayDominant: "Heh. Teď v sobě máš tu správnou hnilobu, cizinče. Vyjdeme spolu dobře.",
        },
        brukk: {
            growthDominant: "Páchneš mízou a jarem. Stroje nevěří rostoucím věcem. Ani já ne.",
            decayDominant: "Koroze v tobě zpívá, bratře. Chór slyší svoje.",
        },
        ravla: {
            growthDominant: "Všechen ten květ na tobě mě znervózňuje. Rostoucí věci chtějí, a chtění je drahé.",
            decayDominant: "Rozklad ti sluší. Snáz se s tebou jedná — hrabiví to mají vždycky.",
        },
        kloor: {
            growthDominant: "Váhy sebou cukají — tvé spory jsou zralé, nabité životem. Prvotřídní zboží.",
            decayDominant: "Pult tě ucítí dřív, než promluvíš — hniloba, a spousta jí. Laciné zboží.",
        },
        townsquare_citizen: {
            growthDominant: "Ta městečka ve mně hučí — neseš v sobě spoustu růstu. Velmi... občanské. Velmi živé.",
            decayDominant: "Má městečka sebou trhnou. Něco v tobě se rozpadá. Jakožto skutečný občan to shledávám... normálním. Naprosto normálním.",
        },
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
