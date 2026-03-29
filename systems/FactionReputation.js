export default class FactionReputation extends Phaser.Events.EventEmitter {
    constructor() {
        super();
        this.factions = {
            RustChoir: {
                reputation: 0,
                name: "Rust Choir",
                color: 0xb87333, // Copper color for Rust Choir
                discovered: false,
                description: "A faction dedicated to reclaiming and repurposing rust and decay."
            },
            PithReclaimers: {
                reputation: 0,
                name: "Pith Reclaimers",
                color: 0x8B4513, // Brown color for Pith Reclaimers
                discovered: false,
                description: "A group focused on maintaining and reclaiming balance and bureaucratic order."
            },
            SporemindAccord: {
                reputation: 0,
                name: "Lumen Directorate",
                color: 0x556B2F, // Dark olive green for Lumen Directorate
                discovered: false,
                description: "An alliance that values growth and all life."
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
            
            // Automatically discover faction when reputation changes
            if (!this.factions[factionName].discovered) {
                this.discoverFaction(factionName);
            }
            
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
     * Mark a faction as discovered
     * @param {string} factionName - Name of the faction to discover
     */
    discoverFaction(factionName) {
        if (this.factions[factionName]) {
            this.factions[factionName].discovered = true;
            this.emit('factionDiscovered', this.factions[factionName].name);
        }
    }
    
    /**
     * Check if a faction has been discovered
     * @param {string} factionName - Name of the faction to check
     * @returns {boolean} True if faction is discovered
     */
    isFactionDiscovered(factionName) {
        return this.factions[factionName]?.discovered || false;
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
