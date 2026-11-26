/**
 * Ulvarex, the Borrowed Horizon: the demo's second symbiont (systems/SymbiontSystem.js), and how she is found.
 *
 * She lives pressed into a puddle's reflection, and only an Oltrac trip shows her: Violet or Amber (not Gray), the
 * effect EffectsSystem keeps in registry 'activeDrugEffect' across scenes. Three places have her puddle: the Scraper
 * 1140 rooftop (ScraperScene), the Shed 521 gate yard by the barrier (Shed521GateScene) and the skyship deck
 * (SkyshipBoardScene). On a trip there the puddle shows a sunset instead of the grey sky, its sun opens as an eye
 * and the conversation starts by itself, once per trip; clicking the puddle afterwards (same trip) asks again.
 * Declined, or no free slot: she shows on a later trip, and then greets him as someone she knows (ulvarex_again;
 * met = the 'met_ulvarex' journal entry). Bonded: never again.
 *
 * A scene calls preloadUlvarexPuddle(this, site) in preload(), setupUlvarexEncounter(this, site) in create() and
 * spreads ulvarexDialog(this) into its dialogContent. Czech: lang/cs/dialogs/UlvarexEncounter.js (merged into those scenes in lang/cs/dialogs/index.js).
 *
 * Her uses elsewhere check canWeave(scene, cost) and pay with spendWeave(scene, cost): she must be carried and awake
 * (Decay not above 70) and the spores must be there. Rule of thumb for what they do to the world: a mirage that
 * protects something living leans to Growth, one for plain gain to Decay. The demo's are all Growth.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { UI_FONT, UI_SMALL } from './pixelFrame.js';

export const ULVAREX_ID = 'ulvarex-borrowed-horizon';
/** The trips that open the eyes far enough (Gray Oltrac is too mild) */
const SEEING_TRIPS = new Set(['violetOltrac', 'amberOltrac']);
const TRIP_MS = 180000;          // EffectsSystem.effectDuration
const SEEN_KEY = 'ulvarex_seen_trip';   // registry: the startTime of the trip she already spoke on
const ULVAREX_ROW = 1;           // her row in assets/images/ui/symbionts.png (GameScene SYMBIONT_ROWS)

/** The Violet/Amber Oltrac trip under way ({ id, startTime }), or null. */
export function seeingTrip(scene) {
    const e = scene.registry.get('activeDrugEffect');
    if (!e || !SEEING_TRIPS.has(e.id) || Date.now() - e.startTime >= TRIP_MS) return null;
    return e;
}

export const hasUlvarex = (scene) => !!scene.symbiontSystem?.hasSymbiont(ULVAREX_ID);

/** He has spoken with her (her journal entry is written when she first speaks: ulvarex_reach). */
const metUlvarex = (scene) => !!scene.hasJournalEntry?.('met_ulvarex');

/** Ulvarex can weave right now: carried, awake (Decay ≤ 70) and `cost` spores at hand. */
export const canWeave = (scene, cost = 0) => !!scene.symbiontSystem?.canWeave?.(cost);

/** Pay a weave's spores. */
export function spendWeave(scene, cost) {
    scene.registry.get('sporeSystem')?.modifySpores(-cost);
}

/** A free symbiont slot (the bought one counts: SymbiontSystem reads the journal). */
function hasFreeSlot(scene) {
    const sys = scene.symbiontSystem;
    if (!sys) return false;
    sys.reconcileUnlockedSlotsFromJournal();
    return sys.symbionts.size < sys.unlockedSlots;
}

/**
 * Her puddles (tools/artgen/ulvarex_puddle.py): one sheet per place, the spot = the frame's middle. Frames 0-1 the sun
 * shut (ripples), 2-3 opening, 4-6 open and looking at you, 7-8 to the left, 9-10 to the right, 11 half shut (a blink),
 * 12 the plain grey puddle (the roof's is painted into its background, so its frame 12 is empty).
 */
