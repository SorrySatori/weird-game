export default class FactionReputation extends Phaser.Events.EventEmitter {
    constructor() {
        super();
        this.factions = {
            RustChoir: {
                reputation: 0,
                name: "Rust Choir",
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
}
