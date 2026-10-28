// What happens in the game for each trailer shot. Every shot is captured to out/shots/<id>.mkv at the
// game's native 1067×600; edit.js decides which part of it is used, the camera move and the titles.
// `setup` runs once after the scene's create(); `update` runs every captured frame with ctx.t in seconds.

export const SURVEY_SCENES = [
    'IntroScene', 'EntryScene', 'CrossroadScene', 'EggCatedralScene', 'CathedralEntrance',
    'ScraperScene', 'ScraperInteriorScene', 'ScraperAmbraScene', 'SkyshipBoardScene',
    'Shed521GateScene', 'Shed521Scene', 'Shed521FloorsScene', 'ShedCourtyard', 'ShedRegistrationScene',
    'ShedHallScene', 'ShedApplicationsScene', 'ShedAbandonedOfficeScene',
    'ScreamingCorkScene', 'ScreamingCorkInteriorScene', 'ScreamingCorkClubScene',
    'VoxMarket', 'VoxmarketMarketScene', 'VoxmarketHallScene', 'BurningBearStreetScene',
];

// ---- helpers (page side) ----

const find = (scene, texKey) => scene.children.list.find(o => o.texture?.key === texKey);

// HUD modes, applied by the director right before every render (so UI created mid-frame never flashes):
/** 'hide' — cinematic: the HUD (depth ≥ 100) and hotspot labels go, except what the shot added itself. */
function hideHud(ctx) {
    for (const o of ctx.scene.children.list) {
        if (ctx.keep.has(o)) continue;
        if (o.depth >= 100 || o.type === 'Text') o.setVisible(false);
    }
}

/** 'quiet' — gameplay: keep the HUD, but drop the location-name toast. */
function quietHud(ctx) {
    for (const o of ctx.scene.children.list) {
        if (ctx.keep.has(o)) continue;
        if (o.type === 'Text' && o.depth === 100) o.setVisible(false);
    }
}

export const HUD = { hide: hideHud, quiet: quietHud };

function bubble(ctx, target, text, opts = {}) {
    const b = ctx.scene.showSpeechBubble(target, text, { duration: 60000, ...opts });
    if (b) ctx.keep.add(b);
    return b;
}

/** Real dialog box with trailer-length text; the options are ones the game offers in that conversation. */
function dialog(ctx, speaker, text, options) {
    const scene = ctx.scene;
    scene.showDialog({ speaker, text, options: options.map((t, i) => ({ text: t, key: `trailer_${i}`, next: 'main' })) });
}

/** Walk the protagonist to x the way PlayerMovementSystem does (its own movePriestTo bails out in some scene states). */
function walk(ctx, x, msPerPx = 5) {
    const s = ctx.scene, p = s.priest, pms = s.playerMovementSystem;
    if (!p) return;
    const glow = pms?.priestGlow;
    s.tweens.killTweensOf(glow ? [p, glow] : p); // e.g. EntryScene's own arrival walk, which ends in a dialog
    const dir = x < p.x ? -1 : 1;
    p.setScale(dir, 1);
    glow?.setScale(1.05 * dir, 1.05);
    if (pms) pms.isTweenMoving = true;
    p.play('walk', true);
    s.tweens.add({
        targets: glow ? [p, glow] : [p], x, duration: Math.abs(x - p.x) * msPerPx,
        onComplete: () => { if (pms) pms.isTweenMoving = false; p.play('idle', true); },
    });
}
function place(ctx, x) {
    const p = ctx.scene.priest;
    if (!p) return;
    p.x = x;
    if (ctx.scene.playerMovementSystem?.priestGlow) ctx.scene.playerMovementSystem.priestGlow.x = x;
}

function setGrowth(game, growth) {
    const gd = game.registry.get('growthDecaySystem');
    if (gd) gd.setGrowth(growth);
}

/** IntroScene: kill the auto-advancing captions and the fader; the trailer times everything itself. */
function tameIntro(scene) {
    scene.fadeFrom = () => scene.fader.setAlpha(0);
    scene.fadeTo = (_ms, done) => { scene.fader.setAlpha(0); done?.(); };
    scene.fader.setAlpha(0);
    scene.skipHint.setVisible(false);
    scene.input.removeAllListeners();
    scene.input.keyboard.removeAllListeners();
}

// ---- shots ----

