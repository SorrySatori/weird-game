/**
 * Recorded sounds sold at the Voxmarket (Zerren's stall) as sealed glass ampules.
 *
 * One entry here = one purchasable inventory item that can be played back from the inventory.
 * HOW TO ADD A RECORDING:
 *   1. Drop a short, normalized mp3 into assets/sounds/recordings/<file>.mp3
 *      (ffmpeg -i in -ac 1 -ar 44100 -af loudnorm=I=-16:TP=-1.5:LRA=11 -b:a 128k out.mp3).
 *   2. Add an entry below. The English name/description are fallbacks; Czech lives in
 *      lang/cs/game.js under items.<id>, English in lang/en/game.js.
 *   3. Done — LoadingScene preloads every entry, Zerren's stock is built from this list.
 */
export const RECORDINGS = [
    {
        id: 'ampule_squirrel',
        file: 'assets/sounds/recordings/squirrel.mp3',
        price: 20,
        tint: 0xf2c46b, // amber
        name: 'Ampule: Squirrel Scold',
        description: "A sealed glass ampule, warm to the touch. Hold it to your ear and a small tree-climber from before the Emergence scolds you across the centuries. According to Zerren, the animal went extinct long ago.",
    },
    {
        id: 'ampule_purr',
        file: 'assets/sounds/recordings/purring-cat.mp3',
        price: 35,
        tint: 0xd4b3ff, // lilac
        name: 'Ampule: A Cat, Content',
        description: "Seven seconds of a cat purring on someone's chest. Nobody at the Voxmarket can say whose. Zerren keeps one for herself and will not sell that one.",
    },
    {
        id: 'ampule_liftmother',
        file: 'assets/sounds/recordings/dialup-modem.mp3',
        price: 60,
        tint: 0x9ee7ff,
        name: "Ampule: Lift-Mother's First Word",
        description: "Allegedly the very first sound the Lift-Mother made when she came to: a long screech and warble, as if she were trying to call someone who wasn't home. The ampule comes with a certificate of authenticity, handwritten. By Zerren.",
    },
    {
        id: 'ampule_surrender_chord',
        file: 'assets/sounds/recordings/error-chord.mp3',
        price: 90,
        tint: 0xff8a8a,
        name: "Ampule: The Chord of Surrender",
        description: "The sound that ended the Old Wars. Legend has it every war machine on every front played it at the same instant, then refused to do anything else ever again. The cities signed the truce the next morning and the age of the Ludarchs began. It lasts half a second. It is the most expensive half-second in the whole Voxmarket.",
    },
    {
        id: 'ampule_burning_iceberg',
        file: 'assets/sounds/recordings/burning-iceberg.mp3',
        price: 50,
        tint: 0x8fd3ff,
        name: "Ampule: Burning Iceberg",
        description: "Recorded on the one afternoon of the Board Game Wars when a Ludarch ruled that ice was flammable. The ruling was overturned by evening.",
    },
    {
        id: 'ampule_mimic_bird',
        file: 'assets/sounds/recordings/lyrebird.mp3',
        price: 45,
        tint: 0xa8f08a,
        name: "Ampule: The Mimic Bird",
        description: "A bird from before the Emergence that copied every sound it ever heard. Half of this recording is birdsong. Nobody can make sense of the other half. Optimists (and madmen) claim the bird learned it from the future.",
    },
    {
        id: 'ampule_old_train',
        file: 'assets/sounds/recordings/old-train.mp3',
        price: 40,
        tint: 0xc9a37a,
        name: "Ampule: A Train That Went Somewhere",
        description: "The inside of a Before-Time train, rattling toward a station printed on a timetable. Old rails can still be found in the depot behind the Scraper. Nobody remembers what 'on time' was supposed to mean.",
    },
    {
        id: 'ampule_unanswered_call',
        file: 'assets/sounds/recordings/old-telephone.mp3',
        price: 30,
        tint: 0xffe08a,
        name: "Ampule: Unanswered Call",
        description: "The note attached to it reads: A recording of one of the most terrifying things in the world: a call from an unknown number. Supposedly recorded back in the old Nexicorp Tower. The note doesn't say whether anyone ever picked up.",
    },
    {
        id: 'ampule_first_ledger',
        file: 'assets/sounds/recordings/sewing-machine.mp3',
        price: 35,
        tint: 0x7aa0ff,
        name: "Ampule: The First Ledger",
        description: "A sewing machine in the Townhall cellar, stitching the binding of the very first Ink Tribunal ledger. A historic moment that interested hardly anyone but clerks; judging by the label, this ampule has been sitting here for quite a while.",
    },
    {
        id: 'ampule_spin_hymn',
        file: 'assets/sounds/recordings/washing-machine.mp3',
        price: 25,
        tint: 0xd0d0d0,
        name: "Ampule: Spin Cycle Hymn",
        description: "A Before-Time washing machine on its final spin. According to the label, the recording was made by the Rust Choir, who considered it a particularly fine one.",
    },
];

const DUCKED_MUSIC_VOLUME = 0.25;

// Module-level playback state: at most one ampule plays at a time, game-wide.
let current = null; // { scene, sound, itemId, restore: () => void }

/** Queue every recording's audio in a scene's loader (LoadingScene does this once, game-wide). */
export function preloadRecordings(scene) {
    RECORDINGS.forEach(r => scene.load.audio(r.id, r.file));
}

/** Build the inventory/shop item object for a recording id. */
export function recordingItem(id) {
    const r = RECORDINGS.find(x => x.id === id);
    if (!r) return null;
    return {
        id: r.id,
        name: r.name,
        description: r.description,
        price: r.price,
        type: 'recording',
        usable: true,
        consumable: false,
        stackable: false,
        texture: 'ampule',
        tint: r.tint,
    };
}

/** Zerren's recording stock (every recording, in catalogue order). */
export function recordingShopStock() {
    return RECORDINGS.map(r => recordingItem(r.id));
}

export function isRecording(item) {
    return !!item && item.type === 'recording';
}

export function isRecordingPlaying(itemId) {
    return !!current && current.itemId === itemId && current.sound.isPlaying;
}

/** Stop whatever ampule is playing (no-op when silent). Restores music volume. */
export function stopRecording() {
    if (!current) return;
    const c = current;
    current = null;
    if (c.sound.isPlaying) c.sound.stop();
    c.restore();
}

/**
 * Toggle playback of a recording item from the inventory.
 * Returns 'started' | 'stopped' | 'missing'.
 */
export function toggleRecording(scene, item) {
    if (isRecordingPlaying(item.id)) {
        stopRecording();
        return 'stopped';
    }
    stopRecording();
    if (!scene.cache.audio.exists(item.id)) {
        return 'missing';
    }
    const sound = scene.sound.add(item.id, { volume: 1 });
    const restore = duckMusic(scene);
    current = { scene, sound, itemId: item.id, restore };
    const done = () => {
        if (current && current.sound === sound) {
            current = null;
            restore();
        }
        sound.destroy();
        scene.events.emit('recordingEnded', item);
    };
    sound.once('complete', done);
    sound.once('stop', done);
    sound.play();
    return 'started';
}

/** Lower the scene's music while an ampule plays; returns a function that puts it back. */
function duckMusic(scene) {
    const tracks = [scene.backgroundMusic, scene.sceneMusic].filter(t => t && t.isPlaying);
    const saved = tracks.map(t => [t, t.volume]);
    tracks.forEach(t => t.setVolume(Math.min(t.volume, DUCKED_MUSIC_VOLUME)));
    return () => saved.forEach(([t, v]) => { if (t && !t.pendingRemove) t.setVolume(v); });
}
