class GrowthDecaySystem {
    constructor() {
        if (GrowthDecaySystem.instance) {
            return GrowthDecaySystem.instance;
        }
        GrowthDecaySystem.instance = this;
        
        this.growth = 50; // Starting at balance
        this.decay = 50;
        this.subscribers = new Set(); // For UI updates
    }

    static getInstance() {
        if (!GrowthDecaySystem.instance) {
            GrowthDecaySystem.instance = new GrowthDecaySystem();
        }
        return GrowthDecaySystem.instance;
    }

    // Update both values ensuring they stay in balance
    updateBalance(growthChange) {
        // Ensure total always equals 100
        this.growth = Math.max(0, Math.min(100, this.growth + growthChange));
        this.decay = 100 - this.growth;
        
        // Notify all subscribers (UI elements) of the change
        this.notifySubscribers();
    }

    // Subscribe UI elements for updates
    subscribe(callback) {
        this.subscribers.add(callback);
    }

    unsubscribe(callback) {
        this.subscribers.delete(callback);
    }

    notifySubscribers() {
        this.subscribers.forEach(callback => {
            callback(this.growth, this.decay);
        });
    }

    // Get current values
    getGrowth() {
        return this.growth;
    }

    getDecay() {
        return this.decay;
    }
}

export default GrowthDecaySystem;
