import { notePlace } from '../utils/places.js';
import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { createAmbientNpc } from '../utils/AmbientNpc.js';

// The people on the floors: animated sheets (tools/artgen/floorsfolk.py, Aseprite ShedFloors_<id>) at their canvas
// anchors (feet, origin bottom-centre); the id is also the texture key; holds = each frame's hold time in ms,
// top = the figure's height in px, h = the frame height
const FLOORS_FOLK = [
    { id: 'floors_welcome_clerk', sheet: 'welcome_clerk', x: 260, y: 514, top: 111, h: 128, holds: [1100, 900, 200, 300, 160, 700, 600, 900] },
    { id: 'floors_dozer', sheet: 'dozer', x: 353, y: 498, top: 66, h: 80, holds: [1200, 1000, 1000, 1200, 1800, 300, 1500] },
    { id: 'floors_queue0', sheet: 'queue0', x: 595, y: 184, top: 114, h: 128, holds: [900, 700, 1100, 700, 800, 1000] },
    { id: 'floors_queue1', sheet: 'queue1', x: 626, y: 184, top: 108, h: 128, holds: [1000, 200, 240, 240, 1000, 1200] },
    { id: 'floors_queue2', sheet: 'queue2', x: 654, y: 184, top: 106, h: 128, holds: [1000, 1000, 1000, 1000, 1000, 1000] },
    { id: 'floors_queue3', sheet: 'queue3', x: 686, y: 184, top: 106, h: 128, holds: [1000, 1000, 1000, 1000, 1700, 800] },
];

// The three floors (canvas coords): the priest's feet line on each, and which floor a click belongs to (everything
// below a floor's slab is the floor beneath it)
const FLOOR_Y = [520, 340, 180];
const floorAt = y => (y >= 356 ? 0 : y >= 196 ? 1 : 2);

// The doors painted in the background (tools/artgen/floors_bg.py), each a hotspot of the door's own shape:
// floor, where the priest stands to go through, and where it leads
const DOORS = [
    { rect: [130, 392, 61, 122], floor: 0, x: 160, target: 'Shed521GateScene' },          // WELCOME, back to the gate
    { rect: [554, 387, 93, 126], floor: 0, x: 600, target: 'Shed521Scene', label: 'Exit' }, // EXIT, out to the yard
    { rect: [246, 228, 61, 112], floor: 1, x: 276, target: 'ShedAbandonedOfficeScene' },  // ASSESSMENTS
    { rect: [182, 68, 60, 112], floor: 2, x: 212, target: 'ShedRegistrationScene' },      // REGISTRATION
    { rect: [502, 69, 61, 111], floor: 2, x: 532, target: 'ShedApplicationsScene' },      // APPLICATIONS
];

// The ways between floors: both ends (feet, lower floor first) and the hotspot over the drawn stairs / ladder
const LINKS = [
    { floors: [0, 1], ends: [{ x: 785, y: 520 }, { x: 990, y: 340 }],                     // the stairs up from the ground floor
      points: [[762, 518], [806, 518], [1004, 350], [1004, 284], [762, 466]] },
    { floors: [0, 1], ends: [{ x: 531, y: 520 }, { x: 531, y: 340 }],                     // the ladder through the hatch
      points: [[509, 322], [553, 322], [553, 518], [509, 518]] },
    { floors: [1, 2], ends: [{ x: 1030, y: 340 }, { x: 880, y: 180 }],                    // the stairs up to the top floor
      points: [[1050, 344], [1050, 282], [882, 148], [856, 168], [856, 198]] },
];
const linkEnd = (link, floor) => link.ends[link.floors.indexOf(floor)];

// Coming back from a room, the priest stands at its door: [floor, x]
const ARRIVALS = {
    Shed521GateScene: [0, 160], Shed521Scene: [0, 600], ShedAbandonedOfficeScene: [1, 276],
    ShedRegistrationScene: [2, 212], ShedApplicationsScene: [2, 532],
};

export default class Shed521FloorsScene extends GameScene {
    constructor() {
        super({ key: 'Shed521FloorsScene' });
        this.isTransitioning = false; // Add flag to track transition state
        this.currentFloor = 0; // 0 ground, 1 first, 2 top
    }

