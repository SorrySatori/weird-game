class GrowthDecaySystem extends Phaser.Events.EventEmitter {
    constructor() {
        super();
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
    modifyBalance(growthChange, decayChange) {
        let totalChange = 0;
        
        if (growthChange) {
            // Update growth and ensure it stays within bounds
            const oldGrowth = this.growth;
            this.growth = Math.max(0, Math.min(100, this.growth + growthChange));
            totalChange = this.growth - oldGrowth;
            
            // Decay is inverse of growth
            this.decay = 100 - this.growth;
            
            // Emit event for growth change
            this.emit('growthChanged', totalChange);
        }
        
        if (decayChange) {
            // Decay change affects growth inversely
            const oldDecay = this.decay;
            this.decay = Math.max(0, Math.min(100, this.decay + decayChange));
            const decayDelta = this.decay - oldDecay;
            
            // Growth is inverse of decay
            this.growth = 100 - this.decay;
            
            // Emit event for decay change
            this.emit('decayChanged', decayDelta);
        }
        
        // Notify all subscribers (UI elements) of the change
        this.notifySubscribers();
        
        return totalChange;
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
    
    // Set specific values (used when loading saved games)
    setGrowth(value) {
        this.growth = Math.max(0, Math.min(100, value));
        this.decay = 100 - this.growth;
        this.notifySubscribers();
    }
    
    setDecay(value) {
        this.decay = Math.max(0, Math.min(100, value));
        this.growth = 100 - this.decay;
        this.notifySubscribers();
    }
    
    /**
     * Get serializable data for saving
     * @returns {Object} Object containing growth and decay values
     */
    getSerializableData() {
        return {
            growth: this.growth,
            decay: this.decay
        };
    }
    
    /**
     * Load system state from saved data
     * @param {Object} data - Object containing growth and decay values
     */
    loadFromData(data) {
        console.log('Loading GrowthDecaySystem from data:', data);
        if (data && typeof data === 'object') {
            if (typeof data.growth === 'number') {
                this.setGrowth(data.growth);
            }
            if (typeof data.decay === 'number') {
                this.setDecay(data.decay);
            }
        }
    }
}

export default GrowthDecaySystem;
