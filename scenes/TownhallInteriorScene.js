import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class TownhallInteriorScene extends GameScene {
    constructor() {
        super({ key: 'TownhallInteriorScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
        };
    }

    preload() {
        super.preload();
        this.load.image('townhallInteriorBg', 'assets/images/backgrounds/townhall_interior.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        const bg = this.add.image(400, 300, 'townhallInteriorBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        this.transitionManager.createTransitionZone(
            400,
            560,
            180,
            80,
            'down',
            'TownhallScene',
            400,
            540,
            'Townhall Exterior'
        );

        this.priest.x = 400;
        this.priest.y = 520;

        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        this.completeEnterTownhallQuestOnFirstEntry();

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    completeEnterTownhallQuestOnFirstEntry() {
        const quest = this.questSystem?.getQuest('enter_townhall');

        if (!quest || quest.isComplete) return;

        this.addJournalEntry(
            'entered_townhall',
            'Entered the Townhall',
            'I made it inside the Townhall. Now I can search the records for the Bishop\'s doppelgänger report and help Phor Calesta with his permits.',
            this.journalSystem.categories.EVENTS,
            { location: 'Townhall' }
        );

        this.questSystem.updateQuest(
            'enter_townhall',
            'I made it inside the Townhall. The locked-door problem is solved; now I can search the records inside.',
            'entered_townhall'
        );
        this.questSystem.completeQuest('enter_townhall');
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.TownhallInteriorScene = TownhallInteriorScene;
}

export { TownhallInteriorScene };
