class QuestSystem extends Phaser.Events.EventEmitter {
    constructor() {
        super();
        if (QuestSystem.instance) {
            return QuestSystem.instance;
        }
        QuestSystem.instance = this;
        
        this.quests = new Map();
        this.subscribers = new Set();
        this.scene = null;
        
        // Initialize event emitter
        if (!this.events) {
            this.events = new Phaser.Events.EventEmitter();
        }
    }

    static getInstance() {
        if (!QuestSystem.instance) {
            QuestSystem.instance = new QuestSystem();
        }
        return QuestSystem.instance;
    }

    subscribe(callback) {
        this.subscribers.add(callback);
    }

    unsubscribe(callback) {
        this.subscribers.delete(callback);
    }

    notifySubscribers() {
        this.subscribers.forEach(callback => callback());
    }

    setScene(scene) {
        this.scene = scene;
    }

    addQuest(id, title, description) {
        if (!this.quests.has(id)) {
            this.quests.set(id, {
                id,
                title,
                description,
                updates: [],
                isComplete: false,
                dateStarted: new Date()
            });
            this.syncRegistryQuests();
            this.notifySubscribers();
            // Emit event directly from this instance
            this.emit('questAdded', id, title);
        }
    }

    updateQuest(id, newInfo, key = null) {
        const quest = this.quests.get(id);
        if (quest) {
            // Skip duplicate updates — if a key is provided and already exists, do nothing
            if (key && quest.updates.some(u => u.key === key)) {
                return;
            }
            quest.updates.push({
                text: newInfo,
                key: key, 
                date: new Date()
            });
            this.syncRegistryQuests();
            this.notifySubscribers();
            // Emit event directly from this instance
            this.emit('questUpdated', id, quest.title);
        }
    }

    completeQuest(id) {
        const quest = this.quests.get(id);
        if (quest) {
            quest.isComplete = true;
            quest.dateCompleted = new Date();
            this.syncRegistryQuests();
            this.notifySubscribers();
            // Emit event directly from this instance
            this.emit('questCompleted', id, quest.title);
        }
    }

    getQuest(id) {
        return this.quests.get(id);
    }

    getAllQuests() {
        return Array.from(this.quests.values());
    }
    
    /**
     * Get serializable data for saving
     * @returns {Object} Data that can be serialized to JSON
     */
    getSerializableData() {
        // Convert Map to array of entries for serialization
        return {
            quests: Array.from(this.quests.entries())
        };
    }

    syncRegistryQuests() {
        if (this.scene?.registry?.has('savedQuests')) {
            this.scene.registry.set('savedQuests', this.getSerializableData());
        }
    }
    
    /**
     * Load data from a save file
     * @param {Object} data - Data from save file
     */
    loadFromData(data) {
        if (data && data.quests) {
            // Clear existing quests
            this.quests.clear();
            
            // Track seen IDs to skip duplicate quests in save data
            const seen = new Set();
            
            // Restore quests from data
            data.quests.forEach(([id, quest]) => {
                // Skip duplicate quest entries — keep only the first occurrence
                if (seen.has(id)) return;
                seen.add(id);
                
                // Convert date strings back to Date objects
                if (quest.dateStarted) {
                    quest.dateStarted = new Date(quest.dateStarted);
                }
                if (quest.dateCompleted) {
                    quest.dateCompleted = new Date(quest.dateCompleted);
                }
                
                // Deduplicate updates by key
                if (quest.updates) {
                    const seenKeys = new Set();
                    quest.updates = quest.updates.filter(update => {
                        if (update.date) {
                            update.date = new Date(update.date);
                        }
                        if (update.key) {
                            if (seenKeys.has(update.key)) return false;
                            seenKeys.add(update.key);
                        }
                        return true;
                    });
                }
                
                this.quests.set(id, quest);
            });
            
            this.notifySubscribers();
        }
    }
}

export default QuestSystem;
