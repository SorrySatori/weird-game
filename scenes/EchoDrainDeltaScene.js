import GameScene from './GameScene.js'
import SceneTransitionManager from '../utils/SceneTransitionManager.js'
import JournalSystem from '../systems/JournalSystem.js'

export default class EchoDrainDeltaScene extends GameScene {
    constructor() {
        super({ key: 'EchoDrainDeltaScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            speaker: 'Narrator',
            sporePlantPrompt: {
                text: `The murky water between the islands teems with something alive — dark currents that swallow anything that touches the surface. But you notice a patch of exposed sediment on the near bank, soft and porous. It could serve as fertile ground for your spores. Planting them here might grow a fungal bridge to the distant island, where you can see a ruined building with faint orange-red crystalline growths pulsing through its pipes.`,
                options: [
                    {
                        text: 'Plant spores (costs 15 spores)',
                        next: 'sporePlantConfirm'
                    },
                    {
                        text: 'Not now',
                        next: 'closeDialog'
                    }
                ]
            },
            sporePlantConfirm: {
                text: '',
                options: [],
                onTrigger: () => {
                    const currentSpores = this.getSporeLevel();
                    if (currentSpores < 15) {
                        this.showNotification('Not enough spores! You need at least 15.');
                        this.hideDialog();
                        return;
                    }

                    this.modifySpores(-15);
                    this.modifyGrowthDecay(3, 0);
                    this.registry.set('delta_fungal_bridge_grown', true);

                    this.addJournalEntry(
                        'delta_fungal_bridge',
                        'Fungal Bridge at Echo Drain Delta',
                        'I planted spores in the sediment between the delta islands. A living fungal bridge grew across the toxic water, connecting me to a distant island with a ruined building covered in strange orange-red crystalline growths. The redmass...',
                        this.journalSystem.categories.EVENTS
                    );

                    this.showNotification('Spores take root... a fungal bridge stretches across the water.');
                    this.createFungalBridge();
                    this.hideDialog();
                }
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

        this.load.image('echoDrainDeltaBg', 'assets/images/backgrounds/EchoDrainDelta.png');
        this.load.image('metal_scrap', 'assets/images/items/metal_scrap.png');
    }

    create() {
        super.create();

        const bg = this.add.image(400, 300, 'echoDrainDeltaBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.journalSystem = JournalSystem.getInstance();

        this.transitionManager = new SceneTransitionManager(this);

        // Transition back to Harbor (left side)
        this.transitionManager.createTransitionZone(
            0,
            300,
            80,
            400,
            'left',
            'HarborScene',
            750,
            300,
        );

        // Create metal scrap collectible
        this.createMetalScrapCollectible();

        // Create the spore planting spot (or fungal bridge if already grown)
        if (this.registry.get('delta_fungal_bridge_grown')) {
            this.createFungalBridge();
        } else {
            this.createSporePlantSpot();
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createSporePlantSpot() {
        // The planting spot near the water's edge, toward the far island
        const plantGlow = this.add.graphics();
        plantGlow.fillStyle(0x7fff8e, 0.15);
        plantGlow.fillCircle(620, 380, 25);
        plantGlow.setDepth(6);

        this.tweens.add({
            targets: plantGlow,
            alpha: { from: 0.15, to: 0.35 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Invisible interactive zone over the spot
        const plantZone = this.add.zone(620, 380, 50, 50)
            .setInteractive({ useHandCursor: true })
            .setDepth(7);

        plantZone.on('pointerdown', () => {
            this.showDialog('sporePlantPrompt');
        });

        // Store references for cleanup after bridge grows
        this.sporePlantSpot = { plantGlow, plantZone };
    }

    createFungalBridge() {
        // Remove planting spot visuals if they exist
        if (this.sporePlantSpot) {
            this.sporePlantSpot.plantGlow.destroy();
            this.sporePlantSpot.plantZone.destroy();
            this.sporePlantSpot = null;
        }

        // Draw the fungal bridge — luminescent mycelium stretching across the water
        const bridge = this.add.graphics();
        bridge.lineStyle(6, 0x4aff6e, 0.7);
        bridge.beginPath();
        bridge.moveTo(620, 390);
        bridge.lineTo(650, 350);
        bridge.lineTo(680, 310);
        bridge.lineTo(710, 270);
        bridge.lineTo(730, 240);
        bridge.strokePath();

        // Thicker organic base
        bridge.lineStyle(10, 0x2a7a3a, 0.5);
        bridge.beginPath();
        bridge.moveTo(622, 392);
        bridge.lineTo(652, 352);
        bridge.lineTo(682, 312);
        bridge.lineTo(712, 272);
        bridge.lineTo(732, 242);
        bridge.strokePath();
        bridge.setDepth(5);

        // Spore particles along the bridge
        const particlePositions = [
            { x: 650, y: 350 }, { x: 680, y: 310 },
            { x: 710, y: 270 }
        ];
        particlePositions.forEach(pos => {
            const particle = this.add.graphics();
            particle.fillStyle(0x7fff8e, 0.4);
            particle.fillCircle(pos.x, pos.y, 5);
            particle.setDepth(6);

            this.tweens.add({
                targets: particle,
                alpha: { from: 0.2, to: 0.6 },
                duration: 1000 + Math.random() * 1000,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        });

        // Transition zone at the far end of the bridge — toward the island building
        this.transitionManager.createTransitionZone(
            700,
            220,
            100,
            80,
            'right',
            'RedmassIslandScene',
            100,
            450
        );
    }

    createMetalScrapCollectible() {
        // Check if metal scrap has already been collected
        if (this.registry.get('delta_metal_scrap_collected')) {
            return;
        }

        const metalScrap = this.add.sprite(500, 450, 'metal_scrap');
        metalScrap.setScale(0.05);
        metalScrap.setDepth(10);
        metalScrap.setInteractive({ useHandCursor: true });

        // Add glow effect
        const scrapGlow = this.add.graphics();
        scrapGlow.fillStyle(0xc0c0c0, 0.2);
        scrapGlow.fillCircle(500, 350, 30);
        scrapGlow.setDepth(9);

        // Pulsing animation
        this.tweens.add({
            targets: scrapGlow,
            alpha: { from: 0.2, to: 0.05 },
            duration: 1500,
            yoyo: true,
            repeat: -1
        });

        // Hover effect
        metalScrap.on('pointerover', () => {
            metalScrap.setScale(0.07);
        });

        metalScrap.on('pointerout', () => {
            metalScrap.setScale(0.05);
        });

        // Collect item
        metalScrap.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }

            // Add to inventory
            const added = this.addItemToInventory({
                id: 'metal_scrap',
                name: 'Metal Scrap',
                description: 'Rusty metal fragments found in the delta.',
                image: 'metal_scrap',
                stackable: true
            });

            if (added) {
                // Mark as collected
                this.registry.set('delta_metal_scrap_collected', true);

                // Fade out and destroy
                this.tweens.add({
                    targets: [metalScrap, scrapGlow],
                    alpha: 0,
                    scale: 0,
                    duration: 300,
                    onComplete: () => {
                        metalScrap.destroy();
                        scrapGlow.destroy();
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
    window.EchoDrainDeltaScene = EchoDrainDeltaScene;
}

export { EchoDrainDeltaScene };
