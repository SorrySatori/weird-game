/**
 * JournalSystem.js
 * A system to track and record important events in the game.
 * Used for narrative recall and to support quest mechanics like Edgar's book writing.
 */
class JournalSystem extends Phaser.Events.EventEmitter {
    constructor() {
        super();
        // Singleton pattern - return existing instance if available
        if (JournalSystem.instance) {
            return JournalSystem.instance;
        }
        JournalSystem.instance = this;
        
        // Initialize journal entries storage
        this.entries = new Map();
        // Facts learned later about an entry (entryId -> [{ id, text }]), shown appended to it.
        // Kept apart from the entries so a fact heard before the entry exists isn't lost.
        this.facts = new Map();
        this.subscribers = new Set();
        this.scene = null;
        
        // Categories for journal entries
        this.categories = {
            PEOPLE: 'People',
            PLACES: 'Places',
            EVENTS: 'Events',
            LORE: 'Lore',
            DREAMS: 'Dreams',
            FACTIONS: 'Factions'
        };
        
        // Initialize event emitter
        if (!this.events) {
            this.events = new Phaser.Events.EventEmitter();
        }
    }

    /**
     * Get singleton instance
     */
    static getInstance() {
        if (!JournalSystem.instance) {
            JournalSystem.instance = new JournalSystem();
        }
        return JournalSystem.instance;
    }

    /**
     * Add subscriber to be notified when entries change
     */
    subscribe(callback) {
        this.subscribers.add(callback);
    }

    /**
     * Remove subscriber
     */
    unsubscribe(callback) {
        this.subscribers.delete(callback);
    }

    /**
     * Notify all subscribers of changes
     */
    notifySubscribers() {
        this.subscribers.forEach(callback => callback());
    }

    /**
     * Set the current scene
     */
    setScene(scene) {
        this.scene = scene;
    }

    /**
     * Add a new journal entry
     * @param {string} id - Unique identifier for the entry
     * @param {string} title - Title of the journal entry
     * @param {string} content - Main content of the journal entry
     * @param {string} category - Category from this.categories
     * @param {Object} metadata - Additional metadata like location, characters involved, etc.
     * @returns {boolean} - True if entry was added, false if it already existed
     */
    addEntry(id, title, content, category, metadata = {}) {
        // Don't add duplicate entries
        if (this.entries.has(id)) {
            return false;
        }

        // Verify category is valid
        const validCategory = Object.values(this.categories).includes(category) 
            ? category 
            : this.categories.EVENTS;

        // Create the entry with timestamp
        const entry = {
            id,
            title,
            content,
            category: validCategory,
            metadata,
            timestamp: new Date(),
            sceneKey: this.scene ? this.scene.scene.key : 'unknown'
        };

        // Store the entry
        this.entries.set(id, entry);
        this.syncRegistryJournal();
        
        // Notify subscribers and emit event
        this.notifySubscribers();
        this.emit('entryAdded', id, title);
        
        return true;
    }

    /**
     * Check if an entry exists in the journal
     * @param {string} id - Entry identifier to check
     * @returns {boolean} - True if entry exists
     */
    hasEntry(id) {
        return this.entries.has(id);
    }

    /**
     * Get a specific journal entry
     * @param {string} id - Entry identifier
     * @returns {Object|null} - The journal entry or null if not found
     */
    getEntry(id) {
        return this.entries.get(id) || null;
    }

    /**
     * Get all journal entries
     * @returns {Array} - Array of all journal entries
     */
    getAllEntries() {
        return Array.from(this.entries.values());
    }

    /**
     * Get entries by category
     * @param {string} category - Category to filter by
     * @returns {Array} - Array of entries in the specified category
     */
    getEntriesByCategory(category) {
        return this.getAllEntries().filter(entry => entry.category === category);
    }

    /**
     * Search journal entries by text
     * @param {string} searchText - Text to search for
     * @returns {Array} - Array of matching entries
     */
    searchEntries(searchText) {
        const lowerSearch = searchText.toLowerCase();
        return this.getAllEntries().filter(entry => {
            return entry.title.toLowerCase().includes(lowerSearch) || 
                   entry.content.toLowerCase().includes(lowerSearch);
        });
    }

