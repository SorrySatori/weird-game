class SporeSystem extends Phaser.Events.EventEmitter {
    constructor() {
        super();
        if (SporeSystem.instance) {
            return SporeSystem.instance;
        }
        SporeSystem.instance = this;
        
        this.sporeLevel = 100;
        this.subscribers = new Set(); // For UI updates
    }

    static getInstance() {
        if (!SporeSystem.instance) {
            SporeSystem.instance = new SporeSystem();
        }
        return SporeSystem.instance;
    }

    // Update both values ensuring they stay in balance
    modifySpores(amount) {
        let totalChange = 0;
        
        if (amount) {
            // Update growth and ensure it stays within bounds
            const oldSporeLevel = this.sporeLevel;
            this.sporeLevel = Math.max(0, Math.min(100, this.sporeLevel + amount));
            totalChange = this.sporeLevel - oldSporeLevel;
            
            // Emit event for growth change
            this.emit('sporeChanged', totalChange);
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
        for (let callback of Array.from(this.subscribers)) {
            try {
                callback(this.sporeLevel);
            } catch (e) {
                console.warn('[SporeSystem] Removing dead subscriber:', callback, e);
                this.subscribers.delete(callback);
            }
        }
        console.log('[SporeSystem] Subscribers after notify:', Array.from(this.subscribers));
    }

    // Get current values
    getSporeLevel() {
        return this.sporeLevel;
    }
        // Clean up resources
        cleanup() {
            this.subscribers = [];
        }
}

export default SporeSystem;
