// The cuts: which part of each captured shot plays when, the camera move applied in post, and the titles.
// Times are trailer seconds. Music cues in upper-morkezela.mp3 (measured): quiet intro, the band kicks in at
// 18.29 s, last hit before the break at 73.78 s, back in at 77.84 s; the pulse is ≈0.857 s (70 BPM).
//
//   story    — opens on Agarida and the Council in the quiet intro, the band comes in on the city (≈75 s)
//   gameplay — "10 tips for visiting Upper Morkezela": cards + cursor-driven play, to Dr. Elphi's Lab (≈108 s)

export const FPS = 60;
export const FADE_OUT = 1.2; // to black at the very end

const MUSIC_FILE = 'assets/sounds/upper-morkezela.mp3';
const CUE = { kick: 18.29, drop: 73.78, back: 77.84 };

const B = 0.857;          // one beat
const H = 2 * B;          // half bar — quick cuts
const U = 4 * B;          // one bar — the standard shot

// Camera moves in game coordinates (1067×600 view): [zoom, centreX, centreY] at the start and the end of the cut.
const still = [[1, 533.5, 300], [1, 533.5, 300]];
// Push in towards (cx, cy); the view is clamped to the picture, so at low zoom it stays near the centre.
const push = (cx, cy, z0 = 1, z1 = 1.12) => [[z0, cx, cy], [z1, cx, cy]];

/** From the band's entrance (KICK) to the last hit (DROP): the city, the world, Shed 521, G/D, the people. */
function montage(KICK, DROP, cityFadeIn) {
    let t = KICK;
    const next = (len, seg) => { const s = { ...seg, at: t }; t += len; return s; };
    return [
        next(U, { shot: 'city', in: 0.2, move: push(560, 250, 1, 1.1), ...(cityFadeIn ? { fadeIn: cityFadeIn } : {}) }),
        next(U, { shot: 'crossroad', in: 0.4, move: push(400, 300, 1.02, 1.2) }),
        next(U, { shot: 'cathedral', in: 0.3, move: push(534, 330, 1.02, 1.16) }),
        next(U, { shot: 'bears', in: 0.3, move: push(534, 270, 1, 1.14) }),
        next(H, { card: 'gods' }),
        next(H, { card: 'paperwork' }),
        next(H, { shot: 'gate', in: 0.3, move: [[1.18, 440, 300], [1.18, 630, 300]] }),
        next(H, { shot: 'registration', in: 0.3, move: push(534, 240, 1.06, 1.18) }),
        next(H, { shot: 'floors', in: 0.3, move: [[1.35, 533.5, 400], [1.35, 533.5, 215]] }),
        next(U, { shot: 'ortolan', in: 0.6, move: still }),
        next(H, { shot: 'shedGrowth', in: 0.3, move: push(400, 330, 1, 1.06) }),
        next(H, { shot: 'shedDecay', in: 0.3, move: push(400, 330, 1.06, 1.12) }),
        next(U, { shot: 'office', in: 0.3, move: push(800, 240, 1, 1.22) }),
        next(H, { shot: 'scraper', in: 0.3, move: [[1.3, 533.5, 420], [1.3, 533.5, 250]] }),
        next(U, { shot: 'liftmother', in: 0.4, move: push(480, 330, 1, 1.12) }),
        next(H, { shot: 'voxmarket', in: 0.3, move: push(534, 320, 1, 1.12) }),
        next(H, { shot: 'zerren', in: 0.3, move: push(260, 380, 1.1, 1.18) }),
        next(H, { shot: 'skyship', in: 0.3, move: push(560, 420, 1.05, 1.15) }),
        next(H, { shot: 'edgar', in: 0.3, move: push(320, 420, 1.08, 1.2) }),
        next(U, { shot: 'feral', in: 0.4, move: push(534, 360, 1.02, 1.2) }),
        next(U, { shot: 'elphi', in: 0.3, move: push(650, 400, 1, 1.12) }),
        next(B, { shot: 'hall', in: 0.3, move: push(620, 350, 1.1, 1.18) }),
        next(B, { shot: 'applications', in: 0.3, move: push(534, 330, 1.1, 1.18) }),
        next(B, { shot: 'auction', in: 0.3, move: push(534, 330, 1.1, 1.18) }),
        next(DROP - t, { shot: 'courtyard', in: 0.3, move: push(300, 300, 1.1, 1.2) }),
    ];
}

