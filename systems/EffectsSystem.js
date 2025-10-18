/**
 * Effects System
 * Manages visual and gameplay effects, including drug effects
 */
export default class EffectsSystem {
    constructor(scene) {
        this.scene = scene;
        this.activeEffects = [];
        this.effectsContainer = null;
        this.effectDuration = 180000; // Increased to 3 minutes (180000ms)
        this.effectTimer = null;
        this.effectStartTime = 0;
        this.currentDrugItem = null;
        this.commentInterval = null;
        this.sporeEffectInterval = null;
        
        // Psychedelic comments for each drug type
        this.drugComments = {
            grayOltrac: [
                "The walls are... breathing? Just a little bit.",
                "I can hear colors. Wait, that doesn't make sense.",
                "My fingers feel like they're made of mushrooms...",
                "Everything is slightly fuzzy around the edges.",
                "The spores are speaking to me in whispers.",
                "Is that shadow supposed to be dancing?"
            ],
            violetOltrac: [
                "The air is THICK with violet possibilities!",
                "My thoughts are growing like mycelium networks!",
                "I can SEE the connections between all things now!",
                "The fungal consciousness is showing me patterns everywhere!",
                "Time is folding in on itself like a spore cap!",
                "HARDCORE! Is this HARDCORE? I'm thinking so!"
            ],
            amberOltrac: [
                "THE VEIL IS TORN! I SEE BEYOND THE MEMBRANE OF REALITY!",
                "My body is dissolving into golden spores... MAGNIFICENT!",
                "The Eternal Mushroom speaks through me! I AM BECOME MYCELIUM!",
                "Stars are just the fruiting bodies of cosmic fungi! IT ALL MAKES SENSE!",
                "I've transcended my flesh prison! I AM EVERYWHERE AND NOWHERE!",
                "The universe is just one giant spore waiting to bloom!",
                "I want to go home... Wait... I'm already home."
            ]
        };
    }

    /**
     * Initialize the effects system
     */
    init() {
        // Create a container for visual effects
        this.effectsContainer = this.scene.add.container(0, 0);
        this.effectsContainer.setDepth(5000); // Very high depth to be above everything
        this.effectsContainer.setVisible(false);
        
        // Check if there's an active drug effect in the registry
        this.checkForActiveEffects();
    }
    
    /**
     * Check for active effects stored in the registry
     */
    checkForActiveEffects() {
        const activeEffect = this.scene.registry.get('activeDrugEffect');
        
        if (activeEffect) {
            console.log('Restoring active drug effect:', activeEffect.id);
            
            // Calculate remaining time
            const elapsedTime = Date.now() - activeEffect.startTime;
            const remainingTime = Math.max(0, this.effectDuration - elapsedTime);
            
            // If effect hasn't expired yet
            if (remainingTime > 0) {
                // Restore the effect
                this.currentDrugItem = activeEffect.item;
                this.effectStartTime = activeEffect.startTime;
                
                // Apply the effect without resetting the timer
                this.applyDrugEffectById(activeEffect.id, remainingTime);
            } else {
                // Effect has expired, clear it from registry
                this.scene.registry.remove('activeDrugEffect');
            }
        }
    }

    /**
     * Apply a drug effect based on the item used
     * @param {object} item - The drug item being used
     */
    applyDrugEffect(item) {
        // Clear any existing effects first
        this.clearEffects();
        
        console.log(`Applying drug effect for ${item.name}`);
        
        // Store the current item and start time
        this.currentDrugItem = item;
        this.effectStartTime = Date.now();
        
        // Store active effect in registry for persistence across scenes
        this.scene.registry.set('activeDrugEffect', {
            id: item.id,
            item: item,
            startTime: this.effectStartTime
        });
        
        // Apply effect based on drug type
        this.applyDrugEffectById(item.id, this.effectDuration);
        
        // Show notification
        if (this.scene.showNotification) {
            this.scene.showNotification(`Experiencing effects of ${item.name}...`);
        }
    }
    
