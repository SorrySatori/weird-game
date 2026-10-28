/**
 * Edgar's book (quest `edgar_book`, ScreamingCorkScene).
 *
 * The player's picks — up to three inspiration topics, a tone, a genre, a protagonist and a setting —
 * become a whole little book: a title with an "aneb …" / "or, …" subtitle, a back-cover blurb, three
 * excerpts and a few reviews from people the player has met. Every pick is a POOL: the cast is drawn
 * from it with a seed fixed when the quest starts, so the same picks give different books in different
 * playthroughs, but one book never changes (journal, cutscene and re-reading all agree).
 *
 * The picks bend each other: the genre swaps the hero and villain pools (funny animals → everyone is an
 * animal, so a political tale gets the Fascist Stag), some genre × tone pairs have their own title, the
 * genre picks the MacGuffin, and the topics bring in cameo characters (the third one gets thanked).
 *
 * Czech is written natively and declined: every character carries its cases and a gender class.
 * Template tokens (both languages):
 *   {P}            the role in nominative (en: its name)
 *   {P.g} …        a case — n g d a i l (cs; en falls back to the name) — or any other field:
 *                  {P.desc}, {S.in}, {S.to}, {S.from}
 *   {P:a|b|c|d}    agreement by gender class m | f | n | pl;   {P:sg|pl}  number only
 *   {^…}           capitalise the result
 * Roles: P protagonist, A antagonist, S setting, M MacGuffin, K / J / L cameos from the topics.
 */

// ---------------------------------------------------------------------------------------------
// Engine
// ---------------------------------------------------------------------------------------------

const GENDER = { m: 0, f: 1, n: 2, pl: 3 };

function hash(str) {
    let h = 2166136261 >>> 0;
    for (let i = 0; i < str.length; i++) {
        h ^= str.charCodeAt(i);
        h = Math.imul(h, 16777619) >>> 0;
    }
    return h;
}

/** Stable pick per named slot, so adding a slot never reshuffles the others. */
const pickIndex = (seed, slot, n) => (n ? hash(`${seed}|${slot}`) % n : 0);
const pick = (seed, slot, arr) => arr[pickIndex(seed, slot, arr.length)];

export function newBookSeed() {
    return Math.floor(Math.random() * 2147483647);
}

const NAME_FIELDS = new Set(['n', 'g', 'd', 'a', 'i', 'l', 'in', 'to', 'from']);

/**
 * Fill a template. `seen` collects the roles already named in this text: from the second mention on,
 * a role with a `short` form uses it ("Čarodějnická akademie, kde se vašim dětem… " → "akademie").
 */
export function render(tpl, roles, lang, seen = new Set()) {
    return tpl.replace(/\{(\^?)([A-Z])(?:\.([a-z]+))?(?::([^}]*))?\}/g, (whole, cap, role, field, alts, at, str) => {
        let r = roles[role]?.[lang];
        if (!r) return whole;
        let out;
        if (alts !== undefined) {
            const forms = alts.split('|');
            out = forms.length === 2 ? forms[r.x === 'pl' ? 1 : 0] : forms[GENDER[r.x] ?? 0];
        } else {
            const naming = NAME_FIELDS.has(field ?? 'n');
            if (naming && r.short && seen.has(role)) r = { ...r, ...r.short };
            if (naming) seen.add(role);
            out = field ? (r[field] ?? r.n) : r.n;
            // Czech closes an embedded relative clause with a comma when the sentence goes on
            // ("fronta, která sní o svém konci, a vrátil se…").
            if (r.rel && field !== 'desc' && str[at + whole.length] === ' ') out += ',';
        }
        return cap ? out.charAt(0).toUpperCase() + out.slice(1) : out;
    });
}

const SMALL_WORDS = new Set(['a', 'an', 'the', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 'but', 'nor', 'as']);

/** English headline case ("Dr. Hyfa Morel and the Mother-in-Law"); first word always capitalised. */
function titleCase(text) {
    let first = true;
    return text.replace(/[A-Za-zÀ-ž']+/g, (word, at) => {
        const prev = text[at - 1];
        const lower = word.toLowerCase();
        const keepSmall = !first && SMALL_WORDS.has(lower) && prev !== ':' && !/[:;]\s$/.test(text.slice(at - 2, at));
        first = false;
        return keepSmall ? word : word.charAt(0).toUpperCase() + word.slice(1);
    });
}

/**
 * A character/thing. `cs` = 'nom|gen|dat|acc|ins|loc'; `tail` is appended to every case (relative
 * clauses, prepositional phrases); x = gender class (en: pronoun he/she/it/they).
 */
function who(en, enX, cs, csX, tail = '', desc = null) {
    const [n, g, d, a, i, l] = cs.split('|').map(f => f + tail);
    return {
        kind: 'who',
        en: { n: en, x: enX, rel: en.includes(', '), ...(desc ? { desc: desc[0] } : {}) },
        cs: { n, g, d, a, i, l, x: csX, rel: tail.startsWith(','), ...(desc ? { desc: desc[1] } : {}),
              ...(tail ? { short: caseForms('who', cs) } : {}) },
    };
}

const CASES = { who: ['n', 'g', 'd', 'a', 'i', 'l'], place: ['n', 'g', 'd', 'a', 'l', 'in', 'to', 'from'] };
function caseForms(kind, forms) {
    const parts = forms.split('|');
    return { ...Object.fromEntries(CASES[kind].map((k, i) => [k, parts[i]])), rel: false };
}

/** A place. `cs` = 'nom|gen|dat|acc|loc|in|to|from'; en prepositions default to in/to/from + name. */
function place(en, cs, csX, tail = '') {
    const [n, g, d, a, l, inn, to, from] = cs.split('|').map(f => f + tail);
    return {
        kind: 'place',
        en: { n: en.n, x: 'n', rel: en.n.includes(', '), in: en.in ?? `in ${en.n}`, to: en.to ?? `to ${en.n}`, from: en.from ?? `from ${en.n}` },
        cs: { n, g, d, a, l, in: inn, to, from, x: csX, rel: tail.startsWith(','),
              ...(tail ? { short: caseForms('place', cs) } : {}) },
    };
}

// ---------------------------------------------------------------------------------------------
// Cast
// ---------------------------------------------------------------------------------------------

const HEROES = {
    'disoriented tourist': [
        who('Ferdinand Kroupa', 'm', 'Ferdinand Kroupa|Ferdinanda Kroupy|Ferdinandu Kroupovi|Ferdinanda Kroupu|Ferdinandem Kroupou|Ferdinandu Kroupovi', 'm', '',
            ['a tourist with a map of an entirely different city', 'turista s mapou úplně jiného města']),
        who('Mrs. Vlasta', 'f', 'paní Vlasta|paní Vlasty|paní Vlastě|paní Vlastu|paní Vlastou|paní Vlastě', 'f', '',
            ['a pensioner who came for the spa cure eleven years ago and is still looking for the spa', 'důchodkyně, která sem před jedenácti lety přijela do lázní a pořád je hledá']),
    ],
    'bad scientist': [
        who('Dr. Hyfa Morel', 'f', 'doktorka Hyfa Smržová|doktorky Hyfy Smržové|doktorce Hyfě Smržové|doktorku Hyfu Smržovou|doktorkou Hyfou Smržovou|doktorce Hyfě Smržové', 'f', '',
            ['a renegade mycologist banned from three universities and one pub', 'houbová vědkyně renegátka, vyhozená ze tří univerzit a jedné hospody']),
        who('Professor Yeastley', 'm', 'profesor Kvasnička|profesora Kvasničky|profesoru Kvasničkovi|profesora Kvasničku|profesorem Kvasničkou|profesoru Kvasničkovi', 'm', '',
            ['who once cloned himself out of spite — the two of them still aren\'t speaking', 'který se jednou ze vzdoru naklonoval – a dodnes spolu nemluví']),
    ],
    'mišutkenn': [
        who('Grumbald', 'm', 'Bručoun|Bručouna|Bručounovi|Bručouna|Bručounem|Bručounovi', 'm', '',
            ['a mišutkenn who isn\'t sure if he\'s a bear, a person or an unpaid invoice', 'mišutkenn, který neví, jestli je medvěd, člověk, nebo nezaplacená faktura']),
        who('Honeypaw', 'f', 'Medulka|Medulky|Medulce|Medulku|Medulkou|Medulce', 'f', '',
            ['a mišutkenn poet who signs her verses with a claw', 'mišutkenní básnířka, která své verše podepisuje drápem']),
    ],
    'strange amnesiac': [
        who('Nobody In Particular', 'm', 'Nikdo Konkrétní|Nikoho Konkrétního|Nikomu Konkrétnímu|Nikoho Konkrétního|Nikým Konkrétním|Nikom Konkrétním', 'm', '',
            ['who woke up in a fountain with three superpowers and no idea which of them are legal', 'který se probudil v kašně se třemi nadpřirozenými schopnostmi a netuší, které z nich jsou legální']),
        who('Agatha Twice', 'f', 'Agáta Dvakrát|Agáty Dvakrát|Agátě Dvakrát|Agátu Dvakrát|Agátou Dvakrát|Agátě Dvakrát', 'f', '',
            ['who forgets everything except other people\'s debts', 'která zapomíná všechno kromě cizích dluhů']),
    ],
    'fungal colony': [
        who('the Toadstool Gang', 'pl', 'Parta muchomůrek|Party muchomůrek|Partě muchomůrek|Partu muchomůrek|Partou muchomůrek|Partě muchomůrek', 'f', '',
            ['a colony of mushrooms with one shared brain and four opinions', 'kolonie hub s jedním společným mozkem a čtyřmi názory']),
        who('the Mushroom Mates', 'pl', 'Houboví kámoši|Houbových kámošů|Houbovým kámošům|Houbové kámoše|Houbovými kámoši|Houbových kámoších', 'pl', '',
            ['technically a single organism, though they split every bill twelve ways', 'technicky jeden organismus, ale každý účet si dělí na dvanáct']),
    ],
    'dream detective': [
        who('Inspector Nod', 'm', 'inspektor Dřímal|inspektora Dřímala|inspektoru Dřímalovi|inspektora Dřímala|inspektorem Dřímalem|inspektoru Dřímalovi', 'm', '',
            ['a dream detective who only solves crimes while asleep, and bills by the hour', 'snový detektiv, který řeší zločiny jen ve spánku, a proto si účtuje každou hodinu']),
        who('Detective Lucida Nightcap', 'f', 'detektivka Lucie Noční|detektivky Lucie Noční|detektivce Lucii Noční|detektivku Lucii Noční|detektivkou Lucií Noční|detektivce Lucii Noční', 'f', '',
            ['who questions suspects inside their own nightmares and has a confession by breakfast', 'která vyslýchá podezřelé v jejich vlastních nočních můrách a přiznání má vždycky do snídaně']),
    ],
    'rogue Ludarch': [
        who('Grandmaster Lawrence', 'm', 'velmistr Vavřinec|velmistra Vavřince|velmistru Vavřincovi|velmistra Vavřince|velmistrem Vavřincem|velmistru Vavřincovi', 'm', '',
            ['the last Ludarch, who lost the war but kept the dice', 'poslední Ludarch, který prohrál válku, ale kostky si nechal']),
        who('Lady Gambit', 'f', 'dáma Gambitová|dámy Gambitové|dámě Gambitové|dámu Gambitovou|dámou Gambitovou|dámě Gambitové', 'f', '',
            ['a rogue Ludarch who cheats at solitaire, on principle', 'odpadlá Ludarchyně, která z principu podvádí i v pasiánsu']),
    ],
    'living collective': [
        who('Mr. Entirely Singular', 'm', 'pan Naprosto Jednotlivý|pana Naprosto Jednotlivého|panu Naprosto Jednotlivému|pana Naprosto Jednotlivého|panem Naprosto Jednotlivým|panu Naprosto Jednotlivém', 'm', '',
            ['forty-one small creatures in one coat who would like to open a bank account', 'jedenačtyřicet drobných tvorů v jednom kabátě, kteří by si rádi založili účet v bance']),
        who('the Committee Called Kevin', 'n', 'Výbor jménem Kevin|Výboru jménem Kevin|Výboru jménem Kevin|Výbor jménem Kevin|Výborem jménem Kevin|Výboru jménem Kevin', 'm', '',
            ['which agreed to be one person after a six-hour vote', 'který se po šestihodinovém hlasování dohodl, že bude jeden člověk']),
    ],
};