export const SHOTS = [
    {
        id: 'hymnar', scene: 'IntroScene', duration: 6.2,
        setup(ctx) {
            const s = ctx.scene;
            tameIntro(s);
            s.nextShot1Step = () => {}; // no caption steps
            s.hideCaption();
            s.captionBand.setVisible(false);
            s.cameras.main.setScroll(0, 400);
            s.runSignal(() => {});
        },
    },
    {
        id: 'council', scene: 'IntroScene', duration: 8.6,
        setup(ctx) {
            const s = ctx.scene;
            tameIntro(s);
            s.nextShot1Step = () => {};
            s.dialogues = [
                { who: 'varhun', speaker: 'ARCHPRIEST VARHUN', text: 'A cry for help. From the city of Upper Morkezela.' },
                { who: 'rhull', speaker: 'ARCHPRIEST RHULL', text: "He is Thaal's apprentice. He is not the... sharpest mushroom in the forest." },
            ];
            s.lineIndex = 0;
            s.toShot2(); // wide shot now, Varhun's close-up after 1 s
        },
        update(ctx) {
            if (ctx.frame === Math.round(4.6 * ctx.fps)) { ctx.scene.finishTyping(); ctx.scene.nextLine(); }
        },
    },
    {
        id: 'city', scene: 'EntryScene', duration: 4.4,
        setup(ctx) {
            place(ctx, 100);
            ctx.scene.priest.initialX = 100; // foreground parallax reference (the arrival walk set it to -50)
            walk(ctx, 480); // up to Master Thaal (x 600)
        },
        hud: 'hide',
    },
    {
        id: 'crossroad', scene: 'CrossroadScene', duration: 4.4,
        setup(ctx) { place(ctx, 120); walk(ctx, 270); },
        hud: 'hide',
        update(ctx) {
            if (ctx.frame === Math.round(1.4 * ctx.fps)) bubble(ctx, { x: 425, y: 136 }, "Hey chief, what's up?", { offsetY: 0 }); // tail on the top of the head
        },
    },
    {
        id: 'cathedral', scene: 'EggCatedralScene', duration: 4.4,
        setup(ctx) { place(ctx, 90); walk(ctx, 300); },
        hud: 'hide',
    },
    {
        id: 'bears', scene: 'BurningBearStreetScene', duration: 4.4,
        setup(ctx) { place(ctx, 820); walk(ctx, 640); },
        hud: 'hide',
    },
    {
        id: 'gate', scene: 'Shed521GateScene', duration: 2.6,
        hud: 'hide',
    },
    {
        id: 'registration', scene: 'ShedRegistrationScene', duration: 2.6,
        setup(ctx) { place(ctx, 110); walk(ctx, 300); },
        hud: 'hide',
    },
    {
        id: 'floors', scene: 'Shed521FloorsScene', duration: 2.6,
        hud: 'hide',
    },
    {
        id: 'ortolan', scene: 'ShedCourtyard', duration: 4.4,
        setup(ctx) { place(ctx, 420); },
        hud: 'quiet',
        update(ctx) {
            if (ctx.frame === Math.round(0.5 * ctx.fps)) {
                dialog(ctx, 'Ortolan Šmelc', 'Do you know how hard it is to design complex board games with just two hands?', [
                    'Why do you need extra arms?', 'I could help you with the paperwork.', 'Good luck with that.',
                ]);
            }
        },
    },
    {
        id: 'shedGrowth', scene: 'Shed521Scene', duration: 2.6,
        before(game) { setGrowth(game, 100); },
        setup(ctx) { place(ctx, 260); },
        hud: 'quiet',
    },
    {
        id: 'shedDecay', scene: 'Shed521Scene', duration: 2.6,
        before(game) { setGrowth(game, 0); },
        setup(ctx) { place(ctx, 260); },
        hud: 'quiet',
    },
    {
        id: 'office', scene: 'ShedAbandonedOfficeScene', duration: 4.4,
        before(game) { setGrowth(game, 50); },
        hud: 'hide',
    },
    {
        id: 'scraper', scene: 'ScraperScene', duration: 2.6,
        hud: 'hide',
    },
    {
        id: 'liftmother', scene: 'ScraperInteriorScene', duration: 4.4,
        setup(ctx) { place(ctx, 200); walk(ctx, 380); },
        hud: 'hide',
        update(ctx) {
            if (ctx.frame === Math.round(0.9 * ctx.fps)) bubble(ctx, { x: 510, y: 300 }, 'Welcome, little toadstool. I am Lift-Mother.', { offsetY: 40 });
        },
    },
    {
        id: 'voxmarket', scene: 'VoxMarket', duration: 2.6,
        hud: 'hide',
    },
    {
        id: 'zerren', scene: 'VoxmarketMarketScene', duration: 2.6,
        setup(ctx) { place(ctx, 420); },
        hud: 'hide',
        update(ctx) {
            if (ctx.frame === Math.round(0.2 * ctx.fps)) bubble(ctx, find(ctx.scene, 'zerren'), 'Looking for anything special today?', { offsetY: 120 });
        },
    },
    {
        id: 'skyship', scene: 'SkyshipBoardScene', duration: 4.6,
        setup(ctx) { place(ctx, 420); },
        hud: 'hide',
        update(ctx) {
            if (ctx.frame === Math.round(0.2 * ctx.fps)) bubble(ctx, find(ctx.scene, 'captainLiris'), 'Welcome aboard the Verdigrace.', { offsetY: 160 });
        },
    },
    {
        id: 'edgar', scene: 'ScreamingCorkScene', duration: 2.6,
        setup(ctx) { place(ctx, 640); },
        hud: 'hide',
    },
    {
        id: 'feral', scene: 'ScreamingCorkClubScene', duration: 4.4,
        async setup(ctx, { frame }) {
            const s = ctx.scene;
            await frame(false); // create()'s delayedCalls are only pending until the clock's next update
            s.time.removeAllEvents(); // the welcome dialog
            s.startPerformance();
            s.priest?.setVisible(false);
            s.playerMovementSystem?.priestGlow?.setVisible(false);
        },
        hud: 'hide',
    },
    {
        id: 'elphi', scene: 'ScraperAmbraScene', duration: 4.8,
        setup(ctx) { place(ctx, 300); walk(ctx, 600); },
        hud: 'hide',
    },
    { id: 'hall', scene: 'ShedHallScene', duration: 1.6, hud: 'hide' },
    { id: 'applications', scene: 'ShedApplicationsScene', duration: 1.6, hud: 'hide' },
    { id: 'auction', scene: 'VoxmarketHallScene', duration: 2.4, hud: 'hide' },
    { id: 'courtyard', scene: 'ShedCourtyard', duration: 2.2, hud: 'hide' },
];

