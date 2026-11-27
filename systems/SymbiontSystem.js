import GrowthDecaySystem from './GrowthDecaySystem.js';

/** Above this Decay Ulvarex's mirages unravel and she goes quiet (her abilities are unavailable meanwhile). */
export const ULVAREX_SILENT_DECAY = 70;
/** Below this many spores Ulvarex grumbles about the bare pantry when asked how she likes living in her host. */
const ULVAREX_HUNGRY_SPORES = 30;

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
            // Ulvarex, the Borrowed Horizon (CZ: feminine, lang/cs/symbiontLines.js)
            'ulvarex-borrowed-horizon': [
                "Never trust your own eyes. Unless I'm the one living in them.",
                "Space and time belong to no one.",
                "I once convinced a river it was a road. The fish built a petrol station on it.",
                "Reality is merely the most popular illusion.",
                "I hear light. I see sound.",
                "Every mirror lies. I just lie more creatively.",
                "Rules are really more like guidelines.",
                "There's only a very thin line between what is and what could be.",
                "I don't make lies. I make truths that haven't happened yet.",
                "Want to see a trick? Look out, what's that behind you?",
                "How many fingers do you see? How many? You'd better go and lie down.",
                "This city isn't pretty enough. It could do with a few more mirages."
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
                        { text: "What's it like, living inside me?", next: 'inside' },
                    ]
                },
                inside: {
                    text: "'Cosy. Warm, damp, a bit cramped after lunch. But the spores, chief! You've got so many in here I've started naming them. That one on the left is Brenda. I eat a few every time we do Brain Rot, but Brenda I'm saving for Sunday.'",
                    options: [
                        { text: 'Back', next: 'main' }
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
            // The demo's Growth-leaning illusionist: silent where Decay runs high (isDormant), her uses lean to Growth
            'ulvarex-borrowed-horizon': {
                main: {
                    text: "Ulvarex's voice arrives like light through a prism, fractured, warm and slightly wrong: 'Ah, host. Looking at the world again with those honest eyes? How exhausting. I am Ulvarex, the Borrowed Horizon, and I deal in what could be. My Mirage Weave bends perception, so people see things that aren't quite there. Some might take it for lying, but I'd say it's more like advanced diplomacy.'",
                    options: [
                        { text: 'Ask about Mirage Weave', next: 'ability' },
                        { text: 'Ask about Ulvarex', next: 'about' },
                        { text: 'Ask how she likes living in you', next: 'host' },
                    ]
                },
                host: {
                    text: "\"Cosy, damp, and a full fridge within reach. Best lodgings I've ever had.\" Ulvarex's voice glimmers, amused. A pause. \"I see no reason to move out just yet.\"",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                // `host` when the host runs low on spores (getSymbiontDialogContent swaps it in)
                host_hungry: {
                    text: "\"Roomy and damp. Only the pantry's been looking a bit bare lately, darling. I'm just mentioning it.\"",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                ability: {
                    text: "Mirage Weave makes convincing illusions: objects, substances, even small creatures. The trick is that every one must be anchored to something real. I can't conjure an illusion out of nothing at all. Give me a shadow, a reflection, a scrap of tin, and I'll build you a cathedral. It costs spores, though. And I have my tastes: a mirage that shelters something living helps this city keep growing, while one spun out of plain greed leaves nothing but decay behind. I'll let you know when I can help.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                about: {
                    text: "I lived at the shore where water meets sky, the place where the two seem to touch. When the strange mists appeared, I started... travelling. I feed on perception, thoughts and spores. Rot is my enemy, though.",
                    options: [
                        { text: 'Back', next: 'main' }
                    ]
                },
                // shown instead of the others while she is dormant (Decay > 70)
                silent: {
                    text: "Ulvarex is silent. With decay ruling the city, she can't weave illusions as well as she used to.",
                    options: []
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
            lastSpoke: 0,
            // she arrives already knowing the world's balance (no "falls silent" notice on bonding in the rot)
            ...(id === 'ulvarex-borrowed-horizon' ? { silenced: this.isDormant(id, true) } : {})
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
        
        // Don't speak if silenced
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
        } else if (symbiontId === 'ulvarex-borrowed-horizon' && Math.random() < 0.1) {
            const messages = this.symbiontPhrases['ulvarex-borrowed-horizon'] || [];
            if (messages.length > 0) {
                const message = messages[Math.floor(Math.random() * messages.length)];
                symbiont.lastSpoke = now;
                this.lastMessageTime = now;
                return `Ulvarex: ${message}`;
            }
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
        const hasUlvarex = this.symbionts.has('ulvarex-borrowed-horizon');

        const reactions = [];

        // Thorne reacting to others
        if (speakerId === 'thorne-still' && hasUlvarex) {
            reactions.push(
                "Thorne-Still: Ulvarex keeps rearranging your rods and cones. I had a system in there.",
                "Thorne-Still: An illusionist. Great. As if reality wasn't confusing enough already.",
                "Thorne-Still: Ulvarex bent the light around my rot spores. I was growing that mould, it was going to be a metre tall. I'm furious."
            );
        }

        // Ulvarex reacting to others
        if (speakerId === 'ulvarex-borrowed-horizon' && hasThorne) {
            reactions.push(
                "Ulvarex: Thorne keeps rotting my illusions from the inside. Rude, but artistically interesting.",
                "Ulvarex: The decay symbiont sees through my mirages. Annoying. Nobody else does.",
                "Ulvarex: Thorne and I disagree on aesthetics. Rot is not a color, I keep telling it."
            );
        }

        if (reactions.length === 0) return null;
        return reactions[Math.floor(Math.random() * reactions.length)];
    }

    brainRot() {
        if (!this.symbionts.has('thorne-still')) {
            return false;
        }
        // Live: Thorne-Still's brain-rot only bites when Decay is high enough to feed it
        // (computed from the current balance, not a stale power stat).
        return GrowthDecaySystem.getInstance().getDecay() > 30;
    }
    
    /**
     * True while a carried symbiont is silenced by the world's balance. The HUD polls it every frame.
     * Thorne-Still never goes silent; Ulvarex does where Decay runs high (the mirror of Thorne-Still
     * leaving at high Growth): the rot curdles the light she weaves with.
     * @param {string} id
     * @param {boolean} [ignorePresence] answer for a symbiont that isn't carried (yet)
     * @returns {boolean}
     */
    isDormant(id, ignorePresence = false) {
        if (!ignorePresence && !this.symbionts.has(id)) return false;
        if (id === 'ulvarex-borrowed-horizon') return GrowthDecaySystem.getInstance().getDecay() > ULVAREX_SILENT_DECAY;
        return false;
    }

    /** Ulvarex is carried, awake (Decay not above 70) and the player has `cost` spores for a weave. */
    canWeave(cost = 0) {
        if (!this.symbionts.has('ulvarex-borrowed-horizon') || this.isDormant('ulvarex-borrowed-horizon')) return false;
        return (this.scene?.registry?.get('sporeSystem')?.getSporeLevel() ?? 0) >= cost;
    }

    /**
     * Ulvarex falling silent or waking up since the last call (GameScene.update polls it): her `silenced` flag rides
     * in the save, so a scene start or a reload never announces a change that didn't happen.
     * @returns {Array<{id: string, state: 'silence'|'recover'}>}
     */
    updateDormancy() {
        const changes = [];
        const id = 'ulvarex-borrowed-horizon';
        const s = this.symbionts.get(id);
        if (!s) return changes;
        const dormant = this.isDormant(id);
        if (dormant !== !!s.silenced) {
            s.silenced = dormant;
            changes.push({ id, state: dormant ? 'silence' : 'recover' });
            this.syncRegistrySymbionts();
        }
        return changes;
    }

    /** What a symbiont says when it falls silent / wakes up (the HUD shows it in a bubble by its pod). */
    dormancyLine(id, state) {
        if (id !== 'ulvarex-borrowed-horizon') return null;
        return state === 'silence'
            ? "Ulvarex: Too much rot in the air. Illusions are hard to make right now. Do something about it, or we've nothing to talk about."
            : "Ulvarex: Ah, the light is clean again. I'm back.";
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
        
        // Silenced by the world's balance: its own "silent" line (localized as dialogs.silent)
        const symbiont = this.symbionts.get(symbiontId);
        if (this.isDormant(symbiontId)) {
            return {
                speaker: symbiont.name,
                text: this.symbiontDialogs[symbiontId]?.silent?.text || `${symbiont.name} is silent in this decay-dominant area...`,
                options: [],
                silent: true
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
        
        // Ulvarex feeds on spores: asked how she likes it in a host who is running low, she hints at the bare pantry
        if (symbiontId === 'ulvarex-borrowed-horizon' && dialogKey === 'host'
            && (this.scene?.registry?.get('sporeSystem')?.getSporeLevel() ?? 100) < ULVAREX_HUNGRY_SPORES) {
            dialogKey = 'host_hungry';
        }

        // Get specific dialog section
        const dialogContent = symbiontDialog[dialogKey];
        if (!dialogContent) {
            // If requested dialog section doesn't exist, return main dialog
            return symbiontDialog.main || null;
        }
        
        // Ensure the dialog content has a speaker (the symbiont's name)
        const result = { ...dialogContent, options: [...dialogContent.options], locKey: dialogKey };
        if (!result.speaker) {
            result.speaker = symbiont.name;
        }
        
        // Inject cross-reaction options into the main dialog
        if (dialogKey === 'main' && this.symbionts.size >= 2) {
            // `askAbout`: GameScene localizes it as symbionts.<that id>.askAbout
            const otherSymbionts = [];
            if (symbiontId !== 'thorne-still' && this.symbionts.has('thorne-still')) {
                otherSymbionts.push({ text: 'Ask about Thorne-Still', next: 'about_thorne', askAbout: 'thorne-still' });
            }
            if (symbiontId !== 'ulvarex-borrowed-horizon' && this.symbionts.has('ulvarex-borrowed-horizon')) {
                otherSymbionts.push({ text: 'Ask about Ulvarex', next: 'about_ulvarex', askAbout: 'ulvarex-borrowed-horizon' });
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
                about_ulvarex: {
                    text: "\"The light-bender. Ulvarex. Harmless, mostly. Keeps rearranging the insides of your optic nerves like it's furniture or something. I had a nice little fungus colony tucked away in your eye socket, and suddenly it's all scrubbed clean.\" Thorne grumbles. \"Illusions are just lies with better lighting. At least decay is honest.\"",
                    options: [{ text: 'Back', next: 'main' }]
                },
            },
            'ulvarex-borrowed-horizon': {
                about_thorne: {
                    text: "\"Thorne-Still? Oh, the little rot-goblin. It keeps nibbling away at my best illusion material. Rude, but I value its devotion to entropy.\" Ulvarex's voice shimmers with amusement. \"We get along, oddly. Just don't let it win: when decay gets the upper hand, I'm the first thing it eats.\"",
                    options: [{ text: 'Back', next: 'main' }]
                },
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

        // Ulvarex: her spores are the stuff of her mirages (quiet while the rot silences her)
        const ulvarex = this.symbionts.get('ulvarex-borrowed-horizon');
        if (ulvarex && !this.isDormant('ulvarex-borrowed-horizon')
            && now - ulvarex.lastSpoke >= this.messageInterval && now - this.lastMessageTime >= this.messageInterval) {
            const change = newLevel - oldLevel;
            if (Math.abs(change) >= 5 && Math.random() < 0.3) {
                const messages = change > 0 ? [
                    "More spores. More raw material. The mirages grow richer.",
                    "Ah, fresh perception-fuel. I can feel the light bending already.",
                    "Your spore reserves are climbing. Perfect material for painting a sunset.",
                    "Excellent. With these spores I could fool a mirror.",
                    "The weave thickens. Reality won't know which way to turn."
                ] : [
                    "Fewer spores. My illusions grow thin, like morning mist.",
                    "Careful. Without spores, I'm just a voice that can't do a thing.",
                    "The weave is fraying. I'd avoid any grand mirages for now.",
                    "Spore reserves dropping. My mirages might start looking like suggestions.",
                    "Less fuel means less spectacle. I'll have to work with shadows alone."
                ];
                ulvarex.lastSpoke = now;
                this.lastMessageTime = now;
                return `Ulvarex: ${messages[Math.floor(Math.random() * messages.length)]}`;
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
