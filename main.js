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
import TownhallInteriorScene from './scenes/TownhallInteriorScene.js';
import TownSquareScene from './scenes/TownSquareScene.js';
import HarborScene from './scenes/HarborScene.js';
import EchoDrainDeltaScene from './scenes/EchoDrainDeltaScene.js';
import RedmassIslandScene from './scenes/RedmassIslandScene.js';
import SkyshipBoardScene from './scenes/SkyshipBoardScene.js';
import IntroScene from './scenes/IntroScene.js';
import TransitionScene from './scenes/TransitionScene.js';
import ScraperInteriorScene from './scenes/ScraperInteriorScene.js';
import ScraperAmbraScene from './scenes/ScraperAmbraScene.js';
import ScraperBackyardScene from './scenes/ScraperBackyardScene.js';
import RustDomainScene from './scenes/RustDomainScene.js';
import AbandonedBusScene from './scenes/AbandonedBusScene.js';
import LumenDirectorateScene from './scenes/LumenDirectorateScene.js';
import LumenDirectorateInteriorScene from './scenes/LumenDirectorateInteriorScene.js';
import PithReclaimersRoomScene from './scenes/PithReclaimersRoomScene.js';
import CardinalFeastScene from './scenes/CardinalFeastScene.js';
import GodgraveyardScene from './scenes/GodgraveyardScene.js';
import ScraperCellarScene from './scenes/ScraperCellarScene.js';
import EggCathedralInteriorScene from './scenes/EggCathedralInteriorScene.js';
import EggCathedralStudyScene from './scenes/EggCathedralStudyScene.js';
import CreditsScene from './scenes/CreditsScene.js';

// WebGL errors are handled by error-blocker.js

const config = {
    type: Phaser.AUTO,
    width: 1067,   // 16:9 at height 600 — fills widescreen with no bars (FIT letterboxes other aspects)
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
    scene: [LoadingScene, MainScene, EntryScene, GameScene, EggCatedralScene, CathedralEntrance, VoxMarket, VoxmarketMarketScene, VoxmarketHallScene, CrossroadScene, ScraperScene, Shed521Scene, Shed521FloorsScene, Shed521GateScene, ShedRegistrationScene, ShedApplicationsScene, ShedAbandonedOfficeScene, ShedHallScene, ShedCourtyardScene, ScreamingCorkScene, ScreamingCorkInteriorScene, ScreamingCorkClubScene, BurningBearStreetScene, TownhallScene, TownhallInteriorScene, TownSquareScene, HarborScene, EchoDrainDeltaScene, RedmassIslandScene, SkyshipBoardScene, IntroScene, TransitionScene, ScraperInteriorScene, ScraperAmbraScene, ScraperBackyardScene, RustDomainScene, AbandonedBusScene, LumenDirectorateScene, LumenDirectorateInteriorScene, CardinalFeastScene, GodgraveyardScene, ScraperCellarScene, EggCathedralInteriorScene, EggCathedralStudyScene, CreditsScene, PithReclaimersRoomScene],
    backgroundColor: '#000000', // canvas clear — the not-yet-widened scene backgrounds show black (not grey) beside them
    scale: {
        // The game renders at a fixed 1067×600 (16:9). FIT scales it uniformly to fill the window,
        // centred, preserving aspect — no distortion, crisp pixels, and no bars on 16:9 displays.
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        width: 1067,
        height: 600
    }
};

const game = new Phaser.Game(config);

// FIT mode auto-refits the canvas when the window changes size — no manual resize needed.
// (Calling game.scale.resize here would change the base game size and re-break the layout.)

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