// ---- Steam screenshots ----
// Bubble lines come verbatim from the game's own dialogs (lang/cs/dialogs for Czech), trimmed the same way.
const L = (byLang) => byLang[window.__cap?.args?.lang] ?? byLang.en;

// Plain gameplay with the HUD on (Steam: "screenshots should exclusively show the gameplay", no added text).
// Captured `at` seconds after setup, upscaled to 1920×1080 → out/screenshots/<id>.png (capture.sh --screenshots).

export const STILLS = [
    {
        id: '01_crossroad', scene: 'CrossroadScene', at: 1.2, hud: 'quiet',
        setup(ctx) { place(ctx, 250); bubble(ctx, { x: 425, y: 136 }, L({ en: "Hey chief, what's up?", cs: 'Čau, šéfe, jak je?' }), { offsetY: 0 }); },
    },
    {
        id: '02_cathedral_guardian', scene: 'CathedralEntrance', at: 1.2, hud: 'quiet',
        setup(ctx) { place(ctx, 330); bubble(ctx, { x: 534, y: 345 }, L({ en: 'Halt. The yolk sleeps uneasily today.', cs: 'Stůj. Žloutek dnes spí neklidně.' }), { offsetY: 0 }); },
    },
    {
        id: '03_ortolan_dialog', scene: 'ShedCourtyard', at: 1.2, hud: 'quiet',
        setup(ctx) { place(ctx, 420); ctx.scene.showDialog('main'); },
    },
    {
        id: '04_registration', scene: 'ShedRegistrationScene', at: 1.2, hud: 'quiet',
        setup(ctx) { place(ctx, 300); },
    },
    {
        id: '05_shed521_gnur', scene: 'Shed521Scene', at: 1.2, hud: 'quiet',
        before(game) { setGrowth(game, 15); },
        setup(ctx) { place(ctx, 420); bubble(ctx, { x: 566, y: 420 }, L({
            en: "What're you lookin' for, outsider? Body upgrade? New lungs? Or just bad ideas?",
            cs: 'Co hledáš, cizinče? Vylepšení těla? Nové plíce? Nebo jen špatné nápady?',
        }), { offsetY: 0 }); },
    },
    {
        id: '06_lift_mother', scene: 'ScraperInteriorScene', at: 1.2, hud: 'quiet',
        before(game) { setGrowth(game, 50); },
        setup(ctx) { place(ctx, 380); bubble(ctx, { x: 510, y: 300 }, L({ en: 'Welcome, little toadstool. I am Lift-Mother.', cs: 'Vítej, malá muchomůrko.' }), { offsetY: 40 }); },
    },
    {
        id: '07_voxmarket_zerren', scene: 'VoxmarketMarketScene', at: 1.2, hud: 'quiet',
        setup(ctx) { place(ctx, 400); bubble(ctx, find(ctx.scene, 'zerren'), L({ en: 'Looking for anything special today?', cs: 'Hledáte něco zvláštního?' }), { offsetY: 120 }); },
    },
    {
        id: '08_feral_toast', scene: 'ScreamingCorkClubScene', at: 6, hud: 'quiet', // after the "begins playing" toasts
        async setup(ctx, { frame }) {
            const s = ctx.scene;
            await frame(false);
            s.time.removeAllEvents(); // the welcome dialog
            s.startPerformance();
            place(ctx, 120);
        },
    },
];

