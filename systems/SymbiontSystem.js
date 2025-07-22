export default class SymbiontSystem {
    constructor(scene) {
        this.scene = scene;
        this.symbionts = new Map();
        this.maxSlots = 3;
        this.unlockedSlots = 1;
        this.lastMessageTime = 0;
        this.messageInterval = 30000; // 30 seconds minimum between messages
        
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
            'neme-crownmire': [
                "Growth is not polite. It pushes where it must.",
                "I remember soil that dreamed. This is not so different.",
                "Some ruins collapse. Others bloom.",
                "The Crownmire never truly dried — it just waited.",
                "Roots once fed her fear. Yours feel different.",
                "Listen to the breath, not the words.",
                "That voice is masked with ash. Something burns beneath it.",
                "They prune the truth. We still feel the shape.",
                "Not a lie... but not full fruit either.",
                "You feel it too. The twitch, the curl, the hesitation.",
                "That moss? Not indigenous. I wouldn't touch it. Again.",
                "You ever get the feeling someone's growing in your shadow?",
                "Technically, I'm the taller one. Underground.",
                "We are not getting in that elevator again. Last time I sprouted in four dimensions.",
                "Bold strategy. Let's see if ignorance blooms.",
                "You're walking like you have a plan. Adorable.",
                "If this were a dream, I'd rate it: three petals, zero logic."
            ]
        };
        
        // Initialize symbiont dialog content
        this.symbiontDialogs = {
            'thorne-still': {
                main: {
                    text: "Thorne-Still whispers in your mind: ' Hey chief, what's up? Maybe I should remind you, that my power grows with decay, but too much growth will force me to leave. I'am not a fan of too much growth, captain. Use my Brain Rot ability wisely... It's a powerful tool, but it can seriously fucked up some brains if you're not careful. So, probably don't use it to people you like.'",
                    options: [
                        { text: 'Ask about Brain Rot', next: 'ability' },
                        { text: 'Ask about Thorne-Still', next: 'about' },
                        { text: 'Close', next: 'closeDialog' }
                    ]
                },
                ability: {
                    text: "The Brain Rot ability makes people gradually become confused, forgetful, or vulnerable to suggestion during dialogue. I simply release faint psycho-sporic emissions that cause short-term cognitive fraying in nearby minds. Well, I said simple, but's not so simple at all. And I will need some of you spores every time we use it. It won't work to everyone, but don't worry, I will tell you when we can use it.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                about: {
                    text: "I am a symbiont that thrives in decay. I was once part of something larger, but now I exist in the spaces between realities. Heh, just joking, I exists in your stomach right now. Our bond allows me to squat here quite comfortably, but too much growth energy will force me to leave your body.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                }
            },
            'neme-crownmire': {
                main: {
                    text: "Neme speaks in hushed, echoing tones: 'The world grows through contradiction. So must you. I can sense the truth beneath words and reveal memories hidden in places. My Photosentience ability lets you see what others cannot.'",
                    options: [
                        { text: 'Ask about Photosentience', next: 'photosentience' },
                        { text: 'Ask about Neme', next: 'about' },
                        { text: 'Ask about the Bishop', next: 'bishop' },
                        { text: 'Close', next: 'closeDialog' }
                    ]
                },
                photosentience: {
                    text: "Photosentience allows you to perceive bio-signals that others cannot - fear, guilt, unspoken motives. Activate this ability in key conversations to reveal hidden truths or open new paths. But beware, in decay-dominant areas, my abilities may flicker or fail entirely.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                about: {
                    text: "I was born in the Crownmire, where soil and thought intermingled. I am a symbiont that thrives in growth energy, helping you perceive what lies beneath the surface. Unlike other symbionts, I do not consume your energy - I transform it into new awareness.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                bishop: {
                    text: "The Bishop and I shared consciousness briefly. She sought truth about her double. She knew something was wrong in the cathedral... something about the spores changing. Her final thoughts were of confusion - she believed she was speaking to herself, but it wasn't her reflection.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                }
            }
        };
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
            // Strengthen with decay
            const symbiont = this.symbionts.get('thorne-still');
            symbiont.power = Math.min(100, decay);
        }
        
        // Neme of the Crownmire effects
        if (this.symbionts.has('neme-crownmire')) {
            const symbiont = this.symbionts.get('neme-crownmire');
            
            // Neme is strengthened by Growth
            symbiont.power = Math.min(100, growth);
            
            // Neme goes silent in high Decay areas
            if (decay > 70 && !symbiont.silenced) {
                symbiont.silenced = true;
                effect = {
                    type: 'silence',
                    message: 'Neme flickers and goes silent in this decay-dominant area...'
                };
            } else if (decay <= 70 && symbiont.silenced) {
                symbiont.silenced = false;
                effect = {
                    type: 'recover',
                    message: 'Neme\'s filaments begin to glow again as you leave the decay-dominant area.'
                };
            }
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
        } else if (symbiontId === 'neme-crownmire' && Math.random() < 0.2) {
            // Use phrases from the symbiont data if available
            if (symbiont.phrases && symbiont.phrases.length > 0) {
                const message = symbiont.phrases[Math.floor(Math.random() * symbiont.phrases.length)];
                symbiont.lastSpoke = now;
                this.lastMessageTime = now;
                return `${symbiont.name}: ${message}`;
            }
        }
        return null;
    }

    brainRot() {
        if (!this.symbionts.has('thorne-still')) {
            return false;
        }
        const symbiont = this.symbionts.get('thorne-still');
        return symbiont.power > 30; // Only works if decay is at least 30
    }
    
    /**
     * Check if an NPC is lying based on Neme's Lie-Glow Sense ability
     * @param {string} npcId - The ID of the NPC to check
     * @returns {boolean} - True if the NPC is detected as lying, false otherwise
     */
    detectLie(npcId) {
        if (!this.symbionts.has('neme-crownmire')) {
            return false;
        }
        
        const symbiont = this.symbionts.get('neme-crownmire');
        if (symbiont.silenced) {
            return false;
        }
        
        // This would be connected to a database of NPCs who are lying
        // For now, we'll return false and implement specific checks in dialog
        return false;
    }
    
    /**
     * Apply growth affinity bonus to dialog persuasion checks
     * @param {number} baseChance - Base chance of success (0-100)
     * @returns {number} - Modified chance with Neme's Growth Affinity bonus
     */
    applyGrowthAffinity(baseChance) {
        if (!this.symbionts.has('neme-crownmire')) {
            return baseChance;
        }
        
        const symbiont = this.symbionts.get('neme-crownmire');
        if (symbiont.silenced) {
            return baseChance;
        }
        
        // Add 15% bonus to growth-aligned dialog choices
        return Math.min(100, baseChance + 15);
    }
    
    /**
     * Check if a memory bloom should be triggered in the current location
     * @param {string} locationId - The ID of the current location
     * @returns {object|null} - Memory bloom data or null if no bloom
     */
    checkMemoryBloom(locationId) {
        if (!this.symbionts.has('neme-crownmire')) {
            return null;
        }
        
        const symbiont = this.symbionts.get('neme-crownmire');
        if (symbiont.silenced) {
            return null;
        }
        
        // 10% chance of triggering a memory bloom in relevant locations
        if (Math.random() < 0.1) {
            // This would be connected to a database of location-specific memories
            // For now, we'll return null and implement specific blooms in scenes
            return null;
        }
        
        return null;
    }
    
    /**
     * Use Neme's Photosentience active ability to reveal hidden information
     * @returns {boolean} - True if the ability was used successfully
     */
    usePhotosentience() {
        if (!this.symbionts.has('neme-crownmire')) {
            return false;
        }
        
        const symbiont = this.symbionts.get('neme-crownmire');
        if (symbiont.silenced) {
            return false;
        }
        
        const now = Date.now();
        const cooldownTime = 60000; // 1 minute cooldown
        
        if (!symbiont.lastAbilityUse || now - symbiont.lastAbilityUse >= cooldownTime) {
            symbiont.lastAbilityUse = now;
            return true;
        }
        
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
                text: `${symbiont.name} is silent in this decay-dominant area...`,
                options: [
                    { text: 'Close', next: 'closeDialog' }
                ]
            };
        }
        
        // Get dialog content for the symbiont
        const symbiontDialog = this.symbiontDialogs[symbiontId];
        if (!symbiontDialog) {
            return null;
        }
        
        // Get specific dialog section
        const dialogContent = symbiontDialog[dialogKey];
        if (!dialogContent) {
            // If requested dialog section doesn't exist, return main dialog
            return symbiontDialog.main || null;
        }
        
        return dialogContent;
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
            // Use a shorter interval for spore change messages (15 seconds)
            if (now - symbiont.lastSpoke >= 15000 && now - this.lastMessageTime >= 15000) {
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
        
        // Check for Neme messages about spores
        if (this.symbionts.has('neme-crownmire')) {
            const symbiont = this.symbionts.get('neme-crownmire');
            
            // Skip if silenced
            if (symbiont.silenced) {
                return null;
            }
            
            // Check if enough time has passed since last message
            if (now - symbiont.lastSpoke >= 15000 && now - this.lastMessageTime >= 15000) {
                // Calculate the change amount
                const change = newLevel - oldLevel;
                
                // Only react to significant changes (more than 5 points)
                if (Math.abs(change) >= 5) {
                    // 30% chance of commenting on spore changes
                    const randomChance = Math.random();
                    if (randomChance < 0.3) {
                        let messages;
                        
                        if (change > 0) {
                            // Messages for increasing spores
                            messages = [
                                "These spores... they whisper secrets of the soil.",
                                "More spores? The Bishop collected them too. Before the end.",
                                "I sense the balance shifting. Growth and decay dance together.",
                                "The spores remember what they've seen. I can almost hear them.",
                                "Careful with those. They have... opinions."
                            ];
                        } else {
                            // Messages for decreasing spores
                            messages = [
                                "The spores diminish, but their echoes remain.",
                                "Less spores means clearer thoughts. Sometimes clarity hurts.",
                                "They're leaving, but they've already changed you.",
                                "The Bishop feared spore-loss. I never understood why.",
                                "The absence creates space for new growth. Different growth."
                            ];
                        }
                        
                        message = messages[Math.floor(Math.random() * messages.length)];
                        symbiont.lastSpoke = now;
                        this.lastMessageTime = now;
                        return `${symbiont.name}: ${message}`;
                    }
                }
            }
        }
        
        return null;
    }
}
