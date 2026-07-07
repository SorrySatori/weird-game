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
            language: 'Language',
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

        // Save / Load
        saveLoad: {
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
            map: 'MAP',
            activeQuests: 'ACTIVE QUESTS',
            completedQuests: 'COMPLETED QUESTS',
            progress: 'Progress:',
            questProgress: 'Progress:',
            noActiveQuests: 'You have no active quests.',
            noCompletedQuests: 'You have not completed any quests yet.',
            noJournalEntries: 'No entries in {category} yet.',
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

        // Inventory
        inventory: {
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
    },
};
