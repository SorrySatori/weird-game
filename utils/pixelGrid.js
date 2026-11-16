/**
 * The game's 2x pixel grid: all world art is drawn with one art pixel = 2x2 screen pixels (tools/artgen/grid2x.py),
 * the backgrounds' grid starting at the canvas origin.
 *
 * snapToArtGrid: a sprite standing at an odd coordinate (a walk, a tween, a scene's own placement) would show its
 * blocks one screen pixel off the background's. Just before drawing, every visible sprite / image (the world's and the
 * HUD's; not ones inside containers) is moved so
 * its top-left corner sits on the grid; right after drawing it goes back, so movement, tweens and input never see it.
 *
 * pixelEllipseTexture: ground shadows as a stepped ellipse on the same grid (a smooth vector ellipse read as UI).
 */
export const GRID = 2;

export function snapToArtGrid(scene) {
    const moved = [];
    const pre = () => {
        for (const o of scene.children.list) {
            if ((o.type !== 'Sprite' && o.type !== 'Image') || !o.visible) continue;   // world and HUD alike
            const left = o.x - o.displayOriginX * Math.abs(o.scaleX), top = o.y - o.displayOriginY * Math.abs(o.scaleY);
            const dx = Math.round(left / GRID) * GRID - left, dy = Math.round(top / GRID) * GRID - top;
            if (dx || dy) { moved.push(o, o.x, o.y); o.x += dx; o.y += dy; }
        }
    };
    const post = () => {
        for (let i = 0; i < moved.length; i += 3) { moved[i].x = moved[i + 1]; moved[i].y = moved[i + 2]; }
        moved.length = 0;
    };
    scene.events.on('prerender', pre);
    scene.events.on('render', post);
    scene.events.once('shutdown', () => { scene.events.off('prerender', pre); scene.events.off('render', post); });
}

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
