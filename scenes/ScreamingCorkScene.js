import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import LanguageSystem from '../systems/LanguageSystem.js';
import JournalSystem from '../systems/JournalSystem.js';

/**
 * Display labels for the book-building choices. The dialog stores short internal ids
 * (`bad scientist`, `god graveyard`, …) that used to leak straight into Edgar's lines and the
 * generated titles. `en`/`cs` are sentence forms (cs in the nominative — the completion line is
 * built so no label needs declining); `title` is the Title-Case form used by generateBookTitle.
 */
const BOOK_LABELS = {
    tone: {
        tragic:       { en: 'tragic',       cs: 'tragický' },
        metaphysical: { en: 'metaphysical', cs: 'metafyzický' },
        romantic:     { en: 'romantic',     cs: 'romantický' },
        existential:  { en: 'existential',  cs: 'existenciální' },
        political:    { en: 'political',    cs: 'politický' },
        comical:      { en: 'comical',      cs: 'komický' },
    },
    genre: {
        'fungal techno':   { en: 'fungal techno-thriller',       cs: 'houbový techno-thriller' },
        'postmodern':      { en: 'postmodern novel',             cs: 'postmoderní román' },
        'urban fantasy':   { en: 'urban fantasy',                cs: 'městská fantasy' },
        'funny animals':   { en: 'funny animals with depression', cs: 'vtipná zvířata s depresí' },
        'detective':       { en: 'detective novel',              cs: 'detektivní román' },
        'weird fiction':   { en: 'dreamy weird fiction',         cs: 'snová weird fiction' },
        'mythic war epic': { en: 'mythic war epic',              cs: 'mýtický válečný epos' },
        'cosmic horror':   { en: 'cosmic horror',                cs: 'kosmický horor' },
    },
    protagonist: {
        'disoriented tourist': { en: 'a disoriented tourist',                          cs: 'dezorientovaný turista',                    title: 'Disoriented Tourist' },
        'bad scientist':       { en: 'a renegade fungal scientist',                    cs: 'houbový vědec renegát',                    title: 'Renegade Scientist' },
        'mišutkenn':           { en: 'a mišutkenn seeking identity',                   cs: 'mišutkenn hledající identitu',              title: 'Mišutkenn' },
        'strange amnesiac':    { en: 'an amnesiac with strange abilities',             cs: 'člověk trpící ztrátou paměti s podivnými schopnostmi', title: 'Amnesiac' },
        'fungal colony':       { en: 'a sentient fungal colony',                       cs: 'inteligentní kolonie hub',              title: 'Fungal Colony' },
        'dream detective':     { en: 'a dream detective',                              cs: 'snový detektiv',                            title: 'Dream Detective' },
        'rogue Ludarch':       { en: 'a rogue Ludarch',                                cs: 'odpadlický Ludarch',                        title: 'Rogue Ludarch' },
        'living collective':   { en: 'a living collective pretending to be one person', cs: 'kolektiv bytostí předstírající jednu osobu',   title: 'Living Collective' },
    },
    setting: {
        'scraper':           { en: "the Scraper's shifting floors",                     cs: 'proměnlivá patra Škrabáku',                                  title: 'Scraper' },
        'magical school':    { en: 'a murderous magical school',                       cs: 'vražedná magická škola',                                    title: 'Magical School' },
        'immortal mammal':   { en: 'a giant immortal mammal swimming in the ocean',    cs: 'obří nesmrtelný savec plovoucí v oceánu',                   title: 'Immortal Mammal' },
        'fungal wilds':      { en: 'the fungal wilds',                                 cs: 'houbová divočina',                                          title: 'Fungal Wilds' },
        'skyship':           { en: 'a skyship above the clouds',                       cs: 'vzducholoď mezi oblaky',                                    title: 'Skyship' },
        'markets':           { en: 'the subterranean markets',                         cs: 'podzemní trhy',                                             title: 'Subterranean Markets' },
        'living board game': { en: 'a war-torn board game that became real',           cs: 'válkou zničená desková hra, která se stala skutečností',    title: 'Living Board Game' },
        'god graveyard':     { en: 'the graveyard of dead gods',                       cs: 'hřbitov mrtvých bohů',                                      title: 'God Graveyard' },
    },
};

/**
 * Czech declension for the generated book titles. Titles put the protagonist and the setting
 * into real sentences, so each needs its cases: nom / gen / acc / ins, plus for settings the
 * prepositional phrases the templates use (`loc` = v/na + locative, `locb` = bare locative after
 * o/po, `from` = z/ze + genitive, `to` = do/na + direction). `g` drives který/která and -l/-la.
 */
const CS_TITLE_FORMS = {
    protagonist: {
        'disoriented tourist': { nom: 'dezorientovaný turista', gen: 'dezorientovaného turisty', acc: 'dezorientovaného turistu', ins: 'dezorientovaným turistou', g: 'm' },
        'bad scientist':       { nom: 'vědec renegát',          gen: 'vědce renegáta',           acc: 'vědce renegáta',           ins: 'vědcem renegátem',         g: 'm' },
        'mišutkenn':           { nom: 'mišutkenn',              gen: 'mišutkenna',               acc: 'mišutkenna',               ins: 'mišutkennem',              g: 'm' },
        'strange amnesiac':    { nom: 'amnezik',                gen: 'amnezika',                 acc: 'amnezika',                 ins: 'amnezikem',                g: 'm' },
        'fungal colony':       { nom: 'kolonie hub',            gen: 'kolonie hub',              acc: 'kolonii hub',              ins: 'kolonií hub',              g: 'f' },
        'dream detective':     { nom: 'snový detektiv',         gen: 'snového detektiva',        acc: 'snového detektiva',        ins: 'snovým detektivem',        g: 'm' },
        'rogue Ludarch':       { nom: 'odpadlický Ludarch',     gen: 'odpadlického Ludarcha',    acc: 'odpadlického Ludarcha',    ins: 'odpadlickým Ludarchem',    g: 'm' },
        'living collective':   { nom: 'kolektiv bytostí',       gen: 'kolektivu bytostí',        acc: 'kolektiv bytostí',         ins: 'kolektivem bytostí',       g: 'm' },
    },
    setting: {
        'scraper':           { nom: 'Škrabák',            gen: 'Škrabáku',            acc: 'Škrabák',             ins: 'Škrabákem',            loc: 've Škrabáku',           locb: 'Škrabáku',           from: 'ze Škrabáku',           to: 'do Škrabáku' },
        'magical school':    { nom: 'magická škola',      gen: 'magické školy',       acc: 'magickou školu',      ins: 'magickou školou',      loc: 'v magické škole',       locb: 'magické škole',      from: 'z magické školy',       to: 'do magické školy' },
        'immortal mammal':   { nom: 'nesmrtelný savec',   gen: 'nesmrtelného savce',  acc: 'nesmrtelného savce',  ins: 'nesmrtelným savcem',   loc: 'v nesmrtelném savci',   locb: 'nesmrtelném savci',  from: 'z nesmrtelného savce',  to: 'do nesmrtelného savce' },
        'fungal wilds':      { nom: 'houbová divočina',   gen: 'houbové divočiny',    acc: 'houbovou divočinu',   ins: 'houbovou divočinou',   loc: 'v houbové divočině',    locb: 'houbové divočině',   from: 'z houbové divočiny',    to: 'do houbové divočiny' },
        'skyship':           { nom: 'vzducholoď',         gen: 'vzducholodi',         acc: 'vzducholoď',          ins: 'vzducholodí',          loc: 've vzducholodi',        locb: 'vzducholodi',        from: 'ze vzducholodi',        to: 'do vzducholodi' },
        'markets':           { nom: 'podzemní trhy',      gen: 'podzemních trhů',     acc: 'podzemní trhy',       ins: 'podzemními trhy',      loc: 'na podzemních trzích',  locb: 'podzemních trzích',  from: 'z podzemních trhů',     to: 'na podzemní trhy' },
        'living board game': { nom: 'živá desková hra',   gen: 'živé deskové hry',    acc: 'živou deskovou hru',  ins: 'živou deskovou hrou',  loc: 'v živé deskové hře',    locb: 'živé deskové hře',   from: 'ze živé deskové hry',   to: 'do živé deskové hry' },
        'god graveyard':     { nom: 'hřbitov bohů',       gen: 'hřbitova bohů',       acc: 'hřbitov bohů',        ins: 'hřbitovem bohů',       loc: 'na hřbitově bohů',      locb: 'hřbitově bohů',      from: 'ze hřbitova bohů',      to: 'na hřbitov bohů' },
    },
};

