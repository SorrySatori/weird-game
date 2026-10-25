import ui from './ui.js';
import game from './game.js';
import intro from './intro.js';
import locations from './locations.js';
import dialogs from './dialogs/index.js';
import quests from './quests.js';
import journal from './journal.js';
import observe from './observe.js';
import ambient from './ambient.js';
import symbiontLines from './symbiontLines.js';

export default {
    ...ui,
    ...game,
    ...intro,
    ...locations,
    dialogs,
    ...quests,
    ...journal,
    ...observe,
    ...ambient,
    ...symbiontLines,
};
