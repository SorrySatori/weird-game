/**
 * Czech game strings – oznámení, popisy úkolů, kategorie deníku
 */
export default {
    cutscene: {
    },
    shop: {
        balance: 'Dinárů: {amount}',
        price: 'Cena: {price} dinárů',
        buy: 'Koupit',
        sell: 'Prodat',
        buyItem: 'Koupit předmět',
        sellItem: 'Prodat předmět',
        forSale: 'Zboží na prodej',
        yourItems: 'Vaše věci',
        noItems: 'Nic tu není',
        nothingToSell: 'Nemáte nic, co bychom od vás koupili.',
        noDescription: 'Bez popisu.',
        names: {
            zerren: 'Zerreniny kuriozity',
            kloor: 'Kloorovo Oltracové emporium',
            cork: 'Krám ve Řvoucím korku',
        },
    },
    scraperAmbra: {
        elphiPresent: 'Dr. Elphi pracuje u svého terminálu',
        arrival: 'Patro 177-Tiché: studio Dr. Elphi',
    },
    skyship: {
        toolObtained: 'Získáno: kalibrační nástroj výtahu',
    },
    club: {
        beginsTitle: 'Feral Toast začínají hrát',
        beginsSub: 'Klubem se valí ultranoise futurepunk',
        endsTitle: 'Feral Toast dohráli',
        endsSub: 'Zkouška končí',
        performance: [
            "Kapela je úplně ponořená do zkoušky a tvoří něco víc než jen hluk.",
            "Cítíš, že za tím hlukem je ještě něco... něco, co k tobě promlouvá.",
            "Těžko to přesně pojmenovat, ale máš pocit, že kdysi existovala bytost, které by se dalo říkat třeba... Bůh hluku?",
            "Možná je to jeden z bohů, kteří přišli do Horní Morkezely zemřít... a ten hluk je to, co po něm zbylo.",
            "Jak posloucháš dál, hluk kolem tebe jako by nabýval tělesné podoby.",
            "Vzduchem se splétají vlákna zvuku a tvoří jakýsi oblak vědomí.",
            "Cítíš zvláštní sounáležitost s Bohem hluku.",
            "Zaplaví tě hluboké poznání: Bůh hluku se nenarodil, byl stvořen...",
            "Dnes z jeho vzoru zbývají jen náznaky – pohřbené v magnetickém prachu, slabě rezonující v rozbitých zesilovačích, v rádiové mlze a v kostech reproduktorů.",
            "Cítíš, že hudba kapely je jeho pozůstatek – způsob, jak se s Bohem hluku spojit.",
        ],
    },
    shedRegistration: {
        queueForms: 'Sotva vejdeš do kanceláře, obklopí tě podivné snové bytosti a seřadí se do fronty...',
        queueFaded: 'Obyvatelé fronty se rozplynuli',
        clerkAppeared: 'Objevil se vrchní úředník...',
        clerkReady: 'Vrchní úředník je připraven tě obsloužit',
        slotUnlocked: 'Odemčen nový slot pro symbionta!',
        maxSlots: 'Už máte nejvyšší povolený počet slotů pro symbionty!',
    },
    // Předměty v inventáři podle id (název/popis v inventáři, u efektů a v obchodech).
    // `names`/`descriptions` = texty podle `variant` u předmětů, jejichž popis závisí na tom, jak je hráč získal.
    items: {
        // Zerreniny zvukové ampule (utils/Recordings.js)
        ampule_squirrel: { name: 'Ampule: Veverčí hubování', description: 'Zatavená skleněná ampule, na dotek teplá. Přilož ji k uchu a malý stromolezec z dob před Vynořením ti přes staletí vyhubuje. Podle Zerren to zvíře dávno vyhynulo.' },
        ampule_purr: { name: 'Ampule: Spokojená kočka', description: 'Sedm vteřin kočičího předení na něčí hrudi. Nikdo na Voxmarketu neví na čí. Zerren si jednu nechává pro sebe a tu neprodá.' },
        ampule_liftmother: { name: "Ampule: První slovo Lift-Mother", description: "Údajně úplně první zvuk, který Lift-Mother vydala, když procitla: dlouhé skřípění a bublání, jako by se snažila dovolat někomu, kdo není doma. K ampuli patří osvědčení o pravosti, psané rukou. Rukou Zerren." },
        ampule_surrender_chord: { name: "Ampule: Akord kapitulace", description: "Zvuk, kterým skončily Staré války. Podle legendy ho v jediném okamžiku zahrály všechny válečné stroje na všech frontách a pak už odmítly udělat cokoli dalšího. Města druhý den ráno podepsala příměří a začal věk Ludarchů. Trvá půl vteřiny. Je to nejdražší půlvteřina na celém Voxmarketu." },
        ampule_burning_iceberg: { name: "Ampule: Hořící ledovec", description: "Nahráno toho jediného odpoledne Deskovkových válek, kdy jeden Ludarch rozhodl, že led je hořlavý. Do večera to pravidlo zrušili." },
        ampule_mimic_bird: { name: "Ampule: Ptačí napodobitel", description: "Pták z dob před Vynořením, který napodoboval každý zvuk, jaký kdy zaslechl. Polovina nahrávky je ptačí zpěv. Tu druhou nikdo nechápe. Optimisté (a blázni) tvrdí, že se ji pták naučil z budoucnosti." },
        ampule_old_train: { name: "Ampule: Vlak, který někam jel", description: "Vnitřek vlaku z Předdoby, který drnčí ke stanici vytištěné v jízdním řádu. V depu za Škrabákem se ještě pořád dají nalézt staré koleje. Co přesně znamenalo „včas“, si už nikdo nepamatuje." },
        ampule_unanswered_call: { name: "Ampule: Nepřijatý hovor", description: "Na doprovodném lístku stojí: Záznam jedné z nejstrašnějších věcí na světě: hovoru z neznámého čísla. Prý zaznamenán ještě ve staré Nexicorp Tower. Nepíše se tu, jestli ten telefon někdo nakonec zvedl." },
        ampule_first_ledger: { name: "Ampule: První kniha zápisů", description: "Šicí stroj ve sklepě Radnice sešívá vazbu úplně první knihy Inkoustového tribunálu. Tento historický moment ovšem zajímal tak leda úředníky, podle cedulky tu ampule leží už pěkně dlouho." },
        ampule_spin_hymn: { name: "Ampule: Hymna odstřeďování", description: "Pračka z Předdoby při posledním odstřeďování. Podle cedulky nahrávku pořídil Rezavý chór a považoval ji za obzvláště vydařenou." },
        market_map: { name: 'Mapa Voxmarketu', description: 'Podrobná mapa Voxmarketu a okolí.' },
        forgotten_elevator_button: { name: 'Zapomenutý výtahový knoflík', description: 'Starý výtahový knoflík s podivnými značkami. Zdá se, že patří k patru, které oficiálně neexistuje.' },
        grayOltrac: { name: 'Šedý Oltrac', description: 'Běžná odrůda Oltracu. Mírné halucinogenní účinky.' },
        violetOltrac: { name: 'Fialový Oltrac', description: 'Středně silná odrůda Oltracu. Zostřuje vnímání a přináší živé vize.' },
        amberOltrac: { name: 'Jantarový Oltrac', description: 'Nejvzácnější a nejsilnější podoba Oltracu. Prý dovolí nahlédnout za závoj skutečnosti.' },
        pliers: { name: 'Kleště', description: 'Obyčejné kleště. Hodí se na opravy i na vytahování věcí.' },
        scraper_backyard_key: { name: 'Klíč od dvorku', description: 'Klíč od dvorku Škrabáku 1140. Jako by slabě zářil.' },
        'forged-arms-permission': { name: 'Padělané povolení na více rukou', description: 'Přesvědčivý padělek Formuláře o výjimce pro umělce, který držiteli dovoluje mít legálně více rukou pro odbornou práci.' },
        vestigel: { name: 'Spisovatelův Vestigel', description: 'Malý, jemně vyřezávaný žeton, který Edgar našel schovaný v plyšové hračce. Zdá se, že má nějaký tajemný význam.' },
        'game-prototype': { name: 'Prototyp hry Sekty a sázky', description: 'Prototyp Ortolanovy hry Sekty a sázky, ve které se snažíš založit vlastní sektu. Vypadá velmi zábavně, ale Ortolan ještě nemá úplně vyladěnou část, ve které se může tvůj nejvěrnější odštěpit a založit si ultraortodoxní křídlo uvnitř sekty. Na druhou stranu dobře zmastroval featuru, kde se hlavním objektem uctívání mohou stát kočky, což je dobrá strategie k vítězství.' },
        'legged-shark-statuette': { name: 'Soška žraloka s nohama', description: 'Soška žraloka s nohama, téměř bez ploutví. Ortolan si už přesně nepamatuje, odkud ji vzal, ale prý je z nějaké deskovky o upírech a démonech.' },
        'black-cactus-card': { name: 'Karta Black Cactus', description: 'Black Cactus ze hry Absolutely Profane Life: Normality, kdysi nejdražší karta ve hře, za kterou byli sběratelé v aukcích schopni zaplatit miliony dinárů. Dneska už žádnou cenu nemá, protože nenasytnost autorů hry všechny naštvala do té míry, že ji přestali hrát. Ortolan si ji nechal z nostalgie.' },
        'hopsalot-figurine': { name: 'Sběratelská figurka Maxima Hopsalota', description: 'Sběratelská figurka Maxima Hopsalota, patrona Lagerlandie. Originální balení doprovázel sixpack piv, ale ten zřejmě Ortolan vypil.' },
        'apocalypse-cop-figure': { name: 'Figurka Apocalypse Copa', description: 'Figurka Apocalypse Copa, detektiva s drinkem Tequila Sunrise v ruce. Ortolan ho má obzvlášť rád, protože mu připomíná období, kdy po pádu Ludarchů propadl alkoholismu. Je ze hry, kterou nedělal on, ale někdo jiný. Ortolan má pocit, že ho budeš potřebovat víc než on.' },
        'living-core': { name: 'Živé jádro', description: 'Pulzující jádro z živého kovu, násilím vyrvané z Boudy.', descriptions: { careful: 'Pulzující jádro z živého kovu, opatrně vyjmuté z Boudy.' } },
        'rulebook-fragment': { name: 'Útržek pravidel', description: 'Vytržená stránka z nedokončených pravidel nějaké hry. Popisuje mechaniku výměny vzpomínek.' },
        'silent-sentence': { name: 'Tichá věta', description: 'Prázdná kartička, která přesto nese význam. Může se hodit, až dojdou slova.' },
        'artisan-exemption-form': { name: 'Formulář o výjimce pro umělce', description: 'Úřední formulář udělující z tvůrčích důvodů výjimku ze standardních omezení počtu končetin. Schváleno pro Ortolana.' },
        'deformity-form': { name: 'Formulář o zděděné deformitě', description: 'Úřední formulář, který klasifikuje více končetin jako prospěšnou mutaci, nikoli deformitu. Schváleno k použití.' },
        'special-dispensation': { name: 'Zvláštní dispens', description: 'Vzácný dokument, který dovoluje úpravu končetin bez standardního papírování. Získán nonverbální cestou.' },
        'temporary-permit': { name: 'Dočasné povolení', description: 'Prozatímní dokument udělující omezený přístup. Není plně schválený, ale lepší než nic.' },
    },
    crossroad: {
        plantGrows: 'Z mrtvoly vyrůstá podivná rostlina. A nad ní si všimneš ještě něčeho...',
    },
    entry: {
        thaalDeparted: 'Houbový mistr odešel do hospody...',
    },
    symbiontUi: {
        ability: 'Schopnost',
        empty: 'Pohodlné místečko na tvém těle, kde se může usídlit symbiont.',
        sealed: 'Tenhle slot je zatím zavřený. Potřebuješ na něj povolení.',
        dormant: 'Teď mlčí.',
    },
    // Hlasy symbiontů (anglické originály jsou v SymbiontSystem; tohle jsou lokalizované kopie).
    symbionts: {
        'thorne-still': {
            name: 'Thorne-Still',
            ability: 'Mozková hniloba',
            dialogs: {
                main: {
                    text: "Thorne-Still ti šeptá v hlavě: ‚Čau, šéfe, jak je? Měl bych ti asi připomenout, že moje síla roste s rozkladem – a naopak, když bude růstu moc, budu muset odejít. Přemíra růstu mi fakt nesedí, kapitáne. Mozkovou hnilobu používej s rozumem... Je to mocný nástroj, ale když si nedáš pozor, dokáže někomu pořádně zprasit mozek. Takže ji radši nezkoušej na lidech, které máš rád.‘",
                    options: ['Zeptat se na Mozkovou hnilobu', 'Zeptat se na Thorne-Stilla'],
                },
                ability: {
                    text: "Mozková hniloba působí lidem zmatenost, zapomnětlivost nebo stav, kdy jsou náchylnější k sugesci. Prostě vypouštím slabé psychosporové emise, které v okolních myslích krátkodobě roztřepí myšlení. Říkám sice prostě, ale tak jednoduché to zas není. Navíc pokaždé, když ji použijeme, budu potřebovat trochu tvých spor. Nezabere to na každého, ale neboj, řeknu ti, kdy ji můžeme použít.",
                    options: ['Zpět'],
                },
                about: {
                    text: "Jsem symbiont, kterému se daří v rozkladu. Kdysi jsem byl součástí něčeho většího, ale teď existuji v prostorách mezi realitami. Heh, dělám si prdel – zrovna teď existuju ve tvém žaludku. Díky našemu poutu se tu dá docela pohodlně bydlet, ale přemíra růstové energie mě z tvého těla vyžene.",
                    options: ['Zpět'],
                },
            },
        },
    },
    // Hlášky posunu Růst/Rozklad: důvod + společný dovětek (notifications.worldSoursDecay / worldLeansGrowth)
    gd: {
    },
    notifications: {
        hintNoSpores: 'Na nápovědu nemáš dost spor (potřebuješ {cost})',
        hintNothing: 'Tady není na co kliknout',
        newQuest: 'Nový úkol',
        questUpdated: 'Úkol aktualizován',
        questCompleted: 'Úkol dokončen!',
        questFailed: 'Úkol selhal',
        journalUpdated: 'Deník aktualizován',
        reputationChange: '{faction} – reputace {sign}{change}',
        moneyGain: '+{amount} dinárů',
        moneyLoss: '-{amount} dinárů',
        purchased: 'Zakoupeno: {item}',
        sold: 'Prodáno: {item}',
        notEnoughMoney: 'Nedostatek dinárů!',
        alreadyOwned: 'Tohle už u sebe máš.',
        ampuleSilent: 'Ampule mlčí.',
        newItemAvailable: 'Nová položka v nabídce: {item}',
        failedToSell: 'Nepodařilo se prodat předmět',
        addedToInventory: 'Přidáno do inventáře: {item}',
        addedToInventoryQty: 'Přidáno {qty}× {item}',
        effectsStart: '{item} začíná působit...',
        effectsEnd: 'Účinky předmětu {item} odezněly.',
        symbiontGained: 'Získán symbiont: {name}',
        worldSoursDecay: 'Svět se naklání k Rozkladu.',
        worldLeansGrowth: 'Svět se naklání k Růstu.',
        growthIncreased: 'Růst vzrostl!',
        growthDecreased: 'Růst poklesl!',
        decayIncreased: 'Rozklad vzrostl!',
        decayDecreased: 'Rozklad poklesl!',
    },

    factions: {
        RustChoir: { name: 'Rezavý chór', description: 'Frakce, která zachraňuje rez a rozklad a dává jim nový účel.' },
        PithReclaimers: { name: 'Inkoustový tribunál', description: 'Městská byrokracie: rovnováha a pořádek udržované inkoustem, pečetí a účetní knihou.' },
        LumenDirectorate: { name: 'Direktorát', description: 'Spojenectví, které si cení růstu a veškerého života.' },
        status: 'Postavení: {status}',
        standings: {
            revered: 'Uctívaný', honored: 'Vážený', friendly: 'Přátelský', liked: 'Oblíbený', neutral: 'Neutrální',
            disliked: 'Neoblíbený', unfriendly: 'Nepřátelský', hostile: 'Zarytý nepřítel', hated: 'Nenáviděný',
        },
    },

    // trip po Oltracu (systems/EffectsSystem.js): výkyvy spor a co se hrdinovi honí hlavou
    drugs: {
        sporesUp: 'Cítíš, jak se v tobě množí spory. (+{n})',
        sporesDown: 'Cítíš, jak z tebe spory ustupují. ({n})',
        surge: 'Tělem ti projede vlna houbové energie! (+{n})',
        loss: 'Najednou cítíš, jak slábne tvoje spojení se sporami! ({n})',
        comments: {
            grayOltrac: [
                "Stěny… dýchají? Jen trošičku.",
                "Slyším barvy. Počkat, to nedává smysl.",
                "Mám pocit, že mám prsty z hub…",
                "Všechno je tak nějak rozmazané na okrajích.",
                "Spory na mě šeptají.",
                "Má ten stín tancovat?",
            ],
            violetOltrac: [
                "Vzduch je HUSTÝ fialovými možnostmi!",
                "Myšlenky mi bují jako mycelium!",
                "Teď VIDÍM, jak je všechno se vším propojené!",
                "Houbové vědomí mi všude ukazuje vzorce!",
                "Čas se do sebe skládá jako klobouk houby!",
                "HARDCORE! Je tohle HARDCORE? Řekl bych, že jo!",
            ],
            amberOltrac: [
                "ZÁVOJ SE ROZTRHL! VIDÍM ZA BLÁNU SKUTEČNOSTI!",
                "Moje tělo se rozpouští ve zlaté spory… NÁDHERA!",
                "Věčná Houba promlouvá skrze mě! STAL JSEM SE MYCELIEM!",
                "Hvězdy jsou jen plodnice vesmírných hub! UŽ TO VŠECHNO DÁVÁ SMYSL!",
                "Unikl jsem z vězení svého masa! JSEM VŠUDE A NIKDE!",
                "Vesmír je jen jedna obří spora, která čeká, až vykvete.",
                "Chci jít domů… Počkat… Vždyť už doma jsem.",
            ],
        },
    },

    mood: {
        liris: {
            growthDominant: "Vstupuješ na palubu a voníš po zeleném počasí. Kapradí rostoucí na palubě se k tobě naklání. Vítej.",
            decayDominant: "Něco s tebou stoupá nahoru – hniloba ve větru. Drž to po větru dál od mé vzducholodě, buď tak laskav.",
        },
        gnur: {
            growthDominant: "Cítím kolem tebe moc růstu. Kazí mi to zboží. Zelené věci se tady dole moc neprodávají.",
            decayDominant: "Heh. Máš v sobě tu správnou hnilobu, cizinče – cítím ji až sem. Vyjdeme spolu dobře.",
        },
        brukk: {
            growthDominant: "Páchneš mízou a jarem. Stroje nevěří rostoucím věcem. Ani já ne.",
            decayDominant: "Koroze v tobě zpívá, bratře. Chór slyší jednoho z nás.",
        },
        ravla: {
            growthDominant: "Všechen ten růst na tobě mě znervózňuje. Rostoucí věci pořád něco chtějí, a chtění je drahé.",
            decayDominant: "Rozklad ti sluší. Snáz se s tebou jedná – lakomí to mají vždycky snazší.",
        },
        kloor: {
            growthDominant: "A hele, ty tvoje spory, ty vypadají na prvotřídní zboží. Nějaký bych koupil.",
            decayDominant: "Heh, ty tvoje spory, ty vypadají na prvotřídní zboží. V tomhle městě plným rozkladu a hniloby přece jen není nějaký ten růst občas na škodu.",
        },
    },

    journal: {
    },

    sporeBar: {
        label: 'SPORY',
        tooltipTitle: 'Sporová Energie',
        tooltipDesc: 'Používá se pro houbové schopnosti a rituály.',
        tooltipCurrent: 'Aktuálně: {current}/{max}',
    },
};