// ---- gameplay ("10 tips") shots: a visible cursor drives the real UI ----
// Clicks are real DOM mouse events on the game canvas, so hover states, dialogs, the shop, the inventory
// and click-to-walk all react exactly as they do for a player.

const CURSOR_ROWS = [
    'X..........',
    'XX.........',
    'XWX........',
    'XWWX.......',
    'XWWWX......',
    'XWWWWX.....',
    'XWWWWWX....',
    'XWWWWWWX...',
    'XWWWWWWWX..',
    'XWWWWWWWWX.',
    'XWWWWWWXXXX',
    'XWWWXWWX...',
    'XWWX.XWWX..',
    'XWX..XWWX..',
    'XX....XWWX.',
    '......XWWX.',
    '.......XX..',
];

function cursorTexture(scene) {
    if (scene.textures.exists('trailerCursor')) return;
    const t = scene.textures.createCanvas('trailerCursor', CURSOR_ROWS[0].length, CURSOR_ROWS.length);
    const c = t.getContext();
    CURSOR_ROWS.forEach((row, y) => [...row].forEach((ch, x) => {
        if (ch === '.') return;
        c.fillStyle = ch === 'X' ? '#14110d' : '#e8e2cf';
        c.fillRect(x, y, 1, 1);
    }));
    t.refresh();
}

/** Every Text (inside containers too) containing `needle` (any case), visible on screen, top to bottom. */
function findTexts(scene, needle, exact = false) {
    const out = [];
    const n = needle.toLowerCase();
    const visit = (list, parentVisible) => {
        for (const o of list) {
            const vis = parentVisible && o.visible !== false && (o.alpha ?? 1) > 0.05;
            const t = o.type === 'Text' && o.text.toLowerCase();
            if (t && vis && (exact ? t.trim() === n : t.includes(n))) out.push(o);
            if (o.list) visit(o.list, vis);
        }
    };
    visit(scene.children.list, true);
    return out.map(o => ({ o, b: o.getBounds() })).sort((a, z) => a.b.y - z.b.y);
}

/** First visible sprite/image with this texture, looking inside containers too (inventory slots, dialogs). */
function findSprite(scene, texKey) {
    const visit = (list, parentVisible) => {
        for (const o of list) {
            const vis = parentVisible && o.visible !== false;
            if (vis && o.texture?.key === texKey && o.type !== 'Text') return o;
            const inner = o.list && visit(o.list, vis);
            if (inner) return inner;
        }
        return null;
    };
    return visit(scene.children.list, true);
}

