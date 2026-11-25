/**
 * Czech for Ulvarex's encounter (utils/ulvarexEncounter.js, its states are shared by ScraperScene, Shed521GateScene
 * and SkyshipBoardScene: lang/cs/dialogs/index.js merges this file into theirs).
 * Ulvarex je v češtině ONA: teatrální, trochu ješitná, laskavá ke všemu živému.
 */
export default {
    _speakers: {
        'Narrator': 'Vypravěč',
        'Ulvarex': 'Ulvarex',
    },
    ulvarex_notice: {
        text: "Divoké barvy způsobené Oltracem ti ještě mihotají před očima, když si všimneš, že kaluž u tvých nohou neodráží šedé nebe, ale oranžový západ slunce. Kde by se ale vzal? Na obloze žádné slunce není. Pak si ale uvědomíš, že to není západ slunce, ale oranžové oko, které se upírá přímo na tebe.",
        options: {
            ulvarex_crouch: "Sklonit se ke kaluži.",
            ulvarex_step_back: "Couvnout. To je jen Oltrac.",
        },
    },
    ulvarex_reach: {
        text: "Jakmile se nad vodu nakloníš, odraz se změní. Ozve se hlas, který se ozývá přímo ve tvé hlavě. „No konečně. Někdo, kdo skutečně vidí. Poděkuj tomu, kdo ti dal Oltrac, ať už to byl kdokoliv: bez něj bys mnou prostě prošel. Jsem v téhle kaluži už... no, když je někdo dvourozměrný, čas mu běží jinak.“",
        options: {
            ulvarex_what_are_you: "Co jsi zač?",
            ulvarex_why_puddle: "Co děláš v kaluži?",
        },
    },
    ulvarex_what: {
        text: "„Jsem Ulvarex, Vypůjčený obzor. Symbiontka vnímání. Dokážu tkát přeludy tak přesvědčivé, že oklamou ruku stejně jako oko. Jenže potřebuju hostitele. Někoho, kdo má nějakou vhodnou organickou hmotu, ve které bych se mohla uhnízdit. Třeba tebe. Jsi nasáklý potenciálem jako houba. Hehe.“",
        options: {
            ulvarex_what_bond: "Co by znamenalo spojit se s tebou?",
            ulvarex_no_tricks: "O žádné triky nestojím.",
        },
    },
    ulvarex_why: {
        text: "„Svezla jsem se na obzvlášť přesvědčivém západu slunce, spadla s ním v dešti na tohle město a skončila tady, vtisknutá do tenké blány na hladině. Trapné, vážně. Pro bytost s nekonečným tvůrčím potenciálem je kaluž dost ponižující adresa. A vidět mě můžou jen lidi na Oltracu nebo obzvlášť citliví jedinci.“",
        options: {
            ulvarex_what_are_you: "A co vlastně jsi zač?",
            ulvarex_leave_puddle: "Tak tě tu nechám, i s kaluží.",
        },
    },
    ulvarex_bond: {
        text: "„Usadím se ti za očima. Živím se sporami, takže dokud budeš nějaké mít, nemusíš se ničeho bát. Na oplátku získáš schopnost Tkaní přeludů: přesvědčivé iluze, které nikdo neprohlédne. No, tedy alespoň ne hned. A ještě jednu věc bys měl vědět. Mám ráda, když věci žijí a rostou. Pokud mé přeludy využiješ, abys například ochránil něco živého, budu ráda. Z přeludu upředeného z chamtivosti se mi dělá špatně.“",
        options: {
            ulvarex_bond_yes: "Dobře. Spoj se se mnou.",
            ulvarex_think: "Musím si to rozmyslet.",
        },
    },
    ulvarex_accept: {
        text: "Z kaluže se odloupne tenká vrstva světla, ovine se ti kolem ruky a šplhá po paži, teplý, beztížný a slabě třpytivý opar. Na okamžik vypadá svět jinak: každý stín má hloubku, každý povrch strukturu, které sis nikdy nevšiml. „Tak. Už jsem ti za očima. Moc silně nemrkej, lechtá to.“",
        options: {
            ulvarex_welcome: "Tak vítej, Ulvarex.",
        },
    },
    ulvarex_no_slot: {
        text: "Záře v kaluži pohasne. „Aha. Ty už jsi obsazený. Každý kout v tobě má nájemníka.“ Prohlíží si tě jako zájemce o byt, který už je pronajatý. „Prý v Registraci v Boudě 521 prodávají místo navíc. Pořiď si ještě jeden slot, dej si další trip a koukej pod nohy. Budu nejspíš v nějaké kaluži.“",
        options: {
            ulvarex_be_back: "Vrátím se.",
        },
    },
    ulvarex_decline: {
        text: "„Jak myslíš. Budu tady. Nebo v nějaké jiné kaluži a budu rozjímat o povaze existence a sebereflexi. Kdyby sis to rozmyslel, dej si další trip a koukej pod nohy.“",
        options: {
            ulvarex_leave: "Odejít.",
        },
    },
    ulvarex_later: {
        text: "„Dej si načas. Po kalužích se potloukám už pár set trávení, pár navíc už přežiju. Jen nezapomeň: bez Oltracu mě asi ani neuvidíš.“",
        options: {
            ulvarex_leave: "Odejít.",
        },
    },
    ulvarex_reconsider: {
        text: "Záře podobná západu slunce v kaluži pořád hoří. Ulvarex tě pozoruje.",
        options: {
            ulvarex_reconsider_yes: "Dobře, spoj se se mnou.",
            ulvarex_what_bond: "Co by znamenalo spojit se s tebou?",
            ulvarex_not_yet: "Ještě ne.",
        },
    },
    // další trip: už se znají
    ulvarex_again: {
        text: "Kaluž u tvých nohou zase září oranžovým západem slunce a slunce v ní se otevře v oko. „Á, to jsi ty. Tak co, rozmyslel sis to?“",
        options: {
            ulvarex_reconsider_yes: "Dobře, spoj se se mnou.",
            ulvarex_remind_bond: "Připomeň mi, co by to spojení znamenalo.",
            ulvarex_not_yet: "Ještě ne.",
        },
    },
};
