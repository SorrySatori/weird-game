import GameScene from './GameScene.js';
import QuestSystem from '../systems/QuestSystem.js';

export default class ShedCourtyardScene extends GameScene {
    constructor() {
        super({ key: 'ShedCourtyard' });
        this.isTransitioning = false;
        this._ortolan = null;
        this._ortholanDialogContent = {
            main: {
                text: "Ah, another visitor to this bureaucratic nightmare... *sigh* I've been here for days trying to get approval for an extra pair of arms. Do you know how hard it is to design complex board games with just two hands?",
                options: [
                    { text: "Why do you need extra arms?", next: "explain_need" },
                    { text: "Board games? What do you mean?", next: "board_games" },
                    { text: "Who are you?", next: "who_are_you" },
                    { text: "Good luck with that!", next: "goodbye" }
                ]
            },
            explain_need: {
                text: "Have you ever tried to playtest a complex strategy game by yourself? Moving pieces, managing resources, tracking multiple player states... It's a nightmare! With four arms, I could revolutionize solo playtesting. But the paperwork here... it's endless!",
                options: [
                    { text: "I could help you with the application process.", next: "start_quest" },
                    { text: "Sounds complicated. Good luck!", next: "goodbye" }
                ]
            },
            board_games: {
                text: "You did heard about a thing called a board game, didn't you? Well, I'm a best damn board game designer in this forsaken place. My games are not like the simple things for children you probably know, they provide a unique gameplay experience. With four arms, I can handle complex interactions and manage multiple player states more effectively. But the bureaucracy... it's a nightmare!",
                options: [
                    { text: "I could help you with the application process.", next: "start_quest" },
                    { text: "Who are you?", next: "who_are_you" },
                    { text: "Sounds complicated. Good luck!", next: "goodbye" }
                ]
            },
            who_are_you: {
                text: "I'm Ortolan Šmelc, a board game designer. I once served as a 'worldwright' during the era of table-top divination wars. My creations are literally microcosmic games—wooden boards sprouting tiny sentient pieces, enacting dramas and politics. You might heard from some calling me conservative, merely because I reject illusion-tech and mindplay, they are usualy morally unstable. Players are gods, but rules are sacred. ",
                options: [
                    { text: "Why do you need extra arms?", next: "explain_need" },
                    { text: "Table top divination wars? What do you mean?", next: "divination_wars" },
                    { text: "Sounds complicated. Good luck!", next: "goodbye" }
                ]
            },
            divination_wars: {
                text: "Ah, yes... terrible times. Maybe you should ask a historian about that. Or I can tell you more, but first I need to get out of this bureaucratic nightmare.",
                options: [
                    { text: "I could help you with the application process.", next: "start_quest" },
                    { text: "Sounds complicated. Good luck!", next: "goodbye" }
                ]
            },
            start_quest: {
                text: "Really? Oh, that would be wonderful! The main issue is getting through to the right department. They keep sending me between floors, and every clerk seems to need a different form. If you could help me track down the right paperwork and get it to the correct office, I'd be eternally grateful!",
                options: [
                    { text: "I'll see what I can do.", next: "accept_quest" }
                ],
                onShow: () => {
                    const questSystem = QuestSystem.getInstance();
                    if (!questSystem.getQuest('ortolan_arms')) {
                        questSystem.addQuest(
                            'ortolan_arms',
                            'Extra Arms for Ortolan',
                            'Help Ortolan, the board game designer, navigate the Shed\'s bureaucracy to get approval for an extra pair of arms.'
                        );
                        this.showNotification('Quest added: Extra Arms for Ortolan');
                    }
                }
            },
            accept_quest: {
                text: "Thank you! With your help, I'm sure we can navigate this bureaucratic maze. Come back when you have any progress to report!",
                options: [
                    { text: "I'll do my best.", next: "goodbye" }
                ]
            },
            quest_active: {
                text: "Still stuck in bureaucratic limbo... But I'm hopeful with your help we can get through this maze of paperwork!",
                options: [
                    { text: "I'll keep working on it.", next: "goodbye" },
                    { text: "See you later.", next: "goodbye" }
                ]
            },
            goodbye: {
                text: "May the spores guide your path...",
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            }
        };
    }

    get dialogContent() {
        return this._ortholanDialogContent;
    }

    preload() {
        super.preload();
        this.load.image('courtyard-bg', 'assets/images/ShedMutationCourtyard.png');
        this.load.image('door', 'assets/images/door.png');
        this.load.image('exitArea', 'assets/images/exitArea.png');
        this.load.image('ortolan', 'assets/images/Ortolan.png');
    }

    create() {
        super.create();
        
        const bg = this.add.image(400, 300, 'courtyard-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        if (this.priest) {
            this.priest.x = 50;
            this.priest.y = 470;
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Add Ortolan
        this._ortolan = this.add.sprite(600, 520, 'ortolan');
        this._ortolan.setOrigin(0.5, 1);
        this._ortolan.setScale(0.15);
        this._ortolan.setInteractive({ useHandCursor: true });
        this._ortolan.on('pointerdown', () => this.showOrtholanDialog());

        // Add idle animation for Ortolan
        this.tweens.add({
            targets: this._ortolan,
            y: this._ortolan.y - 3,
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Random head movements
        this.time.addEvent({
            delay: 5000,
            callback: () => {
                if (Math.random() > 0.5) {
                    this.tweens.add({
                        targets: this._ortolan,
                        angle: Phaser.Math.Between(-5, 5),
                        duration: 1000,
                        ease: 'Sine.easeInOut',
                        yoyo: true
                    });
                }
            },
            loop: true
        });

        // Add invisible clickable exit area at the left of the screen
        this.exitArea = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(50, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        this.exitArea.on('pointerdown', () => {
            if (!this.isTransitioning && this.priest && this.priest.x < 100) {
                this.isTransitioning = true;

                const priest = this.priest;
                priest.play('walk');
                
                this.tweens.killTweensOf(priest);
                
                this.tweens.add({
                    targets: priest,
                    x: 20,
                    y: priest.y,
                    duration: 1000,
                    onComplete: () => {
                        this.cameras.main.fadeOut(800, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            this.scene.start('Shed13GateScene');
                            this.isTransitioning = false;
                        });
                    }
                });
            }
        });
    }

    update() {
        super.update();
        
        if (this.priest && this.priest.x < 100) {
            this.exitArea.input.cursor = 'pointer';
        } else {
            this.exitArea.input.cursor = 'default';
        }
    }

    showOrtholanDialog() {
        const questSystem = QuestSystem.getInstance();
        const hasStartedQuest = questSystem.getQuest('ortolan_arms');

        if (!hasStartedQuest) {
            this.showDialog('main');
        } else {
            this.showDialog('quest_active');
        }
    }
}
