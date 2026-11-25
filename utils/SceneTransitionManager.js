/**
 * SceneTransitionManager.js
 * Handles scene transitions with consistent behavior across all scenes
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { isDemoClosed, placeDemoCones, demoClosedLabel, sayDemoClosed } from './demo.js';
import { UI_FONT, FRAME, UI_SMALL } from './pixelFrame.js';

// exit labels: the in-world UI face on the dialog card's dark green (utils/pixelFrame.js), the names in the dialog's gold
const LABEL_BG = `rgba(${FRAME.fill >> 16 & 255}, ${FRAME.fill >> 8 & 255}, ${FRAME.fill & 255}, ${FRAME.alpha})`;
const EXIT_INK = '#e8c46a';

export default class SceneTransitionManager {
    constructor(scene) {
        this.scene = scene;
        
        // Store references to all transition elements for cleanup
        this.transitionElements = [];
        
        // Define standard colors for transition indicators
        this.colors = {
            normal: 0xffb700,    // Bright amber color for better visibility
            hover: 0xffd700,     // Gold color for hover state
            glow: 0xff9500,      // Orange glow
            text: 0xffffff       // White text
        };
        
        // Default transition settings
        this.defaultSettings = {
            walkDuration: 1000,           // Default duration for walking animations
            fadeOutDuration: 800,        // Default duration for fade out effect
            safetyTimeout: 2000,         // Safety timeout to force transition if tween doesn't complete
            minWalkDuration: 500,        // Minimum walk duration
            walkSpeedFactor: 3           // Walk speed factor (ms per pixel)
        };
        
        // Add scene shutdown event to clean up resources
        this.scene.events.on('shutdown', this.cleanup, this);
    }
    
    /**
     * Clean up all transition elements when the scene shuts down
     */
    cleanup() {
        // Remove all event listeners and destroy all elements
        this.transitionElements.forEach(item => {
            // Remove resize listener
            if (item.elements && item.elements.resizeListener) {
                window.removeEventListener('resize', item.elements.resizeListener);
            }
            
            // Stop all tweens
            if (item.elements && item.elements.tweens) {
                item.elements.tweens.forEach(tween => {
                    if (tween && tween.stop) {
                        tween.stop();
                    }
                });
            }
            
            // Destroy containers
            if (item.elements && item.elements.arrowContainer) {
                item.elements.arrowContainer.destroy();
            }
            
            if (item.elements && item.elements.textContainer) {
                item.elements.textContainer.destroy();
            }
        });
        
        // Clear the array
        this.transitionElements = [];
    }

    /**
     * Create a transition zone that handles scene transitions
     * @param {number} x - X position of the zone
     * @param {number} y - Y position of the zone
     * @param {number} width - Width of the zone
     * @param {number} height - Height of the zone
     * @param {string} direction - Direction of the transition (up, down, left, right)
     * @param {string} targetScene - Target scene key
     * @param {number} walkX - X position to walk to before transition
     * @param {number} walkY - Y position to walk to before transition
     * @param {string} destinationName - Name of the destination to display
     * @param {Object} options - Additional options for the transition
     * @returns {Phaser.GameObjects.Zone} The created transition zone
     */
    createTransitionZone(x, y, width, height, direction, targetScene, walkX, walkY, destinationName = '', options = {}) {
        // Scenes still place their exits in the original 800-wide layout. Remap X proportionally
        // into the current canvas width (1067) so left exits stay left, right exits stay right and
        // door hotspots land where the widened background put them. Y is unchanged (height is
        // still 600). walkX — where the priest walks before leaving — gets the same treatment.
        const kx = this.scene.scale.width / 800;
        x = Math.round(x * kx);
        width = Math.round(width * kx);   // keep relative spacing so remapped zones don't overlap neighbours
        if (typeof walkX === 'number') walkX = Math.round(walkX * kx);

        destinationName = this.exitLabel(destinationName, targetScene, direction);

        // the demo build: a way into a place outside the demo is closed off by a traffic cone
        if (isDemoClosed(targetScene)) return this.createClosedExit({ x: x - width / 2, y: y - height / 2, w: width, h: height }, targetScene);

        // Create the interactive zone
        const zone = this.scene.add.zone(x, y, width, height)
            .setInteractive({ useHandCursor: true })
            .setOrigin(0.5)
            .setDepth(10);
            
        // Store the destination name for use in hover effect
        zone.destinationName = destinationName;
        zone.direction = direction;

        // Add the hover arrow effect
        const transitionElements = this.addHoverEffect(zone, direction);
        
        // Store references to the created elements
        this.transitionElements.push({
            zone,
            elements: transitionElements
        });

        // Add the transition logic
        zone.on('pointerdown', () => {
            // Use the handleSceneTransition method to ensure consistent behavior
            this.handleSceneTransition(targetScene, walkX, walkY, options);
        });

        // A side exit touching the screen edge can also be walked into with the arrow keys: the priest walks on out
        // of the picture while the scene fades (GameScene.registerEdgeExit / PlayerMovementSystem)
        const W = this.scene.scale.width;
        const atEdge = (direction === 'left' && x - width / 2 <= W * 0.2) || (direction === 'right' && x + width / 2 >= W * 0.8);
        if (atEdge && this.scene.registerEdgeExit) {
            this.scene.registerEdgeExit(direction, () => {
                const p = this.scene.priest;
                if (!p) { this.handleSceneTransition(targetScene, walkX, walkY, options); return; }
                this.handleSceneTransition(targetScene, p.x + (direction === 'left' ? -70 : 70), p.y, options);
            }, zone, [y - height / 2 - 40, y + height / 2 + 40]);
        }

        return zone;
    }
    
    /**
     * The localized label of an exit: a scene's own English label via `exits.<label>` (lang/<code>/locations.js),
     * otherwise the destination's name from `locations.<sceneKey>`; a label that is just a scene key counts as none
     */
    exitLabel(destinationName, targetScene, direction) {
        const lang = LanguageSystem.getInstance();
        if (/Scene$/.test(destinationName) && lang.str(`locations.${destinationName}`)) destinationName = '';
        if (destinationName) destinationName = lang.str(`exits.${destinationName}`) || destinationName;
        else destinationName = (targetScene && lang.str(`locations.${targetScene}`)) || '';

        // If there is still no name, create one from the target scene
        if (!destinationName && targetScene) {
            // Convert camelCase to Title Case with spaces
            destinationName = targetScene
                .replace(/([A-Z])/g, ' $1') // Insert a space before all capital letters
                .replace(/^./, str => str.toUpperCase()) // Capitalize the first letter
                .replace(/Scene$/, '') // Remove 'Scene' suffix if present
                .trim();
        }
        // If we still don't have a name (unlikely), use a generic one based on direction
        if (!destinationName) {
            const directionNames = {
                'up': 'Go Up',
                'down': 'Go Down',
                'left': 'Go Left',
                'right': 'Go Right'
            };
            destinationName = directionNames[direction] || 'Exit';
        }
        return destinationName;
    }

    /**
     * An exit painted in the background -- a door, a flight of stairs, a hatch -- as a hotspot of its own shape that
     * lights up whole on hover (a warm wash and its outline, the label above it) instead of the arrow-and-glow of
     * createTransitionZone. Canvas coordinates (not the 800 layout). `shape`: { rect: [x, y, w, h] } or
     * { points: [[x, y], ...] }. Clicking walks the priest to (walkX, walkY) and leaves for `target`, unless `onClick`
     * takes over (e.g. a staircase inside the same scene). `label` may be a function (read on each hover).
     * @returns {Phaser.GameObjects.Zone}
     */
    createDoorZone(shape, { target = null, walkX, walkY, label = '', direction = 'up', onClick = null, depth = 3, options = {} } = {}) {
        const pts = shape.points
            || [[shape.rect[0], shape.rect[1]], [shape.rect[0] + shape.rect[2], shape.rect[1]],
                [shape.rect[0] + shape.rect[2], shape.rect[1] + shape.rect[3]], [shape.rect[0], shape.rect[1] + shape.rect[3]]];
        const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
        const bx = Math.min(...xs), by = Math.min(...ys), bw = Math.max(...xs) - bx, bh = Math.max(...ys) - by;
        if (isDemoClosed(target)) return this.createClosedExit({ x: bx, y: by, w: bw, h: bh }, target);

        // the hit area is the shape itself, in the zone's local space (its top-left corner)
        const zone = this.scene.add.zone(bx, by, bw, bh).setOrigin(0, 0).setDepth(10);
        zone.setInteractive({
            hitArea: new Phaser.Geom.Polygon(pts.map(([x, y]) => [x - bx, y - by]).flat()),
            hitAreaCallback: Phaser.Geom.Polygon.Contains,
            useHandCursor: true
        });

        // the highlight: a soft halo, a warm wash over the shape, a gold outline
        const flat = pts.map(([x, y]) => ({ x, y }));
        const glow = this.scene.add.graphics().setDepth(depth).setAlpha(0);
        glow.lineStyle(7, this.colors.glow, 0.16);
        glow.strokePoints(flat, true, true);
        glow.fillStyle(0xffe6a8, 0.14);
        glow.fillPoints(flat, true, true);
        glow.lineStyle(2, this.colors.hover, 0.9);
        glow.strokePoints(flat, true, true);

        const text = this.scene.add.text(0, 0, '', {
            fontSize: UI_SMALL, fill: EXIT_INK, align: 'center', fontFamily: UI_FONT, backgroundColor: LABEL_BG, padding: { x: 8, y: 4 }
        }).setOrigin(0.5, 1).setDepth(30).setAlpha(0);
        const W = this.scene.scale.width;
        zone.exitLabel = () => this.exitLabel(typeof label === 'function' ? label() : label, target, direction); // also for the hint lantern
        const placeLabel = () => {
            text.setText(zone.exitLabel());
            text.setPosition(Phaser.Math.Clamp(bx + bw / 2, text.width / 2 + 10, W - text.width / 2 - 10), Math.max(text.height + 10, by - 6));
        };
        placeLabel();

        let pulse = null;
        zone.on('pointerover', () => {
            placeLabel();
            this.scene.tweens.killTweensOf([glow, text]);
            this.scene.tweens.add({ targets: [glow, text], alpha: 1, duration: 180, ease: 'Sine.easeOut' });
            pulse = this.scene.tweens.add({ targets: glow, alpha: { from: 1, to: 0.65 }, duration: 700, delay: 180, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        });
        zone.on('pointerout', () => {
            pulse?.stop();
            this.scene.tweens.killTweensOf([glow, text]);
            this.scene.tweens.add({ targets: [glow, text], alpha: 0, duration: 200, ease: 'Sine.easeIn' });
        });
        zone.on('pointerdown', (pointer, localX, localY, event) => {
            event.stopPropagation(); // the click is the exit's, not a walk to that spot
            if (onClick) onClick();
            else if (target) this.handleSceneTransition(target, walkX, walkY, options);
        });

        this.transitionElements.push({ zone, elements: { arrowContainer: glow, textContainer: text } });
        return zone;
    }

    /**
     * An exit that isn't a door -- a street going on past the edge of the picture, a road into the distance -- as a
     * stretch of the scene that lights up on hover: a warm wash over the `points` polygon (canvas coords), soft at its
     * edges, brightening toward `toward` ([x, y], where the way leads), and the label
     * at that end. No arrow, no circle. Clicking walks the priest to (walkX, walkY) and leaves for `target`.
     * `edge` ('left' | 'right'): the way leaves by that screen edge, so the arrow keys take it too.
     * @returns {Phaser.GameObjects.Zone}
     */
    createPathZone(points, { toward, target, walkX, walkY, label = '', direction = 'up', edge = null, onClick = null, depth = 3, options = {} } = {}) {
        const sc = this.scene, W = sc.scale.width;
        const xs = points.map(p => p[0]), ys = points.map(p => p[1]);
        const bx = Math.min(...xs), by = Math.min(...ys), bw = Math.max(...xs) - bx, bh = Math.max(...ys) - by;
        if (isDemoClosed(target)) return this.createClosedExit({ x: bx, y: by, w: bw, h: bh }, target);

        const zone = sc.add.zone(bx, by, bw, bh).setOrigin(0, 0).setDepth(10);
        zone.setInteractive({
            hitArea: new Phaser.Geom.Polygon(points.map(([x, y]) => [x - bx, y - by]).flat()),
            hitAreaCallback: Phaser.Geom.Polygon.Contains,
            useHandCursor: true
        });

        // the shared texture: a ramp (faint → white along x). (A bump of light flowing along it went, 2026-11-25: the user
        // saw it as a darker band flying about; the steady light stays.)
        const ensure = (key, w, h, draw) => {
            if (!sc.textures.exists(key)) { const t = sc.textures.createCanvas(key, w, h); draw(t.getContext(), w, h); t.refresh(); }
            return key;
        };
        const ramp = ensure('exitRamp', 256, 4, (c, w, h) => {
            const g = c.createLinearGradient(0, 0, w, 0);
            g.addColorStop(0, 'rgba(255,255,255,0.18)'); g.addColorStop(0.5, 'rgba(255,255,255,0.55)'); g.addColorStop(1, 'rgba(255,255,255,1)');
            c.fillStyle = g; c.fillRect(0, 0, w, h);
        });
        // the stretch's own soft-edged mask (the polygon, blurred), once per shape
        const PAD = 14;
        const maskKey = `exitMask_${points.flat().join('_')}`;
        ensure(maskKey, Math.ceil(bw + 2 * PAD), Math.ceil(bh + 2 * PAD), (c) => {
            c.filter = 'blur(10px)';
            c.fillStyle = '#ffffff';
            c.beginPath();
            points.forEach(([x, y], i) => (i ? c.lineTo(x - bx + PAD, y - by + PAD) : c.moveTo(x - bx + PAD, y - by + PAD)));
            c.closePath();
            c.fill();
        });
        const mask = sc.make.image({ x: bx - PAD, y: by - PAD, key: maskKey, add: false }).setOrigin(0).createBitmapMask();

        // along the way: from the polygon's near end to its far end (projected onto the direction to `toward`)
        const cx = xs.reduce((a, b) => a + b, 0) / xs.length, cy = ys.reduce((a, b) => a + b, 0) / ys.length;
        const ang = Math.atan2(toward[1] - cy, toward[0] - cx), ux = Math.cos(ang), uy = Math.sin(ang);
        const along = points.map(([x, y]) => (x - cx) * ux + (y - cy) * uy), across = points.map(([x, y]) => -(x - cx) * uy + (y - cy) * ux);
        const a0 = Math.min(...along) - PAD, a1 = Math.max(...along) + PAD;
        const thick = Math.max(...across) - Math.min(...across) + 2 * PAD, len = a1 - a0;
        const at = (t) => ({ x: cx + ux * (a0 + t * len), y: cy + uy * (a0 + t * len) });
        const mid = at(0.5);
        const wash = sc.add.image(mid.x, mid.y, ramp).setDisplaySize(len, thick).setRotation(ang)
            .setTint(0xffb54a).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0).setDepth(depth).setMask(mask);

        // the label at the far end (a side exit: by its edge, with a ‹ / › for the way)
        const text = sc.add.text(0, 0, '', {
            fontSize: UI_SMALL, fill: EXIT_INK, align: 'center', fontFamily: UI_FONT, backgroundColor: LABEL_BG, padding: { x: 8, y: 4 }
        }).setOrigin(0.5, 1).setDepth(30).setAlpha(0);
        zone.exitLabel = () => this.exitLabel(typeof label === 'function' ? label() : label, target, direction); // also for the hint lantern
        const placeLabel = () => {
            const name = zone.exitLabel();
            text.setText(edge === 'left' ? `‹ ${name}` : edge === 'right' ? `${name} ›` : name);
            const end = at(0.86);
            const lx = edge === 'left' ? bx + text.width / 2 + 8 : edge === 'right' ? bx + bw - text.width / 2 - 8 : end.x;
            const ly = edge ? by + bh * 0.42 : Math.min(end.y, by + bh) - 8;
            text.setPosition(Phaser.Math.Clamp(lx, text.width / 2 + 10, W - text.width / 2 - 10), Math.max(text.height + 10, ly));
        };
        placeLabel();

        zone.on('pointerover', () => {
            placeLabel();
            sc.tweens.killTweensOf([wash, text]);
            sc.tweens.add({ targets: wash, alpha: 0.5, duration: 260, ease: 'Sine.easeOut' });
            sc.tweens.add({ targets: text, alpha: 1, duration: 180, ease: 'Sine.easeOut' });
        });
        zone.on('pointerout', () => {
            sc.tweens.killTweensOf([wash, text]);
            sc.tweens.add({ targets: [wash, text], alpha: 0, duration: 220, ease: 'Sine.easeIn' });
        });
        zone.on('pointerdown', (pointer, localX, localY, event) => {
            event.stopPropagation();
            if (onClick) onClick();
            else if (target) this.handleSceneTransition(target, walkX, walkY, options);
        });

        if (edge && sc.registerEdgeExit) {
            sc.registerEdgeExit(edge, () => {
                const pr = sc.priest;
                if (!pr) { this.handleSceneTransition(target, walkX, walkY, options); return; }
                this.handleSceneTransition(target, pr.x + (edge === 'left' ? -70 : 70), pr.y, options);
            }, zone, [by, by + bh]);
        }
        this.transitionElements.push({ zone, elements: { arrowContainer: wash, textContainer: text, tweens: [] } });
        sc.events.once('shutdown', () => { mask.destroy?.(); });
        return zone;
    }

    /**
     * A side exit: the stretch of the scene by the left / right edge (`width` px in from it, from `top` down to the
     * bottom), lit as createPathZone, the way leading out by that edge.
     */
    createEdgeExit(side, { target, walkX, walkY, label = '', width = 150, top = 230, bottom = null, options = {}, onClick = null } = {}) {
        const W = this.scene.scale.width, H = this.scene.scale.height, b = bottom ?? H;
        const x0 = side === 'left' ? 0 : W - width, x1 = side === 'left' ? width : W;
        return this.createPathZone([[x0, top], [x1, top], [x1, b], [x0, b]], {
            toward: [side === 'left' ? 0 : W, (top + b) / 2], target, walkX, walkY, label, direction: side, edge: side, options, onClick
        });
    }

    /**
     * DEMO_BUILD: an exit into a place outside the demo. Cones stand in it; the hover says it's closed and a click makes
     * the priest remark on it instead of leaving. No arrow-key edge exit. `r` = the exit's rect in canvas coords.
     */
    createClosedExit(r, targetScene) {
        const zone = this.scene.add.zone(r.x, r.y, r.w, r.h).setOrigin(0, 0).setDepth(10).setInteractive({ useHandCursor: true });
        zone.destinationName = demoClosedLabel();                       // the hint lantern labels it too
        const cones = placeDemoCones(this.scene, this.scene.scene.key, targetScene, r.x + r.w / 2, Math.min(r.y + r.h, 560), r.w);
        const top = Math.min(r.y, ...cones.map(c => c.y - c.displayHeight));
        const text = this.scene.add.text(r.x + r.w / 2, Math.max(24, top - 6), zone.destinationName, {
            fontSize: UI_SMALL, fill: '#ffd7a8', align: 'center', fontFamily: UI_FONT, backgroundColor: LABEL_BG, padding: { x: 8, y: 4 }
        }).setOrigin(0.5, 1).setDepth(30).setAlpha(0);
        zone.on('pointerover', () => text.setAlpha(1));
        zone.on('pointerout', () => text.setAlpha(0));
        zone.on('pointerdown', (pointer, localX, localY, event) => {
            event.stopPropagation();
            sayDemoClosed(this.scene);
        });
        this.transitionElements.push({ zone, elements: { textContainer: text } });
        return zone;
    }

    /**
     * Handle scene transition with consistent behavior
     * @param {string} targetScene - Target scene key
     * @param {number} walkX - X position to walk to before transition
     * @param {number} walkY - Y position to walk to before transition
     * @param {Object} options - Additional options for the transition
     */
    handleSceneTransition(targetScene, walkX, walkY, options = {}) {
        // Prevent multiple transitions
        if (this.scene.isTransitioning) return;
        if (isDemoClosed(targetScene)) { sayDemoClosed(this.scene); return; }   // a custom hotspot into a closed place
        this.scene.isTransitioning = true;
        
        // Merge options with defaults
        const settings = {
            ...this.defaultSettings,
            ...options
        };
        
        // Get the priest character
        const priest = this.scene.priest;
        
        // If priest doesn't exist, just transition immediately
        if (!priest) {
            this.directTransition(targetScene, settings.fadeOutDuration);
            return;
        }
        
        // Create a variable to track if the tween completed
        let tweenCompleted = false;
        
        // Play walk animation
        if (priest.anims && this.scene.anims.exists('walk')) {        // (the game's animation, not the sprite's own)
            priest.play('walk', true);
        }
        
        // Kill any existing tweens
        this.scene.tweens.killTweensOf(priest);

        // he faces the way he walks (he used to back out of a room toward a door behind him)
        if (Math.abs(walkX - priest.x) > 4) {
            const k = Math.abs(priest.scaleY) || 1, d = walkX < priest.x ? -1 : 1;
            priest.setScale(d * k, k);
            this.scene.priestGlow?.setScale(d * 1.05 * k, 1.05 * k);
        }
        
        // Calculate distance and duration
        const distance = Phaser.Math.Distance.Between(priest.x, priest.y, walkX, walkY);
        const duration = Math.max(settings.minWalkDuration, distance * settings.walkSpeedFactor);
        
        // Create the movement tween
        this.scene.tweens.add({
            targets: priest,
            x: walkX,
            y: walkY,
            duration: duration,
            ease: 'Linear',
            onComplete: () => {
                tweenCompleted = true;
                
                // Play idle animation if it exists
                if (priest.anims && this.scene.anims.exists('idle')) {
                    priest.play('idle');
                }
                
                // Transition to the target scene
                this.directTransition(targetScene, settings.fadeOutDuration);
            }
        });
        
        // Add a safety timeout in case the tween doesn't complete
        this.scene.time.delayedCall(settings.safetyTimeout, () => {
            if (!tweenCompleted) {
                console.log(`Scene transition to ${targetScene} timed out, forcing transition`);
                
                // Play idle animation if it exists
                if (priest && priest.anims && this.scene.anims.exists('idle')) {
                    priest.play('idle');
                }
                
                // Force transition to the target scene
                this.directTransition(targetScene, settings.fadeOutDuration);
            }
        });
    }
    
    /**
     * Direct transition to target scene without character movement
     * @param {string} targetScene - Target scene key
     * @param {number} fadeOutDuration - Duration of fade out effect
     */
    directTransition(targetScene, fadeOutDuration = 800) {
        this.scene.cameras.main.fadeOut(fadeOutDuration, 0, 0, 0);
        this.scene.cameras.main.once('camerafadeoutcomplete', () => {
            // a shared soundtrack flows on into the next scene (GameScene.stopSoundsForTransition)
            if (this.scene.stopSoundsForTransition) this.scene.stopSoundsForTransition(targetScene);
            else this.scene.sound.stopAll();
            this.scene.scene.start(targetScene);
            this.scene.isTransitioning = false;
        });
    }

    addHoverEffect(zone, direction) {
        // Get screen dimensions for positioning calculations
        const screenWidth = this.scene.sys.game.config.width;
        const screenHeight = this.scene.sys.game.config.height;
        
        // Create a container for the arrow and glow
        const arrowContainer = this.scene.add.container(zone.x, zone.y);
        arrowContainer.setDepth(20);
        
        // Create a shadow for the arrow - initially invisible
        const arrowShadow = this.scene.add.sprite(3, 3, 'arrow')
            .setScale(1.0)
            .setTint(0x000000)
            .setAlpha(0) // Initially invisible
            .setDepth(19);
            
        // Create the arrow with enhanced appearance - initially invisible
        const arrow = this.scene.add.sprite(0, 0, 'arrow')
            .setScale(1.0)
            .setTint(0xFFD700) // Gold color
            .setAlpha(0) // Initially invisible
            .setDepth(20);
        
        // Add a glow effect behind the arrow - initially invisible
        const glow = this.scene.add.graphics();
        glow.fillStyle(0xFFF4BD, 0.4); // Gold glow
        glow.fillCircle(0, 0, 20);
        glow.setAlpha(0); // Initially invisible
        
        // Add elements to the arrow container
        arrowContainer.add([glow, arrowShadow, arrow]);
        
        // Set arrow and shadow rotation based on direction
        switch(direction) {
            case 'left': 
                arrow.setAngle(180); 
                arrowShadow.setAngle(180);
                break;
            case 'right': 
                arrow.setAngle(0); 
                arrowShadow.setAngle(0);
                break;
            case 'up': 
                arrow.setAngle(270); 
                arrowShadow.setAngle(270);
                break;
            case 'down': 
                arrow.setAngle(90); 
                arrowShadow.setAngle(90);
                break;
        }
        
        // Process the destination name
        let displayText = zone.destinationName;
        if (displayText.length > 15) {
            if (displayText.includes(' ')) {
                // Two lines, the words kept in order: break at the space that leaves the longer line shortest,
                // never before a dash ("Shed 521 —" / "Floors"). (Filling the shorter line word by word used to
                // reorder them: "Bouda 521 – patra" came out as "Bouda patra" / "521 –".)
                const words = displayText.split(' ');
                let best = null;
                for (let i = 1; i < words.length; i++) {
                    if (/^[–—-]$/.test(words[i])) continue;
                    const lines = [words.slice(0, i).join(' '), words.slice(i).join(' ')];
                    const longest = Math.max(lines[0].length, lines[1].length);
                    if (!best || longest <= best.longest) best = { lines, longest };   // a tie: the longer first line
                }
                if (best) displayText = best.lines.join('\n');
            } else {
                // Truncate if no spaces
                displayText = displayText.substring(0, 12) + '...';
            }
        }
        
        // Create a separate text container that's positioned independently
        // This is the key to solving the positioning issue
        const textContainer = this.scene.add.container(0, 0);
        textContainer.setDepth(30); // Above everything else
        
        // Create the text with background - initially invisible
        const text = this.scene.add.text(0, 0, displayText, {
            fontSize: UI_SMALL,
            fill: EXIT_INK,
            align: 'center',
            fontFamily: UI_FONT, backgroundColor: LABEL_BG,
            padding: { x: 8, y: 4 }
        }).setOrigin(0.5).setAlpha(0); // Initially invisible
        
        // Add text to its container
        textContainer.add(text);
        
        // Function to position text properly based on screen boundaries
        const positionText = () => {
            // Start with a position based on the arrow direction
            let textX = zone.x;
            let textY = zone.y ;
            
            // Position based on direction
            const offset = 50; // Distance from arrow
            textY = zone.y - offset;
            textX = zone.x - offset;

            // Check boundaries and adjust if needed
            const padding = 10; // Padding from screen edges
            const textWidth = text.width;
            const textHeight = text.height;
            
            // Check left edge
            if (textX - textWidth/2 < padding) {
                textX = padding + textWidth/2;
            }
            
            // Check right edge
            if (textX + textWidth/2 > screenWidth - padding) {
                textX = screenWidth - padding - textWidth/2;
            }
            
            // Check top edge
            if (textY - textHeight/2 < padding) {
                textY = padding + textHeight/2;
            }
            
            // Check bottom edge
            if (textY + textHeight/2 > screenHeight - padding) {
                textY = screenHeight - padding - textHeight/2;
            }
            
            // Update text container position
            textContainer.setPosition(textX, textY);
        };
        
        // Initial positioning
        positionText();
        
        // Store animation references but don't start them yet
        let arrowPulse = null;
        let shadowPulse = null;
        let glowPulse = null;
        
        // Add hover effects - show everything on hover
        zone.on('pointerover', () => {
            // Play sound if available
            if (this.scene.sound && this.scene.sound.get('hoverSound')) {
                this.scene.sound.play('hoverSound', { volume: 0.5 });
            }
            
            // Stop any existing animations
            this.scene.tweens.killTweensOf([arrow, arrowShadow, glow, text]);
            
            // Show and animate the arrow
            this.scene.tweens.add({
                targets: arrow,
                alpha: { from: 0, to: 1 }, // Fade in from invisible
                scale: { from: 0.8, to: 1.3 },
                duration: 300,
                ease: 'Back.easeOut'
            });
            
            // Show and animate the shadow with slight delay
            this.scene.tweens.add({
                targets: arrowShadow,
                alpha: { from: 0, to: 0.8 }, // Fade in from invisible
                scale: { from: 0.8, to: 1.3 },
                duration: 300,
                ease: 'Back.easeOut',
                delay: 50
            });
            
            // Show and animate the glow
            this.scene.tweens.add({
                targets: glow,
                alpha: { from: 0, to: 0.7 }, // Fade in from invisible
                scale: { from: 0.8, to: 1.3 },
                duration: 400,
                ease: 'Sine.easeOut'
            });
            
            // Start pulsating animations after initial appearance
            this.scene.time.delayedCall(300, () => {
                // Arrow pulsating
                const newArrowPulse = this.scene.tweens.add({
                    targets: arrow,
                    scale: { from: 1.2, to: 1.4 },
                    duration: 600,
                    ease: 'Sine.easeInOut',
                    yoyo: true,
                    repeat: -1
                });
                arrowPulse = newArrowPulse;
                
                // Shadow pulsating
                const newShadowPulse = this.scene.tweens.add({
                    targets: arrowShadow,
                    scale: { from: 1.2, to: 1.4 },
                    duration: 600,
                    ease: 'Sine.easeInOut',
                    yoyo: true,
                    repeat: -1,
                    delay: 100
                });
                shadowPulse = newShadowPulse;
                
                // Glow pulsating
                const newGlowPulse = this.scene.tweens.add({
                    targets: glow,
                    alpha: { from: 0.6, to: 0.9 },
                    scale: { from: 1.2, to: 1.4 },
                    duration: 800,
                    ease: 'Sine.easeInOut',
                    yoyo: true,
                    repeat: -1
                });
                glowPulse = newGlowPulse;
            });
            
            // Show and animate the text
            this.scene.tweens.add({
                targets: text,
                alpha: { from: 0, to: 1 }, // Fade in from invisible
                scale: { from: 0.8, to: 1.2 },
                duration: 400,
                ease: 'Back.easeOut'
            });
        });
        
        // Add pointer out effects - hide everything on pointer out
        zone.on('pointerout', () => {
            // Stop all tweens
            this.scene.tweens.killTweensOf([arrow, arrowShadow, glow, text]);
            
            if (arrowPulse && arrowPulse.stop) arrowPulse.stop();
            if (shadowPulse && shadowPulse.stop) shadowPulse.stop();
            if (glowPulse && glowPulse.stop) glowPulse.stop();
            
            // Fade out text
            this.scene.tweens.add({
                targets: text,
                alpha: 0, // Fade to invisible
                scale: 0.8,
                duration: 200,
                ease: 'Sine.easeIn'
            });
            
            // Fade out arrow
            this.scene.tweens.add({
                targets: arrow,
                alpha: 0, // Fade to invisible
                scale: 0.8,
                duration: 200,
                ease: 'Sine.easeIn'
            });
            
            // Fade out shadow
            this.scene.tweens.add({
                targets: arrowShadow,
                alpha: 0, // Fade to invisible
                scale: 0.8,
                duration: 200,
                ease: 'Sine.easeIn'
            });
            
            // Fade out glow
            this.scene.tweens.add({
                targets: glow,
                alpha: 0, // Fade to invisible
                scale: 0.8,
                duration: 300,
                ease: 'Sine.easeIn'
            });
        });
        
        // Add resize event listener to reposition text when the window is resized
        const resizeListener = () => positionText();
        window.addEventListener('resize', resizeListener);
        
        // Return all created elements for cleanup
        return {
            arrowContainer,
            textContainer,
            tweens: [], // We'll store tweens dynamically when they're created
            resizeListener,
            // Store references to add tweens later
            storeArrowPulse: (tween) => { arrowPulse = tween; },
            storeShadowPulse: (tween) => { shadowPulse = tween; },
            storeGlowPulse: (tween) => { glowPulse = tween; }
        };
    }
}
