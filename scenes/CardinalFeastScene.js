import JournalSystem from '../systems/JournalSystem.js';

/**
 * CardinalFeastScene — "The Cardinal Feast"
 *
 * The Bishop's reconstructed dream-cartridge, played on Day 2 at Dr. Elphi's
 * studio. A small TOP-DOWN, walkable RPG (Pokémon-style): you ARE Cardinal
 * Emils Ven and you walk the candlelit swamp-cathedral, talking to your flock.
 *
 * Beneath the dark comedy runs the séance: the NPCs remember the Bishop and
 * can't tell you apart from her. Asking after "your" journal leaks the Egg
 * Cathedral. After the feast resolves, the cartridge collapses into the
 * Infinite Fold — the last thing she saw before she died.
 *
 * Self-contained top-down movement + collision + proximity-talk + portrait
 * dialog, with a generative low-organ score. Emils uses the pixel-art portraits
 * (Emils1/2/3); other roles are drawn placeholders until art exists.
 */
export default class CardinalFeastScene extends Phaser.Scene {
    constructor() {
        super({ key: 'CardinalFeastScene' });
    }

    init(data) {
        this.returnScene = (data && data.returnScene) || 'ScraperAmbraScene';
        // Persistent feast/plot state.
        this.feast = {
            devotion: 0, suspicion: 0,
            sermonGiven: false, askedJournal: false, confessed: false,
            guestsTalked: {}, namedGuest: null, inquiryDone: false
        };
        this.learnedEggCathedral = false;
        this.talking = false;
        this._finished = false;
        this.room = null;
        this.activeNpc = null;
        this.path = null;         // click-to-move waypoint list (A* around obstacles)
        this.pendingNpc = null;   // npc/object to talk to on arrival
    }

    preload() {
        this.load.image('emils1', 'assets/images/characters/Emils1.png'); // reading (book)
        this.load.image('emils2', 'assets/images/characters/Emils2.png'); // toast (wine + crosier)
        this.load.image('emils3', 'assets/images/characters/Emils3.png'); // welcome (crosier)
        this.load.image('pimPortrait', 'assets/images/characters/Pim.png');
        this.load.image('vesperPortrait', 'assets/images/characters/inquisitor.png');
        this.load.image('marigoldPortrait', 'assets/images/characters/Marigold.png');
        this.load.image('corneliusPortrait', 'assets/images/characters/Cornelius.png');
        this.load.image('wrenPortrait', 'assets/images/characters/wren.png');
        this.load.image('gallowPortrait', 'assets/images/characters/gallow.png');
    }

    // Pixel-art used for both overworld tokens and dialog portraits (per role).
    // To add a character later: drop a PNG, load it above, add an entry here.
    artKey(roleId, override) {
        const ART = {
            cardinal: override || 'emils3',
            pim: 'pimPortrait',
            vesper: 'vesperPortrait',
            marigold: 'marigoldPortrait',
            cornelius: 'corneliusPortrait',
            wren: 'wrenPortrait',
            gallow: 'gallowPortrait'
        };
        const key = ART[roleId];
        return (key && this.textures.exists(key)) ? key : null;
    }

    create() {
        this.W = this.scale.width;
        this.H = this.scale.height;

        this.questSystem = this.registry.get('questSystem');
        this.journalSystem = JournalSystem.getInstance();
        if (this.journalSystem) this.journalSystem.scene = this;

        this.cameras.main.setBackgroundColor('#0b0a08');
        this.initMusic();

        // Input.
        this.cursors = this.input.keyboard.createCursorKeys();
        this.keys = this.input.keyboard.addKeys('W,A,S,D');
        this.interactKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
        this.interactKey2 = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.E);
        this.interactKey.on('down', () => this.onInteract());
        this.interactKey2.on('down', () => this.onInteract());
        this.input.on('pointerdown', (pointer) => this.onPointer(pointer));

        // Layers.
        this.roomLayer = this.add.container(0, 0).setDepth(0);
        this.actorLayer = this.add.container(0, 0).setDepth(10);
        this.uiLayer = this.add.container(0, 0).setDepth(100);
        this.dialogLayer = this.add.container(0, 0).setDepth(500);

        // Player avatar — Emils, scaled to an overworld token.
        this.player = this.add.image(400, 470, 'emils3').setOrigin(0.5, 0.92);
        this.player.setScale(72 / this.player.height);
        this.actorLayer.add(this.player);
        this.playerGlow = this.add.ellipse(400, 478, 60, 22, 0xffcf7a, 0.12);
        this.roomLayer.add(this.playerGlow);

        // Interaction hint.
        this.hint = this.add.text(0, 0, '▲ Space', {
            fontFamily: 'Georgia, serif', fontSize: '13px', color: '#ffe9ad',
            backgroundColor: 'rgba(10,8,6,0.7)', padding: { x: 5, y: 2 }
        }).setOrigin(0.5, 1).setVisible(false);
        this.uiLayer.add(this.hint);

        this.buildHud();

