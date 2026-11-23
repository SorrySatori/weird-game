/**
 * JournalUI.js — the journal, in the panel set's look (ui/panels/journalScreens.js: the apprentice's notebook, or the
 * office's dossiers), a tab per category. The list shows the entries newest first (an
 * entry that learned a new fact counts as new); the chosen one's text is beside it: what the player knew when it was
 * written, then each fact learned since. The Factions tab lists the discovered factions first, with the standing on a
 * gauge, then the faction records. A tab with something unread wears a red seal until it's looked at.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { openPaperScreen, closePaperScreen, refreshPaperScreen } from './paperKit.js';
import { panelSet } from './panelStyle.js';
import { JOURNAL_SCREENS } from './panels/journalScreens.js';
import { playMenuSound } from '../utils/menuKit.js';

class JournalUI {
    constructor(scene) {
        this.scene = scene;
        this.visible = false;
        this.currentCategory = null;
        this.journalSystem = this.scene.journalSystem;
        this.lang = LanguageSystem.getInstance();
        this.categories = Object.values(this.journalSystem.categories);

        // A tab with something new wears the HUD's red seal until the player opens it (JournalSystem.unread, saved).
        // The journal system outlives the scene, so the listener goes with the scene.
        const onUnread = () => refreshPaperScreen(this);
        this.journalSystem.on('unreadChanged', onUnread);
        this.scene.events.once('shutdown', () => { this.journalSystem.off('unreadChanged', onUnread); closePaperScreen(this); });

        // J toggles (ESC closes: GameMenu)
        this.jKey = this.scene.input.keyboard.addKey('J');
        this.jKey.on('down', () => this.toggle());
    }

    /**
     * Title, description and facts of an entry in the current language: the translated description (falling back to
     * the text stored with the entry), and every fact learned about it since.
     */
    resolveEntryText(entry) {
        const jKey = `journal.${entry.id}`;
        const tr = (key, fallback) => {
            const v = this.lang.t(key);
            return v === key ? fallback : v;
        };
        const facts = this.journalSystem.getFacts(entry.id).map(f => tr(`${jKey}.facts.${f.id}`, f.text));
        return {
            title: tr(`${jKey}.title`, entry.title),
            description: tr(`${jKey}.description`, entry.content),
            facts,
            content: [tr(`${jKey}.description`, entry.content), ...facts].join('\n'),
        };
    }

    /** a category's tab label in the current language (entries keep the English category as their key) */
    categoryLabel(category) {
        const v = this.lang.t(`ui.hud.journalCategories.${category}`);
        return v === `ui.hud.journalCategories.${category}` ? category : v;
    }

    t(key, fallback, params) {
        const v = this.lang.t(key, params);
        return v === key ? fallback : v;
    }

    selectCategory(category) {
        this.currentCategory = category;
        this.journalSystem.markRead(category);
    }

    /** an entry as the designs get it */
    entryData(entry) {
        const { title, description, facts } = this.resolveEntryText(entry);
        return { key: entry.id, title, description, facts, category: entry.category, categoryLabel: this.categoryLabel(entry.category), updated: entry.lastUpdated || entry.timestamp || 0 };
    }

    /** the journal's screen in the panel set's look (ui/panels/journalScreens.js: the notebook, or the dossiers) */
    buildScreen(overlay) {
        return JOURNAL_SCREENS[panelSet()](overlay, this.screenCtx(overlay));
    }

    /** everything a journal screen reads and does (see ui/panels/journalScreens.js for the contract) */
    screenCtx(overlay) {
        // newest first; entries from the same instant in a fixed order (by id), so they don't swap between openings
        const newest = (list) => [...list].sort((a, b) => ((b.lastUpdated || b.timestamp) - (a.lastUpdated || a.timestamp)) || String(a.id).localeCompare(String(b.id)));
        return {
            scene: overlay, W: overlay.scale.width, H: overlay.scale.height, lang: this.lang.getLanguage(),
            t: (key, params, fallback = key) => this.t(key, fallback, params),
            title: this.lang.t('ui.hud.journal'),
            categories: () => this.categories.map(c => ({
                key: c, label: this.categoryLabel(c), unread: this.journalSystem.isUnread(c) && c !== this.currentCategory
            })),
            category: () => this.currentCategory,
            setCategory: (key) => this.selectCategory(key),
            entries: (category = this.currentCategory) => newest(this.journalSystem.getEntriesByCategory(category)).map(e => this.entryData(e)),
            allEntries: () => newest(this.journalSystem.getAllEntries()).map(e => this.entryData(e)),
            factions: () => {
                const fs = this.scene.registry.get('factionSystem');
                const keys = fs ? Object.keys(fs.factions).filter(k => fs.factions[k].discovered || fs.factions[k].reputation !== 0) : [];
                return keys.map(key => {
                    const f = fs.factions[key];
                    return {
                        key, name: fs.displayName ? fs.displayName(key) : f.name, value: f.reputation, standing: this.standing(f.reputation),
                        status: this.t('factions.status', `Standing: ${this.standing(f.reputation)}`, { status: this.standing(f.reputation) }),
                        description: this.t(`factions.${key}.description`, f.description || '')
                    };
                });
            },
            empty: () => (this.currentCategory === 'Factions'
                ? this.lang.t('ui.hud.noFactions')
                : this.lang.t('ui.hud.noJournalEntries', { category: this.categoryLabel(this.currentCategory) })),
            strings: {
                factionStanding: this.lang.t('ui.hud.factionStanding'), factionRecords: this.lang.t('ui.hud.factionRecords'),
                noFactions: this.lang.t('ui.hud.noFactions'), noFactionRecords: this.lang.t('ui.hud.noFactionRecords')
            },
            sound: (key, vol = 1) => playMenuSound(overlay, key, vol),
            close: () => this.close()
        };
    }

    /** paperKit: another panel took the screen over */
    paperClosed() {
        this.visible = false;
        if (this.scene.customCursor) this.scene.customCursor.visible = true;
    }

    close() { if (this.visible) this.toggle(); }

    /** the standing's word, in the player's language */
    standing(rep) {
        const k = rep >= 75 ? 'revered' : rep >= 50 ? 'honored' : rep >= 25 ? 'friendly' : rep >= 10 ? 'liked'
            : rep > -10 ? 'neutral' : rep > -25 ? 'disliked' : rep > -50 ? 'unfriendly' : rep > -75 ? 'hostile' : 'hated';
        return this.t(`factions.standings.${k}`, k[0].toUpperCase() + k.slice(1));
    }

    getMembershipStatus(_factionKey) {
        // the demo build: no faction can be joined yet, so nobody shows a membership
        return null;
    }

    toggle() {
        this.visible = !this.visible;
        if (this.visible) {
            // opened (the HUD icon or J): the HUD's seal goes; the tabs keep theirs until each is looked at
            this.scene.journalNotificationIndicator?.setVisible(false);
            this.scene.registry.set('hasUnreadJournalEntries', false);
            this.selectCategory(this.currentCategory || this.categories[0]);
            openPaperScreen(this);
            if (this.scene.customCursor) this.scene.customCursor.visible = false;
        } else {
            closePaperScreen(this);
            if (this.scene.customCursor) this.scene.customCursor.visible = true;
        }
    }
}

export default JournalUI;
