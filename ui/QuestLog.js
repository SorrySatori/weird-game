/**
 * QuestLog — the quests: a menu-kit ledger panel (ui/LedgerPanel.js) with Active / Completed tabs. Each quest is an
 * enamel card; click its header to open it (description, then every progress update). A quest the demo can't finish
 * (utils/demo.js DEMO_UNFINISHED_QUESTS) carries a traffic cone and says so.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { createHudButton } from '../utils/hudButton.js';
import { playMenuSound, MENU_COLORS } from '../utils/menuKit.js';
import { isDemoUnfinished } from '../utils/demo.js';
import LedgerPanel, { LEDGER_TEXT, LEDGER_PAGE_WIDTH } from './LedgerPanel.js';

const PAD = 18;
const GAP = 10;
const HEAD_H = 48;                                       // a closed card
const CARD_W = LEDGER_PAGE_WIDTH - 8;
const TEXT_W = CARD_W - PAD * 2 - 20;
const DEMO_COLOR = '#e8a24a';                            // the traffic cones' orange, softened

export default class QuestLog {
    constructor(scene, x = 750, y = 50) {
        this.scene = scene;
        this.questSystem = scene.registry.get('questSystem');
        this.lang = LanguageSystem.getInstance();
        this.expandedQuests = new Set();
        this.activeTab = 'active';

        this.createQuestButton(x, y);
        this.createQuestPanel();

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

    createQuestPanel() {
        // over the Spore bar (1000); under the journal (1002)
        this.ledger = new LedgerPanel(this.scene, {
            title: this.lang.t('ui.hud.quests').toUpperCase(), depth: 1001, y: 300, onClose: () => this.hideQuestLog(),
        });
        this.questPanel = this.ledger.container;               // GameScene.isModalOpen() checks questPanel.visible
        const tab = (key, fallback) => { const v = this.lang.t(key); return v === key ? fallback : v; };
        this.ledger.setTabs([tab('ui.hud.questTabActive', 'Active'), tab('ui.hud.questTabDone', 'Completed')], (i) => {
            this.activeTab = i === 0 ? 'active' : 'finished';
            this.updateQuestDisplay();
        });
        this.ledger.selectTab(0);
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

    createQuestEntry(quest, y) {
        const L = this.ledger, sc = this.scene;
        const { tKey, title, description } = this.questText(quest);
        const open = this.expandedQuests.has(quest.id);
        const demo = !quest.isComplete && isDemoUnfinished(quest.id);
        const card = L.addCard(y, HEAD_H, { lit: open });

        const chevron = sc.add.image(PAD + 4, y + HEAD_H / 2, 'menuChevron', open ? 2 : 0).setScale(2);
        const titleText = sc.add.text(PAD + 22, y + HEAD_H / 2, title, {
            ...LEDGER_TEXT.title, color: quest.isComplete ? '#9fe8a8' : MENU_COLORS.title, wordWrap: { width: TEXT_W - 30 },
        }).setOrigin(0, 0.5);
        const parts = [chevron, titleText];
        if (demo && sc.textures.exists('trafficConeFar')) {             // the demo's closed-way sign
            parts.push(sc.add.image(CARD_W - PAD - 8, y + HEAD_H / 2 + 13, 'trafficConeFar').setOrigin(0.5, 1));
        }
        let h = Math.max(HEAD_H, titleText.height + 22);
        titleText.y = y + h / 2; chevron.y = y + h / 2;

        if (open) {
            let cy = y + h + 2;
            const desc = sc.add.text(PAD + 22, cy, description, { ...LEDGER_TEXT.body, wordWrap: { width: TEXT_W } });
            parts.push(desc);
            cy += desc.height + 10;
            if (demo) {
                const note = sc.add.text(PAD + 22, cy, this.lang.t('ui.demo.questNotInDemo'), {
                    ...LEDGER_TEXT.body, color: DEMO_COLOR, fontStyle: 'italic', wordWrap: { width: TEXT_W },
                });
                parts.push(note);
                cy += note.height + 10;
            }
            if (quest.updates?.length) {
                const head = sc.add.text(PAD + 22, cy, this.lang.t('ui.hud.questProgress'), { ...LEDGER_TEXT.heading, fontSize: '16px' });
                parts.push(head);
                cy += head.height + 6;
                for (const update of quest.updates) {
                    const dot = sc.add.image(PAD + 30, cy + 10, 'menuSpore').setScale(2).setTint(0x7fff8e);
                    const line = sc.add.text(PAD + 42, cy, this.updateText(tKey, update), { ...LEDGER_TEXT.dim, wordWrap: { width: TEXT_W - 20 } });
                    parts.push(dot, line);
                    cy += line.height + 8;
                }
            }
            h = cy - y + 6;
        }
        L.content.add(parts);
        card.setSize(CARD_W / 2, h / 2);

        // the header opens / closes the quest
        const hit = sc.add.zone(0, y, CARD_W, Math.max(HEAD_H, titleText.height + 22)).setOrigin(0, 0).setInteractive({ useHandCursor: true });
        hit.on('pointerover', (pointer) => {
            if (!L.inPage(pointer)) return;
            card.setTexture('menuCard', 1); chevron.setFrame(open ? 3 : 1);
            playMenuSound(sc, 'hoverSound', 0.4);
        });
        hit.on('pointerout', () => { card.setTexture('menuCard', open ? 1 : 0); chevron.setFrame(open ? 2 : 0); });
        hit.on('pointerdown', (pointer, lx, ly, event) => {
            event?.stopPropagation();
            if (!L.inPage(pointer)) return;
            playMenuSound(sc, 'clickSound');
            this.toggleQuestExpansion(quest.id);
        });
        L.content.add(hit);
        return h + GAP;
    }

    updateQuestDisplay() {
        const L = this.ledger;
        const keepScroll = L.scrollY;
        L.clear();
        const quests = this.questSystem.getAllQuests().filter(q => (this.activeTab === 'active') !== !!q.isComplete);
        if (!quests.length) {
            const msg = this.lang.t(this.activeTab === 'active' ? 'ui.hud.noActiveQuests' : 'ui.hud.noCompletedQuests');
            L.setContentHeight(L.addEmpty(40, msg) + 60);
            return;
        }
        let y = 6;
        for (const quest of quests) y += this.createQuestEntry(quest, y);
        L.setContentHeight(y + 4);
        if (this.keepScroll) L.scrollTo(keepScroll);
        this.keepScroll = false;
    }

    toggleQuestExpansion(questId) {
        if (this.expandedQuests.has(questId)) this.expandedQuests.delete(questId);
        else this.expandedQuests.add(questId);
        this.keepScroll = true;                                 // opening a card must not jump back to the top
        this.updateQuestDisplay();
    }

    toggleQuestLog() {
        if (this.questPanel.visible) this.hideQuestLog();
        else this.showQuestLog();
    }

    showQuestLog() {
        this.ledger.show();
        this.scene.registry.set('questLogVisible', true);
        this.updateQuestDisplay();
        if (this.questNotificationIndicator) {
            this.questNotificationIndicator.setVisible(false);
            this.scene.registry.set('hasUnreadQuestUpdates', false);
        }
    }

    hideQuestLog() {
        this.ledger.hide();
        this.scene.registry.set('questLogVisible', false);
    }

    cleanup() {
        this.questSystem.unsubscribe(this.onQuestsChanged);
        this.scene.input.keyboard.off('keydown-Q', this.onQ);
        this.buttonContainer?.destroy();
        this.ledger?.destroy();
    }
}