// "Funny animals with depression": the genre turns every hero into an animal.
const ANIMAL_HEROES = {
    'disoriented tourist': who('Ferdinand the Gander', 'm', 'houser Ferdinand|housera Ferdinanda|houseru Ferdinandovi|housera Ferdinanda|houserem Ferdinandem|houseru Ferdinandovi', 'm', '',
        ['a gander who got lost on an all-inclusive package holiday', 'houser, který se ztratil na zájezdu all inclusive']),
    'bad scientist': who('Dr. Badger', 'm', 'doktor Jezevec|doktora Jezevce|doktoru Jezevcovi|doktora Jezevce|doktorem Jezevcem|doktoru Jezevcovi', 'm', '',
        ['a badger in a lab coat, still trying to sequence his own sadness', 'jezevec v laboratorním plášti, který se pořád snaží osekvenovat vlastní smutek']),
    'mišutkenn': who('Grumbald the Bear', 'm', 'medvěd Bručoun|medvěda Bručouna|medvědu Bručounovi|medvěda Bručouna|medvědem Bručounem|medvědu Bručounovi', 'm', '',
        ['a bear who strongly suspects he is a mišutkenn', 'medvěd, který má silné podezření, že je mišutkenn']),
    'strange amnesiac': who('Forget-Me-Not the Squirrel', 'f', 'veverka Pomněnka|veverky Pomněnky|veverce Pomněnce|veverku Pomněnku|veverkou Pomněnkou|veverce Pomněnce', 'f', '',
        ['a squirrel who forgot where she buried her nuts and, worse, why', 'veverka, která zapomněla, kam zahrabala oříšky, a hlavně proč']),
    'fungal colony': who('the Truffle Family', 'pl', 'rodina Lanýžových|rodiny Lanýžových|rodině Lanýžových|rodinu Lanýžových|rodinou Lanýžových|rodině Lanýžových', 'f', '',
        ['truffles nobody goes looking for anymore', 'lanýže, které už nikdo nehledá']),
    'dream detective': who('Inspector Raccoon', 'm', 'inspektor Mýval|inspektora Mývala|inspektoru Mývalovi|inspektora Mývala|inspektorem Mývalem|inspektoru Mývalovi', 'm', '',
        ['a raccoon who only investigates crimes involving food', 'mýval, který vyšetřuje jen zločiny, u kterých se dá něco sníst']),
    'rogue Ludarch': who('Grandmaster Mole', 'm', 'velmistr Krtek|velmistra Krtka|velmistru Krtkovi|velmistra Krtka|velmistrem Krtkem|velmistru Krtkovi', 'm', '',
        ['a mole who played chess against the whole garden and lost', 'krtek, který hrál šachy s celou zahradou a prohrál']),
    'living collective': who('Seventeen Sparrows in a Coat', 'pl', 'sedmnáct vrabců v kabátě|sedmnácti vrabců v kabátě|sedmnácti vrabcům v kabátě|sedmnáct vrabců v kabátě|sedmnácti vrabci v kabátě|sedmnácti vrabcích v kabátě', 'n', '',
        ['who pass for a single civil servant', 'kteří se vydávají za jednoho úředníka']),
};

const VILLAINS = {
    tragic: [
        who('the director of a household-goods company', 'm', 'ředitel|ředitele|řediteli|ředitele|ředitelem|řediteli', 'm', ' firmy s potřebami do domácnosti'),
        who('the Landlord', 'm', 'pan domácí|pana domácího|panu domácímu|pana domácího|panem domácím|panu domácím', 'm'),
    ],
    metaphysical: [
        who('a thought nobody has had yet', 'n', 'myšlenka|myšlenky|myšlence|myšlenku|myšlenkou|myšlence', 'f', ', kterou ještě nikdo neměl'),
        who('the Author', 'm', 'Autor|Autora|Autorovi|Autora|Autorem|Autorovi', 'm'),
    ],
    romantic: [
        who('the ex-fiancé', 'm', 'bývalý snoubenec|bývalého snoubence|bývalému snoubenci|bývalého snoubence|bývalým snoubencem|bývalém snoubenci', 'm'),
        who('a middle manager', 'm', 'middle manager|middle managera|middle managerovi|middle managera|middle managerem|middle managerovi', 'm'),
        who('the wedding planner', 'm', 'svatební plánovač|svatebního plánovače|svatebnímu plánovači|svatebního plánovače|svatebním plánovačem|svatebním plánovači', 'm'),
    ],
    existential: [
        who('Monday', 'n', 'Pondělí|Pondělí|Pondělí|Pondělí|Pondělím|Pondělí', 'n'),
        who('the Void', 'n', 'Prázdnota|Prázdnoty|Prázdnotě|Prázdnotu|Prázdnotou|Prázdnotě', 'f'),
    ],
    political: [
        who('the Ministry of Permitted Joy', 'n', 'Ministerstvo povolené radosti|Ministerstva povolené radosti|Ministerstvu povolené radosti|Ministerstvo povolené radosti|Ministerstvem povolené radosti|Ministerstvu povolené radosti', 'n'),
        who('Chairman Compost', 'm', 'předseda Kompost|předsedy Komposta|předsedovi Kompostovi|předsedu Komposta|předsedou Kompostem|předsedovi Kompostovi', 'm'),
    ],
    comical: [
        who('a cursed accordion', 'n', 'prokletá harmonika|prokleté harmoniky|prokleté harmonice|prokletou harmoniku|prokletou harmonikou|prokleté harmonice', 'f'),
        who('Uncle Bořivoj', 'm', 'strejda Bořivoj|strejdy Bořivoje|strejdovi Bořivojovi|strejdu Bořivoje|strejdou Bořivojem|strejdovi Bořivojovi', 'm'),
    ],
};

const ANIMAL_VILLAINS = {
    tragic: who('the Winter', 'n', 'Zima|Zimy|Zimě|Zimu|Zimou|Zimě', 'f'),
    metaphysical: who('a philosophical snail', 'm', 'filozofický šnek|filozofického šneka|filozofickému šnekovi|filozofického šneka|filozofickým šnekem|filozofickém šnekovi', 'm'),
    romantic: who('a very handsome otter', 'm', 'velmi pohledná vydra|velmi pohledné vydry|velmi pohledné vydře|velmi pohlednou vydru|velmi pohlednou vydrou|velmi pohledné vydře', 'f'),
    existential: who('an empty bird feeder', 'n', 'prázdné krmítko|prázdného krmítka|prázdnému krmítku|prázdné krmítko|prázdným krmítkem|prázdném krmítku', 'n'),
    political: who('the Fascist Stag', 'm', 'fašistický jelen|fašistického jelena|fašistickému jelenovi|fašistického jelena|fašistickým jelenem|fašistickém jelenovi', 'm'),
    comical: who('a goose with a grudge', 'f', 'husa|husy|huse|husu|husou|huse', 'f', ' s nevyřízenými účty'),
};

