/**
 * ScalingManager - Utility class to handle responsive scaling across all game scenes
 */
export default class ScalingManager {
    /**
     * Create a background that fills the screen
     * @param {Phaser.Scene} scene - The scene to add the background to
     * @param {string} textureKey - The key of the texture to use for the background
     * @returns {Phaser.GameObjects.Image} The created background image
     */
    static createFullScreenBackground(scene, textureKey) {
        const bg = scene.add.image(400, 300, textureKey);
        bg.setDisplaySize(800, 600);
        return bg;
    }
    
    /**
     * Create a text object
     * @param {Phaser.Scene} scene - The scene to add the text to
     * @param {number} x - The x position
     * @param {number} y - The y position
     * @param {string} text - The text content
     * @param {number} fontSize - The font size
     * @param {string} color - The text color
     * @returns {Phaser.GameObjects.Text} The created text object
     */
    static createText(scene, x, y, text, fontSize = 16, color = '#ffffff') {
        const textObj = scene.add.text(x, y, text, {
            fontSize: fontSize + 'px',
            fill: color,
            fontFamily: 'Arial'
        });
        textObj.setOrigin(0.5);
        
        return textObj;
    }
    
    /**
     * Create a button
     * @param {Phaser.Scene} scene - The scene to add the button to
     * @param {number} x - The x position
     * @param {number} y - The y position
     * @param {number} width - The width
     * @param {number} height - The height
     * @param {string} text - The button text
     * @param {Function} callback - The callback function when clicked
     * @returns {Object} Object containing the button background and text
     */
    static createButton(scene, x, y, width, height, text, callback) {
        // Create button background
        const bg = scene.add.rectangle(x, y, width, height, 0x0a2712, 0.4);
        bg.setStrokeStyle(2, 0x7fff8e);
        bg.setInteractive({ useHandCursor: true });
        bg.setDepth(1);
        
        // Create button text
        const textObj = scene.add.text(x, y, text, {
            fontSize: '24px',
            fill: '#7fff8e',
            fontFamily: 'Arial'
        });
        textObj.setOrigin(0.5);
        
        // Add hover effects
        bg.on('pointerover', () => {
            bg.setFillStyle(0x0a2712, 0.6);
            textObj.setStyle({ fill: '#2fff91' });
            if (scene.hoverSound) scene.hoverSound.play();
        });
        
        bg.on('pointerout', () => {
            bg.setFillStyle(0x0a2712, 0.4);
            textObj.setStyle({ fill: '#7fff8e' });
        });
        
        // Add click handler
        bg.on('pointerdown', () => {
            if (scene.clickSound) scene.clickSound.play();
            callback();
        });
        
        return { background: bg, text: textObj };
    }
}
