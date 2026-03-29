/**
 * MapUI.js
 * Fast travel map of Upper Morkezela. Shows visited locations as clickable nodes.
 */
export default class MapUI {
    constructor(scene) {
        this.scene = scene;
        this.visible = false;

        // Visited scenes persisted in registry
        if (!this.scene.registry.get('visitedScenes')) {
            this.scene.registry.set('visitedScenes', []);
        }

        // Mark current scene as visited
        this.markVisited(this.scene.scene.key);

        // Map location definitions — x,y are relative to container center (0,0)
        // Container is at (400,300) so these map onto an 800x600 canvas
        this.locations = [
            // --- Upper cluster ---
            { key: 'SkyshipBoardScene',        name: 'Skyship Verdigrace', x: 0,    y: -230 },
            { key: 'CrossroadScene',           name: 'Crossroads',        x: 0,    y: -120 },
            { key: 'EggCatedralScene',         name: 'Egg Cathedral',     x: 120,  y: -50 },
            { key: 'VoxMarket',                name: 'Voxmarket',         x: 230,  y: -120 },

            // --- Scraper cluster ---
            { key: 'ScraperScene',             name: 'Scraper 1140',      x: 0,    y: -10 },
            { key: 'ScraperAmbraScene',        name: 'Dr. Elphi\'s Studio', x: -100, y: 50 },
            { key: 'RustDomainScene',          name: 'Rust Domain',       x: 100,  y: 50 },
            { key: 'AbandonedBusScene',        name: 'Abandoned Bus',     x: 190,  y: 10 },

            // --- Shed 521 cluster ---
            { key: 'Shed521Scene',             name: 'Shed 521',          x: -230, y: -120 },
            { key: 'ShedCourtyard',             name: 'Shed Courtyard',    x: -280, y: 0 },
            { key: 'ShedHallScene',            name: 'Shed Hall',         x: -310, y: 80 },

            // --- Town cluster ---
            { key: 'TownSquareScene',          name: 'Town Square',       x: -100, y: 140 },
            { key: 'TownhallScene',            name: 'Townhall',          x: -100, y: 210 },
            { key: 'LumenDirectorateScene',    name: 'Lumen Directorate', x: -220, y: 160 },
            { key: 'BurningBearStreetScene',   name: 'Burning Bear St.',  x: 20,   y: 210 },
            { key: 'ScreamingCorkScene',       name: 'Screaming Cork',    x: 160,  y: 210 },

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
            ['ScraperScene', 'ScraperAmbraScene'],
            ['ScraperScene', 'RustDomainScene'],
            ['ScraperScene', 'AbandonedBusScene'],
            ['Shed521Scene', 'ShedCourtyard'],
            ['ShedCourtyard', 'ShedHallScene'],
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
        return visited.includes(sceneKey);
    }

    createUI() {
        this.container = this.scene.add.container(400, 300);
        this.container.setDepth(1000);
        this.container.visible = false;
        this.container.setScrollFactor(0);

        // Dark background
        const bg = this.scene.add.graphics();
        bg.fillStyle(0x0a1a12, 0.95);
        bg.fillRect(-400, -300, 800, 600);
        bg.lineStyle(2, 0x2a623d);
        bg.strokeRect(-400, -300, 800, 600);
        this.container.add(bg);

        // Title
        const title = this.scene.add.text(0, -270, 'UPPER MORKEZELA', {
            fontSize: '28px',
            fontFamily: 'Georgia',
            color: '#7fff8e',
            align: 'center'
        }).setOrigin(0.5);
        this.container.add(title);

        const subtitle = this.scene.add.text(0, -245, 'Fast Travel Map', {
            fontSize: '14px',
            fontFamily: 'Georgia',
            color: '#4a9e5c',
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

        // Fungal corner decorations
        this.addCornerDecoration(-380, -280);
        this.addCornerDecoration(360, -280);
        this.addCornerDecoration(-380, 270);
        this.addCornerDecoration(360, 270);

        // Draw connection lines
        this.linesGraphics = this.scene.add.graphics();
        this.container.add(this.linesGraphics);

        // Create location nodes (stored for refresh)
        this.nodeObjects = [];
        this.drawMap();

        // Legend
        const legendY = 260;
        const visitedDot = this.scene.add.circle(-100, legendY, 5, 0x7fff8e);
        const visitedLabel = this.scene.add.text(-90, legendY, 'Visited', {
            fontSize: '12px', fontFamily: 'Georgia', color: '#7fff8e'
        }).setOrigin(0, 0.5);
        const unvisitedDot = this.scene.add.circle(0, legendY, 5, 0x333333);
        const unvisitedLabel = this.scene.add.text(10, legendY, 'Undiscovered', {
            fontSize: '12px', fontFamily: 'Georgia', color: '#555555'
        }).setOrigin(0, 0.5);
        const currentDot = this.scene.add.circle(120, legendY, 5, 0xffd700);
        const currentLabel = this.scene.add.text(130, legendY, 'You are here', {
            fontSize: '12px', fontFamily: 'Georgia', color: '#ffd700'
        }).setOrigin(0, 0.5);
        this.container.add([visitedDot, visitedLabel, unvisitedDot, unvisitedLabel, currentDot, currentLabel]);

        // Hint text
        const hint = this.scene.add.text(0, 280, 'Click a visited location to fast travel  •  Press M or ESC to close', {
            fontSize: '11px', fontFamily: 'Georgia', color: '#4a9e5c', align: 'center'
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

        // Draw connection lines
        for (const [a, b] of this.connections) {
            const la = locMap.get(a);
            const lb = locMap.get(b);
            if (!la || !lb) continue;

            const aVisited = this.isVisited(a);
            const bVisited = this.isVisited(b);

            if (aVisited && bVisited) {
                this.linesGraphics.lineStyle(1.5, 0x2a623d, 0.7);
            } else {
                this.linesGraphics.lineStyle(1, 0x1a1a1a, 0.4);
            }
            this.linesGraphics.beginPath();
            this.linesGraphics.moveTo(la.x, la.y);
            this.linesGraphics.lineTo(lb.x, lb.y);
            this.linesGraphics.strokePath();
        }

        // Draw location nodes
        for (const loc of this.locations) {
            const visited = this.isVisited(loc.key);
            const isCurrent = loc.key === currentScene;

            // Node circle
            const radius = isCurrent ? 10 : 7;
            let color;
            if (isCurrent) {
                color = 0xffd700;
            } else if (visited) {
                color = 0x7fff8e;
            } else {
                color = 0x333333;
            }

            const circle = this.scene.add.circle(loc.x, loc.y, radius, color);
            circle.setAlpha(visited || isCurrent ? 1 : 0.4);
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
            const labelColor = isCurrent ? '#ffd700' : visited ? '#7fff8e' : '#555555';
            const label = this.scene.add.text(loc.x, loc.y + (radius + 8), loc.name, {
                fontSize: '10px',
                fontFamily: 'Georgia',
                color: labelColor,
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
        this.scene.showNotification(`Traveling to ${locationName}...`);
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