const SETTINGS = {
    'scraper': [
        place({ n: 'the Scraper' }, 'Škrabák|Škrabáku|Škrabáku|Škrabák|Škrabáku|ve Škrabáku|do Škrabáku|ze Škrabáku', 'm'),
        place({ n: 'floor minus thirteen', in: 'on floor minus thirteen' }, 'mínus třinácté patro|mínus třináctého patra|mínus třináctému patru|mínus třinácté patro|mínus třináctém patře|v mínus třináctém patře|do mínus třináctého patra|z mínus třináctého patra', 'n'),
    ],
    'magical school': [
        place({ n: 'the Witchcraft Academy, where your children will definitely come to no harm', in: 'at the Witchcraft Academy, where your children will definitely come to no harm' }, 'Čarodějnická akademie|Čarodějnické akademie|Čarodějnické akademii|Čarodějnickou akademii|Čarodějnické akademii|na Čarodějnické akademii|na Čarodějnickou akademii|z Čarodějnické akademie', 'f', ', kde se vašim dětem rozhodně nic nestane'),
        place({ n: 'the Primary School of Necromancy and Home Economics', in: 'at the Primary School of Necromancy and Home Economics' }, 'Základní škola nekromancie a rodinné výchovy|Základní školy nekromancie a rodinné výchovy|Základní škole nekromancie a rodinné výchovy|Základní školu nekromancie a rodinné výchovy|Základní škole nekromancie a rodinné výchovy|na Základní škole nekromancie a rodinné výchovy|na Základní školu nekromancie a rodinné výchovy|ze Základní školy nekromancie a rodinné výchovy', 'f'),
    ],
    'immortal mammal': [
        place({ n: 'the belly of the Eternal Whale' }, 'břicho Věčné velryby|břicha Věčné velryby|břichu Věčné velryby|břicho Věčné velryby|břiše Věčné velryby|v břiše Věčné velryby|do břicha Věčné velryby|z břicha Věčné velryby', 'n'),
        place({ n: 'the left kidney of an immortal manatee' }, 'levá ledvina nesmrtelného kapustňáka|levé ledviny nesmrtelného kapustňáka|levé ledvině nesmrtelného kapustňáka|levou ledvinu nesmrtelného kapustňáka|levé ledvině nesmrtelného kapustňáka|v levé ledvině nesmrtelného kapustňáka|do levé ledviny nesmrtelného kapustňáka|z levé ledviny nesmrtelného kapustňáka', 'f'),
    ],
    'fungal wilds': [
        place({ n: 'the Mycelial Wilds' }, 'Myceliová divočina|Myceliové divočiny|Myceliové divočině|Myceliovou divočinu|Myceliové divočině|v Myceliové divočině|do Myceliové divočiny|z Myceliové divočiny', 'f'),
        place({ n: 'a forest where the mushrooms go picking people' }, 'les|lesa|lesu|les|lese|v lese|do lesa|z lesa', 'm', ', kde houby sbírají houbaře'),
    ],
    'skyship': [
        place({ n: 'the skyship Verdigrace', in: 'aboard the skyship Verdigrace', to: 'aboard the skyship Verdigrace', from: 'off the skyship Verdigrace' }, 'vzducholoď Verdigrace|vzducholodi Verdigrace|vzducholodi Verdigrace|vzducholoď Verdigrace|vzducholodi Verdigrace|na palubě vzducholodi Verdigrace|na palubu vzducholodi Verdigrace|z paluby vzducholodi Verdigrace', 'f'),
        place({ n: 'a budget airship with no toilets', in: 'aboard a budget airship with no toilets', to: 'aboard a budget airship with no toilets', from: 'off a budget airship with no toilets' }, 'nízkonákladová vzducholoď bez záchodů|nízkonákladové vzducholodi bez záchodů|nízkonákladové vzducholodi bez záchodů|nízkonákladovou vzducholoď bez záchodů|nízkonákladové vzducholodi bez záchodů|na nízkonákladové vzducholodi bez záchodů|na nízkonákladovou vzducholoď bez záchodů|z nízkonákladové vzducholodi bez záchodů', 'f'),
    ],
    'markets': [
        place({ n: 'the Voxmarket', in: 'at the Voxmarket' }, 'Voxmarket|Voxmarketu|Voxmarketu|Voxmarket|Voxmarketu|na Voxmarketu|na Voxmarket|z Voxmarketu', 'm'),
        place({ n: 'an underground market where you pay in secrets', in: 'at an underground market where you pay in secrets' }, 'podzemní tržiště|podzemního tržiště|podzemnímu tržišti|podzemní tržiště|podzemním tržišti|na podzemním tržišti|na podzemní tržiště|z podzemního tržiště', 'n', ', kde se platí tajemstvími'),
    ],
    'living board game': [
        // a board game's brand name: undeclined in Czech, neuter agreement ("Mushrooms&Polygons si ničeho nevšimlo")
        place({ n: 'Mushrooms&Polygons' }, 'Mushrooms&Polygons|Mushrooms&Polygons|Mushrooms&Polygons|Mushrooms&Polygons|Mushrooms&Polygons|v Mushrooms&Polygons|do Mushrooms&Polygons|z Mushrooms&Polygons', 'n'),
        place({ n: 'a board game that declared war' }, 'deskovka|deskovky|deskovce|deskovku|deskovce|v deskovce|do deskovky|z deskovky', 'f', ', která vyhlásila válku'),
    ],
    'god graveyard': [
        place({ n: 'the Godgraveyard' }, 'Bohohřbitov|Bohohřbitova|Bohohřbitovu|Bohohřbitov|Bohohřbitově|na Bohohřbitově|na Bohohřbitov|z Bohohřbitova', 'm'),
        place({ n: 'a retirement home for forgotten gods' }, 'domov důchodců pro zapomenuté bohy|domova důchodců pro zapomenuté bohy|domovu důchodců pro zapomenuté bohy|domov důchodců pro zapomenuté bohy|domově důchodců pro zapomenuté bohy|v domově důchodců pro zapomenuté bohy|do domova důchodců pro zapomenuté bohy|z domova důchodců pro zapomenuté bohy', 'm'),
    ],
};

const MACGUFFINS = {
    'fungal techno': [
        who('a USB stick full of spores', 'n', 'flashka plná spor|flashky plné spor|flashce plné spor|flashku plnou spor|flashkou plnou spor|flashce plné spor', 'f'),
        who('the last unencrypted mushroom', 'n', 'poslední nešifrovaná houba|poslední nešifrované houby|poslední nešifrované houbě|poslední nešifrovanou houbu|poslední nešifrovanou houbou|poslední nešifrované houbě', 'f'),
    ],
    'postmodern': [
        who('this very book', 'n', 'tahle kniha|téhle knihy|téhle knize|tuhle knihu|touhle knihou|téhle knize', 'f'),
        who('a footnote on the run', 'n', 'uprchlá poznámka pod čarou|uprchlé poznámky pod čarou|uprchlé poznámce pod čarou|uprchlou poznámku pod čarou|uprchlou poznámkou pod čarou|uprchlé poznámce pod čarou', 'f'),
    ],
    'urban fantasy': [
        who('a key to every door in the city but one', 'n', 'klíč od všech dveří ve městě kromě jedněch|klíče od všech dveří ve městě kromě jedněch|klíči od všech dveří ve městě kromě jedněch|klíč od všech dveří ve městě kromě jedněch|klíčem od všech dveří ve městě kromě jedněch|klíči od všech dveří ve městě kromě jedněch', 'm'),
        who('a tram ticket valid for one miracle', 'n', 'jízdenka na tramvaj platná na jeden zázrak|jízdenky na tramvaj platné na jeden zázrak|jízdence na tramvaj platné na jeden zázrak|jízdenku na tramvaj platnou na jeden zázrak|jízdenkou na tramvaj platnou na jeden zázrak|jízdence na tramvaj platné na jeden zázrak', 'f'),
    ],
    'funny animals': [
        who('the last acorn', 'n', 'poslední žalud|posledního žaludu|poslednímu žaludu|poslední žalud|posledním žaludem|posledním žaludu', 'm'),
        who('a prescription for antidepressants', 'n', 'recept na antidepresiva|receptu na antidepresiva|receptu na antidepresiva|recept na antidepresiva|receptem na antidepresiva|receptu na antidepresiva', 'm'),
    ],
    'detective': [
        who('a strongly worded letter', 'n', 'důrazně formulovaný dopis|důrazně formulovaného dopisu|důrazně formulovanému dopisu|důrazně formulovaný dopis|důrazně formulovaným dopisem|důrazně formulovaném dopisu', 'm'),
        who('a corpse that keeps changing its alibi', 'n', 'mrtvola|mrtvoly|mrtvole|mrtvolu|mrtvolou|mrtvole', 'f', ', která pořád mění alibi'),
    ],
    'weird fiction': [
        who('a door that only opens inwards, into you', 'n', 'branka|branky|brance|branku|brankou|brance', 'f', ', která se otevírá jen dovnitř, do vás'),
        who('a dream somebody left on a tram', 'n', 'sen|snu|snu|sen|snem|snu', 'm', ', který někdo zapomněl v tramvaji'),
    ],
    'mythic war epic': [
        who('the Card of Overpriced Acquisition', 'n', 'Kartička předraženého pořízení|Kartičky předraženého pořízení|Kartičce předraženého pořízení|Kartičku předraženého pořízení|Kartičkou předraženého pořízení|Kartičce předraženého pořízení', 'f'),
        who('a rulebook nobody ever read', 'n', 'příručka pravidel|příručky pravidel|příručce pravidel|příručku pravidel|příručkou pravidel|příručce pravidel', 'f', ', kterou nikdo nikdy nečetl'),
    ],
    'cosmic horror': [
        who('a hymn with one note too many', 'n', 'hymna s jednou notou navíc|hymny s jednou notou navíc|hymně s jednou notou navíc|hymnu s jednou notou navíc|hymnou s jednou notou navíc|hymně s jednou notou navíc', 'f'),
        who('a dead god\'s phone number', 'n', 'telefonní číslo mrtvého boha|telefonního čísla mrtvého boha|telefonnímu číslu mrtvého boha|telefonní číslo mrtvého boha|telefonním číslem mrtvého boha|telefonním čísle mrtvého boha', 'n'),
    ],
};

// The player's own experiences walk into the book as side characters (topic id → cameo).
const CAMEOS = {
    scraper_building: who('a building that rearranges itself out of boredom', 'n', 'budova|budovy|budově|budovu|budovou|budově', 'f', ', která se z nudy přestavuje'),
    lift_mother: who('a lift who insists on being called Mother', 'f', 'výtah|výtahu|výtahu|výtah|výtahem|výtahu', 'm', ', který trvá na oslovení „Matko“'),
    ortolan: who('a four-armed toymaker', 'm', 'čtyřruký výrobce hraček|čtyřrukého výrobce hraček|čtyřrukému výrobci hraček|čtyřrukého výrobce hraček|čtyřrukým výrobcem hraček|čtyřrukém výrobci hraček', 'm'),
    dream_queue: who('a queue that has been dreaming of its own end since spring', 'n', 'fronta|fronty|frontě|frontu|frontou|frontě', 'f', ', která už od jara sní o svém konci'),
    spore_infection: who('a cough with opinions', 'n', 'kašel|kašle|kašli|kašel|kašlem|kašli', 'm', ' s vlastním názorem'),
    vestigels: who('a coin that refuses to be spent', 'n', 'mince|mince|minci|minci|mincí|minci', 'f', ', která se odmítá nechat utratit'),
    kloor_venn: who('a pharmacist who mostly sells side effects', 'm', 'lékárník|lékárníka|lékárníkovi|lékárníka|lékárníkem|lékárníkovi', 'm', ', který prodává hlavně vedlejší účinky'),
    skyships: who('a skyship captain who has never once landed', 'f', 'kapitánka vzducholodi|kapitánky vzducholodi|kapitánce vzducholodi|kapitánku vzducholodi|kapitánkou vzducholodi|kapitánce vzducholodi', 'f', ', která ještě nikdy nepřistála'),
    rust_choir: who('a choir of rusty monks who only sing the dial tone', 'n', 'sbor rezavých mnichů|sboru rezavých mnichů|sboru rezavých mnichů|sbor rezavých mnichů|sborem rezavých mnichů|sboru rezavých mnichů', 'm', ', kteří zpívají jen oznamovací tón'),
    burning_bear: who('a bear costume that has had enough', 'n', 'medvědí kostým|medvědího kostýmu|medvědímu kostýmu|medvědí kostým|medvědím kostýmem|medvědím kostýmu', 'm', ', který už toho má dost'),
    board_games_war: who('a pawn still traumatised by the Board Game Wars', 'm', 'pěšák|pěšáka|pěšákovi|pěšáka|pěšákem|pěšákovi', 'm', ' s traumatem z Deskovkových válek'),
    noise_god: who('a dead god who now lives in a broken amplifier', 'm', 'mrtvý bůh|mrtvého boha|mrtvému bohu|mrtvého boha|mrtvým bohem|mrtvém bohu', 'm', ', který teď bydlí v rozbitém zesilovači'),
    magnekin: who('a man made of tiny cities whose suburbs keep running away', 'm', 'muž z malinkých měst|muže z malinkých měst|muži z malinkých měst|muže z malinkých měst|mužem z malinkých měst|muži z malinkých měst', 'm', ', kterému pořád utíkají předměstí'),
    god_graveyard: who('a divinographer who reads gods by their bones', 'm', 'divinograf|divinografa|divinografovi|divinografa|divinografem|divinografovi', 'm', ', který čte bohy z kostí'),
    city_mystery: who('a street that moves house when nobody is looking', 'n', 'ulice|ulice|ulici|ulici|ulicí|ulici', 'f', ', která se stěhuje, když se nikdo nedívá'),
    misutken_life: who('a mišutkenn landlord with a strict no-bears policy', 'm', 'mišutkenní domácí|mišutkenního domácího|mišutkennímu domácímu|mišutkenního domácího|mišutkenním domácím|mišutkenním domácím', 'm', ', který zakázal medvědy'),
};

