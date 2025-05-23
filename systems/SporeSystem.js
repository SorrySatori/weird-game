export default class SporeSystem {
    constructor(scene) {
        this.scene = scene;
        
        // Initialize spore level (100% at start)
        this.sporeLevel = 100;
        
        // Minimum and maximum values
        this.minSporeLevel = 0;
        this.maxSporeLevel = 100;
        
        // Subscribers for UI updates
        this.subscribers = [];
    }
    
    // Get current spore level
    getSporeLevel() {
        return this.sporeLevel;
    }
    
    // Decrease spore level by given amount
    decreaseSpores(amount) {
        this.sporeLevel = Math.max(this.minSporeLevel, this.sporeLevel - amount);
        this.notifySubscribers();
        return this.sporeLevel;
    }
    
    // Increase spore level by given amount
    increaseSpores(amount) {
        this.sporeLevel = Math.min(this.maxSporeLevel, this.sporeLevel + amount);
        this.notifySubscribers();
        return this.sporeLevel;
    }
    
    // Set spore level to specific value
    setSporeLevel(level) {
        this.sporeLevel = Math.max(this.minSporeLevel, Math.min(this.maxSporeLevel, level));
        this.notifySubscribers();
        return this.sporeLevel;
    }
    
    // Subscribe to changes
    subscribe(callback) {
        if (typeof callback === 'function' && !this.subscribers.includes(callback)) {
            this.subscribers.push(callback);
        }
    }
    
    // Unsubscribe from changes
    unsubscribe(callback) {
        this.subscribers = this.subscribers.filter(sub => sub !== callback);
    }
    
    // Notify all subscribers of changes
    notifySubscribers() {
        this.subscribers.forEach(callback => callback(this.sporeLevel));
    }
    
    // Clean up resources
    cleanup() {
        this.subscribers = [];
    }
}