function makeCursor(ctx, x, y) {
    const s = ctx.scene;
    cursorTexture(s);
    const canvas = ctx.game.canvas;
    const img = s.add.image(x, y, 'trailerCursor').setOrigin(0, 0).setScrollFactor(0).setDepth(1e6);
    ctx.keep.add(img);
    const mouse = (type, buttons = 0) => {
        const r = canvas.getBoundingClientRect();
        const cx = r.left + img.x * r.width / s.scale.width, cy = r.top + img.y * r.height / s.scale.height;
        canvas.dispatchEvent(new MouseEvent(type, { clientX: cx, clientY: cy, button: 0, buttons, bubbles: true, cancelable: true }));
    };
    mouse('mouseover');
    const cur = {
        /** Glide to (tx, ty), or to target() re-read every frame so a walking NPC is still under the cursor on arrival. */
        moveTo(tx, ty, ms = 450, target = null) {
            const from = { x: img.x, y: img.y };
            s.tweens.addCounter({
                from: 0, to: 1, duration: ms, ease: 'Sine.easeInOut',
                onUpdate: (tw) => {
                    const k = tw.getValue();
                    const [x, y] = target ? target() : [tx, ty];
                    img.setPosition(from.x + (x - from.x) * k, from.y + (y - from.y) * k);
                    mouse('mousemove');
                },
            });
        },
        /** Point at a text: a little in from its left edge, vertically centred. pick: 'first' | 'last' (lowest on screen). */
        toText(needle, ms = 450, { exact = false, pick = 'first' } = {}) {
            const hits = findTexts(s, needle, exact);
            if (!hits.length) { window.__cap.log(`cursor: no text "${needle}"`); return; }
            const { b } = pick === 'last' ? hits[hits.length - 1] : hits[0];
            cur.moveTo(b.x + Math.min(b.width * 0.35, 70), b.centerY, ms);
        },
        toSprite(texKey, ms = 450, dy = 0) {
            const o = findSprite(s, texKey);
            if (!o) { window.__cap.log(`cursor: no sprite "${texKey}"`); return; }
            cur.moveTo(0, 0, ms, () => { const b = o.getBounds(); return [b.centerX, b.centerY + dy]; });
        },
        hide() { img.setVisible(false); },
        click() {
            mouse('mousedown', 1);
            const ring = s.add.circle(img.x, img.y, 3).setStrokeStyle(2, 0xe8e2cf, 1).setFillStyle().setScrollFactor(0).setDepth(1e6 - 1);
            ctx.keep.add(ring);
            s.tweens.add({ targets: ring, radius: 14, alpha: 0, duration: 320, onComplete: () => ring.destroy() });
            s.time.delayedCall(70, () => mouse('mouseup'));
        },
    };
    return cur;
}

/** update() that fires each [seconds, fn(cursor, ctx)] step once, in order. */
function script(steps) {
    return (ctx) => {
        ctx.step ??= 0;
        while (ctx.step < steps.length && steps[ctx.step][0] <= ctx.t + 1e-6) steps[ctx.step++][1](ctx.cursor, ctx);
    };
}

/** No random ambient symbiont lines during a shot (they would land at an unplanned moment); undone in after(). */
function muteSymbionts(ctx) { const ss = ctx.scene.symbiontSystem; if (ss) ss.getRandomMessage = () => null; }
function unmuteSymbionts(ctx) { delete ctx.scene.symbiontSystem?.getRandomMessage; }

const HUD_BTN = { map: [897, 50], journal: [957, 50], quests: [1017, 50], inventory: [60, 540] };

const AMBER_OLTRAC = {
    id: 'amberOltrac', name: 'Amber Oltrac',
    description: 'The rarest and most potent form of Oltrac. Said to allow glimpses beyond the veil of reality.',
    price: 50, type: 'drug', usable: true, consumable: true, stackable: true,
};

