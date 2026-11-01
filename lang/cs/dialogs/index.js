/**
 * Czech dialog translations – aggregator
 * Each scene gets its own file for maintainability.
 */
import entryScene from './EntryScene.js';
import crossroadScene from './CrossroadScene.js';
import cathedralEntrance from './CathedralEntrance.js';
import voxMarket from './VoxMarket.js';
import shed521Scene from './Shed521Scene.js';
import screamingCorkInteriorScene from './ScreamingCorkInteriorScene.js';
import screamingCorkClubScene from './ScreamingCorkClubScene.js';
import screamingCorkScene from './ScreamingCorkScene.js';
import shedHallScene from './ShedHallScene.js';
import shedApplicationsScene from './ShedApplicationsScene.js';
import shedCourtyardScene from './ShedCourtyardScene.js';
import shedRegistrationScene from './ShedRegistrationScene.js';
import skyshipBoardScene from './SkyshipBoardScene.js';
import scraperAmbraScene from './ScraperAmbraScene.js';
import scraperInteriorScene from './ScraperInteriorScene.js';
import scraperScene from './ScraperScene.js';
import voxmarketMarketScene from './VoxmarketMarketScene.js';
import voxmarketHallScene from './VoxmarketHallScene.js';
import burningBearStreetScene from './BurningBearStreetScene.js';

export default {
    EntryScene: entryScene,
    CrossroadScene: crossroadScene,
    CathedralEntrance: cathedralEntrance,
    VoxMarket: voxMarket,
    Shed521Scene: shed521Scene,
    ScreamingCorkInteriorScene: screamingCorkInteriorScene,
    ScreamingCorkClubScene: screamingCorkClubScene,
    ScreamingCorkScene: screamingCorkScene,
    ShedHallScene: shedHallScene,
    ShedApplicationsScene: shedApplicationsScene,
    ShedCourtyard: shedCourtyardScene, // keyed by scene key, and this scene's key is 'ShedCourtyard' (not the file name)
    ShedRegistrationScene: shedRegistrationScene,
    SkyshipBoardScene: skyshipBoardScene,
    ScraperAmbraScene: scraperAmbraScene,
    ScraperInteriorScene: scraperInteriorScene,
    ScraperScene: scraperScene,
    VoxmarketMarketScene: voxmarketMarketScene,
    VoxmarketHallScene: voxmarketHallScene,
    BurningBearStreetScene: burningBearStreetScene,
};
