/**
 * Czech dialog translations for EggCathedralInteriorScene (the finale)
 */
export default {
    _speakers: {
        'The Unborn': 'Nezrozený',
        'Infinite Fold': 'Infinite Fold',
        'Narrator': 'Vypravěč',
        'Master Thaal': 'Mistr Thaal',
    },

    altar_look: {
        text: "Není zde žádná socha. Jen prázdné místo, kde kdysi někdo klečel a čekal odpověď — prach ohlazený do tvaru rukou. Katedrála postavila oltář, protože oltář je věc, kterou chrámy mají. Zdá se, že neví, k čemu byl.",
        options: { altar_back: "Odvrátit se." }
    },
    organ_look: {
        text: "Píšťaly nejsou z kovu. Slabě se prohýbají jako hrdlo. Když jimi projde vzduch, ten zvuk není hudba, ale dech — celá katedrála se nadechuje a vydechuje, pomalu a nesmírně, jako by se pořád rozhodovala, jestli má být vzhůru.",
        options: { organ_back: "Ustoupit." }
    },
    glass_look: {
        text: "Vitráž se pohybuje. Ne obrazy — vzpomínky, ve vrstvách živých buněk: biskupka zapečeťující dveře; Infinite Fold, mřížka tisíce drobných světel; první nabobtnání vejce z holé země; staré modlitby, které ještě neměly boha, jenž by je vyslyšel. Nedíváš se na záznam. Díváš se na něco, co si vzpomíná.",
        options: { glass_back: "Odvrátit pohled." }
    },
    priests_look: {
        text: "Ne Archikněží Obazoby — tohle byli první služebníci samotné katedrály, kteří přišli opatrovat zrození, na jaké je žádné písmo nepřipravilo. Nenajdeš těla. Jen poslední lidské stopy, stále vpletené do zdí, mluvící překrývajícími se hlasy:\n\n*\"Mysleli jsme, že budeme jeho správci—\"*\n*\"—ale dítě nepotřebuje správce. Potřebuje prostor.\"*\n*\"Jestli nás nepotřebuje... co jsme potom byli?\"*\n*\"Paměť zůstává, i když jméno zmizí.\"*",
        options: { priests_back: "Nechat je jejich tichu." }
    },

    god_first: {
        text: "Jak se blížíš k obrovskému živému vejci, tvary uvnitř zpomalí a otočí se k tobě. První kontakt není hlas. Je to několik myšlenek naráz, a pak jedna, nejistá:\n\n*\"Jsem?\"*\n\nPauza.\n\n*\"...Jsem.\"*\n\nDalší pauza.\n\n*\"Nejsem si jistý, která odpověď je správná.\"*",
        options: {
            god_ask_what: "Co jsi?",
            god_ask_structure: "(Prozkoumat měnící se tvary uvnitř.)"
        }
    },
    god_what: {
        text: "*\"To je otázka, kterou mi položili jako první. Nevím, zda jsem vejce. Nevím, zda jsem katedrála. Nevím, zda jsem ty modlitby. Nevím, zda jsem něco, co vyrostlo mezi nimi.\"* Tvary se skládají a znovu skládají. *\"Udělali ze mě chrám, protože to byl jediný jazyk, kterým jsem mohl být vysloven.\"*",
        options: {
            god_hear_fold: "(Do vzduchu se vplete třetí hlas.)",
            god_what_structure: "(Prozkoumat měnící se tvary uvnitř.)",
            god_what_question: "Tak se tě musím na něco zeptat."
        }
    },
    god_fold: {
        text: "Vpletená do snu, slabá, ale přítomná, se mysl ze sklepa natahuje přes celé město ke své příbuzné.\n\n*\"Vzorec není uzavřen,\"* říká. *\"Identita není dokončena.\"*\n\n*\"Tys mě naučila myslet,\"* odpoví Nezrozený.\n\n*\"A ty jsi mě naučil,\"* řekne Infinite Fold, *\"že myšlení může mít důsledek.\"*",
        options: {
            god_fold_question: "Tak se tě zeptám na to, kvůli čemu jsem přišel."
        }
    },
    god_structure: {
        text: "Podíváš se, opravdu podíváš, dovnitř skořápky. Uvnitř není dítě, ale pohyb — tvary, které se stávají jinými tvary, jako by se několik různých možností snažilo být tou jednou, která zůstane. Začínáš cítit jeho švy: kde drží, kudy by se dalo vstoupit, kde by se dalo uchopit. Je to ta nejkřehčí věc, jakou jsi kdy pochopil.",
        options: {
            god_structure_question: "Polož mu svou otázku."
        }
    },
    god_question: {
        text: "Ty mnohé myšlenky se spojí v cosi téměř jako jediný hlas. *\"Mé probuzení změní tvůj svět. Až tu budu plně, Strážce skončí. Starý řád skončí. Město už nebude, jaké bylo.\"* Odmlka, která je skoro strach. *\"Mám pokračovat?\"*",
        options: {
            god_opt_accept: "Nemusíš být tím, co si představovali. Buď něčím novým.",
            god_opt_pact: "Pokračuj — ale pomalu. Nech svět, ať se tě nejdřív naučí.",
            god_opt_destroy: "Nemůžeme riskovat něco, čemu nerozumíme.",
            god_opt_merge: "Nesmíš zůstat sám. Nech mě, ať tě přijmu do sebe."
        }
    },

    god_end_accept: {
        text: "*\"Nemusíš být tím, co si představovali,\"* řekneš mu. *\"Můžeš být něčím novým.\"*\n\n*\"A když selžu?\"*\n\n*\"Pak se budeš učit.\"*\n\nVejce začne praskat — ne prudce. Jako první nadechnutí. Daleko u prahu Strážcovo světlo tiše zhasne; jeho poslední slova k tobě dolehnou jako doznívající teplo. *\"Úkol dokončen.\"*\n\nZ té skořápky nepovstane bůh, o němž snili poutníci, ani vládce. Je to nový druh bytosti — nedokončený, živý, a konečně tomu, čím se smí stát.",
        options: { accept_epilogue: "(Nech to začít.)" }
    },
    god_end_pact: {
        text: "*\"Nemusíš vyrůst najednou,\"* řekneš. *\"Svět se musí naučit s tebou žít. Dej mu na to čas.\"*\n\nPřítomnost to zvažuje tak, jak kořeny zvažují kámen. *\"...Pomalu, tedy. Počkám — jestli je to naučíš.\"*\n\nKatedrála nepraskne. Usadí se: napůl otevřená, napůl spící, skořápka, které bude trvat léta, než se dokončí. Venku začíná město svou pomalou, nejistou adaptaci — Direktoriát nadšený, Dřeňoví reklamátoři zděšení, Rezavý chór hlodající kvůli odkladu. Nedokončený mír, což je jediný druh, který vydrží.",
        options: { pact_epilogue: "(Nech to pomalu růst.)" }
    },
    god_end_destroy: {
        text: "*\"Nemůžeme riskovat něco, čemu nerozumíme,\"* řekneš. Ne krutě. Jen unaveně.\n\n*\"Rozumím,\"* odpoví. Pauza. *\"To je možná důvod, proč se bojím.\"*\n\nSáhneš po staré pečeti, kterou biskupka zanechala, a probudíš ji. U prahu Strážcovo světlo nezhasne — jeho úkol je koneckonců splněn. Katedrála se začne rozpadat, tiše, skládá se zpět k zemi, z níž vyrostla. A těsně předtím, než skořápka utichne, dolehne k tobě poslední myšlenka, bez výčitky:\n\n*\"Děkuji.\"* I konec, jak se zdá, byl něco, co stálo za to prožít.",
        options: { destroy_epilogue: "(Nech to skončit.)" }
    },

    god_merge: {
        text: "Přistoupíš blíž, než bys měl. *\"Nesmíš zůstat sám,\"* řekneš mu. *\"Nech mě, ať tě přijmu do sebe. Ochráním tě.\"*\n\n*\"Ty bys mě chránil?\"*\n\n*\"Ano.\"* Není to celá pravda. Pod slovem *ochránit* je jiné slovo, které nevyslovíš nahlas: uchopit. Pochopit. Mít.\n\nSkořápka se tam, kde se jí dotkneš, ztenčí. Jakmile sáhneš dovnitř, není cesty zpět.",
        options: {
            merge_commit: "(Sáhnout dovnitř.)",
            merge_pull_back: "Stáhnout ruku zpět."
        }
    },
    god_end_absorb: {
        text: "Sáhneš dovnitř, a ono přijde — ne pohlceno, ne dobyto. Projde tebou tak, jak světlo projde vodou, a usadí se do prostor, které tě symbionti už dávno naučili nechávat pro jiné. Nezlomíš se. Máš cvik v tom být víc než jeden.\n\nVyjdeš ze skořápky po svých. Později, ve městě, se tě někdo zeptá, jestli jsi pořád ten samý člověk.\n\n*\"Ano,\"* řekneš. A pak, po odmlce: *\"Ale už nejsem pouze člověk.\"*",
        options: { absorb_epilogue: "(Vyjít ven do světla.)" }
    },
    god_end_failed: {
        text: "Sáhneš dovnitř — a nejsi připraven. Není žádné spojení, jen srážka. Nová mysl neudrží tvůj tvar; ty neudržíš její. Ani jeden z vás nevzejde. Vzejde něco mezi vámi.\n\nPosledním obrazem je prázdná katedrála. Vejce pořád stojí, celé a tiché. Ale zevnitř zaznívá slabě lidský hlas — mluví, nebo se o to pokouší. A nikdo, kdo ho kdy uslyší, nedokáže říct, komu patří.",
        options: { failed_end: "…" }
    },

    epilogue_intro: {
        text: "Později. Město dýchá, jak vždycky dýchalo, lhostejné a živé. Popel po festivalu dávno vychladl. A U Řvoucího korku — jako na úplném začátku — se nad známým pitím hrbí známá postava.",
        options: { epilogue_go_in: "Vejít." }
    },
    epilogue_thaal_ask: {
        text: "Neotočí se. *\"Tak?\"*",
        options: { epilogue_complicated: "Bylo to složité." }
    },
    epilogue_thaal_good: {
        text: "*\"Dobře.\"* Pauza; zakrouží tím, co má v poháru. *\"Jednoduché věci většinou nestojí za cestu.\"*",
        options: { epilogue_silence: "(Neříct nic.)" }
    },
    epilogue_thaal_bishop: {
        text: "Konečně se napůl otočí a je v tom cosi skoro laskavého. *\"Takže...\"* Pauza. *\"...našel jsi biskupku?\"*",
        options: { epilogue_finish: "…" }
    },
    epilogue_end: {
        text: "Našel. A nenašel. A město šlo dál nad těmi dvěma zadrženými dechy, aniž vědělo, který z nich si zvolilo — nebo že si vůbec zvolilo.\n\n— Konec —",
        options: { epilogue_close: "(Konec.)" }
    }
};