SHOTS.push(
    {
        id: 'g_gnur', scene: 'Shed521Scene', duration: 4.4, hud: 'quiet',
        before(game) { setGrowth(game, 50); },
        setup(ctx) {
            const s = ctx.scene;
            s.tweens.killTweensOf(s.gnur); // he paces past the elevator zone, which would take the click
            s.gnur.setPosition(640, s.gnur.y);
            place(ctx, 470);
            ctx.cursor = makeCursor(ctx, 860, 470);
        },
        update: script([
            [0.7, c => c.toSprite('gnur', 450)],
            [1.25, c => c.click()],
            [2.0, c => c.toText('Who are you exactly', 450)],
            [2.6, c => c.click()],
        ]),
    },
    {
        id: 'g_kloor', scene: 'VoxMarket', duration: 8.0, hud: 'quiet',
        setup(ctx) { ctx.scene.addMoney(150, false); place(ctx, 640); ctx.cursor = makeCursor(ctx, 700, 420); },
        update: script([
            [1.1, c => c.toSprite('kloor', 450, -30)],
            [1.65, c => c.click()],
            [2.4, c => c.toText('What are you selling', 400)],
            [2.9, c => c.click()],
            [3.7, c => c.toText('Show me what you have', 400)],
            [4.2, c => c.click()],
            [4.9, c => c.toText('Amber Oltrac', 450)],
            [5.45, c => c.click()],
            [6.1, c => c.toText('Buy item', 400)],
            [6.6, c => c.click()],
        ]),
    },
    {
        id: 'g_oltrac', scene: 'ShedCourtyard', duration: 8.4, hud: 'quiet',
        setup(ctx) {
            const s = ctx.scene;
            s.addItemToInventory({ ...AMBER_OLTRAC });
            place(ctx, 160);
            ctx.cursor = makeCursor(ctx, 520, 420);
        },
        update: script([
            [0.1, c => c.moveTo(430, 545, 350)],
            [0.5, c => c.click()],                                   // walk
            [1.3, c => c.moveTo(...HUD_BTN.inventory, 450)],
            [1.85, c => c.click()],                                  // open the inventory
            [2.6, c => c.toSprite('amberOltrac', 400)],               // its icon (utils/itemIcons.js)
            [3.15, c => c.click()],                                  // the item → "Use / Cancel"
            [3.8, c => c.toText('Use', 350, { exact: true })],
            [4.2, c => c.click()],
            [4.3, (c, ctx) => c.moveTo(900, 330, 900)],
        ]),
        after(ctx) { ctx.scene.effectsSystem?.clearEffects(true); },
    },
    {
        id: 'g_corpse', scene: 'CrossroadScene', duration: 7.8, hud: 'quiet',
        setup(ctx) { place(ctx, 250); muteSymbionts(ctx); ctx.cursor = makeCursor(ctx, 640, 470); },
        update: script([
            [0.8, c => c.toSprite('crossroad_corpse', 450, -40)],
            [1.4, c => c.click()],
            [2.0, c => c.toText('Cut it open', 350)],
            [2.4, c => c.click()],
            [3.0, c => c.toText('Accept Thorne-Still', 350)],
            [3.4, c => c.click()],
            [4.0, c => c.toText('Continue', 350)],
            [4.4, c => c.click()],
            [4.7, c => c.moveTo(640, 420, 600)],
            // one of Thorne-Still's own ambient lines (SymbiontSystem.getRandomMessage), shown on cue
            [4.9, (c, ctx) => ctx.scene.showSymbiontBubble('thorne-still', "This body has too many elbows. I'm starting a petition.")],
        ]),
        after(ctx) {
            unmuteSymbionts(ctx);
            ctx.scene.symbiontSystem?.removeSymbiont('thorne-still');
            // the corpse counts as used up once Thorne-Still is out; g_spores needs it whole again
            ['symbiont_thorne_still_offered', 'symbiont_thorne_still_accepted'].forEach(id => ctx.scene.journalSystem.entries.delete(id));
        },
    },
    {
        id: 'g_brainrot', scene: 'VoxmarketHallScene', duration: 7.0, hud: 'quiet',
        before(game) { setGrowth(game, 35); },
        setup(ctx) {
            const s = ctx.scene;
            // the auction errand (from the Seldo quest) and a bonded Thorne-Still unlock the [Brain Rot] option
            if (!s.hasJournalEntry('seldo_auction_errand')) {
                s.addJournalEntry('seldo_auction_errand', 'Auction errand', 'Seldo sent me to the Voxmarket auction.', s.journalSystem.categories.EVENTS);
            }
            s.symbiontSystem.addSymbiont('thorne-still', { name: 'Thorne-Still', power: 0, ability: 'Brain Rot' });
            muteSymbionts(ctx);
            place(ctx, 250);
            ctx.cursor = makeCursor(ctx, 760, 460);
        },
        update: script([
            [0.8, c => c.toSprite('heshAndVell', 450, -30)],
            [1.4, c => c.click()],
            [2.2, c => c.toText('▼', 350, { pick: 'last' })],          // the [Brain Rot] option sits below the fold
            [2.6, c => c.click()],
            [3.0, c => c.toText('[Brain Rot]', 450)],
            [3.6, c => c.click()],
        ]),
        after(ctx) { unmuteSymbionts(ctx); ctx.scene.symbiontSystem?.removeSymbiont('thorne-still'); },
    },
    {
        id: 'g_edgar', scene: 'ScreamingCorkScene', duration: 6.2, hud: 'quiet',
        setup(ctx) { place(ctx, 560); ctx.cursor = makeCursor(ctx, 760, 470); },
        update: script([
            [0.6, c => c.toSprite('edgarEskola', 450, -40)],
            [1.15, c => c.click()],
            [1.9, c => c.toText('Hello there', 400)],
            [2.4, c => c.click()],
        ]),
    },
    {
        // last: by now the other gameplay shots have filled the journal with their real entries
        id: 'g_journal', scene: 'ScraperInteriorScene', duration: 6.8, hud: 'quiet',
        setup(ctx) {
            const f = ctx.game.registry.get('factionSystem');
            if (f) Object.keys(f.factions).forEach((k, i) => f.modifyReputation(k, [30, -20, 12][i] ?? 0));
            place(ctx, 300);
            ctx.cursor = makeCursor(ctx, 640, 320);
        },
        update: script([
            [0.1, c => c.moveTo(...HUD_BTN.journal, 500)],
            [0.7, c => c.click()],
            [1.5, c => c.toText('People', 400, { exact: true })],
            [1.95, c => c.click()],
            [3.4, c => c.toText('Factions', 450, { exact: true })],
            [3.95, c => c.click()],
        ]),
    },
    {
        // spores into the corpse → a mycelium tree → click it (the trailer cuts from here to the skyship deck)
        id: 'g_spores', scene: 'CrossroadScene', duration: 6.0, hud: 'quiet',
        setup(ctx) { place(ctx, 250); ctx.cursor = makeCursor(ctx, 640, 470); },
        update: script([
            [0.8, c => c.toSprite('crossroad_corpse', 450, -40)],
            [1.4, c => c.click()],
            [2.0, c => c.toText('Plant spores', 350)],
            [2.4, c => c.click()],
            [3.0, c => c.toText('Continue', 350)],
            [3.4, c => c.click()],                                   // the corpse grows into a tree
            [4.3, (c, ctx) => c.moveTo(ctx.scene.corpseX + 28, 100, 550)],
            [4.9, (c, ctx) => { ctx.scene.isTransitioning = false; c.click(); }], // the director had locked exits
        ]),
        after(ctx) {
            ctx.game.registry.set('crossroadGrowth', false);
            ctx.scene.journalSystem.entries.delete('crossroad_corpse_spores_planted');
        },
    },
);

