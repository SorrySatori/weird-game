/**
 * LedgerPanel — the big menu-kit panel the journal and the quest log share: the bronze 'ledger' frame with its title
 * plate and close button, a row of tab plaques, and a scrolling page of entry cards (nine-slice enamel cards) with a
 * bronze rail whose gear knob rolls as you scroll. Content is clipped to the page, so cards slide under the tabs.
 * Scroll: mouse wheel, drag the knob or click the rail, ↑/↓ (W/S), PgUp/PgDn, Home/End. ←/→ (A/D) switch tabs.
 * Art: tools/artgen/menu_ui.py (tab, card, rail, chevron, PANELS.ledger) — see utils/menuKit.js.
 */
import { createMenuPanel, addPanelClose, MENU_COLORS, MENU_FONT, playMenuSound } from '../utils/menuKit.js';

const S = 2;                                             // pixel-art scale (as the rest of the kit)
const PAGE = { x: -446, y: -166, w: 852, h: 394 };       // the scrolling page, relative to the panel centre
const RAIL_X = 428;
const TAB = { w: 68 * S, h: 20 * S, gap: 6, y: -201 };
const CARD_SLICE = 7;                                    // menu_card.png corner size (native px)
const KNOB_STEP = 6;                                     // px of travel per knob frame (it rolls)

export const LEDGER_PAGE_WIDTH = PAGE.w;

/** text styles shared by the journal and the quest log */
export const LEDGER_TEXT = {
    title: { fontFamily: MENU_FONT, fontSize: '20px', fontStyle: 'bold', color: MENU_COLORS.title, stroke: MENU_COLORS.stroke, strokeThickness: 3 },
    body: { fontFamily: MENU_FONT, fontSize: '16px', color: MENU_COLORS.text, lineSpacing: 5 },
    dim: { fontFamily: MENU_FONT, fontSize: '15px', color: MENU_COLORS.dim, lineSpacing: 4 },
    heading: { fontFamily: MENU_FONT, fontSize: '17px', color: MENU_COLORS.title, stroke: MENU_COLORS.stroke, strokeThickness: 4 },
    empty: { fontFamily: MENU_FONT, fontSize: '17px', fontStyle: 'italic', color: MENU_COLORS.dim, align: 'center' },
};

export default class LedgerPanel {
    /**
     * @param {Phaser.Scene} scene
     * @param {{ title: string, depth: number, y?: number, onClose: () => void }} opts
     */
    constructor(scene, { title, depth, y = 300, onClose }) {
        this.scene = scene;
        this.scrollY = 0;
        this.contentH = 0;
        this.tabs = [];
        this.tabIndex = -1;
        this.onTab = null;

        const panel = createMenuPanel(scene, 'ledger', scene.scale.width / 2, y, title);
        this.panel = panel;
        this.container = panel.container.setDepth(depth).setScrollFactor(0, 0, true).setVisible(false);
        addPanelClose(scene, panel, () => onClose?.());

        // the page: clipped, so cards scrolled up vanish under the tabs (a geometry mask lives in screen space)
        this.content = scene.add.container(PAGE.x, PAGE.y);
        const maskG = scene.make.graphics({ add: false });
        maskG.fillStyle(0xffffff).fillRect(this.container.x + PAGE.x, this.container.y + PAGE.y, PAGE.w, PAGE.h);
        this.content.setMask(maskG.createGeometryMask());
        this.maskGraphics = maskG;
        this.container.add(this.content);

        // the rail + its gear knob
        this.rail = scene.add.nineslice(RAIL_X, PAGE.y + PAGE.h / 2, 'menuRail', 0, 10, PAGE.h / S, 4, 4, 6, 6).setScale(S);
        this.knob = scene.add.image(RAIL_X, PAGE.y + 16, 'menuKnob', 0).setScale(S);
        const railHit = scene.add.zone(RAIL_X, PAGE.y + PAGE.h / 2, 36, PAGE.h).setInteractive({ useHandCursor: true });
        this.container.add([this.rail, railHit, this.knob]);
        let dragging = false;
        const fromPointer = (pointer) => {
            const top = this.container.y + PAGE.y + 16, span = PAGE.h - 32;
            this.scrollTo(Phaser.Math.Clamp((pointer.y - top) / span, 0, 1) * this.maxScroll());
        };
        railHit.on('pointerdown', (pointer, lx, ly, event) => { event?.stopPropagation(); dragging = true; fromPointer(pointer); this.knobLit(true); });
        railHit.on('pointerover', () => this.knobLit(true));
        railHit.on('pointerout', () => { if (!dragging) this.knobLit(false); });
        this.onMove = (pointer) => { if (dragging) fromPointer(pointer); };
        this.onUp = () => { if (dragging) { dragging = false; this.knobLit(false); } };
        scene.input.on('pointermove', this.onMove);
        scene.input.on('pointerup', this.onUp);
        scene.input.on('pointerupoutside', this.onUp);

        this.onWheel = (pointer, objs, dx, dy) => { if (this.visible) this.scrollBy(dy * 0.8); };
        scene.input.on('wheel', this.onWheel);
        this.onKey = (event) => this.handleKey(event);
        scene.input.keyboard.on('keydown', this.onKey);
        scene.events.once('shutdown', () => this.destroy());
        this.updateRail();
    }