function makeCut({ musicStart, intro, file, musicFadeIn }) {
    const KICK = CUE.kick - musicStart;
    const DROP = CUE.drop - musicStart;   // the title on the last hit before the break
    const BACK = CUE.back - musicStart;   // the end card when the band returns
    const END = BACK + 4.0;
    const SEGMENTS = [
        ...(intro ? [
            { at: 0, shot: 'agarida', in: 1.4, move: still, fadeIn: 1.0 },
            { at: 4.6, shot: 'council', in: 0.9, move: still, dissolve: 0.5 },
        ] : []),
        ...montage(KICK, DROP, intro ? 0 : 0.15),
        { at: DROP, card: 'logo' },
        { at: BACK, card: 'cta' },
    ];
    // Text over the picture; cards carry their own title for their whole length.
    const TITLES = [
        ...(intro ? [{ id: 'agarida', from: 0.7, to: 4.2 }] : []),
        { id: 'city', from: KICK + 0.35, to: KICK + U - 0.2 },
        { id: 'grow', seg: 'shedGrowth' },
        { id: 'decay', seg: 'shedDecay' },
    ];
    return { MUSIC: { file: MUSIC_FILE, start: musicStart, fadeIn: musicFadeIn, fadeOut: 2.0 }, SEGMENTS, TITLES, END, file };
}

/**
 * "10 tips for visiting Upper Morkezela" — the idea of the 2025 YouTube trailer, now on the redrawn game: every tip
 * is a card and a few seconds of real play driven by the cursor (shots g_*). Music: Dr. Elphi's Lab (dr_elphi.mp3,
 * 120 BPM): the intro sits in its quiet dip, the band comes in at 21.175 s on tip 1, and the logo lands on the
 * breakdown at 117.175 s (the music start is derived from where DROP falls).
 */
