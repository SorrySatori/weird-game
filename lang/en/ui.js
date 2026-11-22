/**
 * English UI strings — menus, buttons, labels, HUD, save/load
 */
export default {
    ui: {
        // Main menu
        menu: {
            title: 'Upper Morkezela:',
            subtitle: 'A Weird Game',
            startGame: 'Start Game',
            loadGame: 'Load Game',
            settings: 'Settings',
            language: 'Language',
            exitGame: 'Exit Game',
        },

        // Game menu (ESC)
        gameMenu: {
            title: 'GAME MENU',
            resume: 'Resume Game',
            save: 'Save Game',
            load: 'Load Game',
            exitToMain: 'Exit to Main Menu',
            shortcuts: 'Keyboard Shortcuts: F5 = Quick Save | F9 = Quick Load | ESC = Menu',
        },

        // Settings panel
        settings: {
            title: 'SETTINGS',
            music: 'Music',
            sounds: 'Sounds',
            fullscreen: 'Fullscreen',
            language: 'Language',
            dialogStyle: 'Dialogs',
            dialogStyles: { bubbles: 'Bubbles', cinema: 'Cinema' },
            confirm: 'Confirm',
            on: 'On',
            off: 'Off',
        },

        // Save / Load
        saveLoad: {
            emptySlot: '— empty —',
            confirmOverwrite: 'Overwrite? Click again',
            savedToSlot: 'Saved: {slot}',
            page: 'Page {n} / {total}',
            slotName: 'Save {n}',
            quicksave: 'Quicksave',
            autosave: 'Autosave',
            autosaved: 'Game autosaved',
            saveTitle: 'SAVE GAME',
            loadTitle: 'LOAD GAME',
            save: 'Save',
            noSaves: 'No save files found',
            savingGame: 'Saving game...',
            gameSaved: 'Game saved at {time}',
            saveFailed: 'Failed to save game: {error}',
            loadingQuicksave: 'Loading quicksave...',
            gameLoaded: 'Game loaded successfully',
            loadFailed: 'Failed to load game: {error}',
            noQuicksave: 'No quicksave found',
            selectSlot: 'Please select a save slot',
            saveUnavailable: 'Save system not available',
            loadUnavailable: 'Load system not available',
            gameDataLoaded: 'Game data loaded successfully',
        loadingGame: 'Loading game...',
        },

        // HUD elements
        hud: {
            spores: 'SPORES',
            quests: 'Quests',
            journal: 'JOURNAL',
            questTabActive: 'Active',
            questTabDone: 'Completed',
            map: 'MAP',
            journalButton: 'Journal',
            hintButton: 'Hint',
            mapButton: 'Map',
            activeQuests: 'ACTIVE QUESTS',
            completedQuests: 'COMPLETED QUESTS',
            progress: 'Progress:',
            questProgress: 'Progress:',
            noActiveQuests: 'You have no active quests.',
            noCompletedQuests: 'You have not completed any quests yet.',
            noJournalEntries: 'No entries in {category} yet.',
            journalCategories: { People: 'People', Places: 'Places', Events: 'Events', Lore: 'Lore', Dreams: 'Dreams', Factions: 'Factions' },   // the diary's tabs (entries store the English key)
            factionStanding: 'FACTION STANDING',
            factionRecords: 'FACTION RECORDS',
            noFactions: 'No factions discovered yet.',
            noFactionRecords: 'No faction records yet.',
        },

        // Map
        mapTitle: 'UPPER MORKEZELA',
        mapSubtitle: 'Fast Travel Map',
        mapVisited: 'Visited',
        mapUndiscovered: 'Undiscovered',
        mapYouAreHere: 'You are here',
        mapHint: 'Click a visited location to fast travel  •  Press M or ESC to close',
        travelingTo: 'Traveling to {location}...',

        // Dialog
        dialog: {
            close: 'I should go',
        },

        // In-world hints (door labels etc.)
        hints: {
            // Kloor after the first Violet/Amber Oltrac sale (scenes/VoxMarket.js): the way to Ulvarex
            kloorReflections: "Good choice. Take it for a stroll around the city, you might see things that'll surprise you.",
            returnToCity: 'Return to city',
            exitToTavern: 'Back to the bar',
            enterTavern: 'Enter Tavern',
        },

        // Inventory
        // DEMO_BUILD: an exit into a place outside the demo (utils/demo.js)
        demo: {
            closedLabel: 'Closed in the demo',
            questNotInDemo: "Can't be finished in the demo. It goes on in the full game.",
            closedLine: "A traffic cone. This way doesn't go on in the demo.",
            // the end-of-demo card (scenes/DemoEndScene.js)
            end: {
                title: 'End of the Demo',
                body: "Thank you for playing the demo! The Bishop is dead, and that's where the demo ends. "
                    + 'You will be able to dig deeper into the mysterious circumstances of her death in the full game, '
                    + 'along with more of Upper Morkezela, its people and other symbionts that would love to move into you.\n\n'
                    + 'You can stay a while longer, though, and finish anything you need to.',
                wishlist: 'Wishlist on Steam',
                continue: 'Keep exploring',
                storeOpened: 'The store page is opening in Steam.',
            },
        },

        inventory: {
            button: 'Inventory',
            panelTitle: 'INVENTORY',
            emptyItems: 'Your inventory is empty',
            use: 'USE',
            play: 'PLAY',
            stop: 'STOP',
            useItem: 'Use',
            playItem: 'Play',
            stopItem: 'Stop',
            selectHint: 'Point at an item, or click it to pick it.',
            types: { key_item: 'Key item', tool: 'Tool', drug: 'Drug', consumable: 'Consumable', recording: 'Sound recording', decoration: 'Keepsake' },
            cancel: 'Cancel',
            title: 'SPORE COLLECTION',
            empty: 'Your spore collection is empty.\nGather spores as you explore.',
            full: 'Inventory is full!',
            added: 'Added to inventory: {item}',
        },

        // Growth / Decay
        growthIncreased: 'Growth increased!',
        growthDecreased: 'Growth decreased!',
        decayIncreased: 'Decay increased!',
        decayDecreased: 'Decay decreased!',

        growthLabel: 'Growth: {value}%',
        decayLabel: 'Decay: {value}%',

        // Intro
        pressSpace: 'Press SPACE to continue',

        // Hover labels of exits / hotspots that scenes draw themselves
        hotspots: {
            ulvarexPuddle: 'A puddle with a sunset in it',   // Ulvarex's puddle on an Oltrac trip (utils/ulvarexEncounter.js)
            returnOutside: 'Return Outside',
            returnInside: 'Return Inside',
            enterScraper: 'Enter Scraper',
            backToElevator: 'Back to Elevator',
            backToMainMarket: 'Back to Main Market',
            abandonedBus: 'Abandoned Bus',
            deadBishop: 'Dead Bishop',
            captainLiris: 'Captain Liris',
            skyshipAbove: 'Looks like there is a skyship above the city...',
        },
    },
};
