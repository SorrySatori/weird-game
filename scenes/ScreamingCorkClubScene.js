import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

/**
 * Feral Toast as pixel-art sheets taken from their original art (tools/artgen/feral_px.py → assets/aseprite/
 * FeralToast_*.aseprite → feral_export.lua): 128×192, frames 0-3 idle, 4-11 playing. Shown at scale 1; `y` is the
 * feet line (the soles sit 2 px above the frame's bottom). The playing loop runs two frames per beat of
 * feral-toast.mp3 (≈177 BPM).
 */
const BAND = [
    { key: 'ft_telka', file: 'telka', w: 128, h: 192, fx: 0.24, y: 470, name: 'Telka' },
    { key: 'ft_karlis', file: 'karlis', w: 144, h: 192, fx: 0.39, y: 452, name: 'Fluffy Kārlis' },
    { key: 'ft_bass_xl', file: 'bass_xl', w: 128, h: 192, fx: 0.55, y: 470, name: 'Bass Player XL' },
    { key: 'ft_mira', file: 'mira', w: 128, h: 192, fx: 0.71, y: 452, name: 'Mira Dron' }
];
const BAND_IDLE = [0, 0, 0, 1, 1, 2, 2, 2, 1, 3];   // calm: breathe, look about, blink
const BAND_BPM = 177;

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
                    { text: "I'd love to hear you play", key: 'id_love_to_hear_you_play', next: "feral_play" },
                    { text: "What kind of music do you play?", key: 'what_kind_of_music_do_you_play', next: "feral_style" },
                    { text: "Who are you all?", key: 'who_are_you_all', next: "feral_intro" },
                ]
            },
            
            feral_style: {
                text: "\"We call it 'ultranoise futurepunk' — a blend of psychedelic noise with beats that don't exist... yet.\"",
                options: [
                    { text: "Sounds interesting. Play something!", key: 'sounds_interesting_play_something', next: "feral_play" },
                    { text: "Tell me about the band members", key: 'tell_me_about_the_band_members', next: "feral_intro" },
                ]
            },
            
            feral_intro: {
                text: "\"I'm Telka on guitar. That's Bass Player XL on bass, we got him on sale. Fluffy Kārlis on drums, and Mira Dron on synth. Together we're Feral Toast — the most mind-expanding band in the underground. We make the best noise in town.\"",
                options: [
                    { text: "Let's hear some music!", key: 'lets_hear_some_music', next: "feral_play" },
                    { text: "What's your musical style?", key: 'whats_your_musical_style', next: "feral_style" },
                ]
            },
            
            feral_during: {
                text: "Telka shouts over the wall of sound without missing a chord. \"Not now, fungal friend — we're mid-set! Just listen!\"",
                options: [
                    { text: "(Listen.)", key: 'listen', next: "closeDialog" }
                ]
            },

            feral_play: {
                text: "\"Alright! Let's melt some minds with ultra noise! Ready everyone? One, two, three, four!\"",
                options: [],
                onTrigger: function() {
                    // Store a reference to the scene for use in the callback
                    const scene = this;
                    
                    // Use a short delay to ensure dialog closes properly
                    this.time.delayedCall(100, () => {
                        // Start the performance
                        scene.startPerformance();
                        
                        // Force close any open dialog
                        if (scene.dialogBox) {
                            scene.dialogBox.destroy();
                            scene.dialogBox = null;
                            scene.dialogVisible = false;
                            
                            // Update dialog visibility in player movement system
                            if (scene.playerMovementSystem) {
                                scene.playerMovementSystem.setDialogVisible(false);
                            }
                            
                            // Hide avatar if present
                            if (scene.avatar) {
                                scene.avatar.setVisible(false);
                            }
                            
                            // Destroy text mask if it exists
                            if (scene.textMaskGraphics) {
                                scene.textMaskGraphics.destroy();
                                scene.textMaskGraphics = null;
                            }
                        }
                    });
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
        
        // Band member sheets (see BAND)
        BAND.forEach(m => this.load.spritesheet(m.key, `assets/images/characters/feral_toast/${m.file}.png`, { frameWidth: m.w, frameHeight: m.h }));
        
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
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own floor and stage (tools/artgen/club_bg.py); drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
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
            this.t('ui.hints.exitToTavern') // custom name
        );
        
        // Create the band members
        this.createBandMembers();
        
        // Show welcome dialog after a short delay
        this.time.delayedCall(1000, () => {
            this.showDialog('feral_welcome');
        });
    }
    
    createAmbientLighting() {
        // A light dim over the cellar (the background is dark already)
        const darkOverlay = this.add.rectangle(this.scale.width / 2, this.scale.height / 2, this.scale.width, this.scale.height, 0x000000, 0.15);
        darkOverlay.setDepth(0);
        
        // Stage lights: a soft cone from each of the three lamps hanging over the stage down onto the boards
        // (lamp positions as shares of the canvas width; club_bg.py hangs the lamps there, shades ending at y 118;
        // beams layered narrow → wide).
        this.stageLights = [0.255, 0.483, 0.738].map(fx => {
            const x = Math.round(this.scale.width * fx);
            const beam = this.add.graphics().setDepth(1).setBlendMode(Phaser.BlendModes.ADD);
            for (const [top, bottom, alpha] of [[10, 80, 0.035], [7, 60, 0.045], [4, 38, 0.055]]) {
                beam.fillStyle(0x7fff8e, alpha);
                beam.fillPoints([
                    { x: x - top, y: 118 }, { x: x + top, y: 118 },
                    { x: x + bottom, y: 468 }, { x: x - bottom, y: 468 }
                ], true);
            }
            beam.fillStyle(0x7fff8e, 0.06);
            beam.fillEllipse(x, 466, 170, 26);                  // where the beam lands on the boards
            return beam;
        });
        this.tweens.add({
            targets: this.stageLights,
            alpha: { from: 0.75, to: 1 },
            duration: 2400,
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
    
    stop() {
        // Make sure to stop the music when the scene stops
        if (this.music) {
            this.music.stop();
        }
        
        // End the performance if it's still playing
        if (this.isPlaying) {
            this.isPlaying = false;
        }
        
        // Call parent stop method
        super.stop();
    }

    createBandMembers() {
        this.bandMembers = []; // the scene instance is re-used between visits
        BAND.forEach(cfg => {
            if (!this.anims.exists(`${cfg.key}_idle`)) {
                this.anims.create({ key: `${cfg.key}_idle`, frames: BAND_IDLE.map(f => ({ key: cfg.key, frame: f })), frameRate: 4, repeat: -1 });
                this.anims.create({ key: `${cfg.key}_play`, frames: this.anims.generateFrameNumbers(cfg.key, { start: 4, end: 11 }), frameRate: BAND_BPM * 2 / 60, repeat: -1 });
            }
            const x = Math.round(this.scale.width * cfg.fx);
            const member = this.add.sprite(x, cfg.y + 2, cfg.key, 0).setOrigin(0.5, 1).setDepth(cfg.y > 460 ? 4 : 3);
            member.play({ key: `${cfg.key}_idle`, startFrame: Phaser.Math.Between(0, BAND_IDLE.length - 1) });
            this.addGroundShadow(x, cfg.y - 3, cfg.w * 0.6, 10);

            // A pool of stage light on the boards at their feet (brightens while they play)
            const glow = this.add.ellipse(x, cfg.y - 3, cfg.w * 0.95, 26, 0x7fff8e, 0.12)
                .setBlendMode(Phaser.BlendModes.ADD)
                .setDepth(2);
            this.tweens.add({ targets: glow, alpha: { from: 0.1, to: 0.18 }, duration: 2400, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });

            const nameTag = this.add.text(x, cfg.y + 8, cfg.name, {
                fontSize: '13px',
                fill: '#7fff8e',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                padding: { x: 5, y: 2 }
            }).setOrigin(0.5, 0).setDepth(5);

            member.bandKey = cfg.key;
            member.nameTag = nameTag;
            member.glow = glow;
            this.bandMembers.push(member);
        });

        // The whole band is clickable as one group (the stage, from Telka to Mira)
        const left = Math.round(this.scale.width * BAND[0].fx) - 80, right = Math.round(this.scale.width * BAND[3].fx) + 90;
        const bandZone = this.add.zone((left + right) / 2, 370, right - left, 200)
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
        this.sound.stopAll();

        this.isPlaying = true;
        
        // Show notification
        this.showNotification(this.t('club.beginsTitle'), this.t('club.beginsSub'));
        
        // Create visual effects for the performance
        this.createVisualEffects();
        
        // Play the music - only once, not looped
        this.music = this.sound.add('feral-toast', {
            volume: 0.7,
            loop: false
        });
        this.music.play();
        
        // When music ends, stop the performance
        this.music.once('complete', () => {
            this.endPerformance();
        });
        
        // Start band animations
        this.bandMembers.forEach(member => {
            // Add playing animation
            this.addPlayingAnimation(member);
        });
        
        // Show text gradually during the performance
        this.showPerformanceText();
        
        // Add journal entry
        this.addJournalEntry(
            'feral_toast_performance', 
            'Feral Toast Concert', 
            'Experienced the mind-bending sounds of Feral Toast, an ultranoise futurepunk band at the Screaming Cork Club. Their raw, dirty punk-noise music sounds like a pinnacle of chaos. I liked it.', 
            this.journalSystem.categories.EVENTS,
        );
        
        // Add the Noise God insight journal entry after a delay
        this.time.delayedCall(15000, () => {
            this.addJournalEntry(
                'noise_god_insight', 
                'Noise God Insight', 
                'During the Feral Toast rehearsal, I experienced a profound insight about the Noise God. During their set, the amplifiers began to hum in unison. Not feedback — not even mechanical. It was structured, deliberate, alive. A low harmonic, buried under the mix, pulsing at impossible intervals. I believe it was the Noise God who came to die here a long time ago. He may be forgotten, but the noise is still alive.',
                this.journalSystem.categories.LORE,
            );
            
            // Increase Growth slightly
            this.modifyGrowthDecay(5, 0);
        });
    }
    
    showPerformanceText() {
        // Create a text container for the performance narrative
        const textContainer = this.add.container(this.scale.width / 2, 150);
        textContainer.setDepth(100);
        
        // Add semi-transparent background
        const textBg = this.add.rectangle(0, 0, 600, 100, 0x000000, 0.7);
        textBg.setStrokeStyle(1, 0x7fff8e);
        textContainer.add(textBg);
        
        // Add text with no content yet
        const text = this.add.text(0, 0, '', {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'center',
            wordWrap: { width: 580 }
        });
        text.setOrigin(0.5);
        textContainer.add(text);
        
        // Store reference
        this.performanceText = text;
        this.performanceTextContainer = textContainer;
        
        // Make container initially invisible
        textContainer.setAlpha(0);
        
        // Define the narrative texts to show during performance
        // Localized narrative (array in lang/*/game.js → club.performance)
        const narrativeTexts = this.t('club.performance');
        
        // Show each text with a delay between them
        let delay = 3000; // Start after 3 seconds
        let duration = 6000; // Each text stays for 5 seconds
        
        // Fade in the container
        this.tweens.add({
            targets: textContainer,
            alpha: 1,
            duration: 1000,
            ease: 'Power2'
        });
        
        // Show each narrative text in sequence
        narrativeTexts.forEach((narrativeText, index) => {
            this.time.delayedCall(delay, () => {
                if (!this.isPlaying) return; // Skip if performance ended
                
                // Fade out previous text
                this.tweens.add({
                    targets: text,
                    alpha: 0,
                    duration: 500,
                    onComplete: () => {
                        // Set new text
                        text.setText(narrativeText);
                        
                        // Fade in new text
                        this.tweens.add({
                            targets: text,
                            alpha: 1,
                            duration: 500
                        });
                    }
                });
                
                // If this is the last text, fade out the container after it's done
                if (index === narrativeTexts.length - 1) {
                    this.time.delayedCall(duration, () => {
                        this.tweens.add({
                            targets: textContainer,
                            alpha: 0,
                            duration: 1000,
                            ease: 'Power2'
                        });
                    });
                }
            });
            
            delay += duration; // Increase delay for next text
        });
    }
    
    endPerformance() {
        if (!this.isPlaying) return;
        
        this.isPlaying = false;
        
        // Back to their idle loops, the stage light calms down
        this.bandMembers.forEach(member => {
            if (!member.scene) return;
            member.play({ key: `${member.bandKey}_idle`, startFrame: Phaser.Math.Between(0, BAND_IDLE.length - 1) });
            if (member.glow) {
                this.tweens.killTweensOf(member.glow);
                member.glow.setAlpha(0.12);
            }
        });
        
        // Hide performance text if still visible
        if (this.performanceTextContainer) {
            this.tweens.add({
                targets: this.performanceTextContainer,
                alpha: 0,
                duration: 500,
                onComplete: () => {
                    this.performanceTextContainer.destroy();
                    this.performanceTextContainer = null;
                    this.performanceText = null;
                }
            });
        }
        
        // Show notification
        this.showNotification(this.t('club.endsTitle'), this.t('club.endsSub'));
    }
    
    createVisualEffects() {
        // Create a spotlight effect
        const spotlight = this.add.graphics();
        spotlight.fillStyle(0xffffff, 0.2);
        spotlight.fillCircle(this.scale.width / 2, 340, 260);
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
                source: new Phaser.Geom.Rectangle(this.scale.width * 0.2, 220, this.scale.width * 0.6, 220)
            }
        });
        this.sporeEmitter.setDepth(4);
        
        // Create color-changing overlay for psychedelic effect
        this.psychedelicOverlay = this.add.graphics();
        this.psychedelicOverlay.fillStyle(0x00ff00, 0.05);
        this.psychedelicOverlay.fillRect(0, 0, this.scale.width, this.scale.height);
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
                this.psychedelicOverlay.fillRect(0, 0, this.scale.width, this.scale.height);
            }
        });
    }
    
    addPlayingAnimation(bandMember) {
        // Frame animation on the beat (no tween rotations — they smear pixel art); the light pool brightens
        bandMember.play(`${bandMember.bandKey}_play`);
        if (bandMember.glow) {
            this.tweens.killTweensOf(bandMember.glow);
            this.tweens.add({
                targets: bandMember.glow,
                alpha: { from: 0.18, to: 0.34 },
                duration: 60000 / BAND_BPM,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
    }

    updateBandAnimations() {
        // This method can be used for any frame-by-frame animation updates
        // Currently using tweens for animations, so this is empty
    }
    
    shutdown() {
        // End the performance if it's still playing
        if (this.isPlaying) {
            this.endPerformance();
        }
        this.sound.stopAll();
        // Stop the music when leaving the scene (extra safety check)
        if (this.music) {
            this.music.stop();
            this.music.destroy();
            this.music = null;
        }
        
        // Clean up particles
        if (this.sporeEmitter) {
            this.sporeEmitter.destroy();
            this.sporeEmitter = null;
        }
        
        // Clean up visual effects
        if (this.psychedelicOverlay) {
            this.psychedelicOverlay.destroy();
            this.psychedelicOverlay = null;
        }
        
        // Clean up performance text if it exists
        if (this.performanceTextContainer) {
            this.performanceTextContainer.destroy();
            this.performanceTextContainer = null;
            this.performanceText = null;
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
