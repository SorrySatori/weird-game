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
        return {
            ...super.dialogContent,

            // Ulvarex the Borrowed Horizon encounter
            ulvarex_mirage: {
                speaker: 'Narrator',
                text: "The water at the dock's edge shimmers oddly — not with reflected light, but with something underneath it. A shape moves below the surface that doesn't match anything above. A face, perhaps. Or the memory of a face.",
                options: [
                    { text: "Reach toward the water.", next: "ulvarex_reach" },
                    { text: "Step back.", next: "closeDialog" }
                ]
            },
            ulvarex_reach: {
                speaker: 'Ulvarex',
                text: "The moment your fingers touch the surface, the reflection rearranges itself. A voice arrives — not through your ears but through your optic nerve, as if the words are made of light. \"Oh, finally. Someone who looks at mirages instead of through them. I've been folded into this puddle for... well, time doesn't move the same way when you're two-dimensional.\"",
                options: [
                    { text: "What are you?", next: "ulvarex_what" },
                    { text: "Why were you in the water?", next: "ulvarex_why" }
                ]
            },
            ulvarex_what: {
                speaker: 'Ulvarex',
                text: "\"I am Ulvarex, the Borrowed Horizon. A symbiont of perception. I exist in the gap between what is seen and what is understood. I can weave mirages — illusions convincing enough to fool the hand as well as the eye. But I need a host. Someone with enough spore-matter to serve as my canvas. You, for instance. You're practically dripping with potential.\"",
                options: [
                    { text: "What would bonding with you mean?", next: "ulvarex_bond" },
                    { text: "I'm not interested in tricks.", next: "ulvarex_decline" }
                ]
            },
            ulvarex_why: {
                speaker: 'Ulvarex',
                text: "\"The harbor water carries reflections from everywhere the tide has been. I hitched a ride on a particularly convincing sunset, got tangled in the current, and ended up here — compressed into a film on the surface. Embarrassing, really. For an entity of infinite creative potential, being trapped in a puddle is a humbling experience.\"",
                options: [
                    { text: "What would bonding with you mean?", next: "ulvarex_bond" },
                    { text: "I'll leave you to your puddle.", next: "ulvarex_decline" }
                ]
            },
            ulvarex_bond: {
                speaker: 'Ulvarex',
                text: "\"I settle into your perception. Behind your eyes, technically. I feed on spores — they're rich in perceptual raw material. In return, I give you Mirage Weave: the ability to conjure convincing illusions. Objects, textures, even substances. Useful for... creative problem solving. The only cost is spores, and I promise not to redecorate your dreams. Much.\"",
                options: [
                    { text: "Alright. Bond with me.", next: "ulvarex_accept" },
                    { text: "I need to think about it.", next: "ulvarex_later" }
                ]
            },
            ulvarex_accept: {
                speaker: 'Ulvarex',
                text: "The reflection peels from the water like a film of light and wraps around your hand, then crawls up your arm — warm, weightless, and faintly shimmering. For a moment, the world looks different: every shadow has depth, every surface has texture you've never noticed. Then it settles. \"There. I'm behind your eyes now. Try not to blink too hard — it tickles.\"",
                options: [
                    { text: "Welcome aboard, Ulvarex.", next: "closeDialog" }
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
                    { text: "Leave.", next: "closeDialog" }
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
                    { text: "Leave.", next: "closeDialog" }
                ]
            },
            ulvarex_reconsider: {
                speaker: 'Narrator',
                text: "The strange shimmer on the water's surface is still there. You can see Ulvarex watching you from beneath the reflection, one translucent eyebrow raised.",
                options: [
                    { text: "Alright, bond with me.", next: "ulvarex_accept" },
                    { text: "Not yet.", next: "closeDialog" }
                ]
            },
        };
    }

    preload() {
        super.preload();

        this.load.image('harborBg', 'assets/images/backgrounds/Harbor.png');
        this.load.image('oil', 'assets/images/items/oil.png');
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
