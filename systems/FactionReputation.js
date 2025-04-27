export default class FactionReputation {
    constructor() {
        this.factions = {
            RustChoir: {
                reputation: 0,
                name: "Rust Choir",
                color: 0xb87333 // Copper color for Rust Choir
            }
        };
    }

    modifyReputation(factionName, amount) {
        if (this.factions[factionName]) {
            this.factions[factionName].reputation += amount;
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
