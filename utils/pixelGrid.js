/**
 * The world's pixel grid: backgrounds, characters, props and the HUD are drawn 1:1 (one art pixel = one canvas pixel,
 * 1067x600). Phaser's pixelArt mode already rounds sprite positions to whole pixels (roundPixels).
 * The UI panels (menu kit, dialog card, plates in utils/pixelFrame.js) are a separate layer on a 2x grid.
 *
 * pixelEllipseTexture: ground shadows as a stepped ellipse (a smooth vector ellipse read as UI).
 */
export const GRID = 1;

/** A black stepped ellipse w x h (rounded to the grid), made once per size; shown at scale 1 with the caller's alpha. */
export function pixelEllipseTexture(scene, w, h) {
    w = Math.max(GRID, Math.round(w / GRID) * GRID); h = Math.max(GRID, Math.round(h / GRID) * GRID);
    const key = `pxShadow_${w}x${h}`;
    if (scene.textures.exists(key)) return key;
    const tex = scene.textures.createCanvas(key, w, h), ctx = tex.getContext();
    const cw = w / GRID, ch = h / GRID;
    ctx.fillStyle = '#000';
    for (let j = 0; j < ch; j++) {
        for (let i = 0; i < cw; i++) {
            const u = (i + 0.5 - cw / 2) / (cw / 2), v = (j + 0.5 - ch / 2) / (ch / 2);
            if (u * u + v * v <= 1) ctx.fillRect(i * GRID, j * GRID, GRID, GRID);
        }
    }
    tex.refresh();
    return key;
}
