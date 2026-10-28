// Cuts the captured shots (out/shots/*.mkv) and the titles (out/titles/*.png) into the trailer with the music.
//
//   node tools/trailer/build.mjs [--cut story|gameplay] [--preview]   → out/<cut file>.mp4 (1080p60) or out/preview-<cut>.mp4
//
// Pixel art is upscaled 4× nearest-neighbour first, so the post camera moves (zoompan) glide over crisp pixels.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FPS, FADE_OUT, CUTS } from './edit.js';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '../..');
const OUT = path.join(HERE, 'out');
const preview = process.argv.includes('--preview');
const cutArg = process.argv.indexOf('--cut');
const cutName = cutArg >= 0 ? process.argv[cutArg + 1] : 'story';
if (!CUTS[cutName]) throw new Error(`unknown cut "${cutName}" — one of ${Object.keys(CUTS).join(', ')}`);
const { MUSIC, SEGMENTS, TITLES, END, file: cutFile } = CUTS[cutName];

const GW = 1067, GH = 600;                 // game view
const UP = preview ? 2 : 4;                // nearest-neighbour pre-scale
const [OW, OH] = preview ? [960, 540] : [1920, 1080];
const fr = (s) => Math.round(s * FPS);
const fx = (n) => n.toFixed(4);

const inputs = [];
const addInput = (...args) => { inputs.push(...args); return inputs.filter(a => a === '-i').length - 1; };
const graph = [];

// ---- picture segments ----
const segs = SEGMENTS.map((s, i) => ({ ...s, end: i + 1 < SEGMENTS.length ? SEGMENTS[i + 1].at : END }));

// Titles are overlaid inside the segment they belong to, on its local clock. (Overlaying them on the finished
// timeline made ffmpeg queue every still until its turn came: gigabytes of 1080p RGBA frames, then swapping.)
const titleList = [
    ...TITLES.map(t => {
        if (!t.seg) return t;
        const s = segs.find(x => x.shot === t.seg);
        return { ...t, from: s.at, to: s.end };
    }),
    ...segs.filter(s => s.card).map(s => ({ id: s.card, from: s.at, to: s.end, card: true })),
];
function overlayTitles(chain, s, segLabel, pre) {
    const mine = titleList.filter(t => t.from >= s.at - 1e-6 && t.to <= s.end + 1e-6);
    let cur = chain;
    for (const [k, t] of mine.entries()) {
        const file = path.join(OUT, 'titles', `${t.id}.png`);
        if (!fs.existsSync(file)) throw new Error(`missing title ${file} — run tools/trailer/titles.py`);
        const len = t.to - t.from, start = t.from - s.at + pre / FPS;
        const idx = addInput('-loop', '1', '-framerate', String(FPS), '-t', fx(len), '-i', file);
        const fin = t.card ? 0.25 : 0.4, fout = t.card ? 0.2 : 0.4;
        const fadeOut = t.to >= END - 0.01 ? '' : `,fade=t=out:st=${fx(len - fout)}:d=${fout}:alpha=1`;
        graph.push(`[${idx}:v]scale=${OW}:${OH},format=rgba,fade=t=in:st=0:d=${fin}:alpha=1${fadeOut},setpts=PTS+${fx(start)}/TB[${segLabel}t${k}]`);
        graph.push(`[${cur}][${segLabel}t${k}]overlay=eof_action=pass:format=auto[${segLabel}o${k}]`);
        cur = `${segLabel}o${k}`;
    }
    return cur;
}
const stray = titleList.filter(t => !segs.some(s => t.from >= s.at - 1e-6 && t.to <= s.end + 1e-6));
if (stray.length) throw new Error(`titles must sit inside one segment: ${stray.map(t => t.id).join(', ')}`);

