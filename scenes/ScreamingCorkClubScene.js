import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ScreamingCorkClubScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkClubScene' });
        this.isTransitioning = false;
        this.bandMembers = [];
        this.isPlaying = false;
        this.music = null;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            
            // Feral Toast band dialog group with speaker defined once
            feral: {
                speaker: 'Feral Toast',
            },
            
            // Initial dialog when entering the club
            feral_welcome: {
                text: "The band members of Feral Toast notice you entering the club. The lead guitarist nods in your direction. \"Hey there, fungal friend! We're about to start our rehearsal. Stick around for some mind-melting tunes!\"",
                options: [
                    { text: "I'd love to hear you play", next: "feral_play" },
                    { text: "What kind of music do you play?", next: "feral_style" },
                    { text: "Who are you all?", next: "feral_intro" },
                    { text: "I should go", next: "closeDialog" }
                ]
            },
            
            feral_style: {
                text: "\"We call it 'ultranoise futurepunk' - a blend of psychedelic noise with beats that don't exist... yet.\"",
                options: [
                    { text: "Sounds interesting. Play something!", next: "feral_play" },
                    { text: "Tell me about the band members", next: "feral_intro" },
                    { text: "I should go", next: "closeDialog" }
                ]
            },
            
            feral_intro: {
                text: "\"I'm Telka on guitar. That's Bass Player Xl on bass, we get him on sale. Fluffy Kārlis on drums, and Mira Dron on synth. Together we're Feral Toast - the most mind-expanding band in the underground. We make the best noise in town.\"",
                options: [
                    { text: "Let's hear some music!", next: "feral_play" },
                    { text: "What's your musical style?", next: "feral_style" },
                    { text: "I should go", next: "closeDialog" }
                ]
            },
            
            feral_play: {
                text: "\"Alright! Let's melt some minds with ultra noise!. Ready everyone? One, two, three, four!\"",
                options: [
                    { text: "...", next: "closeDialog" }
                ],
                onTrigger: function() {
                    // Start the performance
                    this.startPerformance();
                }
            },
            
            // Dialog after performance has started
            feral_during: {
                text: "The band is fully immersed in their rehearsal, creating something more than just noise. You can feel that there is something beyond that noise that... speaks to you. It's hard to articulate precisely, but you feel that once there was an entity which can be called maybe... The Noise God? Perhaps it's one of the god who came to die in the Upper Morkezela... and the noise is a remnant of it. The music connects directly to something primal in your mind.",
                options: [
                    { text: "Keep listening", next: "feral_experience" },
                    { text: "Leave the club", next: "closeDialog" }
                ]
            },
            
            feral_experience: {
                text: "As you continue listening, the noise seems to take physical form around you. Tendrils of sound weave through the air, creating a sort of cloud of consciousness. You feel a strange sense of unity with the Noise God.",
                options: [
                    { text: "This is incredible", next: "feral_insight" },
                    { text: "I need some air", next: "closeDialog" }
                ]
            },
            
            feral_insight: {
                text: "A profound insight washes over you: The Noise God was not born but assembled... Now, only hints of its pattern remain — buried in magnetic dust, resonating faintly through broken amplifiers, radio fog, and the bones of speakers. You sense that the band's music is a remnant of it, a way to connect with the Noise God.",
                options: [
                    { text: "...", next: "closeDialog" }
                ],
                onTrigger: function() {
                    // Add journal entry about this insight
                    this.addJournalEntry(
                        'noise_god_insight', 
                        'Noise God Insight', 
                        'During the Feral Toast rehearsal, I experienced a profound insight about the Noise God. During their set, the amplifiers began to hum in unison. Not feedback — not even mechanical. It was structured, deliberate, alive. A low harmonic, buried under the mix, pulsing at impossible intervals. I believe it was the Noise God who came to die here long time ago. He may be forgotten, but the noise is still alive.',
                        this.journalSystem.categories.LORE,
                    );
                    
                    // Show notification
                    this.showNotification('New Journal Entry', 'Noise God Insight');
                    
                    // Increase Growth slightly
                    this.modifyGrowthDecay(5, 0);
                }
            },
            
            // Fan dialogs removed as it's just a rehearsal
        };
    }

    preload() {
        // Call parent preload first
        super.preload();
        
        // Load scene-specific assets
        this.load.image('screamingCorkClubBg', 'assets/images/backgrounds/ScreamingCorkClub.png');
        
        // Load band member images
        this.load.image('feral_guitarist', 'assets/images/characters/feral_guitarist.png');
        this.load.image('feral_bassplayer', 'assets/images/characters/feral_bassplayer.png');
        this.load.image('feral_drummer', 'assets/images/characters/feral_drummer.png');
        this.load.image('feral_synth', 'assets/images/characters/feral_synth.png');
        
        // Load music
        this.load.audio('feral-toast', 'assets/sounds/feral-toast.mp3');
        
        // Load particle for visual effects
        this.load.image('sporeParticle', 'assets/images/effects/spore-particle.png');
        
        // If spore-particle.png doesn't exist, create a fallback
        this.load.once('loaderror', (fileObj) => {
            if (fileObj.key === 'sporeParticle') {
                console.log('Creating fallback spore particle');
                // Create a fallback particle texture
                const graphics = this.make.graphics({ x: 0, y: 0, add: false });
                graphics.fillStyle(0x7fff8e, 1);
                graphics.fillCircle(4, 4, 4);
                graphics.generateTexture('sporeParticle', 8, 8);
            }
        });
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();

        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkClubBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add ambient lighting effects
        this.createAmbientLighting();

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // Position the priest at the bottom when entering from ScreamingCorkInteriorScene
        this.priest.x = 400;
        this.priest.y = 520;

        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Create exit back to ScreamingCorkInteriorScene
        this.transitionManager.createTransitionZone(
            400, // x position
            550, // y position
            150, // width
            50, // height
            'down', // direction
            'ScreamingCorkInteriorScene', // target scene
            400, // walk to x
            500, // walk to y
            'Exit to Tavern' // custom name
        );
        
        // Create the band members
        this.createBandMembers();
        
        // Show welcome dialog after a short delay
        this.time.delayedCall(1000, () => {
            this.showDialog('feral_welcome');
        });
    }
    
    createAmbientLighting() {
        // Add a dark overlay to dim the scene
        const darkOverlay = this.add.rectangle(400, 300, 800, 600, 0x000000, 0.4);
        darkOverlay.setDepth(0);
        
        // Add stage lights using triangles instead of cones
        const stageLightLeft = this.add.graphics();
        stageLightLeft.fillStyle(0x7fff8e, 0.2);
        // Create a triangle for the left light beam
        stageLightLeft.beginPath();
        stageLightLeft.moveTo(200, 100);
        stageLightLeft.lineTo(100, 300);
        stageLightLeft.lineTo(300, 300);
        stageLightLeft.closePath();
        stageLightLeft.fillPath();
        stageLightLeft.setDepth(1);
        
        const stageLightRight = this.add.graphics();
        stageLightRight.fillStyle(0x7fff8e, 0.2);
        // Create a triangle for the right light beam
        stageLightRight.beginPath();
        stageLightRight.moveTo(600, 100);
        stageLightRight.lineTo(500, 300);
        stageLightRight.lineTo(700, 300);
        stageLightRight.closePath();
        stageLightRight.fillPath();
        stageLightRight.setDepth(1);
        
        // Add pulsating animation to the stage lights
        this.tweens.add({
            targets: [stageLightLeft, stageLightRight],
            alpha: { from: 0.2, to: 0.4 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }
    
    // Audience removed as it's just a rehearsal

    update() {
        super.update();
        
        // Update band animations if needed
        if (this.isPlaying) {
            this.updateBandAnimations();
        }
    }

    createBandMembers() {
        // Create band members with their positions on stage
        const bandConfig = [
            { key: 'feral_guitarist', x: 250, y: 350, scale: 0.18, name: 'Telca (Guitar/Vocals)' },
            { key: 'feral_bassplayer', x: 500, y: 350, scale: 0.18, name: 'Bass Player XL (Bass)' },
            { key: 'feral_drummer', x: 400, y: 330, scale: 0.18, name: 'Fluffy Kārlis (Drums)' },
            { key: 'feral_synth', x: 650, y: 330, scale: 0.18, name: 'Mira Dron (Synth)' }
        ];
        
        // Create each band member
        bandConfig.forEach(config => {
            const member = this.add.image(config.x, config.y, config.key);
            member.setScale(config.scale);
            member.setDepth(3);
            member.originalY = config.y; // Store original Y for animations
            member.originalScale = config.scale; // Store original scale for animations
            
            // Add name tag below the character
            const nameTag = this.add.text(config.x, config.y + 50, config.name, {
                fontSize: '14px',
                fill: '#7fff8e',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                padding: { x: 5, y: 3 }
            });
            nameTag.setOrigin(0.5);
            nameTag.setDepth(3);
            
            // Add subtle glow effect
            const glow = this.add.graphics();
            glow.fillStyle(0x7fff8e, 0.3);
            glow.fillCircle(config.x, config.y, 40);
            glow.setDepth(2);
            
            // Add pulsating animation to the glow
            this.tweens.add({
                targets: glow,
                alpha: { from: 0.3, to: 0.5 },
                scale: { from: 0.9, to: 1.1 },
                duration: 1500,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
            
            // Store references
            member.nameTag = nameTag;
            member.glow = glow;
            
            // Add to band members array
            this.bandMembers.push(member);
        });
        
        // Make the whole band interactive as a group
        const bandZone = this.add.zone(400, 320, 400, 200)
            .setInteractive({ useHandCursor: true })
            .setOrigin(0.5);
            
        bandZone.on('pointerdown', () => {
            if (this.dialogVisible) return;
            
            if (this.isPlaying) {
                this.showDialog('feral_during');
            } else {
                this.showDialog('feral_welcome');
            }
        });
    }
    
    startPerformance() {
        if (this.isPlaying) return; // Already playing
        
        this.isPlaying = true;
        
        // Show notification
        this.showNotification('Feral Toast begins playing', 'Mycelial Wave music fills the club');
        
        // Create visual effects for the performance
        this.createVisualEffects();
        
        // Play the music
        this.music = this.sound.add('feral-toast', {
            volume: 0.7,
            loop: true
        });
        this.music.play();
        
        // Start band animations
        this.bandMembers.forEach(member => {
            // Add playing animation
            this.addPlayingAnimation(member);
        });
        
        // Add audience reaction
        this.addJournalEntry(
            'feral_toast_performance', 
            'Feral Toast Concert', 
            'Experienced the mind-bending sounds of Feral Toast, an ultranoise futurepunk band at the Screaming Cork Club. Their raw, dirty punk-noise music sounds like a pinnacle of chaos. I liked it.', 
            this.journalSystem.categories.EVENTS,
        );
    }
    
    createVisualEffects() {
        // Create a spotlight effect
        const spotlight = this.add.graphics();
        spotlight.fillStyle(0xffffff, 0.2);
        spotlight.fillCircle(400, 320, 200);
        spotlight.setDepth(1);
        
        // Add pulsating animation to the spotlight
        this.tweens.add({
            targets: spotlight,
            alpha: { from: 0.2, to: 0.4 },
            scale: { from: 0.9, to: 1.1 },
            duration: 1200,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Create floating spore particles
        this.sporeEmitter = this.add.particles(0, 0, 'sporeParticle', {
            frame: 0,
            quantity: 2,
            frequency: 500,
            lifespan: 6000,
            gravityY: -10,
            scale: { start: 0.2, end: 0.1 },
            alpha: { start: 0.6, end: 0 },
            speed: { min: 20, max: 50 },
            angle: { min: 0, max: 360 },
            rotate: { min: 0, max: 360 },
            emitZone: {
                type: 'random',
                source: new Phaser.Geom.Rectangle(200, 200, 400, 200)
            }
        });
        this.sporeEmitter.setDepth(4);
        
        // Create color-changing overlay for psychedelic effect
        this.psychedelicOverlay = this.add.graphics();
        this.psychedelicOverlay.fillStyle(0x00ff00, 0.05);
        this.psychedelicOverlay.fillRect(0, 0, 800, 600);
        this.psychedelicOverlay.setDepth(10);
        
        // Animate the overlay colors
        this.time.addEvent({
            delay: 2000,
            callback: this.changeOverlayColor,
            callbackScope: this,
            loop: true
        });
    }
    
    changeOverlayColor() {
        if (!this.isPlaying) return;
        
        // Random psychedelic colors
        const colors = [0x00ff00, 0x0000ff, 0xff00ff, 0xffff00, 0x00ffff];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        
        this.tweens.add({
            targets: this.psychedelicOverlay,
            fillColor: { from: this.psychedelicOverlay.fillColor, to: randomColor },
            duration: 2000,
            ease: 'Sine.easeInOut',
            onUpdate: () => {
                this.psychedelicOverlay.clear();
                this.psychedelicOverlay.fillStyle(this.psychedelicOverlay.fillColor, 0.05);
                this.psychedelicOverlay.fillRect(0, 0, 800, 600);
            }
        });
    }
    
    addPlayingAnimation(bandMember) {
        // Different animation for each band member based on their instrument
        if (bandMember.texture.key === 'feral_guitarist') {
            // Guitarist animation - side to side movement with more energy
            this.tweens.add({
                targets: bandMember,
                x: { from: bandMember.x - 15, to: bandMember.x + 15 },
                angle: { from: -8, to: 8 },
                duration: 600,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
            
            // Add jumping effect occasionally
            this.time.addEvent({
                delay: 4000,
                callback: () => {
                    if (!this.isPlaying) return;
                    
                    this.tweens.add({
                        targets: bandMember,
                        y: { from: bandMember.originalY, to: bandMember.originalY - 30 },
                        duration: 200,
                        yoyo: true,
                        ease: 'Cubic.easeOut'
                    });
                },
                loop: true
            });
        } 
        else if (bandMember.texture.key === 'feral_bassplayer') {
            // Bass player animation - bobbing up and down with head movement
            this.tweens.add({
                targets: bandMember,
                y: { from: bandMember.originalY - 8, to: bandMember.originalY + 8 },
                duration: 600,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
            
            // Add head bobbing
            this.tweens.add({
                targets: bandMember,
                angle: { from: -4, to: 4 },
                duration: 300,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        else if (bandMember.texture.key === 'feral_drummer') {
            // Drummer animation - more energetic movement
            this.tweens.add({
                targets: bandMember,
                y: { from: bandMember.originalY - 12, to: bandMember.originalY + 5 },
                angle: { from: -5, to: 5 },
                duration: 200,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
            
            // Add occasional arm flourish
            this.time.addEvent({
                delay: 3000,
                callback: () => {
                    if (!this.isPlaying) return;
                    
                    this.tweens.add({
                        targets: bandMember,
                        scaleX: { from: bandMember.originalScale, to: bandMember.originalScale * 1.2 },
                        scaleY: { from: bandMember.originalScale, to: bandMember.originalScale * 1.2 },
                        duration: 200,
                        yoyo: true,
                        ease: 'Back.easeOut'
                    });
                },
                loop: true
            });
        }
        else if (bandMember.texture.key === 'feral_synth') {
            // Synth player animation - more dynamic swaying and movement
            this.tweens.add({
                targets: bandMember,
                angle: { from: -4, to: 4 },
                duration: 1200,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
            
            // Add subtle up and down movement
            this.tweens.add({
                targets: bandMember,
                y: { from: bandMember.originalY - 5, to: bandMember.originalY + 5 },
                duration: 1500,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        
        // Enhance the glow effect during performance
        if (bandMember.glow) {
            this.tweens.add({
                targets: bandMember.glow,
                alpha: { from: 0.3, to: 0.7 },
                scale: { from: 0.8, to: 1.3 },
                duration: 800,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        
        // Also animate the name tag to follow its character
        if (bandMember.nameTag) {
            this.tweens.add({
                targets: bandMember.nameTag,
                x: bandMember.x,
                y: bandMember.y + 50,
                duration: 100,
                repeat: -1
            });
        }
    }
    
    updateBandAnimations() {
        // This method can be used for any frame-by-frame animation updates
        // Currently using tweens for animations, so this is empty
    }
    
    shutdown() {
        // Stop the music when leaving the scene
        if (this.music && this.music.isPlaying) {
            this.music.stop();
        }
        
        // Clean up particles
        if (this.sporeEmitter) {
            this.sporeEmitter.destroy();
        }
        
        // Clean up visual effects
        if (this.psychedelicOverlay) {
            this.psychedelicOverlay.destroy();
        }
        
        // Add a journal entry about the experience if it was a first visit
        if (!this.hasJournalEntry('feral_toast_first_visit')) {
            this.addJournalEntry(
                'feral_toast_first_visit',
                'Feral Toast Rehearsal',
                'Visited the Screaming Cork Club and experienced a rehearsal by Feral Toast, an ultranoise futurepunk band.',
                this.journalSystem.categories.EVENTS,
            );
        }
        
        // Call parent shutdown
        super.shutdown();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScreamingCorkClubScene = ScreamingCorkClubScene;
}
