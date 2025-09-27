export default class SceneTransitionManager {
    constructor(scene) {
        this.scene = scene;
        
        // Store references to all transition elements for cleanup
        this.transitionElements = [];
        
        // Define standard colors for transition indicators
        this.colors = {
            normal: 0xffb700,    // Bright amber color for better visibility
            hover: 0xffd700,     // Gold color for hover state
            glow: 0xff9500,      // Orange glow
            text: 0xffffff       // White text
        };
        
        // Add scene shutdown event to clean up resources
        this.scene.events.on('shutdown', this.cleanup, this);
    }
    
    /**
     * Clean up all transition elements when the scene shuts down
     */
    cleanup() {
        // Remove all event listeners and destroy all elements
        this.transitionElements.forEach(item => {
            // Remove resize listener
            if (item.elements && item.elements.resizeListener) {
                window.removeEventListener('resize', item.elements.resizeListener);
            }
            
            // Stop all tweens
            if (item.elements && item.elements.tweens) {
                item.elements.tweens.forEach(tween => {
                    if (tween && tween.stop) {
                        tween.stop();
                    }
                });
            }
            
            // Destroy containers
            if (item.elements && item.elements.arrowContainer) {
                item.elements.arrowContainer.destroy();
            }
            
            if (item.elements && item.elements.textContainer) {
                item.elements.textContainer.destroy();
            }
        });
        
        // Clear the array
        this.transitionElements = [];
    }

    createTransitionZone(x, y, width, height, direction, targetScene, walkX, walkY, destinationName = '') {
        // If no destination name is provided, create one from the target scene
        if (!destinationName) {
            // Convert camelCase to Title Case with spaces
            destinationName = targetScene
                .replace(/([A-Z])/g, ' $1') // Insert a space before all capital letters
                .replace(/^./, str => str.toUpperCase()) // Capitalize the first letter
                .replace(/Scene$/, '') // Remove 'Scene' suffix if present
                .trim();
            
            // If we still don't have a name (unlikely), use a generic one based on direction
            if (!destinationName) {
                const directionNames = {
                    'up': 'Go Up',
                    'down': 'Go Down',
                    'left': 'Go Left',
                    'right': 'Go Right'
                };
                destinationName = directionNames[direction] || 'Exit';
            }
        }
        
        // Create the interactive zone
        const zone = this.scene.add.zone(x, y, width, height)
            .setInteractive({ useHandCursor: true })
            .setOrigin(0.5)
            .setDepth(10);
            
        // Store the destination name for use in hover effect
        zone.destinationName = destinationName;
        zone.direction = direction;

        // Add the hover arrow effect
        const transitionElements = this.addHoverEffect(zone, direction);
        
        // Store references to the created elements
        this.transitionElements.push({
            zone,
            elements: transitionElements
        });

        // Add the transition logic
        zone.on('pointerdown', () => {
            if (this.scene.isTransitioning) return;
            this.scene.isTransitioning = true;

            const priest = this.scene.priest;
            priest.play('walk');
            this.scene.tweens.killTweensOf(priest);
            
            this.scene.tweens.add({
                targets: priest,
                x: walkX,
                y: walkY,
                duration: 1000,
                onComplete: () => {
                    this.scene.cameras.main.fadeOut(800, 0, 0, 0);
                    this.scene.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.scene.start(targetScene);
                        this.scene.isTransitioning = false;
                    });
                }
            });
        });

        return zone;
    }

    addHoverEffect(zone, direction) {
        // Get screen dimensions for positioning calculations
        const screenWidth = this.scene.sys.game.config.width;
        const screenHeight = this.scene.sys.game.config.height;
        
        // Create a container for the arrow and glow
        const arrowContainer = this.scene.add.container(zone.x, zone.y);
        arrowContainer.setDepth(20);
        
        // Create a shadow for the arrow - initially invisible
        const arrowShadow = this.scene.add.sprite(3, 3, 'arrow')
            .setScale(1.0)
            .setTint(0x000000)
            .setAlpha(0) // Initially invisible
            .setDepth(19);
            
        // Create the arrow with enhanced appearance - initially invisible
        const arrow = this.scene.add.sprite(0, 0, 'arrow')
            .setScale(1.0)
            .setTint(0xFFD700) // Gold color
            .setAlpha(0) // Initially invisible
            .setDepth(20);
        
        // Add a glow effect behind the arrow - initially invisible
        const glow = this.scene.add.graphics();
        glow.fillStyle(0xFFD700, 0.4); // Gold glow
        glow.fillCircle(0, 0, 40);
        glow.setAlpha(0); // Initially invisible
        
        // Add elements to the arrow container
        arrowContainer.add([glow, arrowShadow, arrow]);
        
        // Set arrow and shadow rotation based on direction
        switch(direction) {
            case 'left': 
                arrow.setAngle(180); 
                arrowShadow.setAngle(180);
                break;
            case 'right': 
                arrow.setAngle(0); 
                arrowShadow.setAngle(0);
                break;
            case 'up': 
                arrow.setAngle(270); 
                arrowShadow.setAngle(270);
                break;
            case 'down': 
                arrow.setAngle(90); 
                arrowShadow.setAngle(90);
                break;
        }
        
        // Process the destination name
        let displayText = zone.destinationName;
        if (displayText.length > 15) {
            if (displayText.includes(' ')) {
                // Split at spaces for multi-line display
                const words = displayText.split(' ');
                let line1 = '';
                let line2 = '';
                
                for (let i = 0; i < words.length; i++) {
                    if (line1.length <= line2.length && line1.length + words[i].length <= 15) {
                        line1 += (line1 ? ' ' : '') + words[i];
                    } else {
                        line2 += (line2 ? ' ' : '') + words[i];
                    }
                }
                
                displayText = line1 + '\n' + line2;
            } else {
                // Truncate if no spaces
                displayText = displayText.substring(0, 12) + '...';
            }
        }
        
        // Create a separate text container that's positioned independently
        // This is the key to solving the positioning issue
        const textContainer = this.scene.add.container(0, 0);
        textContainer.setDepth(30); // Above everything else
        
        // Create the text with background - initially invisible
        const text = this.scene.add.text(0, 0, displayText, {
            fontSize: '14px',
            fontFamily: 'Arial',
            fill: '#ffffff',
            align: 'center',
            fontStyle: 'bold',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: { x: 8, y: 4 }
        }).setOrigin(0.5).setAlpha(0); // Initially invisible
        
        // Add stroke to text
        text.setStroke('#000000', 2);
        
        // Add text to its container
        textContainer.add(text);
        
        // Function to position text properly based on screen boundaries
        const positionText = () => {
            // Start with a position based on the arrow direction
            let textX = zone.x;
            let textY = zone.y;
            
            // Position based on direction
            const offset = 50; // Distance from arrow
            
            switch(direction) {
                case 'up':
                    textY = zone.y - offset;
                    break;
                case 'down':
                    textY = zone.y + offset;
                    break;
                case 'left':
                    textX = zone.x - offset;
                    break;
                case 'right':
                    textX = zone.x + offset;
                    break;
            }
            
            // Check boundaries and adjust if needed
            const padding = 10; // Padding from screen edges
            const textWidth = text.width;
            const textHeight = text.height;
            
            // Check left edge
            if (textX - textWidth/2 < padding) {
                textX = padding + textWidth/2;
            }
            
            // Check right edge
            if (textX + textWidth/2 > screenWidth - padding) {
                textX = screenWidth - padding - textWidth/2;
            }
            
            // Check top edge
            if (textY - textHeight/2 < padding) {
                textY = padding + textHeight/2;
            }
            
            // Check bottom edge
            if (textY + textHeight/2 > screenHeight - padding) {
                textY = screenHeight - padding - textHeight/2;
            }
            
            // Update text container position
            textContainer.setPosition(textX, textY);
        };
        
        // Initial positioning
        positionText();
        
        // Store animation references but don't start them yet
        let arrowPulse = null;
        let shadowPulse = null;
        let glowPulse = null;
        
        // Add hover effects - show everything on hover
        zone.on('pointerover', () => {
            // Play sound if available
            if (this.scene.sound && this.scene.sound.get('hoverSound')) {
                this.scene.sound.play('hoverSound', { volume: 0.5 });
            }
            
            // Stop any existing animations
            this.scene.tweens.killTweensOf([arrow, arrowShadow, glow, text]);
            
            // Show and animate the arrow
            this.scene.tweens.add({
                targets: arrow,
                alpha: { from: 0, to: 1 }, // Fade in from invisible
                scale: { from: 0.8, to: 1.3 },
                duration: 300,
                ease: 'Back.easeOut'
            });
            
            // Show and animate the shadow with slight delay
            this.scene.tweens.add({
                targets: arrowShadow,
                alpha: { from: 0, to: 0.8 }, // Fade in from invisible
                scale: { from: 0.8, to: 1.3 },
                duration: 300,
                ease: 'Back.easeOut',
                delay: 50
            });
            
            // Show and animate the glow
            this.scene.tweens.add({
                targets: glow,
                alpha: { from: 0, to: 0.7 }, // Fade in from invisible
                scale: { from: 0.8, to: 1.3 },
                duration: 400,
                ease: 'Sine.easeOut'
            });
            
            // Start pulsating animations after initial appearance
            this.scene.time.delayedCall(300, () => {
                // Arrow pulsating
                const newArrowPulse = this.scene.tweens.add({
                    targets: arrow,
                    scale: { from: 1.2, to: 1.4 },
                    duration: 600,
                    ease: 'Sine.easeInOut',
                    yoyo: true,
                    repeat: -1
                });
                arrowPulse = newArrowPulse;
                
                // Shadow pulsating
                const newShadowPulse = this.scene.tweens.add({
                    targets: arrowShadow,
                    scale: { from: 1.2, to: 1.4 },
                    duration: 600,
                    ease: 'Sine.easeInOut',
                    yoyo: true,
                    repeat: -1,
                    delay: 100
                });
                shadowPulse = newShadowPulse;
                
                // Glow pulsating
                const newGlowPulse = this.scene.tweens.add({
                    targets: glow,
                    alpha: { from: 0.6, to: 0.9 },
                    scale: { from: 1.2, to: 1.4 },
                    duration: 800,
                    ease: 'Sine.easeInOut',
                    yoyo: true,
                    repeat: -1
                });
                glowPulse = newGlowPulse;
            });
            
            // Show and animate the text
            this.scene.tweens.add({
                targets: text,
                alpha: { from: 0, to: 1 }, // Fade in from invisible
                scale: { from: 0.8, to: 1.2 },
                duration: 400,
                ease: 'Back.easeOut'
            });
        });
        
        // Add pointer out effects - hide everything on pointer out
        zone.on('pointerout', () => {
            // Stop all tweens
            this.scene.tweens.killTweensOf([arrow, arrowShadow, glow, text]);
            
            if (arrowPulse && arrowPulse.stop) arrowPulse.stop();
            if (shadowPulse && shadowPulse.stop) shadowPulse.stop();
            if (glowPulse && glowPulse.stop) glowPulse.stop();
            
            // Fade out text
            this.scene.tweens.add({
                targets: text,
                alpha: 0, // Fade to invisible
                scale: 0.8,
                duration: 200,
                ease: 'Sine.easeIn'
            });
            
            // Fade out arrow
            this.scene.tweens.add({
                targets: arrow,
                alpha: 0, // Fade to invisible
                scale: 0.8,
                duration: 200,
                ease: 'Sine.easeIn'
            });
            
            // Fade out shadow
            this.scene.tweens.add({
                targets: arrowShadow,
                alpha: 0, // Fade to invisible
                scale: 0.8,
                duration: 200,
                ease: 'Sine.easeIn'
            });
            
            // Fade out glow
            this.scene.tweens.add({
                targets: glow,
                alpha: 0, // Fade to invisible
                scale: 0.8,
                duration: 300,
                ease: 'Sine.easeIn'
            });
        });
        
        // Add resize event listener to reposition text when the window is resized
        const resizeListener = () => positionText();
        window.addEventListener('resize', resizeListener);
        
        // Return all created elements for cleanup
        return {
            arrowContainer,
            textContainer,
            tweens: [], // We'll store tweens dynamically when they're created
            resizeListener,
            // Store references to add tweens later
            storeArrowPulse: (tween) => { arrowPulse = tween; },
            storeShadowPulse: (tween) => { shadowPulse = tween; },
            storeGlowPulse: (tween) => { glowPulse = tween; }
        };
    }
}