    get visible() { return this.container.visible; }

    /** is the pointer over the visible page? (input ignores masks: a card scrolled under the tabs is still "there") */
    inPage(pointer) {
        const x = pointer.x - this.container.x, y = pointer.y - this.container.y;
        return x >= PAGE.x && x <= PAGE.x + PAGE.w && y >= PAGE.y && y <= PAGE.y + PAGE.h;
    }

    show() { this.container.setVisible(true); }
    hide() { this.container.setVisible(false); }

    // ------------------------------------------------------------------ tabs
    /** a row of tab plaques, centred on the panel; onSelect(index) when one is clicked (or ←/→) */
    setTabs(labels, onSelect) {
        this.tabs.forEach(t => { t.img.destroy(); t.text.destroy(); });
        this.tabs = [];
        this.onTab = onSelect;
        const w = TAB.w, step = w + TAB.gap;
        const x0 = -((labels.length - 1) * step) / 2;            // centred on the panel (the page itself leaves room for the rail)
        labels.forEach((label, i) => {
            const x = x0 + i * step;
            const img = this.scene.add.image(x, TAB.y, 'menuTab', 0).setScale(S).setInteractive({ useHandCursor: true });
            img.input.hitArea.setTo(1, 1, 66, 18);
            const text = this.scene.add.text(x, TAB.y, label, {
                fontFamily: MENU_FONT, fontSize: label.length > 9 ? '14px' : '16px', color: MENU_COLORS.text,
                stroke: MENU_COLORS.stroke, strokeThickness: 3,
            }).setOrigin(0.5);
            const tab = { img, text, hover: false };
            img.on('pointerover', () => { tab.hover = true; this.drawTab(i); playMenuSound(this.scene, 'hoverSound', 0.5); });
            img.on('pointerout', () => { tab.hover = false; this.drawTab(i); });
            img.on('pointerdown', (pointer, lx, ly, event) => {
                event?.stopPropagation();
                if (i === this.tabIndex) return;
                playMenuSound(this.scene, 'clickSound');
                this.selectTab(i, true);
            });
            this.container.add([img, text]);
            this.tabs.push(tab);
        });
    }

    selectTab(i, notify = false) {
        this.tabIndex = i;
        this.tabs.forEach((t, k) => this.drawTab(k));
        if (notify) this.onTab?.(i);
    }

    drawTab(i) {
        const t = this.tabs[i];
        if (!t) return;
        const sel = i === this.tabIndex;
        t.img.setFrame(sel ? 2 : t.hover ? 1 : 0);
        t.text.y = TAB.y + (sel ? -1 : 1);
        t.text.setColor(sel ? MENU_COLORS.textHover : t.hover ? MENU_COLORS.textHover : MENU_COLORS.text);
        t.text.setShadow(0, 0, '#7fff8e', sel ? 6 : 0, false, true);
    }

    // ------------------------------------------------------------------ page content
    /** empty the page and scroll back to the top */
    clear() {
        this.content.removeAll(true);
        this.scrollY = 0;
        this.content.y = PAGE.y;
        this.contentH = 0;
        this.updateRail();
    }

