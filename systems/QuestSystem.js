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
            this.notifySubscribers();
            // Emit event directly from this instance
            this.emit('questAdded', id, title);
        }
    }

    updateQuest(id, newInfo) {
        const quest = this.quests.get(id);
        if (quest) {
            quest.updates.push({
                text: newInfo,
                date: new Date()
            });
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
}

export default QuestSystem;