function makeTipsCut() {
    let t = 0;
    const seq = [];
    const add = (len, seg) => { seq.push({ ...seg, at: t }); t += len; };
    // one-line cards get a bar; two-line cards stay up longer so they can be read
    const tip = (n, cardLen, shots) => { add(cardLen, { card: `tip${n}` }); shots.forEach(([len, seg]) => add(len, seg)); };
    const ui = still;                                   // no camera move while the UI is being read

    add(4, { shot: 'city', in: 0.2, move: push(560, 250, 1, 1.1), fadeIn: 0.5 });
    add(4, { shot: 'bears', in: 0.3, move: push(534, 270, 1, 1.14) });
    // T 8: the band comes in on tip 1
    // dialog shots open on ~1 s of the location before the first click
    tip(1, 2, [[3.5, { shot: 'g_gnur', in: 0.25, move: ui }], [2.5, { shot: 'ortolan', in: 0.6, move: ui }]]);
    tip(2, 3, [[7, { shot: 'g_kloor', in: 0.6, move: ui }]]);
    tip(3, 3.5, [[6, { shot: 'g_oltrac', in: 1.4, move: ui }]]);
    tip(4, 3, [[5, { shot: 'g_journal', in: 0.4, move: ui }]]);
    tip(5, 2, [[1.75, { shot: 'cathedral', in: 0.5, move: push(534, 330, 1.02, 1.12) }],
        [1.75, { shot: 'scraper', in: 0.3, move: [[1.3, 533.5, 420], [1.3, 533.5, 280]] }],
        [1.5, { shot: 'voxmarket', in: 0.3, move: push(534, 320, 1, 1.1) }]]);
    tip(6, 3, [[7, { shot: 'g_corpse', in: 0.4, move: ui }]]);
    tip(7, 3, [[6, { shot: 'g_brainrot', in: 0.4, move: ui }]]);
    tip(8, 2, [[2, { shot: 'zerren', in: 0.3, move: push(260, 380, 1.08, 1.14) }],
        [2, { shot: 'liftmother', in: 1.0, move: push(480, 330, 1.04, 1.1) }]]);
    // plant the spores, the tree grows, click it — then straight onto the deck (no look-up picture)
    tip(9, 3.5, [[5, { shot: 'g_spores', in: 0.4, move: ui }],
        [4, { shot: 'skyship', in: 0.3, move: push(560, 420, 1.02, 1.12) }]]);
    tip(10, 2, [[5, { shot: 'g_edgar', in: 0.15, move: ui }]]);
    add(3, { card: 'bonus' });
    add(1.5, { shot: 'shedGrowth', in: 0.3, move: push(400, 330, 1, 1.06) });
    add(1.5, { shot: 'shedDecay', in: 0.3, move: push(400, 330, 1.06, 1.12) });
    add(1.5, { shot: 'feral', in: 0.4, move: push(534, 360, 1.05, 1.18) });
    add(1.5, { shot: 'office', in: 0.3, move: push(800, 240, 1.05, 1.2) });
    const DROP = t;                                      // 104: lands on the breakdown at 117.175 s in the track
    add(4, { card: 'logo' });
    add(5, { card: 'cta' });
    add(3.5, { card: 'joke' });
    return {
        MUSIC: { file: 'assets/sounds/dr_elphi.mp3', start: 117.175 - DROP, fadeIn: 0.5, fadeOut: 2.0 },
        SEGMENTS: seq,
        TITLES: [{ id: 'dream', from: 0.3, to: 3.8 }, { id: 'tips_title', from: 4.3, to: 7.8 }],
        END: t,
        DROP,
        file: 'upper-morkezela-demo-trailer-gameplay.mp4',
    };
}

/**
 * The demo announcement cut (≈71.3 s): an invitation to the city, only what the demo holds (no spoilers). Two pieces,
 * one transition: "Flop" (Ortolan's courtyard beat, 110 BPM, a bar = 24/11 s, an 11-bar loop) under the announcement,
 * the premise (in titles over the demo's places: the call, the city, Master Thaal and his apprentice) and the city; then the entry theme (the demo's entry-theme.mp3 = infinite_fold.mp3 here;
 * 100 BPM, a bar = 2.4 s, downbeats at 4.965 + 2.4k s) comes in on a downbeat of its fuller part with the things to do
 * and carries the finale, the logo and the end card. Every cut sits on a beat of the piece playing under it.
 */