const PUDDLES = {
    roof:    { w: 104, h: 16, x: 336, y: 550, plain: false },   // ScraperScene: the puddle in the rooftop's painting
    gate:    { w: 124, h: 36, x: 588, y: 522, plain: true },    // Shed521GateScene: on the cobbles of the yard
    skyship: { w: 120, h: 36, x: 440, y: 512, plain: true },    // SkyshipBoardScene: on the deck planks
};
const puddleKey = site => `ulvarexPuddle_${site}`;
const rep = (f, n) => Array(n).fill(f);
// (10 fps: a frame repeated = held; the blink is quick)
const EYE_ANIMS = {
    shut: { frames: [...rep(0, 5), ...rep(1, 5)], repeat: -1 },
    open: { frames: [...rep(0, 3), 2, 2, 3, 3, 4], repeat: 0 },
    idle: { frames: [
        ...rep(4, 4), ...rep(5, 4), ...rep(6, 4), ...rep(4, 4), ...rep(5, 4), ...rep(6, 4),
        ...rep(7, 4), ...rep(8, 4), ...rep(7, 4), ...rep(8, 4), ...rep(4, 4), ...rep(5, 4),
        11, 0, 11, ...rep(6, 4), ...rep(4, 4), ...rep(5, 4),
        ...rep(9, 4), ...rep(10, 4), ...rep(9, 4), ...rep(10, 4), ...rep(6, 4), ...rep(4, 4), ...rep(5, 4), ...rep(6, 4),
    ], repeat: -1 },
};

/** A scene with her puddle loads its sheet in preload(). */
export function preloadUlvarexPuddle(scene, site) {
    const p = PUDDLES[site];
    scene.load.spritesheet(puddleKey(site), `assets/images/props/ulvarex_puddle_${site}.png`, { frameWidth: p.w, frameHeight: p.h });
}

/**
 * Her puddle in a scene (`site`: a PUDDLES entry). The plain puddle is always there (the roof's is in the painting);
 * on a seeing trip the sunset fades in over it, its sun shut, and the first time she shows on a trip she starts
 * talking as soon as nothing else is open: the sun opens as an eye and looks at him.
 */