export default class ScreamingCorkScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkScene' });

        // Get instance of the journal system
        this.journalSystem = JournalSystem.getInstance();
        this.isTransitioning = false;

        // Initialize book properties
        this.bookTopics = [];
        this.bookTone = '';
        this.bookGenre = '';
        this.bookProtagonist = '';
        this.bookSetting = '';
        this.maxTopics = 3; // Maximum number of inspirational topics
    }

    // Helper method to check if player has journal entry related to specific experiences
    hasJournalExperience(entryId) {
        return this.journalSystem.getEntry(entryId);
    }
    
    // Helper method for compatibility with dialog system
    hasJournalEntry(entryId) {
        return this.journalSystem.getEntry(entryId);
    }

    /** Display label for the current pick of `kind` (tone/genre/protagonist/setting); `form` = en | cs | title. */
    bookLabel(kind, form = 'en') {
        const value = { tone: this.bookTone, genre: this.bookGenre, protagonist: this.bookProtagonist, setting: this.bookSetting }[kind];
        const entry = BOOK_LABELS[kind]?.[value];
        return entry?.[form] ?? entry?.en ?? value ?? '';
    }

    // Helper method to get available inspirational topics based on journal entries
    getAvailableTopics() {
        const topics = [];
        // Get already selected topic IDs for filtering
        const selectedTopicIds = this.bookTopics ? this.bookTopics.map(topic => topic.id) : [];

        // Check for various journal entries that could serve as inspiration
        if (this.hasJournalExperience('scraper_sighting') && !selectedTopicIds.includes('scraper_building')) {
            topics.push({
                id: 'scraper_building',
                text: "The mysterious Scraper building",
                description: "A building that seems to shift and change, with floors that rearrange themselves"
            });
        }

        if (this.hasJournalExperience('lift_mother_meeting') && !selectedTopicIds.includes('lift_mother')) {
            topics.push({
                id: 'lift_mother',
                text: "The sentient elevator Lift-Mother",
                description: "An ancient, conscious elevator that remembers the city's history"
            });
        }

        if (this.hasJournalExperience('ortolan_meeting') && !selectedTopicIds.includes('ortolan')) {
            topics.push({
                id: 'ortolan',
                text: "Ortolan, the board game designer",
                description: "A character who creates complex games and seeks more arms for playtesting"
            });
        }

        if (this.hasJournalExperience('dream_queue') && !selectedTopicIds.includes('dream_queue')) {
            topics.push({
                id: 'dream_queue',
                text: "The Dream Queue",
                description: "A mysterious place where people's dreams are processed and stored"
            });
        }

        if (this.hasJournalExperience('spore_infection') && !selectedTopicIds.includes('spore_infection')) {
            topics.push({
                id: 'spore_infection',
                text: "The fungal spore infection",
                description: "The strange spores that infect people and change them"
            });
        }

        if (this.hasJournalExperience('vestigel_quest') && !selectedTopicIds.includes('vestigels')) {
            topics.push({
                id: 'vestigels',
                text: "The mysterious vestigels",
                description: "Ancient artifacts with unknown powers that you're collecting"
            });
        }

        if (this.hasJournalExperience('kloor_venn_meeting') && !selectedTopicIds.includes('kloor_venn')) {
            topics.push({
                id: 'kloor_venn',
                text: "The enigmatic Kloor Venn",
                description: "A character who speaks in riddles and seems to exist in multiple places at once"
            });
        }

        if (this.hasJournalExperience('skyship_sighting') && !selectedTopicIds.includes('skyships')) {
            topics.push({
                id: 'skyships',
                text: "The skyships above the city",
                description: "Massive vessels that drift through the clouds for reasons unknown"
            });
        }

        if (this.hasJournalExperience('rust_choir') && !selectedTopicIds.includes('rust_choir')) {
            topics.push({
                id: 'rust_choir',
                text: "The mysterious Rust Choir",
                description: "A faction that communicates through the vibrations of rusting metal"
            });
        }

        if (this.hasJournalExperience('burning_bear_festival') && !selectedTopicIds.includes('burning_bear')) {
            topics.push({
                id: 'burning_bear',
                text: "The Burning Bear Festival",
                description: "A controversial festival with deep meaning for Edgar"
            });
        }

        if (this.hasJournalExperience('board_games_war') && !selectedTopicIds.includes('board_games_war')) {
            topics.push({
                id: 'board_games_war',
                text: "The Board Games War",
                description: "An ancient conflict where Ludarchs — game designers who could rewrite reality — destroyed entire cities as pawns in their games"
            });
        }

        if (this.hasJournalExperience('noise_god_insight') && !selectedTopicIds.includes('noise_god')) {
            topics.push({
                id: 'noise_god',
                text: "The Noise God",
                description: "A forgotten deity that came to die in Upper Morkezela, whose presence still pulses through broken amplifiers and magnetic dust"
            });
        }

        if (this.hasJournalExperience('magnekin_reveal') && !selectedTopicIds.includes('magnekin')) {
            topics.push({
                id: 'magnekin',
                text: "Magnekin — A Civilization in One Body",
                description: "A collective of tiny cities held together by magnetic forces, disguised as a single humanoid citizen"
            });
        }

        if (this.hasJournalExperience('phor_calesta') && !selectedTopicIds.includes('god_graveyard')) {
            topics.push({
                id: 'god_graveyard',
                text: "The God Graveyard beneath the city",
                description: "Layers of fossilized dead gods lying beneath Upper Morkezela, their prayers turned to strata and halos crystallized into mineral deposits"
            });
        }

        // Always provide some default topics even if the player hasn't journaled much
        if (topics.length < 2) {
            // Only add default topics if they haven't been selected yet
            if (!selectedTopicIds.includes('city_mystery')) {
                topics.push({
                    id: 'city_mystery',
                    text: "The mysteries of Upper Morkezela",
                    description: "The strange city with its fungal growth and unusual inhabitants"
                });
            }

            if (!selectedTopicIds.includes('misutken_life')) {
                topics.push({
                    id: 'misutken_life',
                    text: "Life as a mišutkenn in the city",
                    description: "The challenges and perspectives of being different in Upper Morkezela"
                });
            }
        }

        return topics;
    }

    // Title from the picked genre × tone. One template per pair (the old if/if/else chains let the
    // last `else` win for most tones), built from Title-Case labels instead of raw ids.
    // `lang` = 'en' | 'cs' — the English title is what gets persisted (the nightlife cutscene is EN-only).
    generateBookTitle(lang = 'en') {
        if (lang === 'cs') return this.generateBookTitleCs();
        const P = this.bookLabel('protagonist', 'title');
        const S = this.bookLabel('setting', 'title');
        const T = this.bookTone;
        const pick = (byTone, fallback) => byTone[T] || fallback;

        switch (this.bookGenre) {
            case 'fungal techno':
                return pick({
                    tragic: `The Last ${P} of the ${S}`,
                    metaphysical: `${S} Recursions`,
                    romantic: `Techno Weekend: ${S} of Love`,
                    existential: `The ${P}'s Dilemma`,
                    political: `Revolution in the ${S}`,
                }, `The Ridiculous Adventures of a ${P} in the ${S}`);

            case 'postmodern':
                return pick({
                    existential: `${S}, ${S}, ${P}`,
                    metaphysical: `The Day the ${P} Discovered the ${S}'s Secret`,
                    romantic: `The Secret Life of the ${P} in the ${S}`,
                    political: `The ${P} Who Changed the ${S}`,
                    comical: `The Absurd Chronicles of the ${P} in the ${S}`,
                    tragic: `The Making of the ${P} from the ${S}`,
                }, `In the Name of the ${P}`);

            case 'urban fantasy':
                return pick({
                    political: `The ${P} of ${S} Street`,
                    metaphysical: `The Tale of the ${P}'s Travels to the ${S}`,
                    tragic: `The ${P} Who Lost the ${S}`,
                    comical: `The Hilarious Misadventures of the ${P} in the ${S}`,
                    romantic: `A Love Story in the ${S}: Life of the ${P}`,
                    existential: `What Can Change the ${P} and the Average ${S} Citizen?`,
                }, `The ${P} of the ${S}`);

            case 'funny animals':
                return pick({
                    political: `The ${P}'s Guide to Political Living`,
                    existential: `The ${P} Who Thought Too Much`,
                    tragic: `The Sad Tale of the ${P} Who Wished to Be a Zookeeper`,
                    romantic: `Finding Love in the ${S}: A ${P}'s Story`,
                    metaphysical: `The ${P} and the Meaning of Life`,
                }, `Crazy Cats of the ${S}: The Day the ${P} Went Wild`);

            case 'detective':
                return pick({
                    metaphysical: `The ${S} Mystery`,
                    tragic: `The Sad ${P} Case`,
                    comical: `The Hilarious ${P} and the ${S} Murder`,
                    existential: `The ${P} Travels to the ${S} to Find Himself and Make Some Existential Hardcore Decisions`,
                    romantic: `Love in the Time of ${S} Crimes`,
                    political: `The ${P} vs. the ${S} Conspiracy`,
                }, `The Case of the ${S}`);

            case 'weird fiction':
                return pick({
                    comical: `Making Fun of the ${P}'s Dreams of the ${S}`,
                    tragic: `The ${P} Who Cried Fungi`,
                    romantic: `A ${P}'s Guide to Love in the ${S}`,
                    political: `The Manifesto of the ${P}: How to Destroy the ${S} and Make a Revolution`,
                    existential: `The ${P} and the ${S} Paradox`,
                }, `The ${P} in the ${S} Labyrinth`);

            case 'mythic war epic':
                return pick({
                    tragic: `The Last Game of the ${P}`,
                    metaphysical: `${S}: Rules of the Fallen`,
                    romantic: `Love Between Moves: A ${P}'s War`,
                    existential: `Why the ${P} Stopped Playing`,
                    political: `The ${P}'s Gambit for the ${S}`,
                    comical: `The ${P} Who Cheated at the ${S}`,
                }, `${P}: Chronicle of the ${S} Wars`);

            case 'cosmic horror':
                return pick({
                    tragic: `The Silence After the ${S}`,
                    metaphysical: `${S}: What the ${P} Heard`,
                    romantic: `A ${P}'s Hymn to the Dying ${S}`,
                    existential: `The ${P} Who Listened Too Long`,
                    political: `Who Buried the Gods of the ${S}?`,
                    comical: `The ${P} and the Very Dead God of the ${S}`,
                }, `Beneath the ${S}: The ${P}'s Descent`);

            default:
                return `The ${P} of the ${S}`;
        }
    }

    // Czech counterpart of generateBookTitle — same genre × tone grid, real declension.
    generateBookTitleCs() {
        const p = CS_TITLE_FORMS.protagonist[this.bookProtagonist] || { nom: this.bookProtagonist || '', gen: '', acc: '', ins: '', g: 'm' };
        const s = CS_TITLE_FORMS.setting[this.bookSetting] || { nom: this.bookSetting || '', gen: '', acc: '', ins: '', loc: '', locb: '', from: '', to: '' };
        const f = p.g === 'f';
        const ktery = f ? 'která' : 'který';   // relative pronoun
        const la = f ? 'la' : 'l';             // past-tense ending
        const sam = f ? 'sama' : 'sám';
        const T = this.bookTone;
        const pick = (byTone, fallback) => byTone[T] || fallback;
        const cap = (t) => t.charAt(0).toUpperCase() + t.slice(1);

        let title;
        switch (this.bookGenre) {
            case 'fungal techno':
                title = pick({
                    tragic: `Poslední ${p.nom} ${s.from}`,
                    metaphysical: `Rekurze ${s.gen}`,
                    romantic: `Techno víkend: ${s.nom} lásky`,
                    existential: `Dilema ${p.gen}`,
                    political: `Revoluce ${s.loc}`,
                }, `Směšná dobrodružství ${p.gen} ${s.loc}`);
                break;
            case 'postmodern':
                title = pick({
                    existential: `${s.nom}, ${s.nom}, ${p.nom}`,
                    metaphysical: `Den, kdy ${p.nom} odhali${la} tajemství ${s.gen}`,
                    romantic: `Tajný život ${p.gen} ${s.loc}`,
                    political: `${p.nom}, ${ktery} změni${la} ${s.acc}`,
                    comical: `Absurdní kroniky ${p.gen} ${s.loc}`,
                    tragic: `Zrození ${p.gen} ${s.from}`,
                }, `Ve jménu ${p.gen}`);
                break;
            case 'urban fantasy':
                title = pick({
                    political: `${p.nom} z ulice ${s.gen}`,
                    metaphysical: `Příběh o cestách ${p.gen} ${s.to}`,
                    tragic: `${p.nom}, ${ktery} ztrati${la} ${s.acc}`,
                    comical: `Veselé nehody ${p.gen} ${s.loc}`,
                    romantic: `Milostný příběh ${s.loc}: život ${p.gen}`,
                    existential: `Co může změnit ${p.acc} a průměrného občana ${s.gen}?`,
                }, `${p.nom} ${s.from}`);
                break;
            case 'funny animals':
                title = pick({
                    political: `Průvodce ${p.gen} politickým životem`,
                    existential: `${p.nom}, ${ktery} příliš přemýšle${la}`,
                    tragic: `Smutný příběh ${p.gen}, ${ktery} chtě${la} být ošetřovatelem v zoo`,
                    romantic: `Hledání lásky ${s.loc}: příběh ${p.gen}`,
                    metaphysical: `${p.nom} a smysl života`,
                }, `Šílené kočky ${s.gen}: den, kdy se ${p.nom} zblázni${la}`);
                break;
            case 'detective':
                title = pick({
                    metaphysical: `Záhada ${s.gen}`,
                    tragic: `Smutný případ ${p.gen}`,
                    comical: `${f ? 'Veselá' : 'Veselý'} ${p.nom} a vražda ${s.loc}`,
                    existential: `${p.nom} jede ${s.to}, aby naše${la} ${sam} sebe a učini${la} pár existenciálně hardcore rozhodnutí`,
                    romantic: `Láska za časů zločinů ${s.gen}`,
                    political: `${p.nom} versus spiknutí ${s.gen}`,
                }, `Případ ${s.gen}`);
                break;
            case 'weird fiction':
                title = pick({
                    comical: `Jak si utahovat ze snů ${p.gen} o ${s.locb}`,
                    tragic: `${p.nom}, ${ktery} plaka${la} houby`,
                    romantic: `Průvodce ${p.gen} láskou ${s.loc}`,
                    political: `Manifest ${p.gen}: jak zničit ${s.acc} a udělat revoluci`,
                    existential: `${p.nom} a paradox ${s.gen}`,
                }, `${p.nom} v labyrintu ${s.gen}`);
                break;
            case 'mythic war epic':
                title = pick({
                    tragic: `Poslední hra ${p.gen}`,
                    metaphysical: `${s.nom}: pravidla padlých`,
                    romantic: `Láska mezi tahy: válka ${p.gen}`,
                    existential: `Proč ${p.nom} přesta${la} hrát`,
                    political: `Gambit ${p.gen} o ${s.locb}`,
                    comical: `${p.nom}, ${ktery} podvádě${la} ${s.loc}`,
                }, `${p.nom}: kronika válek o ${s.acc}`);
                break;
            case 'cosmic horror':
                title = pick({
                    tragic: `Ticho po ${s.locb}`,
                    metaphysical: `${s.nom}: co ${p.nom} slyše${la}`,
                    romantic: `Hymna ${p.gen} na umírající ${s.acc}`,
                    existential: `${p.nom}, ${ktery} naslouchal${f ? 'a' : ''} příliš dlouho`,
                    political: `Kdo pohřbil bohy ${s.gen}?`,
                    comical: `${p.nom} a velmi mrtvý bůh ${s.gen}`,
                }, `Pod ${s.ins}: sestup ${p.gen}`);
                break;
            default:
                title = `${p.nom} ${s.from}`;
        }
        return cap(title);
    }

    get dialogContent() {
        // QuestSystem tracks completion as `isComplete` (there is no `status` field).
        const bookDone = !!this.questSystem.getQuest('edgar_book')?.isComplete;
        // Finishing the book while the Vestigel hunt is open hands the token over in the farewell.
        // Computed here (the getter runs at show time) — assigning into `this.dialogContent.x.text`
        // from an onTrigger is lost, because every getter call builds a fresh object.
        const farewellGivesVestigel = !!this.questSystem.getQuest('the_three_vestigels') && !this.hasItem('vestigel');
        const cs = LanguageSystem.getInstance?.().getLanguage?.() === 'cs';

        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs

            // Edgar Eskola dialog
            speaker: 'Edgar Eskola',
            edgar_start: {
        
                text: "The ursine creature shifts uncomfortably. He glances at you with a mix of wariness and curiosity.",
                options: [
                    { text: "Hello there.", key: 'hello_there', next: "edgar_greeting" },
                    { text: "What are you doing here?", key: 'what_are_you_doing_here', next: "edgar_purpose" },
                    { text: "Tell me about yourself.", key: 'tell_me_about_yourself', next: "edgar_background" },
                    { text: "What do you know about the Burning Bear Festival?", key: 'what_do_you_know_about_the_burning_bear_festival', next: "edgar_festival" },
                    // Dynamically add vestigel option if player has the quest
                    ...(this.questSystem.getQuest('the_three_vestigels') ? [
                        { text: "I'm looking for a vestigel, I heard you might have one.", key: 'im_looking_for_a_vestigel_i_heard_you_might_have_o', next: "edgar_vestigel" }
                    ] : []),
                    // Only show book topics option if quest is active but not completed
                    ...(this.questSystem.getQuest('edgar_book') && !this.questSystem.getQuest('edgar_book').isComplete ? [
                        { text: "Let's start with some inspirational topics.", key: 'lets_start_with_some_inspirational_topics', next: "edgar_book_topics" }
                    ] : []),
                    // Before the finale: Edgar's overlooked-places perspective on the Egg Cathedral
                    ...(this.hasJournalEntry('met_infinite_fold') ? [
                        { text: "[Before entering the cathedral] You've worked everywhere in this city. Is there a way into the Egg Cathedral nobody talks about?", key: 'edgar_cathedral_ask', next: "edgar_cathedral_way" }
                    ] : []),
                ],
                onTrigger: () => {
                    // Add journal entry about meeting Edgar Eskola
                    if (!this.hasJournalExperience('edgar_eskola_meeting')) {
                        this.addJournalEntry(
                            'edgar_eskola_meeting',
                            'Edgar Eskola — The Mišutkenn of Screaming Cork',
                            'I met Edgar Eskola, a mišutkenn patron at the Screaming Cork tavern. He seems uncomfortable around humans, which is understandable given the history of prejudice against his kind in Upper Morkezela. Despite his bearish appearance, there\'s a softness to him — an intellectual quality that suggests he\'s more than the city\'s stereotypes would imply.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Edgar Eskola', location: 'Screaming Cork' }
                        );
                    }
                }
            },
            edgar_greeting: {
        
                text: "Mmm. Hello. Not often people choose to speak with me. Most avoid mišutkenn if they can help it.",
                options: [
                    { text: "Why is that?", key: 'why_is_that', next: "edgar_prejudice" },
                    { text: "What are mišutkenn?", key: 'what_are_miutkenn', next: "edgar_what" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_what: {
        
                text: "Mišutkenn are... well, we're not exactly human. We're... different.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(1, 0); // the G/D system announces the change itself
                }
            },
            edgar_prejudice: {
                text: "History. Superstition. Fear of what's different. Take your pick. The founders of this city drove my ancestors from the Remaper Hills. Now we're just... tolerated. At best.",
                options: [
                    { text: "That's unfortunate.", key: 'thats_unfortunate', next: "edgar_unfortunate" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_unfortunate: {
        
                text: "That's one way to put it. But I've learned to live with it. Mostly.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_purpose: {
                text: "Waiting. Watching. Avoiding the preparations for that cursed festival. The Screaming Cork is one of the few places that doesn't go all-in on the bear burning nonsense.",
                options: [
                    { text: "You don't like the festival?", key: 'you_dont_like_the_festival', next: "edgar_festival" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_background: {
        
                text: "Not much to tell. I've had more jobs than I can count. Janitor at 1140 Scraper, professional imaginator, clerk, art model, airship mechanic, meat packer... None of them stuck. Not entirely my fault, though.",
                options: [
                    { text: "Professional imaginator?", key: 'professional_imaginator', next: "edgar_imaginator" },
                    { text: "Why didn't they work out?", key: 'why_didnt_they_work_out', next: "edgar_jobs" },
                    { text: "What would you like to do?", key: 'what_would_you_like_to_do', next: "edgar_dream_job" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_dream_job: {
        
                text: "I've tried everything. Janitor. Clerk. Meat assembler. Imaginator. But I've never been anything truly mine. I think… I want to write a book. But I don't know what it's about yet.",
                options: [
                    ...(!this.questSystem.getQuest('edgar_book') ? [
                        { text: "I can help you write the book", key: 'i_can_help_you_write_the_book', next: "edgar_book" }
                    ] : []),
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    // Add journal entry about Edgar's aspiration
                    if (!this.hasJournalExperience('edgar_aspiration')) {
                        this.addJournalEntry(
                            'edgar_aspiration',
                            'Edgar\'s Literary Aspirations',
                            'Edgar Eskola, the bearish mišutkenn from the Screaming Cork, expressed his desire to write a book. Despite having worked many jobs in the city, he feels he hasn\'t found his true calling. Writing could be his chance to create something truly his own.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Edgar Eskola', location: 'Screaming Cork' }
                        );
                    }
                }
            },
            edgar_book: {
                text: "You would... do that for me? Thank you. I don't know what it's about yet. But I'm open to suggestions.",
                options: [
                    { text: "Let's start with some inspirational topics", key: 'lets_start_with_some_inspirational_topics', next: "edgar_book_topics" },
                    { text: "I will come back when I have an idea", key: 'i_will_come_back_when_i_have_an_idea', next: "edgar_start" }
                ],
                onTrigger: () => {
                    if (!this.questSystem.getQuest('edgar_book')) {
                        this.questSystem.addQuest(
                            'edgar_book',
                            'Help Edgar to write a book',
                            'Edgar Eskola mentioned he wants to write a book. I should help him.'
                        );

                        // Add journal entry about agreeing to help with the book
                        this.addJournalEntry(
                            'edgar_book_quest_start',
                            'A Promise to a Writer',
                            'I offered to help Edgar Eskola write his book. He seems genuinely touched by the gesture, though neither of us have a clear idea of what the book should be about yet. My experiences in this strange city might provide inspiration for his story.',
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                quest: 'edgar_book'
                            }
                        );
                    }
                }
            },

            // Topic selection dialog - lets player choose inspirational topics
            edgar_book_topics: {
                text: "What inspires you about this city? What experiences might make a good story? I've been stuck in the same routines for so long, I need fresh perspectives.",
                // `key: topic.id` lets the cs file translate the labels. The pick is parked in
                // `currentTopic`; edgar_book_topic_selected's onTrigger records it (topic list +
                // journal) — previously nothing ever set currentTopic, so that journal never fired.
                options: this.getAvailableTopics().map(function(topic) {
                    return {
                        text: topic.text,
                        key: topic.id,
                        next: "edgar_book_topic_selected",
                        onSelect: function() {
                            this.currentTopic = topic;
                        }
                    };
                }),
            },

            // Topic selected dialog - adds the selected topic and returns to topic selection
            edgar_book_topic_selected: {
                text: "That's a fascinating topic! It gives me some interesting ideas to work with.",
                // Instead of spreading conditionally in the declaration, we'll set this in a function
                options: function() {
                    const options = [];
                    
                    if (this.bookTopics && this.bookTopics.length >= 3) {
                        options.push({ text: "I think we have enough topics", key: 'i_think_we_have_enough_topics', next: "edgar_book_tone" });
                    } else options.push({ text: "Let's continue", key: 'lets_continue', next: "edgar_book_topics" })
                    
                    return options;
                },
                hideCloseOption: true,
                onTrigger: () => {
                    // Add the selected topic to our list
                    if (this.currentTopic) {
                        this.bookTopics.push(this.currentTopic);

                        // Add journal entry about suggesting this topic
                        this.addJournalEntry(
                            `edgar_book_topic_${this.currentTopic.id}`,
                            `Book Inspiration: ${this.currentTopic.text}`,
                            `I suggested ${this.currentTopic.text} as inspiration for Edgar's book. ${this.currentTopic.description}. Edgar seemed intrigued by the concept and jotted down some notes.`,
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                quest: 'edgar_book'
                            }
                        );

                        this.currentTopic = null;
                    }
                }
            },

            // Tone selection dialog - choose emotional tone for the book
            edgar_book_tone: {
        
                text: "Now that we have some topics to work with, what tone should the book have? I'm thinking about the emotional feel of it.",
                hideCloseOption: true,
                options: [
                    { text: "Tragic — a tale of sorrow and loss", key: 'tragic_a_tale_of_sorrow_and_loss', next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'tragic'; } },
                    { text: "Metaphysical — exploring nature of reality", key: 'metaphysical_exploring_consciousness', next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'metaphysical'; } },
                    { text: "Romantic — focusing on connections", key: 'romantic_focusing_on_connections', next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'romantic'; } },
                    { text: "Existential — pondering meaning of life and mortality", key: 'existential_pondering_meaning_and_mortality', next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'existential'; } },
                    { text: "Political — examining power dynamics", key: 'political_examining_power_dynamics', next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'political'; } },
                    { text: "Comical — finding humor in the strange", key: 'comical_finding_humor_in_the_strange', next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'comical'; } }
                ]
            },

            // Tone selected dialog
            edgar_book_tone_selected: {
                text: "That's a great tone choice! It will give the book a distinct emotional flavor that should resonate with readers.",
                options: [
                    { text: "Now let's choose a genre for the book", key: 'now_lets_choose_a_genre_for_the_book', next: "edgar_book_genre" }
                ],
                hideCloseOption: true,
                onTrigger: () => {
                    // Add journal entry about the tone selection
                    let toneDescription;
                    switch (this.bookTone) {
                        case 'tragic': toneDescription = 'a somber exploration of loss and sorrow'; break;
                        case 'metaphysical': toneDescription = 'a deep dive into questions of consciousness and reality'; break;
                        case 'romantic': toneDescription = 'a story focused on connection and love'; break;
                        case 'existential': toneDescription = 'a meditation on meaning and mortality'; break;
                        case 'political': toneDescription = 'an examination of power structures and their effects'; break;
                        case 'comical': toneDescription = 'a humorous look at the absurdities of life'; break;
                        default: toneDescription = 'an emotional journey'; break;
                    }

                    this.addJournalEntry(
                        `edgar_book_tone_${this.bookTone}`,
                        `Book Tone: ${this.bookTone.charAt(0).toUpperCase() + this.bookTone.slice(1)}`,
                        `I suggested that Edgar's book should have a ${this.bookTone} tone - ${toneDescription}. He seemed to embrace the idea, considering how it would fit with the inspirations we discussed.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book'
                        }
                    );
                }
            },

            // Genre selection dialog - choose genre for the book
            edgar_book_genre: {
                hideCloseOption: true,
                text: "The tone is set, but what genre should this story be? I've been exploring some experimental options.",
                options: [
                    { text: "Fungal techno-thriller", key: 'fungal_technothriller', next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'fungal techno'; } },
                    { text: "Postmodern novel", key: 'postmodern_novel', next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'postmodern'; } },
                    { text: "Urban fantasy", key: 'urban_fantasy', next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'urban fantasy'; } },
                    { text: "Funny animals with depression", key: 'funny_animals_with_depression', next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'funny animals'; } },
                    { text: "Detective novel", key: 'detective_novel', next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'detective'; } },
                    { text: "Dreamy weird fiction", key: 'dreamy_weird_fiction', next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'weird fiction'; } },
                    { text: "Mythic war epic", key: 'mythic_war_epic', next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'mythic war epic'; } },
                    { text: "Cosmic horror", key: 'cosmic_horror', next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'cosmic horror'; } }
                ]
            },

            // Genre selected dialog
            edgar_book_genre_selected: {
                hideCloseOption: true,
                text: "That genre is perfect! It captures exactly the kind of story that would work in this strange city.",
                options: [
                    { text: "Let's decide on the main protagonist", key: 'lets_decide_on_the_main_protagonist', next: "edgar_book_protagonist" }
                ],
                onTrigger: () => {
                    // Add journal entry about the genre selection
                    let genreDescription;
                    switch (this.bookGenre) {
                        case 'fungal techno': genreDescription = 'combining biotechnology with horror elements'; break;
                        case 'postmodern': genreDescription = 'breaking conventional narrative rules'; break;
                        case 'urban fantasy': genreDescription = 'bringing magical elements into the city setting'; break;
                        case 'funny animals': genreDescription = 'using anthropomorphic characters to explore deeper emotions'; break;
                        case 'detective': genreDescription = 'following clues to unravel mysteries'; break;
                        case 'weird fiction': genreDescription = 'blurring the lines between reality and dreams'; break;
                        case 'mythic war epic': genreDescription = 'an epic recounting of ancient wars where games rewrote reality'; break;
                        case 'cosmic horror': genreDescription = 'confronting the terrifying remnants of dead gods and forgotten entities'; break;
                        default: genreDescription = 'a compelling literary style'; break;
                    }

                    this.addJournalEntry(
                        `edgar_book_genre_${this.bookGenre}`,
                        `Book Genre: ${this.bookGenre.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
                        `I suggested that Edgar write a ${this.bookGenre.replace('_', ' ')} - ${genreDescription}. Edgar seemed to see the potential in using this genre to express his experiences in Upper Morkezela.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book'
                        }
                    );
                }
            },

            // Protagonist selection dialog
            edgar_book_protagonist: {
                hideCloseOption: true,
                text: "Who should the main character be? What kind of protagonist would fit this story?",
                options: [
                    { text: "A disoriented tourist", key: 'a_disoriented_tourist', next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'disoriented tourist'; } },
                    { text: "A renegade fungal scientist", key: 'a_renegade_fungal_scientist', next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'bad scientist'; } },
                    { text: "A mišutkenn seeking identity", key: 'a_miutkenn_seeking_identity', next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'mišutkenn'; } },
                    { text: "An amnesiac with strange abilities", key: 'an_amnesiac_with_strange_abilities', next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'strange amnesiac'; } },
                    { text: "A sentient fungal colony", key: 'a_sentient_fungal_colony', next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'fungal colony'; } },
                    { text: "A dream detective", key: 'a_dream_detective', next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'dream detective'; } },
                    { text: "A rogue Ludarch", key: 'a_rogue_ludarch', next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'rogue Ludarch'; } },
                    { text: "A living collective pretending to be one person", key: 'a_living_collective_pretending_to_be_one_person', next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'living collective'; } },
                ]
            },

            // Protagonist selected dialog
            edgar_book_protagonist_selected: {
                hideCloseOption: true,
                text: "That's a fascinating protagonist choice! I can already imagine how they would navigate through the story and engage with readers.",
                options: [
                    { text: "Finally, let's choose a setting", key: 'finally_lets_choose_a_setting', next: "edgar_book_setting" }
                ],
                onTrigger: () => {
                    // Add journal entry about the protagonist selection
                    let protagonistDescription;
                    switch (this.bookProtagonist) {
                        case 'disoriented tourist': protagonistDescription = 'experiencing the strange city with fresh, confused eyes'; break;
                        case 'bad scientist': protagonistDescription = 'delving into the mysteries of the city\'s fungal biology'; break;
                        case 'mišutkenn': protagonistDescription = 'searching for identity and belonging between worlds'; break;
                        case 'strange amnesiac': protagonistDescription = 'uncovering their past while wielding unusual abilities'; break;
                        case 'fungal colony': protagonistDescription = 'a collective consciousness experiencing individuality'; break;
                        case 'dream detective': protagonistDescription = 'solving mysteries by entering people\'s dreams'; break;
                        case 'rogue Ludarch': protagonistDescription = 'the last reality-bending game designer, haunted by the wars they helped start'; break;
                        case 'living collective': protagonistDescription = 'millions of tiny beings pretending to be one person, experiencing the big world for the first time'; break;
                        default: protagonistDescription = 'navigating the complexities of Upper Morkezela'; break;
                    }

                    this.addJournalEntry(
                        `edgar_book_protagonist_${this.bookProtagonist}`,
                        `Book Protagonist: ${this.bookProtagonist.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
                        `I suggested that the main character of Edgar's book should be a ${this.bookProtagonist.replace('_', ' ')} - ${protagonistDescription}. Edgar seemed excited about developing this character for his story.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book'
                        }
                    );
                }
            },

            // Setting selection dialog
            edgar_book_setting: {
                hideCloseOption: true,
                text: "And finally, where should this story take place? What's the setting?",
                options: [
                    { text: "The Scraper's shifting floors", key: 'the_scrapers_shifting_floors', next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'scraper'; } },
                    { text: "A murderous magical school", key: 'a_murderous_magical_school', next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'magical school'; } },
                    { text: "A giant immortal mammal, swimming in the ocean", key: 'a_giant_immortal_mammal_swimming_in_the_ocean', next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'immortal mammal'; } },
                    { text: "The fungal wilds", key: 'the_fungal_wilds', next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'fungal wilds'; } },
                    { text: "A skyship above the clouds", key: 'a_skyship_above_the_clouds', next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'skyship'; } },
                    { text: "The subterranean markets", key: 'the_subterranean_markets', next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'markets'; } },
                    { text: "A war-torn board game that became real", key: 'a_wartorn_board_game_that_became_real', next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'living board game'; } },
                    { text: "The graveyard of dead gods", key: 'the_graveyard_of_dead_gods', next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'god graveyard'; } }
                ]
            },

            // Setting selected dialog
            edgar_book_setting_selected: {
                hideCloseOption: true,
                text: "What an excellent setting! It creates the perfect atmosphere and provides so many narrative possibilities.",
                options: [
                    { text: "Let's see what book we've created", key: 'lets_see_what_book_weve_created', next: "edgar_book_completion" }
                ],
                onTrigger: () => {
                    // Add journal entry about the setting selection
                    let settingDescription;
                    switch (this.bookSetting) {
                        case 'scraper': settingDescription = 'a mysterious building with floors that rearrange themselves'; break;
                        case 'magical school': settingDescription = 'the magical school, where kids are dying every year under suspicious circumstances, except the main protagonist, of course'; break;
                        case 'immortal mammal': settingDescription = 'an enormous creature without a name, swimming eternally in the depths'; break;
                        case 'fungal wilds': settingDescription = 'the untamed areas where fungal growths take their most primordial forms'; break;
                        case 'skyship': settingDescription = 'a vessel drifting above the clouds, isolated yet connected to the city below'; break;
                        case 'markets': settingDescription = 'the underground commercial spaces where anything can be traded'; break;
                        case 'living board game': settingDescription = 'a war-torn board game that became real, its miniaturized world now populated by sentient pawns'; break;
                        case 'god graveyard': settingDescription = 'the fossilized layers of dead gods beneath the city, where prayers turned to stone and halos became crystal'; break;
                        default: settingDescription = 'a compelling environment for the story'; break;
                    }

                    this.addJournalEntry(
                        `edgar_book_setting_${this.bookSetting}`,
                        `Book Setting: ${this.bookSetting.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
                        `I suggested that Edgar's book should be set in ${this.bookSetting.replace('_', ' ')} - ${settingDescription}. Edgar seemed inspired by this location and how it would interact with the story's other elements.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book'
                        }
                    );
                }
            },

            // Final book completion dialog
            edgar_book_completion: {
                // Assembled at show time from the player's picks. Localized here (like the Guardian's
                // dynamic lines) because the cs dialog file can't template — its `text: ""` was ignored
                // and the whole payoff showed in English. Labels come from BOOK_LABELS, not raw ids.
                text: cs
                    ? `„${this.generateBookTitle('cs')}"... To je dokonalé! Spojuje všechny prvky do něčeho soudržného, a přitom překvapivého. Už vidím, jak se celý příběh rýsuje. Hlavní postava: ${this.bookLabel('protagonist', 'cs')}. Žánr: ${this.bookLabel('genre', 'cs')} — to se mi líbí. A ten celkově ${this.bookLabel('tone', 'cs')} tón, pěkný tah. Prostředí: ${this.bookLabel('setting', 'cs')}, velmi originální. Myslím, že máme v rukou trhák! Děkuji, příteli. Pomohl jste mi najít můj spisovatelský hlas. Pustím se do toho hned. Až to vyjde, dostanete první výtisk, slibuji.`
                    : `"${this.generateBookTitle()}"... This is perfect! It combines all the elements into something cohesive yet surprising. I can see the whole narrative taking shape already. It will be about ${this.bookLabel('protagonist')} and the genre will be ${this.bookLabel('genre')}, I like that. Nice touch with the overall ${this.bookLabel('tone')} book tone. The setting is ${this.bookLabel('setting')}, very original. I think we have an ultimate hit on our hands! Thank you, my friend. You've helped me find my voice as a writer. I'll start working on it right away. When it's published, you'll get the first copy, I promise.`,
                options: [
                    { text: "I look forward to reading it", key: 'i_look_forward_to_reading_it', next: "edgar_book_farewell" },
                    { text: "Make sure to credit me as co-author", key: 'make_sure_to_credit_me_as_coauthor', next: "edgar_book_farewell" }
                ],
                onTrigger: () => {
                    // Generate book title
                    const bookTitle = this.generateBookTitle();

                    // Complete the quest
                    this.questSystem.updateQuest('edgar_book', 'You have helped Edgar Eskola develop his book concept. He is very grateful to you.', 'completed');
                    this.questSystem.completeQuest('edgar_book');

                    // Journal entry about the completed book. Built at runtime from the picks, so it
                    // is localized here (lang/*/journal.js can't template); topic labels come back
                    // translated through the same lookup the dialog options use.
                    const topicLabels = LanguageSystem.getInstance().translateDialog(
                        this.scene.key, 'edgar_book_topics',
                        { options: this.bookTopics.map(t => ({ text: t.text, key: t.id })) }
                    ).options.map(o => o.text);
                    const L = (kind) => this.bookLabel(kind, cs ? 'cs' : 'en');
                    const bookTitleCs = this.generateBookTitle('cs');
                    const shownTitle = cs ? bookTitleCs : bookTitle;
                    const journalTitle = cs ? `Edgarova kniha: „${shownTitle}"` : `Edgar's Book: "${shownTitle}"`;
                    const journalText = cs
                        ? `Pomohl jsem Edgaru Eskolovi vymyslet koncept jeho knihy. ${topicLabels.length ? 'Inspirovali jsme se tématy: ' + topicLabels.map(t => `„${t}"`).join(', ') + '. ' : ''}Žánr: ${L('genre')}, tón: ${L('tone')}. Hlavní postava: ${L('protagonist')}. Prostředí: ${L('setting')}. Edgar knihu nazval „${shownTitle}" a vypadal, že se do psaní opravdu těší. Slíbil mi první výtisk, až vyjde.`
                        : `I helped Edgar Eskola develop his book concept. ${topicLabels.length ? 'Drawing inspiration from ' + topicLabels.map(t => t.toLowerCase()).join(', ') + ', ' : ''}we created a ${L('tone')} ${L('genre')} featuring ${L('protagonist')} in ${L('setting')}. Edgar titled it "${bookTitle}" and seemed genuinely inspired to begin writing. He promised me the first copy when it's published.`;

                    this.addJournalEntry(
                        'edgar_book_completed',
                        journalTitle,
                        journalText,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book',
                            quest_status: 'completed',
                            // Persist the chosen book variant so later scenes (e.g. the
                            // Day 1 nightlife cutscene) can reference the exact book.
                            book_title: bookTitle,       // EN — the nightlife cutscene captions are English
                            book_title_cs: bookTitleCs,
                            book_genre: this.bookGenre,
                            book_tone: this.bookTone,
                            book_protagonist: this.bookProtagonist,
                            book_setting: this.bookSetting,
                            book_topics: this.bookTopics.map(t => t.text)
                        }
                    );
                    
                }
            },

            // Final farewell after completing the book quest
            edgar_book_farewell: {
                textKey: farewellGivesVestigel ? 'vestigel' : 'plain',
                text: farewellGivesVestigel
                    ? "I should get to work now. The ideas are flowing, and I don't want to lose them. Oh, and as promised, here's the vestigel. It's of more use to you than to me. Thank you again for your help. Feel free to check in on my progress sometime."
                    : "I should get to work now. The ideas are flowing, and I don't want to lose them. Thank you again for your help. Feel free to check in on my progress sometime.",
                options: [
                    { text: "Good luck, Edgar", key: 'good_luck_edgar', next: "closeDialog" }
                ],
                onTrigger: () => {
                    
                    // Check if the player has the vestigel quest and doesn't already have the vestigel
                    if (this.questSystem.getQuest('the_three_vestigels') && !this.hasItem('vestigel')) {
                        
                        // Create the vestigel item
                        const vestigelItem = {
                            id: 'vestigel',
                            name: 'Writer\'s Vestigel',
                            description: 'A small, intricately carved token that Edgar found hidden inside a plush toy. It seems to have some mysterious significance.',
                            icon: 'vestigel',
                            usable: false,
                            consumable: false,
                            value: 0
                        };
                        
                        // Add the vestigel to inventory
                        this.addItemToInventory(vestigelItem);
                        
                        // Update quest progress
                        this.questSystem.updateQuest('the_three_vestigels', 'Received a vestigel from Edgar Eskola in exchange for helping with his book.', 'edgar_vestigel_acquired');
                        
                        // Add journal entry about receiving the vestigel
                        this.addJournalEntry(
                            'edgar_vestigel_received',
                            'The Writer\'s Token',
                            'Today I acquired one of the three vestigels from Edgar Eskola at the Screaming Cork. He gave it to me in exchange for my help with writing his book. The vestigel had been hidden inside a plush toy that Edgar had bought from a street vendor. He mentioned that the vendor refused to take it back when offered, citing "professional honor." The vestigel itself is small but intricately carved, clearly valuable to someone who knows its purpose.',
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                item: 'Vestigel',
                                quest: 'the_three_vestigels',
                                importance: 'high'
                            }
                        );
                    }
                }
            },

            edgar_imaginator: {
        
                text: "I dreamed up locations and characters for Dr. Elphi Quarn's games. Turns out my imagination was too... wild. Too erratic, they said. My dreams were 'unusable.' Their loss.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_jobs: {
        
                text: "Bad timing, mostly. The Scraper took the Rust Choir and stopped being an official part of the city — no need for a janitor then. The other jobs... Well, being a mišutkenn doesn't help with job security in this city.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_festival: {
        
                text: "The Burning Bear Festival? A cruel reminder of an ancient 'victory' over my kind. They stuff bear skins with things they want to be rid of, then burn them at midnight. Some fill them with pests, bad habits, vices... others with rivals, if the rumors are true.",
                options: [
                    { text: "That sounds disturbing.", key: 'that_sounds_disturbing', next: "edgar_disturbing" },
                    { text: "It's just tradition, isn't it?", key: 'its_just_tradition_isnt_it', next: "edgar_tradition" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_disturbing: {
                text: "It is. Imagine being surrounded by burning effigies that look like your ancestors. The city lights up with fires of different colors and smells, while I hide away, waiting for it to end.",
                options: [
                    { text: "I'm sorry to hear that.", key: 'im_sorry_to_hear_that', next: "edgar_sympathy" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_tradition: {
        
                text: "Tradition? Traditions can be cruel. Just because something has been done for generations doesn't make it right. But few in this city would agree with me.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_sympathy: {
        
                text: "Your sympathy is... unexpected. But appreciated. Perhaps not everyone in this city is as thoughtless as I've come to believe.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(1, 0); // the G/D system announces the change itself
                }
            },

            // New vestigel dialog path
            edgar_vestigel: {
        
                text: "A vestigel? Yes... I do have one. It's a peculiar object, a small, but apparently valuable token. It was hidden inside a plush toy. See, I rather bought it from a street vendor, when I saw it. Otherwise somebody would use it for that cursed festival. The vendor didn't know about the Vestigel, but she surprisingly refused to take it back, when I offered it to her. She said something about a professional honor, hmm...",
                options: [
                    // Use ternary to determine next dialog based on book quest completion status
                    { text: "I need it for an important purpose.", key: 'i_need_it_for_an_important_purpose', next: bookDone ? "edgar_vestigel_give_completed" : "edgar_vestigel_need" },
                    { text: "May I have it?", key: 'may_i_have_it', next: bookDone ? "edgar_vestigel_give_completed" : "edgar_vestigel_request" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_vestigel_need: {
        
                text: "Important purpose, you say? Well, I don't really *need* it, but I kinda like it. Maybe you could do something for me in exchange?",
                options: [
                    { text: "What do you need?", key: 'what_do_you_need', next: "edgar_vestigel_convince" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_vestigel_request: {
        
                text: "Just like that? You know that's a valuable trinket. I wouldn't give it away without good reason.",
                options: [
                    { text: "What would convince you to part with it?", key: 'what_would_convince_you_to_part_with_it', next: "edgar_vestigel_convince" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_vestigel_convince: {
        
                text: "Hmm...",
                options: [
                    // Determine which option to show based on book quest status
                    ...(bookDone ? [
                        { text: "I already helped you write your book.", key: 'i_already_helped_you_write_your_book', next: "edgar_vestigel_give_completed" }
                    ] : this.questSystem.getQuest('edgar_book') ? [
                        { text: "I could help with your book, as we discussed earlier.", key: 'i_could_help_with_your_book_as_we_discussed_earlie', next: "edgar_vestigel_book_help" }
                    ] : [
                        { text: "Maybe I could help you with something.", key: 'maybe_i_could_help_you_with_something', next: "edgar_vestigel_offer" }
                    ]),
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_vestigel_offer: {
                text: "Hmm... maybe you could help me with something. Do you know something about literature? I would like to become... a writer. But I don't know where to start. Would you help me with that? I've been struggling to find a voice, a story worth telling. If you could truly help me...",
                options: [
                    { text: "I'll do my best.", key: 'ill_do_my_best', next: "edgar_vestigel_thanks" }
                ],
                onTrigger: () => {
                    this.questSystem.addQuest(
                        'edgar_book',
                        'Help Edgar to write a book',
                        'Edgar Eskola mentioned he wants to write a book. I should help him.'
                    );

                    // Add journal entry about the vestigel negotiation
                    this.addJournalEntry(
                        'edgar_vestigel_negotiation',
                        'A Deal with Edgar',
                        'Edgar Eskola agreed to trade his vestigel in exchange for help with writing his book. The vestigel seems valuable to him, but his desire to become an author is stronger. This arrangement could benefit us both - he gets his book, and I get the vestigel I need.',
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            item: 'Vestigel',
                            quest: 'the_three_vestigels'
                        }
                    );
                }
            },
            edgar_vestigel_book_help: {
                text: "Yes, you did offer to help with my book. A fair exchange — your help for the vestigel. I've been collecting ideas but haven't made much progress.",
                options: [
                    { text: "I'll make sure your book becomes a reality.", key: 'ill_make_sure_your_book_becomes_a_reality', next: "edgar_vestigel_thanks" }
                ]
            },
            
            // New dialog for when player asks for vestigel after book is completed
            edgar_vestigel_give_completed: {
        
                text: "Oh, you're interested in the vestigel? After all your help with my book, I'd be happy to give it to you. It's of more use to you than to me. Here, take it with my gratitude.",
                options: [
                    { text: "Thank you, Edgar.", key: 'thank_you_edgar', next: "edgar_start" }
                ],
                onTrigger: () => {
                    // Only give vestigel if player doesn't already have it
                    if (!this.hasItem('vestigel')) {
                        // Create the vestigel item
                        const vestigelItem = {
                            id: 'vestigel',
                            name: 'Writer\'s Vestigel',
                            description: 'A small, intricately carved token that Edgar found hidden inside a plush toy. It seems to have some mysterious significance.',
                            icon: 'vestigel',
                            usable: false,
                            consumable: false,
                            value: 0
                        };
                        
                        // Add the vestigel to inventory
                        this.addItemToInventory(vestigelItem);
                        
                        // Update quest progress
                        this.questSystem.updateQuest('the_three_vestigels', 'Received a vestigel from Edgar Eskola after helping with his book.', 'edgar_vestigel_acquired');
                        
                        // Add journal entry about receiving the vestigel
                        this.addJournalEntry(
                            'edgar_vestigel_received_after_book',
                            'The Writer\'s Token',
                            'Today I acquired one of the three vestigels from Edgar Eskola at the Screaming Cork. He gave it to me as thanks for helping him write his book. The vestigel had been hidden inside a plush toy that Edgar had bought from a street vendor. He mentioned that the vendor refused to take it back when offered, citing "professional honor." The vestigel itself is small but intricately carved, clearly valuable to someone who knows its purpose.',
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                item: 'Vestigel',
                                quest: 'the_three_vestigels',
                                importance: 'high'
                            }
                        );
                    }
                }
            },
            edgar_vestigel_thanks: {
        
                text: "Remember your promise. I look forward to seeing what we can create together. A book that truly captures the essence of... well, that's what we need to discover.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(1, 0);

                    // Only update the quest state if we haven't already received the vestigel
                    if (!this.hasItem('vestigel')) {
                        this.questSystem.updateQuest('the_three_vestigels', 'Edgar Eskola would trade the Vestigel for your help with his book.', 'edgar_book_trade');
                        
                        // Add journal entry about Edgar's agreement
                        this.addJournalEntry(
                            'edgar_vestigel_agreement',
                            'The Vestigel Bargain',
                            'Edgar agreed to give me his vestigel once I help him write his book. He seems particularly excited about the prospect of becoming an author. The way his eyes lit up when discussing the project suggests this means more to him than just a simple trade - it represents a chance to leave his mark on the city that has so often marginalized him.',
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                item: 'Vestigel',
                                quests: ['the_three_vestigels', 'edgar_book'],
                                importance: 'high'
                            }
                        );
                    }
                }
            },

            // Before the finale: Edgar's secret way into the Egg Cathedral
            edgar_cathedral_way: {
                text: "The ursine creature goes very still — the way animals do when they hear something potentially dangerous. \"The Egg Cathedral… Yes. I've thought about that place more than most have.\" He lowers his voice. \"I swept its corridors. Oiled its lift-cages. Carried out its ash. Nobody watches the one who carries out the ash. And I learned a thing the priests never did: everyone was using the main entrance. The great doors. The Sentinel. I always looked for the hidden places. Some nights, the walls breathe.\"",
                options: [
                    { text: "The walls breathe?", key: 'the_walls_breathe', next: "edgar_cathedral_breathe" },
                    { text: "Then show me the way in.", key: 'then_show_me_the_way_in', next: "edgar_cathedral_path" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_cathedral_breathe: {
                text: "\"They're breathing. In and out, slowly, as if something were sleeping there. Everyone thinks the cathedral's cellars are just a dead, empty space where nothing exists. But I don't think they're dead. There's something down there. Honestly, I stopped working there because I got scared. I have no idea if those corridors have changed in any way since then — you'll have to see for yourself.\"",
                options: [
                    { text: "So there is a way in.", key: 'so_there_is_a_way_in', next: "edgar_cathedral_path" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_cathedral_path: {
                text: "\"There is. On the north side, where the cathedral wall meets the dead gods strata, there is a spot where the ground is constantly shifting, creating a narrow passage. A gap the width of a bear's shoulders, if you don't mind the smell of the underneath. You'd better go right away. Whatever's waking in there won't leave a gap open for long.\" He hesitates, one great paw flat on the table. \"Be careful. I've always thought of myself as someone who notices things that no one else notices. I wouldn't want to be the last person to see you alive.\"",
                options: [
                    { text: "Thank you, Edgar.", key: 'thank_you_edgar_cathedral', next: "edgar_start" },
                    { text: "I should go.", key: 'i_should_go', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('edgar_cathedral_path')) {
                        this.addJournalEntry(
                            'edgar_cathedral_path',
                            'Edgar\'s Secret Way',
                            'Edgar Eskola — who spent years as a janitor in the Egg Cathedral, sweeping its corridors and carrying out its ash — told me of a way inside that ignores the great doors and the Sentinel entirely. On the north side, where the cathedral wall meets the dead-god strata, the ground is constantly shifting and has opened a narrow passage — a gap the width of a bear\'s shoulders. He says the cellars everyone takes for dead space are not dead: something is down there, and some nights the walls breathe. He stopped working there because it frightened him, and he doesn\'t know how the corridors have changed since. "Everyone was using the main entrance," he said. "I always looked for the hidden places."',
                            this.journalSystem.categories.PLACES,
                            { character: 'Edgar Eskola', location: 'Egg Cathedral' }
                        );
                    }
                }
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkBg', 'assets/images/backgrounds/ScreamingCork.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('edgarEskola', 'assets/images/characters/EdgarEskola.png');
        this.load.image('vestigel', 'assets/images/items/vestigel.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();

        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkBg');
        this.fitBackground(bg);
        bg.setDepth(-1);

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // Position the priest at the right side when entering from ScraperScene
        this.priest.x = 700;
        this.priest.y = 470;

        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Create exit to ScraperScene at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'BurningBearStreetScene', // target scene
            50, // walk to x
            470 // walk to y
        );

        // Create entrance to the tavern interior (centered on the tavern door)
        this.transitionManager.createTransitionZone(
            400, // x position - centered on the door
            470, // y position
            100, // width
            200, // height
            'up', // direction
            'ScreamingCorkInteriorScene', // target scene
            100, // walk to x - position inside the tavern
            470 // walk to y
        );

        // Add a hint about the tavern entrance
        const doorHint = this.add.text(400, 380, this.t('ui.hints.enterTavern'), {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        doorHint.setOrigin(0.5);
        doorHint.setAlpha(0);
        doorHint.setDepth(10);

        // Show hint when hovering near the door
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the door area
            if (Math.abs(pointer.x - 400) < 50 && Math.abs(pointer.y - 470) < 100) {
                doorHint.setAlpha(1);
            } else {
                doorHint.setAlpha(0);
            }
        });

        // Add Edgar Eskola NPC
        this.createEdgarEskola();

        // Examine: the tavern & the beat under its floorboards (sign/building, upper-center).
        this.createObservable(400, 235, 260, 130, () => {
            if (this.hasJournalEntry('noise_god_insight') || this.hasJournalEntry('feral_toast_performance')) return this.t('observe.screaming_cork.knows_noise');
            return this.t('observe.screaming_cork.default');
        }, { hint: this.t('observe.screaming_cork.hint') });
    }

    update() {
        super.update();
    }

    createEdgarEskola() {
        // Create Edgar Eskola NPC
        this.edgar = this.add.image(200, 510, 'edgarEskola'); // Further increased Y to lower position more
        this.edgar.setScale(0.125); // Set appropriate scale
        this.edgar.setOrigin(0.5, 1.0); // Set origin to bottom center to align with ground
        this.edgar.setDepth(5);
        this.addGroundShadow(200, 510, this.edgar.displayWidth * 0.55, this.edgar.displayHeight * 0.10);
        this.edgar.setInteractive({ useHandCursor: true });

        // Add dialog interaction
        this.edgar.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('edgar_start');
        });

        // Add subtle wobble effect
        this.addWobbleEffect(this.edgar, 200, 510); // Update wobble position to match new Y
    }

    addWobbleEffect(sprite, baseX, baseY) {
        // Create a very subtle wobble effect
        this.tweens.add({
            targets: sprite,
            y: { from: baseY - 1, to: baseY + 1 },
            ease: 'Sine.easeInOut',
            duration: 1500,
            yoyo: true,
            repeat: -1
        });

        // Add a very slight rotation wobble
        this.tweens.add({
            targets: sprite,
            angle: { from: -1, to: 1 },
            ease: 'Sine.easeInOut',
            duration: 2000,
            yoyo: true,
            repeat: -1,
            delay: 5000 // Offset from the y-wobble for more natural movement
        });
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScreamingCorkScene = ScreamingCorkScene;
}