        this.cameras.main.fadeIn(800, 0, 0, 0);
        // Boot the cartridge, then drop into the nave.
        this.showBoot();
    }

    // =================================================================== music

    initMusic() {
        try {
            const AC = window.AudioContext || window['webkitAudioContext'];
            if (!AC) return;
            const ctx = this.actx = new AC();
            this.musicGain = ctx.createGain(); this.musicGain.gain.value = 0.0001; this.musicGain.connect(ctx.destination);
            this.musicFilter = ctx.createBiquadFilter(); this.musicFilter.type = 'lowpass'; this.musicFilter.frequency.value = 900; this.musicFilter.connect(this.musicGain);
            this.oscs = [];
            [73.42, 110.0, 146.83].forEach((f, i) => {
                const o = ctx.createOscillator(); o.type = i === 0 ? 'sine' : 'triangle'; o.frequency.value = f; o.detune.value = (i - 1) * 5;
                const g = ctx.createGain(); g.gain.value = 0.06; o.connect(g); g.connect(this.musicFilter); o.start();
                this.oscs.push({ o, g });
            });
            this.swell = ctx.createOscillator(); this.swell.frequency.value = 0.07;
            const swg = ctx.createGain(); swg.gain.value = 0.05; this.swell.connect(swg); swg.connect(this.musicGain.gain); this.swell.start();
            this.musicGain.gain.setValueAtTime(0.0001, ctx.currentTime);
            this.musicGain.gain.exponentialRampToValueAtTime(0.13, ctx.currentTime + 3.5);
            this.choralEvent = this.time.addEvent({ delay: 8500, loop: true, callback: () => this.playChoralNote() });
            this.resumeAudio();
        } catch (e) { /* best effort */ }
    }
    resumeAudio() { try { if (this.actx && this.actx.state === 'suspended') this.actx.resume(); } catch (e) { /* */ } }
    playChoralNote() {
        try {
            if (!this.actx || this._mood === 'glitch') return;
            const ctx = this.actx, t = ctx.currentTime, scale = [293.66, 349.23, 440.0, 587.33];
            const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = scale[Math.floor(Math.random() * scale.length)];
            const g = ctx.createGain(); g.gain.value = 0.0001; o.connect(g); g.connect(this.musicFilter); o.start(t);
            g.gain.exponentialRampToValueAtTime(0.035, t + 1.2); g.gain.exponentialRampToValueAtTime(0.0001, t + 3.4); o.stop(t + 3.6);
        } catch (e) { /* */ }
    }
    setMood(mood) {
        if (mood === this._mood || !this.actx) return; this._mood = mood;
        try {
            const t = this.actx.currentTime;
            if (mood === 'glitch') {
                this.musicFilter.frequency.linearRampToValueAtTime(260, t + 1.5);
                const det = [0, 30, -45]; this.oscs.forEach((o, i) => { o.o.detune.linearRampToValueAtTime(det[i] || 0, t + 1.2); o.g.gain.linearRampToValueAtTime(i === 0 ? 0.1 : 0.03, t + 1.2); });
            } else {
                this.musicFilter.frequency.linearRampToValueAtTime(mood === 'hall' ? 1100 : 850, t + 1.5);
                this.oscs.forEach((o, i) => { o.o.detune.linearRampToValueAtTime((i - 1) * 5, t + 1.2); o.g.gain.linearRampToValueAtTime(0.06, t + 1.2); });
            }
        } catch (e) { /* */ }
    }
    stopMusic() {
        try {
            if (this.choralEvent) { this.choralEvent.remove(); this.choralEvent = null; }
            if (this.actx) { const ctx = this.actx, t = ctx.currentTime; this.musicGain.gain.cancelScheduledValues(t); this.musicGain.gain.setValueAtTime(this.musicGain.gain.value, t); this.musicGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.7); setTimeout(() => { try { ctx.close(); } catch (e) { } }, 800); this.actx = null; }
        } catch (e) { /* */ }
    }

    // ============================================================ role/portrait

    role(id) {
        const R = {
            cardinal: { name: 'Cardinal Emils Ven', robe: 0x7a1530, trim: 0xc8a24a, skin: 0x8aa06a },
            pim: { name: 'Brother Pim', robe: 0x6b7f4a, trim: 0xcdbf8e, skin: 0x9bb56a },
            vesper: { name: 'Inquisitor Vesper Tann', robe: 0x24242c, trim: 0x9aa0ad, skin: 0x69745c },
            marigold: { name: 'Sister Marigold', robe: 0x8a6fae, trim: 0xe6d9a8, skin: 0x86996a },
            quill: { name: 'Old Mother Quill', robe: 0x5f5e59, trim: 0x9a9790, skin: 0x6f7a64, blind: true },
            gallow: { name: 'Gallow', robe: 0x352a22, trim: 0x7c7c7c, skin: 0x4f5a44 },
            cornelius: { name: 'Cornelius Brack', robe: 0xb98a2a, trim: 0xe2c66a, skin: 0x95a35a },
            wren: { name: 'Wren', robe: 0x6f9ec0, trim: 0xd7e6f0, skin: 0x90ad6c },
            otho: { name: 'Otho Pinescale', robe: 0x9a3b2a, trim: 0xe0a060, skin: 0xa6a85e },
            twins: { name: 'The Goodfennow Twins', robe: 0xc9c2d8, trim: 0xa99ec4, skin: 0x86996a },
            foyle: { name: 'Deacon Foyle', robe: 0x4a6b50, trim: 0xbfae6e, skin: 0x86a05f },
            system: { name: 'The Cardinal Feast', robe: 0x7a1530, trim: 0xc8a24a, skin: 0x7a1530 }
        };
        return R[id] || R.system;
    }

    // A small top-down token: robe body + head, in the room.
    makeToken(roleId) {
        const c = this.add.container(0, 0);
        const key = this.artKey(roleId);
        if (key) {
            // Use the pixel-art character, scaled to an overworld token (feet at origin).
            c.add(this.add.ellipse(0, 6, 38, 12, 0x000000, 0.3));
            const img = this.add.image(0, 10, key).setOrigin(0.5, 1);
            img.setScale(60 / img.height);
            c.add(img);
            c.artImage = img; // pixel-accurate hit target
            return c;
        }
        // Fallback: simple drawn token for roles without art yet.
        const r = this.role(roleId);
        const g = this.add.graphics();
        g.fillStyle(0x000000, 0.25); g.fillEllipse(0, 18, 34, 10);          // shadow
        g.fillStyle(r.robe, 1); g.fillEllipse(0, 4, 30, 40);                 // robe (top-down body)
        g.fillStyle(r.trim, 0.8); g.fillRect(-3, -8, 6, 24);                 // stole
        g.fillStyle(r.skin, 1); g.fillCircle(0, -16, 12);                    // head
        g.fillStyle(0x20281c, 1); g.fillCircle(-4, -16, 1.7); g.fillCircle(4, -16, 1.7); // eyes
        if (roleId === 'cardinal') { g.fillStyle(r.robe, 1); g.fillTriangle(-9, -22, 9, -22, 0, -38); g.lineStyle(2, r.trim, 0.9); g.lineBetween(0, -34, 0, -24); }
        c.add(g);
        return c;
    }

    // Dialog portrait: Emils uses the pixel art; others use a drawn bust.
    drawPortrait(roleId, x, y, size, portraitKey) {
        const cont = this.add.container(0, 0);
        const bg = this.add.graphics();
        bg.fillStyle(0x0a0806, 0.95); bg.fillRect(x, y, size, size);
        cont.add(bg);

        // Clip only the character art to the inner square (frame stays crisp).
        const mask = this.make.graphics({ add: false }); mask.fillStyle(0xffffff); mask.fillRect(x, y, size, size);

        // Use the role's pixel-art portrait if we have it (Emils picks a pose via
        // portraitKey); roles without art fall back to the drawn bust below.
        const imgKey = this.artKey(roleId, portraitKey);
        if (imgKey) {
            // Fit to the box width and anchor at the TOP so the head/mitre is the
            // visible part (the figures are full-body, ~2:3 portraits).
            const img = this.add.image(x + size / 2, y - 6, imgKey).setOrigin(0.5, 0);
            img.setScale(size / img.width);
            img.setMask(mask.createGeometryMask());
            cont.add(img);
        } else {
            const r = this.role(roleId), g = this.add.graphics();
            const cx = x + size / 2, by = y + size - 6, s = size / 150;
            g.fillStyle(r.robe, 1); g.fillTriangle(cx - 52 * s, by, cx + 52 * s, by, cx, by - 96 * s);
            g.fillStyle(r.trim, 0.85); g.fillTriangle(cx - 8 * s, by - 70 * s, cx + 8 * s, by - 70 * s, cx, by);
            g.fillStyle(r.skin, 1); g.fillEllipse(cx, by - 92 * s, 60 * s, 56 * s);                 // head
            g.fillTriangle(cx + 24 * s, by - 100 * s, cx + 70 * s, by - 86 * s, cx + 24 * s, by - 74 * s); // snout
            g.fillStyle(0x2a3322, 1); g.fillCircle(cx + 64 * s, by - 88 * s, 3 * s);
            if (r.blind) { g.lineStyle(3 * s, 0xcfcabf, 0.9); g.lineBetween(cx + 4 * s, by - 96 * s, cx + 20 * s, by - 96 * s); }
            else { g.fillStyle(0xfdf6e3, 1); g.fillCircle(cx + 18 * s, by - 98 * s, 8 * s); g.fillStyle(0x101010, 1); g.fillCircle(cx + 20 * s, by - 98 * s, 3.5 * s); }
            g.lineStyle(2 * s, 0x2a3322, 0.8); g.beginPath(); g.arc(cx + 30 * s, by - 82 * s, 14 * s, 0, Math.PI * 0.6); g.strokePath();
            g.setMask(mask.createGeometryMask());
            cont.add(g);
        }

        const frame = this.add.graphics();
        frame.lineStyle(2, 0xc8a24a, 0.9); frame.strokeRect(x, y, size, size);
        cont.add(frame);
        return cont;
    }

    // ===================================================================== HUD

    buildHud() {
        this.hudG = this.add.graphics(); this.uiLayer.add(this.hudG);
        this.hudDev = this.add.text(54, 8, '', { fontFamily: 'Georgia, serif', fontSize: '12px', color: '#cdbf8e' }); this.uiLayer.add(this.hudDev);
        this.hudSus = this.add.text(54, 28, '', { fontFamily: 'Georgia, serif', fontSize: '12px', color: '#cdbf8e' }); this.uiLayer.add(this.hudSus);
        this.refreshHud();
    }
    refreshHud() {
        const g = this.hudG; g.clear();
        g.fillStyle(0x140d0a, 0.85); g.fillRect(6, 4, 250, 44); g.lineStyle(1, 0xc8a24a, 0.7); g.strokeRect(6, 4, 250, 44);
        const dev = Math.max(0, Math.min(8, this.feast.devotion));
        const sus = Math.max(0, Math.min(8, this.feast.suspicion));
        this.hudDev.setText('DEVOTION'); this.hudSus.setText('SUSPICION').setColor(sus > 5 ? '#e0726a' : '#cdbf8e');
        for (let i = 0; i < 8; i++) {
            g.fillStyle(i < dev ? 0xffcf7a : 0x4a3a22, i < dev ? 0.95 : 0.5); g.fillEllipse(140 + i * 13, 14, 5, 10);
            g.fillStyle(i < sus ? 0xe0726a : 0x4a3a22, i < sus ? 0.95 : 0.5); g.fillEllipse(140 + i * 13, 34, 5, 10);
        }
    }

    // ================================================================== rooms

    clearRoom() {
        if (this._roomItems) this._roomItems.forEach(o => o.destroy());
        this._roomItems = [];
        if (this._beatTweens) this._beatTweens.forEach(t => t && t.stop());
        this._beatTweens = [];
        this.npcs = [];
        this.colliders = [];
        this.doors = [];
    }
    addItem(o) { this._roomItems.push(o); return o; }

    // Floor tiles + wall border shared by rooms.
    drawFloor(g, x0, y0, x1, y1, floorA, floorB, wall) {
        const ts = 40;
        for (let y = y0; y < y1; y += ts) for (let x = x0; x < x1; x += ts) {
            g.fillStyle(((x / ts + y / ts) % 2 === 0) ? floorA : floorB, 1);
            g.fillRect(x, y, ts, ts);
        }
        g.fillStyle(wall, 1);
        g.fillRect(0, 0, this.W, y0); g.fillRect(0, y1, this.W, this.H - y1);
        g.fillRect(0, 0, x0, this.H); g.fillRect(x1, 0, this.W - x1, this.H);
        g.lineStyle(3, 0x000000, 0.4); g.strokeRect(x0, y0, x1 - x0, y1 - y0);
    }

    addNpc(roleId, x, y, dialogStart, opts) {
        opts = opts || {};
        const token = this.makeToken(roleId);
        token.setPosition(x, y);
        this.actorLayer.add(token); this.addItem(token);
        const label = this.add.text(x, y - 42, opts.label || this.role(roleId).name.split(' ')[0], {
            fontFamily: 'Georgia, serif', fontSize: '11px', color: '#e8dcc0', backgroundColor: 'rgba(10,8,6,0.5)', padding: { x: 3, y: 1 }
        }).setOrigin(0.5);
        this.actorLayer.add(label); this.addItem(label);
        const npc = { roleId, x, y, token, label, dialogStart, getNode: opts.getNode };
        // Pixel-accurate clickable area (cursor + click) that matches the visible art.
        if (token.artImage) {
            token.artImage.setInteractive({ useHandCursor: true, pixelPerfect: true });
            token.artImage.setData('npcRef', npc);
        } else {
            token.setSize(40, 56);
            token.setInteractive({ hitArea: new Phaser.Geom.Rectangle(-20, -38, 40, 56), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
            token.setData('npcRef', npc);
        }
        this.npcs.push(npc);
        // NPCs block movement.
        this.colliders.push({ x: x - 18, y: y - 6, w: 36, h: 18 });
        return npc;
    }

    buildRoom(room, spawn) {
        this.clearRoom();
        this.room = room;
        this.setMood(room === 'hall' ? 'hall' : 'cathedral');
        const g = this.add.graphics(); this.roomLayer.addAt(g, 0); this.addItem(g);

        if (room === 'nave') {
            // Bounds + floor.
            this.bounds = { x0: 60, y0: 120, x1: 740, y1: 540 };
            this.drawFloor(g, 60, 120, 740, 540, 0x2a2016, 0x241b12, 0x161009);
            // A long crimson aisle rug.
            g.fillStyle(0x5a1226, 0.5); g.fillRect(360, 150, 80, 360);
            // Pews (decorative blocks) flanking the aisle.
            g.fillStyle(0x3a2c1e, 1);
            for (let i = 0; i < 4; i++) { g.fillRect(150, 200 + i * 70, 150, 26); g.fillRect(500, 200 + i * 70, 150, 26); }
            // Candles along the walls.
            for (let i = 0; i < 6; i++) { this.drawCandle(g, 90, 170 + i * 64); this.drawCandle(g, 710, 170 + i * 64); }
            // Pulpit (front-left, off the aisle so it never blocks the north door).
            g.fillStyle(0x4a3520, 1); g.fillRoundedRect(150, 150, 80, 40, 6); g.lineStyle(2, 0xc8a24a, 0.7); g.strokeRoundedRect(150, 150, 80, 40, 6);
            this.colliders.push({ x: 150, y: 150, w: 80, h: 46 });
            this.addInteract(190, 200, 'pulpit', '✝ Pulpit', { x: 150, y: 148, w: 80, h: 50 });
            // Confession booth (west).
            g.fillStyle(0x3a261a, 1); g.fillRoundedRect(72, 360, 70, 110, 6); g.lineStyle(2, 0x8a6a2e, 0.8); g.strokeRoundedRect(72, 360, 70, 110, 6);
            g.fillStyle(0x140d0a, 1); g.fillRect(96, 392, 22, 40);
            this.colliders.push({ x: 72, y: 360, w: 70, h: 110 });
            this.addInteract(150, 415, 'booth', '⌂ Confession', { x: 72, y: 360, w: 70, h: 110 });
            // North doorway to the hall.
            g.fillStyle(0x6a4a2a, 1); g.fillRect(370, 116, 60, 12);
            this.doors.push({ x: 372, y: 116, w: 56, h: 34, to: 'hall', spawn: { x: 400, y: 500 }, locked: () => !this.feast.sermonGiven, lockMsg: 'The hall is not ready. Give the sermon first.' });
            this.addItem(this.add.text(400, 104, 'to the Long Hall ▲', { fontFamily: 'Georgia, serif', fontSize: '11px', color: '#cdbf8e' }).setOrigin(0.5).setDepth(20));

            // NPCs.
            this.addNpc('pim', 250, 300, 'start');
            this.titleBanner('The Nave — Sunday');
        } else if (room === 'hall') {
            this.bounds = { x0: 60, y0: 110, x1: 740, y1: 540 };
            this.drawFloor(g, 60, 110, 740, 540, 0x322012, 0x2a1a10, 0x140b0a);
            // The long table down the centre.
            g.fillStyle(0x4a3320, 1); g.fillRoundedRect(180, 200, 440, 200, 10);
            g.fillStyle(0xe7d8b4, 0.5); g.fillRoundedRect(196, 214, 408, 172, 8);
            for (let i = 0; i < 5; i++) { this.drawCandle(g, 250 + i * 80, 300); g.fillStyle(0x7a1530, 0.6); g.fillCircle(240 + i * 82, 250, 10); g.fillCircle(240 + i * 82, 350, 10); }
            this.colliders.push({ x: 180, y: 200, w: 440, h: 200 });
            // Kitchen doorway (west) — Gallow.
            g.fillStyle(0x140d0a, 1); g.fillRect(60, 250, 16, 70);
            // South doorway back to the nave.
            g.fillStyle(0x6a4a2a, 1); g.fillRect(370, 532, 60, 12);
            this.doors.push({ x: 372, y: 528, w: 56, h: 18, to: 'nave', spawn: { x: 400, y: 230 } });
            this.addItem(this.add.text(400, 548, '▼ back to the Nave', { fontFamily: 'Georgia, serif', fontSize: '11px', color: '#cdbf8e' }).setOrigin(0.5).setDepth(20));

            // Seated guests around the table.
            this.addNpc('cornelius', 250, 180, 'start');
            this.addNpc('wren', 360, 180, 'start');
            this.addNpc('otho', 470, 180, 'start');
            this.addNpc('foyle', 560, 180, 'start');
            this.addNpc('twins', 300, 420, 'start');
            this.addNpc('marigold', 470, 420, 'start');
            this.addNpc('quill', 660, 300, 'start');
            this.addNpc('gallow', 95, 285, 'start', { label: 'Gallow' });
            this.addNpc('vesper', 400, 150, 'start', { label: 'Tann' });
            // The guest-of-honour seat (head of table, east).
            this.addInteract(650, 250, 'guesthonor', '☥ Name the guest of honour', { x: 614, y: 214, w: 74, h: 74 });
            this.titleBanner('The Long Hall');
        }

        // Place the player.
        const sp = spawn || { x: 400, y: 470 };
        this.player.setVisible(true).setPosition(sp.x, sp.y);
        this.playerGlow.setVisible(true).setPosition(sp.x, sp.y + 8);
        this.actorLayer.bringToTop(this.player);
        this.refreshHud();
    }

    drawCandle(g, x, y) {
        g.fillStyle(0xe7d8b4, 0.9); g.fillRect(x - 2, y, 4, 14);
        g.fillStyle(0xffcf7a, 0.9); g.fillEllipse(x, y - 4, 5, 11);
    }

    titleBanner(text) {
        const t = this.add.text(this.W / 2, 70, text, { fontFamily: 'Georgia, serif', fontSize: '20px', fontStyle: 'bold', color: '#e8c97a', stroke: '#000', strokeThickness: 4 }).setOrigin(0.5).setDepth(20);
        this.uiLayer.add(t); this.addItem(t);
        t.setAlpha(0); this.tweens.add({ targets: t, alpha: 1, duration: 600, yoyo: true, hold: 1400, onComplete: () => t.setAlpha(0.5) });
    }

    // Interactable objects (pulpit, booth, guest-of-honour). `x,y` is the spot the
    // player walks to; `hit` is the clickable footprint (defaults to a box around x,y).
    addInteract(x, y, id, label, hit) {
        const npc = { roleId: 'system', x, y, isObject: true, dialogStart: id, label };
        const marker = this.add.text(x, y - 30, label, { fontFamily: 'Georgia, serif', fontSize: '11px', color: '#e8c97a', backgroundColor: 'rgba(10,8,6,0.5)', padding: { x: 3, y: 1 } }).setOrigin(0.5).setDepth(15);
        this.actorLayer.add(marker); this.addItem(marker);
        npc.label2 = marker;
        // A clickable zone matching the object so the hand cursor + clicks land on it.
        const hz = hit || { x: x - 35, y: y - 60, w: 70, h: 80 };
        const zone = this.add.zone(hz.x, hz.y, hz.w, hz.h).setOrigin(0, 0);
        zone.setInteractive({ hitArea: new Phaser.Geom.Rectangle(0, 0, hz.w, hz.h), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
        zone.setData('npcRef', npc);
        npc.hit = { x: hz.x, y: hz.y, w: hz.w, h: hz.h }; // for the click fallback
        this.actorLayer.add(zone); this.addItem(zone);
        this.npcs.push(npc);
        return npc;
    }

    // ============================================================ movement loop

    near(npc) {
        return this.player && Phaser.Math.Distance.Between(this.player.x, this.player.y, npc.x, npc.y) < 70;
    }

    // Click-to-move and click-to-interact (works alongside the keyboard).
    onPointer(pointer) {
        this.resumeAudio();
        if (this.talking || this._inLoop || this._finished || this._transitioning || !this.bounds) return;

        // Accurate hit-test: did the click land on an interactive NPC/object?
        const hits = this.input.hitTestPointer(pointer) || [];
        let npc = null;
        for (const h of hits) { const ref = h.getData && h.getData('npcRef'); if (ref) { npc = ref; break; } }
        // Small safety net: a dead-centre click on a character whose exact pixel
        // happened to be transparent still counts.
        if (!npc) {
            const px = pointer.worldX, py = pointer.worldY;
            let bd = 26;
            for (const n of this.npcs) {
                if (n.hit) { if (px >= n.hit.x && px <= n.hit.x + n.hit.w && py >= n.hit.y && py <= n.hit.y + n.hit.h) { npc = n; break; } continue; }
                const d = Phaser.Math.Distance.Between(px, py, n.x, n.y - 24);
                if (d < bd) { bd = d; npc = n; }
            }
        }
        if (npc) {
            if (this.near(npc)) { this.path = null; this.pendingNpc = null; this.talkTo(npc); }
            else { this.walkTo(npc.x, npc.y, npc); this.clickMark(npc.x, npc.y); }
            return;
        }

        // Otherwise walk to the clicked floor point (routed around obstacles).
        const tx = Phaser.Math.Clamp(pointer.worldX, this.bounds.x0 + 16, this.bounds.x1 - 16);
        const ty = Phaser.Math.Clamp(pointer.worldY, this.bounds.y0 + 12, this.bounds.y1 - 6);
        this.walkTo(tx, ty, null);
        this.clickMark(tx, ty);
    }

    walkTo(tx, ty, npc) {
        this.pendingNpc = npc || null;
        const path = this.pathfind(this.player.x, this.player.y, tx, ty);
        this.path = (path && path.length) ? path : [{ x: tx, y: ty }]; // straight-line fallback
    }

    arrivePath() {
        const npc = this.pendingNpc;
        this.path = null;
        this.pendingNpc = null;
        if (npc && this.near(npc)) this.talkTo(npc);
    }

    clickMark(x, y) {
        const ring = this.add.circle(x, y, 6, 0xffcf7a, 0).setStrokeStyle(2, 0xffcf7a, 0.9).setDepth(8);
        this.tweens.add({ targets: ring, scale: 2.4, alpha: { from: 0.9, to: 0 }, duration: 420, onComplete: () => ring.destroy() });
    }

    update() {
        if (this.talking || this._finished || this._inLoop || !this.player || !this.bounds) return;
        const sp = 2.6;
        let dx = 0, dy = 0;
        if (this.cursors.left.isDown || this.keys.A.isDown) dx -= sp;
        if (this.cursors.right.isDown || this.keys.D.isDown) dx += sp;
        if (this.cursors.up.isDown || this.keys.W.isDown) dy -= sp;
        if (this.cursors.down.isDown || this.keys.S.isDown) dy += sp;

        const usingKeys = (dx !== 0 || dy !== 0);
        if (usingKeys) { this.path = null; this.pendingNpc = null; }
        else if (this.path && this.path.length) {
            // Follow the computed path, waypoint by waypoint.
            const wp = this.path[0];
            const dist = Phaser.Math.Distance.Between(this.player.x, this.player.y, wp.x, wp.y);
            if (dist <= sp) {
                this.player.x = wp.x; this.player.y = wp.y; this.path.shift();
                if (!this.path.length) this.arrivePath();
            } else {
                const a = Math.atan2(wp.y - this.player.y, wp.x - this.player.x);
                dx = Math.cos(a) * sp; dy = Math.sin(a) * sp;
            }
        }

        let moved = false;
        const attempted = (dx !== 0 || dy !== 0);
        if (dx !== 0) { const nx = this.player.x + dx; if (!this.blocked(nx, this.player.y)) { this.player.x = nx; moved = true; } this.player.setFlipX(dx > 0); }
        if (dy !== 0) { const ny = this.player.y + dy; if (!this.blocked(this.player.x, ny)) { this.player.y = ny; moved = true; } }

        this.player.x = Phaser.Math.Clamp(this.player.x, this.bounds.x0 + 16, this.bounds.x1 - 16);
        this.player.y = Phaser.Math.Clamp(this.player.y, this.bounds.y0 + 12, this.bounds.y1 - 6);
        this.playerGlow.setPosition(this.player.x, this.player.y + 8);

        // Wedged while following a path → give up gracefully (talk if we're near the target).
        if (!usingKeys && this.path && attempted && !moved) this.arrivePath();

        // Doorways.
        for (const d of this.doors) {
            if (this.player.x > d.x && this.player.x < d.x + d.w && this.player.y > d.y - 10 && this.player.y < d.y + d.h + 10) {
                if (d.locked && d.locked()) { this.floatMsg(d.lockMsg); break; }
                this.gotoRoom(d.to, d.spawn); break;
            }
        }

        // Nearest interactable → hint.
        let best = null, bestD = 9999;
        for (const n of this.npcs) {
            const d = Phaser.Math.Distance.Between(this.player.x, this.player.y, n.x, n.y);
            if (d < 64 && d < bestD) { best = n; bestD = d; }
        }
        this.activeNpc = best;
        if (best) { this.hint.setVisible(true).setPosition(best.x, best.y - 50); }
        else this.hint.setVisible(false);
    }

    blocked(x, y) {
        const fx = x - 12, fy = y - 6, fw = 24, fh = 12; // feet box
        for (const c of this.colliders) {
            if (fx < c.x + c.w && fx + fw > c.x && fy < c.y + c.h && fy + fh > c.y) return true;
        }
        return false;
    }

    // True if the straight segment between two points is free of obstacles.
    clearLine(x1, y1, x2, y2) {
        const dist = Phaser.Math.Distance.Between(x1, y1, x2, y2);
        const steps = Math.max(1, Math.ceil(dist / 8));
        for (let i = 0; i <= steps; i++) {
            const t = i / steps;
            if (this.blocked(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)) return false;
        }
        return true;
    }

    /**
     * A* over a coarse grid of the current room, routing the player AROUND
     * obstacles (table, pulpit, booth, other guests) instead of through them.
     * Returns a smoothed list of world-space waypoints, or null if unreachable.
     */
    pathfind(sx, sy, tx, ty) {
        // Shortcut: if we can see the target in a straight line, just go.
        if (this.clearLine(sx, sy, tx, ty)) return [{ x: tx, y: ty }];

        const b = this.bounds, cell = 20;
        const cols = Math.max(1, Math.ceil((b.x1 - b.x0) / cell));
        const rows = Math.max(1, Math.ceil((b.y1 - b.y0) / cell));
        const center = (cx, cy) => ({ x: b.x0 + cx * cell + cell / 2, y: b.y0 + cy * cell + cell / 2 });
        const walkable = (cx, cy) => {
            if (cx < 0 || cy < 0 || cx >= cols || cy >= rows) return false;
            const c = center(cx, cy);
            if (c.x < b.x0 + 16 || c.x > b.x1 - 16 || c.y < b.y0 + 12 || c.y > b.y1 - 6) return false;
            return !this.blocked(c.x, c.y);
        };
        const toCell = (x, y) => ({
            cx: Phaser.Math.Clamp(Math.floor((x - b.x0) / cell), 0, cols - 1),
            cy: Phaser.Math.Clamp(Math.floor((y - b.y0) / cell), 0, rows - 1)
        });
        const key = (cx, cy) => cy * cols + cx;

        const start = toCell(sx, sy);
        let goal = toCell(tx, ty);
        let goalSnapped = false;
        if (!walkable(goal.cx, goal.cy)) {
            const g2 = this.nearestWalkable(goal, walkable, cols, rows);
            if (!g2) return null;
            goal = g2; goalSnapped = true;
        }

        const startKey = key(start.cx, start.cy), goalKey = key(goal.cx, goal.cy);
        const open = [startKey], inOpen = new Set([startKey]), closed = new Set();
        const came = {}, g = { [startKey]: 0 }, f = { [startKey]: 0 };
        const h = (cx, cy) => Math.abs(cx - goal.cx) + Math.abs(cy - goal.cy);
        const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];

        let guard = 0, found = (startKey === goalKey);
        while (open.length && guard++ < 8000) {
            let bi = 0; for (let i = 1; i < open.length; i++) if (f[open[i]] < f[open[bi]]) bi = i;
            const cur = open.splice(bi, 1)[0]; inOpen.delete(cur);
            if (cur === goalKey) { found = true; break; }
            closed.add(cur);
            const ccx = cur % cols, ccy = Math.floor(cur / cols);
            for (const [dxc, dyc] of dirs) {
                const nx = ccx + dxc, ny = ccy + dyc;
                if (!walkable(nx, ny)) continue;
                if (dxc !== 0 && dyc !== 0 && (!walkable(ccx + dxc, ccy) || !walkable(ccx, ccy + dyc))) continue; // no corner cutting
                const nk = key(nx, ny);
                if (closed.has(nk)) continue;
                const tentative = g[cur] + ((dxc !== 0 && dyc !== 0) ? 1.414 : 1);
                if (g[nk] === undefined || tentative < g[nk]) {
                    came[nk] = cur; g[nk] = tentative; f[nk] = tentative + h(nx, ny);
                    if (!inOpen.has(nk)) { open.push(nk); inOpen.add(nk); }
                }
            }
        }
        if (!found) return null;

        const cells = [];
        let ck = goalKey;
        while (ck !== undefined && ck !== startKey) { cells.unshift({ cx: ck % cols, cy: Math.floor(ck / cols) }); ck = came[ck]; }
        let pts = cells.map(c => center(c.cx, c.cy));
        if (!goalSnapped) { if (pts.length) pts[pts.length - 1] = { x: tx, y: ty }; else pts = [{ x: tx, y: ty }]; }
        return this.smoothPath(sx, sy, pts);
    }

    nearestWalkable(cell, walkable, cols, rows) {
        for (let r = 1; r < Math.max(cols, rows); r++) {
            for (let dx = -r; dx <= r; dx++) for (let dy = -r; dy <= r; dy++) {
                if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
                if (walkable(cell.cx + dx, cell.cy + dy)) return { cx: cell.cx + dx, cy: cell.cy + dy };
            }
        }
        return null;
    }

    // Collapse grid waypoints using line-of-sight so movement looks natural, not staircased.
    smoothPath(sx, sy, pts) {
        if (pts.length <= 1) return pts;
        const out = []; let ax = sx, ay = sy, i = 0;
        while (i < pts.length) {
            let j = i;
            for (let k = pts.length - 1; k >= i; k--) { if (this.clearLine(ax, ay, pts[k].x, pts[k].y)) { j = k; break; } }
            out.push(pts[j]); ax = pts[j].x; ay = pts[j].y; i = j + 1;
        }
        return out;
    }

    gotoRoom(to, spawn) {
        if (this._transitioning) return;
        this._transitioning = true;
        this.path = null; this.pendingNpc = null;
        this.hint.setVisible(false);
        this.cameras.main.fadeOut(280, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => {
            this.buildRoom(to, spawn);
            this.cameras.main.fadeIn(280, 0, 0, 0);
            this.time.delayedCall(320, () => { this._transitioning = false; });
        });
    }

    floatMsg(text) {
        if (this._floatLock) return; this._floatLock = true;
        const t = this.add.text(this.player.x, this.player.y - 60, text, { fontFamily: 'Georgia, serif', fontSize: '13px', color: '#ffd0c0', backgroundColor: 'rgba(10,8,6,0.8)', padding: { x: 6, y: 3 }, wordWrap: { width: 280 }, align: 'center' }).setOrigin(0.5).setDepth(200);
        this.tweens.add({ targets: t, y: t.y - 24, alpha: { from: 1, to: 0 }, duration: 1600, onComplete: () => { t.destroy(); this._floatLock = false; } });
    }

    onInteract() {
        this.resumeAudio();
        if (this._inLoop) return; // the Loop has its own advance handler
        if (this.talking) {
            // Only auto-advance single-choice ("continue") nodes; real choices need a click.
            if (this._singleChoice && this._choiceCbs && this._choiceCbs[0]) this._choiceCbs[0]();
            return;
        }
        if (this.activeNpc) this.talkTo(this.activeNpc);
    }

    // ================================================================== dialog

    talkTo(npc) {
        const tree = this.dialogTree(npc.roleId, npc.dialogStart, npc);
        if (!tree) return;
        this.talking = true;
        this.hint.setVisible(false);
        this._dialogRole = npc.dialogRole || (npc.isObject ? 'cardinal' : npc.roleId);
        this.renderNode(tree, tree.startId || 'start', npc);
    }

    renderNode(tree, id, npc) {
        const node = tree.nodes[id];
        if (!node) { this.endTalk(); return; }
        if (node.onEnter) node.onEnter();
        if (node.action === 'close') { this.endTalk(); return; }

        if (this._dialogBox) this._dialogBox.destroy();
        this._dialogBox = this.add.container(0, 0).setDepth(500);
        this._choiceCbs = [];

        const boxX = 10, boxY = 392, boxW = this.W - 20, boxH = this.H - boxY - 10;
        const g = this.add.graphics();
        g.fillStyle(0x0d0a08, 0.96); g.fillRect(boxX, boxY, boxW, boxH);
        g.lineStyle(2, node.glitch ? 0x7a2030 : 0xc8a24a, 0.9); g.strokeRect(boxX, boxY, boxW, boxH);
        g.lineStyle(1, 0x7a5e28, 0.6); g.strokeRect(boxX + 4, boxY + 4, boxW - 8, boxH - 8);
        this._dialogBox.add(g);

        // Portrait (left).
        const roleId = node.role || this._dialogRole;
        const pSize = 150, pX = boxX + 10, pY = boxY + 12;
        this._dialogBox.add(this.drawPortrait(roleId, pX, pY, pSize, node.portrait));

        const textX = pX + pSize + 18;
        const textW = boxW - (textX - boxX) - 24;
        const r = this.role(roleId);
        this._dialogBox.add(this.add.text(textX, boxY + 14, node.speaker || r.name, {
            fontFamily: 'Georgia, "Times New Roman", serif', fontSize: '19px', fontStyle: 'bold', color: node.glitch ? '#d06a78' : '#e8c97a'
        }));

        const text = typeof node.text === 'function' ? node.text() : node.text;
        const choices = (typeof node.choices === 'function' ? node.choices() : node.choices) || [{ label: '(continue)', action: 'close' }];
        this._singleChoice = choices.length === 1;

        // Auto-fit body text to the space above the choices.
        const choiceH = Math.min(choices.length, 4) * 26 + 8;
        const availH = boxH - 46 - choiceH;
        let body, fs = 16;
        for (; fs >= 11; fs--) { if (body) body.destroy(); body = this.add.text(textX, boxY + 42, text, { fontFamily: 'Georgia, "Times New Roman", serif', fontSize: fs + 'px', color: node.glitch ? '#d8a0a8' : '#e6dcc4', wordWrap: { width: textW }, lineSpacing: 3 }); if (body.height <= availH) break; }
        this._dialogBox.add(body);

        let cy = boxY + boxH - choiceH;
        choices.forEach((choice, i) => {
            const seal = this.add.circle(textX + 7, cy + 9, 5, node.glitch ? 0x6a1224 : 0x7a1530, 1).setStrokeStyle(1, 0xc8a24a);
            const label = this.add.text(textX + 22, cy, choice.label, { fontFamily: 'Georgia, "Times New Roman", serif', fontSize: '15px', color: '#d8c79a', wordWrap: { width: textW - 30 } }).setOrigin(0, 0);
            label.setInteractive({ useHandCursor: true });
            const pick = () => this.pickChoice(tree, choice, npc);
            this._choiceCbs.push(pick);
            label.on('pointerover', () => { label.setColor('#fff0c8'); seal.setScale(1.3); });
            label.on('pointerout', () => { label.setColor('#d8c79a'); seal.setScale(1); });
            label.on('pointerdown', pick);
            this._dialogBox.add(seal); this._dialogBox.add(label);
            cy += 26;
        });

        this._dialogBox.setAlpha(0); this.tweens.add({ targets: this._dialogBox, alpha: 1, duration: 160 });
    }

    pickChoice(tree, choice, npc) {
        if (typeof choice.dev === 'number') this.feast.devotion += choice.dev;
        if (typeof choice.sus === 'number') this.feast.suspicion = Math.max(0, this.feast.suspicion + choice.sus);
        if (choice.set) Object.assign(this.feast, choice.set);
        if (choice.onPick) choice.onPick();
        this.refreshHud();
        if (choice.action === 'close') { this.endTalk(); return; }
        if (choice.action === 'ending') { this.endTalk(); this.beginEnding(); return; }
        if (choice.next) { this.renderNode(tree, choice.next, npc); return; }
        this.endTalk();
    }

    endTalk() {
        if (this._dialogBox) { this._dialogBox.destroy(); this._dialogBox = null; }
        this.talking = false;
        this._choiceCbs = [];
    }

    // =============================================================== dialog data

    dialogTree(roleId, startId, npc) {
        const f = this.feast;
        const learnEgg = () => { this.learnedEggCathedral = true; f.askedJournal = true; };

        // ---- interactable objects ----
        if (roleId === 'system') {
            if (startId === 'pulpit') {
                return { startId: 'start', nodes: {
                    start: {
                        role: 'cardinal', portrait: 'emils1',
                        text: f.sermonGiven
                            ? "The pulpit. The flock is seated and fed on words. There is nothing left to preach until Sunday next."
                            : "You mount the pulpit. The pews are half-empty and doubtful. A sermon is yours to shape — and a fuller flock makes a richer feast.",
                        choices: () => f.sermonGiven
                            ? [{ label: "Step down.", action: 'close' }]
                            : [
                                { label: "Preach of mercy and the open table.", dev: 2, set: { sermonGiven: true }, next: 'done' },
                                { label: "Preach of hunger, and Who provides.", dev: 1, sus: 1, set: { sermonGiven: true }, next: 'done' }
                            ]
                    },
                    done: { role: 'cardinal', portrait: 'emils2', text: "The doubt melts off their faces like tallow. \"Come to the open table this Sunday,\" you tell them. The north door to the Long Hall stands open now.", choices: [{ label: "Amen.", action: 'close' }] }
                } };
            }
            if (startId === 'booth') {
                return { startId: 'start', nodes: {
                    start: {
                        role: 'cardinal', portrait: 'emils3',
                        text: f.confessed
                            ? "The booth is quiet now. You already know whose secret you mean to act upon."
                            : "The confession booth. One by one they kneel and unburden themselves — and beneath the comedy you are taking inventory. Whose secret do you keep?",
                        choices: () => f.confessed ? [{ label: "Close the grille.", action: 'close' }] : [
                            { label: "The one no one would miss. (a shy scribe)", set: { confessed: true, target: 'wren' }, next: 'done' },
                            { label: "The one everyone despises. (a tax-man)", dev: 1, set: { confessed: true, target: 'cornelius' }, next: 'done' },
                            { label: "The one asking questions. (a deacon)", sus: 1, set: { confessed: true, target: 'foyle' }, next: 'done' }
                        ]
                    },
                    done: { role: 'cardinal', text: "You let yourself feel clever about it. That is always the first course — the cleverness.", choices: [{ label: "Bless you, my child.", action: 'close' }] }
                } };
            }
            if (startId === 'guesthonor') {
                const talked = Object.keys(f.guestsTalked).length;
                if (f.namedGuest) return { startId: 'start', nodes: { start: { role: 'cardinal', text: "The guest of honour is chosen. Only the Inquisitor stands between you and the last course. Speak with Vesper Tann.", choices: [{ label: "Soon.", action: 'close' }] } } };
                if (talked < 3) return { startId: 'start', nodes: { start: { role: 'cardinal', text: "The head of the table, and its empty honoured seat. But you have barely worked the room. Greet your guests first — learn who is ripe.", choices: [{ label: "Not yet.", action: 'close' }] } } };
                return { startId: 'start', nodes: {
                    start: {
                        role: 'cardinal', portrait: 'emils2',
                        text: "The candle is two-thirds gone. You must name the guest of honour — and decide how greedy to be.",
                        choices: [
                            { label: "The modest plate — Cornelius. The flock thanks you.", set: { namedGuest: 'cornelius' }, dev: 1, next: 'done' },
                            { label: "The clever plate — Wren. No one misses her for weeks.", set: { namedGuest: 'wren' }, dev: 2, sus: 1, next: 'done' },
                            { label: "The greedy plate — a Goodfennow twin. A feast of a lifetime.", set: { namedGuest: 'twin' }, dev: 3, sus: 3, next: 'done' },
                            { label: "The defensive plate — Foyle, before he talks.", set: { namedGuest: 'foyle' }, sus: 2, next: 'done' }
                        ]
                    },
                    done: { role: 'cardinal', text: "Gallow inclines his head from the kitchen door. The seat is spoken for. Now there is only the matter of the Inquisitor.", choices: [{ label: "Speak with Vesper.", action: 'close' }] }
                } };
            }
        }

        // ---- characters ----
        if (roleId === 'pim') {
            return { startId: 'start', nodes: {
                start: {
                    role: 'pim',
                    text: "Pim hurries up with the wine jug, beaming — then stops dead, blinking. \"Your Eminence — sorry. I thought you were going to ask the other thing. The thing she asked. The lady who used to sit where you sit.\"",
                    choices: [
                        { label: "\"Have we spoken before, Pim?\"", next: 'before' },
                        { label: "\"Where did I put my journal?\"", next: 'journal' },
                        { label: "\"Never mind, Brother.\"", action: 'close' }
                    ]
                },
                before: { role: 'pim', text: "\"In a way that makes my scales crawl, yes. You ask things the way she asked them. Same pauses. Same weight. She stopped coming one day. We kept her place anyway.\"", choices: [{ label: "\"Where did I put my journal?\"", next: 'journal' }, { label: "\"Thank you, Pim.\"", action: 'close' }] },
                journal: { role: 'pim', onEnter: learnEgg, text: "He answers before he can think — reciting, not remembering: \"Your journal? You said you'd tucked it away somewhere no one would think to look. Somewhere with the eggs. The Egg Cathedral, you said.\" He stares, frightened by his own mouth.", choices: [{ label: "\"...The Egg Cathedral.\" (Remember this.)", action: 'close' }] }
            } };
        }

        const guest = (id, line, choices) => ({ startId: 'start', nodes: { start: { role: id, text: line, choices, onEnter: () => { f.guestsTalked[id] = true; } }, ack: { role: id, text: "Emils smiles like sunrise and moves on down the table.", choices: [{ label: "(step away)", action: 'close' }] } } });

        if (roleId === 'cornelius') return guest('cornelius', "\"Frankly, Eminence, the beggars on your steps are an eyesore.\" \"Oh, I quite agree, Cornelius,\" you say warmly. \"You give me such an appetite for reform.\"", [
            { label: "Indulge him. (he marks himself)", dev: 1, next: 'ack' },
            { label: "Rebuke him gently. (the table loves you)", dev: 1, sus: 1, next: 'ack' }
        ]);
        if (roleId === 'wren') return guest('wren', "\"I've never sat at a table like this. I wrote to Mum about you — I said I'd finally found somewhere kind.\" Your smile flickers, almost nothing, then returns. \"...Did you. Eat, child.\"", [
            { label: "Charm her. (the easiest meal)", dev: 2, next: 'ack' },
            { label: "Send her toward the far end. (safer for her)", sus: 1, next: 'ack' }
        ]);
        if (roleId === 'otho') return guest('otho', "\"A TOAST! To the Cardinal! To the cheese! I've sold wine in THREE CITIES—\" \"Three cities,\" you murmur. \"Sit, my friend. Save your strength for the next course.\"", [
            { label: "Toast him back. (harmless fun)", dev: 1, next: 'ack' },
            { label: "Silence him. (a relief — but he is known)", sus: 2, next: 'ack' }
        ]);
        if (roleId === 'foyle') return guest('foyle', "\"The grocery line in the ledgers is extraordinary, Eminence. So much... meat. For a swamp parish.\" \"The Lord provides, Foyle. A good shepherd should know his flock by taste.\"", [
            { label: "Reassure him.", dev: 1, next: 'ack' },
            { label: "Let the threat hang.", sus: 1, next: 'ack' }
        ]);
        if (roleId === 'twins') return guest('twins', "\"A lovely spread.\" \"Lovely. Though the seat between us is laid... and empty.\" \"A place kept for the guest of honour,\" you say. \"These things reveal themselves in time.\"", [
            { label: "Smile and move on.", dev: 1, next: 'ack' }
        ]);
        if (roleId === 'marigold') return guest('marigold', "Sister Marigold laughs at every joke and keeps refilling your plate, never noticing she is being fattened in turn. \"You're too good to us, Emils. Far too good.\"", [
            { label: "\"It is you who are good to me, Marigold.\"", dev: 1, next: 'ack' }
        ]);
        if (roleId === 'quill') return { startId: 'start', nodes: {
            start: {
                role: 'quill',
                onEnter: () => { f.guestsTalked.quill = true; if (!this.learnedEggCathedral) this.learnedEggCathedral = true; },
                text: () => "Without turning her blind head: \"Emils. The boy from the marsh. The miller's wife. That nice tax-man you'll have by Lent. You always did keep a full larder.\"\nThen, lower — and not to Emils: "
                    + (f.askedJournal ? "\"You found where you hid it. The Egg Cathedral. The part of you that wrote it always remembered.\"" : "\"You. You already know where it is. You hid it yourself. The Egg Cathedral.\""),
                choices: [{ label: "Say nothing. Let her sip her wine.", action: 'close' }]
            }
        } };
        if (roleId === 'gallow') return { startId: 'start', nodes: { start: { role: 'gallow', text: "Gallow the cook fills the kitchen doorway, cleaver resting on one shoulder like a parade rifle. He says nothing. He never does. He simply waits to be told whose seat is spoken for.", choices: [{ label: "Nod to him.", action: 'close' }] } } };

        if (roleId === 'vesper') {
            if (!f.namedGuest) return { startId: 'start', nodes: { start: { role: 'vesper', text: "Inquisitor Vesper Tann sits at the far end, her plate empty, watching. \"I am in no hurry, Emils. I will eat when you show me what is really being served. Take your time. I always do.\"", choices: [{ label: "Step away.", action: 'close' }] } } };
            if (f.inquiryDone) return { startId: 'start', nodes: { start: { role: 'vesper', text: "She watches the candle gutter. \"It is nearly time for the last course. We both know it.\"", choices: [{ label: "Serve the last course.", action: 'ending' }] } } };
            return { startId: 'start', nodes: {
                start: {
                    role: 'vesper',
                    text: () => {
                        const v = { cornelius: "\"The tax-collector. Gone between courses. How convenient.\"", wren: "\"A girl who wrote letters home. They've stopped. Her mother wrote to me instead.\"", twin: "\"A Goodfennow. Marsh-nobility. Their house has sent riders.\"", foyle: "\"A churchman this time. You ate the only other soul who could count.\"" }[f.namedGuest] || "\"Something is wrong in this diocese, and we both know its name.\"";
                        return "Vesper sets down her empty plate. " + v + " Every charming word from here buys you time and costs you something.";
                    },
                    choices: [
                        { label: "Deflect, charmingly.", sus: 1, set: { inquiryDone: true }, next: 'after' },
                        { label: "A devastatingly sincere defense.", set: { inquiryDone: true }, next: 'after' },
                        { label: "Frame an innocent. (Pim's hands shake)", sus: 1, dev: -1, set: { inquiryDone: true }, next: 'after' },
                        { label: "Begin, very slightly, to crack.", sus: 2, set: { inquiryDone: true }, next: 'after' }
                    ]
                },
                after: {
                    role: 'vesper',
                    text: () => f.suspicion >= 6 ? "She does not blink. \"I have had enough for some time.\" Her chair scrapes back. Behind you, Gallow shifts his weight, and the kitchen door does not open." : "She almost — almost — smiles. \"You are very good. The good ones are always hardest to bury.\" She lets it lie. For now.",
                    choices: [{ label: "Serve the last course.", action: 'ending' }]
                }
            } };
        }
        return null;
    }

    // ============================================================ endgame + loop

    beginEnding() {
        const f = this.feast;
        let endText;
        if (f.suspicion >= 6) endText = "Vesper wins. They make you give one last sermon, and you give them your confession instead — every name, every course — with total, terrible serenity. \"Go in peace,\" you tell them as they take you away. \"Come back hungry.\"";
        else if (f.devotion >= 6 && f.namedGuest) endText = "You reshaped the doctrine so gently no one noticed its shape. The whole congregation reaches for the covered dish at once, smiling, grateful, willing. \"Go in peace,\" they say together. \"Come back hungry.\"";
        else endText = "You are never caught. You grow old and full, and press your ring into Brother Pim's trembling hand. \"Go in peace,\" you tell the emptying hall. \"Come back hungry.\"";

        // Play the ending as a portrait beat, then the Loop.
        this.talking = true;
        this.renderNode({ startId: 's', nodes: { s: {
            role: 'cardinal', portrait: 'emils2', speaker: 'Cardinal Emils Ven', text: endText,
            choices: [{ label: "▸ The screen holds on your face — a beat too long.", onPick: () => this.playLoop() }]
        } } }, 's', null);
    }

    playLoop() {
        this.endTalk();
        this._inLoop = true;
        this.setMood('glitch');
        // Tear down the room into a lightless hall with a faceless presence.
        this.clearRoom();
        this.player.setVisible(false); this.playerGlow.setVisible(false); this.hint.setVisible(false);
        const g = this.add.graphics().setDepth(300); this.addItem(g);
        g.fillStyle(0x05050a, 1); g.fillRect(0, 0, this.W, this.H);
        g.fillStyle(0x16120f, 0.9); g.fillTriangle(240, 540, 560, 540, this.W / 2, 220);
        g.fillStyle(0x000000, 1); g.fillEllipse(this.W / 2, 210, 90, 130); // faceless presence
        for (let i = 0; i < 6; i++) { g.fillStyle(0x5a1020, 0.45); g.fillRect(0, 60 + i * 70, this.W, 3); }

        const panels = [
            { title: 'INFINITE FOLD', text: "The warm gold drains out of the world. The hall again — but empty, lightless, every candle snuffed. The long table is set for one. At its head sits a presence that is not the cardinal, and it does not turn around." },
            { title: 'INFINITE FOLD', text: "The same three seconds play, and play, and play. Each pass a fraction darker. A held organ note. A sound like a held breath. You cannot reach the menu." },
            { title: 'INFINITE FOLD', text: () => "This is not a bug. This is the last thing she saw. She sat where you are sitting. Then she was gone."
                + (this.learnedEggCathedral ? "\n\nThe rest is out there, in her own hand, where she hid it: the Egg Cathedral." : "\n\nWhatever she meant to tell you, she left it somewhere only the game still remembers.") }
        ];
        let i = 0;
        const titleT = this.add.text(this.W / 2, 110, '', { fontFamily: 'Georgia, serif', fontSize: '30px', fontStyle: 'bold', color: '#c9b8ff', stroke: '#000', strokeThickness: 5 }).setOrigin(0.5).setDepth(320); this.addItem(titleT);
        const bodyT = this.add.text(this.W / 2, 470, '', { fontFamily: 'Georgia, serif', fontSize: '17px', color: '#d8c0e0', align: 'center', wordWrap: { width: 640 }, lineSpacing: 4 }).setOrigin(0.5, 0).setDepth(320); this.addItem(bodyT);
        const prompt = this.add.text(this.W / 2, 568, '▸ click or press Space', { fontFamily: 'Georgia, serif', fontSize: '13px', color: '#9a7ab0' }).setOrigin(0.5).setDepth(320); this.addItem(prompt);
        this.tweens.add({ targets: prompt, alpha: { from: 0.3, to: 1 }, duration: 900, yoyo: true, repeat: -1 });

        const show = () => {
            if (i >= panels.length) { this.finishFeast(); return; }
            const p = panels[i];
            titleT.setText(p.title);
            bodyT.setText(typeof p.text === 'function' ? p.text() : p.text);
            titleT.setAlpha(0); bodyT.setAlpha(0);
            this.tweens.add({ targets: [titleT, bodyT], alpha: 1, duration: 500 });
            i++;
        };
        this._loopAdvance = () => { if (!this._loopBusy) { this._loopBusy = true; show(); this.time.delayedCall(220, () => { this._loopBusy = false; }); } };
        const onKey = () => this._loopAdvance();
        this.interactKey.on('down', onKey); this.interactKey2.on('down', onKey);
        this.input.on('pointerdown', onKey);
        show();
    }

    // ================================================================== finish

    finishFeast() {
        if (this._finished) return;
        this._finished = true;
        this.stopMusic();
        const cat = this.journalSystem ? this.journalSystem.categories : {};

        if (this.journalSystem && !this.journalSystem.hasEntry('cardinal_feast_played')) {
            this.journalSystem.addEntry('cardinal_feast_played', 'Played The Cardinal Feast',
                "I resumed the Bishop's last session of The Cardinal Feast on Dr. Elphi's repaired cartridge — a small top-down RPG where you play a cannibal cardinal hosting a feast. Its characters remember the Bishop and answered me as if I were her. After the feast resolved, the cartridge collapsed into \"Infinite Fold\": an empty hall with a faceless presence at the head of the table. It is the last thing the Bishop saw before she died.",
                cat.EVENTS, { location: 'ARB Ambra', character: 'The Bishop', related: 'Dream cartridge' });
        }
        if (this.journalSystem && !this.journalSystem.hasEntry('bishop_journal_egg_cathedral')) {
            this.journalSystem.addEntry('bishop_journal_egg_cathedral', "The Journal's Hiding Place",
                "Inside The Cardinal Feast, the characters leaked something they had no business knowing: the Bishop hid the rest of her journal \"somewhere no one would think to look — the Egg Cathedral.\" The game answered because it believed I was her. The missing notebook is at the Egg Cathedral she sealed before she died.",
                cat.EVENTS, { location: 'Egg Cathedral', character: 'The Bishop', related: "Bishop's notebook" });
        }
        if (this.questSystem) {
            if (this.questSystem.getQuest('who_killed_bishop')) {
                this.questSystem.updateQuest('who_killed_bishop',
                    "Dr. Elphi's reconstructed cartridge let me play the Bishop's last session of The Cardinal Feast. Its characters remember her and answered as if I were her — leaking that she hid the rest of her journal at the Egg Cathedral. The session ends in \"Infinite Fold\": the last thing she saw before she died.",
                    'cardinal_feast_egg_cathedral_lead');
            }
            if (this.questSystem.getQuest('find_bishop_notebook')) {
                this.questSystem.updateQuest('find_bishop_notebook', "The Cardinal Feast revealed the Bishop hid the rest of her notebook at the Egg Cathedral. I should go there.", 'notebook_at_egg_cathedral');
            } else {
                this.questSystem.addQuest('find_bishop_notebook', "Find the Bishop's Notebook", "The Cardinal Feast revealed the Bishop hid the rest of her notebook at the Egg Cathedral. I should search there.");
            }
        }
        this.registry.set('cardinal_feast_played', true);

        this.cameras.main.fadeOut(900, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => this.scene.start(this.returnScene));
    }

    // ============================================================= boot screen

    showBoot() {
        this.talking = true;
        this.player.setVisible(false); this.playerGlow.setVisible(false);
        const tree = { startId: 'boot', nodes: {
            boot: { role: 'system', speaker: 'The Cardinal Feast', portrait: 'emils1',
                text: "ARB AMBRA NEUROFICTION // THE CARDINAL FEAST\n\n\"A small, sinful RPG about appetite and authority.\"\n\nReconstructed save data recovered. Last player on this cartridge: BISHOP.",
                choices: [{ label: "▸ Load the Bishop's last session", next: 'saves' }] },
            saves: { role: 'system', speaker: 'The Cardinal Feast',
                text: "The helmet warms against your temples. A save list flickers up in a hand that isn't yours:\n\n   ✦ autosave — \"The Confession\"\n   ✦ save 2 — \"The Feast\"\n   ✦ save 3 — [ C O R R U P T E D ]\n\nThe cursor already rests on the corrupted save. You did not put it there.",
                choices: [{ label: "▸ Resume the session", action: 'close', onPick: () => { this.time.delayedCall(50, () => this.buildRoom('nave', { x: 400, y: 470 })); } }] }
        } };
        this._dialogRole = 'system';
        this.renderNode(tree, 'boot', null);
    }
}

if (typeof window !== 'undefined') {
    window.CardinalFeastScene = CardinalFeastScene;
}

export { CardinalFeastScene };