function makeAnnounceCut(cta, file) {
    const FB = 24 / 11;                      // a bar of Flop (from trailer 0)
    const EB = 2.4;                          // a bar of the entry theme
    const E_IN = 25.365;                     // the entry theme comes in on beat 3 of a bar: its accents in this part fall there, so the logo and the end card land on them
    const T2 = 14 * FB;                      // the transition: the things to do
    const SEGMENTS = [];
    let t = 0;
    const put = (len, seg) => { SEGMENTS.push({ ...seg, at: t }); t += len; };
    // the premise in titles over the demo's own places (no intro footage): the call, the city, who answers it
    put(1.5 * FB, { card: 'announce' });
    put(2 * FB, { shot: 'office', in: 0.3, move: push(800, 240, 1, 1.14), fadeIn: 0.4 });
    put(2 * FB, { shot: 'bears', in: 0.3, move: push(534, 270, 1, 1.12) });
    put(2.5 * FB, { shot: 'city', in: 0.2, move: push(560, 250, 1, 1.1) });
    put(1.5 * FB, { shot: 'crossroad', in: 0.4, move: push(400, 300, 1.02, 1.14) });
    put(1.5 * FB, { shot: 'cathedral', in: 0.3, move: push(534, 330, 1.02, 1.16) });
    put(FB, { shot: 'scraper', in: 0.3, move: [[1.3, 533.5, 420], [1.3, 533.5, 280]] });
    put(2 * FB, { shot: 'voxmarket', in: 0.3, move: push(534, 320, 1, 1.12) });
    // the things to do: a bar and a half each on the entry theme, the band two bars
    [['registration', 0.3, push(534, 240, 1.04, 1.14)], ['courtyard', 0.3, push(320, 300, 1.06, 1.16)],
        ['gnur', 0.3, push(420, 420, 1.1, 1.2)], ['liftmother', 0.4, push(480, 330, 1, 1.1)],
        ['zerren', 0.3, push(260, 380, 1.08, 1.16)], ['edgar', 0.3, push(320, 420, 1.06, 1.16)]]
        .forEach(([shot, inp, move]) => put(1.5 * EB, { shot, in: inp, move }));
    put(2 * EB, { shot: 'feral', in: 0.4, move: push(534, 360, 1.02, 1.16) });
    put(EB, { shot: 'shedGrowth', in: 0.3, move: push(400, 330, 1, 1.06) });
    put(EB, { shot: 'shedDecay', in: 0.3, move: push(400, 330, 1.06, 1.14) });
    put(2 * EB, { card: 'logo' });
    put(2 * EB, { card: cta });
    const END = t;
    const TITLES = [
        { id: 'premise1', seg: 'office' },
        { id: 'premise2', seg: 'bears' },
        { id: 'premise3', seg: 'city' },
        { id: 'trace', seg: 'cathedral' },
        { id: 'explore', seg: 'voxmarket' },
        ...['registration', 'courtyard', 'gnur', 'liftmother', 'zerren', 'edgar', 'feral'].map((seg, i) => ({ id: `do${i + 1}`, seg })),
        { id: 'grow2', seg: 'shedGrowth' },
        { id: 'rot', seg: 'shedDecay' },
    ];
    // the transition: no overlap. Flop fades out under the Voxmarket shot (2.4 s), half a second of silence before the cut,
    // then the entry theme rises from silence with the things to do (1.5 s, an S-curve)
    const OUT = 2.4, GAP = 0.5;
    const MUSIC = [
        { file: 'assets/sounds/flop.opus', from: 0, at: 0, dur: T2 - GAP, loop: 1, fadeIn: 0.02, fadeOut: OUT, fadeOutCurve: 'qsin', gain: 2.0 },
        { file: 'assets/sounds/infinite_fold.mp3', from: E_IN, at: T2, dur: END - T2, fadeIn: 1.5, fadeInCurve: 'hsin', fadeOut: 2.0, gain: -3.3 },
    ];   // Flop at −14, the entry theme at −14 LUFS (measured −16.1 / −10.8); a limiter at −1 dBFS on the mix
    return { MUSIC, SEGMENTS, TITLES, END, file };
}

/**
 * The field notes cut (≈66.6 s): the apprentice's diary, one dry line per place (only what the demo holds, no spoilers),
 * on other places than the announcement. Two pieces, both recorded by people: "Loop" (the Shed 521 guitar) under the
 * diary, every cut on one of its strong attacks (tools/trailer/onsets.py); then, in the tavern, "Finally, some peace and
 * quiet": the guitar fades out, a moment of silence, and the Feral Toast rehearsal bursts through the wall
 * (tavern-rehearsal.mp3); the logo and the end card land on the band's hits.
 */
