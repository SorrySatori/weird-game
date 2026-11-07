/**
 * Czech UI strings – nabídky, tlačítka, štítky, HUD, ukládání/načítání
 */
export default {
    ui: {
        // Hlavní nabídka
        menu: {
            title: 'Horní Morkezela:',
            subtitle: 'A Weird Game',   // part of the title: stays English (user, 2026-10-30)
            startGame: 'Nová hra',
            loadGame: 'Načíst hru',
            settings: 'Nastavení',
            language: 'Jazyk',
            exitGame: 'Ukončit hru',
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

        // Panel nastavení
        settings: {
            title: 'NASTAVENÍ',
            music: 'Hudba',
            sounds: 'Zvuky',
            fullscreen: 'Celá obrazovka',
            language: 'Jazyk',
            on: 'Zapnuto',
            off: 'Vypnuto',
        },

        // Ukládání / Načítání
        saveLoad: {
            emptySlot: '— volné —',
            confirmOverwrite: 'Přepsat? Klikni znovu',
            savedToSlot: 'Uloženo: {slot}',
            page: 'Strana {n} / {total}',
            slotName: 'Uložení {n}',
            quicksave: 'Rychlé uložení',
            autosave: 'Automatické uložení',
            autosaved: 'Hra se automaticky uložila',
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
            questTabActive: 'Aktivní',
            questTabDone: 'Dokončené',
            map: 'MAPA',
            journalButton: 'Deník',
            hintButton: 'Nápověda',
            mapButton: 'Mapa',
            activeQuests: 'AKTIVNÍ ÚKOLY',
            completedQuests: 'DOKONČENÉ ÚKOLY',
            progress: 'Průběh:',
            questProgress: 'Průběh:',
            noActiveQuests: 'Nemáte žádné aktivní úkoly.',
            noCompletedQuests: 'Zatím jste nedokončili žádné úkoly.',
            noJournalEntries: 'Zatím žádné záznamy v kategorii {category}.',
            journalCategories: { People: 'Lidé', Places: 'Místa', Events: 'Události', Lore: 'Vědění', Dreams: 'Sny', Factions: 'Frakce' },   // the diary's tabs (entries store the English key)
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

        // Nápovědy ve světě (popisky dveří apod.)
        hints: {
            returnToCity: 'Zpět do města',
            exitToTavern: 'Zpět do hospody',
            enterTavern: 'Vstoupit do hospody',
        },

        // Inventář
        // DEMO_BUILD: an exit into a place outside the demo (utils/demo.js)
        demo: {
            closedLabel: 'V demu uzavřeno',
            questNotInDemo: 'V demu nejde dokončit – pokračuje v plné verzi hry.',
            closedLine: "Dopravní kužel. Tudy se v demu dál nedostanu.",
            // závěrečná karta dema (scenes/DemoEndScene.js)
            end: {
                title: 'Konec dema',
                body: 'Děkujeme, že jste si zahráli demo! Klíč od Elphi odemyká dvorek Škrabáku – a tam demo končí. '
                    + 'Pátrání po Biskupce pokračuje v plné hře, napříč celou Horní Morkezelou: jejími čtvrtěmi, '
                    + 'frakcemi i symbionty, kteří by se ve vás rádi zabydleli.\n\n'
                    + 'Můžete tu ale ještě chvíli zůstat – co jste nedokončili, na vás počká.',
                wishlist: 'Přidat do seznamu přání',
                continue: 'Hrát dál',
                storeOpened: 'Stránka hry se otevírá ve Steamu.',
            },
        },

        inventory: {
            button: 'Inventář',
            panelTitle: 'INVENTÁŘ',
            emptyItems: 'Váš inventář je prázdný',
            use: 'POUŽÍT',
            play: 'PŘEHRÁT',
            stop: 'STOP',
            useItem: 'Použít',
            playItem: 'Přehrát',
            stopItem: 'Zastavit',
            selectHint: 'Najeď na předmět, nebo ho kliknutím vyber.',
            types: { key_item: 'Klíčový předmět', tool: 'Nástroj', drug: 'Droga', consumable: 'Spotřební', recording: 'Zvuková nahrávka', decoration: 'Památka' },
            cancel: 'Zrušit',
            title: 'SBÍRKA SPOR',
            empty: 'Tvoje sbírka spor je prázdná.\nSbírej spory při průzkumu.',
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

        // Popisky východů a míst, které si scény kreslí samy
        hotspots: {
            returnOutside: 'Ven',
            returnInside: 'Zpět dovnitř',
            enterScraper: 'Do Škrabáku',
            backToElevator: 'Zpět k výtahu',
            backToMainMarket: 'Zpět na tržnici',
            abandonedBus: 'Opuštěný autobus',
            captainLiris: 'Kapitánka Liris',
            skyshipAbove: 'Vypadá to, že nad městem visí vzducholoď...',
        },
    },
};