const labels = [];
for (const [i, s] of segs.entries()) {
    const n = fr(s.end) - fr(s.at);
    const pre = s.dissolve ? fr(s.dissolve) : 0;
    const label = `s${i}`;
    if (s.card) {
        graph.push(`color=c=black:s=${OW}x${OH}:r=${FPS},trim=end_frame=${n},setsar=1,format=yuv444p[${label}b]`);
    } else {
        const file = path.join(OUT, 'shots', `${s.shot}.mkv`);
        if (!fs.existsSync(file)) throw new Error(`missing capture ${file} — run tools/trailer/capture.sh`);
        const idx = addInput('-i', file);
        const a = fr(s.in) - pre, frames = n + pre;
        if (a < 0) throw new Error(`${s.shot}: in-point too early for its dissolve`);
        // a short capture would silently shorten the segment and slide every later cut off the music
        const have = fr(Number(spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', file]).stdout));
        if (a + frames > have) throw new Error(`${s.shot}: needs ${a + frames} frames from in-point ${s.in}s, capture has ${have} — lengthen it in shots.js`);
        const [[z0, cx0, cy0], [z1, cx1, cy1]] = s.move;
        const p = `(on/${Math.max(frames - 1, 1)})`;
        const zoom = `${fx(z0)}+${fx(z1 - z0)}*${p}`;
        const x = `max(0,min(iw-iw/zoom,(${fx(cx0)}+${fx(cx1 - cx0)}*${p})*${UP}-iw/zoom/2))`;
        const y = `max(0,min(ih-ih/zoom,(${fx(cy0)}+${fx(cy1 - cy0)}*${p})*${UP}-ih/zoom/2))`;
        let chain = `[${idx}:v]trim=start_frame=${a}:end_frame=${a + frames},setpts=PTS-STARTPTS,` +
            `scale=${GW * UP}:${GH * UP}:flags=neighbor,` +
            `zoompan=z='${zoom}':x='${x}':y='${y}':d=1:s=${OW}x${OH}:fps=${FPS},setsar=1,format=yuv444p`;
        if (s.fadeIn) chain += `,fade=t=in:st=0:d=${s.fadeIn}`;
        graph.push(`${chain}[${label}b]`);
    }
    const top = overlayTitles(`${label}b`, s, label, pre);
    graph.push(`[${top}]format=yuv444p[${label}]`);
    labels.push({ label, dissolve: s.dissolve, len: s.end - s.at });
}

// dissolves fold a segment into its predecessor with xfade; everything else is a straight cut
const chunks = [];
let acc = null, accLen = 0;
for (const { label, dissolve, len } of labels) {
    if (dissolve && acc) {
        const out = `${acc}x`;
        graph.push(`[${acc}][${label}]xfade=transition=fade:duration=${dissolve}:offset=${fx(accLen - dissolve)}[${out}]`);
        acc = out; accLen += len;
        chunks[chunks.length - 1] = acc;
    } else {
        acc = label; accLen = len;
        chunks.push(acc);
    }
}
graph.push(`${chunks.map(c => `[${c}]`).join('')}concat=n=${chunks.length}:v=1:a=0[base]`);

graph.push(`[base]fade=t=out:st=${fx(END - FADE_OUT)}:d=${FADE_OUT},format=yuv420p[v]`);

// ---- music ----
const mi = addInput('-ss', String(MUSIC.start), '-t', fx(END), '-i', path.join(REPO, MUSIC.file));
graph.push(`[${mi}:a]afade=t=in:st=0:d=${MUSIC.fadeIn},afade=t=out:st=${fx(END - MUSIC.fadeOut)}:d=${MUSIC.fadeOut}[a]`);

const outFile = path.join(OUT, preview ? `preview-${cutName}.mp4` : cutFile);
const scriptFile = path.join(OUT, `filter-${cutName}.txt`);
fs.writeFileSync(scriptFile, graph.join(';\n'));
const enc = preview
    ? ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23']
    // Steamworks asks for 5,000+ kbps and its own Media Encoder preset is 20 Mbps; Steam re-encodes the upload
    : ['-c:v', 'libx264', '-preset', 'slow', '-b:v', '20M', '-maxrate', '24M', '-bufsize', '40M', '-profile:v', 'high', '-level', '4.2'];
const args = ['-hide_banner', '-loglevel', 'error', '-stats', '-y', ...inputs,
    '-/filter_complex', scriptFile, '-map', '[v]', '-map', '[a]',
    ...enc, '-r', String(FPS), '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', fx(END), '-movflags', '+faststart', outFile];
console.log(`segments ${segs.length}, titles ${titleList.length}, length ${END.toFixed(2)} s → ${path.relative(process.cwd(), outFile)}`);
const r = spawnSync('ffmpeg', args, { stdio: 'inherit' });
process.exit(r.status ?? 1);