    preload() {
        super.preload();
        this.preloadMusic('shedLoop');
        this.load.image('floors', 'assets/images/backgrounds/Shed521_floors.png');
        FLOORS_FOLK.forEach(({ id, sheet, h }) => {
            this.load.spritesheet(id, `assets/images/characters/shedfloors/${sheet}.png`, { frameWidth: 128, frameHeight: h });
        });
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        notePlace(this, 'place_shed_521');   // the journal's Places tab, on the first visit
        this.playSceneMusic('shedLoop', { resume: true });
        this._routeId = 0;  // the scene instance is re-used: a fresh route counter per visit

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // The priest comes in at the door he came through (the middle of the ground floor otherwise)
        const [floor, x] = ARRIVALS[this.enteredFrom] || [0, 533];
        this.currentFloor = floor;
        if (this.priest) {
            this.priest.x = x;
            this.priest.y = FLOOR_Y[floor];
            this.priest.setOrigin(0.5, 1);  // Ensure origin is at feet
            this.priest.play('idle');
        }

        // The bureau's three floors as a cut-away (native 1067×600: tools/artgen/floors_bg.py); the floor lines are
        // y 520 / 340 / 180 (the priest's feet), the doors and stairs sit where DOORS and LINKS say
        const bg = this.add.image(this.scale.width / 2, 300, 'floors');
        this.fitBackground(bg);
        bg.setDepth(-1);
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        // the WELCOME clerk, a dozer on the bench, the queue at APPLICATIONS: a click gets a line, not a dialog
        // (whatever stands in front of them -- the counter, the bench, the railing -- is cut out of their frames)
        this.floorsFolk = FLOORS_FOLK.map(cfg => createAmbientNpc(this, cfg));

        // Every door is clickable whole and lights up on hover; one on another floor is reached by the stairs first
        DOORS.forEach(door => {
            const zone = this.transitionManager.createDoorZone({ rect: door.rect }, {
                target: door.target, label: door.label, onClick: () => this.enterDoor(door)
            });
            // the arrow keys leave by the WELCOME door at the left edge of the ground floor, as before
            if (door.target === 'Shed521GateScene') {
                this.registerEdgeExit('left', () => this.leaveByEdge('left', door.target), zone, [FLOOR_Y[0] - 40, FLOOR_Y[0] + 40]);
            }
        });
        // ...and so are the stairs and the ladder: up or down, depending on where the priest stands
        LINKS.forEach(link => {
            this.transitionManager.createDoorZone({ points: link.points }, {
                label: () => (this.currentFloor <= link.floors[0] ? 'Upstairs' : 'Downstairs'),
                onClick: () => this.useLink(link)
            });
        });

        // At the foot or the top of the stairs the arrow keys ↑ / ↓ take them; a small hint shows which way
        const climbByKey = up => {
            if (this.isTransitioning || this.isInputBlocked() || !this.priest) return;
            const link = this.linkHere(this.currentFloor + (up ? 1 : -1));
            if (!link) return;
            this._routeId++;
            this.tweens.killTweensOf(this.priest);
            this.climb(link);
        };
        this.input.keyboard.on('keydown-UP', () => climbByKey(true));
        this.input.keyboard.on('keydown-DOWN', () => climbByKey(false));
        this.stairHint = this.add.text(0, 0, '', {
            fontSize: '16px', fontStyle: 'bold', fill: '#ffd700', backgroundColor: 'rgba(0, 0, 0, 0.55)', padding: { x: 5, y: 1 }
        }).setOrigin(0.5, 1).setDepth(30).setVisible(false);
    }

    /** A click on another floor: the priest takes the stairs (or the ladder) there and walks to the spot. */
    handleWalkClick(pointer) {
        if (this.isTransitioning) return true;                       // on the stairs: let him finish
        const floor = floorAt(pointer.y);
        if (floor === this.currentFloor) return false;               // the same floor: the usual walk
        this.goTo(floor, pointer.x);
        return true;
    }

    /** The link (stairs or ladder) to floor `to` whose end the priest stands at, if any. */
    linkHere(to) {
        return LINKS.find(l => l.floors.includes(this.currentFloor) && l.floors.includes(to)
            && Math.abs(linkEnd(l, this.currentFloor).x - this.priest.x) < 56);
    }

