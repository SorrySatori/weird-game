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
            ],
            'ulvarex-borrowed-horizon': [
                "What you see is never what is. That's not a flaw — it's a feature.",
                "The horizon is always borrowed. No one owns distance.",
                "I once convinced a river it was a road. It drowned three merchants.",
                "Reality is merely the most popular illusion.",
                "Light bends around me. I try not to take it personally.",
                "Every mirror lies. I just lie more creatively.",
                "You see walls. I see suggestions.",
                "There's a thin membrane between what is and what could seem to be.",
                "I don't create false things. I create true things that haven't happened yet.",
                "The best illusion is the one the audience wants to believe."
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
            },
            'ulvarex-borrowed-horizon': {
                main: {
                    text: "Ulvarex's voice arrives like light through a prism — fractured, warm, slightly wrong: 'Ah, host. You're looking at the world again with those honest eyes. How exhausting. I am Ulvarex, the Borrowed Horizon. I deal in what-could-be. My Mirage Weave lets us bend perception — make people see things that aren't quite there. Some call it lying. I call it advanced diplomacy.'",
                    options: [
                        { text: 'Ask about Mirage Weave', next: 'ability' },
                        { text: 'Ask about Ulvarex', next: 'about' },
                    ]
                },
                ability: {
                    text: "Mirage Weave creates convincing illusions — objects, substances, even small creatures. The trick is that they must be anchored to something real. I can't conjure from nothing. Give me a shadow, a reflection, a memory, and I'll build you a cathedral. But it costs spores, and if your reserves are too low, the weave unravels. Badly.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                about: {
                    text: "I existed at the shore where water meets sky — the place where the eye is fooled into believing they touch. When the mists came, I became... portable. I feed on perception itself, not growth or decay. Your spores are my medium — the raw material of bent light. The more you carry, the grander the illusion.",
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
        
        // Ulvarex the Borrowed Horizon effects
        if (this.symbionts.has('ulvarex-borrowed-horizon')) {
            const symbiont = this.symbionts.get('ulvarex-borrowed-horizon');
            // Ulvarex feeds on spores — power is half of current spore level
            // SporeSystem level is accessed through scene registry
            if (this.scene && this.scene.registry) {
                const sporeLevel = this.scene.registry.get('sporeLevel') || 0;
                symbiont.power = Math.min(100, Math.floor(sporeLevel / 2));
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
        } else if (symbiontId === 'ulvarex-borrowed-horizon' && Math.random() < 0.2) {
            const messages = this.symbiontPhrases['ulvarex-borrowed-horizon'] || [];
            if (messages.length > 0) {
                const message = messages[Math.floor(Math.random() * messages.length)];
                symbiont.lastSpoke = now;
                this.lastMessageTime = now;
                return `Ulvarex: ${message}`;
            }
        }

        // Cross-reactions: symbionts commenting on each other (10% chance)
        if (this.symbionts.size >= 2 && Math.random() < 0.1) {
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
        const hasNeme = this.symbionts.has('neme-crownmire');
        const hasUlvarex = this.symbionts.has('ulvarex-borrowed-horizon');

        const reactions = [];

        // Thorne reacting to others
        if (speakerId === 'thorne-still') {
            if (hasNeme) {
                reactions.push(
                    "Thorne-Still: That fungal thing keeps trying to photosynthesize my thoughts. Boundaries, Neme.",
                    "Thorne-Still: Neme's growing roots near my favorite organ again. Tell her to stop.",
                    "Thorne-Still: I don't trust anything that thrives on sunlight. It's unnatural.",
                    "Thorne-Still: Neme whispered something about 'renewal' in my sleep. I haven't slept in decades."
                );
            }
            if (hasUlvarex) {
                reactions.push(
                    "Thorne-Still: Ulvarex keeps rearranging your visual cortex. I had a system in there.",
                    "Thorne-Still: An illusionist. Great. As if reality wasn't confusing enough already.",
                    "Thorne-Still: Ulvarex bent the light around my rot spores. They looked like butterflies. I'm furious."
                );
            }
        }

        // Neme reacting to others
        if (speakerId === 'neme-crownmire') {
            if (hasThorne) {
                reactions.push(
                    "Neme: Thorne leaves a trail of decay wherever it settles. My roots keep having to regrow.",
                    "Neme: That stitcher-between-worlds is corroding your liver. I've filed a formal complaint.",
                    "Neme: Thorne and I have a... professional disagreement about cellular integrity.",
                    "Neme: I grew a flower in your spleen. Thorne ate it. This is why we can't cohabitate."
                );
            }
            if (hasUlvarex) {
                reactions.push(
                    "Neme: Ulvarex's illusions smell like burnt sugar. Real things smell like soil.",
                    "Neme: I can see through Ulvarex's mirages. They're beautiful, but hollow.",
                    "Neme: The illusionist keeps making my root-visions look prettier. I didn't ask for an editor."
                );
            }
        }

        // Ulvarex reacting to others
        if (speakerId === 'ulvarex-borrowed-horizon') {
            if (hasThorne) {
                reactions.push(
                    "Ulvarex: Thorne keeps rotting my illusions from the inside. Rude, but artistically interesting.",
                    "Ulvarex: The decay symbiont sees through my mirages. Annoying. Nobody else does.",
                    "Ulvarex: Thorne and I disagree on aesthetics. Rot is not a color palette, I keep telling it."
                );
            }
            if (hasNeme) {
                reactions.push(
                    "Ulvarex: Neme's growth keeps making my illusions sprout actual leaves. That's not how mirages work.",
                    "Ulvarex: The plant one insists on truth. How exhausting. We balance each other out, I suppose.",
                    "Ulvarex: Neme grew moss on my best mirage. I'll never forgive her. It was a masterpiece."
                );
            }
            if (hasThorne && hasNeme) {
                reactions.push(
                    "Ulvarex: Three symbionts in one body. We're less of a partnership and more of a landlord dispute.",
                    "Ulvarex: Thorne rots, Neme grows, I lie. Together we're basically a functioning ecosystem."
                );
            }
        }

        if (reactions.length === 0) return null;
        return reactions[Math.floor(Math.random() * reactions.length)];
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
            if (symbiontId !== 'neme-crownmire' && this.symbionts.has('neme-crownmire')) {
                otherSymbionts.push({ text: 'Ask about Neme', next: 'about_neme' });
            }
            if (symbiontId !== 'ulvarex-borrowed-horizon' && this.symbionts.has('ulvarex-borrowed-horizon')) {
                otherSymbionts.push({ text: 'Ask about Ulvarex', next: 'about_ulvarex' });
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
                about_neme: {
                    text: "\"That fungal squatter? Neme of the Crownmire. Growth-obsessed sentimentalist. She keeps trying to 'renew' my favorite necrotic tissue. We have a... professional disagreement about the direction of your cellular health.\" A pause. \"She's not wrong about everything. But don't tell her I said that.\"",
                    options: [{ text: 'Back', next: 'main' }]
                },
                about_ulvarex: {
                    text: "\"The light-bender. Ulvarex. Harmless, mostly. Keeps rearranging your visual cortex like it's furniture. I had a perfectly good rot colony in your optic nerve and now it looks like a sunset.\" Thorne grumbles. \"Illusions are just lies with better lighting. At least decay is honest.\"",
                    options: [{ text: 'Back', next: 'main' }]
                }
            },
            'neme-crownmire': {
                about_thorne: {
                    text: "\"Thorne-Still. The stitcher-between-worlds.\" Neme's tone is careful, measured. \"We are... contrary forces sharing the same soil. It corrodes. I cultivate. Some days the balance holds. Other days I find my root-tips dissolved overnight.\" A gentle sigh. \"It means well. In its own entropic way.\"",
                    options: [{ text: 'Back', next: 'main' }]
                },
                about_ulvarex: {
                    text: "\"Ulvarex. The Borrowed Horizon.\" Neme considers. \"It makes false flowers that smell real. I find this... unsettling. Truth has texture. Illusions have none, no matter how beautiful they appear.\" A pause. \"But I admit — its mirages sometimes reveal what people wish were true. And wishes are a kind of seed.\"",
                    options: [{ text: 'Back', next: 'main' }]
                }
            },
            'ulvarex-borrowed-horizon': {
                about_thorne: {
                    text: "\"Thorne-Still? Oh, the little rot-goblin. It keeps eating my best illusions from the inside out. Rude, but I respect the commitment to entropy.\" Ulvarex's voice shimmers with amusement. \"We actually work well together, oddly. Decay makes things ambiguous, and ambiguity is my favorite raw material.\"",
                    options: [{ text: 'Back', next: 'main' }]
                },
                about_neme: {
                    text: "\"Neme. Dear, earnest Neme. She sees through every mirage I weave and then grows moss on it.\" A theatrical sigh. \"The problem with truth-seekers is they think truth is the point. It's not. The point is what people do with what they believe.\" A beat. \"She's good company, though. Even her disapproval has texture.\"",
                    options: [{ text: 'Back', next: 'main' }]
                }
            }
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
        
        // Check for Ulvarex messages about spores
        if (this.symbionts.has('ulvarex-borrowed-horizon')) {
            const symbiont = this.symbionts.get('ulvarex-borrowed-horizon');
            
            if (now - symbiont.lastSpoke >= 15000 && now - this.lastMessageTime >= 15000) {
                const change = newLevel - oldLevel;
                
                if (Math.abs(change) >= 5) {
                    if (Math.random() < 0.3) {
                        let messages;
                        
                        if (change > 0) {
                            messages = [
                                "More spores. More raw material. The mirages grow richer.",
                                "Ah, fresh perception-fuel. I can feel the light bending already.",
                                "Your spore reserves are climbing. I could paint a sunset with these.",
                                "Excellent. With these spores I could fool a mirror.",
                                "The weave thickens. Reality won't know what hit it."
                            ];
                        } else {
                            messages = [
                                "Fewer spores. My illusions grow thin, like morning mist.",
                                "Careful. Without spores, I'm just a voice with opinions.",
                                "The weave is fraying. I'd avoid any grand deceptions for now.",
                                "Spore reserves dropping. My mirages might start looking like suggestions.",
                                "Less fuel means less spectacle. I'll have to work with shadows alone."
                            ];
                        }
                        
                        message = messages[Math.floor(Math.random() * messages.length)];
                        symbiont.lastSpoke = now;
                        this.lastMessageTime = now;
                        return `Ulvarex: ${message}`;
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
    }
}
