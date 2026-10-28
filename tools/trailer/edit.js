// The cuts: which part of each captured shot plays when, the camera move applied in post, and the titles.
// Times are trailer seconds. Music cues in upper-morkezela.mp3 (measured): quiet intro, the band kicks in at
// 18.29 s, last hit before the break at 73.78 s, back in at 77.84 s; the pulse is ≈0.857 s (70 BPM).
//
//   story    — opens on the Hymnar and the Council in the quiet intro, the band comes in on the city (≈75 s)
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
            { at: 0, shot: 'hymnar', in: 1.4, move: still, fadeIn: 1.0 },
            { at: 4.6, shot: 'council', in: 0.9, move: still, dissolve: 0.5 },
        ] : []),
        ...montage(KICK, DROP, intro ? 0 : 0.15),
        { at: DROP, card: 'logo' },
        { at: BACK, card: 'cta' },
    ];
    // Text over the picture; cards carry their own title for their whole length.
    const TITLES = [
        ...(intro ? [{ id: 'hymnar', from: 0.7, to: 4.2 }] : []),
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

export const CUTS = {
    story: makeCut({ musicStart: 6.27, intro: true, musicFadeIn: 0.3, file: 'upper-morkezela-demo-trailer.mp4' }),
    gameplay: makeTipsCut(),
};