const FALLBACK_CAMEOS = [
    who('a talking umbrella', 'n', 'mluvící deštník|mluvícího deštníku|mluvícímu deštníku|mluvící deštník|mluvícím deštníkem|mluvícím deštníku', 'm'),
    who('a philosopher stuck in a revolving door', 'm', 'filozof uvězněný v otáčecích dveřích|filozofa uvězněného v otáčecích dveřích|filozofovi uvězněnému v otáčecích dveřích|filozofa uvězněného v otáčecích dveřích|filozofem uvězněným v otáčecích dveřích|filozofovi uvězněném v otáčecích dveřích', 'm'),
];

// Second-mention forms. EN: a name or { n, in, to, from }; CS: the case list (null = drop the tail).
const SHORT = {
    // heroes
    'Ferdinand Kroupa': ['Ferdinand', 'Ferdinand|Ferdinanda|Ferdinandovi|Ferdinanda|Ferdinandem|Ferdinandovi'],
    'Ferdinand the Gander': ['Ferdinand', 'Ferdinand|Ferdinanda|Ferdinandovi|Ferdinanda|Ferdinandem|Ferdinandovi'],
    'Dr. Hyfa Morel': ['Dr. Morel', 'doktorka Smržová|doktorky Smržové|doktorce Smržové|doktorku Smržovou|doktorkou Smržovou|doktorce Smržové'],
    'Detective Lucida Nightcap': ['Detective Nightcap', 'detektivka Noční|detektivky Noční|detektivce Noční|detektivku Noční|detektivkou Noční|detektivce Noční'],
    'the Committee Called Kevin': ['Kevin', 'Kevin|Kevina|Kevinovi|Kevina|Kevinem|Kevinovi'],
    'Forget-Me-Not the Squirrel': ['Forget-Me-Not', 'Pomněnka|Pomněnky|Pomněnce|Pomněnku|Pomněnkou|Pomněnce'],
    // villains
    'the director of a household-goods company': ['the director', null],
    'a thought nobody has had yet': ['the thought', null],
    'a middle manager': ['the middle manager', null],
    'the Ministry of Permitted Joy': ['the Ministry', 'Ministerstvo|Ministerstva|Ministerstvu|Ministerstvo|Ministerstvem|Ministerstvu'],
    'a cursed accordion': ['the accordion', 'harmonika|harmoniky|harmonice|harmoniku|harmonikou|harmonice'],
    'a philosophical snail': ['the snail', 'šnek|šneka|šnekovi|šneka|šnekem|šnekovi'],
    'a very handsome otter': ['the otter', 'vydra|vydry|vydře|vydru|vydrou|vydře'],
    'an empty bird feeder': ['the bird feeder', 'krmítko|krmítka|krmítku|krmítko|krmítkem|krmítku'],
    'a goose with a grudge': ['the goose', null],
    // places
    'the Witchcraft Academy, where your children will definitely come to no harm': [{ n: 'the Academy', in: 'at the Academy', to: 'to the Academy', from: 'from the Academy' }, 'akademie|akademie|akademii|akademii|akademii|na akademii|na akademii|z akademie'],
    'the Primary School of Necromancy and Home Economics': [{ n: 'the school', in: 'at the school', to: 'to the school', from: 'from the school' }, 'škola|školy|škole|školu|škole|ve škole|do školy|ze školy'],
    'the belly of the Eternal Whale': [{ n: 'the Whale\'s belly', in: 'in the Whale\'s belly', to: 'into the Whale\'s belly', from: 'out of the Whale\'s belly' }, 'břicho Velryby|břicha Velryby|břichu Velryby|břicho Velryby|břiše Velryby|v břiše Velryby|do břicha Velryby|z břicha Velryby'],
    'the left kidney of an immortal manatee': [{ n: 'the kidney', in: 'in the kidney', to: 'into the kidney', from: 'out of the kidney' }, 'ledvina|ledviny|ledvině|ledvinu|ledvině|v ledvině|do ledviny|z ledviny'],
    'a forest where the mushrooms go picking people': [{ n: 'the forest', in: 'in the forest', to: 'to the forest', from: 'from the forest' }, null],
    'the skyship Verdigrace': [{ n: 'the Verdigrace', in: 'aboard the Verdigrace', to: 'aboard the Verdigrace', from: 'off the Verdigrace' }, 'Verdigrace|Verdigrace|Verdigrace|Verdigrace|Verdigrace|na palubě Verdigrace|na palubu Verdigrace|z paluby Verdigrace'],
    'a budget airship with no toilets': [{ n: 'the airship', in: 'aboard the airship', to: 'aboard the airship', from: 'off the airship' }, 'vzducholoď|vzducholodi|vzducholodi|vzducholoď|vzducholodi|na vzducholodi|na vzducholoď|ze vzducholodi'],
    'an underground market where you pay in secrets': [{ n: 'the market', in: 'at the market', to: 'to the market', from: 'from the market' }, null],
    'a board game that declared war': [{ n: 'the board game', in: 'in the board game', to: 'into the board game', from: 'out of the board game' }, null],
    'a retirement home for forgotten gods': [{ n: 'the home', in: 'in the home', to: 'to the home', from: 'from the home' }, 'domov|domova|domovu|domov|domově|v domově|do domova|z domova'],
    // MacGuffins
    'a USB stick full of spores': ['the USB stick', 'flashka|flashky|flashce|flashku|flashkou|flashce'],
    'the last unencrypted mushroom': ['the mushroom', 'houba|houby|houbě|houbu|houbou|houbě'],
    'a footnote on the run': ['the footnote', 'poznámka|poznámky|poznámce|poznámku|poznámkou|poznámce'],
    'a key to every door in the city but one': ['the key', 'klíč|klíče|klíči|klíč|klíčem|klíči'],
    'a tram ticket valid for one miracle': ['the ticket', 'jízdenka|jízdenky|jízdence|jízdenku|jízdenkou|jízdence'],
    'a prescription for antidepressants': ['the prescription', 'recept|receptu|receptu|recept|receptem|receptu'],
    'a strongly worded letter': ['the letter', 'dopis|dopisu|dopisu|dopis|dopisem|dopisu'],
    'a corpse that keeps changing its alibi': ['the corpse', null],
    'a door that only opens inwards, into you': ['the door', null],
    'a dream somebody left on a tram': ['the dream', null],
    'the Card of Overpriced Acquisition': ['the Card', 'Kartička|Kartičky|Kartičce|Kartičku|Kartičkou|Kartičce'],
    'a rulebook nobody ever read': ['the rulebook', null],
    'a hymn with one note too many': ['the hymn', 'hymna|hymny|hymně|hymnu|hymnou|hymně'],
    'a dead god\'s phone number': ['the number', 'číslo|čísla|číslu|číslo|číslem|čísle'],
    // cameos
    'a building that rearranges itself out of boredom': ['the building', null],
    'a lift who insists on being called Mother': ['the lift', null],
    'a four-armed toymaker': ['the toymaker', 'výrobce hraček|výrobce hraček|výrobci hraček|výrobce hraček|výrobcem hraček|výrobci hraček'],
    'a queue that has been dreaming of its own end since spring': ['the queue', null],
    'a cough with opinions': ['the cough', null],
    'a coin that refuses to be spent': ['the coin', null],
    'a pharmacist who mostly sells side effects': ['the pharmacist', null],
    'a skyship captain who has never once landed': ['the captain', 'kapitánka|kapitánky|kapitánce|kapitánku|kapitánkou|kapitánce'],
    'a choir of rusty monks who only sing the dial tone': ['the choir', 'sbor|sboru|sboru|sbor|sborem|sboru'],
    'a bear costume that has had enough': ['the bear costume', 'kostým|kostýmu|kostýmu|kostým|kostýmem|kostýmu'],
    'a pawn still traumatised by the Board Game Wars': ['the pawn', null],
    'a dead god who now lives in a broken amplifier': ['the dead god', null],
    'a man made of tiny cities whose suburbs keep running away': ['the man of tiny cities', null],
    'a divinographer who reads gods by their bones': ['the divinographer', null],
    'a street that moves house when nobody is looking': ['the street', null],
    'a mišutkenn landlord with a strict no-bears policy': ['the landlord', 'domácí|domácího|domácímu|domácího|domácím|domácím'],
    'a talking umbrella': ['the umbrella', 'deštník|deštníku|deštníku|deštník|deštníkem|deštníku'],
    'a philosopher stuck in a revolving door': ['the philosopher', 'filozof|filozofa|filozofovi|filozofa|filozofem|filozofovi'],
};

for (const pool of [HEROES, ANIMAL_HEROES, VILLAINS, ANIMAL_VILLAINS, SETTINGS, MACGUFFINS, CAMEOS, FALLBACK_CAMEOS]) {
    for (const entity of Object.values(pool).flat()) {
        const short = SHORT[entity.en.n];
        if (!short) continue;
        const [en, cs] = short;
        entity.en.short = { ...(typeof en === 'string' ? { n: en } : en), rel: false };
        if (cs) entity.cs.short = caseForms(entity.kind, cs);
    }
}

// ---------------------------------------------------------------------------------------------
// Titles: genre gives the title, tone the "aneb …" / "or, …" subtitle; some pairs have their own.
// ---------------------------------------------------------------------------------------------

