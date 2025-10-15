/**
 * SaveSystem.js - Handles saving and loading game state
 */
export default class SaveSystem {
    constructor(scene) {
        this.scene = scene;
        this.saveSlot = 'save1';
        this.lastSaveTime = null;
    }

    /**
     * Collect all game state data that needs to be saved
     * @returns {Object} Complete game state data
     */
    collectSaveData() {
        const game = this.scene.game;
        const registry = game.registry;
        const saveData = {
            version: '1.0.0',
            timestamp: new Date().toISOString(),
            currentScene: this.scene.scene.key,
            player: {
                position: null, // Will be filled if player exists
                scene: this.scene.scene.key
            },
            registry: {},
            usedDialogOptions: Array.from(this.scene.usedDialogOptions || new Map())
        };

        // Save player position if available
        if (this.scene.player) {
            saveData.player.position = {
                x: this.scene.player.x,
                y: this.scene.player.y
            };
        }

        // Save inventory data if available
        if (this.scene.inventorySystem) {
            saveData.inventory = this.scene.inventorySystem.getInventoryData();
        } else {
            saveData.inventory = registry.get('inventory') || { items: [], maxItems: 12 };
        }

        // Save growth/decay data
        const growthDecaySystem = registry.get('growthDecaySystem');
        if (growthDecaySystem && growthDecaySystem.getSerializableData) {
            saveData.growthDecay = growthDecaySystem.getSerializableData();
        } else {
            saveData.growthDecay = registry.get('growthDecayBalance') || { growth: 50, decay: 50 };
        }

        // Save quest data if available
        if (registry.get('questSystem')) {
            const questSystem = registry.get('questSystem');
            saveData.quests = questSystem.getSerializableData();
        }

        // Save journal data if available
        if (this.scene.journalSystem) {
            saveData.journal = this.scene.journalSystem.getSerializableData();
        }

        // Save symbiont data if available
        if (registry.get('symbiontSystem')) {
            const symbiontSystem = registry.get('symbiontSystem');
            saveData.symbionts = symbiontSystem.getSerializableData();
        }

        // Save faction data if available
        if (registry.get('factionSystem')) {
            const factionSystem = registry.get('factionSystem');
            saveData.factions = factionSystem.getReputations();
        }

        // Save effects if available
        if (this.scene.effectsSystem) {
            saveData.effects = this.scene.effectsSystem.getActiveEffects();
        }

        // Save spore data if available
        if (registry.get('sporeSystem')) {
            const sporeSystem = registry.get('sporeSystem');
            saveData.spores = {
                currentSpores: sporeSystem.currentSpores,
                maxSpores: sporeSystem.maxSpores
            };
        }

        // Save money data if available
        if (this.scene.moneySystem) {
            saveData.money = {
                amount: this.scene.moneySystem.get(),
                currencyName: this.scene.moneySystem.getCurrencyName()
            };
        }

        return saveData;
    }

    /**
     * Save the current game state
     * @param {string} slotName - Name of the save slot
     * @returns {Promise} Result of the save operation
     */
    async saveGame(slotName = null) {
        if (slotName) {
            this.saveSlot = slotName;
        }
        
        const saveData = this.collectSaveData();
        
        try {
            // Use the game API to save the game
            const result = window.gameAPI ? window.gameAPI.saveGame(saveData, this.saveSlot) : { success: false, error: 'Game API not available' };
            
            if (result.success) {
                this.lastSaveTime = new Date();
                console.log(`Game saved successfully to ${result.path}`);
                return { success: true, message: 'Game saved successfully' };
            } else {
                console.error('Failed to save game:', result.error);
                return { success: false, message: `Failed to save game: ${result.error}` };
            }
        } catch (error) {
            console.error('Error saving game:', error);
            return { success: false, message: `Error saving game: ${error.message}` };
        }
    }

    /**
     * Load a saved game
     * @param {string} slotName - Name of the save slot
     * @returns {Promise} Result of the load operation
     */
    async loadGame(slotName = null) {
        if (slotName) {
            this.saveSlot = slotName;
        }
        
        try {
            // Use the game API to load the game
            const result = window.gameAPI ? window.gameAPI.loadGame(this.saveSlot) : { success: false, error: 'Game API not available' };
            
            if (result.success) {
                const saveData = result.data;
                await this.applyLoadedData(saveData);
                return { success: true, message: 'Game loaded successfully' };
            } else {
                console.error('Failed to load game:', result.error);
                return { success: false, message: `Failed to load game: ${result.error}` };
            }
        } catch (error) {
            console.error('Error loading game:', error);
            return { success: false, message: `Error loading game: ${error.message}` };
        }
    }

