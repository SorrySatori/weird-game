import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';
import { addHoverAura } from '../utils/hoverAura.js';
import { preloadUlvarexPuddle, setupUlvarexEncounter, ulvarexDialog, hasUlvarex } from '../utils/ulvarexEncounter.js';

export default class ScraperScene extends GameScene {
    constructor() {
        super({ key: 'ScraperScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    preload() {
        super.preload();
        this.preloadMusic('streetSong');
        this.load.image('scraperBg', 'assets/images/backgrounds/Scraper1140.png');
        preloadUlvarexPuddle(this, 'roof');   // Ulvarex's puddle (utils/ulvarexEncounter.js)
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        // Don Girandole, 8 idle frames of 136x168 (tools/artgen/lamps.py on dev): in the demo just for company
        this.load.spritesheet('lamp_don', 'assets/images/characters/lamps/don.png', { frameWidth: 136, frameHeight: 168 });
    }

    // In the demo the Don is only a character to talk to: no Gang of Lamps quest, no quest log or journal entry.
    // His goodbye leaves a door open for the full game ("tell any lamp the Don says hello").
    get dialogContent() {
        const met = !!this.registry.get('don_demo_met');
        const ask = [
            { text: "Who are you, exactly?", key: 'don_demo_who', next: 'don_demo_who' },
            { text: "What do you do up here?", key: 'don_demo_view', next: 'don_demo_view' },
            { text: "...you're a talking lamp.", key: 'don_demo_lamp', next: 'don_demo_lamp' },
            // his hint at Ulvarex's puddle up here (utils/ulvarexEncounter.js), next to Kloor's; gone once she's bonded
            ...(hasUlvarex(this) ? [] : [{ text: "Quite a view of the Scraper from up here.", key: 'don_demo_scraper', next: 'don_demo_scraper' }]),
            { text: "They say this is the city of dead gods.", key: 'don_demo_dead_gods', next: 'don_demo_dead_gods' },
            { text: "I should go.", key: 'don_demo_bye', next: 'don_demo_farewell' },
        ];
        const more = [
            { text: "Something else.", key: 'don_demo_back', next: 'don_demo_more' },
            { text: "I should go.", key: 'don_demo_bye', next: 'don_demo_farewell' },
        ];
        return {
            ...super.dialogContent,
            ...ulvarexDialog(this),
            don_demo_start: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                textKey: met ? 'don_demo_again' : 'don_demo_first',
                text: met
                    ? `The Don's flame turns to you lazily, the ember of his cigar glowing. "Back again? Good. A lamp gets lonely up here, with only the wind and the wires for company."`
                    : `On the pipe tower above the walkway stands a gaudy old lamp. For some reason it doesn't stand on an ordinary post but on the body of a portly man in a three-piece suit, a white-gloved hand round a smoking cigar. It swivels its head-lamp toward you, and the flame leans closer behind the glass. "Well, well. A visitor who looks up. Hardly anybody looks up in this city, friend. They look at their feet, at their papers, busy with their earthbound little affairs. Nobody ever looks at an old lamp." A slow puff of smoke. "Don Girandole. Pleased to make your acquaintance."`,
                options: ask,
                onTrigger: () => { this.registry.set('don_demo_met', true); },
            },
            don_demo_more: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                text: `The flame turns back to you. "What else, friend?"`,
                options: ask,
            },
            don_demo_who: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                text: `"Head of a family, friend. A family of lamps, before you laugh." The flame narrows. "We're scattered all over this city, every one of us bolted to some post or wall, and not one of us can take a single step. Still, we do quite nicely." He taps the ash off his cigar. "One day I may need a pair of legs like yours. But not today. Business is good."`,
                options: more,
            },
            don_demo_view: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                text: `"I watch the windows. Every one that lights up and every one that goes dark. You learn a lot about people from the lights they leave on, and more from the ones they put out." The flame dips toward the tower. "That one never sleeps, by the way. Remember that whenever you're inside."`,
                options: more,
            },
            don_demo_scraper: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                text: `"Magnificent building, the Scraper, eh? I never get tired of looking at it. Mind you, once I had some extra strong Oltrac, and then I saw some really weird things."`,
                options: more,
            },
            don_demo_lamp: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                text: `"And you're a talking pair of legs. We've all got our quirks, friend." The ember glows brighter, amused. "And don't stare. It's not polite to stare at a man's lamp."`,
                options: more,
            },
            // the dying gods seen by a lamp, whose trade it is (he doesn't say where the lamps came from: canon 2026-11-26)
            don_demo_dead_gods: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                text: `"It is. And for lamps it's good business." The flame sways contentedly. "Every god who comes here to die wants a light on the way." A puff on the cigar.`,
                options: [{ text: "My god will never come here to die.", key: 'don_demo_my_god', next: 'don_demo_my_god' }, ...more],
            },
            don_demo_my_god: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                text: `"They all said that, friend. Under the cobbles of this city lie plenty of gods who were never going to come here to die." He draws on the cigar. "But don't worry. When yours does, I'll light his way."`,
                options: more,
            },
            don_demo_farewell: {
                speaker: 'Don Girandole',
                hideCloseOption: true,   // his own "I should go" leads to the goodbye
                text: `"Go on, then. And if you ever catch a lamp somewhere in this city looking at you a moment too long, tell it the Don says hello."`,
                options: [{ text: "Goodbye, Don.", key: 'don_demo_close', next: 'closeDialog' }],
            },
        };
    }

    /** Don Girandole on the pipe-tower platform at the right edge (deck rim y 379), idle, clickable, with his bust. */
    createDon() {
        if (!this.anims.exists('lamp_don_idle')) {
            this.anims.create({ key: 'lamp_don_idle', frameRate: 5, repeat: -1,
                frames: this.anims.generateFrameNumbers('lamp_don', { frames: [0, 1, 1, 0, 0, 2, 3, 3, 3, 3, 4, 4, 5, 0, 0, 1, 0, 6, 6, 7, 0, 0] }) });
        }
        const don = this.add.sprite(1024, 381, 'lamp_don', 0).setOrigin(0.5, 1).setDepth(6);
        don.play({ key: 'lamp_don_idle', startFrame: Math.floor(Math.random() * 22) });
        // the hit box stops above the right-edge exit zone (canvas y 370..570)
        don.setInteractive({ hitArea: new Phaser.Geom.Rectangle(8, 4, 96, 150), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
        addHoverAura(don, [don], 0xffd27a);   // the character aura in his own lamp-light gold
        don.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('don_demo_start');
        });
        this.dialogPortraits = { ...(this.dialogPortraits || {}), 'Don Girandole': { key: 'lamp_don', frame: 3, zoom: 2, top: 22 } };
        this.don = don;
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Native 1067×600, 1 px pixel art (tools/artgen/scraper_native_bg.py): the tower across the gap, a wet rooftop to walk on
        const bg = this.add.image(400, 300, 'scraperBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own roof and duckboards; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        this.playSceneMusic('streetSong', { resume: true });

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the right side when entering
        this.priest.x = 700;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Exits (canvas coords):
        // - the Scraper: the gate of the footbridge lights up whole (its first visit writes the journal entry)
        // - the Crossroad: the walkway on to the left, past the stair-house (not through its door); the arrow keys too
        // - Burning Bear Street: the street on to the right (the band stays under the Don's lamp-post)
        const tm = this.transitionManager;
        tm.createDoorZone({ rect: [487, 374, 92, 141] }, {
            target: 'ScraperInteriorScene', walkX: 533, walkY: 470, label: () => this.t('ui.hotspots.enterScraper'),
            onClick: () => {
                if (!this.hasJournalEntry('scraper_building')) {
                    this.addJournalEntry(
                        'scraper_building',
                        'The Scraper',
                        "Scraper 1140: a crooked skyscraper towering over the city. It used to be an office tower; now every floor lives a life of its own, and nobody seems quite sure how many floors there are.",
                        this.journalSystem.categories.PLACES,
                        { location: 'The Scraper, Upper Morkezela' }
                    );
                }
                tm.handleSceneTransition('ScraperInteriorScene', 533, 470);
            }
        });
        tm.createEdgeExit('left', { target: 'CrossroadScene', walkX: 20, walkY: 470, width: 190, top: 395 });   // as tall as the right one
        tm.createEdgeExit('right', { target: 'BurningBearStreetScene', walkX: 1047, walkY: 470, width: 170, top: 395 });


        // Examine: the tower & its "SCRAPER 1140" sign (upper-center, clear of the gate below).
        // Comment deepens once you've been inside.
        this.createObservable(447, 160, 200, 170, () => {
            if (this.hasJournalEntry('scraper_building')) return this.t('observe.scraper.been_inside');
            return this.t('observe.scraper.default');
        }, { hint: this.t('observe.scraper.hint') });

        // Don Girandole on the pipe-tower platform (the full game's Gang of Lamps boss; here just to talk to)
        this.createDon();

        // Ulvarex's puddle on the wet roof left of the footbridge (shows on a Violet/Amber Oltrac trip)
        setupUlvarexEncounter(this, 'roof');
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScraperScene = ScraperScene;
}
