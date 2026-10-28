// Looping GIFs for the Steam "About This Game" section → out/gifs/<id>.gif
//
//   node tools/trailer/gifs.mjs [id ...]
//
// Steam: every description image < 5 MB and all of them together < 15 MB; textless (text would need translating).
// 616 px is the width of the description column. Camera moves are avoided: a GIF stays small only while most
// pixels hold still between frames. Sources are the gif_* (and some story) captures from shots.js.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, 'out');
const W = 616, FPS = 15;

// parts play in order; `fade` crossfades into the next part. `crop`: [zoom, cx, cy] in game coordinates.
const GIFS = {
    // the same street, Growth → Decay → Growth (both captures run on the same clock, so Gnur keeps walking)
    growth_decay: { parts: [
        { shot: 'gif_growth', in: 0.2, len: 1.6, fade: 0.5 },
        { shot: 'gif_decay', in: 1.3, len: 1.5, fade: 0.5 },
        { shot: 'gif_growth', in: 2.3, len: 0.9 },
    ] },
    // spores into the demigod's corpse: the mycelium tree at the Crossroads
    spores_tree: { crop: [1.25, 470, 300], parts: [
        { shot: 'gif_corpse_before', in: 0.3, len: 1.2, fade: 0.6 },
        { shot: 'gif_corpse_after', in: 0.3, len: 2.4, fade: 0.5 },
        { shot: 'gif_corpse_before', in: 0.3, len: 0.6 },
    ] },
    // Amber Oltrac, past the game's full-screen flash at 1.0–1.9 s; the particles change most pixels every frame,
    // so this one runs at a lower frame rate and with a smaller palette to stay under 5 MB
    // (the effect shakes the camera: the slight crop keeps the black beyond the picture out of frame)
    oltrac: { fps: 12, colors: 160, crop: [1.1, 533.5, 300], parts: [
        { shot: 'gif_oltrac', in: 0.1, len: 0.8, fade: 0.5 },
        { shot: 'gif_oltrac', in: 2.0, len: 2.6, fade: 0.5 },
        { shot: 'gif_oltrac', in: 0.1, len: 0.5 },
    ] },
    // Feral Toast on stage; three cycles of the 177 BPM playing loop (8 frames, 2 per beat)
    feral_toast: { crop: [1.55, 534, 385], parts: [{ shot: 'feral', in: 0.3, len: 3 * 8 * 60 / 177 / 2 }] },
    // the city: four places, straight cuts
    city: { parts: [
        { shot: 'cathedral', in: 0.6, len: 1.4 },
        { shot: 'scraper', in: 0.4, len: 1.4 },
        { shot: 'voxmarket', in: 0.4, len: 1.4 },
        { shot: 'bears', in: 0.6, len: 1.4 },
    ] },
};

function build(id, { parts, crop, fps = FPS, colors = 256 }) {
    const inputs = [], graph = [];
    parts.forEach((p, i) => {
        const file = path.join(OUT, 'shots', `${p.shot}.mkv`);
        if (!fs.existsSync(file)) throw new Error(`missing capture ${file} — run tools/trailer/capture.sh --only ${p.shot}`);
        inputs.push('-i', file);
        let chain = `[${i}:v]trim=start=${p.in}:duration=${p.len},setpts=PTS-STARTPTS`;
        if (crop) {
            const [z, cx, cy] = crop, cw = Math.round(1067 / z), ch = Math.round(600 / z);
            const x = Math.max(0, Math.min(1067 - cw, Math.round(cx - cw / 2))), y = Math.max(0, Math.min(600 - ch, Math.round(cy - ch / 2)));
            chain += `,crop=${cw}:${ch}:${x}:${y}`;
        }
        graph.push(`${chain},scale=${W}:-2:flags=area,fps=${fps},format=rgb24,setsar=1[p${i}]`);
    });
    let cur = 'p0', len = parts[0].len;
    for (let i = 1; i < parts.length; i++) {
        const fade = parts[i - 1].fade;
        if (fade) {
            graph.push(`[${cur}][p${i}]xfade=transition=fade:duration=${fade}:offset=${(len - fade).toFixed(3)}[x${i}]`);
            len += parts[i].len - fade;
        } else {
            graph.push(`[${cur}][p${i}]concat=n=2:v=1:a=0[x${i}]`);
            len += parts[i].len;
        }
        cur = `x${i}`;
    }
    // one palette per GIF; Bayer dithering keeps flat pixel-art areas flat (and the file small)
    graph.push(`[${cur}]split[a][b];[a]palettegen=max_colors=${colors}:stats_mode=full[pal];[b][pal]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle[g]`);
    const out = path.join(OUT, 'gifs', `${id}.gif`);
    const r = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...inputs, '-filter_complex', graph.join(';'),
        '-map', '[g]', '-loop', '0', out], { stdio: 'inherit' });
    if (r.status !== 0) throw new Error(`ffmpeg failed for ${id}`);
    const mb = fs.statSync(out).size / 1e6;
    console.log(`${id}.gif  ${len.toFixed(2)} s  ${mb.toFixed(2)} MB${mb >= 5 ? '  ← over Steam\'s 5 MB limit' : ''}`);
    return mb;
}

fs.mkdirSync(path.join(OUT, 'gifs'), { recursive: true });
const want = process.argv.slice(2);
let total = 0;
for (const [id, def] of Object.entries(GIFS)) if (!want.length || want.includes(id)) total += build(id, def);
console.log(`total ${total.toFixed(2)} MB (Steam: < 15 MB for all description images)`);
