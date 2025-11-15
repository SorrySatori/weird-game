import GameScene from './GameScene.js'
import SceneTransitionManager from '../utils/SceneTransitionManager.js'

export default class TownSquareScene extends GameScene {
    constructor() {
        super({ key: 'TownSquareScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            ...this._magnekinDialogContent,
            ...this._buskerDialogContent
        };
    }

    preload() {
        super.preload();

        this.load.image('townSquareBg', 'assets/images/backgrounds/TownSquare.png');
        this.load.image('magnekin', 'assets/images/characters/magnekin.png');
        this.load.image('busker', 'assets/images/characters/busker.png');
    }

    create() {
        super.create();        
        this.playSceneMusic('busker_theme');
        
        const bg = this.add.image(400, 300, 'townSquareBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        this.transitionManager = new SceneTransitionManager(this);
        
        this.transitionManager.createTransitionZone(
            720,
            300,
            80,
            400,
            'right',
            'TownhallScene',
            50,
            300,
        );
        
        this.createMagnekin();
        this.createBusker();

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createMagnekin() {
        this._magnekinDialogContent = {
            speaker: 'Magnekin',
            
            magnekin_greeting: {
                text: "Greetings, traveler. I am Magnekin, keeper of magnetic harmonies. The city's metal veins sing to me—iron whispers, copper hums, steel resonates.",
                options: [
                    { text: "What do you mean by 'magnetic harmonies'?", next: "magnekin_harmonies" },
                    { text: "Can you sense metal objects?", next: "magnekin_sense" },
                    { text: "Farewell.", next: null }
                ]
            },
            
            magnekin_harmonies: {
                text: "Every metal has its own frequency, its own song. I can hear them all—the ancient iron in the foundations, the new copper in the pipes, even the rust singing its slow decay. It's a symphony of civilization.",
                options: [
                    { text: "That sounds fascinating.", next: "magnekin_greeting" },
                    { text: "Farewell.", next: null }
                ]
            },
            
            magnekin_sense: {
                text: "Indeed. I can feel the pull of every nail, every coin, every blade within a hundred paces. It's both a gift and a burden—imagine hearing every conversation in a crowded room, all at once.",
                options: [
                    { text: "How do you manage it?", next: "magnekin_manage" },
                    { text: "Farewell.", next: null }
                ]
            },
            
            magnekin_manage: {
                text: "Meditation, mostly. I've learned to tune out the noise, to focus on specific frequencies. But sometimes, when the city is quiet, I let it all wash over me. It's strangely peaceful.",
                options: [
                    { text: "Interesting. Tell me more.", next: "magnekin_greeting" },
                    { text: "Farewell.", next: null }
                ]
            }
        };

        this.magnekin = this.add.container(250, 300);
        this.magnekin.setDepth(-1);
        
        const magnekinSprite = this.add.sprite(0, 0, 'magnekin');
        magnekinSprite.setScale(0.2);
        
        magnekinSprite.setTint(0xc0c0c0);
        
        this.magnekin.add(magnekinSprite);
        
        this.magnekinGlow = this.add.graphics();
        this.magnekinGlow.fillStyle(0x8888ff, 0.15);
        this.magnekinGlow.fillCircle(250, 350, 45);
        this.magnekinGlow.setDepth(4);
        
        this.tweens.add({
            targets: this.magnekinGlow,
            alpha: { from: 0.15, to: 0.05 },
            duration: 2000,
            yoyo: true,
            repeat: -1
        });
        
        this.tweens.add({
            targets: this.magnekin,
            y: { from: 350, to: 345 },
            duration: 2500,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });
        
        const hitArea = new Phaser.Geom.Rectangle(-40, -90, 80, 140);
        this.magnekin.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);
        
        this.magnekin.on('pointerover', () => {
            this.magnekin.setScale(1.05);
            document.body.style.cursor = 'pointer';
        });
        
        this.magnekin.on('pointerout', () => {
            this.magnekin.setScale(1);
            document.body.style.cursor = 'default';
        });
        
        this.magnekin.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }
            
            this.tweens.add({
                targets: this.magnekin,
                y: { from: this.magnekin.y, to: this.magnekin.y - 5 },
                duration: 100,
                ease: 'Power1',
                yoyo: true
            });
            
            this.showDialog('magnekin_greeting');
        });
    }

    createBusker() {
        this._buskerDialogContent = {
            speaker: 'Busker',
            
            busker_greeting: {
                text: "Hey there! Care to hear a tune? I play the songs of the old world—melodies that remember when the sky was blue and the air was clean.",
                options: [
                    { text: "What kind of songs do you play?", next: "busker_songs" },
                    { text: "Where did you learn these songs?", next: "busker_learn" },
                    { text: "Maybe later.", next: null }
                ]
            },
            
            busker_songs: {
                text: "Ballads of lost cities, lullabies from forgotten cultures, work songs from trades that no longer exist. Each one is a memory preserved in melody. Music is the only time machine we have left.",
                options: [
                    { text: "That's beautiful.", next: "busker_greeting" },
                    { text: "Maybe later.", next: null }
                ]
            },
            
            busker_learn: {
                text: "From the elders, mostly. They taught me before they passed on. Now I'm one of the few who remembers. Sometimes I wonder if anyone really listens, or if I'm just singing to the stones.",
                options: [
                    { text: "I'm listening.", next: "busker_thanks" },
                    { text: "Maybe later.", next: null }
                ]
            },
            
            busker_thanks: {
                text: "Thank you, friend. That means more than you know. As long as someone listens, the songs live on. And as long as the songs live, so do the memories.",
                options: [
                    { text: "Tell me more.", next: "busker_greeting" },
                    { text: "Farewell.", next: null }
                ]
            }
        };

        this.busker = this.add.container(550, 380);
        this.busker.setDepth(-1);
        
        const buskerSprite = this.add.sprite(0, 0, 'busker');
        buskerSprite.setScale(0.2);
        
        buskerSprite.setTint(0xffcc88);
        
        this.busker.add(buskerSprite);
        
        this.buskerGlow = this.add.graphics();
        this.buskerGlow.fillStyle(0xffaa44, 0.15);
        this.buskerGlow.fillCircle(550, 380, 45);
        this.buskerGlow.setDepth(4);
        
        this.tweens.add({
            targets: this.buskerGlow,
            alpha: { from: 0.15, to: 0.05 },
            duration: 1800,
            yoyo: true,
            repeat: -1
        });
        
        this.tweens.add({
            targets: this.busker,
            angle: { from: -2, to: 2 },
            duration: 3000,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });
        
        const hitArea = new Phaser.Geom.Rectangle(-40, -90, 80, 140);
        this.busker.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);
        
        this.busker.on('pointerover', () => {
            this.busker.setScale(1.05);
            document.body.style.cursor = 'pointer';
        });
        
        this.busker.on('pointerout', () => {
            this.busker.setScale(1);
            document.body.style.cursor = 'default';
        });
        
        this.busker.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }
            
            this.tweens.add({
                targets: this.busker,
                y: { from: this.busker.y, to: this.busker.y - 5 },
                duration: 100,
                ease: 'Power1',
                yoyo: true
            });
            
            this.showDialog('busker_greeting');
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
    window.TownSquareScene = TownSquareScene;
}

export { TownSquareScene };
