/**
 * talk.js: when a character's line appears in a dialogue, their mouth moves for a few moments.
 *
 * The mouths are overlay sheets made by tools/artgen/talk_mouths.py (assets/images/characters/talk/<sheet>.png): the
 * idle sheet's frame size, row 0 half open, row 1 open, only the mouth's pixels opaque. An overlay sprite follows the
 * speaking sprite every frame (position, origin, scale, mirroring, its idle frame, mask, container), so it opens the
 * mouth of whatever frame is showing; being a character sheet it takes the scene's light like the sprite it covers.
 *
 * Which part of a line is spoken: the words in quotes if there are any ("Heliodor nods. „Welcome…“" moves the mouth
 * for the welcome only), else the line without its *actions*; a line opening with the speaker's own name and no
 * quotes is narration and moves nothing. Characters without a sheet here simply don't move their mouth.
 */
const SHEETS = {   // the sheet's file name → its frame size and the mouth's middle column (talk_mouths.py CHARS)
    edgar_eskola: [128, 192, 57], heliodor_idle: [128, 192, 64], ortolan_idle: [128, 160, 64], elphi_idle: [128, 160, 58],
    liris_idle: [128, 160, 64], ravla_idle: [128, 144, 60], senior_clerk: [128, 192, 64], clerk_applications: [128, 176, 64],
    zerren: [176, 160, 88], kloor: [128, 160, 101],
};
const keyOf = stem => `talk_${stem}`;

const STEM = new Map();   // texture key → its sheet's file name (module-wide: textures outlive the scenes)

/**
 * GameScene.preload (first thing): note which file each character texture comes from (the loader hands images over as
 * blob URLs, so a texture can't tell), and load the mouths (small, once; the texture manager keeps them).
 */
export function preloadTalk(scene) {
    const loader = scene.load;
    if (!loader.__talkStems) {
        loader.__talkStems = true;
        loader.on('load', file => {
            const m = /assets\/images\/characters\/(?:[^/]+\/)*([^/]+)\.png/.exec(file.url || '');
            if (m && SHEETS[m[1]] && !/\/talk\//.test(file.url)) STEM.set(file.key, m[1]);
        });
    }
    for (const [stem, [frameWidth, frameHeight]] of Object.entries(SHEETS)) {
        if (!scene.textures.exists(keyOf(stem))) {
            loader.spritesheet(keyOf(stem), `assets/images/characters/talk/${stem}.png`, { frameWidth, frameHeight });
        }
    }
}

/** the column of a texture's face (its mouth's middle, frame 0), or null: the Cinema portrait centres on it */
export function faceX(textureKey) {
    const stem = STEM.get(textureKey);
    return stem ? SHEETS[stem][2] : null;
}

/** the mouth sheet of a sprite's texture (a sheet can be loaded under several keys) */
function mouthKey(scene, sprite) {
    const stem = STEM.get(sprite?.texture?.key);
    return stem && scene.textures.exists(keyOf(stem)) ? keyOf(stem) : null;
}

/** How long the mouth moves for a line (ms), 0 for none. */
export function talkTime(text, speaker) {
    if (!text) return 0;
    const quoted = [...text.matchAll(/„([^“”"]+)[“”"]|“([^”]+)”|"([^"]+)"|(?:^|\s)'([^']+)'(?=[\s.,!?…]|$)/g)]
        .map(m => m.slice(1).find(Boolean)).join(' ');
    let speech = quoted;
    if (!speech) {
        speech = text.replace(/\*[^*]*\*/g, ' ').trim();
        const first = speech.split(/\s+/)[0]?.replace(/[^\p{L}]/gu, '').toLowerCase();
        const names = String(speaker || '').toLowerCase().split(/\s+/).filter(w => w.length >= 3);
        if (first && names.includes(first)) return 0;           // "Heliodor nods politely." is narration
    }
    const letters = speech.replace(/[^\p{L}\p{N}]/gu, '').length;
    return letters < 2 ? 0 : Math.max(700, Math.min(2800, letters * 55));
}

/** an overlay sprite over `host`, or null when the host has no mouth sheet */
function overlay(scene, host) {
    if (!host?.active || (host.type !== 'Sprite' && host.type !== 'Image')) return null;
    const key = mouthKey(scene, host);
    if (!key) return null;
    const ov = scene.add.sprite(host.x, host.y, key, 0).setVisible(false);
    const c = host.parentContainer;
    if (c) c.addAt(ov, c.getIndex(host) + 1);                 // the cinema's portrait: inside its bar, over the bust
    else scene.children.moveAbove?.(ov, host);                // the world: right over the sprite, at its depth
    if (host.mask) ov.setMask(host.mask);
    return { ov, host, n: (scene.textures.get(key).frameTotal - 1) / 2 };
}

function follow({ ov, host, n }, state) {
    if (!ov.active) return;
    const idx = Number(host.frame?.name);
    if (!state || !host.active || !host.visible || !(idx >= 0 && idx < n)) { ov.setVisible(false); return; }
    ov.setFrame((state - 1) * n + idx).setVisible(true)
        .setPosition(host.x, host.y).setOrigin(host.originX, host.originY)
        .setScale(host.scaleX, host.scaleY).setFlip(host.flipX, host.flipY)
        .setRotation(host.rotation).setAlpha(host.alpha)
        .setScrollFactor(host.scrollFactorX, host.scrollFactorY);
    if (!host.parentContainer && ov.depth !== host.depth) ov.setDepth(host.depth);
}

/** Move the mouths of `hosts` (the speaker's sprite in the world, their portrait) for this line. */
export function startTalk(scene, hosts, text, speaker) {
    stopTalk(scene);
    const ms = talkTime(text, speaker);
    if (!ms) return;
    const items = [...new Set(hosts)].map(h => overlay(scene, h)).filter(Boolean);
    if (!items.length) return;
    const talk = { items, state: 0, timer: null, end: scene.time.now + ms };
    talk.sync = () => items.forEach(it => follow(it, talk.state));
    // the mouth flaps: open, half, shut at an uneven pace, never the same twice, and shuts at the end
    const flap = () => {
        if (scene.time.now >= talk.end) { talk.state = 0; talk.sync(); return; }
        const next = [0, 1, 2].filter(s => s !== talk.state);
        talk.state = next[Math.random() < (talk.state === 0 ? 0.65 : 0.5) ? next.length - 1 : 0];
        talk.sync();
        talk.timer = scene.time.delayedCall(Phaser.Math.Between(70, 140), flap);
    };
    scene.events.on('postupdate', talk.sync);
    scene._talk = talk;
    flap();
}

/** Shut the mouths and remove the overlays (the next line, the dialog closing). */
export function stopTalk(scene) {
    const talk = scene._talk;
    if (!talk) return;
    scene._talk = null;
    talk.timer?.remove(false);
    scene.events.off('postupdate', talk.sync);
    talk.items.forEach(({ ov }) => ov.destroy());
}
