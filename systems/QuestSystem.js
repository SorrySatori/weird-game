class QuestSystem {
    constructor() {
        if (QuestSystem.instance) {
            return QuestSystem.instance;
        }
        QuestSystem.instance = this;
        
        this.quests = new Map();
        this.subscribers = new Set();
        this.scene = null;
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

    showNotification() {
        if (this.scene) {
            this.scene.showNotification('Quest Log Updated', 0x7fff8e);
        }
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
            this.showNotification();
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
            this.showNotification();
        }
    }

    completeQuest(id) {
        const quest = this.quests.get(id);
        if (quest) {
            quest.isComplete = true;
            quest.dateCompleted = new Date();
            this.notifySubscribers();
            this.showNotification();
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