function makeNotesCut(cta, file) {
    const LOOP = [3.895, 7.74, 12.02, 14.115, 17.725, 21.555, 26.155, 30.345, 35.235, 38.855, 42.49, 49.64, 53.955];   // Loop's accents = trailer time
    const BURST = 57.2;                      // the band's first hit (tavern-rehearsal.mp3 at 1.655 s)
    const band = (tau) => BURST + tau - 1.655;
    const LOGO = band(4.025), CTA = band(9.15), END = band(12.705) + 0.9;
    const shots = [
        ['thaal', 0.2, push(560, 400, 1.06, 1.16)], ['sentinel', 0.3, push(534, 380, 1.04, 1.16)],
        ['gate', 0.3, push(534, 320, 1.04, 1.1)], ['floors', 0.3, push(534, 330, 1.02, 1.12)],
        ['applications', 0.3, push(534, 330, 1.04, 1.14)], ['kloor', 0.4, push(600, 380, 1.04, 1.14)],
        ['g_oltrac', 4.2, still], ['auction', 0.3, push(620, 330, 1.02, 1.14)],
        ['corkin', 0.3, push(520, 360, 1.02, 1.1)], ['skyship', 0.3, push(560, 420, 1.04, 1.14)],
        ['g_corpse', 0.6, still], ['g_edgar', 1.0, still],
        ['corkin', 4.2, push(560, 340, 1.0, 1.06)],
    ];
    const SEGMENTS = [
        { at: 0, card: 'notes_title' },
        ...shots.map(([shot, inp, move], i) => ({ at: LOOP[i], shot, in: inp, move })),
        { at: BURST, shot: 'corkin', in: 7.45, move: push(990, 350, 1.55, 1.62) },   // the jolt: tight on the club door
        { at: LOGO, card: 'logo' },
        { at: CTA, card: cta },
    ];
    const seg = (i) => [LOOP[i], i + 1 < LOOP.length ? LOOP[i + 1] : BURST];
    const over = (id, i, a = 0.3, b = 0.25) => { const [s0, s1] = seg(i); return { id, from: s0 + a, to: s1 - b }; };
    const TITLES = [
        over('n_thaal', 0), over('n_guard', 1), over('n_queue', 3), over('n_form', 4), over('n_kloor', 5), over('n_oltrac', 6),
        over('n_twins', 7), over('n_barman', 8), over('n_sky', 9),
        { id: 'n_corpse', from: LOOP[10] + 0.3, to: LOOP[10] + 3.7 }, { id: 'n_roommate', from: LOOP[10] + 4.4, to: LOOP[11] - 0.25 },
        over('n_bear', 11), over('n_quiet', 12, 0.4, 0.1),
        { id: 'n_band', from: BURST + 0.15, to: LOGO - 0.2 },
    ];
    const MUSIC = [
        { file: 'assets/sounds/guitar-loop.ogg', from: 0, at: 0, dur: 56.6, fadeIn: 0.02, fadeOut: 2.1, fadeOutCurve: 'qsin', gain: -0.4 },
        { file: 'assets/sounds/tavern-rehearsal.mp3', from: 1.5, at: BURST - 0.155, dur: END - BURST + 0.155, fadeIn: 0.02, fadeOut: 2.0, gain: 7.4 },
    ];   // Loop at −15 LUFS, the band through the wall at −13 (measured −14.6 / −20.4: the punchline is louder)
    return { MUSIC, SEGMENTS, TITLES, END, file };
}

export const CUTS = {
    announce: makeAnnounceCut('cta_nov_dec', 'upper-morkezela-demo-announcement.mp4'),
    announce_late_nov: makeAnnounceCut('cta_late_nov', 'upper-morkezela-demo-announcement-late-nov.mp4'),
    notes: makeNotesCut('cta_nov_dec', 'upper-morkezela-demo-field-notes.mp4'),
    notes_late_nov: makeNotesCut('cta_late_nov', 'upper-morkezela-demo-field-notes-late-nov.mp4'),
    story: makeCut({ musicStart: 6.27, intro: true, musicFadeIn: 0.3, file: 'upper-morkezela-demo-trailer.mp4' }),
    gameplay: makeTipsCut(),
};