export function setupUlvarexEncounter(scene, site) {
    scene._ulvarex = null;
    scene._scriptedWalk = false;   // (scene instances are re-used)
    const P = PUDDLES[site], key = puddleKey(site);
    const { x, y } = P;
    if (P.plain) scene.add.sprite(x, y, key, 12).setDepth(1);
    if (hasUlvarex(scene)) return;

    for (const [name, a] of Object.entries(EYE_ANIMS)) {
        if (!scene.anims.exists(`${key}_${name}`)) {
            scene.anims.create({ key: `${key}_${name}`, frameRate: 10, repeat: a.repeat,
                frames: scene.anims.generateFrameNumbers(key, { frames: a.frames }) });
        }
    }
    const sunset = scene.add.sprite(x, y, key, 0).setDepth(2).setAlpha(0).setVisible(false);
    // a soft warm light round the water while she shows (WebGL; without it, none)
    if (sunset.preFX) sunset.preFX.padding = 14;
    const glow = sunset.preFX?.addGlow(0xffaa5a, 0, 0, false, 0.1, 12) || null;
    // Her voice: the dialog styles look for a visible sprite of her symbiont sheet to put her line over (Bubbles) and
    // to take her portrait's animation from (Cinema); this one sits unseen (alpha 0) over the sun while she talks
    if (!scene.anims.exists('ulvarex-world-idle')) {
        scene.anims.create({ key: 'ulvarex-world-idle', frameRate: 6, repeat: -1,
            frames: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 3, 3, 3].map(f => ({ key: 'symbionts', frame: ULVAREX_ROW * 4 + f })) });
    }
    const voice = scene.add.sprite(x, y - P.h / 2 - 16, 'symbionts', ULVAREX_ROW * 4).setDepth(2).setAlpha(0).setVisible(false);
    voice.play('ulvarex-world-idle');

    // A click on the puddle (on a trip, before she's bonded) asks her again
    const zone = scene.add.zone(x, y, P.w + 10, Math.max(P.h + 10, 30)).setDepth(8);
    const label = scene.add.text(x, y - P.h / 2 - 28, LanguageSystem.getInstance().t('ui.hotspots.ulvarexPuddle'), {
        fontFamily: UI_FONT, fontSize: UI_SMALL, fill: '#7fff8e', backgroundColor: 'rgba(12, 20, 16, 0.92)', padding: { x: 6, y: 4 }
    }).setOrigin(0.5).setDepth(100).setAlpha(0);
    zone.on('pointerover', () => { if (state.shown && !scene.dialogVisible) label.setAlpha(1); });
    zone.on('pointerout', () => label.setAlpha(0));
    zone.on('pointerdown', (pointer, lx, ly, event) => {
        event?.stopPropagation?.();
        if (!state.shown || scene.dialogVisible || scene.isInputBlocked?.() || hasUlvarex(scene)) return;
        label.setAlpha(0);
        // not met yet (he stepped back from her first look): she speaks up now, as she would have
        approach(() => talk(metUlvarex(scene) ? 'ulvarex_reconsider' : 'ulvarex_reach'));
    });

    const state = { shown: false, sunset, glow, voice, zone, x, y, eyeOpen: false };
    scene._ulvarex = state;
    let glowTween = null;

    const setVisible = (v) => sunset.setVisible(v);
    const stopLoops = () => { glowTween?.stop(); glowTween = null; };
    const fadeGlow = (to, duration, onComplete) => glow
        ? scene.tweens.add({ targets: glow, outerStrength: to, duration, ease: 'Sine.easeInOut', onComplete })
        : onComplete?.();
    state.stopLoops = stopLoops;
    state.setVisible = setVisible;
    state.fadeGlow = fadeGlow;

    const show = () => {
        state.shown = true;
        state.eyeOpen = false;
        setVisible(true);
        sunset.play(`${key}_shut`);
        zone.setInteractive({ useHandCursor: true });
        scene.tweens.add({ targets: sunset, alpha: 1, duration: 1400, ease: 'Sine.easeInOut' });
        fadeGlow(2, 1400, () => {
            if (state.shown) glowTween = scene.tweens.add({ targets: glow, outerStrength: 0.8, duration: 2200, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        });
    };
    const hide = () => {
        state.shown = false;
        zone.disableInteractive();
        label.setAlpha(0);
        stopLoops();
        voice.setVisible(false);
        fadeGlow(0, 1200);
        scene.tweens.add({ targets: sunset, alpha: 0, duration: 1200, ease: 'Sine.easeInOut',
            onComplete: () => { if (!state.shown) setVisible(false); } });
    };

    // The sun opens as an eye (once per showing), he turns to the puddle, her voice is there for the dialog
    const talk = (dialogKey) => {
        if (!state.eyeOpen) {
            state.eyeOpen = true;
            sunset.play(`${key}_open`);
            sunset.once(Phaser.Animations.Events.ANIMATION_COMPLETE, () => { if (state.shown) sunset.play(`${key}_idle`); });
        }
        const p = scene.priest;
        if (p) {
            const dir = x >= p.x ? 1 : -1;
            p.setScale(dir * Math.abs(p.scaleX || 1), p.scaleY || 1);
            scene.priestGlow?.setScale(dir * Math.abs(scene.priestGlow.scaleX || 1.05), scene.priestGlow.scaleY || 1.05);
        }
        voice.setVisible(true);
        scene.showDialog(dialogKey);
        state.talking = true;
    };

    // He walks up beside the puddle first ("the puddle at your feet"); clicks wait meanwhile (GameScene.isModalOpen)
    const approach = (then) => {
        const p = scene.priest;
        const reach = Math.round(P.w / 2) + 10;
        const standX = x + (p && p.x <= x ? -reach : reach);
        if (!p || Math.abs(p.x - standX) < 24) { then(); return; }
        scene.playerMovementSystem?.stop();
        scene._scriptedWalk = true;
        const k = scene.priestScale || 1, dir = standX > p.x ? 1 : -1;
        p.setScale(dir * k, k);
        scene.priestGlow?.setScale(1.05 * dir * k, 1.05 * k);
        p.play('walk', true);
        scene.tweens.add({
            targets: scene.priestGlow ? [p, scene.priestGlow] : [p],
            x: standX,
            duration: Math.abs(standX - p.x) * 5 / k,
            ease: 'Linear',
            onComplete: () => {
                p.play('idle', true);
                scene._scriptedWalk = false;
                if (scene.sys.isActive()) then();
            }
        });
    };

    // Every 0.4 s: the trip starting or ending here, her first words on a trip, the end of a talk
    scene.time.addEvent({ delay: 400, loop: true, callback: () => {
        if (hasUlvarex(scene)) {
            if (state.shown && !state.merging) hide();
            return;
        }
        const trip = seeingTrip(scene);
        if (trip && !state.shown) show();
        else if (!trip && state.shown && !scene.dialogVisible) hide();

        if (state.talking && !scene.dialogVisible) {
            state.talking = false;
            voice.setVisible(false);
        }
        if (trip && state.shown && !state.talking && scene.registry.get(SEEN_KEY) !== trip.startTime
            && !scene.isInputBlocked?.() && !scene.isTransitioning && !scene.cutscene && sunset.alpha > 0.9) {
            scene.registry.set(SEEN_KEY, trip.startTime);
            // the first meeting once; on a later trip she knows him
            approach(() => talk(metUlvarex(scene) ? 'ulvarex_again' : 'ulvarex_notice'));
        }
    } });
}

/** Bond her (the accept state's onTrigger): the symbiont, its journal entry, a little Growth, her flight into him. */
function bondUlvarex(scene) {
    if (hasUlvarex(scene)) return;
    const data = { name: 'Ulvarex the Borrowed Horizon', power: 0, ability: 'Mirage Weave' };
    if (!scene.symbiontSystem?.addSymbiont(ULVAREX_ID, data)) return;
    scene.modifyGrowthDecay(1, 0);
    if (!scene.hasJournalEntry('symbiont_ulvarex_accepted')) {
        scene.addJournalEntry(
            'symbiont_ulvarex_accepted',
            'Accepted Ulvarex',
            "On an Oltrac trip I found Ulvarex, the Borrowed Horizon. She settled behind my eyes. She feeds on my spores and gives me Mirage Weave: illusions convincing enough to fool the hand as well as the eye. She likes the city alive: should decay take over, she will fall silent.",
            scene.journalSystem.categories.EVENTS,
            { symbiont: ULVAREX_ID }
        );
    }
    scene.addSymbiontIcon?.(ULVAREX_ID, data);
    const L = LanguageSystem.getInstance();
    scene.showNotification(scene.t('notifications.symbiontGained', { name: L.str(`symbionts.${ULVAREX_ID}.name`) || data.name }));

    // the reflection peels off the water and flies into him; the puddle goes back to being a puddle
    const st = scene._ulvarex;
    if (st) {
        st.merging = true;
        st.talking = false;
        st.stopLoops();
        st.voice.setVisible(false);
        const p = scene.priest;
        const wisp = scene.add.ellipse(st.x, st.y, 46, 10, 0xffc070, 0.9).setDepth(21).setBlendMode(Phaser.BlendModes.ADD);
        scene.tweens.add({ targets: wisp, x: p?.x ?? st.x, y: (p?.y ?? st.y) - 10, scaleX: 0.25, scaleY: 2.2, alpha: 0,
            duration: 900, ease: 'Sine.easeIn', onComplete: () => wisp.destroy() });
        st.fadeGlow(0, 900);
        scene.tweens.add({ targets: st.sunset, alpha: 0, duration: 1400, delay: 200,
            onComplete: () => { st.merging = false; st.shown = false; st.zone.disableInteractive(); st.setVisible(false); } });
    }
}

/** The encounter's dialog states (EN; CZ in lang/cs/dialogs/UlvarexEncounter.js). */
export function ulvarexDialog(scene) {
    const bondNext = hasFreeSlot(scene) ? 'ulvarex_accept' : 'ulvarex_no_slot';
    const yes = (text, key) => ({ text, key, next: bondNext });
    return {
        ulvarex_notice: {
            hideCloseOption: true,      // (its own way out is enough: no second "I should go")
            speaker: 'Narrator',
            text: "The Oltrac's wild colours are still flickering before your eyes when you notice that the puddle at your feet doesn't reflect the grey sky but an orange sunset. Where would that come from? There's no sun in the sky. Then it dawns on you: it isn't a sunset at all, but an orange eye, staring straight at you.",
            options: [
                { text: "Bend down to the puddle.", key: 'ulvarex_crouch', next: 'ulvarex_reach' },
                { text: "Step back. It's only the Oltrac.", key: 'ulvarex_step_back', next: 'closeDialog' },
            ],
        },
        ulvarex_reach: {
            speaker: 'Ulvarex',
            text: "The moment you lean over the water, the reflection changes. A voice speaks, right inside your head. \"Oh, finally. Someone who actually sees. Thank whoever gave you the Oltrac: without it you'd have walked straight through me. I've been in this puddle for... well, time moves differently when you're two-dimensional.\"",
            options: [
                { text: "What are you?", key: 'ulvarex_what_are_you', next: 'ulvarex_what' },
                { text: "What are you doing in a puddle?", key: 'ulvarex_why_puddle', next: 'ulvarex_why' },
            ],
            onTrigger: () => {
                if (!scene.hasJournalEntry('met_ulvarex')) {
                    scene.addJournalEntry(
                        'met_ulvarex',
                        'Ulvarex',
                        "On an Oltrac trip I saw a puddle mirroring a sunset instead of the grey sky. In it lives Ulvarex, the Borrowed Horizon, a symbiont pressed into the reflection. I can only see her on Oltrac.",
                        scene.journalSystem.categories.PEOPLE,
                        { symbiont: ULVAREX_ID }
                    );
                }
            },
        },
        ulvarex_what: {
            speaker: 'Ulvarex',
            text: "\"I am Ulvarex, the Borrowed Horizon. A symbiont of perception. I can weave mirages convincing enough to fool the hand as well as the eye. But I need a host. Someone with some suitable organic matter I could nest in. You, for instance. You're soaked with potential like a sponge. Or a mushroom. Hehe.\"",
            options: [
                { text: "What would bonding with you mean?", key: 'ulvarex_what_bond', next: 'ulvarex_bond' },
                { text: "I'm not interested in tricks.", key: 'ulvarex_no_tricks', next: 'ulvarex_decline' },
            ],
        },
        ulvarex_why: {
            speaker: 'Ulvarex',
            text: "\"I hitched a ride on a particularly convincing sunset, rained down with it over this city and ended up here, pressed into a film on the water. Embarrassing, really. For an entity of infinite creative potential, a puddle is a humbling address. And the only ones who can see me at all are people on Oltrac, or particularly sensitive individuals.\"",
            // she hasn't said yet what she is or that she wants a host: ask that first (bonding comes up in ulvarex_what)
            options: [
                { text: "And what are you, exactly?", key: 'ulvarex_what_are_you', next: 'ulvarex_what' },
                { text: "I'll leave you to your puddle.", key: 'ulvarex_leave_puddle', next: 'ulvarex_decline' },
            ],
        },
        ulvarex_bond: {
            speaker: 'Ulvarex',
            text: "\"I'll settle in behind your eyes. I feed on spores, so as long as you have some, you've nothing to fear. In return you get the gift of Mirage Weave: convincing illusions nobody can see through. Well, not straight away, anyway. One more thing you should know. I like it when things live and grow. Use my mirages to protect something living, say, and I'll be glad. A mirage spun out of greed makes me queasy.\"",
            options: [
                yes("Alright. Bond with me.", 'ulvarex_bond_yes'),
                { text: "I need to think about it.", key: 'ulvarex_think', next: 'ulvarex_later' },
            ],
        },
        ulvarex_accept: {
            speaker: 'Ulvarex',
            text: "A thin film of light peels off the puddle, wraps around your hand and crawls up your arm, a warm, weightless, faintly shimmering haze. For a moment the world looks different: every shadow has depth, every surface a texture you've never noticed. \"There. I'm behind your eyes now. Try not to blink too hard, it tickles.\"",
            hideCloseOption: true,
            options: [
                { text: "Welcome aboard, Ulvarex.", key: 'ulvarex_welcome', next: 'closeDialog' },
            ],
            onTrigger: () => bondUlvarex(scene),
        },
        ulvarex_no_slot: {
            hideCloseOption: true,      // (its own way out is enough: no second "I should go")
            speaker: 'Ulvarex',
            text: "The glow in the puddle dims. \"Oh. You're already occupied. Every corner of you has a tenant.\" She sizes you up like someone viewing a flat that's already let. \"The Registration office in Shed 521 sells extra room, I hear. Get yourself one more slot, take another trip, and look down. I'll probably be in some puddle or other.\"",
            options: [
                { text: "I'll be back.", key: 'ulvarex_be_back', next: 'closeDialog' },
            ],
        },
        ulvarex_decline: {
            hideCloseOption: true,      // (its own way out is enough: no second "I should go")
            speaker: 'Ulvarex',
            text: "\"Suit yourself. I'll be here. Or in some other puddle, contemplating the nature of existence and self-reflection. If you change your mind, take another trip and look down.\"",
            options: [
                { text: "Leave.", key: 'ulvarex_leave', next: 'closeDialog' },
            ],
        },
        ulvarex_later: {
            hideCloseOption: true,      // (its own way out is enough: no second "I should go")
            speaker: 'Ulvarex',
            text: "\"Take your time. I've been drifting from puddle to puddle for a few hundred digestions; I'll survive a few more. Just remember: without the Oltrac you probably won't even see me.\"",
            options: [
                { text: "Leave.", key: 'ulvarex_leave', next: 'closeDialog' },
            ],
        },
        ulvarex_reconsider: {
            hideCloseOption: true,      // (its own way out is enough: no second "I should go")
            speaker: 'Narrator',
            text: "The sunset glow in the puddle is still burning. Ulvarex watches you.",
            options: [
                yes("Alright, bond with me.", 'ulvarex_reconsider_yes'),
                // (the talk may have ended before she ever offered it)
                { text: "What would bonding with you mean?", key: 'ulvarex_what_bond', next: 'ulvarex_bond' },
                { text: "Not yet.", key: 'ulvarex_not_yet', next: 'closeDialog' },
            ],
        },
        // a later trip: they have met, so no first look and no introductions
        ulvarex_again: {
            hideCloseOption: true,      // (its own way out is enough: no second "I should go")
            speaker: 'Ulvarex',
            text: "The puddle at your feet glows with an orange sunset again, and the sun in it opens into an eye. \"Oh, it's you. So, have you thought it over?\"",
            options: [
                yes("Alright, bond with me.", 'ulvarex_reconsider_yes'),
                { text: "Remind me what bonding with you would mean.", key: 'ulvarex_remind_bond', next: 'ulvarex_bond' },
                { text: "Not yet.", key: 'ulvarex_not_yet', next: 'closeDialog' },
            ],
        },
    };
}