    /** Turn the priest (and his glow) left (-1) or right (1). */
    face(dir) {
        const k = this.priestScale || 1;
        this.priest.setScale(dir * k, k);
        this.priestGlow?.setScale(1.05 * dir * k, 1.05 * k);
    }

    /** Walk along the current floor to x (resolves on arrival; never if another walk or a panel cuts it short). */
    walkTo(x) {
        return new Promise(resolve => {
            const p = this.priest, move = this.playerMovementSystem;
            x = Phaser.Math.Clamp(x, 40, this.scale.width - 40);
            this.tweens.killTweensOf(p);
            const dist = Math.abs(x - p.x);
            if (dist < 3) { resolve(); return; }
            this.face(x < p.x ? -1 : 1);
            if (move) move.isTweenMoving = true;                    // a panel opening stops him (GameScene.createModalBlocker)
            p.play('walk', true);
            this.tweens.add({
                targets: p, x, duration: dist * 5 / (move?.speedMultiplier || 1), ease: 'Linear',
                onComplete: () => { if (move) move.isTweenMoving = false; p.play('idle', true); resolve(); }
            });
        });
    }

    /** Take a link from the current floor to its other end (keys and clicks wait meanwhile). */
    climb(link) {
        return new Promise(resolve => {
            const p = this.priest, move = this.playerMovementSystem;
            const from = this.currentFloor, to = link.floors[0] === from ? link.floors[1] : link.floors[0];
            const end = linkEnd(link, to);
            this.isTransitioning = true;
            if (end.x !== p.x) this.face(end.x < p.x ? -1 : 1);
            if (move) move.isTweenMoving = true;
            p.play('walk', true);
            this.tweens.add({
                targets: p, x: end.x, y: end.y, duration: Phaser.Math.Distance.Between(p.x, p.y, end.x, end.y) * 6, ease: 'Linear',
                onComplete: () => {
                    if (move) move.isTweenMoving = false;
                    this.currentFloor = to;
                    this.isTransitioning = false;
                    p.play('idle', true);
                    resolve();
                }
            });
        });
    }

    /** Go to floor `floor` (by the nearest stairs or ladder, floor by floor), walk to x there, then `then()`. */
    async goTo(floor, x, then) {
        const id = ++this._routeId;                                  // a newer route abandons this one
        while (this.currentFloor !== floor) {
            const next = this.currentFloor + (floor > this.currentFloor ? 1 : -1);
            const links = LINKS.filter(l => l.floors.includes(this.currentFloor) && l.floors.includes(next));
            const link = links.reduce((a, b) => (Math.abs(linkEnd(a, this.currentFloor).x - this.priest.x)
                <= Math.abs(linkEnd(b, this.currentFloor).x - this.priest.x) ? a : b));
            await this.walkTo(linkEnd(link, this.currentFloor).x);
            if (id !== this._routeId) return;
            await this.climb(link);
            if (id !== this._routeId) return;
        }
        await this.walkTo(x);
        if (id === this._routeId && then) then();
    }

    /** A click on the stairs / the ladder: up if he stands at or below its lower end, down otherwise. */
    useLink(link) {
        if (this.isTransitioning) return;
        const [lo, hi] = link.floors;
        const start = this.currentFloor <= lo ? lo : hi;
        this.goTo(start, linkEnd(link, start).x, () => { this._routeId++; this.climb(link); });
    }

    /** A click on a door: get to its floor and in front of it, then go through. */
    enterDoor(door) {
        if (this.isTransitioning) return;
        this.goTo(door.floor, door.x, () => {
            this.isTransitioning = true;
            this.priest.play('idle', true);
            this.transitionManager.directTransition(door.target);
        });
    }

    update() {
        super.update();

        // ↑ / ↓ over his head while he stands where the stairs or the ladder start
        if (this.stairHint && this.priest) {
            const up = !this.isTransitioning && this.linkHere(this.currentFloor + 1);
            const down = !this.isTransitioning && this.linkHere(this.currentFloor - 1);
            this.stairHint.setVisible(!!(up || down) && !this.isModalOpen());
            if (up || down) {
                this.stairHint.setText(up && down ? '↑ ↓' : up ? '↑' : '↓');
                this.stairHint.setPosition(this.priest.x, this.priest.y - this.priest.displayHeight - 4);
            }
        }
    }
}