const TITLES = {
    'fungal techno': [
        { en: '{^P}: Protocol Mycelium', cs: '{^P}: Protokol Mycelium' },
        { en: 'Ctrl+Alt+Spore', cs: 'Ctrl+Alt+Spora' },
        { en: '{^M} Must Not Germinate', cs: '{^M} nesmí vyklíčit' },
    ],
    'postmodern': [
        { en: 'This Is Not a Novel About {P}', cs: 'Tohle není román o {P.l}' },
        { en: '{^P} {P:Is|Are} Reading This Title', cs: '{^P} právě {P:čte|čtou} tento název' },
        { en: 'Chapter Seven (There Is No Chapter Six)', cs: 'Kapitola sedmá (šestá neexistuje)' },
    ],
    'urban fantasy': [
        { en: '{^P} and {M}', cs: '{^P} a {M}' },
        { en: 'Night Shift {S.in}', cs: 'Noční směna {S.in}' },
        { en: 'Nobody Leaves {S}', cs: 'Nikdo neodejde {S.from}' },
    ],
    'funny animals': [
        { en: '{^P} {P:Has|Have} the Blues', cs: '{^P} {P:má|mají} depku' },
        { en: 'The Tale of {A}', cs: 'O {A.l}' },
        { en: 'Nobody Hugs {P}', cs: 'Nikdo neobjímá {P.a}' },
    ],
    'detective': [
        { en: 'The Case of {M}', cs: 'Případ {M.g}' },
        { en: '{^P} Investigate{P:s|}', cs: '{^P} {P:vyšetřuje|vyšetřují}' },
        { en: 'Murder {S.in}', cs: 'Vražda {S.in}' },
    ],
    'weird fiction': [
        { en: '{^S} Is Dreaming About You', cs: '{^S} sní o vás' },
        { en: 'The Inside of {P}', cs: 'Vnitřek {P.g}' },
        { en: '{^M}', cs: '{^M}' },
    ],
    'mythic war epic': [
        { en: '{^P}: The Last Turn', cs: '{^P}: Poslední tah' },
        { en: 'The Song of {P} and {M}', cs: 'Píseň o {P.l} a {M.l}' },
        { en: 'The War for {S}', cs: 'Válka o {S.a}' },
    ],
    'cosmic horror': [
        { en: 'What Sleeps {S.in}', cs: 'Co spí {S.in}' },
        { en: '{^P} Should Not Have Listened', cs: '{^P} neměl{P:|a|o|i} poslouchat' },
        { en: 'The Silence Behind {M}', cs: 'Ticho za {M.i}' },
    ],
};

const SUBTITLES = {
    tragic: [
        { en: 'How {P} Lost Everything Except {M}', cs: 'Jak {P} přiš{P:el|la|lo|li} o všechno kromě {M.g}' },
        { en: 'Nobody Survives, Not Even the Reader', cs: 'Nikdo nepřežije, ani čtenář' },
        { en: '{^A} Always Wins in the End', cs: '{^A} nakonec vždycky vyhraje' },
    ],
    metaphysical: [
        { en: 'Does {S} Exist If Nobody Pays Rent There?', cs: 'Existuje {S}, když tam nikdo neplatí nájem?' },
        { en: '{^P} Meet{P:s|} {P:Himself|Herself|Itself|Themselves} Halfway', cs: '{^P} {P:potká|potkají} v půli cesty {P:sám sebe|sama sebe|samo sebe|sami sebe}' },
        { en: 'A Footnote to God', cs: 'Poznámka pod čarou k Bohu' },
    ],
    romantic: [
        { en: 'Love {S.in}', cs: 'Láska {S.in}' },
        { en: '{^P} and {A}: A Forbidden Romance', cs: '{^P} a {A}: zakázaná romance' },
        { en: 'Kiss Me Before {M} Goes Off', cs: 'Polib mě, než {M} vybuchne' },
    ],
    existential: [
        { en: 'Why Get Up at All?', cs: 'Proč vůbec vstávat?' },
        { en: '{^P} Wait{P:s|} for {A}', cs: '{^P} {P:čeká|čekají} na {A.a}' },
        { en: 'Is That All There Is {S.in}?', cs: 'To je všechno, co je {S.in}?' },
    ],
    political: [
        { en: 'How We Founded an Anarcho-Syndicalist Union {S.in}', cs: 'Jak jsme {S.in} založili anarchosyndikalistické odbory' },
        { en: 'The Five-Year Plan of {A}', cs: 'Pětiletka {A.g}' },
        { en: '{^P} Run{P:s|} for Office (Unopposed, Unvoted)', cs: '{^P} {P:kandiduje|kandidují} (bez protikandidáta a bez voličů)' },
    ],
    comical: [
        { en: 'Hold My Mead', cs: 'Podrž mi medovinu' },
        { en: '{^A} Strikes Back, and Misses', cs: '{^A} vrací úder a netrefí se' },
        { en: 'Three Weddings and a Mycelium', cs: 'Tři svatby a jedno mycelium' },
    ],
};

const SPECIAL_TITLES = {
    'funny animals|political': {
        en: ['The Tale of the Fascist Stag', 'How We Founded an Anarcho-Syndicalist Union in Our Forest'],
        cs: ['O fašistickém jelenovi', 'Jak jsme v našem lese založili anarchosyndikalistické odbory'],
    },
    'funny animals|existential': {
        en: ['The Bear Who Read Kierkegaard', 'Fear, Trembling and Honey'],
        cs: ['Medvěd, který četl Kierkegaarda', 'Bázeň, chvění a med'],
    },
    'postmodern|existential': {
        en: ['Waiting for Edgar', 'A Novel That Never Quite Arrives'],
        cs: ['Čekání na Edgara', 'Román, který tak úplně nedorazí'],
    },
    'mythic war epic|comical': {
        en: ['War and Cheese', 'Volume One of Seven, with an Appendix on Cheese'],
        cs: ['Vojna a sýr', 'Svazek první ze sedmi s přílohou o sýrech'],
    },
    'cosmic horror|romantic': {
        en: ['Love in the Time of Unspeakable Things', '{^P} and {A}'],
        cs: ['Láska za časů nevyslovitelných hrůz', '{^P} a {A}'],
    },
    'fungal techno|political': {
        en: ['Nineteen Eighty-Spore', 'Big Mycelium Is Watching You'],
        cs: ['1984 spor', 'Velké mycelium tě sleduje'],
    },
    'detective|metaphysical': {
        en: ['Who Killed the Author?', 'A Mystery in Which the Reader Did It'],
        cs: ['Kdo zabil autora?', 'Detektivka, v níž je vrahem čtenář'],
    },
    'urban fantasy|romantic': {
        en: ['Fifty Shades of Mould', '{^P} Fall{P:s|} for {A}'],
        cs: ['Padesát odstínů plísně', '{^P} se {P:zamiluje|zamilují} do {A.g}'],
    },
};

// ---------------------------------------------------------------------------------------------
// Back cover, excerpts, reviews
// ---------------------------------------------------------------------------------------------

const BLURBS = {
    'fungal techno': [
        { en: 'When {P} — {P.desc} — finds {M} {S.in}, the city\'s mushroom exchange crashes overnight. Now {P:he|she|it|they} must outrun {A}, a mycelial firewall and {P:his|her|its|their} own spore allergy.',
          cs: 'Když {P} – {P.desc} – {P:najde|najdou} {S.in} {M.a}, houbová burza se přes noc zhroutí. Teď musí utéct před {A.i}, myceliálním firewallem i vlastní alergií na spory.' },
        { en: '{^S} runs on a mycelial network that miraculously appeared overnight, all by itself. {^P} — {P.desc} — is the only one who notices that someone unknown is moving through the network.',
          cs: '{^S} běží na myceliální síti, která se zázračně sama objevila přes noc. {^P} – {P.desc} – si jako jedin{P:ý|á|é|í} všimne, že na síti se pohybuje ještě někdo neznámý.' },
    ],
    'postmodern': [
        { en: 'This blurb was meant to introduce {P}, {P.desc}. Unfortunately {P:he|she|it|they} read the manuscript first and lodged a complaint with {A}.',
          cs: 'Tahle anotace měla představit {P.a} – {P.desc}. Jenže {P:si přečetl|si přečetla|si přečetlo|si přečetli} rukopis dřív než vy a {P:podal|podala|podalo|podali} stížnost u {A.g}.' },
        { en: 'A novel in which nothing happens {S.in}, beautifully. {^P} look{P:s|} for {M}. {^M} looks back. Chapter twelve is printed upside down on purpose.',
          cs: 'Román, ve kterém se {S.in} krásně nic neděje. {^P} {P:hledá|hledají} {M.a}. {^M} hledá {P.a} taky. Dvanáctá kapitola je schválně vytištěná vzhůru nohama.' },
    ],
    'urban fantasy': [
        { en: 'By day, {P} {P:is|are} {P.desc}. By night, {P:he|she|it|they} guard{P:s|} {S} against {A}, armed only with {M} and a library card.',
          cs: 'Ve dne {P:je|jsou} {P} {P.desc}. V noci {P:chrání|chrání} {S.a} před {A.i} – vyzbrojen{P:|a|o|i} jen {M.i} a průkazkou do knihovny.' },
        { en: 'Nobody leaves {S} after midnight. {^P} must, because {K} is waiting outside with {M} and a very bad plan.',
          cs: 'Po půlnoci nikdo neodchází {S.from}. {^P} ale musí, protože venku čeká {K} s {M.i} a velmi špatným plánem.' },
    ],
    'funny animals': [
        { en: '{^P} — {P.desc} — {P:has|have} had a rough autumn. Supplies of {M} are running low {S.in}, {A} is gaining followers, and every Thursday everyone goes to therapy.',
          cs: '{^P} – {P.desc} – {P:má|mají} za sebou těžký podzim. {^S.in} dochází {M}, {A} sbírá stoupence a každý čtvrtek všichni chodí na terapii.' },
        { en: 'A heart-warming story about friendship, depression and {M}. {^P} and {K} set out to learn why everyone {S.in} is so sad.',
          cs: 'Hřejivý příběh o přátelství, depresi a {M.l}. {^P} a {K} se vydávají zjistit, proč jsou všichni {S.in} tak smutní.' },
    ],
    'detective': [
        { en: '{^S}, three in the morning. A body, {M}, and a witness who saw nothing except {A}. {^P} light{P:s|} a cigarette {P:he won\'t|she won\'t|it won\'t|they won\'t} finish and get{P:s|} to work.',
          cs: '{^S}, tři hodiny ráno. Tělo, {M} a svědek, který neviděl nic kromě {A.g}. {^P} si zapálí cigaretu, kterou nedokouří, a pustí se do práce.' },
        { en: 'Someone has stolen {M} from {S}, and everyone has an alibi except {K}. {^P} — {P.desc} — suspect{P:s|} {A}. {^A} suspects the reader.',
          cs: 'Někdo ukradl {M.a} {S.from} a alibi mají všichni kromě {K.g}. {^P} – {P.desc} – {P:podezírá|podezírají} {A.a}. {^A} podezírá čtenáře.' },
    ],
    'weird fiction': [
        { en: '{^P} wake{P:s|} up {S.in} and find{P:s|} {M} where {P:his|her|its|their} heart used to be. It is the best day of {P:his|her|its|their} life, and it seems it will never end.',
          cs: '{^P} se {S.in} {P:probudí|probudí} a místo srdce {P:najde|najdou} {M.a}. Je to nejlepší den {P:jeho|jejího|jeho|jejich} života a zdá se, že nikdy neskončí.' },
        { en: 'Nothing in this book is real except {A}. {^P} and {K} try to prove otherwise, using only {M} and the rules of a game nobody remembers.',
          cs: 'Nic v téhle knize není skutečné kromě {A.g}. {^P} a {K} se snaží dokázat opak – jen pomocí {M.g} a pravidel hry, která si nikdo nepamatuje.' },
    ],
    'mythic war epic': [
        { en: 'For a thousand turns {S} has been at war with {A}. Now {P} — {P.desc} — has drawn {M}, and the board will never be the same.',
          cs: 'Už tisíc tahů zuří {S.in} válka s {A.i}. Teď {P} – {P.desc} – {P:vytáhl|vytáhla|vytáhlo|vytáhli} {M.a} a hrací deska už nikdy nebude jako dřív.' },
        { en: 'Sing, o Muse, of {P}, who went {S.to} with {K} and came back with {M} and no explanation whatsoever.',
          cs: 'Zpívej, Múzo, o {P.l}, {P:jenž odešel|jež odešla|jež odešlo|již odešli} {S.to} s {K.i} a {P:vrátil|vrátila|vrátilo|vrátili} se s {M.i} a bez jakéhokoli vysvětlení.' },
    ],
    'cosmic horror': [
        { en: 'Something is waiting {S.in}, and it knows the name of {P}. {^P} — {P.desc} — should have stopped reading at chapter three. {P:He|She|It|They} didn\'t. Neither will you.',
          cs: 'Cosi čeká {S.in} a zná jméno {P.g}. {^P} – {P.desc} – měl{P:|a|o|i} přestat číst u třetí kapitoly. Nepřestal{P:|a|o|i}. Vy taky ne.' },
        { en: 'There is a hymn with one note too many, and {A} is humming it. {^P} and {K} must find {M} before the last verse — or the last reader.',
          cs: 'Existuje hymna s jednou notou navíc a {A} si ji pobrukuje. {^P} a {K} musí najít {M.a} dřív, než dozní poslední sloka – nebo poslední čtenář.' },
    ],
};

