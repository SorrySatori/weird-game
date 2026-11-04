import GrowthDecaySystem from './GrowthDecaySystem.js';

export default class SymbiontSystem {
    constructor(scene) {
        this.scene = scene;
        this.symbionts = new Map();
        this.maxSlots = 3;
        this.unlockedSlots = 1;
        this.lastMessageTime = 0;
        this.messageInterval = 120000; // 2 minutes minimum between messages
        
        // Initialize symbiont phrases
        this.symbiontPhrases = {
            'thorne-still': [
                "Reality is fraying at the edges here.",
                "I sense decay. It strengthens me.",
                "Too much growth will force me to leave.",
                "The threads between worlds are thin in this place.",
                "I can stitch this reality back together... temporarily.",
                "We are between what is and what could be.",
                "The more decay, the stronger my abilities become.",
                "This area needs suturing. The fabric is weak.",
                "I was born in the spaces between realities.",
                "Our bond allows me to help you navigate unstable areas."
            ],
        };
        
        // Initialize symbiont dialog content
        this.symbiontDialogs = {
            'thorne-still': {
                main: {
                    text: "Thorne-Still whispers in your mind: 'Hey chief, what's up? Maybe I should remind you that my power grows with decay, but too much growth will force me to leave. I'm not a fan of too much growth, captain. Use my Brain Rot ability wisely... It's a powerful tool, but it can seriously fuck up some brains if you're not careful. So, probably don't use it on people you like.'",
                    options: [
                        { text: 'Ask about Brain Rot', next: 'ability' },
                        { text: 'Ask about Thorne-Still', next: 'about' },
                    ]
                },
                ability: {
                    text: "The Brain Rot ability makes people gradually become confused, forgetful, or vulnerable to suggestion during dialogue. I simply release faint psycho-sporic emissions that cause short-term cognitive fraying in nearby minds. Well, I said simple, but it's not so simple at all. And I will need some of your spores every time we use it. It won't work on everyone, but don't worry, I'll tell you when we can use it.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                about: {
                    text: "I am a symbiont that thrives in decay. I was once part of something larger, but now I exist in the spaces between realities. Heh, just joking, I exist in your stomach right now. Our bond allows me to squat here quite comfortably, but too much growth energy will force me to leave your body.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                }
            },
        };
    }

    addSymbiont(id, data) {
        this.reconcileUnlockedSlotsFromJournal();

        if (this.symbionts.size >= this.unlockedSlots) {
            return false;
        }
        this.symbionts.set(id, {
            ...data,
            lastSpoke: 0
        });
        this.syncRegistrySymbionts();
        return true;
    }

    removeSymbiont(id) {
        const removed = this.symbionts.delete(id);
        if (removed) this.syncRegistrySymbionts();
        return removed;
    }
    
    /**
     * Check if a specific symbiont is present
     * @param {string} id - The ID of the symbiont to check
     * @returns {boolean} - True if the symbiont exists, false otherwise
     */
    hasSymbiont(id) {
        return this.symbionts.has(id);
    }

    /**
     * Total number of symbionts the player currently carries — ALL of them, not a
     * fixed subset. Used by the "you are already many" gates (the Cathedral merge,
     * the Fold's symbiosis reading, the Guardian's reflection).
     * @returns {number}
     */
    getSymbiontCount() {
        return this.symbionts.size;
    }

    unlockSlot() {
        if (this.unlockedSlots < this.maxSlots) {
            this.unlockedSlots++;
            this.syncRegistrySymbionts();
            return true;
        }
        return false;
    }

    syncRegistrySymbionts() {
        if (this.scene?.registry?.has('savedSymbionts')) {
            this.scene.registry.set('savedSymbionts', this.getSerializableData());
        }
    }

    reconcileUnlockedSlotsFromJournal() {
        const boughtExtraSlot = this.scene?.journalSystem?.hasEntry('extra_symbiont_slot_purchased');

        if (boughtExtraSlot && this.unlockedSlots < 2) {
            this.unlockedSlots = 2;
            this.syncRegistrySymbionts();
        }
    }

    checkDecayGrowthEffects(decay, growth) {
        let effect = null;
        
        // Thorne-Still effects
        if (this.symbionts.has('thorne-still')) {
            if (growth > 80) {
                this.removeSymbiont('thorne-still');
                effect = {
                    type: 'leave',
                    message: 'The overwhelming growth forces Thorne-Still to leave your body...'
                };
            }
            // Strengthen with decay (unless it just left)
            const symbiont = this.symbionts.get('thorne-still');
            if (symbiont) symbiont.power = Math.min(100, decay);
        }
        
        




        return effect;
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
        
        // Don't speak if silenced (for Neme)
        if (symbiont.silenced) {
            return null;
        }

        // Add random chance (20%) of actually speaking
        if (symbiontId === 'thorne-still' && Math.random() < 0.1) {
            const messages = [
                "In the spaces between reality, truth flows like mercury...",
                "Flesh is just wet soil, ready for burial.",
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

        // Cross-reactions: symbionts commenting on each other (5% chance)
        if (this.symbionts.size >= 2 && Math.random() < 0.05) {
            const crossMessage = this.getCrossReactionMessage(symbiontId);
            if (crossMessage) {
                symbiont.lastSpoke = now;
                this.lastMessageTime = now;
                return crossMessage;
            }
        }

        return null;
    }

    getCrossReactionMessage(speakerId) {
        const hasThorne = this.symbionts.has('thorne-still');

        const reactions = [];

        // Thorne reacting to others
        if (speakerId === 'thorne-still') {
        }




        if (reactions.length === 0) return null;
        return reactions[Math.floor(Math.random() * reactions.length)];
    }

    brainRot() {
        if (!this.symbionts.has('thorne-still')) {
            return false;
        }
        // Live: Thorne-Still's brain-rot only bites when Decay is high enough to feed it
        // (mirror of nemeCanRead — computed from current balance, not a stale power stat).
        return GrowthDecaySystem.getInstance().getDecay() > 30;
    }
    
    /**
     * True while a carried symbiont is silenced by the world's balance: Neme where Decay > 70, Osswine where
     * Growth > 70. Read-only (unlike nemeCanRead/osswineCanRead) — the HUD polls it every frame.
     * @param {string} id
     * @returns {boolean}
     */
    isDormant(id) {
        if (!this.symbionts.has(id)) return false;
        const gd = GrowthDecaySystem.getInstance();
        if (id === 'neme-crownmire') return gd.getDecay() > 70;
        if (id === 'osswine') return gd.getGrowth() > 70;
        return false;
    }

    /**
     * Generate a message from Thorne-Still when spore level changes
     * @param {number} oldLevel - Previous spore level
     * @param {number} newLevel - New spore level
     * @returns {string|null} - Message from Thorne-Still or null if no message
     */
    /**
     * Get dialog content for a specific symbiont
     * @param {string} symbiontId - The ID of the symbiont
     * @param {string} dialogKey - The specific dialog section to retrieve (defaults to 'main')
     * @returns {object|null} - Dialog content object or null if not found
     */
    getSymbiontDialogContent(symbiontId, dialogKey = 'main') {
        // Check if symbiont exists
        if (!this.symbionts.has(symbiontId)) {
            return null;
        }
        
        // Check if symbiont is silenced (for Neme)
        const symbiont = this.symbionts.get(symbiontId);
        if (symbiont.silenced) {
            return {
                speaker: symbiont.name,
                text: `${symbiont.name} is silent in this decay-dominant area...`,
                options: []
            };
        }
        
        // Get dialog content for the symbiont
        const symbiontDialog = this.symbiontDialogs[symbiontId];
        if (!symbiontDialog) {
            return null;
        }
        
        // Check for cross-reaction dialog keys
        const crossDialog = this.getCrossReactionDialog(symbiontId, dialogKey);
        if (crossDialog) {
            return { ...crossDialog, speaker: crossDialog.speaker || symbiont.name };
        }
        
        // Get specific dialog section
        const dialogContent = symbiontDialog[dialogKey];
        if (!dialogContent) {
            // If requested dialog section doesn't exist, return main dialog
            return symbiontDialog.main || null;
        }
        
        // Ensure the dialog content has a speaker (the symbiont's name)
        const result = { ...dialogContent, options: [...dialogContent.options] };
        if (!result.speaker) {
            result.speaker = symbiont.name;
        }
        
        // Inject cross-reaction options into the main dialog
        if (dialogKey === 'main' && this.symbionts.size >= 2) {
            const otherSymbionts = [];
            if (symbiontId !== 'thorne-still' && this.symbionts.has('thorne-still')) {
                otherSymbionts.push({ text: 'Ask about Thorne-Still', next: 'about_thorne' });
            }
            // Insert before the last option (usually "Close")
            const closeIdx = result.options.findIndex(o => o.next === 'closeDialog');
            const insertIdx = closeIdx >= 0 ? closeIdx : result.options.length;
            result.options.splice(insertIdx, 0, ...otherSymbionts);
        }
        
        return result;
    }

    getCrossReactionDialog(speakerId, dialogKey) {
        const crossReactions = {
            'thorne-still': {
            },
        };

        return crossReactions[speakerId]?.[dialogKey] || null;
    }
    
    /**
     * Get the active symbiont ID (the one currently being interacted with)
     * @returns {string|null} - ID of the active symbiont or null if none
     */
    getActiveSymbiontId() {
        // Find the first non-silenced symbiont
        for (const [id, symbiont] of this.symbionts.entries()) {
            if (!symbiont.silenced) {
                return id;
            }
        }
        return null;
    }
    
    /**
     * Get the phrases for a specific symbiont
     * @param {string} symbiontId - The ID of the symbiont
     * @returns {Array} - Array of phrases or empty array if symbiont not found
     */
    getSymbiontPhrases(symbiontId) {
        return this.symbiontPhrases[symbiontId] || [];
    }
    
    getSporeChangeMessage(oldLevel, newLevel) {
        console.log('[SymbiontSystem] getSporeChangeMessage called:', oldLevel, '->', newLevel);
        
        const now = Date.now();
        let message = null;
        
        // Check for Thorne-Still messages
        if (this.symbionts.has('thorne-still')) {
            const symbiont = this.symbionts.get('thorne-still');
            console.log('[SymbiontSystem] Thorne-Still data:', symbiont);
            console.log('[SymbiontSystem] Time since last message:', now - this.lastMessageTime, 'ms');
            console.log('[SymbiontSystem] Time since symbiont last spoke:', now - symbiont.lastSpoke, 'ms');
            
            // Check if enough time has passed since last message
            // Use the same interval as ambient messages
            if (now - symbiont.lastSpoke >= this.messageInterval && now - this.lastMessageTime >= this.messageInterval) {
                // Calculate the change amount
                const change = newLevel - oldLevel;
                console.log('[SymbiontSystem] Spore change amount:', change);
                
                // Only react to significant changes (more than 5 points)
                if (Math.abs(change) >= 5) {
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
                        
                        message = messages[Math.floor(Math.random() * messages.length)];
                        symbiont.lastSpoke = now;
                        this.lastMessageTime = now;
                        return `thorne-still: ${message}`;
                    }
                }
            }
        }
        
        
        
        return null;
    }
    
    /**
     * Get serializable data for saving
     * @returns {Object} Data that can be serialized to JSON
     */
    getSerializableData() {
        return {
            symbionts: Array.from(this.symbionts.entries()),
            maxSlots: this.maxSlots,
            unlockedSlots: this.unlockedSlots,
            lastMessageTime: this.lastMessageTime,
            messageInterval: this.messageInterval
        };
    }
    
    /**
     * Load data from a save file
     * @param {Object} data - Data from save file
     */
    loadFromData(data) {
        if (!data) return;
        
        // Restore symbionts
        if (data.symbionts) {
            this.symbionts = new Map(data.symbionts);
            
            // Convert date strings back to Date objects
            this.symbionts.forEach(symbiont => {
                if (symbiont.lastSpoke) {
                    symbiont.lastSpoke = new Date(symbiont.lastSpoke);
                }
            });
        }
        
        // Restore other properties
        if (data.maxSlots) this.maxSlots = data.maxSlots;
        if (data.unlockedSlots) this.unlockedSlots = data.unlockedSlots;
        if (data.lastMessageTime) this.lastMessageTime = data.lastMessageTime;
        if (data.messageInterval) this.messageInterval = data.messageInterval;
        this.reconcileUnlockedSlotsFromJournal();
        this.syncRegistrySymbionts();
    }
}
