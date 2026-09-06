/**
 * equipmentTutorial.js — the optional, meta-narrative "equipment" tutorial offered by Master
 * Thaal in the intro.
 *
 * A small guided tour: each step highlights a HUD element and explains it. For the openable
 * panels (diary, quest log, map, inventory) the player opens them themselves (click the
 * highlighted icon or press the key) — doing so clears the indicator and reveals the explanation
 * of what's inside. Runs once. Purely additive UI — no game logic touched; the player can skip
 * at any point.
 *
 * Extracted from GameScene to keep the scene lean; it's a pure function of the scene, so the
 * scene just exposes `startEquipmentTutorial() { runEquipmentTutorial(this); }`.
 */

import LanguageSystem from '../systems/LanguageSystem.js';

/** Run the equipment tutorial on `scene` (a GameScene / subclass). */
export function runEquipmentTutorial(scene) {
    if (scene._tutorialActive) return;
    // Already done (e.g. re-entry): fire the completion signal so any deferred follow-up
    // (like an NPC waiting to walk off after the tutorial) still resolves.
    if (scene.registry.get('equipment_tutorial_done')) { scene.events.emit('equipment-tutorial-finished'); return; }
    scene._tutorialActive = true;
    scene.playerMovementSystem?.setDialogVisible(true); // lock movement while it runs

    const cs = LanguageSystem.getInstance?.().getLanguage?.() === 'cs';
    const T = (en, cz) => (cs ? cz : en);

    const steps = [
        { anchor: { x: 690, y: 50 },
          isOpen: () => !!scene.journalUI?.visible,
          close: () => { if (scene.journalUI && scene.journalUI.visible) scene.journalUI.toggle(); },
          show: T("This is your diary. (In meta-narrative terms: a menu of notes.) Open it with the icon top-right, or press J.",
                  "Tohle je tvůj deník. (Meta-narativně řečeno: menu s poznámkami.) Otevřeš ho ikonou vpravo nahoře, nebo klávesou J."),
          tabs: T("It gathers everything that matters — tabs for People, Places, Events, Lore, Dreams and Factions. Wherever the story takes you, the clues end up here.",
                  "Sbírá vše důležité — záložky Lidé, Místa, Události, Vědění, Sny a Frakce. Kamkoli tě příběh zavede, stopy skončí tady.") },
        { anchor: { x: 750, y: 50 },
          isOpen: () => !!scene.questLog?.questPanel?.visible,
          close: () => scene.questLog?.hideQuestLog(),
          show: T("Your quest log sits beside the diary — it tracks what you're supposed to be doing.",
                  "Deník úkolů je hned vedle deníku — drží, co máš dělat."),
          tabs: T("Active quests and their progress. Click a quest to expand its individual steps.",
                  "Aktivní úkoly a jejich postup. Rozklikni úkol pro jednotlivé kroky.") },
        { anchor: { x: 630, y: 50 },
          isOpen: () => !!scene.mapUI?.visible,
          close: () => { if (scene.mapUI && scene.mapUI.visible) scene.mapUI.toggle(); },
          show: T("The fast-travel map — the MAP icon, or press M.",
                  "Mapa rychlého cestování — ikona MAP, nebo klávesa M."),
          tabs: T("Click any place you've already visited to travel there. New places unlock as you discover them.",
                  "Klikni na místo, které jsi už navštívil, a přesuneš se tam. Nová místa se odemykají, jak je objevíš.") },
        { anchor: { x: 430, y: 22 },
          show: T("That gauge up top is your spores — part fungal currency, part fuel. They replenish slowly and with difficulty, so spend them wisely: some things cost them, some creatures feed on them, and merchants will pay for them.",
                  "Ten ukazatel nahoře jsou tvoje spory — napůl houbová měna, napůl palivo. Doplňují se jen pomalu a obtížně, tak s nimi šetři: něco je spotřebuje, něco se jimi živí a kupci ti je proplatí.") },
        { anchor: { x: 50, y: 50 },
          show: T("Growth and Decay. Meta-narratively: the world's moral-ecological slider. Your choices tip it — and the city, and its people, react in kind.",
                  "Růst a Rozklad. Meta-narativně: morálně-ekologický posuvník světa. Tvé volby ho naklánějí — a město i jeho obyvatelé podle toho reagují.") },
        { anchor: { x: 60, y: 540 },
          // The inventory lives in InventorySystem (scene.inventorySystem) — read its state.
          isOpen: () => !!scene.inventorySystem?.inventoryVisible || !!scene.inventorySystem?.inventoryPanel?.visible,
          close: () => scene.inventorySystem?.toggleInventory(false),
          show: T("Your inventory — that little mushroom bottom-left, or press I.",
                  "Tvůj inventář — ta houbička vlevo dole, nebo klávesa I."),
          tabs: T("Whatever you find or are given lives here. Some items can be used, worn, or sold.",
                  "Co najdeš nebo dostaneš, je tady. Některé předměty jdou použít, nosit nebo prodat.") },
    ];
    const finalText = T("And that's the lot. Meta-narrative lecture concluded — now if you'll excuse me, the Fermented Cap won't drink itself. Glory to the Eternal Mushroom!",
                        "A to je vše. Meta-narativní přednáška ukončena — a teď mě omluv, hospoda U Kvašeného klobouku se sama nevypije. Sláva Věčné houbě!");

    let i = 0, openClose = null;
    const objs = [];
    const clear = () => { objs.forEach(o => { try { o.destroy(); } catch (e) { /* ignore */ } }); objs.length = 0; };
    const finish = () => {
        if (openClose) { try { openClose(); } catch (e) { /* ignore */ } }
        openClose = null; clear();
        scene._tutorialActive = false;
        scene.registry.set('equipment_tutorial_done', true);
        scene.playerMovementSystem?.setDialogVisible(false);
        scene.events.emit('equipment-tutorial-finished'); // NPCs may defer their exit until now
    };

    const ringFor = (a) => {
        const g = scene.add.graphics().setDepth(6000); objs.push(g);
        let rr = 22;
        const draw = () => { g.clear(); g.lineStyle(6, 0x7fff8e, 0.14); g.strokeCircle(a.x, a.y, rr); g.lineStyle(3, 0x7fff8e, 0.9); g.strokeCircle(a.x, a.y, rr); };
        draw();
        const tw = scene.tweens.addCounter({ from: 22, to: 34, duration: 850, yoyo: true, repeat: -1, onUpdate: t => { rr = t.getValue(); draw(); } });
        objs.push({ destroy: () => tw.stop() });
    };

    const caption = (body, cy, buttons) => {
        const W = 560, PAD = 18, GAP = 16, BH = 32, BGAP = 12;
        const c = scene.add.container(400, cy).setDepth(6001); objs.push(c);
        const label = scene.add.text(0, 0, T('MASTER THAAL', 'MISTR THAAL'), { fontFamily: '"Courier New", monospace', fontSize: '11px', color: '#7fff8e', letterSpacing: 2 }).setOrigin(0.5, 0);
        const txt = scene.add.text(0, 0, body, { fontFamily: 'system-ui, -apple-system, sans-serif', fontSize: '16px', color: '#e6efdf', align: 'center', wordWrap: { width: W - 2 * PAD }, lineSpacing: 5 }).setOrigin(0.5, 0);
        buttons.forEach(b => { const t = scene.add.text(0, 0, b.label, { fontFamily: '"Courier New", monospace', fontSize: '14px', color: b.primary ? '#0b0e0a' : '#c8e6d0' }).setOrigin(0.5); b._t = t; b._w = t.width + 26; });
        const totalBW = buttons.reduce((s, b) => s + b._w, 0) + BGAP * (buttons.length - 1);
        const boxH = PAD + 16 + txt.height + GAP + BH + PAD;
        // Keep the whole box (incl. its buttons) on-screen — a tall caption near the bottom
        // would otherwise push the buttons below the 600px world height and hide them.
        c.y = Math.max(boxH / 2 + 10, Math.min(cy, 600 - boxH / 2 - 10));
        c.add(scene.add.rectangle(0, 0, W, boxH, 0x0c1410, 0.98).setStrokeStyle(2, 0x2f5a44));
        let y = -boxH / 2 + PAD;
        label.y = y; c.add(label); y += 20;
        txt.y = y; c.add(txt); y += txt.height + GAP;
        let bx = -totalBW / 2;
        buttons.forEach(b => {
            const rect = scene.add.rectangle(bx + b._w / 2, y + BH / 2, b._w, BH, b.primary ? 0x7fff8e : 0x14261a, b.primary ? 1 : 0.7).setStrokeStyle(1, 0x2f5a44).setInteractive({ useHandCursor: true });
            b._t.setPosition(bx + b._w / 2, y + BH / 2);
            rect.on('pointerover', () => rect.setScale(1.05));
            rect.on('pointerout', () => rect.setScale(1));
            rect.on('pointerdown', () => { if (scene.clickSound) scene.clickSound.play(); b.onClick(); });
            c.add(rect); c.add(b._t);
            bx += b._w + BGAP;
        });
    };

    const skipBtn = { label: T('Skip tutorial', 'Přeskočit'), onClick: finish };
    // Phase B: the panel is now open — the ring/prompt are cleared and the content is explained.
    const renderPhaseB = (step) => {
        clear(); // removes the highlight ring, the open-prompt and its poll
        caption(step.tabs, 540, [
            { label: T('Close & continue ▸', 'Zavřít a dál ▸'), primary: true, onClick: () => { if (openClose) { try { openClose(); } catch (e) { /* ignore */ } } openClose = null; i++; renderStep(); } },
            skipBtn,
        ]);
    };
    const renderStep = () => {
        clear();
        if (i >= steps.length) {
            caption(finalText, 300, [{ label: T('Done', 'Hotovo'), primary: true, onClick: finish }]);
            return;
        }
        const step = steps[i];
        const cy = step.anchor.y > 300 ? 130 : 470;
        if (step.isOpen) {
            // Interactive: the PLAYER opens the panel (click the highlighted icon or press the key);
            // opening it advances the step and removes the indicator. No "show me" button.
            if (step.isOpen()) { openClose = step.close; renderPhaseB(step); return; }
            ringFor(step.anchor);
            caption(step.show, cy, [skipBtn]);
            const poll = scene.time.addEvent({ delay: 150, loop: true, callback: () => {
                if (step.isOpen()) { openClose = step.close; renderPhaseB(step); }
            } });
            objs.push({ destroy: () => poll.remove() });
        } else {
            ringFor(step.anchor);
            caption(step.show, cy, [
                { label: T('Next ▸', 'Další ▸'), primary: true, onClick: () => { i++; renderStep(); } },
                skipBtn,
            ]);
        }
    };
    renderStep();
}
