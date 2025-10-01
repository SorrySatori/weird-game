import LoadingScene from './scenes/LoadingScene.js';
import MainScene from './scenes/MainScene.js';
import EntryScene from './scenes/EntryScene.js';
import GameScene from './scenes/GameScene.js';
import EggCatedralScene from './scenes/EggCatedralScene.js';
import CathedralEntrance from './scenes/CathedralEntrance.js';
import VoxMarket from './scenes/VoxMarket.js';
import VoxmarketMarketScene from './scenes/VoxmarketMarketScene.js';
import VoxmarketHallScene from './scenes/VoxmarketHallScene.js';
import CrossroadScene from './scenes/CrossroadScene.js';
import ScraperScene from './scenes/ScraperScene.js';
import Shed521Scene from './scenes/Shed521Scene.js';
import Shed521FloorsScene from './scenes/Shed521FloorsScene.js';
import Shed521GateScene from './scenes/Shed521GateScene.js';
import ShedRegistrationScene from './scenes/ShedRegistrationScene.js';
import ShedApplicationsScene from './scenes/ShedApplicationsScene.js';
import ShedAbandonedOfficeScene from './scenes/ShedAbandonedOfficeScene.js';
import ShedHallScene from './scenes/ShedHallScene.js';
import ShedCourtyardScene from './scenes/ShedCourtyardScene.js';
import ScreamingCorkScene from './scenes/ScreamingCorkScene.js';
import ScreamingCorkInteriorScene from './scenes/ScreamingCorkInteriorScene.js';
import BurningBearStreetScene from './scenes/BurningBearStreetScene.js';
import SkyshipBoardScene from './scenes/SkyshipBoardScene.js';
import IntroScene from './scenes/IntroScene.js';
import TransitionScene from './scenes/TransitionScene.js';
import ScraperInteriorScene from './scenes/ScraperInteriorScene.js';
import ScraperAmbraScene from './scenes/ScraperAmbraScene.js';
import ScraperBackyardScene from './scenes/ScraperBackyardScene.js';
import AbandonedBusScene from './scenes/AbandonedBusScene.js';

const config = {
    // Force Canvas renderer to avoid WebGL framebuffer issues
    type: Phaser.CANVAS,
    // Base game size - this is the size the game is designed for
    width: 800,
    height: 600,
    parent: 'game-container',
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 },
            debug: false
        }
    },
    input: {
        keyboard: true,
        gamepad: false
    },
    scene: [LoadingScene, MainScene, EntryScene, GameScene, EggCatedralScene, CathedralEntrance, VoxMarket, VoxmarketMarketScene, VoxmarketHallScene, CrossroadScene, ScraperScene, Shed521Scene, Shed521FloorsScene, Shed521GateScene, ShedRegistrationScene, ShedApplicationsScene, ShedAbandonedOfficeScene, ShedHallScene, ShedCourtyardScene, ScreamingCorkScene, ScreamingCorkInteriorScene, BurningBearStreetScene, SkyshipBoardScene, IntroScene, TransitionScene, ScraperInteriorScene, ScraperAmbraScene, ScraperBackyardScene, AbandonedBusScene],
    backgroundColor: '#2d2d2d',
    pixelArt: true,
    scale: {
        // Use NONE mode to avoid framebuffer issues
        mode: Phaser.Scale.NONE,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        parent: 'game-container',
        width: 800,
        height: 600
    }
};

const game = new Phaser.Game(config);

// Function to handle resizing and scaling
function resizeGame() {
    // Get the game canvas
    const canvas = document.querySelector('canvas');
    if (!canvas) return;
    
    // Calculate the scale factor
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    
    // Use a smaller target size to ensure the game fits comfortably
    // Using 90% of the available space as a safety margin
    const targetWidth = windowWidth * 0.9;
    const targetHeight = windowHeight * 0.9;
    
    const widthScale = targetWidth / 800;
    const heightScale = targetHeight / 600;
    
    // Use the smaller scale to ensure it fits both dimensions
    const scale = Math.min(widthScale, heightScale);

    console.log(`Window resized: ${windowWidth}x${windowHeight}, Scale: ${scale.toFixed(2)}`);
}

// Add window resize event handler
window.addEventListener('resize', resizeGame);

// Initial resize after game loads
window.addEventListener('load', () => {
    setTimeout(resizeGame, 100);
});

// Initialize game state in registry
game.registry.set('inventoryVisible', false);
game.registry.set('questLogVisible', false);
game.registry.set('inventory', {
    items: [],
    maxItems: 12
});

// Initialize Growth/Decay balance
game.registry.set('growthDecayBalance', {
    growth: 50,
    decay: 50
});