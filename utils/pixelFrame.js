/**
 * Small UI plates on the 2x pixel grid (utils/pixelGrid.js), in the menu kit's colours: a dark green body and a 2 px
 * rim with its corners cut off (one grid pixel, or two for `round`), so notices, tooltips, labels and speech bubbles
 * read as pixel art beside the world and the menu kit, not as smooth vector boxes. Sizes are rounded up to the grid
 * (centred plates to 4, so their edges stay on even pixels).
 *
 * UI_FONT is the in-world UI's one face (the dialog's): menus keep the kit's own (MENU_FONT).
 */
import { GRID } from './pixelGrid.js';

export const UI_FONT = '"Departure Mono", "Courier New", monospace';
// Departure Mono is drawn on an 11 px grid, so only 11 and 22 px are crisp (and no bold: the browser smears a fake one).
export const UI_SIZE = '22px';    // reading text: dialogs, captions, the intro, the tutorial (its pixels on the 2x grid)
export const UI_SMALL = '11px';   // small UI: speech bubbles, notices, labels, tooltips, name tags (as small as before)
export const FRAME = { fill: 0x0c1410, alpha: 0.92, rim: 0x8a6a2a };   // the dialog card's body, the kit's dull gold

const up = (v, step) => Math.ceil(v / step) * step;
export const snap = v => Math.round(v / GRID) * GRID;

/** Draw a plate into graphics `g`, top-left (x, y), w x h (snapped). Returns the snapped box. */
export function drawPixelFrame(g, x, y, w, h, { fill = FRAME.fill, alpha = FRAME.alpha, rim = FRAME.rim, rimAlpha = 1, round = false } = {}) {
    const G = GRID, c = round ? 2 * G : G;                          // corner cut
    x = snap(x); y = snap(y); w = up(w, G); h = up(h, G);
    g.fillStyle(fill, alpha);
    g.fillRect(x + G, y + G, w - 2 * G, h - 2 * G);
    g.fillStyle(rim, rimAlpha);
    g.fillRect(x + c, y, w - 2 * c, G);                             // top, bottom
    g.fillRect(x + c, y + h - G, w - 2 * c, G);
    g.fillRect(x, y + c, G, h - 2 * c);                             // left, right
    g.fillRect(x + w - G, y + c, G, h - 2 * c);
    if (round) {                                                    // the step inside each cut corner
        for (const [cx, cy] of [[x + G, y + G], [x + w - 2 * G, y + G], [x + G, y + h - 2 * G], [x + w - 2 * G, y + h - 2 * G]]) {
            g.fillRect(cx, cy, G, G);
        }
    }
    return { x, y, w, h };
}

/** A plate centred on (0, 0): a Graphics to put in a container. Width / height rounded up to 4. */
export function pixelPlate(scene, w, h, opts) {
    const g = scene.add.graphics();
    w = up(w, 2 * GRID); h = up(h, 2 * GRID);
    drawPixelFrame(g, -w / 2, -h / 2, w, h, opts);
    g.plateW = w; g.plateH = h;
    return g;
}

/**
 * A stepped tail (a bubble's pointer) with its tip at (tipX, tipY), `steps` grid rows long, pointing 'down', 'up' or 'left'.
 * Its widest row lies on the plate's rim and opens it, so draw it after the plate, with the base row on the rim.
 */
export function drawPixelTail(g, tipX, tipY, steps, dir, { fill = FRAME.fill, rim = FRAME.rim } = {}) {
    const G = GRID;
    tipX = snap(tipX); tipY = snap(tipY);
    for (let i = 0; i < steps; i++) {
        const half = i * G;                                         // 0 at the tip
        if (dir === 'down' || dir === 'up') {
            const y = dir === 'down' ? tipY - (i + 1) * G : tipY + i * G;
            if (half) g.fillStyle(fill, 1).fillRect(tipX - half, y, 2 * half, G);   // opaque: it covers the rim it opens
            g.fillStyle(rim, 1).fillRect(tipX - half - G, y, G, G).fillRect(tipX + half, y, G, G);
        } else {                                                    // 'left': the tip on the left
            const x = tipX + i * G;
            if (half) g.fillStyle(fill, 1).fillRect(x, tipY - half, G, 2 * half);
            g.fillStyle(rim, 1).fillRect(x, tipY - half - G, G, G).fillRect(x, tipY + half, G, G);
        }
    }
}
