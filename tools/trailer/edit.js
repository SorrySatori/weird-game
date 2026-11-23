// The cuts: which part of each captured shot plays when, the camera move applied in post, and the titles.
// Times are trailer seconds. Music cues in upper-morkezela.mp3 (measured): quiet intro, the band kicks in at
// 18.29 s, last hit before the break at 73.78 s, back in at 77.84 s; the pulse is ≈0.857 s (70 BPM).
//
//   story    — opens on Agarida and the Council in the quiet intro, the band comes in on the city (≈75 s)
//   gameplay — "10 tips for visiting Upper Morkezela": cards + cursor-driven play, to Dr. Elphi's Lab (≈108 s)
//   noir, noir_cs — the release trailer: the apprentice tells the case like a noir detective, captions in English / Czech

import fs from 'node:fs';

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
 * The noir release cut (≈2 min): the apprentice tells the case like a tired noir detective, one dry joke per place, in
 * captions (noir.json; the shots nr_* have no speech bubbles, so one capture serves both languages). Each caption stays
 * up as long as its longer language needs, the punchline comes after a beat, and every cut sits on an attack of the
 * guitar. Music, all recorded by people: "Les" (guitar) under the case; it fades out in the quiet tavern ("The God of
 * Noise came here to die."), the Feral Toast rehearsal bursts in on the band's punchline and stops dead on the next cut;
 * after a moment of silence "Les" comes back on its last part, so the logo and the end card land on its final accents.
 */
const NOIR = JSON.parse(fs.readFileSync(new URL('./noir.json', import.meta.url), 'utf8'));
// strong attacks in guitar-les.mp3 (python3 tools/trailer/onsets.py assets/sounds/guitar-les.mp3 0 146, strength ≥ 0.6)
const LES_ONSETS = [0.435,0.860,1.295,2.320,2.500,2.910,3.295,3.715,4.100,5.770,6.195,6.455,6.600,6.995,7.415,9.820,10.180,10.595,10.745,10.865,10.900,12.240,12.650,13.045,13.450,13.860,15.880,16.275,16.680,17.105,18.705,19.515,19.925,20.320,21.545,21.950,22.345,22.765,23.170,23.590,25.655,26.055,26.470,26.890,28.940,29.325,29.715,30.140,31.190,31.360,31.410,31.750,32.565,32.970,33.390,35.035,35.840,36.230,36.640,38.690,39.090,39.910,41.110,41.525,41.935,42.705,43.080,43.475,43.875,45.095,45.905,46.320,47.115,47.520,47.570,48.330,49.155,49.560,50.800,52.060,52.445,52.870,53.290,54.745,58.310,58.720,59.135,59.560,61.965,62.370,64.395,64.800,65.240,65.640,66.460,68.895,71.725,72.530,72.925,73.325,78.575,79.000,81.870,83.875,85.485,86.105,86.675,87.095,87.915,87.980,89.930,90.345,90.750,92.215,92.450,92.835,93.695,95.310,96.130,97.365,98.585,100.630,101.050,101.885,103.905,104.110,104.330,104.445,104.705,110.805,111.220,113.930,113.990,114.225,115.265,116.910,120.450,121.245,122.515,122.930,123.355,123.755,125.405,125.835,126.230,126.655,128.685,129.105,129.515,129.930,132.255,132.350,132.390,132.785,133.205,134.470,135.690,136.105,136.525,138.155,138.560,138.950,139.370,139.800,141.835,144.650];

function makeNoirCut(lang, file) {
    const CPS = 16, PAD = 0.55, MIN = 1.7;                  // reading speed, the eye's start-up, the shortest caption
    const LEAD = 0.35, GAP = 0.25, BEAT = 0.45, TAIL = 0.35;
    const capLen = (id) => { const c = NOIR.captions[id]; return Math.max(MIN, Math.max(c.en.length, c.cs.length) / CPS + PAD); };
    // shot, in-point, camera move, captions; `beat`: a pause before the last caption (the punchline); lead / tail override
    const A = [
        // the city first, the camera easing back from its skyline as the apprentice walks up to the Master
        { shot: 'nr_city', in: 0.3, move: [[1.35, 560, 225], [1.0, 533.5, 300]], fadeIn: 1.0, caps: ['1a', '1b'], beat: true, lead: 1.2 },
        { shot: 'nr_thaal', in: 0.3, move: push(545, 430, 1.4, 1.52), caps: ['2a', '2b', '2c'] },
        { shot: 'nr_sentinel', in: 0.3, move: push(534, 380, 1.02, 1.12), caps: ['3a', '3b', '3c'], beat: true },
        { shot: 'nr_queue', in: 0.3, move: push(534, 300, 1.02, 1.1), caps: ['4a', '4b'], beat: true },
        { shot: 'nr_ortolan', in: 0.3, move: push(510, 400, 1.04, 1.16), caps: ['5a', '5b'], beat: true },
        { shot: 'nr_gnur', in: 0.3, move: push(420, 420, 1.06, 1.18), caps: ['6a', '6b'], beat: true },
        { shot: 'nr_kloor', in: 0.4, move: push(600, 380, 1.04, 1.14), caps: ['7a'] },
        { shot: 'nr_oltrac', in: 0.1, move: still, caps: ['7b', '7c'], beat: true, lead: 0.6 },
        { shot: 'nr_zerren', in: 0.3, move: push(300, 380, 1.04, 1.14), caps: ['8a', '8b'] },
        { shot: 'nr_bears', in: 0.3, move: push(534, 270, 1, 1.12), caps: ['9'] },
        { shot: 'nr_edgar', in: 0.3, move: push(320, 420, 1.06, 1.16), caps: ['10a', '10b'], beat: true },
        { shot: 'nr_corkin', in: 0.3, move: push(520, 360, 1.02, 1.08), caps: ['11a'], tail: 0.9 },   // the quiet
    ];
    const C = [
        { shot: 'nr_lift', in: 0.3, move: push(480, 330, 1, 1.1), caps: ['12a', '12b'], beat: true, lead: 0.5 },
        { shot: 'nr_corpse', in: 0.3, move: push(330, 380, 1.02, 1.14), caps: ['13a', '13b'] },
        { shot: 'nr_growth', in: 0.3, move: push(400, 330, 1, 1.06), caps: ['14a'], tail: 0.2 },
        { shot: 'nr_decay', in: 0.3, move: push(400, 330, 1.06, 1.12), caps: ['14b'], lead: 0.2 },
        { shot: 'nr_sky', in: 0.3, move: push(560, 420, 1.02, 1.12), caps: ['15a', '15b', '15c'], beat: true, tail: 0.6 },
    ];
    const length = (seg) => (seg.lead ?? LEAD) + seg.caps.reduce((n, id, i) => n + capLen(id) + (i ? (seg.beat && i === seg.caps.length - 1 ? BEAT : GAP) : 0), 0) + (seg.tail ?? TAIL);
    // a cut onto the nearest attack within reach (track time = trailer time + offset)
    const snap = (t, offset) => {
        const near = LES_ONSETS.map(o => o - offset).filter(o => Math.abs(o - t) <= 0.4).sort((a, b) => Math.abs(a - t) - Math.abs(b - t));
        return near.length ? near[0] : t;
    };
    const SEGMENTS = [], TITLES = [];
    const lay = (list, t0, offset) => {
        const ends = [];
        let t = t0;
        for (const seg of list) { t += length(seg); ends.push(t); }
        const last = ends.pop();
        const cuts = [t0, ...ends.map(e => snap(e, offset)), last];
        list.forEach((seg, k) => {
            const { caps, beat, lead, tail, ...shot } = seg;
            SEGMENTS.push({ ...shot, at: cuts[k] });
            let c = cuts[k] + (lead ?? LEAD);
            caps.forEach((id, i) => {
                if (i) c += beat && i === caps.length - 1 ? BEAT : GAP;
                const to = Math.min(c + capLen(id), cuts[k + 1] - 0.1);
                TITLES.push({ id: `nr_${lang}_${id}`, from: c, to });
                c += capLen(id);
            });
        });
        return last;
    };
    // Part A: "Les" from its start under the case
    const BURST = lay(A, 0, 0);
    // the band: tavern-rehearsal.mp3's first hit (1.655 s) on the cut, its punchline caption, a dead stop on its hit at 6.245 s
    const STOP = BURST + 6.245 - 1.655;
    SEGMENTS.push({ shot: 'nr_feral', in: 0.4, move: push(534, 360, 1.02, 1.16), at: BURST });
    TITLES.push({ id: `nr_${lang}_11b`, from: BURST + 0.15, to: STOP - 0.1 });
    // Part C: a moment of silence, then "Les" again, timed so the logo lands on its accent at 129.93 s and the end card on 133.205 s
    const RESUME = STOP + 0.9;
    const lenC = C.reduce((n, seg) => n + length(seg), 0);
    const LOGO = STOP + lenC, fromC = 129.93 - (LOGO - RESUME);
    lay(C, STOP, fromC - RESUME);
    const CTA = LOGO + (133.205 - 129.93), END = CTA + 5.5;
    SEGMENTS.push({ card: 'nr_logo', at: LOGO }, { card: `nr_${lang}_cta`, at: CTA });
    const MUSIC = [
        { file: 'assets/sounds/guitar-les.mp3', from: 0, at: 0, dur: BURST - 0.6, fadeIn: 0.02, fadeOut: 2.6, fadeOutCurve: 'qsin', gain: -0.2 },
        { file: 'assets/sounds/tavern-rehearsal.mp3', from: 1.5, at: BURST - 0.155, dur: STOP - BURST + 0.155, fadeIn: 0.02, fadeOut: 0.04, gain: 9.5 },
        { file: 'assets/sounds/guitar-les.mp3', from: fromC, at: RESUME, dur: END - RESUME, fadeIn: 1.2, fadeInCurve: 'hsin', fadeOut: 2.5, gain: -0.2 },
    ];   // "Les" at −15 LUFS, the band at −11.5 (measured −14.8 / −21.0: the punchline is louder)
    return { MUSIC, SEGMENTS, TITLES, END, file };
}

export const CUTS = {
    noir: makeNoirCut('en', 'upper-morkezela-demo-noir.mp4'),
    noir_cs: makeNoirCut('cs', 'upper-morkezela-demo-noir-czech.mp4'),
    story: makeCut({ musicStart: 6.27, intro: true, musicFadeIn: 0.3, file: 'upper-morkezela-demo-trailer.mp4' }),
    gameplay: makeTipsCut(),
};