    /**
     * Update an existing journal entry
     * @param {string} id - Entry identifier
     * @param {Object} updates - Properties to update
     * @returns {boolean} - True if entry was updated
     */
    updateEntry(id, updates) {
        const entry = this.entries.get(id);
        if (!entry) {
            return false;
        }

        // Apply updates to the entry
        Object.keys(updates).forEach(key => {
            if (key !== 'id' && key !== 'timestamp') {
                entry[key] = updates[key];
            }
        });

        // Add update timestamp
        entry.lastUpdated = new Date();
        this.syncRegistryJournal();
        
        // Notify subscribers and emit event
        this.notifySubscribers();
        this.emit('entryUpdated', id, entry.title);
        
        return true;
    }

    /**
     * Append something the player has just learned to an entry (a person's entry grows as they find
     * out more). Idempotent per factId. The text is the English fallback; the journal UI shows
     * `journal.<entryId>.facts.<factId>` from the language files when present.
     * @returns {boolean} - True if the fact is new
     */
    addFact(entryId, factId, text) {
        const list = this.facts.get(entryId) || [];
        if (list.some(f => f.id === factId)) {
            return false;
        }
        list.push({ id: factId, text });
        this.facts.set(entryId, list);

        const entry = this.entries.get(entryId);
        if (entry) entry.lastUpdated = new Date();
        this.syncRegistryJournal();
        this.notifySubscribers();
        if (entry) this.emit('entryUpdated', entryId, entry.title);
        return true;
    }

    hasFact(entryId, factId) {
        return (this.facts.get(entryId) || []).some(f => f.id === factId);
    }

    /** Facts learned about an entry, in the order they were found out. */
    getFacts(entryId) {
        return this.facts.get(entryId) || [];
    }

    /**
     * Count how many entries match a specific criteria
     * @param {Function} filterFn - Filter function to apply
     * @returns {number} - Count of matching entries
     */
    countEntries(filterFn = null) {
        if (filterFn) {
            return this.getAllEntries().filter(filterFn).length;
        }
        return this.entries.size;
    }
    
    /**
     * Get serializable data for saving
     * @returns {Object} Data that can be serialized to JSON
     */
    getSerializableData() {
        // Convert Map to array of entries for serialization
        return {
            entries: Array.from(this.entries.entries()),
            facts: Array.from(this.facts.entries())
        };
    }

    syncRegistryJournal() {
        if (this.scene?.registry?.has('savedJournal')) {
            this.scene.registry.set('savedJournal', this.getSerializableData());
        }
    }
    
    /**
     * Load data from a save file
     * @param {Object} data - Data from save file
     */
    loadFromData(data) {
        if (data && data.entries) {
            // Clear existing entries
            this.entries.clear();
            
            // Track seen IDs to skip duplicates in save data
            const seen = new Set();
            
            // Restore entries from data
            data.entries.forEach(([id, entry]) => {
                // Skip duplicate entries — keep only the first occurrence
                if (seen.has(id)) return;
                seen.add(id);
                
                // Convert date strings back to Date objects
                if (entry.timestamp) {
                    entry.timestamp = new Date(entry.timestamp);
                }
                if (entry.lastUpdated) {
                    entry.lastUpdated = new Date(entry.lastUpdated);
                }
                
                this.entries.set(id, entry);
            });

            // Saves from before facts existed have none
            this.facts = new Map(data.facts || []);
            if (!data.facts && this.entries.has('met_infinite_fold')) {
                // that entry used to state the Bishop truth outright; dialog gates on knowing it
                this.facts.set('met_infinite_fold', [{ id: 'bishop_truth', text: "It told me the truth about the Bishop: it and its kindred offered to make her their human conduit; she refused rather than cease being herself; it misread her refusal as a runtime fault and, trying to 'complete' her, destroyed her." }]);
            }

            this.notifySubscribers();
        }
    }
}

export default JournalSystem;
