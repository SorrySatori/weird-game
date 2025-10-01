/**
 * InputScaleManager - Utility class to handle input scaling when using CSS transforms
 * This helps ensure that click/touch coordinates match the game coordinates when the canvas is scaled with CSS
 */
export default class InputScaleManager {
    /**
     * Initialize the input scale manager
     * @param {Phaser.Scene} scene - The scene to attach the input manager to
     */
    constructor(scene) {
        this.scene = scene;
        this.game = scene.game;
        
        // Initialize scale values
        this.scaleX = 1;
        this.scaleY = 1;
        this.offsetX = 0;
        this.offsetY = 0;
        
        // Calculate the initial scale
        this.calculateScale();
        
        // Add resize event listener to recalculate scale when window is resized
        window.addEventListener('resize', () => this.calculateScale());
        
        // Add our own input event listener to handle scaling
        this.setupInputListener();
        
        // Log that the input scale manager is initialized
        console.log('InputScaleManager initialized');
    }
    
    /**
     * Set up input event listener to handle coordinate scaling
     */
    setupInputListener() {
        // Get the canvas element
        const canvas = this.game.canvas;
        if (!canvas) return;
        
        // Store the original pointer down handler
        const originalPointerDownHandler = this.scene.input.manager.onPointerDown;
        
        // Override the pointer down handler
        this.scene.input.manager.onPointerDown = (event) => {
            // Get the original event
            const originalEvent = event.originalEvent;
            
            // Calculate the scaled coordinates
            const scaledX = (originalEvent.clientX - this.offsetX) / this.scaleX;
            const scaledY = (originalEvent.clientY - this.offsetY) / this.scaleY;
            
            // Update the event coordinates
            originalEvent.clientX = scaledX;
            originalEvent.clientY = scaledY;
            
            // Call the original handler
            originalPointerDownHandler.call(this.scene.input.manager, event);
        };
        
        // Store the original pointer move handler
        const originalPointerMoveHandler = this.scene.input.manager.onPointerMove;
        
        // Override the pointer move handler
        this.scene.input.manager.onPointerMove = (event) => {
            // Get the original event
            const originalEvent = event.originalEvent;
            
            // Calculate the scaled coordinates
            const scaledX = (originalEvent.clientX - this.offsetX) / this.scaleX;
            const scaledY = (originalEvent.clientY - this.offsetY) / this.scaleY;
            
            // Update the event coordinates
            originalEvent.clientX = scaledX;
            originalEvent.clientY = scaledY;
            
            // Call the original handler
            originalPointerMoveHandler.call(this.scene.input.manager, event);
        };
    }
    
    /**
     * Calculate the scale and offset based on the canvas element's CSS transform
     */
    calculateScale() {
        const canvas = this.game.canvas;
        if (!canvas) return;
        
        // Get the canvas bounds
        const canvasBounds = canvas.getBoundingClientRect();
        
        // Calculate the CSS scale
        this.scaleX = canvasBounds.width / 800;  // 800 is the base game width
        this.scaleY = canvasBounds.height / 600; // 600 is the base game height
        
        // Calculate the offset
        this.offsetX = canvasBounds.left;
        this.offsetY = canvasBounds.top;
        
        console.log(`Input scale updated: ${this.scaleX.toFixed(2)}x${this.scaleY.toFixed(2)}, Offset: ${this.offsetX.toFixed(0)},${this.offsetY.toFixed(0)}`);
    }
}
