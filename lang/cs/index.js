import ui from './ui.js';
import game from './game.js';
import intro from './intro.js';
import locations from './locations.js';
import dialogs from './dialogs/index.js';
import quests from './quests.js';
import journal from './journal.js';

export default {
    ...ui,
    ...game,
    ...intro,
    ...locations,
    dialogs,
    ...quests,
    ...journal,
};