    /**
     * Apply a drug effect by its ID with specified duration
     * @param {string} effectId - The effect ID to apply
     * @param {number} duration - Duration in milliseconds
     */
    applyDrugEffectById(effectId, duration) {
        // Apply effect based on drug type
        switch(effectId) {
            case 'grayOltrac':
                this.applyGrayOltracEffect();
                this.applyGameplayEffect(effectId, 'mild');
                break;
            case 'violetOltrac':
                this.applyVioletOltracEffect();
                this.applyGameplayEffect(effectId, 'medium');
                break;
            case 'amberOltrac':
                this.applyAmberOltracEffect();
                this.applyGameplayEffect(effectId, 'intense');
                break;
            default:
                console.warn(`No effect defined for effect ID: ${effectId}`);
                return;
        }
        
        // Start psychedelic comments
        this.startPsychedelicComments(effectId);
        
        // Set timer to clear effects
        if (this.effectTimer) {
            this.effectTimer.remove();
        }
        
        this.effectTimer = this.scene.time.delayedCall(duration, () => {
            this.clearEffects();
            if (this.scene.showNotification && this.currentDrugItem) {
                this.scene.showNotification(`The effects of ${this.currentDrugItem.name} have worn off.`);
            }
            // Clear from registry when effect expires naturally
            this.scene.registry.remove('activeDrugEffect');
        });
    }
    