const BLURB_TAILS = {
    tragic: { en: 'Bring tissues. Bring two packs.', cs: 'Vezměte si kapesníky. Dva balíčky.' },
    metaphysical: { en: 'Ask yourself: who is reading here, and who is being read?', cs: 'Zeptejte se sami sebe: kdo tu vlastně čte a kdo je čten?' },
    romantic: { en: 'Includes one (1) kiss, tastefully described over forty pages.', cs: 'Obsahuje jeden (1) polibek, vkusně popsaný na čtyřiceti stranách.' },
    existential: { en: 'You will finish it. Then what?', cs: 'Dočtete to. A co pak?' },
    political: { en: 'Banned in three countries, which is excellent for sales.', cs: 'Zakázáno ve třech zemích, což skvěle pomáhá prodejům.' },
    comical: { en: 'Warning: may cause snorting in public places.', cs: 'Upozornění: může vyvolat chrochtání na veřejnosti.' },
};

const OPENINGS = {
    'fungal techno': [
        { en: 'Chapter One. The button mushrooms arrived at 3:14 a.m., which was rude. {^P} {P:was|were} asleep {S.in} when {M} began to hum. "Nobody move," said {K}. Nobody had invited {K:him|her|it|them}.',
          cs: 'Kapitola první. Žampiony dorazily ve 3:14 ráno, což bylo nezdvořilé. {^P} {P:spal|spala|spalo|spali} {S.in}, když {M} začal{M:|a|o|y} bzučet. „Nikdo se nehýbejte,“ řekl{K:|a|o|i} {K}. Nikdo {K:ho|ji|ho|je} nepozval.' },
        { en: 'Chapter One. {^S} smelled of damp keyboards and ambition. {^P} plugged in {M}. The lights went out across the whole district, and somewhere, {A} smiled.',
          cs: 'Kapitola první. {^S} {S:páchl|páchla|páchlo|páchly} vlhkými klávesnicemi a ambicemi. {^P} {P:zapojil|zapojila|zapojilo|zapojili} {M.a}. V celé čtvrti zhasla světla a kdesi se usmál{A:|a|o|i} {A}.' },
    ],
    'postmodern': [
        { en: 'Chapter Seven. (Chapters one to six were deleted by {A}.) {^P} sat {S.in}, aware that you were watching, and tried to look interesting.',
          cs: 'Kapitola sedmá. (Kapitoly jedna až šest smazal{A:|a|o|i} {A}.) {^P} {P:seděl|seděla|sedělo|seděli} {S.in}, {P:věděl|věděla|vědělo|věděli}, že se díváte, a {P:snažil|snažila|snažilo|snažili} se vypadat zajímavě.' },
        { en: 'This sentence is about {P}. This one is about {M}. This one is the author crying for help. Please ignore it.',
          cs: 'Tahle věta je o {P.l}. Tahle o {M.l}. Tahle je autorovo volání o pomoc. Ignorujte ji, prosím.' },
    ],
    'urban fantasy': [
        { en: 'Chapter One. The tram {S.to} only stops for people with exact change who know the ticket inspectors\' incantations. {^P} qualified on both counts.',
          cs: 'Kapitola první. Tramvaj {S.to} zastavuje jen těm, kdo mají přesně odpočítané drobné a ovládají revizorská zaklínadla. {^P} {P:splňoval|splňovala|splňovalo|splňovali} obojí.' },
        { en: '"You\'re late," said {K}. It was true: {P} had spent the night {S.in} hiding {M} from {A}.',
          cs: '„Jdeš pozdě,“ řekl{K:|a|o|i} {K}. Byla to pravda: {P} {P:strávil|strávila|strávilo|strávili} noc {S.in} schováváním {M.g} před {A.i}.' },
    ],
    'funny animals': [
        { en: 'Chapter One. It was a Tuesday, and {P} did not want to get out of the burrow. Outside, {A} was giving a speech about order.',
          cs: 'Kapitola první. Bylo úterý a {P} se {P:nechtěl|nechtěla|nechtělo|nechtěli} vyhrabat z nory. Venku měl{A:|a|o|i} {A} projev o pořádku.' },
        { en: '"Do you ever feel," said {K}, "like {M} is the only thing holding this forest together?" {^P} said nothing, having eaten it an hour ago.',
          cs: '„Nepřipadá ti někdy,“ řekl{K:|a|o|i} {K}, „že celý les drží pohromadě jen {M}?“ {^P} mlčel{P:|a|o|i}, protože {M:ho|ji|ho|ho} před hodinou snědl{P:|a|o|i}.' },
    ],
    'detective': [
        { en: 'Chapter One. The rain fell on {S} like an overdue invoice. {^P} looked at {M} and knew at once: this was the work of {A}.',
          cs: 'Kapitola první. Déšť padal {S.in} jako faktura po splatnosti. {^P} se {P:podíval|podívala|podívalo|podívali} na {M.a} a hned {P:věděl|věděla|vědělo|věděli}: tohle je dílo {A.g}.' },
        { en: '"I didn\'t do it," said {K}. Nobody had asked. {^P} wrote it down, underlined it twice and ordered another coffee.',
          cs: '„Já to nebyl{K:|a|o|i},“ řekl{K:|a|o|i} {K}. Nikdo se neptal. {^P} si to {P:zapsal|zapsala|zapsalo|zapsali}, dvakrát podtrhl{P:|a|o|i} a {P:objednal|objednala|objednalo|objednali} si další kávu.' },
    ],
    'weird fiction': [
        { en: 'Chapter Zero. {^S} was smaller on the inside. {^P} noticed at once, then forgot, then noticed again.',
          cs: 'Kapitola nultá. {^S} {S:byl|byla|bylo|byly} uvnitř menší než zvenku. {^P} si toho hned {P:všiml|všimla|všimlo|všimli}, pak zapomněl{P:|a|o|i} a pak si všiml{P:|a|o|i} znovu.' },
        { en: 'In the dream of {P} there was a door, behind the door was {M}, and behind {M} was {A}, eating a sandwich.',
          cs: 'Ve snu {P.g} byly dveře, za dveřmi {M} a za {M.i} {A}, {A:který jedl|která jedla|které jedlo|kteří jedli} chlebíček.' },
    ],
    'mythic war epic': [
        { en: 'Book the First. In the beginning was the Turn, and the Turn belonged to {A}. Then {P} cheated.',
          cs: 'Kniha první. Na počátku byl Tah a ten Tah patřil {A.d}. Pak {P} {P:podvedl|podvedla|podvedlo|podvedli}.' },
        { en: 'Seven armies marched {S.to}. Six of them had read the rules. {^P} led the seventh.',
          cs: '{^S.to} táhlo sedm armád. Šest z nich četlo pravidla. Sedmou vedl{P:|a|o|i} {P}.' },
    ],
    'cosmic horror': [
        { en: 'Chapter One. The first time {P} heard the note, {P:he|she|it|they} thought it was the plumbing. The plumbing {S.in} has been dead for nine hundred years.',
          cs: 'Kapitola první. Když {P} ten tón {P:uslyšel|uslyšela|uslyšelo|uslyšeli} poprvé, {P:myslel|myslela|myslelo|mysleli} si, že to jsou trubky. Trubky {S.in} jsou ale devět set let mrtvé.' },
        { en: 'Do not read this paragraph aloud. {^P} did, once, {S.in}, and that is how {A} learned {P:his|her|its|their} address.',
          cs: 'Tenhle odstavec nečtěte nahlas. {^P} to jednou {S.in} {P:udělal|udělala|udělalo|udělali} a tak se {A} {A:dozvěděl|dozvěděla|dozvědělo|dozvěděli} {P:jeho|její|jeho|jejich} adresu.' },
    ],
};

