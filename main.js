import MainScene from './scenes/MainScene.js';
import EntryScene from './scenes/EntryScene.js';
import GameScene from './scenes/GameScene.js';
import EggCatedralScene from './scenes/EggCatedralScene.js';
import CathedralEntrance from './scenes/CathedralEntrance.js';
import VoxMarket from './scenes/VoxMarket.js';
import CrossroadScene from './scenes/CrossroadScene.js';
import ScraperScene from './scenes/ScraperScene.js';
import Shed13Scene from './scenes/Shed13Scene.js';
import Shed13FloorsScene from './scenes/Shed13FloorsScene.js';
import Shed13GateScene from './scenes/Shed13GateScene.js';
import ShedRegistrationScene from './scenes/ShedRegistrationScene.js';
import ShedApplicationsScene from './scenes/ShedApplicationsScene.js';
import ShedAbandonedOfficeScene from './scenes/ShedAbandonedOfficeScene.js';
import ShedHallScene from './scenes/ShedHallScene.js';
import ShedCourtyardScene from './scenes/ShedCourtyardScene.js';
import ScreamingCorkScene from './scenes/ScreamingCorkScene.js';

const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
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
    scene: [MainScene, EntryScene, GameScene, EggCatedralScene, CathedralEntrance, VoxMarket, CrossroadScene, ScraperScene, Shed13Scene, Shed13FloorsScene, Shed13GateScene, ShedRegistrationScene, ShedApplicationsScene, ShedAbandonedOfficeScene, ShedHallScene, ShedCourtyardScene, ScreamingCorkScene],
    backgroundColor: '#2d2d2d',
    pixelArt: true,
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        fullscreenTarget: 'game'
    }
};

const game = new Phaser.Game(config);

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
