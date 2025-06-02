export default class SymbiontSystem {
    constructor(scene) {
        this.scene = scene;
        this.symbionts = new Map();
        this.maxSlots = 3;
        this.unlockedSlots = 1;
        this.lastMessageTime = 0;
        this.messageInterval = 30000; // 30 seconds minimum between messages
    }

    addSymbiont(id, data) {
        if (this.symbionts.size >= this.unlockedSlots) {
            return false;
        }
        this.symbionts.set(id, {
            ...data,
            lastSpoke: 0
        });
        return true;
    }

    removeSymbiont(id) {
        return this.symbionts.delete(id);
    }
    
    /**
     * Check if a specific symbiont is present
     * @param {string} id - The ID of the symbiont to check
     * @returns {boolean} - True if the symbiont exists, false otherwise
     */
    hasSymbiont(id) {
        return this.symbionts.has(id);
    }

    unlockSlot() {
        if (this.unlockedSlots < this.maxSlots) {
            this.unlockedSlots++;
            return true;
        }
        return false;
    }

    checkDecayGrowthEffects(decay, growth) {
        if (this.symbionts.has('thorne-still')) {
            if (growth > 80) {
                this.removeSymbiont('thorne-still');
                return {
                    type: 'leave',
                    message: 'The overwhelming growth forces Thorne-Still to leave your body...'
                };
            }
            // Strengthen with decay
            const symbiont = this.symbionts.get('thorne-still');
            symbiont.power = Math.min(100, decay);
        }
        return null;
    }

    getRandomMessage(symbiontId) {
        const now = Date.now();
        if (now - this.lastMessageTime < this.messageInterval) {
            return null;
        }

        const symbiont = this.symbionts.get(symbiontId);
        if (!symbiont || now - symbiont.lastSpoke < this.messageInterval) {
            return null;
        }

        // Add random chance (20%) of actually speaking
        if (symbiontId === 'thorne-still' && Math.random() < 0.2) {
            const messages = [
                "In the spaces between reality, truth flows like mercury...",
                "Flesh is just wet soil for the next thing",
                "I see the threads that bind this world together...",
                "The void whispers secrets to those who listen...",
                "Hold still. I'm aligning your inner moss...",
                "Technically, I'm a certified emotional support parasite.",
                "This body has too many elbows. I'm starting a petition.",
                "We should really talk about your hydration levels.",
                "If you die, can I keep your kneecaps?",
                "I once knew a mushroom who had ambition. It didn't end well."
            ];
            const message = messages[Math.floor(Math.random() * messages.length)];
            symbiont.lastSpoke = now;
            this.lastMessageTime = now;
            return `${symbiontId}: ${message}`;
        }
        return null;
    }

    sutureReality() {
        if (!this.symbionts.has('thorne-still')) {
            return false;
        }
        const symbiont = this.symbionts.get('thorne-still');
        return symbiont.power > 30; // Only works if decay is at least 30
    }
    
    /**
     * Generate a message from Thorne-Still when spore level changes
     * @param {number} oldLevel - Previous spore level
     * @param {number} newLevel - New spore level
     * @returns {string|null} - Message from Thorne-Still or null if no message
     */
    getSporeChangeMessage(oldLevel, newLevel) {
        console.log('[SymbiontSystem] getSporeChangeMessage called:', oldLevel, '->', newLevel);
        
        // Only generate messages if Thorne-Still is present
        if (!this.symbionts.has('thorne-still')) {
            console.log('[SymbiontSystem] Thorne-Still not present');
            return null;
        }
        
        const now = Date.now();
        const symbiont = this.symbionts.get('thorne-still');
        console.log('[SymbiontSystem] Symbiont data:', symbiont);
        console.log('[SymbiontSystem] Time since last message:', now - this.lastMessageTime, 'ms');
        console.log('[SymbiontSystem] Time since symbiont last spoke:', now - symbiont.lastSpoke, 'ms');
        
        // Check if enough time has passed since last message
        // Use a shorter interval for spore change messages (15 seconds)
        if (now - symbiont.lastSpoke < 15000 || now - this.lastMessageTime < 15000) {
            console.log('[SymbiontSystem] Not enough time has passed since last message');
            return null;
        }
        
        // Calculate the change amount
        const change = newLevel - oldLevel;
        console.log('[SymbiontSystem] Spore change amount:', change);
        
        // Only react to significant changes (more than 5 points)
        if (Math.abs(change) < 5) {
            console.log('[SymbiontSystem] Change not significant enough');
            return null;
        }
        
        // 40% chance of commenting on spore changes
        const randomChance = Math.random();
        console.log('[SymbiontSystem] Random chance:', randomChance);
        if (randomChance < 0.4) {
            let messages;
            
            if (change > 0) {
                // Messages for increasing spores
                messages = [
                    "Mmm, more spores. My favorite food group.",
                    "Your spore levels are rising. I can taste the sweet decay.",
                    "Ah, fresh spores! My cellular structure is tingling.",
                    "More spores? You're spoiling me. Literally.",
                    "I sense the spores multiplying. It's like a little party in here.",
                    "Spore levels up! That's good for business. My business is parasitism.",
                    "Ooh, spicy new spores! They have that tangy aftertaste I love.",
                    "Your spore collection is impressive. I'm taking notes.",
                    "More spores means more fun for everyone! By everyone, I mean me.",
                    "Spores increasing? I feel like I just got a promotion."
                ];
            } else {
                // Messages for decreasing spores
                messages = [
                    "Hey! I was saving those spores for later.",
                    "Selling spores? I hope you got a good price for MY dinner.",
                    "Less spores means less me. Is that what you want?",
                    "I felt those spores vanish. It's like watching money burn.",
                    "Fewer spores? I'm going to have to start rationing my existence.",
                    "You're hemorrhaging spores. That's basically symbiont abuse.",
                    "Those spores were load-bearing! The architecture of this relationship is at risk.",
                    "I was counting those spores. Literally counting them. Now I have to start over.",
                    "Spore reduction? This is why we can't have nice parasitic relationships.",
                    "Less spores? Fine. I'll just photosynthesize your emotions instead."
                ];
            }
            
            const message = messages[Math.floor(Math.random() * messages.length)];
            symbiont.lastSpoke = now;
            this.lastMessageTime = now;
            return `thorne-still: ${message}`;
        }
        
        return null;
    }
}