    /** an enamel card at page y (x 0, the page's full width unless given); resize it later with setSize */
    addCard(y, h, { x = 0, w = PAGE.w - 8, lit = false } = {}) {
        const card = this.scene.add.nineslice(x, y, 'menuCard', lit ? 1 : 0, w / S, Math.max(h, 30) / S,
            CARD_SLICE, CARD_SLICE, CARD_SLICE, CARD_SLICE).setOrigin(0, 0).setScale(S);
        this.content.add(card);
        return card;
    }

    /** a section heading across the page: gold title between two thin bronze rules */
    addHeading(y, label) {
        const text = this.scene.add.text(PAGE.w / 2, y, label, LEDGER_TEXT.heading).setOrigin(0.5, 0);
        const g = this.scene.add.graphics();
        const cy = y + text.height / 2, half = text.width / 2 + 14;
        g.lineStyle(2, 0x6b5a2e, 1).lineBetween(24, cy, PAGE.w / 2 - half, cy).lineBetween(PAGE.w / 2 + half, cy, PAGE.w - 32, cy);
        g.fillStyle(0x9fb59a, 1).fillRect(PAGE.w / 2 - half - 3, cy - 2, 4, 4).fillRect(PAGE.w / 2 + half - 1, cy - 2, 4, 4);
        this.content.add([g, text]);
        return text.height;
    }

    addEmpty(y, label) {
        const t = this.scene.add.text(PAGE.w / 2, y, label, { ...LEDGER_TEXT.empty, wordWrap: { width: PAGE.w - 80 } }).setOrigin(0.5, 0);
        this.content.add(t);
        return t.height;
    }

    setContentHeight(h) {
        this.contentH = h;
        this.scrollTo(this.scrollY);
    }

    // ------------------------------------------------------------------ scrolling
    maxScroll() { return Math.max(0, this.contentH - PAGE.h); }

    scrollTo(y) {
        this.scrollY = Phaser.Math.Clamp(y, 0, this.maxScroll());
        this.content.y = PAGE.y - this.scrollY;
        this.updateRail();
    }

    scrollBy(dy) { this.scrollTo(this.scrollY + dy); }

    updateRail() {
        const max = this.maxScroll();
        const on = max > 0;
        this.rail.setVisible(on);
        this.knob.setVisible(on);
        if (!on) return;
        const ky = PAGE.y + 16 + (this.scrollY / max) * (PAGE.h - 32);
        this.knob.y = ky;
        this.knob.setFrame((Math.floor(ky / KNOB_STEP) % 4 + 4) % 4 + (this.knobOn ? 4 : 0));
    }

    knobLit(on) { this.knobOn = on; this.updateRail(); }

    handleKey(event) {
        if (!this.visible) return;
        const line = 40;
        switch (event.code) {
            case 'ArrowDown': case 'KeyS': this.scrollBy(line); break;
            case 'ArrowUp': case 'KeyW': this.scrollBy(-line); break;
            case 'PageDown': this.scrollBy(PAGE.h - 40); break;
            case 'PageUp': this.scrollBy(-(PAGE.h - 40)); break;
            case 'Home': this.scrollTo(0); break;
            case 'End': this.scrollTo(this.maxScroll()); break;
            case 'ArrowRight': case 'KeyD':
                if (this.tabs.length && this.tabIndex < this.tabs.length - 1) { playMenuSound(this.scene, 'clickSound'); this.selectTab(this.tabIndex + 1, true); }
                break;
            case 'ArrowLeft': case 'KeyA':
                if (this.tabs.length && this.tabIndex > 0) { playMenuSound(this.scene, 'clickSound'); this.selectTab(this.tabIndex - 1, true); }
                break;
        }
    }

    destroy() {
        if (this.destroyed) return;
        this.destroyed = true;
        const input = this.scene.input;
        input?.off('wheel', this.onWheel);
        input?.off('pointermove', this.onMove);
        input?.off('pointerup', this.onUp);
        input?.off('pointerupoutside', this.onUp);
        input?.keyboard?.off('keydown', this.onKey);
        this.maskGraphics?.destroy();
        this.container?.destroy();
    }
}
