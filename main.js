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
import ScreamingCorkClubScene from './scenes/ScreamingCorkClubScene.js';
import BurningBearStreetScene from './scenes/BurningBearStreetScene.js';
import TownhallScene from './scenes/TownhallScene.js';
import SkyshipBoardScene from './scenes/SkyshipBoardScene.js';
import IntroScene from './scenes/IntroScene.js';
import TransitionScene from './scenes/TransitionScene.js';
import ScraperInteriorScene from './scenes/ScraperInteriorScene.js';
import ScraperAmbraScene from './scenes/ScraperAmbraScene.js';
import ScraperBackyardScene from './scenes/ScraperBackyardScene.js';
import AbandonedBusScene from './scenes/AbandonedBusScene.js';

// WebGL errors are handled by error-blocker.js

const config = {
    type: Phaser.AUTO,
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
    pixelArt: true,
    input: {
        keyboard: true,
        gamepad: false
    },
    scene: [LoadingScene, MainScene, EntryScene, GameScene, EggCatedralScene, CathedralEntrance, VoxMarket, VoxmarketMarketScene, VoxmarketHallScene, CrossroadScene, ScraperScene, Shed521Scene, Shed521FloorsScene, Shed521GateScene, ShedRegistrationScene, ShedApplicationsScene, ShedAbandonedOfficeScene, ShedHallScene, ShedCourtyardScene, ScreamingCorkScene, ScreamingCorkInteriorScene, ScreamingCorkClubScene, BurningBearStreetScene, TownhallScene, SkyshipBoardScene, IntroScene, TransitionScene, ScraperInteriorScene, ScraperAmbraScene, ScraperBackyardScene, AbandonedBusScene],
    backgroundColor: '#2d2d2d',
    scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        fullscreenTarget: 'game-container',
        width: window.innerWidth,
        height: window.innerHeight
    }
};

const game = new Phaser.Game(config);

// Add window resize event handler
window.addEventListener('resize', () => {
    game.scale.resize(window.innerWidth, window.innerHeight);
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
