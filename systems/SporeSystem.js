class SporeSystem extends Phaser.Events.EventEmitter {
    constructor(scene) {
        super();
        if (SporeSystem.instance) {
            return SporeSystem.instance;
        }
        SporeSystem.instance = this;
        
        this.scene = scene; // Store reference to the scene
        this.currentSpores = 100; // Current spore level
        this.maxSpores = 100;     // Maximum spore capacity
        this.sporeLevel = 100;     // Legacy property for compatibility
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
            const oldSporeLevel = this.currentSpores;
            this.currentSpores = Math.max(0, Math.min(this.maxSpores, this.currentSpores + amount));
            this.sporeLevel = this.currentSpores; // Update legacy property for compatibility
            totalChange = this.currentSpores - oldSporeLevel;
            
            // Emit event for growth change
            this.emit('sporeChanged', totalChange);
            
            // Check for symbiont reaction to spore change
            if (totalChange !== 0) {
                console.log('[SporeSystem] Spore level changed:', oldSporeLevel, '->', this.currentSpores);
                
                // Try to get the symbiont system directly from the registry
                const symbiontSystem = this.scene?.registry?.get('symbiontSystem');
                
                if (symbiontSystem) {
                    console.log('[SporeSystem] Found symbiontSystem in registry');
                    const message = symbiontSystem.getSporeChangeMessage(oldSporeLevel, this.currentSpores);
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
                callback(this.currentSpores, this.maxSpores);
            } catch (e) {
                console.warn('[SporeSystem] Removing dead subscriber:', callback, e);
                this.subscribers.delete(callback);
            }
        }
        console.log('[SporeSystem] Subscribers after notify:', Array.from(this.subscribers));
    }

    // Get current values
    getSporeLevel() {
        return this.currentSpores;
    }
    
    // Get maximum spore capacity
    getMaxSpores() {
        return this.maxSpores;
    }
    
    // Set spore level (used when loading saved games)
    setSporeLevel(value) {
        this.currentSpores = Math.max(0, Math.min(this.maxSpores, value));
        this.sporeLevel = this.currentSpores; // Update legacy property
        this.notifySubscribers();
    }
    
    // Set maximum spore capacity
    setMaxSpores(value) {
        this.maxSpores = Math.max(1, value);
        this.currentSpores = Math.min(this.currentSpores, this.maxSpores);
        this.sporeLevel = this.currentSpores; // Update legacy property
        this.notifySubscribers();
    }
    
    // Clean up resources
    cleanup() {
        this.subscribers = [];
    }
}

export default SporeSystem;
