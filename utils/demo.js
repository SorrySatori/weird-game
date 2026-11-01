/**
 * The demo cut (config/build.js DEMO_BUILD). Places outside the demo stay in the game, but every way into them is
 * closed off: SceneTransitionManager turns an exit to one of them into a traffic cone the priest won't pass, and the
 * few dialog / script transitions check isDemoClosed() themselves. Demo = the main line up to the first talk with
 * Dr. Elphi + the Ortolan, Edgar, Gnur and Kloor side quests (tools/trailer/shots.js SURVEY_SCENES lists its places).
 */
import { DEMO_BUILD } from '../config/build.js';
import LanguageSystem from '../systems/LanguageSystem.js';

export const DEMO_CLOSED_SCENES = new Set([
    'TownhallScene', 'TownhallInteriorScene', 'PithReclaimersRoomScene', 'TownSquareScene',
    'LumenDirectorateScene', 'LumenDirectorateInteriorScene', 'GodgraveyardScene', 'HarborScene',
    'EchoDrainDeltaScene', 'RedmassIslandScene',
    'ScraperBackyardScene', 'AbandonedBusScene', 'RustDomainScene', 'ScraperCellarScene',
    'EggCathedralStudyScene', 'EggCathedralInteriorScene', 'CardinalFeastScene',
]);

export const isDemoClosed = (sceneKey) => DEMO_BUILD && DEMO_CLOSED_SCENES.has(sceneKey);

/**
 * Where a loaded save continues: its own scene, unless the build doesn't have it (a save from the full game standing in
 * a place the demo left out) -- then at the Crossroads, the demo's hub.
 */
export function playableScene(sceneManager, key, fallback = 'CrossroadScene') {
    return key && sceneManager?.keys?.[key] && !isDemoClosed(key) ? key : fallback;
}

export function preloadDemoCones(scene) {
    if (!DEMO_BUILD) return;
    scene.load.image('trafficCone', 'assets/images/props/prop_traffic_cone.png');        // tools/artgen/props.py
    scene.load.image('trafficConeFar', 'assets/images/props/prop_traffic_cone_far.png');
}

/**
 * Where the cones go when an exit's rect doesn't stand on the floor where the way is (a door high in the picture, a
 * street's far end): `${fromScene}>${toScene}` -> [{ x, y, far }] in canvas coords, feet anchored.
 */
const CONE_SPOTS = {
    'BurningBearStreetScene>TownhallScene': [{ x: 520, y: 432, far: true }, { x: 548, y: 434, far: true }],
    // the way in is the top of the picture, past the Guardian: the cones stand in the doorway on either side of him
    'CathedralEntrance>EggCathedralStudyScene': [{ x: 478, y: 506 }, { x: 590, y: 506 }],
};

/**
 * Stand cones in a closed exit: hand-placed ones from CONE_SPOTS, otherwise on the exit's bottom edge -- one, or two
 * for a wide exit. Far up the picture (a street's far end) they're the small cone.
 */
export function placeDemoCones(scene, fromScene, toScene, x, bottom, width) {
    const spots = CONE_SPOTS[`${fromScene}>${toScene}`]
        || (width >= 120 ? [{ x: x - 20, y: bottom }, { x: x + 20, y: bottom + 2 }] : [{ x, y: bottom }]);
    return spots.map(s => scene.add.image(s.x, s.y, s.far || s.y < 450 ? 'trafficConeFar' : 'trafficCone')
        .setOrigin(0.5, 1).setDepth(5));
}

export const demoClosedLabel = () => LanguageSystem.getInstance().t('ui.demo.closedLabel');

/** The priest's aside at a cone (a speech bubble, so it reads as part of the world). */
export function sayDemoClosed(scene) {
    const line = LanguageSystem.getInstance().t('ui.demo.closedLine');
    if (scene.priest && scene.showSpeechBubble) scene.showSpeechBubble(scene.priest, line, { duration: 3200 });
    else scene.showNotification?.(line);
}
