// Electron entry for the trailer capture. Opens capture.html in a hidden window and turns the frames the
// director sends into one lossless clip per shot (out/shots/<id>.mkv) plus PNG stills (out/stills/).
//
//   node_modules/.bin/electron tools/trailer/capture-main.cjs [--survey|--screenshots] [--only id,id] [--fps 60] [--lang cs]
const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const W = 1067, H = 600;
const OUT = path.join(__dirname, 'out');

const argv = process.argv.slice(2);
const flag = (name) => argv.includes(`--${name}`);
const opt = (name, def) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : def; };
const options = {
    survey: flag('survey'),
    screenshots: flag('screenshots'),
    only: opt('only', '') ? opt('only').split(',') : null,
    fps: Number(opt('fps', 60)),
    lang: opt('lang', 'en'),
};
// Steam matches localized screenshots by a language suffix in the file name (foo_czech.png).
const STEAM_LANG = { en: '', cs: '_czech' };

fs.mkdirSync(path.join(OUT, 'shots'), { recursive: true });
fs.mkdirSync(path.join(OUT, 'stills'), { recursive: true });
fs.mkdirSync(path.join(OUT, 'screenshots'), { recursive: true });

let encoder = null; // { proc, done: Promise, frames }

function ffmpeg(args) {
    const proc = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', ...args], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise((res, rej) => proc.on('close', code => code === 0 ? res() : rej(new Error(`ffmpeg exited ${code}`))));
    return { proc, done };
}

const rawInput = (fps) => ['-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(fps), '-i', '-'];

ipcMain.on('args', (e) => { e.returnValue = options; });
ipcMain.on('log', (_e, msg) => console.log(`[page] ${msg}`));

ipcMain.handle('begin', (_e, id) => {
    const file = path.join(OUT, 'shots', `${id}.mkv`);
    // readPixels rows come bottom-up, hence vflip. Lossless RGB so the post upscale starts from exact pixels.
    encoder = { ...ffmpeg([...rawInput(options.fps), '-vf', 'vflip', '-c:v', 'libx264rgb', '-qp', '0', '-preset', 'ultrafast', file]), frames: 0, id };
    console.log(`[capture] ${id} → ${path.relative(process.cwd(), file)}`);
});

ipcMain.handle('frame', (_e, data) => new Promise((res) => {
    const buf = Buffer.from(data.buffer, data.byteOffset, data.byteLength);
    encoder.frames++;
    if (encoder.proc.stdin.write(buf)) res(); else encoder.proc.stdin.once('drain', res);
}));

ipcMain.handle('end', async () => {
    const { proc, done, frames, id } = encoder;
    proc.stdin.end();
    await done;
    console.log(`[capture] ${id}: ${frames} frames (${(frames / options.fps).toFixed(2)} s)`);
    encoder = null;
});

// A survey still stays at native size; a Steam screenshot is upscaled 4× nearest-neighbour, then averaged down to 1080p.
ipcMain.handle('still', async (_e, name, data, screenshot) => {
    const vf = screenshot ? `vflip,scale=${W * 4}:${H * 4}:flags=neighbor,scale=1920:1080:flags=area` : 'vflip';
    const file = path.join(OUT, screenshot ? 'screenshots' : 'stills', `${name}${screenshot ? STEAM_LANG[options.lang] ?? `_${options.lang}` : ''}.png`);
    const { proc, done } = ffmpeg([...rawInput(1), '-vf', vf, '-frames:v', '1', file]);
    proc.stdin.end(Buffer.from(data.buffer, data.byteOffset, data.byteLength));
    await done;
});

ipcMain.handle('json', (_e, name, data) => {
    fs.writeFileSync(path.join(OUT, 'stills', `${name}.json`), JSON.stringify(data, null, 1));
});

ipcMain.handle('finish', (_e, code) => { process.exitCode = code || 0; app.quit(); });

app.whenReady().then(() => {
    const win = new BrowserWindow({
        width: W, height: H, useContentSize: true, show: false,
        webPreferences: {
            preload: path.join(__dirname, 'capture-preload.cjs'),
            contextIsolation: false, sandbox: false, nodeIntegration: false,
            backgroundThrottling: false,
            partition: 'trailer-capture', // in-memory: fresh localStorage every run
        },
    });
    win.webContents.setAudioMuted(true);
    win.webContents.on('console-message', (_e, level, message, line, source) => {
        if (level >= 2) console.log(`[console:${level}] ${message} (${path.basename(source || '')}:${line})`);
    });
    win.webContents.on('render-process-gone', (_e, d) => { console.error('[capture] renderer gone', d); app.exit(2); });
    win.loadFile(path.join(__dirname, 'capture.html'));
});
