import { notePlace } from '../utils/places.js';
import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { applyGDBackground } from '../utils/GDProps.js';

export default class VoxmarketHallScene extends GameScene {
    constructor() {
        super({ key: 'VoxmarketHallScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        const metTwins = !!this.hasJournalEntry('met_hesh_vell');

        return {
            ...super.dialogContent,

            // ——— Hesh & Vell, the Twin Auctioneers ———
            twins_start: {
                speaker: 'Hesh & Vell',
                textKey: metTwins ? 'twins_start_no_auction_return' : 'twins_start_no_auction_first',
                text: metTwins
                    ? `"Back again?" says Hesh, and Vell's lips trail half a beat behind. "No auction today, I'm afraid. The hall is dark, the lots locked away. Come back when the Voxmarket calls the next sale. You'll know when. Everyone does."`
                    : `"The hall is closed for bidding," says Hesh. Vell forms the words a half-second behind, the echo unsettling in the empty room. "We are Hesh, and Vell. We conduct the auctions... when there are auctions. There is none today." Both twins tilt their heads in unison. "Come back when the Voxmarket calls a sale."`,
                options: [
                    { text: "How does the auction work?", key: 'how_does_the_auction_work', next: "twins_auction_rules" },
                    { text: "Why do you do that, the delayed mouthing?", key: 'why_do_you_do_that_the_delayed_mouthing', next: "twins_echo" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_hesh_vell')) {
                        this.addJournalEntry(
                            'met_hesh_vell',
                            'The Twin Auctioneers: Hesh & Vell',
                            'Met the twin auctioneers at the Voxmarket Auction Hall. One speaks, the other mouths the same words half a second late. Their synchronization is unsettling and precise, and likely deliberate. They run the auction together.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Hesh & Vell' }
                        );
                    }
                }
            },

            twins_auction_rules: {
                speaker: 'Hesh & Vell',
                text: `"The rules are simple," says Hesh. Vell's lips follow. "Lots are presented one by one. Bidding starts at the listed price. Raise your hand to bid. Highest bidder when we call 'Settled' wins the lot.\n\nPayment is immediate. Gold only: no barter, no vestigels, no promises. If you can't pay, you leave. If you cause a scene, you leave faster.\n\nThe pre-auction social period is just as important. Know your competition. Make friends. Or make them nervous."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_echo: {
                speaker: 'Hesh & Vell',
                text: `"Do what?" says Hesh. Vell mouths "Do what?" precisely on delay. They look at each other, Hesh with a slight smirk, Vell with the ghost of the same smirk half a second later.\n\n"We've always been like this," Hesh says. "Born half a second apart. Lived half a second apart. Will probably die half a second apart. It's not an affectation. It's a condition.\n\nAlso, it makes our auction pacing impossible to interrupt. By the time you've processed what I've said, Vell has already reinforced it. Very effective for driving up bids."`,
                options: [
                    { text: "That's... honestly unsettling.", key: 'thats_honestly_unsettling', next: "twins_unsettling" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_unsettling: {
                speaker: 'Hesh & Vell',
                text: `"Thank you," they say. For once, perfectly in unison. Then the delay resumes.\n\n"Unsettling is good for business," Hesh adds. "A nervous bidder is a generous bidder."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },
        };
    }

    preload() {
        super.preload();
        this.load.image('voxmarketHallBg', 'assets/images/backgrounds/VoxmarketHall.png');
        this.load.image('voxmarketHallBg_growth', 'assets/images/backgrounds/VoxmarketHall_growth.png');
        this.load.image('voxmarketHallBg_decay', 'assets/images/backgrounds/VoxmarketHall_decay.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.spritesheet('heshAndVell', 'assets/images/characters/voxmarket/hesh_vell.png', { frameWidth: 208, frameHeight: 176 }); // 8 idle frames, Vell two behind Hesh
    }

    create() {
        super.create();
        notePlace(this, 'place_voxmarket');   // the journal's Places tab, on the first visit
        
        this.playSceneMusic('marketTheme');
        
        const bg = this.add.image(400, 300, 'voxmarketHallBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        applyGDBackground(this, bg, 'voxmarketHallBg'); // the auction bay paints its own floor
        
        if (this.ground) {
            this.ground.destroy();
        }
        
        this.transitionManager = new SceneTransitionManager(this);
        
        this.priest.x = 100;
        this.priest.y = 470;
        
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // the exit's own hover label is the only one (a second hint here doubled it)
        this.transitionManager.createTransitionZone(
            50, 470, 50, 200, 'left', 'VoxMarket', 100, 470, 'Back to Main Market'
        );
        
        if (this.stranger) {
            this.stranger.destroy();
        }

        // The auction is dark: only the twins keep the hall.
        this.createTwinAuctioneers();

        // Show arrival notification
        this.time.delayedCall(500, () => {
            this.showNotification('Voxmarket Auction Hall', 0x8B4513);
        });
    }

    createTwinAuctioneers() {
        if (!this.anims.exists('twins_idle')) {
            this.anims.create({ key: 'twins_idle', frames: this.anims.generateFrameNumbers('heshAndVell', { start: 0, end: 7 }), frameRate: 4, repeat: -1 });
        }
        // On the stage (its top is at y≈431); the idle loop is the desynchronization: Vell's gavel two frames late
        this.twins = this.add.sprite(440, 429, 'heshAndVell', 0).setOrigin(0.5, 1);
        this.twins.setDepth(5);
        this.twins.play('twins_idle');
        this.addGroundShadow(440, 427, 170, 10);
        this.twins.setInteractive({ useHandCursor: true });

        this.twins.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('twins_start');
        });
    }

    shutdown() {
        // Restore background music when leaving the scene
        this.restoreBackgroundMusic();
        super.shutdown();
    }

    update() {
        // Call parent update for all standard mechanics
        super.update();
    }
}
