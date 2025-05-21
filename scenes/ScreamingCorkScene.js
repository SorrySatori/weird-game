import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ScreamingCorkScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            
            // Edgar Eskola dialog
            edgar_start: {
                text: "Edgar Eskola shifts uncomfortably, his mišutkenn features catching the dim light. He glances at you with a mix of wariness and curiosity.",
                options: [
                    { text: "Hello there.", next: "edgar_greeting" },
                    { text: "What are you doing here?", next: "edgar_purpose" },
                    { text: "Tell me about yourself.", next: "edgar_background" },
                    { text: "What do you know about the Burning Bear Festival?", next: "edgar_festival" },
                    { text: "Goodbye.", next: "closeDialog" }
                ]
            },
            edgar_greeting: {
                text: "Mmm. Hello," + "Not often people choose to speak with me. Most avoid mišutkenn if they can help it.",
                options: [
                    { text: "Why is that?", next: "edgar_prejudice" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_prejudice: {
                text: "History. Superstition. Fear of what's different. Take your pick. The founders of this city drove my ancestors from the Remaper Hills. Now we're just... tolerated. At best.",
                options: [
                    { text: "That's unfortunate.", next: "edgar_unfortunate" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_unfortunate: {
                text: "That's one way to put it. But I've learned to live with it. Mostly.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_purpose: {
                text: "Waiting. Watching. Avoiding the preparations for that cursed festival. The Screaming Cork is one of the few places that doesn't go all-in on the bear burning nonsense.",
                options: [
                    { text: "You don't like the festival?", next: "edgar_festival" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_background: {
                text: "Not much to tell. I've had more jobs than I can count. Janitor at 1140 Scraper, professional imaginator, clerk, art model, airship mechanic, meat packer... None of them stuck. Not entirely my fault, though.",
                options: [
                    { text: "Professional imaginator?", next: "edgar_imaginator" },
                    { text: "Why didn't they work out?", next: "edgar_jobs" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_imaginator: {
                text: "I dreamed up locations and characters for Dr. Elphi Quarn's games. Turns out my imagination was too... wild. Too erratic, they said. My dreams were 'unusable.' Their loss.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_jobs: {
                text: "Bad timing, mostly. The Scraper took the Rusty Choir and stopped being an official part of the city - no need for a janitor then. The other jobs... well, being a mišutkenn doesn't help with job security in this city.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_festival: {
                text: "The Burning Bear Festival? A cruel reminder of an ancient 'victory' over my kind. They stuff bear skins with things they want to be rid of, then burn them at midnight. Some fill them with pests, bad habits, vices... others with rivals, if the rumors are true.",
                options: [
                    { text: "That sounds disturbing.", next: "edgar_disturbing" },
                    { text: "It's just tradition, isn't it?", next: "edgar_tradition" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_disturbing: {
                text: "It is. Imagine being surrounded by burning effigies that look like your ancestors. The city lights up with fires of different colors and smells, while I hide away, waiting for it to end.",
                options: [
                    { text: "I'm sorry to hear that.", next: "edgar_sympathy" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_tradition: {
                text: "Tradition? Traditions can be cruel. Just because something has been done for generations doesn't make it right. But few in this city would agree with me.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_sympathy: {
                text: "Your sympathy is... unexpected. But appreciated. Perhaps not everyone in this city is as thoughtless as I've come to believe.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkBg', 'assets/images/ScreamingCork.png');
        this.load.image('arrow', 'assets/images/arrow.png');
        this.load.image('edgarEskola', 'assets/images/EdgarEskola.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the right side when entering from ScraperScene
        this.priest.x = 700;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Create exit to ScraperScene at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'ScraperScene', // target scene
            50, // walk to x
            470 // walk to y
        );
        
        // Create entrance to the tavern interior (centered on the tavern door)
        this.transitionManager.createTransitionZone(
            400, // x position - centered on the door
            470, // y position
            100, // width
            200, // height
            'up', // direction
            'ScreamingCorkInteriorScene', // target scene
            100, // walk to x - position inside the tavern
            470 // walk to y
        );
        
        // Add a hint about the tavern entrance
        const doorHint = this.add.text(400, 380, 'Enter Tavern', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        doorHint.setOrigin(0.5);
        doorHint.setAlpha(0);
        doorHint.setDepth(10);
        
        // Show hint when hovering near the door
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the door area
            if (Math.abs(pointer.x - 400) < 50 && Math.abs(pointer.y - 470) < 100) {
                doorHint.setAlpha(1);
            } else {
                doorHint.setAlpha(0);
            }
        });
        
        // Add Edgar Eskola NPC
        this.createEdgarEskola();
    }

    update() {
        super.update();
    }
    
    createEdgarEskola() {
        // Create Edgar Eskola NPC
        this.edgar = this.add.image(200, 510, 'edgarEskola'); // Further increased Y to lower position more
        this.edgar.setScale(0.125); // Set appropriate scale
        this.edgar.setOrigin(0.5, 1.0); // Set origin to bottom center to align with ground
        this.edgar.setDepth(5);
        this.edgar.setInteractive({ useHandCursor: true });
        
        // Add dialog interaction
        this.edgar.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('edgar_start');
        });
        
        // Add subtle wobble effect
        this.addWobbleEffect(this.edgar, 200, 510); // Update wobble position to match new Y
    }
    
    addWobbleEffect(sprite, baseX, baseY) {
        // Create a very subtle wobble effect
        this.tweens.add({
            targets: sprite,
            y: { from: baseY - 1, to: baseY + 1 },
            ease: 'Sine.easeInOut',
            duration: 1500,
            yoyo: true,
            repeat: -1
        });
        
        // Add a very slight rotation wobble
        this.tweens.add({
            targets: sprite,
            angle: { from: -1, to: 1 },
            ease: 'Sine.easeInOut',
            duration: 2000,
            yoyo: true,
            repeat: -1,
            delay: 5000 // Offset from the y-wobble for more natural movement
        });
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScreamingCorkScene = ScreamingCorkScene;
}
