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
        const hasPalinode = !!this.symbiontSystem?.hasSymbiont('palinode');
        const hasFreeSlot = !!this.symbiontSystem && this.symbiontSystem.symbionts.size < this.symbiontSystem.unlockedSlots;
        const crossed = !!(this.registry.get('delta_fungal_bridge_grown') || this.registry.get('delta_seam_opened'));
        return {
            ...super.dialogContent,
            speaker: 'Narrator',
            sporePlantPrompt: {
                text: `The murky water between the islands teems with something alive — dark currents that swallow anything that touches the surface. But you notice a patch of exposed sediment on the near bank, soft and porous. It could serve as fertile ground for your spores. Planting them here might grow a fungal bridge to the distant island, where you can see a ruined building with faint orange-red crystalline growths pulsing through its pipes.`,
                options: [
                    {
                        text: 'Plant spores (costs 15 spores)',
                        key: 'plant_spores_costs_15_spores',
                        next: 'sporePlantConfirm'
                    },
                    ...(hasPalinode && !crossed ? [{
                        text: '[Seam-Sense] Feel for a hidden way across.',
                        key: 'seam_sense_cross',
                        next: 'seamCrossConfirm'
                    }] : []),
                    {
                        text: 'Not now',
                        key: 'not_now',
                        next: 'closeDialog'
                    }
                ]
            },
            seamCrossConfirm: {
                speaker: 'Palinode',
                text: `Palinode stirs, and the drowned world tilts. Where you saw only black water, you now feel the *seam* — a spit of half-sunk ruin the current has been pretending isn't there, a threshold the delta unsaid to itself long ago. "No spores," Palinode murmurs. "No bridge. Only a 'for now' that forgot it was temporary. Walk. I'll hold it open."`,
                options: [
                    { text: 'Cross by the seam.', key: 'cross_by_the_seam', next: 'closeDialog', onSelect: () => this.openSeamCrossing() }
                ]
            },

            // --- Palinode, the unsaying: a neutral traversal symbiont found in the delta's seams. ---
            palinode_offer: {
                speaker: 'Palinode',
                text: `Among the porous ruins something catches your eye that shouldn't: a shimmer that is not water and not light — a gap wearing the shape of solid stone. When you look straight at it, it apologizes, and rearranges into a voice already halfway through retracting itself:\n\n"You noticed. Almost no one notices. I am Palinode — the unsaying. This whole delta is seams; I have lived in the space between what was sealed and what leaked. The living have their readers; the dead have theirs. No one keeps the one who finds the way through. Carry me, and no wall will be the last word."`,
                options: [
                    ...(hasFreeSlot
                        ? [{ text: 'Bond with it. (take Palinode)', key: 'palinode_bond', next: 'palinode_accept' }]
                        : [{ text: 'I have no room to carry it.', key: 'palinode_no_room', next: 'palinode_no_slot' }]),
                    { text: 'What are you, exactly?', key: 'palinode_what', next: 'palinode_about' },
                    { text: 'Leave it in the ruins.', key: 'palinode_leave', next: 'closeDialog' }
                ]
            },
            palinode_about: {
                speaker: 'Palinode',
                text: `"A palinode is a poem that takes back an earlier poem. That is my whole nature: I unsay walls. Sealed doors, bricked passages, the honest draft under a false floor — I feel the seam and persuade the gap to widen. I care nothing for your growth or your rot; I feed on spores and on the simple fact that nothing stays shut forever. Neme reads the living, the mourner reads the dead — I read the way out."`,
                options: [
                    { text: 'Back.', key: 'palinode_about_back', next: 'palinode_offer' }
                ]
            },
            palinode_no_slot: {
                speaker: 'Palinode',
                text: `The shimmer thins, almost amused. "Full already? A pity — you of all people should keep room for an exit. Make some: the shape-clerks at the Shed register vessels, and the rust-folk weld them. Then come back. I am a seam. I am not going anywhere the water can reach."`,
                options: [
                    { text: "I'll come back.", key: 'palinode_no_slot_back', next: 'closeDialog' }
                ]
            },
            palinode_accept: {
                speaker: 'Palinode',
                text: `You reach into the gap that pretends to be stone. It gives — of course it gives — and threads into you along every joint and seam of your body, a second sense that always points toward the way through.\n\n"There. Now you will never quite believe a wall again. Good. Neither do I."`,
                onTrigger: () => this.bondPalinode(),
                options: [
                    { text: 'Understood.', key: 'palinode_accept_ok', next: 'closeDialog' }
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

                    this.showNotification('Spores take root... a small fungal island stretches across the water.');
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
        this.load.image('bridge', 'assets/images/items/bridge.png');
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

        // Create the crossing: fungal bridge, Palinode seam, or the planting spot.
        if (this.registry.get('delta_fungal_bridge_grown')) {
            this.createFungalBridge();
        } else if (this.registry.get('delta_seam_opened')) {
            this.createSeamCrossing();
        } else {
            this.createSporePlantSpot();
        }

        // Palinode waits in the delta's seams until it has bonded.
        this.createPalinodeSpot();

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

        // Place the bridge sprite across the water, connecting mainland to island
        const bridgeSprite = this.add.image(600, 430, 'bridge');
        bridgeSprite.setDepth(-0.5);
        bridgeSprite.setScale(0.16);

        // Transition zone at the far end of the bridge — toward the island building
        this.transitionManager.createTransitionZone(
            700,
            320,
            100,
            80,
            'right',
            'RedmassIslandScene',
            100,
            450
        );
    }

    /** Palinode's alternative crossing — a hidden seam, no spore cost, no fungal bridge. */
    openSeamCrossing() {
        this.registry.set('delta_seam_opened', true);
        if (!this.hasJournalEntry('delta_seam_crossing')) {
            this.addJournalEntry(
                'delta_seam_crossing',
                'A Seam Across the Delta',
                'With Palinode I felt the seam the dark water hides — a spit of half-sunk ruin the current pretends isn\'t there. No spores, no fungal bridge: I simply unsaid the gap and walked. The way to the island stands open.',
                this.journalSystem.categories.EVENTS,
                { location: 'Echo Drain Delta', via: 'palinode' }
            );
        }
        if (this.sporePlantSpot) {
            this.sporePlantSpot.plantGlow.destroy();
            this.sporePlantSpot.plantZone.destroy();
            this.sporePlantSpot = null;
        }
        this.createSeamCrossing();
    }

    createSeamCrossing() {
        // A faint shimmer over the half-sunk ruin instead of a fungal bridge.
        const shimmer = this.add.graphics().setDepth(-0.5);
        shimmer.fillStyle(0xbfe6c8, 0.10);
        shimmer.fillRect(560, 410, 210, 34);
        this.transitionManager.createTransitionZone(
            700, 320, 100, 80, 'right', 'RedmassIslandScene', 100, 450
        );
    }

    /** The seam where Palinode waits — a gap wearing the shape of stone. */
    createPalinodeSpot() {
        if (this.symbiontSystem?.hasSymbiont('palinode')) return;
        const cx = 150, cy = 330;
        const glint = this.add.graphics().setDepth(6);
        glint.fillStyle(0xbfe6c8, 0.14);
        glint.fillCircle(cx, cy, 22);
        this.tweens.add({ targets: glint, alpha: { from: 0.14, to: 0.4 }, duration: 1600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        const label = this.add.text(cx, cy - 40, 'A SEAM IN THE RUIN', {
            fontSize: '12px', fill: '#cde6d6', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 }
        }).setOrigin(0.5).setDepth(8).setVisible(false);
        const zone = this.add.zone(cx - 30, cy - 45, 60, 90).setOrigin(0, 0);
        zone.setInteractive({ hitArea: new Phaser.Geom.Rectangle(0, 0, 60, 90), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
        zone.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
        zone.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
        zone.on('pointerdown', () => { if (this.dialogVisible) return; if (this.clickSound) this.clickSound.play(); this.showDialog('palinode_offer'); });
    }

    /** Bond the Palinode symbiont (Seam-Sense). */
    bondPalinode() {
        if (this.symbiontSystem?.hasSymbiont('palinode')) return;
        const data = { name: 'Palinode', power: 0, ability: 'Seam-Sense', phrases: this.symbiontSystem.getSymbiontPhrases('palinode') };
        const success = this.symbiontSystem?.addSymbiont('palinode', data);
        if (!success) { this.showNotification('No free symbiont slot!'); return; }
        if (this.addSymbiontIcon) this.addSymbiontIcon('palinode', data);
        if (!this.hasJournalEntry('palinode_bonded')) {
            this.addJournalEntry(
                'palinode_bonded',
                'Bonded: Palinode',
                'In the seams of the Echo Drain Delta I took on Palinode, "the unsaying" — a neutral symbiont whose Seam-Sense finds and opens hidden ways: sealed doors, bricked passages, the honest draft under a false wall. It is powered by spores and cares nothing for Growth or Decay.',
                this.journalSystem.categories.PEOPLE,
                { location: 'Echo Drain Delta', symbiont: 'palinode' }
            );
        }
        this.showNotification('Gained Symbiont: Palinode');
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
