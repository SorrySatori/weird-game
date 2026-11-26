import { notePlace } from '../utils/places.js';
import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { applyGDBackground } from '../utils/GDProps.js';
import { canWeave, spendWeave } from '../utils/ulvarexEncounter.js';

/** Spores for Ulvarex's mirage lot (anchored in the shine of the auction block) */
const MIRAGE_LOT_COST = 10;

export default class VoxmarketHallScene extends GameScene {
    constructor() {
        super({ key: 'VoxmarketHallScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        const metTwins = !!this.hasJournalEntry('met_hesh_vell');
        // Ulvarex: a mirage lot for their promise to stop planting bidders, once the player knows (Zerren's tip, or
        // Ulvarex herself sees through their talk of nervous bidders: twins_ulvarex_sees)
        const knowsShills = !!(this.journalSystem?.hasFact('met_hesh_vell', 'shills') || this.journalSystem?.hasFact('met_hesh_vell', 'shills_ulvarex'));
        const honest = this.hasJournalEntry('twins_honest_auction');
        const canMirageLot = knowsShills && !honest && canWeave(this, MIRAGE_LOT_COST);
        const ulvarexSees = !knowsShills && !honest && canWeave(this, 0)
            ? [{ text: "[Ulvarex] What does she see there?", key: 'twins_ulvarex_ask', next: "twins_ulvarex_sees" }] : [];

        return {
            ...super.dialogContent,

            // ——— Hesh & Vell, the Twin Auctioneers ———
            twins_start: {
                speaker: 'Hesh & Vell',
                textKey: metTwins ? 'twins_start_no_auction_return' : 'twins_start_no_auction_first',
                text: metTwins
                    ? `"Back again?" says Hesh, and Vell's lips trail half a beat behind. "No auction today, I'm afraid. The hall is dark, the lots locked away. Come back when the Voxmarket calls the next sale. You'll know when. Everyone does."`
                    : `"The hall is closed for bidding," says Hesh. Vell's lips shape the same words a half-second behind, without a sound, which is somehow worse in the empty room. "We are Hesh, and Vell. We conduct the auctions... when there are auctions. There is none today." Both twins tilt their heads in unison. "Come back when the Voxmarket calls a sale."`,
                options: [
                    { text: "How does the auction work?", key: 'how_does_the_auction_work', next: "twins_auction_rules" },
                    { text: "Why do you do that, the delayed mouthing?", key: 'why_do_you_do_that_the_delayed_mouthing', next: "twins_echo" },
                    { text: "How much would you get for me?", key: 'how_much_would_you_get_for_me', next: "twins_appraise" },
                    ...(canMirageLot ? [{ text: "[Ulvarex] Show them a lot worth more than their whole hall.", key: 'twins_ulvarex_lot', next: "twins_ulvarex_offer" }] : []),
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
                text: `"The rules are simple," says Hesh. Vell's lips follow. "Lots are presented one by one. Bidding starts at the listed price. Raise your hand to bid. Highest bidder when we call 'Settled' wins the lot.\n\nPayment is immediate. Dinar only: no barter, no vestigels, no promises. If you can't pay, you leave. If you cause a scene, you leave faster.\n\nThe pre-auction social period is just as important. Know your competition. Make friends. Or make them nervous."`,
                options: [
                    ...ulvarexSees,
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            // (review 19) auctioneers see a lot in everything, the apprentice included
            twins_appraise: {
                speaker: 'Hesh & Vell',
                text: `"A young apprentice of the Obazoba cult, one piece," says Hesh. Vell's lips trail half a beat behind. "Slightly worn from the road. Robe, travelling. Amulet, glowing. Spores, inside, quantity unverified." Both twins look you up and down. "Starting price fifty dinar."`,
                options: [
                    { text: "Only fifty?", key: 'only_fifty', next: "twins_appraise_god" },
                ]
            },
            twins_appraise_god: {
                speaker: 'Hesh & Vell',
                text: `"Priests and cultists sell badly," says Hesh. "Nobody wants to drag a stranger's god home. Then he dies on you, and who's going to clean up?"`,
                options: [
                    { text: "Obazoba won't die. He hasn't even got a body.", key: 'obazoba_wont_die', next: "twins_appraise_layers" },
                ]
            },
            twins_appraise_layers: {
                speaker: 'Hesh & Vell',
                text: `"They all said that," says Hesh. Vell mouths it after him, this time almost a full second late. "Now they lie under the Townhall. In layers."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_echo: {
                speaker: 'Hesh & Vell',
                text: `"Do what?" says Hesh. Vell mouths "Do what?" precisely on delay. They look at each other, Hesh with a slight smirk, Vell with the ghost of the same smirk half a second later.\n\n"We've always been like this," Hesh says. "Born half a second apart. Lived half a second apart. Will probably die half a second apart. It's not an affectation. It's just who we are.\n\nIt comes in handy at auctions, too. It gives them more drama and suspense. And it makes the bidders nervous. A nervous bidder is usually a generous bidder."`,
                options: [
                    { text: "That's... honestly unsettling.", key: 'thats_honestly_unsettling', next: "twins_unsettling" },
                    ...ulvarexSees,
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },
            // Ulvarex, a symbiont of perception, hears the rigged room in their talk of nervous bidders (free: seeing
            // costs nothing); then the mirage lot is on offer in twins_start
            twins_ulvarex_sees: {
                speaker: 'Ulvarex',
                text: `Ulvarex's voice arrives behind your eyes, low and amused: "'Nervous bidders.' Did you hear that? I know a staged scene when I see one. Half the hands raised at their sales belong to their own people, driving the price up at the expense of honest fools. A rigged room. Shall we offer them a better deal?"`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ],
                onTrigger: () => {
                    this.addJournalFact('met_hesh_vell', 'shills_ulvarex', "Ulvarex saw through the twins: half the hands raised at their sales belong to their own people. And that's probably just one of their dirty tricks.");
                }
            },

            // Ulvarex: a mirage lot (a bell jar with a tiny violet planet) for a promise of honest sales. Growth: the
            // bidders stop being fleeced. The payoff is the full game's: the auction's price pressure should read the
            // promise (journal 'twins_honest_auction'), and one day the twins find out the jar was never there.
            twins_ulvarex_offer: {
                speaker: 'Hesh & Vell',
                hideCloseOption: true,
                text: `You let Ulvarex set something new on the auction block. On the velvet appears an artefact that seems to belong to no century: a bell jar with a small violet planet inside. When you lean towards the jar, you make out tiny mountain ranges on the planet, rivers and seas, and at last even little towns with streets. If you look really closely, you can spot a little train crawling slowly across the violet landscape. Both twins lean in, Vell half a beat after Hesh.\n\n"Where did you get that?" says Hesh. Vell's lips follow. "Imagine if we sold that. We would sell that for millions."`,
                options: [
                    { text: "It's yours to sell. On one condition: no more dirty tricks at your auctions.", key: 'twins_ulvarex_condition', next: "twins_ulvarex_deal" },
                    { text: "Never mind.", key: 'twins_ulvarex_never_mind', next: "twins_ulvarex_dissolve" },
                ],
                onTrigger: () => {
                    if (this._mirageLot) return;   // (the spores go once per weave)
                    this._mirageLot = true;
                    spendWeave(this, MIRAGE_LOT_COST);
                }
            },
            twins_ulvarex_deal: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                speaker: 'Hesh & Vell',
                text: `The twins exchange a look that lasts half a second longer than it should.\n\n"No tricks," says Hesh. "No tricks," says Vell, on delay, which makes it sound like a vow taken twice. "Every lot goes for a fair price. You have our word." "Both our words," Vell adds, which is something you rarely hear from Vell alone.\n\nHesh lifts the bell jar as if it might break. It won't. There is nothing there to break. But it will look real for a long, long time.`,
                options: [
                    { text: "Pleasure doing business.", key: 'twins_ulvarex_pleasure', next: "closeDialog" },
                ],
                onTrigger: () => {
                    this._mirageLot = false;
                    if (this.hasJournalEntry('twins_honest_auction')) return;
                    this.gdChoiceOnce('ulvarex_twins_lot', 3, 0);
                    this.addJournalEntry(
                        'twins_honest_auction',
                        'An Honest Auction',
                        "I gave Hesh & Vell an artefact woven by Ulvarex, a bell jar holding a violet planet, in exchange for their promise to stop cheating at their auctions. Every lot is to go for a fair price.",
                        this.journalSystem.categories.EVENTS,
                        { character: 'Hesh & Vell', via: 'ulvarex-borrowed-horizon' }
                    );
                }
            },
            twins_ulvarex_dissolve: {
                speaker: 'Hesh & Vell',
                text: `You let the mirage go. The violet planet and the bell jar dissolve into thin air, and the twins keep staring at the empty velvet for a while, Vell half a second longer.`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ],
                onTrigger: () => { this._mirageLot = false; }
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
        
        // back to the main market past the left edge; the exit's own hover label is the only one (a second hint here doubled it)
        this.transitionManager.createEdgeExit('left', { target: 'VoxMarket', walkX: 133, walkY: 470, label: 'Back to Main Market', width: 150, top: 260 });

        if (this.stranger) {
            this.stranger.destroy();
        }

        // The auction is dark: only the twins keep the hall.
        this.createTwinAuctioneers();

        // Show arrival notification
        this.time.delayedCall(500, () => {
            this.showNotification(this.t('locations.VoxmarketHallScene'));   // the place's own name (lang/<code>/locations.js)
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
