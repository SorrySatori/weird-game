export default class FactionReputation extends Phaser.Events.EventEmitter {
    constructor() {
        super();
        this.factions = {
            RustChoir: {
                reputation: 0,
                name: "Rust Choir",
                color: 0xb87333 // Copper color for Rust Choir
            },
            PithReclaimers: {
                reputation: 0,
                name: "Pith Reclaimers",
                color: 0xb87333 // Copper color for Rust Choir
            }
        };
        
        // Initialize event emitter
        if (!this.events) {
            this.events = new Phaser.Events.EventEmitter();
        }
    }

    modifyReputation(factionName, amount) {
        if (this.factions[factionName]) {
            this.factions[factionName].reputation += amount;
            // Emit event directly from this instance
            this.emit('reputationChanged', this.factions[factionName].name, amount);
            return {
                faction: this.factions[factionName].name,
                amount: amount,
                newTotal: this.factions[factionName].reputation
            };
        }
        return null;
    }

    getReputation(factionName) {
        return this.factions[factionName]?.reputation || 0;
    }
    
    /**
     * Get all faction reputations for serialization
     * @returns {Object} All faction data
     */
    getReputations() {
        return JSON.parse(JSON.stringify(this.factions));
    }
    
    /**
     * Set faction reputations from saved data
     * @param {Object} factionData - Faction data from save file
     */
    setReputations(factionData) {
        if (!factionData) return;
        
        // Update existing factions with saved values
        Object.keys(factionData).forEach(factionName => {
            if (this.factions[factionName]) {
                this.factions[factionName].reputation = factionData[factionName].reputation;
            }
        });
    }
}
