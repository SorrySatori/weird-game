/**
 * MapUI.js
 * Fast travel map of Upper Morkezela. Shows visited locations as clickable nodes.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { isDemoClosed } from '../utils/demo.js';

export default class MapUI {
    constructor(scene) {
        this.scene = scene;
        this.visible = false;
        this.lang = LanguageSystem.getInstance();

        // Visited scenes persisted in registry
        if (!this.scene.registry.get('visitedScenes')) {
            this.scene.registry.set('visitedScenes', []);
        }

        // Mark current scene as visited
        this.markVisited(this.scene.scene.key);

        // Map location definitions: x,y are relative to the container centre (scale.width/2, 300), i.e. the 1067x600
        // hand-drawn map minus (533.5, 300). One node per place on the map: `inside` lists the scenes within it (floors,
        // rooms, the yard), which count as a visit and show "you are here" there; fast travel always goes to `key`.
        // Each node sits on the doorstep of its drawing (tools/artgen/handmap.py, NODES): keep them in sync.
        this.locations = [
            // --- the user's sketch: the upper town ---
            { key: 'SkyshipBoardScene',        name: 'Skyship Verdigrace', x: -104, y: -226 },
            { key: 'CrossroadScene',           name: 'Crossroads',        x: -109, y: -115 },
            { key: 'Shed521Scene',             name: 'Shed 521',          x: -439, y: -106,
              inside: ['Shed521GateScene', 'ShedCourtyard', 'ShedHallScene', 'ShedRegistrationScene', 'ShedApplicationsScene',
                       'Shed521FloorsScene', 'ShedAbandonedOfficeScene'] },
            { key: 'VoxMarket',                name: 'Voxmarket',         x: 70,   y: -122,
              inside: ['VoxmarketMarketScene', 'VoxmarketHallScene'] },
            // Dr. Elphi's studio and the Rust Domain are floors of the tower
            { key: 'ScraperScene',             name: 'Scraper 1140',      x: -148, y: 67,
              inside: ['ScraperInteriorScene', 'ScraperAmbraScene', 'RustDomainScene', 'ScraperCellarScene', 'ScraperBackyardScene'] },
            { key: 'EggCatedralScene',         name: 'Egg Cathedral',     x: 88,   y: 4,
              inside: ['CathedralEntrance', 'EggCathedralInteriorScene', 'EggCathedralStudyScene'] },
            { key: 'AbandonedBusScene',        name: 'Abandoned Bus',     x: 222,  y: 70 },

            // --- the lower town ---
            { key: 'LumenDirectorateScene',    name: 'Lumen Directorate', x: -438, y: 60,
              inside: ['LumenDirectorateInteriorScene'] },
            { key: 'TownhallScene',            name: 'Townhall',          x: -164, y: 228,
              inside: ['TownhallInteriorScene', 'PithReclaimersRoomScene'] },
            { key: 'TownSquareScene',          name: 'Town Square',       x: -282, y: 178 },
            { key: 'GodgraveyardScene',        name: 'Godgraveyard',      x: -465, y: 206 },
            { key: 'BurningBearStreetScene',   name: 'Burning Bear St.',  x: -84,  y: 212 },
            { key: 'ScreamingCorkScene',       name: 'Screaming Cork',    x: 111,  y: 241,
              inside: ['ScreamingCorkInteriorScene', 'ScreamingCorkClubScene'] },

            // --- the coast ---
            { key: 'HarborScene',              name: 'Harbor',            x: 315,  y: 206 },
            { key: 'EchoDrainDeltaScene',      name: 'Echo Drain Delta',  x: 333,  y: -42 },
            { key: 'RedmassIslandScene',       name: 'Redmass Island',    x: 471,  y: 152 },
        ];

        // Connections between locations (for drawing lines): the real exits of the scenes (scenes/*.js), which the
        // drawn roads follow too
        this.connections = [
            ['SkyshipBoardScene', 'CrossroadScene'],
            ['CrossroadScene', 'VoxMarket'],
            ['CrossroadScene', 'Shed521Scene'],
            ['CrossroadScene', 'EggCatedralScene'],
            ['CrossroadScene', 'ScraperScene'],
            ['ScraperScene', 'AbandonedBusScene'],
            ['TownSquareScene', 'TownhallScene'],
            ['TownSquareScene', 'HarborScene'],
            ['TownSquareScene', 'LumenDirectorateScene'],
            ['TownSquareScene', 'GodgraveyardScene'],
            ['TownhallScene', 'BurningBearStreetScene'],
            ['BurningBearStreetScene', 'ScreamingCorkScene'],
            ['HarborScene', 'EchoDrainDeltaScene'],
            ['EchoDrainDeltaScene', 'RedmassIslandScene'],
            // Town connects to Scraper area
            ['BurningBearStreetScene', 'ScraperScene'],
        ];

        this.createUI();
    }

    markVisited(sceneKey) {
        const visited = this.scene.registry.get('visitedScenes') || [];
        if (!visited.includes(sceneKey)) {
            visited.push(sceneKey);
            this.scene.registry.set('visitedScenes', visited);
        }
    }

    isVisited(sceneKey) {
        if (isDemoClosed(sceneKey)) return false;   // the demo build: places outside it never show up (an old save may know them)
        const visited = this.scene.registry.get('visitedScenes') || [];
        const loc = this.locations.find(l => l.key === sceneKey);
        return [sceneKey, ...(loc?.inside || [])].some(k => visited.includes(k));
    }

    isHere(loc, sceneKey) {
        return loc.key === sceneKey || !!loc.inside?.includes(sceneKey);
    }

    createUI() {
        this.container = this.scene.add.container(this.scene.scale.width / 2, 300);
        this.container.setDepth(1000);
        this.container.visible = false;
        this.container.setScrollFactor(0);

        // Dark background (backdrop / fallback behind the map image)
        const halfW = this.scene.scale.width / 2;
        const bg = this.scene.add.graphics();
        bg.fillStyle(0x0a1a12, 0.95);
        bg.fillRect(-halfW, -300, halfW * 2, 600);
        this.container.add(bg);

        // Map artwork: the hand-drawn map (tools/artgen/handmap.py), full screen, aligned with the node coordinates.
        // Its roads already follow this.connections, so the straight lines and corner fungi are skipped.
        this.hasMapArt = this.scene.textures.exists('mapBg');
        if (this.hasMapArt) {
            const mapImage = this.scene.add.image(0, 0, 'mapBg');
            mapImage.setDisplaySize(halfW * 2, 600);
            this.container.add(mapImage);
        } else {
            const frame = this.scene.add.graphics();
            frame.lineStyle(2, 0x2a623d);
            frame.strokeRect(-halfW, -300, halfW * 2, 600);
            this.container.add(frame);
        }

        // ink on paper over the drawing, the old green on the plain backdrop
        const st = this.style = this.hasMapArt
            ? { ink: '#2b2420', soft: '#5a4a3c', paper: '#efe8d6', hot: '#a8261c', visited: 0x2f4f7a, here: 0xb3261e, ring: 0xefe8d6 }
            : { ink: '#7fff8e', soft: '#4a9e5c', paper: '#0a0d08', hot: '#ffffff', visited: 0x7fff8e, here: 0xffd700, ring: 0x0a0d08 };
        const titleX = this.hasMapArt ? -halfW + 26 : 0;
        const titleOrigin = this.hasMapArt ? 0 : 0.5;

        // Title
        const title = this.scene.add.text(titleX, -270, this.lang.t('ui.mapTitle'), {
            fontSize: '28px',
            fontFamily: 'Georgia',
            color: st.ink,
            stroke: st.paper,
            strokeThickness: 4,
            align: 'center'
        }).setOrigin(titleOrigin, 0.5);
        this.container.add(title);

        const subtitle = this.scene.add.text(titleX + (this.hasMapArt ? 2 : 0), -245, this.lang.t('ui.mapSubtitle'), {
            fontSize: '14px',
            fontFamily: 'Georgia',
            fontStyle: this.hasMapArt ? 'italic' : 'normal',
            color: st.soft,
            stroke: st.paper,
            strokeThickness: 3,
            align: 'center'
        }).setOrigin(titleOrigin, 0.5);
        this.container.add(subtitle);

        // Close button
        const closeBtn = this.scene.add.text(halfW - 20, -280, 'X', {
            fontSize: '24px',
            fontFamily: 'Georgia',
            color: st.ink,
            stroke: st.paper,
            strokeThickness: 3
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });
        closeBtn.on('pointerover', () => closeBtn.setColor(st.hot));
        closeBtn.on('pointerout', () => closeBtn.setColor(st.ink));
        closeBtn.on('pointerdown', () => this.toggle());
        this.container.add(closeBtn);

        // Fungal corner decorations (the pixel map has its own riveted frame)
        if (!this.hasMapArt) {
            this.addCornerDecoration(-halfW + 20, -280);
            this.addCornerDecoration(halfW - 40, -280);
            this.addCornerDecoration(-halfW + 20, 270);
            this.addCornerDecoration(halfW - 40, 270);
        }

        // Draw connection lines
        this.linesGraphics = this.scene.add.graphics();
        this.container.add(this.linesGraphics);

        // Create location nodes (stored for refresh)
        this.nodeObjects = [];
        this.drawMap();

        // Legend (undiscovered places get no marker at all, so they need no legend entry)
        // (on the drawing: under the title, top left; on the plain backdrop: along the bottom)
        const legendY = this.hasMapArt ? -220 : 260;
        const lx = this.hasMapArt ? titleX + 6 : -80;
        const visitedDot = this.scene.add.circle(lx, legendY, 5, st.visited).setStrokeStyle(2, st.ring);
        const visitedLabel = this.scene.add.text(lx + 10, legendY, this.lang.t('ui.mapVisited'), {
            fontSize: '12px', fontFamily: 'Georgia', color: st.ink, stroke: st.paper, strokeThickness: 3
        }).setOrigin(0, 0.5);
        const cx = lx + 18 + visitedLabel.width + 16;
        const currentDot = this.scene.add.circle(cx, legendY, 5, st.here).setStrokeStyle(2, st.ring);
        const currentLabel = this.scene.add.text(cx + 10, legendY, this.lang.t('ui.mapYouAreHere'), {
            fontSize: '12px', fontFamily: 'Georgia', color: this.hasMapArt ? st.hot : '#ffd700', stroke: st.paper, strokeThickness: 3
        }).setOrigin(0, 0.5);
        this.container.add([visitedDot, visitedLabel, currentDot, currentLabel]);

        // Hint text
        const hint = this.scene.add.text(0, 287, this.lang.t('ui.mapHint'), {
            fontSize: '11px', fontFamily: 'Georgia', color: st.soft, stroke: st.paper, strokeThickness: 3, align: 'center'
        }).setOrigin(0.5);
        this.container.add(hint);
    }

    addCornerDecoration(x, y) {
        const dec = this.scene.add.graphics();
        dec.fillStyle(0x2a623d, 1);
        dec.fillCircle(x, y, 20);
        dec.fillStyle(0x7fff8e, 0.5);
        dec.fillCircle(x + 6, y - 4, 4);
        dec.fillCircle(x - 5, y + 6, 3);
        this.container.add(dec);
    }

    drawMap() {
        // Clear old nodes
        for (const obj of this.nodeObjects) {
            obj.destroy();
        }
        this.nodeObjects = [];
        this.linesGraphics.clear();

        const currentScene = this.scene.scene.key;
        const locMap = new Map(this.locations.map(l => [l.key, l]));

        // Draw connection lines (only over the plain backdrop; the map art draws the roads)
        for (const [a, b] of this.hasMapArt ? [] : this.connections) {
            const la = locMap.get(a);
            const lb = locMap.get(b);
            if (!la || !lb) continue;

            // a road to an undiscovered place would give it away
            if (!this.isVisited(a) || !this.isVisited(b)) continue;
            this.linesGraphics.lineStyle(1.5, 0x2a623d, 0.7);
            this.linesGraphics.beginPath();
            this.linesGraphics.moveTo(la.x, la.y);
            this.linesGraphics.lineTo(lb.x, lb.y);
            this.linesGraphics.strokePath();
        }

        // Draw location nodes — only where the player has been: an undiscovered place is just part of the drawing
        for (const loc of this.locations) {
            const visited = this.isVisited(loc.key);
            const isCurrent = this.isHere(loc, currentScene);
            if (!visited && !isCurrent) continue;

            // Node circle
            const st = this.style;
            const radius = isCurrent ? (this.hasMapArt ? 8 : 10) : (this.hasMapArt ? 6 : 7);
            const color = isCurrent ? st.here : st.visited;

            const circle = this.scene.add.circle(loc.x, loc.y, radius, color);
            circle.setStrokeStyle(2, st.ring);
            this.container.add(circle);
            this.nodeObjects.push(circle);

            // Pulsing glow for current location
            if (isCurrent) {
                const glow = this.scene.add.circle(loc.x, loc.y, 14, st.here, 0.3);
                this.container.add(glow);
                this.nodeObjects.push(glow);
                this.scene.tweens.add({
                    targets: glow,
                    alpha: { from: 0.3, to: 0.05 },
                    scaleX: { from: 1, to: 1.5 },
                    scaleY: { from: 1, to: 1.5 },
                    duration: 1200,
                    yoyo: true,
                    repeat: -1
                });
            }

            // Label
            const labelColor = isCurrent ? (this.hasMapArt ? st.hot : '#ffd700') : st.ink;
            const label = this.scene.add.text(loc.x, loc.y + radius + (this.hasMapArt ? 3 : 8), this.lang.t(`locations.${loc.key}`) || loc.name, {
                fontSize: this.hasMapArt ? '12px' : '10px',
                fontFamily: 'Georgia',
                fontStyle: this.hasMapArt ? 'bold' : 'normal',
                color: labelColor,
                stroke: st.paper,
                strokeThickness: this.hasMapArt ? 4 : 3,
                align: 'center'
            }).setOrigin(0.5, 0);
            this.container.add(label);
            this.nodeObjects.push(label);

            // Make visited (non-current) nodes clickable for fast travel
            if (visited && !isCurrent) {
                circle.setInteractive({ useHandCursor: true });
                label.setInteractive({ useHandCursor: true });

                const onOver = () => {
                    circle.setScale(1.4);
                    label.setColor(st.hot);
                };
                const onOut = () => {
                    circle.setScale(1);
                    label.setColor(st.ink);
                };
                const onClick = () => {
                    this.fastTravel(loc.key, loc.name);
                };

                circle.on('pointerover', onOver);
                circle.on('pointerout', onOut);
                circle.on('pointerdown', onClick);
                label.on('pointerover', onOver);
                label.on('pointerout', onOut);
                label.on('pointerdown', onClick);
            }
        }
    }

    fastTravel(sceneKey, locationName) {
        this.hide();
        const translatedName = this.lang.t(`locations.${sceneKey}`) || locationName;
        this.scene.showNotification(this.lang.t('ui.travelingTo', { location: translatedName }));
        // Short delay so notification is visible before transition
        this.scene.time.delayedCall(400, () => {
            this.scene.transitionToScene(sceneKey);
        });
    }

    toggle() {
        if (this.visible) {
            this.hide();
        } else {
            this.show();
        }
    }

    show() {
        // Refresh visited state and redraw
        this.markVisited(this.scene.scene.key);
        this.drawMap();
        this.container.visible = true;
        this.visible = true;
    }

    hide() {
        this.container.visible = false;
        this.visible = false;
    }
}