// ---- Steam description GIFs (gifs.mjs): textless, HUD off ----

SHOTS.push(
    { id: 'gif_growth', scene: 'Shed521Scene', duration: 3.4, hud: 'hide', before(game) { setGrowth(game, 100); }, setup(ctx) { place(ctx, 300); } },
    { id: 'gif_decay', scene: 'Shed521Scene', duration: 3.4, hud: 'hide', before(game) { setGrowth(game, 0); }, setup(ctx) { place(ctx, 300); } },
    { id: 'gif_corpse_before', scene: 'CrossroadScene', duration: 2.6, hud: 'hide', before(game) { setGrowth(game, 50); }, setup(ctx) { place(ctx, 250); } },
    {
        id: 'gif_corpse_after', scene: 'CrossroadScene', duration: 3.4, hud: 'hide',
        setup(ctx) { place(ctx, 250); ctx.game.registry.set('crossroadGrowth', true); ctx.scene.applyGrowth(); },
        after(ctx) { ctx.game.registry.set('crossroadGrowth', false); },
    },
    {
        id: 'gif_oltrac', scene: 'ShedCourtyard', duration: 5.6, hud: 'hide',
        setup(ctx) {
            const fx = ctx.scene.effectsSystem;
            ctx.keep.add(fx.effectsContainer);          // depth 5000, would otherwise go with the HUD
            fx.startPsychedelicComments = () => {};     // the comments are text
            place(ctx, 330);
        },
        update: script([[1.0, (c, ctx) => ctx.scene.effectsSystem.applyDrugEffect({ ...AMBER_OLTRAC })]]),
        after(ctx) { ctx.scene.effectsSystem?.clearEffects(true); },
    },
);
