/**
 * paintingIdleFX.js — the main menu painting's two characters (Edgar and Ortolan) breathe and shift their weight,
 * each as a whole: a post-FX on the painting that warps it gently inside a soft weight map (idle_weight.png from
 * tools/artgen/menu_painting_band.py: R = Edgar, G = Ortolan). Nothing is cut out, so there are no seams: the warp
 * fades out over a few pixels round each figure, and the feet are its anchor (they don't move at all).
 *
 *   breathing  the figure stretches up a little (the head ~1.6 px), the chest widens a touch
 *   weight     it leans slowly from side to side, more at the top than at the hips
 *
 * The amounts are in the painting's own pixels (band.png); the periods differ between the two so they never move in
 * step. The painting may sit anywhere on screen at any scale (origin, scale: MainScene's menu layouts). Sampling is
 * done by hand (bilinear) so sub-pixel motion stays smooth with pixelArt's NEAREST filtering.
 */
const FRAG = `
#define SHADER_NAME PAINTING_IDLE_FS
precision highp float;           // pixel coordinates up to 1067: mediump is off by half a pixel there
uniform sampler2D uMainSampler;
uniform sampler2D uWeight;
uniform vec2 uBand;        // the painting's size in its own px (band.png)
uniform vec2 uScreen;      // the render target's size in px (the game's size)
uniform vec2 uOrigin;      // the painting's top-left on screen
uniform float uScale;      // painting px -> screen px
uniform float uFlip;       // 1: the render target's v runs bottom-up
uniform float uTime;
uniform vec4 uGeoA;        // Edgar: feet y, height, centre x, half width (painting px)
uniform vec4 uMotA;        // Edgar: breath px, sway px, breath period s, sway period s
uniform vec4 uGeoB;        // Ortolan
uniform vec4 uMotB;
varying vec2 outTexCoord;

vec2 toUv(vec2 s) {
    vec2 uv = s / uScreen;
    return vec2(uv.x, mix(uv.y, 1.0 - uv.y, uFlip));
}

vec4 bilinear(vec2 px) {
    vec2 p = px - 0.5;
    vec2 f = fract(p);
    vec2 i = floor(p);
    vec4 a = texture2D(uMainSampler, toUv(i + vec2(0.5, 0.5)));
    vec4 b = texture2D(uMainSampler, toUv(i + vec2(1.5, 0.5)));
    vec4 c = texture2D(uMainSampler, toUv(i + vec2(0.5, 1.5)));
    vec4 d = texture2D(uMainSampler, toUv(i + vec2(1.5, 1.5)));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

vec2 idle(vec2 px, vec4 geo, vec4 mot, float phase) {
    float h = clamp((geo.x - px.y) / geo.y, 0.0, 1.0);               // 0 at the soles, 1 at the top of the head
    float breath = mot.x * 0.5 * (1.0 - cos(6.2831853 * uTime / mot.z + phase));
    float sway = mot.y * sin(6.2831853 * uTime / mot.w + phase * 1.7);
    float chest = exp(-pow((h - 0.66) / 0.16, 2.0));
    float dx = sway * pow(h, 1.3) + breath * 0.4 * chest * clamp((px.x - geo.z) / geo.w, -1.0, 1.0);
    float dy = -breath * pow(h, 1.4);
    return vec2(dx, dy);
}

void main() {
    vec2 uv = outTexCoord;
    vec2 s = vec2(uv.x, mix(uv.y, 1.0 - uv.y, uFlip)) * uScreen;    // screen px, y down
    vec2 px = (s - uOrigin) / uScale;                                   // painting px
    vec4 w = texture2D(uWeight, clamp(px / uBand, 0.0, 1.0));
    if (w.r + w.g < 0.004 || px.x < 0.0 || px.y < 0.0 || px.x > uBand.x || px.y > uBand.y) {
        gl_FragColor = texture2D(uMainSampler, uv);
        return;
    }
    vec2 d = w.r * idle(px, uGeoA, uMotA, 0.0) + w.g * idle(px, uGeoB, uMotB, 2.1);
    gl_FragColor = bilinear(s - d * uScale);
}
`;

export class PaintingIdleFX extends Phaser.Renderer.WebGL.Pipelines.PostFXPipeline {
    constructor(game) {
        super({ game, name: 'PaintingIdleFX', fragShader: FRAG });
        this.time = 0;
        this.weight = null;       // the weight map's WebGL texture
        this.band = [1012, 716];
        this.origin = [0, 0];
        this.scale = 1;
        this.flip = 1;
        this.geo = { edgar: [0, 1, 0, 1], ortolan: [0, 1, 0, 1] };
        this.motion = { edgar: [1.6, 1.3, 4.6, 9.0], ortolan: [1.5, 1.1, 5.4, 11.0] };
    }

    onDraw(target) {
        this.set1f('uTime', this.time);
        this.set2f('uBand', this.band[0], this.band[1]);
        this.set2f('uScreen', target.width, target.height);
        this.set2f('uOrigin', this.origin[0], this.origin[1]);
        this.set1f('uScale', this.scale);
        this.set1f('uFlip', this.flip);
        this.set4f('uGeoA', ...this.geo.edgar);
        this.set4f('uMotA', ...this.motion.edgar);
        this.set4f('uGeoB', ...this.geo.ortolan);
        this.set4f('uMotB', ...this.motion.ortolan);
        if (this.weight) {
            this.bindTexture(this.weight, 1);
            this.set1i('uWeight', 1);
        }
        this.bindAndDraw(target);
    }
}