    /**
     * Apply loaded save data to the game
     * @param {Object} saveData - The loaded save data
     * @returns {Promise} Resolves when data is applied
     */
    async applyLoadedData(saveData) {
        const game = this.scene.game;
        const registry = game.registry;
        
        console.log('Applying loaded save data:', saveData);

        // Restore inventory
        if (saveData.inventory) {
            console.log('Restoring inventory:', saveData.inventory);
            registry.set('inventory', saveData.inventory);
            
            if (this.scene.inventorySystem) {
                this.scene.inventorySystem.loadInventoryData(saveData.inventory);
            }
        }

        // Restore growth/decay balance
        if (saveData.growthDecay) {
            console.log('Restoring growth/decay:', saveData.growthDecay);
            registry.set('growthDecayBalance', saveData.growthDecay);
            
            if (this.scene.growthDecaySystem) {
                this.scene.growthDecaySystem.loadFromData(saveData.growthDecay);
            } else if (registry.get('growthDecaySystem')) {
                registry.get('growthDecaySystem').loadFromData(saveData.growthDecay);
            }
        }

        // Restore quest data
        if (saveData.quests) {
            console.log('Restoring quests:', saveData.quests);
            // Store in registry for access by other scenes
            registry.set('savedQuests', saveData.quests);
            
            // Apply to current scene if available
            if (this.scene.questSystem) {
                this.scene.questSystem.loadFromData(saveData.quests);
            } else if (registry.get('questSystem')) {
                registry.get('questSystem').loadFromData(saveData.quests);
            }
        }

        // Restore journal data
        if (saveData.journal) {
            console.log('Restoring journal:', saveData.journal);
            // Store in registry for access by other scenes
            registry.set('savedJournal', saveData.journal);
            
            // Apply to current scene if available
            if (this.scene.journalSystem) {
                this.scene.journalSystem.loadFromData(saveData.journal);
            }
        }

        // Restore symbiont data
        if (saveData.symbionts) {
            console.log('Restoring symbionts:', saveData.symbionts);
            // Store in registry for access by other scenes
            registry.set('savedSymbionts', saveData.symbionts);
            
            // Apply to current scene if available
            if (this.scene.symbiontSystem) {
                this.scene.symbiontSystem.loadFromData(saveData.symbionts);
                
                // Rebuild symbiont UI
                if (this.scene.createSymbiontUI) {
                    this.scene.createSymbiontUI();
                }
            } else if (registry.get('symbiontSystem')) {
                registry.get('symbiontSystem').loadFromData(saveData.symbionts);
            }
        }

        // Restore faction data
        if (saveData.factions) {
            console.log('Restoring factions:', saveData.factions);
            // Store in registry for access by other scenes
            registry.set('savedFactions', saveData.factions);
            
            // Apply to current scene if available
            if (this.scene.factionSystem) {
                this.scene.factionSystem.setReputations(saveData.factions);
            } else if (registry.get('factionSystem')) {
                registry.get('factionSystem').setReputations(saveData.factions);
            }
        }

        // Restore effects
        if (saveData.effects) {
            console.log('Restoring effects:', saveData.effects);
            // Store in registry for access by other scenes
            registry.set('savedEffects', saveData.effects);
            
            // Apply to current scene if available
            if (this.scene.effectsSystem) {
                this.scene.effectsSystem.loadEffects(saveData.effects);
            }
        }

        // Restore spore data
        if (saveData.spores) {
            console.log('Restoring spores:', saveData.spores);
            // Store in registry for access by other scenes
            registry.set('savedSpores', saveData.spores);
            
            // Apply to current scene if available
            if (registry.get('sporeSystem')) {
                const sporeSystem = registry.get('sporeSystem');
                sporeSystem.setSporeLevel(saveData.spores.currentSpores);
                sporeSystem.setMaxSpores(saveData.spores.maxSpores);
                
                // Update spore bar if it exists
                if (this.scene.sporeBar) {
                    this.scene.sporeBar.updateDisplay(
                        saveData.spores.currentSpores,
                        saveData.spores.maxSpores
                    );
                }
            }
        }

        // Restore money data
        if (saveData.money) {
            console.log('Restoring money:', saveData.money);
            // Store in registry for access by other scenes
            registry.set('savedMoney', saveData.money);
            
            // Apply to current scene if available
            if (this.scene.moneySystem) {
                this.scene.moneySystem.setAmount(saveData.money.amount);
            }
        }

        // Restore used dialog options
        if (saveData.usedDialogOptions) {
            console.log('Restoring dialog options');
            this.scene.usedDialogOptions = new Map(saveData.usedDialogOptions);
            registry.set('usedDialogOptions', this.scene.usedDialogOptions);
        }

        // Show notification about loaded game
        if (this.scene.showNotification) {
            this.scene.showNotification('Game loaded successfully', 0x00ff00);
        }

        // Switch to the saved scene if different from current
        if (saveData.currentScene && saveData.currentScene !== this.scene.scene.key) {
            console.log(`Switching to scene: ${saveData.currentScene}`);
            this.scene.scene.start(saveData.currentScene, { 
                loadedPosition: saveData.player.position,
                loadedSave: true // Flag to indicate this is a loaded save
            });
        } else if (saveData.player.position && this.scene.player) {
            // Just update player position in current scene
            console.log('Updating player position in current scene');
            this.scene.player.setPosition(
                saveData.player.position.x,
                saveData.player.position.y
            );
        }
    }

    /**
     * List all available save files
     * @returns {Array} List of save files with metadata
     */
    listSaveFiles() {
        try {
            const result = window.gameAPI ? window.gameAPI.listSaveFiles() : { success: false, error: 'Game API not available' };
            if (result.success) {
                return result.files;
            } else {
                console.error('Failed to list save files:', result.error);
                return [];
            }
        } catch (error) {
            console.error('Error listing save files:', error);
            return [];
        }
    }

    /**
     * Delete a save file
     * @param {string} slotName - Name of the save slot to delete
     * @returns {Object} Result of the delete operation
     */
    deleteSaveFile(slotName) {
        try {
            const result = window.gameAPI ? window.gameAPI.deleteSaveFile(slotName) : { success: false, error: 'Game API not available' };
            return result;
        } catch (error) {
            console.error('Error deleting save file:', error);
            return { success: false, error: error.message };
        }
    }
}
