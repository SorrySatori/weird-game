class SporeSystem extends Phaser.Events.EventEmitter {
    constructor(scene) {
        super();
        if (SporeSystem.instance) {
            return SporeSystem.instance;
        }
        SporeSystem.instance = this;
        
        this.scene = scene; // Store reference to the scene
        this.sporeLevel = 100;
        this.subscribers = new Set(); // For UI updates
    }

    static getInstance(scene) {
        if (!SporeSystem.instance) {
            SporeSystem.instance = new SporeSystem(scene);
        } else if (scene && !SporeSystem.instance.scene) {
            // Update the scene reference if it wasn't set before
            SporeSystem.instance.scene = scene;
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
            
            // Check for symbiont reaction to spore change
            if (totalChange !== 0) {
                console.log('[SporeSystem] Spore level changed:', oldSporeLevel, '->', this.sporeLevel);
                
                // Try to get the symbiont system directly from the registry
                const symbiontSystem = this.scene?.registry?.get('symbiontSystem');
                
                if (symbiontSystem) {
                    console.log('[SporeSystem] Found symbiontSystem in registry');
                    const message = symbiontSystem.getSporeChangeMessage(oldSporeLevel, this.sporeLevel);
                    if (message) {
                        console.log('[SporeSystem] Symbiont message:', message);
                        // Use the scene directly to show notification
                        this.scene.showNotification(message, "", "", 10000);
                    } else {
                        console.log('[SporeSystem] No symbiont message generated');
                    }
                } else {
                    console.log('[SporeSystem] Could not find symbiontSystem in registry');
                }
            }
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
