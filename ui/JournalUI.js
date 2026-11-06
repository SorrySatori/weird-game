/**
 * JournalUI.js — the journal: a menu-kit ledger panel (ui/LedgerPanel.js) with a tab per category; every entry is an
 * enamel card (title, what the player knew when it was written, then each fact learned since). The Factions tab also
 * shows the standing with each discovered faction on a glass gauge.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import LedgerPanel, { LEDGER_TEXT, LEDGER_PAGE_WIDTH } from './LedgerPanel.js';

const PAD = 18;                       // inside a card
const GAP = 12;                       // between cards
const CARD_W = LEDGER_PAGE_WIDTH - 8;
const TEXT_W = CARD_W - PAD * 2;
const GAUGE = { half: 63, center: 68 };          // menu_slider's glass (native px 4..131): the middle, half its length

class JournalUI {
    constructor(scene) {
        this.scene = scene;
        this.visible = false;
        this.currentCategory = null;
        this.journalSystem = this.scene.journalSystem;
        this.lang = LanguageSystem.getInstance();
        this.categories = Object.values(this.journalSystem.categories);

        // over the Spore bar / G/D medallion (1000, created later) and the quest log (1001)
        this.ledger = new LedgerPanel(scene, { title: this.lang.t('ui.hud.journal'), depth: 1002, onClose: () => this.toggle() });
        this.container = this.ledger.container;
        this.ledger.setTabs(this.categories.map(c => this.categoryLabel(c)), (i) => this.selectCategory(this.categories[i]));

        // ESC closes, J toggles
        this.escKey = this.scene.input.keyboard.addKey('ESC');
        this.escKey.on('down', () => { if (this.visible) this.toggle(); });
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
        this.ledger.selectTab(this.categories.indexOf(category));
        this.refreshContent();
    }

    refreshContent() {
        const L = this.ledger;
        L.clear();
        let y = 6;
        if (this.currentCategory === 'Factions') {
            y = this.addFactionStandings(y);
            y += L.addHeading(y, this.lang.t('ui.hud.factionRecords')) + 14;
            y = this.addEntries(y, this.journalSystem.getEntriesByCategory('Factions'), this.lang.t('ui.hud.noFactionRecords'));
        } else {
            const entries = this.currentCategory
                ? this.journalSystem.getEntriesByCategory(this.currentCategory)
                : this.journalSystem.getAllEntries();
            y = this.addEntries(y, entries, this.lang.t('ui.hud.noJournalEntries', {
                category: this.currentCategory ? this.categoryLabel(this.currentCategory) : 'journal',
            }));
        }
        L.setContentHeight(y + 6);
    }

    /** newest first (an entry that just learned a new fact counts as new); returns the y below the last card */
    addEntries(y, entries, emptyText) {
        if (!entries.length) return y + this.ledger.addEmpty(y + 30, emptyText) + 40;
        entries = [...entries].sort((a, b) => (b.lastUpdated || b.timestamp) - (a.lastUpdated || a.timestamp));
        for (const entry of entries) {
            const { title, description, facts } = this.resolveEntryText(entry);
            y += this.addEntryCard(y, title, description, facts) + GAP;
        }
        return y;
    }

    addEntryCard(y, title, description, facts) {
        const L = this.ledger, sc = this.scene;
        const card = L.addCard(y, 60);
        const titleText = sc.add.text(PAD, y + PAD - 4, title, { ...LEDGER_TEXT.title, wordWrap: { width: TEXT_W } });
        let cy = y + PAD - 4 + titleText.height + 6;
        const parts = [titleText];
        if (description) {
            const body = sc.add.text(PAD, cy, description, { ...LEDGER_TEXT.body, wordWrap: { width: TEXT_W } });
            parts.push(body);
            cy += body.height + 4;
        }
        for (const fact of facts) {                                   // what was learned later: one glowing spore each
            const dot = sc.add.image(PAD + 4, cy + 10, 'menuSpore').setScale(2).setTint(0x7fff8e);
            const line = sc.add.text(PAD + 16, cy, fact, { ...LEDGER_TEXT.body, wordWrap: { width: TEXT_W - 16 } });
            parts.push(dot, line);
            cy += line.height + 4;
        }
        L.content.add(parts);
        const h = cy - y + PAD - 6;
        card.setSize(CARD_W / 2, h / 2);
        return h;
    }

    /** the standing with each discovered faction: name, a glass gauge (green right / red left of the middle), status */
    addFactionStandings(y) {
        const L = this.ledger, sc = this.scene;
        y += L.addHeading(y, this.lang.t('ui.hud.factionStanding')) + 14;
        const fs = this.scene.registry.get('factionSystem');
        const keys = fs ? Object.keys(fs.factions).filter(k => fs.factions[k].discovered || fs.factions[k].reputation !== 0) : [];
        if (!keys.length) return y + L.addEmpty(y + 10, this.lang.t('ui.hud.noFactions')) + 30;

        for (const key of keys) {
            const f = fs.factions[key];
            const rep = Phaser.Math.Clamp(f.reputation, -100, 100);
            const card = L.addCard(y, 60);
            const name = sc.add.text(PAD, y + PAD - 4, fs.displayName ? fs.displayName(key) : f.name, LEDGER_TEXT.title);
            const gy = y + PAD - 4 + name.height + 22;
            const gx = PAD + 136;                                     // gauge centre
            const track = sc.add.image(gx, gy, 'menuSlider', 0).setScale(2);
            const fill = sc.add.image(gx, gy, 'menuSliderFill').setScale(2);
            const len = Math.round(Math.abs(rep) / 100 * GAUGE.half);
            if (rep >= 0) fill.setCrop(GAUGE.center, 0, len, 16);
            else fill.setCrop(GAUGE.center - len, 0, len, 16).setTintFill(0xc4553a);   // red liquid for a grudge
            const value = sc.add.text(gx + 152, gy, `${rep >= 0 ? '+' : ''}${f.reputation}`, {
                ...LEDGER_TEXT.title, color: rep >= 0 ? '#9fe8a8' : '#ff8a6a',
            }).setOrigin(0, 0.5);
            const status = sc.add.text(gx + 220, gy, this.t('factions.status', `Standing: ${this.standing(rep)}`,
                { status: this.standing(rep) }), { ...LEDGER_TEXT.body, fontStyle: 'italic' }).setOrigin(0, 0.5);
            let cy = gy + 24;
            const parts = [name, track, fill, value, status];
            const member = this.getMembershipStatus(key);
            if (member) {
                const m = sc.add.text(PAD, cy, member.text, { ...LEDGER_TEXT.body, color: member.color, fontStyle: 'bold' });
                parts.push(m); cy += m.height + 4;
            }
            const desc = sc.add.text(PAD, cy, this.t(`factions.${key}.description`, f.description || ''), { ...LEDGER_TEXT.dim, wordWrap: { width: TEXT_W } });
            parts.push(desc);
            cy += desc.height;
            L.content.add(parts);
            const h = cy - y + PAD - 2;
            card.setSize(CARD_W / 2, h / 2);
            y += h + GAP;
        }
        return y + 10;
    }

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
            this.ledger.show();
            if (!this.currentCategory) this.selectCategory(this.categories[0]);
            else this.refreshContent();
            if (this.scene.customCursor) this.scene.customCursor.visible = false;
        } else {
            this.ledger.hide();
            if (this.scene.customCursor) this.scene.customCursor.visible = true;
        }
    }
}

export default JournalUI;