const MIDDLES = {
    tragic: [
        { en: '"I was going to tell you," whispered {K}, "but {A} got here first." {^P} looked at {M} for a long time, then put it away with everything else {P:he|she|it|they} had lost.',
          cs: '„Chtěl{K:|a|o|i} jsem ti to říct,“ zašeptal{K:|a|o|i} {K}, „ale {A} tu byl{A:|a|o|i} dřív.“ {^P} se dlouho {P:díval|dívala|dívalo|dívali} na {M.a}. Pak {M:ho|ji|ho|ho} {P:uložil|uložila|uložilo|uložili} ke všemu ostatnímu, o co {P:přišel|přišla|přišlo|přišli}.' },
        { en: '{^J} came to the funeral in a hat. Nobody knew whose funeral it was. {^P} suspected it might be {P:his|her|its|their} own, a little early.',
          cs: '{^J} {J:přišel|přišla|přišlo|přišli} na pohřeb v klobouku. Nikdo nevěděl, čí pohřeb to je. {^P} {P:měl|měla|mělo|měli} podezření, že {P:jeho|její|jeho|jejich} vlastní, jen trochu předčasný.' },
    ],
    metaphysical: [
        { en: '"What if," said {K}, "{S} is just a thought {A} is having?" {^P} stopped walking. Somewhere, {A} lost the thread, and half the street disappeared.',
          cs: '„Co když,“ řekl{K:|a|o|i} {K}, „{S} je jen myšlenka, kterou má {A}?“ {^P} se {P:zastavil|zastavila|zastavilo|zastavili}. Kdesi {A} ztratil{A:|a|o|i} nit a půlka ulice zmizela.' },
        { en: '{^P} met {J} at the edge of the page. "Are we being read?" asked {J}. "Constantly," said {P}, and turned {P:his|her|its|their} better side to the reader.',
          cs: '{^P} {P:potkal|potkala|potkalo|potkali} {J.a} na okraji stránky. „Čte nás někdo?“ zeptal{J:|a|o|i} se {J}. „Pořád,“ odpověděl{P:|a|o|i} {P} a natočil{P:|a|o|i} se ke čtenáři lepším profilem.' },
    ],
    romantic: [
        { en: '{^P} and {A} reached for {M} at the same moment. Their hands touched. Somewhere {S.in}, {K} began to play the accordion, unasked.',
          cs: '{^P} a {A} sáhli po {M.l} ve stejnou chvíli. Ruce se jim dotkly. Kdesi {S.in} začal{K:|a|o|i} {K} nevyžádaně hrát na harmoniku.' },
        { en: '"I\'ve loved you since chapter two," said {J}. "This is chapter two," said {P}. "I know," said {J}. "It\'s been a long chapter."',
          cs: '„Miluju tě od druhé kapitoly,“ řekl{J:|a|o|i} {J}. „Tohle je druhá kapitola,“ odpověděl{P:|a|o|i} {P}. „Já vím,“ řekl{J:|a|o|i} {J}. „Je to dlouhá kapitola.“' },
    ],
    existential: [
        { en: '{^P} sat {S.in} and waited for {A}. {^K} sat down next to {P:him|her|it|them} and waited too, mostly out of politeness.',
          cs: '{^P} {P:seděl|seděla|sedělo|seděli} {S.in} a {P:čekal|čekala|čekalo|čekali} na {A.a}. {^K} si {K:přisedl|přisedla|přisedlo|přisedli} a čekal{K:|a|o|i} taky, hlavně ze slušnosti.' },
        { en: '"What is the point of {M}?" asked {J}. {^P} thought about it for eleven pages and then said, "Lunch."',
          cs: '„Jaký smysl má {M}?“ zeptal{J:|a|o|i} se {J}. {^P} o tom jedenáct stran {P:přemýšlel|přemýšlela|přemýšlelo|přemýšleli} a pak {P:řekl|řekla|řeklo|řekli}: „Oběd.“' },
    ],
    political: [
        { en: 'The first meeting of the union took place {S.in}. {^K} chaired, {J} took the minutes, and {P} moved to abolish {A}. The motion passed with one vote against: {A}.',
          cs: 'První schůze odborů proběhla {S.in}. Předsedal{K:|a|o|i} {K}, zápis psal{J:|a|o|i} {J} a {P} {P:navrhl|navrhla|navrhlo|navrhli} zrušit {A.a}. Návrh prošel s jedním hlasem proti – hlasem {A.g}.' },
        { en: '{^A} issued Decree No. 1: {M} belongs to the people, meaning to {A:him|her|it|them}. Decree No. 2: there is no Decree No. 1. {^P} started printing leaflets.',
          cs: '{^A} {A:vydal|vydala|vydalo|vydali} dekret č. 1: {M} patří lidu, tedy {A:jemu|jí|jemu|jim}. Dekret č. 2: žádný dekret č. 1 neexistuje. {^P} začal{P:|a|o|i} tisknout letáky.' },
    ],
    comical: [
        { en: '{^P} slipped on {M}, fell {S.to}, landed on {A}, and everyone laughed at {P:him|her|it|them} for a long time afterwards.',
          cs: '{^P} {P:uklouzl|uklouzla|uklouzlo|uklouzli} na {M.l}, {P:spadl|spadla|spadlo|spadli} {S.to}, {P:přistál|přistála|přistálo|přistáli} na {A.l} a všichni se {P:mu|jí|mu|jim} ještě pak dlouho smáli.' },
        { en: '"Hold my mead," said {K}. Three chapters later, {J} is still holding it.',
          cs: '„Podrž mi medovinu,“ řekl{K:|a|o|i} {K}. O tři kapitoly později ji {J} pořád drží.' },
    ],
};

const ENDINGS = {
    tragic: [
        { en: 'And so {P} gave up {M} to save {S}. Nobody {S.in} noticed a thing. Nobody ever does. THE END.',
          cs: 'A tak {P} {P:obětoval|obětovala|obětovalo|obětovali} {M.a}, aby zachránil{P:|a|o|i} {S.a}. {^S.in} si ničeho nevšimli. To se stává. KONEC.' },
        { en: 'The last thing {P} heard was {A} saying, "Told you." The last thing {P} said was, "Fair."',
          cs: 'Poslední, co {P} {P:slyšel|slyšela|slyšelo|slyšeli}, bylo, jak {A} {A:říká|říká|říká|říkají}: „Říkal{A:|a|o|i} jsem to.“ Poslední, co {P} {P:řekl|řekla|řeklo|řekli}, bylo: „Fér.“' },
    ],
    metaphysical: [
        { en: 'In the end {P} closed the book. Inside the book, {P} closed the book. Somewhere in between, {A} is still reading.',
          cs: 'Nakonec {P} knihu {P:zavřel|zavřela|zavřelo|zavřeli}. V té knize {P} knihu {P:zavřel|zavřela|zavřelo|zavřeli}. A někde mezi tím {A} pořád čte.' },
        { en: '{^P} finally understood everything. It took four seconds; then {P:he|she|it|they} forgot it, which was for the best.',
          cs: '{^P} konečně {P:pochopil|pochopila|pochopilo|pochopili} všechno. Trvalo to čtyři vteřiny, pak to zapomněl{P:|a|o|i}, což bylo jedině dobře.' },
    ],
    romantic: [
        { en: 'They married {S.in}. {^A} caught the bouquet and wept. {^K} officiated, despite having no qualifications whatsoever.',
          cs: 'Vzali se {S.in}. Kytici chytil{A:|a|o|i} {A} a rozplakal{A:|a|o|i} se. Oddával{K:|a|o|i} {K}, přestože k tomu {K:neměl|neměla|nemělo|neměli} žádné oprávnění.' },
        { en: '"Stay," said {A}. "They need us {S.in}." {^P} stayed. Nobody {S.in} needed them. They stayed anyway. THE END.',
          cs: '„Zůstaň,“ řekl{A:|a|o|i} {A}. „{^S.in} nás potřebují.“ {^P} {P:zůstal|zůstala|zůstalo|zůstali}. {^S.in} je nikdo nepotřeboval. Zůstali stejně. KONEC.' },
    ],
    existential: [
        { en: '{^A} never came. {^P} went home, made tea, and found that it was enough. Almost.',
          cs: '{^A} nikdy {A:nepřišel|nepřišla|nepřišlo|nepřišli}. {^P} {P:šel|šla|šlo|šli} domů, {P:uvařil|uvařila|uvařilo|uvařili} si čaj a {P:zjistil|zjistila|zjistilo|zjistili}, že to stačí. Skoro.' },
        { en: '"So that\'s it?" asked {P}. "That\'s it," said the book. "Unless you count the appendix." Nobody counts the appendix.',
          cs: '„Tak to je všechno?“ zeptal{P:|a|o|i} se {P}. „To je všechno,“ řekla kniha. „Pokud nepočítáte přílohu.“ Přílohu nikdo nepočítá.' },
    ],
    political: [
        { en: '{^A} fell on a Thursday. By Friday {P} had become exactly as bad, and the union went on strike again. The struggle continues in volume two.',
          cs: '{^A} {A:padl|padla|padlo|padli} ve čtvrtek. V pátek už byl{P:|a|o|i} {P} přesně tak zl{P:ý|á|é|í} a odbory znovu vstoupily do stávky. Boj pokračuje ve druhém díle.' },
        { en: 'The revolution won. The new government\'s first decree banned this book. {^P} signed it personally.',
          cs: 'Revoluce zvítězila. Prvním dekretem nové vlády byl zákaz této knihy. {^P} ho {P:podepsal|podepsala|podepsalo|podepsali} osobně.' },
    ],
    comical: [
        { en: 'Everything worked out. {^A} opened a bakery. {^K} got a tattoo. {^P} {P:is|are} still looking for the other shoe.',
          cs: 'Všechno dobře dopadlo. {^A} si {A:otevřel|otevřela|otevřelo|otevřeli} pekárnu. {^K} si {K:nechal|nechala|nechalo|nechali} udělat tetování. {^P} pořád {P:hledá|hledají} druhou botu.' },
        { en: 'And then {M} exploded. Nobody was hurt, except emotionally, and {A}, also emotionally.',
          cs: 'A pak {M} vybuchl{M:|a|o|y}. Nikdo nebyl zraněn, jen citově, a {A} taky jen citově.' },
    ],
};

