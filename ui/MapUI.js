/**
 * MapUI.js
 * Fast travel map of Upper Morkezela. Shows visited locations as clickable nodes.
 */
import LanguageSystem from '../systems/LanguageSystem.js';

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

        // Map location definitions — x,y are relative to container center (0,0)
        // Container is at (400,300) so these map onto an 800x600 canvas.
        // One node per place on the map: `inside` lists the scenes within it (floors, rooms, the yard), which count as
        // a visit and show "you are here" there; fast travel always goes to `key`, the way in.
        // The pixel art (tools/artgen/map_bg.py, N) draws every landmark just above these coordinates — keep them in sync.
        this.locations = [
            // --- Upper cluster ---
            { key: 'SkyshipBoardScene',        name: 'Skyship Verdigrace', x: 0,    y: -195 },
            { key: 'CrossroadScene',           name: 'Crossroads',        x: 0,    y: -120 },
            { key: 'EggCatedralScene',         name: 'Egg Cathedral',     x: 120,  y: -50,
              inside: ['CathedralEntrance', 'EggCathedralInteriorScene', 'EggCathedralStudyScene'] },
            { key: 'VoxMarket',                name: 'Voxmarket',         x: 230,  y: -120,
              inside: ['VoxmarketMarketScene', 'VoxmarketHallScene'] },

            // --- Scraper cluster --- (Dr. Elphi's studio and the Rust Domain are floors of the tower)
            { key: 'ScraperScene',             name: 'Scraper 1140',      x: 0,    y: 20,
              inside: ['ScraperInteriorScene', 'ScraperAmbraScene', 'RustDomainScene', 'ScraperCellarScene', 'ScraperBackyardScene'] },
            { key: 'AbandonedBusScene',        name: 'Abandoned Bus',     x: 190,  y: 10 },

            // --- Shed 521: one walled compound ---
            { key: 'Shed521Scene',             name: 'Shed 521',          x: -240, y: -70,
              inside: ['Shed521GateScene', 'ShedCourtyard', 'ShedHallScene', 'ShedRegistrationScene', 'ShedApplicationsScene',
                       'Shed521FloorsScene', 'ShedAbandonedOfficeScene'] },

            // --- Town cluster ---
            { key: 'TownSquareScene',          name: 'Town Square',       x: -100, y: 140 },
            { key: 'TownhallScene',            name: 'Townhall',          x: -100, y: 210,
              inside: ['TownhallInteriorScene', 'PithReclaimersRoomScene'] },
            { key: 'LumenDirectorateScene',    name: 'Lumen Directorate', x: -220, y: 160,
              inside: ['LumenDirectorateInteriorScene'] },
            { key: 'BurningBearStreetScene',   name: 'Burning Bear St.',  x: 20,   y: 210 },
            { key: 'ScreamingCorkScene',       name: 'Screaming Cork',    x: 160,  y: 210,
              inside: ['ScreamingCorkInteriorScene', 'ScreamingCorkClubScene'] },

            // --- Harbor cluster ---
            { key: 'HarborScene',              name: 'Harbor',            x: 80,   y: 140 },
            { key: 'EchoDrainDeltaScene',      name: 'Echo Drain Delta',  x: 230,  y: 140 },
            { key: 'RedmassIslandScene',       name: 'Redmass Island',    x: 330,  y: 140 },
        ];

        // Connections between locations (for drawing lines)
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
            ['TownSquareScene', 'BurningBearStreetScene'],
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
        const bg = this.scene.add.graphics();
        bg.fillStyle(0x0a1a12, 0.95);
        bg.fillRect(-400, -300, 800, 600);
        this.container.add(bg);

        // Map artwork — aligns with the node coordinates below. Sits behind lines/nodes/labels.
        // Pixel art (tools/artgen/map_bg.py): its roads already follow this.connections and each
        // landmark stands just above its node, so the straight lines and corner fungi are skipped.
        this.hasMapArt = this.scene.textures.exists('mapBg');
        if (this.hasMapArt) {
            const mapImage = this.scene.add.image(0, 0, 'mapBg');
            mapImage.setDisplaySize(800, 600);
            this.container.add(mapImage);
        }

        // Border frame on top of the artwork
        const frame = this.scene.add.graphics();
        frame.lineStyle(2, 0x2a623d);
        frame.strokeRect(-400, -300, 800, 600);
        this.container.add(frame);

        // Title
        const title = this.scene.add.text(0, -270, this.lang.t('ui.mapTitle'), {
            fontSize: '28px',
            fontFamily: 'Georgia',
            color: '#7fff8e',
            stroke: '#0a0d08',
            strokeThickness: 4,
            align: 'center'
        }).setOrigin(0.5);
        this.container.add(title);

        const subtitle = this.scene.add.text(0, -245, this.lang.t('ui.mapSubtitle'), {
            fontSize: '14px',
            fontFamily: 'Georgia',
            color: '#4a9e5c',
            stroke: '#0a0d08',
            strokeThickness: 3,
            align: 'center'
        }).setOrigin(0.5);
        this.container.add(subtitle);

        // Close button
        const closeBtn = this.scene.add.text(380, -280, 'X', {
            fontSize: '24px',
            fontFamily: 'Georgia',
            color: '#7fff8e'
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });
        closeBtn.on('pointerover', () => closeBtn.setColor('#ffffff'));
        closeBtn.on('pointerout', () => closeBtn.setColor('#7fff8e'));
        closeBtn.on('pointerdown', () => this.toggle());
        this.container.add(closeBtn);

        // Fungal corner decorations (the pixel map has its own riveted frame)
        if (!this.hasMapArt) {
            this.addCornerDecoration(-380, -280);
            this.addCornerDecoration(360, -280);
            this.addCornerDecoration(-380, 270);
            this.addCornerDecoration(360, 270);
        }

        // Draw connection lines
        this.linesGraphics = this.scene.add.graphics();
        this.container.add(this.linesGraphics);

        // Create location nodes (stored for refresh)
        this.nodeObjects = [];
        this.drawMap();

        // Legend (undiscovered places get no marker at all, so they need no legend entry)
        const legendY = 260;
        const visitedDot = this.scene.add.circle(-80, legendY, 5, 0x7fff8e).setStrokeStyle(2, 0x0a0d08);
        const visitedLabel = this.scene.add.text(-70, legendY, this.lang.t('ui.mapVisited'), {
            fontSize: '12px', fontFamily: 'Georgia', color: '#7fff8e', stroke: '#0a0d08', strokeThickness: 3
        }).setOrigin(0, 0.5);
        const currentDot = this.scene.add.circle(30, legendY, 5, 0xffd700).setStrokeStyle(2, 0x0a0d08);
        const currentLabel = this.scene.add.text(40, legendY, this.lang.t('ui.mapYouAreHere'), {
            fontSize: '12px', fontFamily: 'Georgia', color: '#ffd700', stroke: '#0a0d08', strokeThickness: 3
        }).setOrigin(0, 0.5);
        this.container.add([visitedDot, visitedLabel, currentDot, currentLabel]);

        // Hint text
        const hint = this.scene.add.text(0, 280, this.lang.t('ui.mapHint'), {
            fontSize: '11px', fontFamily: 'Georgia', color: '#4a9e5c', stroke: '#0a0d08', strokeThickness: 3, align: 'center'
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
            const radius = isCurrent ? 10 : 7;
            const color = isCurrent ? 0xffd700 : 0x7fff8e;

            const circle = this.scene.add.circle(loc.x, loc.y, radius, color);
            circle.setStrokeStyle(2, 0x0a0d08);
            this.container.add(circle);
            this.nodeObjects.push(circle);

            // Pulsing glow for current location
            if (isCurrent) {
                const glow = this.scene.add.circle(loc.x, loc.y, 14, 0xffd700, 0.3);
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
            const labelColor = isCurrent ? '#ffd700' : '#7fff8e';
            const label = this.scene.add.text(loc.x, loc.y + (radius + 8), this.lang.t(`locations.${loc.key}`) || loc.name, {
                fontSize: '10px',
                fontFamily: 'Georgia',
                color: labelColor,
                stroke: '#0a0d08',
                strokeThickness: 3,
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
                    label.setColor('#ffffff');
                };
                const onOut = () => {
                    circle.setScale(1);
                    label.setColor('#7fff8e');
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
