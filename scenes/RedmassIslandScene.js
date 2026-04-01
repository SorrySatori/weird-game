import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class RedmassIslandScene extends GameScene {
    constructor() {
        super({ key: 'RedmassIslandScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
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
                    {
                        text: '"I need you for the Rust Feast. I\'m sorry."',
                        key: 'i_need_you_for_the_rust_feast_im_sorry',
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
                    {
                        text: '"I need redmass for the Rust Feast."',
                        key: 'i_need_redmass_for_the_rust_feast',
                        next: 'redmassVoluntary'
                    },
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
        this.load.image('redmassIslandBg', 'assets/images/backgrounds/RedmassIsland.png');
        this.load.image('redmass', 'assets/images/items/redmass.png');
    }

    create() {
        super.create();

        const bg = this.add.image(400, 300, 'redmassIslandBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.journalSystem = JournalSystem.getInstance();

        this.transitionManager = new SceneTransitionManager(this);

        // Transition back to Echo Drain Delta
        this.transitionManager.createTransitionZone(
            0,
            400,
            80,
            300,
            'left',
            'EchoDrainDeltaScene',
            620,
            380
        );

        // Create the redmass interaction
        this.createRedmass();

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createRedmass() {
        const collected = this.registry.get('delta_redmass_collected');

        if (collected) {
            // Show empty spot where redmass was — just an interactive zone
            const scarZone = this.add.zone(400, 350, 60, 60)
                .setInteractive({ useHandCursor: true })
                .setDepth(10);

            scarZone.on('pointerdown', () => {
                this.showDialog('redmassAlreadyCollected');
            });
            return;
        }

        // The living redmass — using the actual redmass sprite
        const redmass = this.add.sprite(400, 350, 'redmass');
        redmass.setScale(0.15);
        redmass.setDepth(10);
        redmass.setInteractive({ useHandCursor: true });

        // Ambient glow around the redmass
        const ambientGlow = this.add.graphics();
        ambientGlow.fillStyle(0xff4400, 0.15);
        ambientGlow.fillCircle(400, 350, 50);
        ambientGlow.setDepth(9);

        this.tweens.add({
            targets: ambientGlow,
            alpha: { from: 0.1, to: 0.3 },
            duration: 2500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Hover effect
        redmass.on('pointerover', () => {
            redmass.setScale(0.18);
        });

        redmass.on('pointerout', () => {
            redmass.setScale(0.15);
        });

        // Store references for removal on collect
        this.redmassSprite = redmass;
        this.redmassGlow = ambientGlow;

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
            this.modifyGrowthDecay(0, 10);

            this.registry.set('delta_redmass_collected', true);

            this.addJournalEntry(
                'redmass_collected_force',
                'Took the Redmass by Force',
                'I tore the living redmass from the island despite its pleas. It screamed — a sound I can still feel in my bones. The decay grows stronger in me. I have what I need for the Rust Feast, but at what cost?',
                this.journalSystem.categories.EVENTS
            );

            const questSystem = this.registry.get('questSystem');
            if (questSystem && questSystem.getQuest('rust_feast')) {
                questSystem.updateQuest('rust_feast',
                    'I collected the living redmass from the island at Echo Drain Delta. It begged me to stop, but I took it anyway. The Rust Choir will have their feast.',
                    'redmass_collected'
                );
            }

            this.showNotification('Collected: Living Redmass. Decay increases...');

            if (this.redmassSprite) {
                this.tweens.add({
                    targets: [this.redmassSprite, this.redmassGlow],
                    alpha: 0,
                    duration: 500,
                    onComplete: () => {
                        this.redmassSprite.destroy();
                        this.redmassGlow.destroy();
                        this.redmassSprite = null;
                        this.redmassGlow = null;
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
                    'The living redmass gave me a shard of itself willingly. The Rust Choir will have their feast — and I carry no guilt for it.',
                    'redmass_collected'
                );
            }

            this.showNotification('Received: Living Redmass (given willingly)');

            // Shrink the redmass — it survives but is diminished
            if (this.redmassSprite) {
                this.tweens.add({
                    targets: this.redmassSprite,
                    scaleX: 0.08,
                    scaleY: 0.08,
                    alpha: 0.5,
                    duration: 500
                });
                this.tweens.add({
                    targets: this.redmassGlow,
                    alpha: 0.05,
                    duration: 500,
                    onComplete: () => {
                        // Disable further interaction
                        this.redmassSprite.disableInteractive();
                    }
                });
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