    /**
     * Apply Gray Oltrac effect - mild visual distortion
     */
    applyGrayOltracEffect() {
        // Make effects container visible
        this.effectsContainer.setVisible(true);
        
        // Create semi-transparent overlay
        const overlay = this.scene.add.rectangle(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2,
            this.scene.cameras.main.width,
            this.scene.cameras.main.height,
            0x333333, 0.3
        );
        this.effectsContainer.add(overlay);
        
        // Add subtle pulsating effect
        this.scene.tweens.add({
            targets: overlay,
            alpha: { from: 0.3, to: 0.5 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add some floating particles
        for (let i = 0; i < 20; i++) {
            const x = Phaser.Math.Between(0, this.scene.cameras.main.width);
            const y = Phaser.Math.Between(0, this.scene.cameras.main.height);
            const size = Phaser.Math.Between(3, 8);
            
            const particle = this.scene.add.circle(x, y, size, 0xaaaaaa, 0.6);
            this.effectsContainer.add(particle);
            
            // Random floating movement
            this.scene.tweens.add({
                targets: particle,
                x: x + Phaser.Math.Between(-100, 100),
                y: y + Phaser.Math.Between(-100, 100),
                alpha: { from: 0.6, to: 0.2 },
                duration: Phaser.Math.Between(3000, 6000),
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        
        // Add the drug image as a semi-transparent overlay
        if (this.scene.textures.exists('grayOltrac')) {
            const drugImage = this.scene.add.image(
                this.scene.cameras.main.width / 2,
                this.scene.cameras.main.height / 2,
                'grayOltrac'
            );
            drugImage.setAlpha(0.15);
            drugImage.setBlendMode(Phaser.BlendModes.SCREEN);
            this.effectsContainer.add(drugImage);
            
            // Slow rotation
            this.scene.tweens.add({
                targets: drugImage,
                angle: 360,
                duration: 60000,
                repeat: -1
            });
        }
        
        // Add to active effects
        this.activeEffects.push('grayOltrac');
    }
    
    /**
     * Apply Violet Oltrac effect - enhanced perception with color shifts
     */
    applyVioletOltracEffect() {
        // Make effects container visible
        this.effectsContainer.setVisible(true);
        
        // Create violet-tinted overlay
        const overlay = this.scene.add.rectangle(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2,
            this.scene.cameras.main.width,
            this.scene.cameras.main.height,
            0x6a0dad, 0.2
        );
        this.effectsContainer.add(overlay);
        
        // Add pulsating effect
        this.scene.tweens.add({
            targets: overlay,
            alpha: { from: 0.2, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add more vivid floating particles
        for (let i = 0; i < 40; i++) {
            const x = Phaser.Math.Between(0, this.scene.cameras.main.width);
            const y = Phaser.Math.Between(0, this.scene.cameras.main.height);
            const size = Phaser.Math.Between(4, 12);
            
            // Random violet-themed colors
            const colors = [0x9400d3, 0x8a2be2, 0x9370db, 0x7b68ee, 0x6a5acd];
            const color = Phaser.Utils.Array.GetRandom(colors);
            
            const particle = this.scene.add.circle(x, y, size, color, 0.7);
            this.effectsContainer.add(particle);
            
            // More dynamic movement
            this.scene.tweens.add({
                targets: particle,
                x: x + Phaser.Math.Between(-200, 200),
                y: y + Phaser.Math.Between(-200, 200),
                alpha: { from: 0.7, to: 0.3 },
                scale: { from: 1, to: Phaser.Math.FloatBetween(0.5, 1.5) },
                duration: Phaser.Math.Between(2000, 5000),
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        
        // Add the drug image as a semi-transparent overlay
        if (this.scene.textures.exists('violetOltrac')) {
            const drugImage = this.scene.add.image(
                this.scene.cameras.main.width / 2,
                this.scene.cameras.main.height / 2,
                'violetOltrac'
            );
            drugImage.setAlpha(0.25);
            drugImage.setBlendMode(Phaser.BlendModes.SCREEN);
            this.effectsContainer.add(drugImage);
            
            // Slow rotation and pulsating
            this.scene.tweens.add({
                targets: drugImage,
                angle: 360,
                scale: { from: 1, to: 1.1 },
                duration: 40000,
                yoyo: true,
                repeat: -1
            });
        }
        
        // Add subtle camera shake
        this.scene.cameras.main.shake(this.effectDuration, 0.002);
        
        // Add to active effects
        this.activeEffects.push('violetOltrac');
    }
    
    /**
     * Apply Amber Oltrac effect - intense reality-bending visuals
     */
    applyAmberOltracEffect() {
        // Make effects container visible
        this.effectsContainer.setVisible(true);
        
        // Create amber-tinted overlay
        const overlay = this.scene.add.rectangle(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2,
            this.scene.cameras.main.width,
            this.scene.cameras.main.height,
            0xffbf00, 0.15
        );
        this.effectsContainer.add(overlay);
        
        // Add strong pulsating effect
        this.scene.tweens.add({
            targets: overlay,
            alpha: { from: 0.15, to: 0.35 },
            duration: 1000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add intense floating particles
        for (let i = 0; i < 60; i++) {
            const x = Phaser.Math.Between(0, this.scene.cameras.main.width);
            const y = Phaser.Math.Between(0, this.scene.cameras.main.height);
            const size = Phaser.Math.Between(5, 15);
            
            // Random amber-themed colors
            const colors = [0xffbf00, 0xdaa520, 0xffd700, 0xffa500, 0xff8c00];
            const color = Phaser.Utils.Array.GetRandom(colors);
            
            // Use a star shape for some particles
            let particle;
            if (i % 3 === 0) {
                particle = this.scene.add.star(x, y, 5, size, size/2, color, 0.8);
            } else {
                particle = this.scene.add.circle(x, y, size, color, 0.8);
            }
            
            this.effectsContainer.add(particle);
            
            // Complex movement
            this.scene.tweens.add({
                targets: particle,
                x: x + Phaser.Math.Between(-300, 300),
                y: y + Phaser.Math.Between(-300, 300),
                angle: Phaser.Math.Between(0, 360),
                alpha: { from: 0.8, to: 0.4 },
                scale: { from: 1, to: Phaser.Math.FloatBetween(0.5, 2) },
                duration: Phaser.Math.Between(1500, 4000),
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        
        // Add the drug image as a semi-transparent overlay
        if (this.scene.textures.exists('amberOltrac')) {
            const drugImage = this.scene.add.image(
                this.scene.cameras.main.width / 2,
                this.scene.cameras.main.height / 2,
                'amberOltrac'
            );
            drugImage.setAlpha(0.3);
            drugImage.setBlendMode(Phaser.BlendModes.SCREEN);
            this.effectsContainer.add(drugImage);
            
            // Complex animation
            this.scene.tweens.add({
                targets: drugImage,
                angle: 720,
                scale: { from: 1, to: 1.2 },
                alpha: { from: 0.3, to: 0.5 },
                duration: 30000,
                yoyo: true,
                repeat: -1
            });
        }
        
        // Add more intense camera effects
        this.scene.cameras.main.shake(this.effectDuration, 0.004);
        this.scene.cameras.main.flash(1000, 255, 191, 0, true);
        
        // Add reality-warping effect (screen distortion)
        // This would ideally use a shader, but we'll simulate with scaling
        const gameObjects = this.scene.children.list.filter(obj => 
            obj !== this.effectsContainer && 
            obj.type === 'Container' || 
            obj.type === 'Sprite' || 
            obj.type === 'Image'
        );
        
        gameObjects.forEach(obj => {
            if (obj.setScale) {
                const originalScale = obj.scale;
                this.scene.tweens.add({
                    targets: obj,
                    scaleX: originalScale * Phaser.Math.FloatBetween(0.95, 1.05),
                    scaleY: originalScale * Phaser.Math.FloatBetween(0.95, 1.05),
                    duration: Phaser.Math.Between(2000, 4000),
                    yoyo: true,
                    repeat: Math.ceil(this.effectDuration / 4000),
                    ease: 'Sine.easeInOut'
                });
            }
        });
        
        // Add to active effects
        this.activeEffects.push('amberOltrac');
    }
    
    /**
     * Clear all active effects
     * @param {boolean} clearRegistry - Whether to also clear from registry
     */
    clearEffects(clearRegistry = true) {
        // Stop any existing effect timer
        if (this.effectTimer) {
            this.effectTimer.remove();
            this.effectTimer = null;
        }
        
        // Stop comment and spore effect intervals
        if (this.commentInterval) {
            this.commentInterval.remove();
            this.commentInterval = null;
        }
        
        if (this.sporeEffectInterval) {
            this.sporeEffectInterval.remove();
            this.sporeEffectInterval = null;
        }
        
        // Clear all effects
        if (this.effectsContainer) {
            this.effectsContainer.removeAll(true);
            this.effectsContainer.setVisible(false);
        }
        
        // Reset camera effects
        this.scene.cameras.main.resetFX();
        
        // Clear active effects list
        this.activeEffects = [];
        
        // Clear current drug item
        this.currentDrugItem = null;
        
        // Clear from registry if specified
        if (clearRegistry) {
            this.scene.registry.remove('activeDrugEffect');
        }
    }
    
    /**
     * Check if a specific effect is active
     * @param {string} effectId - The effect ID to check
     * @returns {boolean} - Whether the effect is active
     */
    hasActiveEffect(effectId) {
        return this.activeEffects.includes(effectId);
    }
    
    /**
     * Apply gameplay effects based on drug type
     * @param {string} drugId - The drug ID
     * @param {string} intensity - The intensity level (mild, medium, intense)
     */
    applyGameplayEffect(drugId, intensity) {
        // Get the spore system if available
        const sporeSystem = this.scene.registry.get('sporeSystem');
        if (!sporeSystem) {
            console.warn('SporeSystem not found in registry, cannot apply gameplay effects');
            return;
        }
        
        // Apply initial spore effect based on drug type - now with randomness
        let maxInitialChange = 0;
        switch(drugId) {
            case 'grayOltrac':
                maxInitialChange = 8; // Small effect range (-8 to +8)
                break;
            case 'violetOltrac':
                maxInitialChange = 15; // Medium effect range (-15 to +15)
                break;
            case 'amberOltrac':
                maxInitialChange = 25; // Large effect range (-25 to +25)
                break;
        }
        
        // Generate random initial effect (can be positive or negative)
        const initialEffect = Math.floor(Math.random() * (maxInitialChange * 2 + 1)) - maxInitialChange;
        
        // Apply the initial spore change
        sporeSystem.modifySpores(initialEffect);
        console.log(`[EffectsSystem] Initial ${drugId} effect: ${initialEffect} spores`);
        
        // Show a notification about the spore change
        const effectMessage = initialEffect > 0 ? 
            `You feel the spores multiplying within you. (+${initialEffect})` : 
            `You feel the spores receding from your system. (${initialEffect})`;
        this.scene.showNotification(effectMessage, '', '', 3000);
        
        // Set up interval for random spore fluctuations
        const intervalTime = intensity === 'intense' ? 15000 : 
                            intensity === 'medium' ? 25000 : 35000;
        
        // Clear any existing interval
        if (this.sporeEffectInterval) {
            this.sporeEffectInterval.remove();
        }
        
        // Create new interval for random effects
        this.sporeEffectInterval = this.scene.time.addEvent({
            delay: intervalTime,
            callback: () => {
                // Random spore fluctuation based on intensity
                const maxChange = intensity === 'intense' ? 10 : 
                                intensity === 'medium' ? 7 : 4;
                                
                const change = Math.floor(Math.random() * (maxChange * 2 + 1)) - maxChange;
                
                if (change !== 0) {
                    sporeSystem.modifySpores(change);
                    console.log(`[EffectsSystem] Random spore fluctuation: ${change}`);
                    
                    // For significant changes, show a notification
                    const significantThreshold = intensity === 'intense' ? 7 : 
                                               intensity === 'medium' ? 5 : 3;
                    
                    if (Math.abs(change) >= significantThreshold) {
                        const fluctMessage = change > 0 ? 
                            `A wave of fungal energy surges through you! (+${change})` : 
                            `You feel a sudden loss of spore connection! (${change})`;
                        this.scene.showNotification(fluctMessage, '', '', 2000);
                    }
                }
            },
            callbackScope: this,
            loop: true
        });
    }
    
    /**
     * Start displaying random psychedelic comments
     * @param {string} drugId - The drug ID
     */
    startPsychedelicComments(drugId) {
        // Clear any existing interval
        if (this.commentInterval) {
            this.commentInterval.remove();
        }
        
        // Get comments for this drug type
        const comments = this.drugComments[drugId];
        if (!comments || !comments.length) {
            console.warn(`No comments found for drug: ${drugId}`);
            return;
        }
        
        // Show first comment immediately
        const firstComment = comments[Math.floor(Math.random() * comments.length)];
        this.scene.showNotification(firstComment, '', '', 3000);
        
        // Set interval for random comments
        const intervalTime = drugId === 'amberOltrac' ? 20000 : 
                           drugId === 'violetOltrac' ? 30000 : 40000;
        
        this.commentInterval = this.scene.time.addEvent({
            delay: intervalTime,
            callback: () => {
                // Get a random comment
                const comment = comments[Math.floor(Math.random() * comments.length)];
                this.scene.showNotification(comment, '', '', 3000);
            },
            callbackScope: this,
            loop: true
        });
    }
    
    /**
     * Clean up resources
     * @param {boolean} preserveEffect - Whether to preserve the effect in registry
     */
    cleanup(preserveEffect = true) {
        // Clear effects but don't remove from registry if preserveEffect is true
        this.clearEffects(!preserveEffect);
        
        if (this.effectsContainer) {
            this.effectsContainer.destroy();
            this.effectsContainer = null;
        }
    }
    
    /**
     * Get active effects data for serialization
     * @returns {Object} Data that can be serialized to JSON
     */
    getActiveEffects() {
        return {
            activeEffects: this.activeEffects.map(effect => ({
                type: effect.type,
                intensity: effect.intensity,
                startTime: effect.startTime,
                duration: effect.duration,
                itemId: effect.itemId
            })),
            effectStartTime: this.effectStartTime,
            currentDrugItem: this.currentDrugItem
        };
    }
    
    /**
     * Load effects from saved data
     * @param {Object} data - Effects data from save file
     */
    loadEffects(data) {
        if (!data) return;
        
        // Clear current effects
        this.clearEffects(true);
        
        // Restore effect state
        if (data.effectStartTime) {
            this.effectStartTime = data.effectStartTime;
        }
        
        if (data.currentDrugItem) {
            this.currentDrugItem = data.currentDrugItem;
        }
        
        // Restore active effects
        if (data.activeEffects && Array.isArray(data.activeEffects)) {
            // Calculate how much time has passed since the save
            const now = Date.now();
            const timePassed = now - this.effectStartTime;
            
            data.activeEffects.forEach(effectData => {
                // Only restore effects that haven't expired
                if (timePassed < effectData.duration) {
                    // Apply the effect with remaining duration
                    const remainingDuration = effectData.duration - timePassed;
                    this.applyEffect(effectData.type, effectData.intensity, remainingDuration, effectData.itemId);
                }
            });
        }
    }
}
