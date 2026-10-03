import GameScene from './GameScene.js';
import QuestSystem from '../systems/QuestSystem.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ShedHallScene extends GameScene {
    constructor() {
        super({ key: 'ShedHallScene' });
        this.isTransitioning = false;
        this._livingCore = null;
        this._livingCoreDialogContent = {
            main: {
                speaker: 'Narrator',
                text: "A Living Core pulses with an otherworldly energy. It seems to be fused with the wall, but it might be possible to extract it...",
                options: [
                    { text: "Examine it more carefully", key: 'examine_it_more_carefully', next: "examine" },
                    { text: "Extract it forcefully", key: 'extract_it_forcefully', next: "force_extract" },
                    { text: "Leave it alone", key: 'leave_it_alone', next: "goodbye" }
                ]
            },
            examine: {
                text: "The Living Core seems connected to the wall only at a few points. With the right tools, like a pair of pliers, you might be able to extract it without causing damage...",
                options: [
                    { text: "Back", key: 'back', next: "main" }
                ]
            },
            force_extract: {
                text: "You wrench the Living Core free with brute force. The surrounding area seems to be getting cold...",
                options: [
                    { text: "Continue", key: 'continue', next: "goodbye_taken" }
                ],
                onTrigger: () => {
                    const questSystem = QuestSystem.getInstance();
                    
                    this.modifyGrowthDecay(0,5);
                    this.addItemToInventory({ id: 'living-core', name: 'Living Core', description: 'A pulsating core of living metal, forcefully extracted from the Shed.', spriteKey: 'living-core', stackable: false });
                    questSystem.updateQuest('rust_reclamation', 'I have retrieved the Living Core, with a bit of good old violence.', 'core_taken_force');
                    if (this._livingCore) {
                        this._livingCore.destroy();
                        this._livingCore = null;
                    }
                }
            },
            careful_extract: {
                text: "Using the pliers, you carefully extract the Living Core. Nothing else happens... Or at least you don't see any visible changes.",
                options: [
                    { text: "Continue", key: 'continue', next: "careful_extract_complete" }
                ],
                onTrigger: () => {
                    const questSystem = QuestSystem.getInstance();
                    
                    this.modifyGrowthDecay(2,0);
                    this.addItemToInventory({ id: 'living-core', name: 'Living Core', description: 'A pulsating core of living metal, carefully extracted from the Shed.', variant: 'careful', spriteKey: 'living-core', stackable: false });
                    questSystem.updateQuest('rust_reclamation', 'Carefully extracted the Living Core using pliers; it probably didn\'t damage the building in any way.', 'core_taken_careful');
                    if (this._livingCore) {
                        this._livingCore.destroy();
                        this._livingCore = null;
                    }
                }
            },
            careful_extract_complete: {
                text: "The Living Core pulses contentedly in your hands, its energy seemingly preserved by your careful extraction.",
                options: [
                    { text: "Continue", key: 'continue', next: "goodbye_taken" }
                ]
            },
            goodbye: {
                text: "You step back from the Living Core.",
                options: []
            },
            goodbye_taken: {
                text: "You step back from where the Living Core was.",
                options: []
            }
        };
    }

    get dialogContent() {
        return this._livingCoreDialogContent;
    }

    preload() {
        super.preload();
        this.load.image('hall-bg', 'assets/images/backgrounds/ShedHall.png');
        this.load.image('exitArea', 'assets/images/ui/exitArea.png');
        this.load.image('living-core', 'assets/images/characters/living-core.png');
    }

    create() {
        super.create();
        
        const bg = this.add.image(400, 300, 'hall-bg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        
        if (this.priest) {
            this.priest.x = 400;
            this.priest.y = 470;
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Add Living Core
        this._livingCore = this.add.sprite(600, 300, 'living-core');
        this._livingCore.setScale(0.5);
        this._livingCore.setInteractive({ useHandCursor: true });
        this._livingCore.on('pointerdown', () => this.showLivingCoreDialog());

        // Add glow effect to Living Core
        this.tweens.add({
            targets: this._livingCore,
            alpha: 0.7,
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Initialize SceneTransitionManager
        this.transitionManager = new SceneTransitionManager(this);

        this.transitionManager.createTransitionZone(
            90, // x position
            370, // y position
            50, // width
            200, // height
            'left', // direction
            'Shed521FloorsScene',
            100, // walk to x
            470, // walk to y
            'Back'
        );

            const inventory = this.registry.get('inventory');
            const alreadyInInventory = inventory.items.some(item => item.id === 'living-core');
            if (alreadyInInventory) {
                this._livingCore.setVisible(false);
            }
    }

    update() {
        super.update();
    }

    showLivingCoreDialog() {
        const inventory = this.registry.get('inventory');
        const hasPliers = inventory.items.some(item => item.id ==='pliers');

        // Update main dialog options based on pliers
        if (hasPliers) {
            this._livingCoreDialogContent.main.options = [
                { text: "Use pliers to carefully extract it", key: 'use_pliers_to_carefully_extract_it', next: "careful_extract" },
                { text: "Extract it forcefully", key: 'extract_it_forcefully', next: "force_extract" },
                { text: "Leave it alone", key: 'leave_it_alone', next: "goodbye" }
            ];
        } else {
            this._livingCoreDialogContent.main.options = [
                { text: "Examine it more carefully", key: 'examine_it_more_carefully', next: "examine" },
                { text: "Extract it forcefully", key: 'extract_it_forcefully', next: "force_extract" },
                { text: "Leave it alone", key: 'leave_it_alone', next: "goodbye" }
            ];
        }

        this.showDialog('main');
    }
}
