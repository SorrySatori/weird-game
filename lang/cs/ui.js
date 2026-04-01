/**
 * Czech UI strings — nabídky, tlačítka, štítky, HUD, ukládání/načítání
 */
export default {
    ui: {
        // Hlavní nabídka
        menu: {
            title: 'Horní Morkezela:',
            subtitle: 'Podivná Hra',
            startGame: 'Nová hra',
            loadGame: 'Načíst hru',
            language: 'Jazyk',
        },

        // Herní nabídka (ESC)
        gameMenu: {
            title: 'HERNÍ NABÍDKA',
            resume: 'Pokračovat ve hře',
            save: 'Uložit hru',
            load: 'Načíst hru',
            exitToMain: 'Zpět do hlavní nabídky',
            shortcuts: 'Klávesové zkratky: F5 = Rychlé uložení | F9 = Rychlé načtení | ESC = Nabídka',
        },

        // Ukládání / Načítání
        saveLoad: {
            saveTitle: 'ULOŽIT HRU',
            loadTitle: 'NAČÍST HRU',
            save: 'Uložit',
            noSaves: 'Žádné uložené hry nenalezeny',
            savingGame: 'Ukládám hru...',
            gameSaved: 'Hra uložena v {time}',
            saveFailed: 'Nepodařilo se uložit hru: {error}',
            loadingQuicksave: 'Načítám rychlé uložení...',
            gameLoaded: 'Hra úspěšně načtena',
            loadFailed: 'Nepodařilo se načíst hru: {error}',
            noQuicksave: 'Žádné rychlé uložení nenalezeno',
            selectSlot: 'Vyberte slot pro uložení',
            saveUnavailable: 'Systém ukládání není dostupný',
            loadUnavailable: 'Systém načítání není dostupný',
            gameDataLoaded: 'Herní data úspěšně načtena',
            loadingGame: 'Načítám hru...',
        },

        // Prvky HUD
        hud: {
            spores: 'SPORY',
            quests: 'Úkoly',
            journal: 'DENÍK',
            map: 'MAPA',
            activeQuests: 'AKTIVNÍ ÚKOLY',
            completedQuests: 'DOKONČENÉ ÚKOLY',
            progress: 'Průběh:',
            questProgress: 'Průběh:',
            noActiveQuests: 'Nemáte žádné aktivní úkoly.',
            noCompletedQuests: 'Zatím jste nedokončili žádné úkoly.',
            noJournalEntries: 'Zatím žádné záznamy v kategorii {category}.',
            factionStanding: 'POSTAVENÍ FRAKCÍ',
            factionRecords: 'ZÁZNAMY FRAKCÍ',
            noFactions: 'Zatím nebyly objeveny žádné frakce.',
            noFactionRecords: 'Zatím žádné záznamy o frakcích.',
        },

        // Mapa
        mapTitle: 'HORNÍ MORKEZELA',
        mapSubtitle: 'Mapa rychlého cestování',
        mapVisited: 'Navštíveno',
        mapUndiscovered: 'Neobjeveno',
        mapYouAreHere: 'Jste zde',
        mapHint: 'Klikněte na navštívené místo pro rychlé cestování  •  Stiskněte M nebo ESC pro zavření',
        travelingTo: 'Cestujete do {location}...',

        // Dialog
        dialog: {
            close: 'Měl bych jít',
        },

        // Inventář
        inventory: {
            title: 'SBÍRKA SPOR',
            empty: 'Vaše sbírka spor je prázdná.\nSbírejte spory při průzkumu.',
            full: 'Inventář je plný!',
            added: 'Přidáno do inventáře: {item}',
        },

        // Růst / Rozklad
        growthIncreased: 'Růst vzrostl!',
        growthDecreased: 'Růst klesl!',
        decayIncreased: 'Rozklad vzrostl!',
        decayDecreased: 'Rozklad klesl!',

        growthLabel: 'Růst: {value}%',
        decayLabel: 'Rozklad: {value}%',

        // Intro
        pressSpace: 'Stiskněte MEZERNÍK pro pokračování',
    },
};
