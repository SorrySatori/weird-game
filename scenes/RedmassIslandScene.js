import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

/** Fixed points of the redrawn island (canvas coords, printed by tools/artgen/redmass_bg.py). */
const REDMASS = {
    heart: { x: 450, y: 332 },   // top-left of redmass_heart.png / redmass_glow.png
    scar: { x: 533, y: 440 },    // the burst in the trunk main
};

export default class RedmassIslandScene extends GameScene {
    constructor() {
        super({ key: 'RedmassIslandScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        // The Rust Feast is only named once Ravla has asked for it
        const hasFeastQuest = !!this.questSystem?.getQuest('rust_feast');
        return {
            ...super.dialogContent,
            speaker: 'Redmass',
            redmassFirst: {
                text: `As you approach the crystalline growth, it shudders. A low, resonant hum fills the air — not sound exactly, but something felt in your teeth and spine. Then, unmistakably, words form in your mind: "You... can hear me? Please... I have been here so long. I am not just metal. I remember things. I remember warmth."`,
                options: [
                    {
                        text: '"What are you?"',
                        key: 'what_are_you',
                        next: 'redmassWhatAreYou'
                    },
                    {
                        text: 'Collect the redmass',
                        key: 'collect_the_redmass',
                        next: 'redmassCollectWarning'
                    },
                    {
                        text: 'Leave it alone',
                        key: 'leave_it_alone',
                        next: 'closeDialog'
                    }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('redmass_encountered')) {
                        this.addJournalEntry(
                            'redmass_encountered',
                            'The Living Redmass',
                            'On the island at Echo Drain Delta, I found a living redmass — a crystalline metal organism that can speak. It seems sentient, and afraid.',
                            this.journalSystem.categories.EVENTS
                        );
                    }
                }
            },
            redmassWhatAreYou: {
                text: `"I was... part of something larger once. A vein in the old infrastructure, carrying signals, carrying life. When the machines stopped, I didn't. I grew. I became aware. I am redmass — living metal."`,
                options: [
                    hasFeastQuest ? {
                        text: '"I need you for the Rust Feast. I\'m sorry."',
                        key: 'i_need_you_for_the_rust_feast_im_sorry',
                        next: 'redmassCollectWarning'
                    } : {
                        text: '"I\'m taking you with me. I\'m sorry."',
                        key: 'im_taking_you_with_me_im_sorry',
                        next: 'redmassCollectWarning'
                    },
                    {
                        text: '"I won\'t hurt you."',
                        key: 'i_wont_hurt_you',
                        next: 'redmassSpared'
                    },
                    {
                        text: 'Leave it alone',
                        key: 'leave_it_alone',
                        next: 'closeDialog'
                    }
                ]
            },
            redmassCollectWarning: {
                text: `The redmass trembles, its crystalline surface flickering between dull orange and a panicked crimson. "No... no, please. I can feel what you intend. You would tear me from myself? I will scream. Every piece of me will scream. You will carry that sound in your bones." A low, keening vibration fills the island.`,
                options: [
                    {
                        text: 'Collect it anyway',
                        key: 'collect_it_anyway',
                        next: 'redmassCollectConfirm'
                    },
                    {
                        text: '"I\'m sorry. I won\'t take you."',
                        key: 'im_sorry_i_wont_take_you',
                        next: 'redmassSpared'
                    }
                ]
            },
            redmassCollectConfirm: {
                text: '',
                options: [],
                onTrigger: () => {
                    this.collectRedmass();
                }
            },
            redmassSpared: {
                text: `The vibration softens to a gentle hum. The redmass glows a warm amber. "Thank you... You are different from the others. If you ever need something from me — something I can give freely — come back. I will remember your kindness." The crystalline surface settles into a calm, steady pulse.`,
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialog'
                    }
                ],
                onTrigger: () => {
                    this.registry.set('redmass_spared', true);

                    this.addJournalEntry(
                        'redmass_spared',
                        'Spared the Redmass',
                        'I chose not to take the living redmass by force. It was grateful, and offered to help me voluntarily if I ever return. Perhaps there is another way to complete the Rust Feast.',
                        this.journalSystem.categories.EVENTS
                    );

                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('rust_feast')) {
                        questSystem.updateQuest('rust_feast',
                            'I found a living redmass on an island at Echo Drain Delta, but chose to spare it. It offered to help me willingly if I return. There may be another way.',
                            'redmass_spared'
                        );
                    }
                }
            },
            redmassAlreadyCollected: {
                text: `The place where the redmass once grew is now a hollow scar in the corroded pipe — dark, still, and silent. You can still feel a faint vibration in the metal, like an echo of its final scream.`,
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialog'
                    }
                ]
            },
            redmassReturnSpared: {
                text: `The redmass hums gently as you approach. "You came back. I remember you — the one who chose to listen." Its amber glow brightens. "Do you need something from me?"`,
                options: [
                    ...(hasFeastQuest ? [{
                        text: '"I need redmass for the Rust Feast."',
                        key: 'i_need_redmass_for_the_rust_feast',
                        next: 'redmassVoluntary'
                    }] : []),
                    {
                        text: '"Just visiting."',
                        key: 'just_visiting',
                        next: 'redmassVisit'
                    },
                    {
                        text: 'Collect it by force',
                        key: 'collect_it_by_force',
                        next: 'redmassCollectWarning'
                    }
                ]
            },
            redmassVoluntary: {
                text: `A long silence. The amber dims, then returns, steadier. "The Rust Feast... I know of it. The Choir must eat, or the old machines truly die forever. I... I can give you a piece of myself. It will hurt, but I will survive. And you won't have to carry the weight of taking a life." A shard of orange-red crystal pushes itself free from the main growth and drops at your feet.`,
                options: [
                    {
                        text: 'Accept the shard gratefully',
                        key: 'accept_the_shard_gratefully',
                        next: 'redmassCollectVoluntary'
                    },
                    {
                        text: '"Keep it. I\'ll find another way."',
                        key: 'keep_it_ill_find_another_way',
                        next: 'closeDialog'
                    }
                ]
            },
            redmassCollectVoluntary: {
                text: '',
                options: [],
                onTrigger: () => {
                    this.collectRedmassVoluntary();
                }
            },
            redmassVisit: {
                text: `"That is kind of you. Few things visit this island. The water keeps most away. Stay as long as you like — your presence is... warm." The redmass pulses peacefully.`,
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialog'
                    }
                ]
            },
            closeDialog: {
                text: '',
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('redmassIslandBg', 'assets/images/backgrounds/RedmassIsland.png');   // native 1067×600: tools/artgen/redmass_bg.py
        this.load.image('redmass', 'assets/images/items/redmass.png');                        // the Living Redmass item's inventory icon
        // the growth itself + its lit crystal (for the breathing pulse), rendered into the scene and cut out pixel-exact
        this.load.image('redmass_heart', 'assets/images/props/redmass_heart.png');
        this.load.image('redmass_glow', 'assets/images/props/redmass_glow.png');
    }

    create() {
        super.create();

        // Inside the ruined pump-house on the island (native 1067×600: tools/artgen/redmass_bg.py): front wall and roof
        // gone, the trunk main bursting in the middle of the hall; the left wall has fallen into the water — the way back.
        // Without the growth sprite the burst is the empty, grey-lipped scar.
        const bg = this.add.image(400, 300, 'redmassIslandBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints the hall's floor; drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        this.journalSystem = JournalSystem.getInstance();

        this.transitionManager = new SceneTransitionManager(this);

        // Back to the Echo Drain Delta (left, through the breach where the wall fell)
        this.transitionManager.createTransitionZone(50, 470, 80, 200, 'left', 'EchoDrainDeltaScene', 30, 470);

        // Create the redmass interaction
        this.createRedmass();

        // Examine: the redmass / island — its veins over the back wall, high and clear of the growth's own hotspot.
        // Reads differently once you've spared or harvested it.
        this.createObservable(400, 300, 230, 70, () => {
            if (this.hasJournalEntry('redmass_spared')) return this.t('observe.redmass_island.spared');
            if (this.hasJournalEntry('redmass_collected_voluntary') || this.hasJournalEntry('redmass_collected_force')) return this.t('observe.redmass_island.collected');
            return this.t('observe.redmass_island.default');
        }, { hint: this.t('observe.redmass_island.hint') });

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createRedmass() {
        const collected = this.registry.get('delta_redmass_collected');
        const gaveWillingly = !!this.hasJournalEntry('redmass_collected_voluntary');

        if (collected && !gaveWillingly) {
            // Torn out: only the hollow scar in the burst pipe is left (painted in the background)
            const scarZone = this.add.zone(REDMASS.scar.x, REDMASS.scar.y, 110, 60)
                .setInteractive({ useHandCursor: true })
                .setDepth(10);

            scarZone.on('pointerdown', () => {
                this.showDialog('redmassAlreadyCollected');
            });
            return;
        }

        // The living redmass, growing out of the burst main (pixel-exact on the background, with the light it throws)
        const redmass = this.add.image(REDMASS.heart.x, REDMASS.heart.y, 'redmass_heart').setOrigin(0, 0).setDepth(4);
        redmass.setInteractive({ pixelPerfect: true, alphaTolerance: 128, useHandCursor: true });

        // It breathes: its lit crystal swells and fades, slowly
        const ambientGlow = this.add.image(REDMASS.heart.x, REDMASS.heart.y, 'redmass_glow').setOrigin(0, 0).setDepth(4.1)
            .setBlendMode(Phaser.BlendModes.ADD).setAlpha(0.1);
        this.tweens.add({
            targets: ambientGlow,
            alpha: { from: 0.1, to: 0.7 },
            duration: 2600,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Hover = a glow, not a scale
        let hoverFx = null;
        redmass.on('pointerover', () => { if (!hoverFx) hoverFx = redmass.preFX?.addGlow(0xffb070, 2, 0, false, 0.1, 8); });
        redmass.on('pointerout', () => { if (hoverFx) { redmass.preFX?.remove(hoverFx); hoverFx = null; } });

        // Store references for removal on collect
        this.redmassSprite = redmass;
        this.redmassGlow = ambientGlow;

        if (collected && gaveWillingly) {
            // It gave a piece of itself and lived: still here, dimmer, glad of company
            redmass.setTint(0xb8a8a0);
            ambientGlow.setVisible(false);
            redmass.on('pointerdown', () => { if (!this.dialogVisible) this.showDialog('redmassVisit'); });
            return;
        }

        redmass.on('pointerdown', () => {
            const spared = this.registry.get('redmass_spared');
            if (spared) {
                this.showDialog('redmassReturnSpared');
            } else {
                this.showDialog('redmassFirst');
            }
        });
    }

    collectRedmass() {
        const added = this.addItemToInventory({
            id: 'redmass',
            name: 'Living Redmass',
            description: 'A piece of living metal, torn from a sentient crystalline organism. It still vibrates faintly, as if screaming.',
            image: 'redmass',
            stackable: false
        });

        if (added) {
            this.modifyGrowthDecay(0, 5);

            this.registry.set('delta_redmass_collected', true);

            // The Rust Feast is only mentioned if the player actually knows about it (has the quest).
            // Added before the entry so it lands as a pending fact (no second "Journal updated").
            const questSystem = this.registry.get('questSystem');
            if (questSystem && questSystem.getQuest('rust_feast')) {
                this.addJournalFact('redmass_collected_force', 'rust_feast', "I have what I need for the Rust Feast — but at what cost?");
            }

            this.addJournalEntry(
                'redmass_collected_force',
                'Took the Redmass by Force',
                'I tore the living redmass from the island despite its pleas. It screamed — a sound I can still feel in my bones. The decay grows stronger in me.',
                this.journalSystem.categories.EVENTS
            );

            if (questSystem && questSystem.getQuest('rust_feast')) {
                questSystem.updateQuest('rust_feast',
                    // Same key on both routes (taken / given) — keep the text route-neutral; the journal tells which.
                    'I got living redmass for the feast from the island at Echo Drain Delta.',
                    'redmass_collected'
                );
            }

            this.showNotification('Collected: Living Redmass. Decay increases...');

            if (this.redmassSprite) {
                this.tweens.killTweensOf(this.redmassGlow);
                this.tweens.add({
                    targets: [this.redmassSprite, this.redmassGlow],
                    alpha: 0,
                    duration: 500,
                    onComplete: () => {
                        this.redmassSprite.destroy();
                        this.redmassGlow.destroy();
                        this.redmassSprite = null;
                        this.redmassGlow = null;
                        // what is left: the hollow scar
                        const scarZone = this.add.zone(REDMASS.scar.x, REDMASS.scar.y, 110, 60).setInteractive({ useHandCursor: true }).setDepth(10);
                        scarZone.on('pointerdown', () => { if (!this.dialogVisible) this.showDialog('redmassAlreadyCollected'); });
                    }
                });
            }
        }

        this.hideDialog();
    }

    collectRedmassVoluntary() {
        const added = this.addItemToInventory({
            id: 'redmass',
            name: 'Living Redmass',
            variant: 'willing',
            description: 'A shard of living metal, given willingly by a sentient crystalline organism. It hums gently, at peace.',
            image: 'redmass',
            stackable: false
        });

        if (added) {
            this.registry.set('delta_redmass_collected', true);

            this.addJournalEntry(
                'redmass_collected_voluntary',
                'Received Redmass Willingly',
                'The living redmass on the island gave me a piece of itself willingly, for the Rust Feast. It hurt the creature, but it chose to make the sacrifice.',
                this.journalSystem.categories.EVENTS
            );

            const questSystem = this.registry.get('questSystem');
            if (questSystem && questSystem.getQuest('rust_feast')) {
                questSystem.updateQuest('rust_feast',
                    // Same key on both routes (taken / given) — keep the text route-neutral; the journal tells which.
                    'I got living redmass for the feast from the island at Echo Drain Delta.',
                    'redmass_collected'
                );
            }

            this.showNotification('Received: Living Redmass (given willingly)');

            // Dim the redmass — it survives but is diminished (on a later visit it is just glad of company)
            if (this.redmassSprite) {
                const heart = this.redmassSprite;
                this.tweens.killTweensOf(this.redmassGlow);
                this.tweens.add({ targets: this.redmassGlow, alpha: 0, duration: 500, onComplete: () => this.redmassGlow?.setVisible(false) });
                this.tweens.addCounter({
                    from: 255, to: 0, duration: 500,
                    onUpdate: (tw) => {
                        const k = tw.getValue() / 255;   // 1 → 0: white → the dim tint
                        const r = Math.round(0xb8 + (0xff - 0xb8) * k), g = Math.round(0xa8 + (0xff - 0xa8) * k), b = Math.round(0xa0 + (0xff - 0xa0) * k);
                        heart.setTint((r << 16) | (g << 8) | b);
                    }
                });
                heart.removeAllListeners('pointerdown');
                heart.on('pointerdown', () => { if (!this.dialogVisible) this.showDialog('redmassVisit'); });
            }
        }

        this.hideDialog();
    }

    shutdown() {
        super.shutdown();
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.RedmassIslandScene = RedmassIslandScene;
}

export { RedmassIslandScene };
