/**
 * fitBackground.js — show the WHOLE background image, fitted to the 1067×600 canvas.
 *
 * This is the game's original behaviour generalised to the new resolution: the source art (mixed
 * aspect ratios, usually much larger than the canvas) is scaled to exactly fill the frame, so the
 * entire picture is always on screen — no bars, nothing cropped, one image. Non-16:9 sources get
 * stretched horizontally to fit, exactly as they were stretched to 4:3 before; that is acceptable
 * for scenery, and the ideal remains redrawing backgrounds at 1067×600.
 *
 * Uniform "cover" (crops the image — lost most of the Crossroad buildings) and "contain + dim echo"
 * (looked like two backgrounds stacked) were both tried and rejected: the full picture must show.
 */
export function fitBackground(scene, img) {
    const cw = scene.scale.width, ch = scene.scale.height;
    img.setDisplaySize(cw, ch).setPosition(cw / 2, ch / 2);
    return img;
}
