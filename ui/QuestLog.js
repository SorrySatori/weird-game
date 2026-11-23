/**
 * QuestLog — the quests, in the panel set's look (ui/panels/questScreens.js: the apprentice's corkboard, or the
 * office's forms), Active / Completed tabs.
 * The list shows each quest with its latest step under the title; the chosen one's text is beside it (what to do,
 * then every step so far). A quest the demo can't finish (utils/demo.js DEMO_UNFINISHED_QUESTS) carries a traffic
 * cone and says so.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { createHudButton } from '../utils/hudButton.js';
import { isDemoUnfinished } from '../utils/demo.js';
import { openPaperScreen, closePaperScreen, refreshPaperScreen } from './paperKit.js';
import { panelSet } from './panelStyle.js';
import { QUEST_SCREENS } from './panels/questScreens.js';
import { playMenuSound } from '../utils/menuKit.js';

const DEMO_COLOR = '#b8601a';                            // the traffic cones' orange, darkened for paper

export default class QuestLog {
    constructor(scene, x = 750, y = 50) {
        this.scene = scene;
        this.questSystem = scene.registry.get('questSystem');
        this.lang = LanguageSystem.getInstance();
        this.activeTab = 'active';
        this.questPanel = { visible: false };                  // GameScene.isModalOpen() and the tutorial read questPanel.visible

        this.createQuestButton(x, y);

        this.onQuestsChanged = () => { if (this.questPanel.visible) this.updateQuestDisplay(); };
        this.questSystem.subscribe(this.onQuestsChanged);
        // the quest system outlives the scene: let go of it when the scene shuts down (scenes are re-used)
        this.scene.events.once('shutdown', () => this.questSystem.unsubscribe(this.onQuestsChanged));
        this.onQ = () => this.toggleQuestLog();
        this.scene.input.keyboard.on('keydown-Q', this.onQ);
    }

    createQuestButton(x, y) {
        const { container, badge } = createHudButton(this.scene, 'quests', this.lang.t('ui.hud.quests'), () => this.toggleQuestLog(), { x, y });
        this.buttonContainer = container;
        this.questNotificationIndicator = badge;
        if (this.scene.registry.get('hasUnreadQuestUpdates')) {
            this.questNotificationIndicator.setVisible(true);
        }
    }

    /** a quest's title / description / update in the current language (stored English if there's no translation) */
    questText(quest) {
        const tKey = `quests.${quest.id}`;
        const tr = (key, fallback) => { const v = this.lang.t(key); return v === key ? fallback : v; };
        return { tKey, title: tr(`${tKey}.title`, quest.title), description: tr(`${tKey}.description`, quest.description) };
    }

    updateText(tKey, update) {
        // via the update key (or params.textKey for runtime-built text), filling {placeholders} from the saved params;
        // keep the stored text if there's no translation or a placeholder has no value (old saves)
        const textKey = update.params?.textKey || update.key;
        if (textKey) {
            const uKey = `${tKey}.updates.${textKey}`;
            const t = this.lang.t(uKey, update.params || {});
            if (typeof t === 'string' && t !== uKey && !/\{\w+\}/.test(t)) return t;
        }
        return update.text;
    }

    tabLabel(key, fallback) { const v = this.lang.t(key); return v === key ? fallback : v; }

    /** a quest as the designs get it */
    questData(q) {
        const { tKey, title, description } = this.questText(q);
        return {
            key: q.id, title, description, done: !!q.isComplete, demo: !q.isComplete && isDemoUnfinished(q.id),
            updates: (q.updates || []).map(u => this.updateText(tKey, u))
        };
    }

    /** the quest log's screen in the panel set's look (ui/panels/questScreens.js: a corkboard, or official forms) */
    buildScreen(overlay) {
        return QUEST_SCREENS[panelSet()](overlay, this.screenCtx(overlay));
    }

    /** everything a quest-log screen reads and does (see ui/panels/questScreens.js for the contract) */
    screenCtx(overlay) {
        return {
            scene: overlay, W: overlay.scale.width, H: overlay.scale.height, lang: this.lang.getLanguage(),
            t: (key, params, fallback = key) => { const v = this.lang.t(key, params); return v === key ? fallback : v; },
            title: this.lang.t('ui.hud.quests'),
            tabs: [{ key: 'active', label: this.tabLabel('ui.hud.questTabActive', 'Active') }, { key: 'finished', label: this.tabLabel('ui.hud.questTabDone', 'Completed') }],
            tab: () => this.activeTab,
            setTab: (key) => { this.activeTab = key; },
            quests: () => this.questSystem.getAllQuests().filter(q => (this.activeTab === 'active') !== !!q.isComplete).map(q => this.questData(q)),
            all: () => this.questSystem.getAllQuests().map(q => this.questData(q)),
            empty: () => this.lang.t(this.activeTab === 'active' ? 'ui.hud.noActiveQuests' : 'ui.hud.noCompletedQuests'),
            strings: {
                progress: this.lang.t('ui.hud.questProgress'), demoNote: this.lang.t('ui.demo.questNotInDemo'),
                done: this.tabLabel('ui.hud.questTabDone', 'Completed'), active: this.tabLabel('ui.hud.questTabActive', 'Active')
            },
            sound: (key, vol = 1) => playMenuSound(overlay, key, vol),
            close: () => this.close()
        };
    }

    updateQuestDisplay() { refreshPaperScreen(this); }

    /** paperKit: another panel took the screen over */
    paperClosed() {
        this.questPanel.visible = false;
        this.scene.registry.set('questLogVisible', false);
    }

    close() { this.hideQuestLog(); }

    toggleQuestLog() {
        if (this.questPanel.visible) this.hideQuestLog();
        else this.showQuestLog();
    }

    showQuestLog() {
        this.questPanel.visible = true;
        this.scene.registry.set('questLogVisible', true);
        openPaperScreen(this);
        if (this.questNotificationIndicator) {
            this.questNotificationIndicator.setVisible(false);
            this.scene.registry.set('hasUnreadQuestUpdates', false);
        }
    }

    hideQuestLog() {
        this.questPanel.visible = false;
        this.scene.registry.set('questLogVisible', false);
        closePaperScreen(this);
    }

    cleanup() {
        this.questSystem.unsubscribe(this.onQuestsChanged);
        this.scene.input.keyboard.off('keydown-Q', this.onQ);
        this.buttonContainer?.destroy();
        closePaperScreen(this);
    }
}