/** Reviews: only from people the player has actually met (journal id), plus a few anonymous ones. */
const CRITICS = [
    { req: null, en: '"I didn\'t understand a word of it, but I feel that the author understood me completely." — Master Thaal', cs: '„Nepochopil jsem z toho ani slovo, ale cítil jsem, že autor pochopil mne samotného.“ — mistr Thaal' },
    { req: 'met_ravla', en: '"Too long. I read it twice." — Ravla', cs: '„Moc dlouhé. Přečetla jsem to dvakrát.“ — Ravla' },
    { req: 'heliodor_lore', en: '"We read it in shifts. Oorarabaz woke up for chapter nine." — Heliodor', cs: '„Četli jsme to na směny. Kvůli deváté kapitole jsme vzbudili i Oorarabaze.“ — Heliodor' },
    { req: 'kloor_venn_meeting', en: '"Side effects include feelings. Somewhat." — Kloor Venn', cs: '„Vedlejší účinky: city. Tak trochu.“ — Kloor Venn' },
    { req: 'magnekin_reveal', en: '"A real citizen would buy two copies. I bought two copies." — Magnekin', cs: '„Skutečný občan by si koupil dva výtisky. Koupil jsem si dva výtisky.“ — Magnekin' },
    { req: 'phor_calesta', en: '"It fossilises beautifully." — Phor Calesta', cs: '„Krásně to zkamenělo.“ — Phor Calesta' },
    { req: 'lift_mother_meeting', en: '"Finally, someone writes about {S}. Going up?" — the Lift-Mother', cs: '„Konečně někdo píše o {S.l}. Jedeme nahoru?“ — Lift-Mother' },
    { req: 'met_dr_elphi', en: '"Derivative. I\'d have dreamed it better." — Dr. Elphi Quarn', cs: '„Odvozené. Já bych to vysnila líp.“ — Dr. Elphi Quarn' },
    { req: 'gnur_meeting', en: '"Ain\'t read it. Sold it twice, though." — Gnur', cs: '„Nečet’ jsem to. Ale dvakrát jsem to prodal.“ — Gnur' },
    { req: 'met_seldo', en: '"I laughed, I cried, I filed a complaint." — Seldo Thrice-Corrected', cs: '„Smál jsem se, plakal jsem, podal jsem stížnost.“ — Seldo Třikrát-Korigovaný' },
    { req: null, en: '"{^P}? That\'s me. I\'m suing the author." — someone at the Screaming Cork', cs: '„{^P}? Vždyť to jsem já. Budu autora žalovat.“ — kdosi ve Řvoucím korku' },
    { req: null, en: '"Ten out of ten. Would get lost {S.in} again." — a disoriented tourist', cs: '„Deset z deseti. Klidně bych se {S.in} ztratil znovu.“ — jeden dezorientovaný turista' },
];

const THANKS = {
    en: 'P.S. The author thanks {L}, without whom this book would have been shorter.',
    cs: 'P.S. Autor děkuje {L.d}, bez {L:kterého|které|kterého|kterých} by tahle kniha byla kratší.',
};

// ---------------------------------------------------------------------------------------------
// Edgar's reactions while the book takes shape
// ---------------------------------------------------------------------------------------------

const TOPIC_REACTIONS = [
    { en: '{^K}! Oh, that goes in. That absolutely goes in.', cs: '{^K}! To tam musí být. To tam rozhodně musí být.' },
    { en: 'I can already see {K} in chapter four, ruining everything.', cs: 'Už vidím, jak ve čtvrté kapitole všechno pokazí {K}.' },
    { en: '{^K}. Yes. Every great novel needs one.', cs: '{^K}. Ano. Každý velký román něco takového potřebuje.' },
];

const TONE_REACTIONS = {
    tragic: { en: 'Tragic. I\'m already sad for the characters, and they don\'t even exist yet.', cs: 'Tragický. Už teď je mi líto všech postav, a to ještě ani neexistují.' },
    metaphysical: { en: 'Metaphysical. Good. If anyone asks what it\'s about, we say "everything" and leave quickly.', cs: 'Metafyzický. Výborně. Kdyby se někdo ptal, o čem to je, řekneme „o všem“ a rychle odejdeme.' },
    romantic: { en: 'Romantic! I\'ve never written a kiss. I\'ve read about them. They seem… damp.', cs: 'Romantický! Ještě nikdy jsem nepsal o polibku. Četl jsem o nich. Vypadají… vlhce.' },
    existential: { en: 'Existential. Finally, a book where nobody expects a happy ending, least of all me.', cs: 'Existenciální. Konečně kniha, kde nikdo nečeká šťastný konec, a já nejmíň.' },
    political: { en: 'Political. Careful — the last mišutkenn who wrote a political novel is now a rug.', cs: 'Politický. Opatrně – poslední mišutkenn, který napsal politický román, je teď předložka u krbu.' },
    comical: { en: 'Comical! Good. People laugh at me anyway; this way I get paid for it.', cs: 'Komický! Dobře. Lidi se mi smějí tak jako tak – takhle za to aspoň dostanu zaplaceno.' },
};

const GENRE_REACTIONS = {
    'fungal techno': { en: 'A fungal techno-thriller. Hackers, spores, and a mushroom that knows your password.', cs: 'Houbový techno-thriller. Hackeři, spory a houba, která zná vaše heslo.' },
    'postmodern': { en: 'Postmodern. So the book will know it\'s a book. Poor thing.', cs: 'Postmoderní. Takže kniha bude vědět, že je kniha. Chudinka.' },
    'urban fantasy': { en: 'Urban fantasy. Magic, but with public transport.', cs: 'Městská fantasy. Kouzla, ale s městskou hromadnou dopravou.' },
    'funny animals': { en: 'Funny animals with depression. Finally, a genre about my family.', cs: 'Vtipná zvířata s depresí. Konečně žánr o mé rodině.' },
    'detective': { en: 'A detective novel. Somebody dies on page one and everyone is relieved.', cs: 'Detektivka. Na první stránce někdo umře a všem se uleví.' },
    'weird fiction': { en: 'Dreamy weird fiction. Nobody will understand it, so nobody can criticise it.', cs: 'Snová weird fiction. Nikdo tomu nebude rozumět, takže to nikdo nemůže kritizovat.' },
    'mythic war epic': { en: 'A mythic war epic. Seven volumes, minimum. I\'ll need a bigger table.', cs: 'Mýtický válečný epos. Minimálně sedm dílů. Budu potřebovat větší stůl.' },
    'cosmic horror': { en: 'Cosmic horror. Something ancient and terrible, and very rude about it.', cs: 'Kosmický horor. Něco prastarého a strašlivého, a navíc nevychovaného.' },
};

const VILLAIN_REACTION = { en: 'And every proper story needs a villain. Ours will be… {A}.', cs: 'A každý pořádný příběh potřebuje padoucha. Naším padouchem bude… {A}.' };

const PROTAGONIST_REACTIONS = [
    { en: 'Our hero: {P} — {P.desc}. I\'m in love already.', cs: 'Náš hrdina: {P} – {P.desc}. Už teď jsem zamilovaný.' },
    { en: '{^P}! No — wait — yes. {^P}, {P.desc}. Perfect.', cs: '{^P}! Ne – počkat – ano. {^P}, {P.desc}. Dokonalé.' },
];

const SETTING_REACTIONS = [
    { en: '{^S}. I can smell it from here.', cs: '{^S}. Už to cítím až sem.' },
    { en: 'And it all happens {S.in}. Of course it does.', cs: 'A celé se to odehraje {S.in}. No jasně.' },
];

// ---------------------------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------------------------

/**
 * The cast for a draft (any pick may still be missing). draft = { seed, topics[], tone, genre,
 * protagonist, setting }. The genre bends the hero and villain pools.
 */
export function bookRoles(draft) {
    const seed = draft.seed ?? 0;
    const animals = draft.genre === 'funny animals';
    const roles = {};
    if (draft.protagonist) {
        roles.P = animals ? ANIMAL_HEROES[draft.protagonist] : pick(seed, 'P', HEROES[draft.protagonist] || []);
    }
    if (draft.tone) {
        roles.A = animals ? ANIMAL_VILLAINS[draft.tone] : pick(seed, 'A', VILLAINS[draft.tone] || []);
    }
    if (draft.setting) roles.S = pick(seed, 'S', SETTINGS[draft.setting] || []);
    if (draft.genre) roles.M = pick(seed, 'M', MACGUFFINS[draft.genre] || []);

    // Cameos from the chosen topics; the gaps are filled with two distinct stand-ins.
    const topics = draft.topics || [];
    const spare = [...FALLBACK_CAMEOS];
    if (pickIndex(seed, 'K', 2)) spare.reverse();
    const cameo = (i) => CAMEOS[topics[i]] || spare.shift();
    roles.K = cameo(0);
    roles.J = cameo(1);
    if (topics[2] && CAMEOS[topics[2]]) roles.L = CAMEOS[topics[2]];
    return roles;
}

/** One finished book in `lang`. `knows(journalId)` filters the reviewers to people the player met. */
export function composeBook(draft, lang, knows = () => false) {
    const seed = draft.seed ?? 0;
    const roles = bookRoles(draft);
    const R = (tpl) => render(tpl, roles, lang);
    const choose = (slot, arr) => pick(seed, slot, arr)?.[lang] ?? '';

    const special = SPECIAL_TITLES[`${draft.genre}|${draft.tone}`];
    const heading = lang === 'en' ? titleCase : (t) => t;
    const named = new Set();
    const title = heading(render(special ? special[lang][0] : choose('title', TITLES[draft.genre] || []), roles, lang, named));
    const subtitle = heading(render(special ? special[lang][1] : choose('subtitle', SUBTITLES[draft.tone] || []), roles, lang, named));
    const fullTitle = lang === 'cs' ? `${title} aneb ${subtitle}` : `${title}; or, ${subtitle}`;

    const blurb = [R(choose('blurb', BLURBS[draft.genre] || [])), BLURB_TAILS[draft.tone]?.[lang] ?? ''].filter(Boolean).join(' ');
    const excerpts = {
        opening: R(choose('opening', OPENINGS[draft.genre] || [])),
        middle: R(choose('middle', MIDDLES[draft.tone] || [])),
        ending: R(choose('ending', ENDINGS[draft.tone] || [])),
    };

    // Three reviews, in a stable order shuffled by the seed.
    const eligible = CRITICS.filter(c => !c.req || knows(c.req))
        .map(c => ({ c, k: hash(`${seed}|critic|${c.en}`) }))
        .sort((a, b) => a.k - b.k)
        .slice(0, 3)
        .map(({ c }) => R(c[lang]));
    const thanks = roles.L ? R(THANKS[lang]) : '';

    return { title, subtitle, fullTitle, blurb, excerpts, critics: eligible, thanks };
}

/** Edgar's reaction to the pick just made: kind = topic | tone | genre | protagonist | setting. */
export function edgarReaction(kind, draft, lang, topicId = null) {
    const seed = draft.seed ?? 0;
    const roles = bookRoles(draft);
    switch (kind) {
        case 'topic': {
            const K = CAMEOS[topicId];
            if (!K) return null;
            return render(pick(seed, `topic|${topicId}`, TOPIC_REACTIONS)[lang], { ...roles, K }, lang);
        }
        case 'tone': return TONE_REACTIONS[draft.tone]?.[lang] ?? null;
        case 'genre': {
            const line = GENRE_REACTIONS[draft.genre]?.[lang];
            return line ? `${line} ${render(VILLAIN_REACTION[lang], roles, lang)}` : null;
        }
        case 'protagonist': return render(pick(seed, 'reactP', PROTAGONIST_REACTIONS)[lang], roles, lang);
        case 'setting': return render(pick(seed, 'reactS', SETTING_REACTIONS)[lang], roles, lang);
        default: return null;
    }
}

/** Every pick id the book understands (for tests / validation). */
export const BOOK_IDS = {
    topics: Object.keys(CAMEOS),
    tone: Object.keys(VILLAINS),
    genre: Object.keys(TITLES),
    protagonist: Object.keys(HEROES),
    setting: Object.keys(SETTINGS),
};
