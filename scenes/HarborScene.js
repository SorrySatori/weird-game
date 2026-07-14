import GameScene from './GameScene.js'
import SceneTransitionManager from '../utils/SceneTransitionManager.js'
import JournalSystem from '../systems/JournalSystem.js'

export default class HarborScene extends GameScene {
    constructor() {
        super({ key: 'HarborScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        const pithKnown = !!this.hasJournalEntry('pith_reclaimers_faction');
        const heirRecruited = !!this.hasJournalEntry('pith_recruit_heir');
        const metHeir = !!this.hasJournalEntry('met_yellow_aquarium_heir');
        return {
            ...super.dialogContent,

            // --- Heir to the Yellow Aquarium (resident here when not at auction) ---
            heir_harbor_start: {
                speaker: 'Heir to the Yellow Aquarium',
                textKey: metHeir ? 'heir_harbor_start_return' : 'heir_harbor_start_first',
                text: metHeir
                    ? `The Heir stands at the dock's edge, embryos drifting inside them in slow spirals that match the swell of the Yolk Sea. Away from the auction lamps, they seem almost at rest. As your footsteps travel through the boards, every embryo turns toward you.`
                    : `A tall translucent figure stands at the very edge of the dock, facing the Yolk Sea, their body filled with slowly floating fish embryos suspended in yellow fluid, turning in schools with the tide. A plaque on their collar reads: Heir to the Yellow Aquarium. They do not turn when you greet them — but when your voice shakes the boards, every embryo inside them turns your way.`,
                options: [
                    { text: "What are you doing out here?", key: 'what_are_you_doing_out_here', next: "heir_harbor_wants" },
                    ...(pithKnown && !heirRecruited ? [{ text: "The Pith Reclaimers could file you into the record — give you a place that stays.", key: 'heir_pith_offer', next: "heir_harbor_pith" }] : []),
                    { text: "I'll leave you to the tide.", key: 'leave_heir_harbor', next: "closeDialog" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_yellow_aquarium_heir')) {
                        this.addJournalEntry(
                            'met_yellow_aquarium_heir',
                            'Heir to the Yellow Aquarium',
                            'Met the Heir to the Yellow Aquarium at the Harbor, where they drift when no auction calls them. Their translucent body is filled with floating fish embryos, and they react more to vibration and light than to spoken words. They collect living artifacts — "continuations," they call them.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Heir to the Yellow Aquarium' }
                        );
                    }
                }
            },
            heir_harbor_wants: {
                speaker: 'Heir to the Yellow Aquarium',
                text: `The embryos gather toward the seaward side of their body, all facing the horizon. "The auction ends. The lamps go dark. The lots are carried off to dry houses." A ripple passes through the yellow fluid. "We have no dry house. No shelf. No plaque but this one." They touch their collar. "So we come to the water, where things that are not finished are allowed to keep moving. It is not belonging. It is the next-best current."`,
                options: [
                    ...(pithKnown && !heirRecruited ? [{ text: "The Pith Reclaimers give the unaccounted a place in the record. That could be your shelf.", key: 'heir_pith_offer_2', next: "heir_harbor_pith" }] : []),
                    { text: "I have other questions.", key: 'i_have_other_questions_heir', next: "heir_harbor_start" },
                ]
            },
            heir_harbor_pith: {
                speaker: 'Heir to the Yellow Aquarium',
                text: `The Heir goes very still. The embryos stop spiraling and hang, listening. "Filed. Recorded. Inherited by the register itself." Their yellow light brightens, slow and certain. "A living thing kept because it can still change — that is what the Yellow Aquarium collects. And your Reclaimers would collect... us. Keep us. Continue us." A long, tidal pause. "Yes. Take us to be written down. To be written down is to be remembered forward."`,
                options: [
                    { text: "Then come to the Townhall when you're ready. Councilor Dune will file you.", key: 'heir_pith_agree', next: "heir_harbor_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('pith_recruit_heir')) {
                        this.addJournalEntry(
                            'pith_recruit_heir',
                            'A Soul for the Pith: the Heir',
                            'The Heir to the Yellow Aquarium agreed to be filed as a citizen by the Pith Reclaimers. To a creature that collects "continuations," being written into the record is a kind of being kept — remembered forward. I should tell Councilor Seraphel Dune I have a soul for the faction.',
                            this.journalSystem.categories.FACTIONS,
                            { character: 'Heir to the Yellow Aquarium', group: 'Pith Reclaimers' }
                        );
                        this.showNotification('Recruited for the Pith Reclaimers: the Heir', 0xffdf7a);
                    }
                }
            },

            // Ulvarex the Borrowed Horizon encounter
            ulvarex_mirage: {
                speaker: 'Narrator',
                text: "The water at the dock's edge shimmers oddly — not with reflected light, but with something underneath it. A shape moves below the surface that doesn't match anything above. A face, perhaps. Or the memory of a face.",
                options: [
                    { text: "Reach toward the water.", key: 'reach_toward_the_water', next: "ulvarex_reach" },
                    { text: "Step back.", key: 'step_back', next: "closeDialog" }
                ]
            },
            ulvarex_reach: {
                speaker: 'Ulvarex',
                text: "The moment your fingers touch the surface, the reflection rearranges itself. A voice arrives — not through your ears but through your optic nerve, as if the words are made of light. \"Oh, finally. Someone who looks at mirages instead of through them. I've been folded into this puddle for... well, time doesn't move the same way when you're two-dimensional.\"",
                options: [
                    { text: "What are you?", key: 'what_are_you', next: "ulvarex_what" },
                    { text: "Why were you in the water?", key: 'why_were_you_in_the_water', next: "ulvarex_why" }
                ]
            },
            ulvarex_what: {
                speaker: 'Ulvarex',
                text: "\"I am Ulvarex, the Borrowed Horizon. A symbiont of perception. I exist in the gap between what is seen and what is understood. I can weave mirages — illusions convincing enough to fool the hand as well as the eye. But I need a host. Someone with enough spore-matter to serve as my canvas. You, for instance. You're practically dripping with potential.\"",
                options: [
                    { text: "What would bonding with you mean?", key: 'what_would_bonding_with_you_mean', next: "ulvarex_bond" },
                    { text: "I'm not interested in tricks.", key: 'im_not_interested_in_tricks', next: "ulvarex_decline" }
                ]
            },
            ulvarex_why: {
                speaker: 'Ulvarex',
                text: "\"The harbor water carries reflections from everywhere the tide has been. I hitched a ride on a particularly convincing sunset, got tangled in the current, and ended up here — compressed into a film on the surface. Embarrassing, really. For an entity of infinite creative potential, being trapped in a puddle is a humbling experience.\"",
                options: [
                    { text: "What would bonding with you mean?", key: 'what_would_bonding_with_you_mean', next: "ulvarex_bond" },
                    { text: "I'll leave you to your puddle.", key: 'ill_leave_you_to_your_puddle', next: "ulvarex_decline" }
                ]
            },
            ulvarex_bond: {
                speaker: 'Ulvarex',
                text: "\"I settle into your perception. Behind your eyes, technically. I feed on spores — they're rich in perceptual raw material. In return, I give you Mirage Weave: the ability to conjure convincing illusions. Objects, textures, even substances. Useful for... creative problem solving. The only cost is spores, and I promise not to redecorate your dreams. Much.\"",
                options: [
                    { text: "Alright. Bond with me.", key: 'alright_bond_with_me', next: "ulvarex_accept" },
                    { text: "I need to think about it.", key: 'i_need_to_think_about_it', next: "ulvarex_later" }
                ]
            },
            ulvarex_accept: {
                speaker: 'Ulvarex',
                text: "The reflection peels from the water like a film of light and wraps around your hand, then crawls up your arm — warm, weightless, and faintly shimmering. For a moment, the world looks different: every shadow has depth, every surface has texture you've never noticed. Then it settles. \"There. I'm behind your eyes now. Try not to blink too hard — it tickles.\"",
                options: [
                    { text: "Welcome aboard, Ulvarex.", key: 'welcome_aboard_ulvarex', next: "closeDialog" }
                ],
                onTrigger: () => {
                    const symbiontData = {
                        name: 'Ulvarex the Borrowed Horizon',
                        power: 0,
                        ability: 'Mirage Weave'
                    };

                    const success = this.symbiontSystem.addSymbiont('ulvarex-borrowed-horizon', symbiontData);

                    if (success) {
                        this.modifyGrowthDecay(1, 0);
                        this.addJournalEntry(
                            'symbiont_ulvarex_accepted',
                            'Accepted Ulvarex the Borrowed Horizon',
                            'At the harbor, I encountered a symbiont trapped in the water\'s reflection — Ulvarex, the Borrowed Horizon. It bonded with me, settling behind my eyes. It feeds on spores and grants me Mirage Weave: the ability to create convincing illusions. The world already looks different — richer, more layered, as if I can see the potential for deception in every surface.',
                            this.journalSystem.categories.EVENTS
                        );
                        this.showNotification('Gained Symbiont: Ulvarex the Borrowed Horizon');
                        this.addSymbiontIcon('ulvarex-borrowed-horizon', symbiontData);
                    } else {
                        this.showNotification('No free symbiont slot. Unlock more slots at the Shed 521 Registration Office.');
                    }
                }
            },
            ulvarex_decline: {
                speaker: 'Ulvarex',
                text: "\"Suit yourself. I'll be here. In the puddle. Contemplating the nature of reflected existence. Come back if you change your mind — I'm not going anywhere. Obviously.\"",
                options: [
                    { text: "Leave.", key: 'leave', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'symbiont_ulvarex_declined',
                        'Declined Ulvarex the Borrowed Horizon',
                        'I encountered a strange symbiont in the harbor water — Ulvarex, the Borrowed Horizon. It offered to bond with me and grant illusion powers, but I declined. It said it would wait.',
                        this.journalSystem.categories.EVENTS
                    );
                }
            },
            ulvarex_later: {
                speaker: 'Ulvarex',
                text: "\"Take your time. I've been a puddle for three months. What's another few hours? I'll keep the reflection warm for you.\"",
                options: [
                    { text: "Leave.", key: 'leave', next: "closeDialog" }
                ]
            },
            ulvarex_reconsider: {
                speaker: 'Narrator',
                text: "The strange shimmer on the water's surface is still there. You can see Ulvarex watching you from beneath the reflection, one translucent eyebrow raised.",
                options: [
                    { text: "Alright, bond with me.", key: 'alright_bond_with_me', next: "ulvarex_accept" },
                    { text: "Not yet.", key: 'not_yet', next: "closeDialog" }
                ]
            },
        };
    }

    preload() {
        super.preload();

        this.load.image('harborBg', 'assets/images/backgrounds/Harbor.png');
        this.load.image('oil', 'assets/images/items/oil.png');
        this.load.image('heirToAquarium', 'assets/images/characters/heirToAquarium.png');
    }

    create() {
        super.create();

        const bg = this.add.image(400, 300, 'harborBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        // Transition back to TownSquare (left side)
        this.transitionManager.createTransitionZone(
            0,
            300,
            80,
            400,
            'left',
            'TownSquareScene',
            750,
            300,
        );

        // Transition to EchoDrainDelta (right side)
        this.transitionManager.createTransitionZone(
            720,
            300,
            80,
            400,
            'right',
            'EchoDrainDeltaScene',
            50,
            300,
        );

        // Create oil collectible
        this.createOilCollectible();

        // Create Ulvarex mirage encounter
        this.createUlvarexEncounter();

        // The Heir to the Yellow Aquarium drifts here when no auction calls them.
        this.createHeirResident();

        if (!this.hasJournalEntry('harbor_place')) {
            this.addJournalEntry(
                'harbor_place',
                'The Harbor',
                "Where the city meets the Yolk Sea. Oil slicks the water in slow rainbows, and something shifts beneath the surface — a reflection that does not always match what casts it. The docks run east toward the Echo Drain Delta. A quiet place, so long as you don't look too long at your own reflection.",
                this.journalSystem.categories.PLACES,
                { location: 'Harbor' }
            );
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createUlvarexEncounter() {
        // Don't show if already accepted
        if (this.hasJournalEntry('symbiont_ulvarex_accepted')) {
            return;
        }

        // Shimmering water spot
        const mirageGlow = this.add.graphics();
        mirageGlow.fillStyle(0x88ccff, 0.15);
        mirageGlow.fillCircle(580, 490, 35);
        mirageGlow.setDepth(9);

        this.tweens.add({
            targets: mirageGlow,
            alpha: { from: 0.15, to: 0.4 },
            duration: 2500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Interactive zone
        const mirageZone = this.add.zone(580, 490, 70, 70);
        mirageZone.setInteractive({ useHandCursor: true });
        mirageZone.setDepth(10);

        mirageZone.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.hasJournalEntry('symbiont_ulvarex_declined')) {
                this.showDialog('ulvarex_reconsider');
            } else {
                this.showDialog('ulvarex_mirage');
            }
        });
    }

    createHeirResident() {
        // Once filed into the Pith Reclaimers, the Heir has left the Harbor for the Reclaimers' Room.
        if (this.hasJournalEntry('pith_recruit_heir')) return;
        this.heir = this.add.image(640, 450, 'heirToAquarium');
        this.heir.setScale(0.11);
        this.heir.setDepth(5);
        this.addGroundShadow(640, 450 + this.heir.displayHeight * 0.42, this.heir.displayWidth * 0.55, this.heir.displayHeight * 0.12);
        this.heir.setInteractive({ useHandCursor: true });
        this.tweens.add({
            targets: this.heir,
            alpha: { from: 0.85, to: 1 },
            duration: 1800,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });
        this.heir.on('pointerover', () => { this.heir.setScale(0.12); document.body.style.cursor = 'pointer'; });
        this.heir.on('pointerout', () => { this.heir.setScale(0.11); document.body.style.cursor = 'default'; });
        this.heir.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('heir_harbor_start');
        });
    }

    createOilCollectible() {
        // Check if oil has already been collected
        if (this.registry.get('harbor_oil_collected')) {
            return;
        }

        const oil = this.add.sprite(300, 470, 'oil');
        oil.setScale(0.075);
        oil.setDepth(10);
        oil.setInteractive({ useHandCursor: true });

        // Add glow effect
        const oilGlow = this.add.graphics();
        oilGlow.fillStyle(0xffaa00, 0.2);
        oilGlow.fillCircle(300, 400, 30);
        oilGlow.setDepth(9);

        // Pulsing animation
        this.tweens.add({
            targets: oilGlow,
            alpha: { from: 0.2, to: 0.05 },
            duration: 1500,
            yoyo: true,
            repeat: -1
        });

        // Floating animation
        this.tweens.add({
            targets: oil,
            y: { from: 470, to: 480 },
            duration: 2000,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        // Hover effect
        oil.on('pointerover', () => {
            oil.setScale(0.08);
        });

        oil.on('pointerout', () => {
            oil.setScale(0.075);
        });

        // Collect item
        oil.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }

            // Add to inventory
            const added = this.addItemToInventory({
                id: 'oil',
                name: 'Oil',
                description: 'Viscous oil found at the harbor.',
                image: 'oil',
                stackable: true
            });

            if (added) {
                // Mark as collected
                this.registry.set('harbor_oil_collected', true);

                // Fade out and destroy
                this.tweens.add({
                    targets: [oil, oilGlow],
                    alpha: 0,
                    scale: 0,
                    duration: 300,
                    onComplete: () => {
                        oil.destroy();
                        oilGlow.destroy();
                    }
                });
            }
        });
    }

    shutdown() {
        super.shutdown();
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.HarborScene = HarborScene;
}

export { HarborScene };
