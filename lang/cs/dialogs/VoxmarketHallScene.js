/**
 * Czech dialog translations for VoxmarketHallScene
 * Speakers: Hesh & Vell (twin auctioneers), Sister Calyx (Pith Reclaimers), Heartbroker Lune, Heir to the Yellow Aquarium, The Silence Beneath the Stairwell
 */
export default {
    _speakers: {
        'Hesh & Vell': 'Hesh a Vell',
        'Sister Calyx': 'Sestra Calyx',
        'Heartbroker Lune': 'Srdcokupec Lune',
        'Heir to the Yellow Aquarium': 'Dědic Žlutého akvária',
        'The Silence Beneath the Stairwell': 'Ticho pod schodištěm',
    },

    // ——— Hesh & Vell ———
    twins_start: {
        text: {
            twins_start_return: `„Vítejte zpět," říká Hesh. Vell bezhlasně artikuluje tatáž slova o půl sekundy později, rty formují každou slabiku v podivném zpoždění. „Aukce brzy začne. Rozhlédněte se. Společensky se zapojte. Položky jsou vystaveny u zadní stěny."`,
            twins_start_confused_return: `„Vítejte... zpět," říká Hesh. Vell bezhlasně artikuluje slova o půl sekundy později, ale klopýtá — rytmus nesedí, synchronizace je narušená. „Aukce... brzy začne," pokračuje Hesh a Vellovy rty dohánějí příliš pozdě.\n\nStále fungují, ale jejich proslulé tempování je narušené. Ostří licitátorů — otupené.`,
            twins_start_first: `„Vítejte v Aukční hale Voxmarketu," říká Hesh — nebo je to Vell? Jeden mluví, druhý bezhlasně artikuluje tatáž slova o půl sekundy pozadu, čímž vytváří znepokojivý efekt ozvěny bez skutečné ozvěny.\n\n„Já jsem Hesh," říká ten nalevo. „A já jsem Vell," artikuluje ten napravo, o moment pozadu. „Vedeme aukci. Všechny prodeje jsou konečné. Všechny příhozy jsou závazné. Všechna lítost je vaše vlastní."\n\nJejich synchronizace je hypnotická — nacvičená, přesná a hluboce znepokojivá.`,
        },
        options: {
            how_does_the_auction_work: "Jak funguje aukce?",
            whats_being_auctioned_today: "Co se dnes draží?",
            im_here_for_a_specific_lot_a_chronoslurry_toadlet: "Jsem tu kvůli konkrétní položce — Chronobřečkovému Ropušátku.",
            why_do_you_do_that_the_delayed_mouthing: "Proč to děláte — to opožděné artikulování?",
            brain_rot_disrupt_their_synchronization: "[Mozkový rozklad] Narušit jejich synchronizaci.",
        }
    },

    twins_auction_rules: {
        text: `„Pravidla jsou jednoduchá," říká Hesh. Vellovy rty následují. „Položky se představují jedna po druhé. Dražba začíná na uvedené ceně. Zvedněte ruku pro příhoz. Nejvyšší nabízející, když zvoláme ‚Uzavřeno', vyhrává.\n\nPlatba je okamžitá. Pouze zlaté — žádný barter, žádné vestigely, žádné sliby. Pokud nemůžete zaplatit, odejdete. Pokud způsobíte scénu, odejdete rychleji.\n\nPředaukční společenská doba je stejně důležitá. Poznejte konkurenci. Spřátelte se. Nebo je znervózněte."`,
        options: {
            whats_being_auctioned_today: "Co se dnes draží?",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    twins_lots: {
        text: `„Dnešní položky zahrnují," začíná Hesh a Vellova opožděná ozvěna mění seznam v skandování:\n\n„Sklenice komprimované nostalgie — vzpomínky na místo, které nikdy neexistovalo. Vyvolávací cena 30 zlatých.\n\nJedno Chronobřečkové Ropušátko — prorocký obojživelník, tříminutové okno předvídavosti. Vyvolávací cena 60 zlatých.\n\nSada samoostřících byrokratických brků — samy vyplní správnou odpověď na jakýkoli úřední formulář. Vyvolávací cena 45 zlatých.\n\nMembrána Solopisu — spící symbiontní tkáň uchovaná v minerálním solném roztoku. Vyvolávací cena čeká na ověření.\n\nA hlavní kousek večera: Zkamenělé snové vejce z katedrálních vykopávek. Vyvolávací cena 120 zlatých."\n\nVell konečně dožene a oba dvojčata se usmějí současně. Tato část je přinejmenším dokonale synchronizovaná.`,
        options: {
            tell_me_more_about_the_chronoslurry_toadlet: "Řekněte mi víc o Chronobřečkovém Ropušátku.",
            interesting_selection_ill_look_around_first: "Zajímavý výběr. Nejdřív se rozhlédnu.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    twins_toadlet: {
        text: {
            twins_toadlet_confused: `„Ropušátko, ano," říká Hesh. Vellova ústa se pohybují, ale načasování je špatné — příliš brzy, pak příliš pozdě, pak vynechává celá slova. „Vyvolávací cena je... čtyřicet zlatých." Hesh se krátce zamračí, jako by to číslo překvapilo i je. „Je to... oblíbená položka. Několik zájemců."\n\nJejich obvyklý rytmus je narušený. Cena, kterou uvedli, je nižší než v seznamu — jejich manipulace tempováním nefunguje správně.`,
            twins_toadlet_normal: `„Ach, Ropušátko," říká Hesh s nacvičeným zájmem. Vellovy rty formují slova s teatrální přesností. „Krásný exemplář. Tři minuty dokonalé předvídavosti po jazykovém kontaktu. Velmi oblíbené u byrokratů, gamblerů a chronicky nerozhodných.\n\nVyvolávací cena: 60 zlatých. Ale čekejte konkurenci — máme minimálně dva vážné zájemce. Konečná cena... no." Oba dvojčata se usmějí. „To závisí na sále."`,
        },
        options: {
            who_else_is_bidding_on_it: "Kdo další na něj dráží?",
            ill_be_ready_when_bidding_starts: "Budu připraven, až začne dražba.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    twins_competitors: {
        text: `„Nesdělujeme identity dražitelů před aukcí," říká Hesh. Vell artikuluje spolu, ale jedno oko uhne směrem k vzdálenému rohu místnosti — k Sestře Calyx.\n\n„Nicméně," pokračuje Hesh, „předaukční společenská doba existuje z dobrého důvodu. Pozorujte. Představte se. Vyvozujte si vlastní závěry o tom, kdo chce co.\n\nAukce odměňuje přípravu stejně jako bohatství."`,
        options: {
            understood_ill_mingle: "Rozumím. Půjdu se porozhlédnout.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    twins_echo: {
        text: `„Děláme co?" říká Hesh. Vell artikuluje „Děláme co?" přesně na zpoždění. Podívají se na sebe — Hesh s lehkým úšklebkem, Vell s přízrakem téhož úšklebku o půl sekundy později.\n\n„Vždycky jsme byli takoví," říká Hesh. „Narodili jsme se o půl sekundy od sebe. Žijeme o půl sekundy od sebe. Pravděpodobně zemřeme o půl sekundy od sebe. Není to manýra — je to stav.\n\nTaké to dělá naše aukční tempování nemožným k přerušení. Než zpracujete, co jsem řekl, Vell to už posílil. Velmi účinné pro hnání cen nahoru."`,
        options: {
            thats_honestly_unsettling: "To je... upřímně znepokojivé.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    twins_unsettling: {
        text: `„Děkujeme," řeknou — a poprvé dokonale unisono. Pak se zpoždění obnoví.\n\n„Znepokojení je dobré pro obchod," dodá Hesh. „Nervózní dražitel je štědrý dražitel."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    twins_brain_rot: {
        text: `Sáhnete dovnitř a necháte Thorne-Stillův rozklad prosáknout ven — jemný pulz kognitivního rozkladu zacílený na proslulou synchronizaci dvojčat-licitátorů.\n\nÚčinek je okamžitý. Vellova opožděná ozvěna zakoktá — artikuluje špatná slova, pak ta správná příliš brzy, pak úplně zamrzne. Hesh mluví dál, ale pohlédne stranou, viditelně zneklidněný. Na okamžik jsou to prostě dva lidé stojící vedle sebe. Hypnotický rytmus je zlomený.\n\n„Já... omluvte nás," říká Hesh. Vell artikuluje něco úplně jiného. Stáhnou se za svůj pult, aby se překalibrovali.\n\nAž aukce začne, jejich tempování — a jejich manipulace cenami — bude narušená.`,
    },

    twins_brain_rot_after: {
        text: `Hesh se za pultem narovná, ale škoda je napáchána. Vellova artikulace je teď opožděná o celou sekundu — někdy o dvě. Neviditelný rytmus, který pohání jejich aukční tempování, je nalomený.\n\n„Jsme v pořádku," trvá na svém Hesh. Vell artikuluje „Jsme v pořádku" daleko příliš pozdě, čímž to tvrzení zcela vyvrací.`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    // ——— Sister Calyx ———
    calyx_start: {
        text: {
            calyx_start_return: `„Zase tu," říká Sestra Calyx a upravuje si malou lahvičku u opasku. „Aukce přitahuje všechny druhy. Jsem tu ve věci Reklamátorů jádra — nic víc."`,
            calyx_start_rattled_return: `Sestra Calyx stojí ztuhlá, její sebejistota nalomená. Prohlíží si vás se zjevnou ostražitostí. „Zase vy. Doufám, že jste tu na prohlídku, ne abyste... pokračoval v našem dřívějším rozhovoru."`,
            calyx_start_first: `U aukčních položek stojí vysoká žena ve vrstvených šedozelených hábitech a zkoumá je s klinickou přesností. Houbová vlákna jsou vetkána do jejího roucha jako stříbrné nitě a její prsty končí lehce zbarvenými nehty — znamení dlouhodobé práce s extrakcí jádra.\n\n„Sestra Calyx," řekne, když si všimne vašeho přiblížení. „Reklamátoři jádra. Jsem tu ve věci naší kapituly. A vy jste...?"`,
        },
        options: {
            just_browsing_what_are_the_pith_reclaimers: "Jen se rozhlížím. Co jsou Reklamátoři jádra?",
            what_are_you_bidding_on: "Na co dražíte?",
            im_here_for_the_chronoslurry_toadlet: "Jsem tu kvůli Chronobřečkovému Ropušátku.",
            photosentience_read_her_biosignals: "[Fotosentience] Přečíst její bio-signály.",
            mirage_weave_create_a_distraction: "[Tkaní přeludů] Vytvořit rozptýlení.",
        }
    },

    calyx_pith: {
        text: `„Reklamátoři jádra extrahují houbovou esenci — jádro — z živých organismů. Rafinujeme ji, studujeme, obchodujeme s ní. Direktoriát nám říká ‚paraziti,' Rezavý chór nám říká ‚zloději.' My si říkáme praktičtí.\n\nKaždá živá věc v tomto městě nese sklizitelnou esenci. My prostě... sbíráme, co se už stejně plýtvá. Katedrální vejce, sporová pole, dokonce i živé zdi města — to vše jsou zdroje surového jádra.\n\nNaše kapitula zde v Horní Morkezele je malá, ale dobře financovaná. Proto moje přítomnost na této aukci."`,
        options: {
            what_are_you_bidding_on: "Na co dražíte?",
            essence_extraction_sounds_invasive: "Extrakce esence zní invazivně.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_ethics: {
        text: `„Invazivní?" Upraví si manžetu protkanou houbovými vlákny. „Je invazivní, když dýcháte? S každým nádechem vdechujete spory. My to prostě děláme se záměrem a přesností.\n\nLumen Direktoriát pěstuje věci a předstírá, že jsou přirozené. Rezavý chór nechává věci rozpadat a nazývá to posvátným. My extrahujeme, co je užitečné, a nazýváme to poctivým.\n\nAle nepřišla jsem sem diskutovat o filozofii. Přišla jsem dražit."`,
        options: {
            what_are_you_bidding_on: "Na co dražíte?",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_bidding: {
        text: `„Zkamenělé snové vejce, primárně. Katedrální artefakty nesou koncentrované jádro — dekády nashromážděné esence stlačené do kamene. Naše kapitula by ho mohla studovat roky.\n\nAle sekundárně mě zajímá i Chronobřečkové Ropušátko. Proročtí obojživelníci produkují jedinečný podpis jádra, když se aktivuje jejich předvídavost. Velmi cenné pro náš výzkum temporální extrakce.\n\nMám rozpočet 150 zlatých. Hodlám ho použít strategicky."`,
        options: {
            the_toadlet_is_mine_im_bidding_on_it_too: "Ropušátko je moje. Dražím na něj taky.",
            thats_a_serious_budget: "To je vážný rozpočet.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_toadlet_rival: {
        text: `Přimhouří oči. „Vy chcete Ropušátko? Zajímavé. Není to zrovna neformální nákup — proročtí obojživelníci vyžadují specializovanou péči. Nebo ho jen chcete olíznout a nahlédnout tři minuty dopředu jako všichni ostatní?\n\nNebudu předstírat, že ustoupím. Ale snové vejce je moje priorita — pokud Ropušátko vyletí příliš vysoko, budu si muset vybrat.\n\nLeda byste mě přesvědčili, že Ropušátko nestojí za moje zlaté."`,
        options: {
            what_would_convince_you_to_drop_the_toadlet_bid: "Co by vás přesvědčilo vzdát se dražby Ropušátka?",
            may_the_best_bidder_win: "Ať vyhraje lepší dražitel.",
            brain_rot_confuse_her_about_which_lot_she_wanted: "[Mozkový rozklad] Zmást ji, o kterou položku jí šlo.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_negotiate: {
        text: `„Přesvědčit mě?" Zkříží ruce, houbová vlákna zachytí světlo. „Kapitula mě poslala pro zdroje jádra. Musím se vrátit s něčím, co ospravedlní cestovní náklady.\n\nPokud snové vejce půjde za rozumnou cenu, mohla bych na něj soustředit rozpočet a nechat Ropušátko vám. Ale pokud někdo vyžene vejce příliš vysoko, přeorientuji se na Ropušátko jako sekundární akvizici.\n\nTakže vaše nejlepší strategie je zajistit, abych dostala snové vejce levně. Nedražte na něj. Nenechte nikoho jiného ho zdražovat. A já nechám vašeho obojživelníka na pokoji."`,
        options: {
            so_we_have_an_understanding_i_avoid_the_egg_you_av: "Takže máme dohodu — vyhneme se vejci, vy Ropušátku.",
            no_promises_ill_bid_as_i_see_fit: "Nic neslibuju. Budu dražit, jak uznám za vhodné.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_deal: {
        text: `„Porozumění. Ne dohoda — Reklamátoři jádra neuzavírají dohody s cizími na aukcích. Ale... porozumění. Ano.\n\nSoustředím se na snové vejce. Vy se soustřeďte na Ropušátko. A nikdo z nás nezdražuje cíl toho druhého. Efektivní. Praktické. Velmi reklamátorské z vaší strany."\n\nLehounce přikývne — uznání, ne vřelost.`,
    },

    calyx_no_deal: {
        text: `„Jak chcete. Ale nedivte se, když dražba bude... energická. Reklamátoři jádra neprohrávají aukce, na které mají rozpočet.\n\nKéž jsou vaše kapsy hlubší než vaše tvrdohlavost."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_challenge: {
        text: `„Ať vyhraje lepší dražitel," zopakuje a její úsměv má ostří. „Hodlám. Reklamátoři jádra nechodí na aukce pro zábavu.\n\nAle společenská doba ještě neskončila. Je stále čas být přesvědčivý — nebo dělat chyby."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_budget: {
        text: `„Kapitula nefinancuje polovičatosti. Když identifikujeme zdroj jádra hodný akvizice, získáme ho. 150 zlatých je skromné podle reklamátorských standardů — některé kapituly posílají delegace s desetinásobkem.\n\nAle Horní Morkezela je malá kapitula. Jsme... opatrní s alokacemi. Proto musím dražit strategicky, ne emotivně."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_neme: {
        text: `Necháte Nemino vnímání rozvinout — úponky bio-vědomí dosahující k Sestře Calyx. Její signály rozkvetou do zaostření: disciplína, kalkulace, pečlivě udržovaná fasáda klidu.\n\nAle pod povrchem — úzkost. Je pod tlakem své kapituly. Rozpočet je napjatý, napjatější, než přiznává. A je tu ještě něco: Ropušátko ve skutečnosti nechce pro výzkum jádra. Chce ho pro sebe. Příběh o temporální extrakci je krytí.\n\nNeme šeptá: „Reklamuje od ostatních, co nemůže vypěstovat sama. Ale tentokrát si chce úrodu ponechat."`,
        options: {
            your_chapter_didnt_send_you_for_the_toadlet_did_th: "Vaše kapitula vás pro Ropušátko neposlala, že?",
            keep_this_to_yourself_for_now: "[Nechat si to zatím pro sebe.]",
        }
    },

    calyx_caught: {
        text: `Její klid praskne — jen na okamžik. Ruka se pohne k lahvičce u opasku, pak klesne.\n\n„Jak jste — " Zastaví se. Zhluboka se nadechne. „Máte čtečku. Nějaký bio-senzorický symbiont. Reklamátoři takové studovali."\n\nZtiší hlas. „Dobře. Ropušátko není pro kapitulu. Mám... temporální vertigo. Ztrácím čas. Tři minuty předvídavosti by mi pomohly zakotvit se. Kapitula neví.\n\nMění to něco mezi námi?"`,
        options: {
            it_does_drop_the_toadlet_bid_or_i_tell_the_room: "Mění. Vzdejte se dražby Ropušátka, nebo to řeknu celému sálu.",
            your_secret_is_safe_but_stay_away_from_the_toadlet: "Vaše tajemství je v bezpečí. Ale vyhněte se Ropušátku.",
            i_wont_use_this_against_you_bid_as_you_wish: "Nepoužiji to proti vám. Dražte, jak chcete.",
        }
    },

    calyx_blackmail: {
        text: `Její čelist ztuhne. Houbová vlákna v jejím rouchu jako by ztmavla.\n\n„Odhalil byste zdravotní stav, abyste vyhrál aukci? To je... myšlení Rezavého chóru. Rozklad jako páka."\n\nDlouhý moment mlčí. „Dobře. Ropušátko je vaše. Soustředím se na snové vejce. Ale pamatujte si — Reklamátoři jádra mají dlouhou paměť a velmi specifické metody extrakce.\n\nNedělejte si z naší kapituly nepřítele lehkovážně."`,
    },

    calyx_mercy: {
        text: `Úleva přeběhne jejím obličejem, než se profesionální maska vrátí. „Já... cením si diskrétnosti. Temporální vertigo není něco, k čemu by kapitula přistupovala se soucitem. Odvolali by mě, přeřadili mé povinnosti na někoho ‚temporálně stabilního.'\n\nRopušátko byl stejně dlouhý pokus. Snové vejce je hlavní mise. Na to se soustředím.\n\nDěkuji. To neříkám často."`,
    },

    calyx_respect: {
        text: `Chvíli vás studuje, přehodnocuje. „To je... nečekané. Většina lidí v tomto městě využije každou výhodu, kterou najde.\n\nDobrá. Budu dražit, jak uznám za vhodné, a vy také. Ale vězte, že jsem si všimla vaší zdrženlivosti. Reklamátoři jádra si cení těch, kdo rozumí rozdílu mezi extrakcí a vykořisťováním."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_thorne: {
        text: `Necháte Thorne-Stillův rozklad šeptat ven — cílený pulz kognitivní zmatenosti namířený na Sestru Calyx.\n\nJejí oči se na moment zamlží. Zamrká, dotkne se spánku. „Já... snové vejce. Ne — Ropušátko. Ne, to..." Odmlčí se, její pečlivě připravená dražební strategie se rozpouští v mlze.\n\n„Omluvte mě. Potřebuji chvilku." Odstoupí od položek, viditelně zmatená, pro které věci sem vlastně přišla.\n\nJejí dražební priority jsou pomotané. Bude méně efektivní jako konkurentka u jakékoli položky.`,
    },

    calyx_thorne_after: {
        text: `Sestra Calyx stojí mírně stranou od ostatních hostů a masíruje si spánky. Houbová vlákna v jejím rouchu pulzují nepravidelně — i ta jako by byla zmatená.\n\n„Jsem v pořádku," říká nikomu konkrétnímu. „Jen se... přizpůsobuju atmosféře."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    calyx_mirage: {
        text: `Sáhnete po Ulvarexově moci a utkaete jemnou iluzi — fantomového aukčního úředníka přistupujícího k Sestře Calyx s naléhavou zprávou.\n\n„Sestro Calyx? Zpráva z vaší kapituly. Prioritní odvolání — jste potřebná v extrakční laboratoři okamžitě." Iluzorní úředník podá přesvědčivý dopis zapečetěný jádrem.\n\nCalyxin obličej pohasne. „Teď? Ale aukce—" Natáhne ruku po dopise a projde skrz. Iluze se zatřpytí a rozpustí.\n\nZírá na místo, kde úředník stál. Pak na vás. Ví.\n\n„Iluzionista. Jak... kreativní." Její klid vytrvá, ale je otřesená. Pokud dokážete vyčarovat fantomové úředníky, co dalšího může být falešné? Položky? Ostatní dražitelé? Bude zpochybňovat všechno.`,
    },

    calyx_mirage_after: {
        text: `Sestra Calyx stojí u položek, ale už je nezkoumá s klinickou přesností. Její oči neustále skenují místnost — kontrolují, jestli ještě něco dalšího není iluze.\n\n„Šikovný trik," zamumlá, když se přiblížíte. „Ale triky fungují oběma směry. Reklamátoři jádra studují iluze taky, víte. Extrahujeme je."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    // ——— Heartbroker Lune ———
    lune_start: {
        text: {
            lune_start_exposed: `Srdcokupec Lune drží jednu rukavicí krytou ruku nad nejmenším srdcem ve svém skleněném postroji. Tepe mimo rytmus ostatních, teď už střežené.\n\n„Poslouchal jste příliš pozorně," říká. „Neme, že? Nezdvořilý talent. Velmi cenný. Prosím, nemiřte jím na mě znovu, pokud za to nemíníte zaplatit."`,
            lune_start_misled: `Srdcokupec Lune si prohlíží položky s přimhouřenýma očima a její skleněná srdce se barví pochybovačně šedě.\n\n„Emoční provenience je tu... méně spolehlivá, než se tvrdilo," zamumlá. „Někdo osolil místnost falešným kontextem. Velmi otravné. Velmi účinné."`,
            lune_start_return: `„Zase vy," říká Srdcokupec Lune. Modré srdce v jejím postroji zrychlí a na okamžik pocítíte očekávání dřív než ona. Zdvořilým kývnutím si ho vezme zpět.\n\n„Odpusťte. Zvyk."`,
            lune_start_first: `Žena v lakovaných rukavicích stojí pod postrojem z foukaných skleněných komor, z nichž každá drží jiné tlukoucí srdce. Některá jsou rudá a vlhce působící, některá bledá jako vosk ze svíčky, jedno je průsvitné a plné drobných bublinek.\n\n„Srdcokupec Lune," říká. Zatímco mluví, podráždění z vás odteče a nahradí ho cizí mírná nostalgie. Spokojeně se nadechne a vaše podráždění se vrátí.\n\n„Omlouvám se. Obchoduji s pocity konverzačně. Udržuje to vyjednávání upřímné, nebo alespoň zajímavé."`,
        },
        options: {
            what_are_emotionlinked_artifacts: "Co jsou emočně vázané artefakty?",
            what_are_you_bidding_on: "Na co dražíte?",
            did_you_just_trade_my_feelings: "Vy jste právě obchodovala s mými pocity?",
            offer_the_wrong_emotional_context_for_the_lots: "Nabídnout položkám špatný emoční kontext.",
            photosentience_let_neme_expose_what_she_values: "[Fotosentience] Nechat Neme odhalit, čeho si skutečně cení.",
        }
    },

    lune_artifacts: {
        text: `„Předměty si pamatují doteky," říká Lune. Jedno z jejích skleněných srdcí se zakalí jantarovým teplem. „Svatební nůž si pamatuje oddanost. Rozvodová lžíce si pamatuje úlevu. Ztracený knoflík dítěte může nést víc žalu než relikvie z bojiště, pokud to dítě ten kabát milovalo dost."\n\nLehce klepne na postroj. „Páruji artefakty se srdci, která je dokážou strávit. Správné spojení vytváří vzácné pocity. Lahvovanou odvahu. Jedlé výčitky. Nostalgii dost ostrou na krájení ovoce."`,
        options: {
            what_are_you_bidding_on: "Na co dražíte?",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    lune_bidding: {
        text: `„Komprimovanou nostalgii, samozřejmě. Celá sklenice stesku po domově, který nikdy neexistoval? Lahodné. Snové vejce možná, pokud nese dost katedrální hrůzy. Solopis také, i když je to méně artefakt než vlhký archiv čekající na tělo. Dokonce i Ropušátko mě trochu zajímá — předvídavost má chuť paniky, když ji používají zbabělci."\n\nMalé zelené srdce v jejím postroji začne bít rychleji. Náhle cítíte majetnické vzrušení, pak vám zmizí z hrudi a usadí se za jejími žebry.\n\n„Nekoupím všechno. Jen to, co zpívá ve správné emoční tónině."`,
        options: {
            what_makes_an_emotional_key_correct: "Co dělá emoční tóninu správnou?",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    lune_trade: {
        text: `„Krátce," říká Lune. „Ochutnala jsem podráždění, půjčila vám nostalgii a obojí vrátila s minimem pohmoždění. Dokonale zdvořilé."\n\nUpraví ventil na postroji. „Většina lidí lže slovy a přiznává se pocity. Dávám přednost čistšímu dokumentu."\n\nNa půl sekundy pocítíte její nudu: starou, vyleštěnou, drahou. Pak si ji vezme zpět.`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    lune_wrong_context: {
        text: `Nakloníte se blíž a nabídnete sebejistou lež: Snové vejce vůbec není nasáklé hrůzou. Aukční personál ho špatně označil. Jeho dominantním kontextem je byrokratické uspokojení — schválené formuláře, srovnané kartotéky, každé razítko dopadající přesně na místo.\n\nLune lehce ucukne. Tři srdce v jejím postroji zpomalí do zklamaného plazení.\n\n„Administrativní obsah? V katedrálním kameni? Jak vulgární." Znovu se podívá k položkám a přepočítává. „Budu muset ověřit všechno. Pomalu. S podezřením."\n\nJejí jistota je otrávena. Bude méně rozhodná dražitelka.`,
    },

    lune_neme: {
        text: `Necháte Neminu fotosentienci otevřít se jako tiché zelené oko. Lunin postroj se promění v zahradu vypůjčených tepů: chuť, marnivost, profesionální potěšení. Ale pod nimi sedí maličké nezapálené srdce, které nikdy nenechá dotknout se vzduchu.\n\nNeme šeptá: „Necení si silných pocitů. Cení si prázdna po nich. Čisté dutiny. Ticha tam, kde kdysi bývalo chtění."\n\nLunin úsměv ztuhne. „Tohle," řekne tiše, „nebylo k obchodu."`,
        options: {
            then_these_lots_are_too_noisy_for_you: "Pak jsou pro vás tyhle položky příliš hlučné.",
            ill_keep_your_secret_for_now: "Nechám si vaše tajemství zatím pro sebe.",
        }
    },

    lune_exposed: {
        text: `Poprvé si žádné z Luniných srdcí nevymění místo s ničím jiným. Prostě bijí, odhalená a nesynchronizovaná.\n\n„Příliš hlučné," zopakuje. „Ano. Možná jsou."\n\nOdstoupí od výstavní stěny. „Přišla jsem lovit delikatesy a našla místnost plnou křičícího masa. Dražte si, jak chcete. Potřebuji tišší zboží."`,
    },

    lune_secret: {
        text: `„Jak velkorysé," říká Lune příliš rychle. Fialové srdce v jejím postroji se pokusí nabídnout vděčnost; zavře ventil dřív, než k vám dorazí.\n\n„Nechte si ho tedy. Tajemství nabývají úrok. Pokud tohle později utratíte, utraťte ho elegantně."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    // ——— Heir to the Yellow Aquarium ———
    heir_start: {
        text: {
            heir_start_disrupted: `Dědic Žlutého akvária stojí naprosto nehybně, ale rybí embrya unášená v jeho průsvitném trupu se už nepohybují v ladných hejnech. Jemně do sebe narážejí, vyplašená proudy, které neexistují.\n\nPod jeho kůží pulzuje slabé žluté světlo: otázka, bolest, rekalibrace. Když promluvíte, nedívá se na vaše ústa. Sleduje vibraci, která vám prochází hrdlem.`,
            heir_start_return: `Dědic se k vám otočí dřív, než promluvíte, reaguje na drobné zachvění vašich kroků. Rybí embrya v jeho hrudi se vznášejí v pomalých synchronizovaných spirálách.\n\nZvedne jednu ruku k nejbližší lampě. Světlo projde jeho prsty a embrya odpoví tím, že se všechna naráz otočí.`,
            heir_start_first: `U výstavní stěny stojí vysoký průsvitný humanoid, jehož tělo je naplněné pomalu se vznášejícími rybími embryi zavěšenými ve žluté tekutině. Embrya se otáčejí v hejnech, když se někdo zasměje příliš hlasitě, a rozprchnou se, když aukční lampy zablikají.\n\nNa štítku na jeho límci stojí: Dědic Žlutého akvária.\n\nKdyž ho pozdravíte, nereaguje. Ale jakmile váš hlas zavibruje podlahovými prkny, každé embryo v něm se k vám otočí.`,
        },
        options: {
            what_are_you_looking_for: "Co hledáte?",
            can_you_understand_me: "Rozumíte mi?",
            why_living_artifacts_and_symbionts: "Proč živé artefakty a symbionty?",
            brain_rot_disrupt_the_embryo_synchronization: "[Mozkový rozklad] Narušit synchronizaci embryí.",
        }
    },

    heir_wants: {
        text: `Embrya se otočí k výstavní stěně dřív než Dědic. Žlutou tekutinou v jeho těle projde vlnka.\n\n„Živé kusy," řekne konečně Dědic. Jeho hlas je tichý, ale lampy souhlasně zabzučí. „Artefakty, které ještě odpovídají. Symbionty, kteří si pamatují, že nejsou dokončení. Mrtvé poklady klesají. Živé poklady plavou."\n\nJeho pozornost ulpí na membráně Solopisu, pak na Ropušátku, pak na Snovém vejci. Každý pohled působí méně jako touha a víc jako přílivové rozpoznání.`,
        options: {
            can_you_understand_me: "Rozumíte mi?",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    heir_communication: {
        text: `Ptáte se opatrně. Dědic neodpoví, dokud nezabliká visící lampa. Pak se embrya v něm uspořádají do volné spirály a jeho hlava se nakloní, jako by poslouchal skrz vodu.\n\n„Řeč je povrchové rušení," řekne. „Vibrace má hloubku. Světlo má záměr. Slova jsou užitečná jen tehdy, když se správně chvějí."\n\nPoklepe dvěma prsty na límec. Skleněný tón projde podlahovými prkny a embrya se postupně rozzáří. Souhlas, možná. Nebo interpunkce.`,
        options: {
            what_are_you_looking_for: "Co hledáte?",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    heir_living_artifacts: {
        text: `„Žluté akvárium dědí jen to, co se ještě dokáže měnit," říká Dědic. „Živý artefakt vyjednává se svým nositelem. Symbiont upravuje tělo, které ho chrání. I prorocký obojživelník je malá smlouva mezi hladem a časem."\n\nEmbrya v něm se shromáždí u žeber, všechna obrácená ven.\n\n„Statické relikvie jsou pro suché domy. My sbíráme pokračování."`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    heir_brain_rot: {
        text: `Necháte Thorne-Stilla vydechnout kognitivní rozklad do vibrací kolem Dědice. Nezasáhne Dědicovu mysl přímo. Vstoupí rytmem. Podlahou. Drobounkými synchronizovanými obraty embryí zavěšených uvnitř něj.\n\nHejno se rozpadne. Embrya se rozprchnou všemi směry a měkce narážejí do průsvitných žeber. Dědic ztuhne. Jeho žluté světlo bliká mimo pořadí.\n\n„Příliš mnoho proudů," zašeptá. „Příliš mnoho úst ve vodě."\n\nOdstoupí od výstavní stěny a snaží se obnovit vnitřní vzorec, který vedl jeho dražební instinkty.`,
    },

    // ——— The Silence Beneath the Stairwell ———
    silence_start: {
        text: {
            silence_start_after_neme: `Malé temné stvoření se přesunulo ještě blíž ke zdi. Pod kapucovitým stínem není vidět téměř žádná tvář — jen náznak úst, která zapomněla svůj účel.\n\nKdyž se přiblížíte, zvedne dva prsty, jeden sklopí a pak ukáže k podlaze pod vašima nohama. Neme se neklidně zachvěje. Ani teď se gesto odmítá proměnit ve význam.`,
            silence_start_return: `Ticho pod schodištěm vás vezme na vědomí, aniž vzhlédne. Z rukávu se vysunou tři prsty, zastaví se a zase zmizí.\n\nNenásleduje žádný zvuk. Ta nepřítomnost působí záměrně, tvarovaně, téměř gramaticky.`,
            silence_start_first: `Tam, kde stín aukční síně u stěny houstne, dřepí malé temné stvoření. Nemá téměř žádnou viditelnou tvář — jen měkké přerušení tmy tam, kde by měly být rysy.\n\nNa kartičce vedle něj stojí: Ticho pod schodištěm.\n\nNepozdraví vás. Zvedne úzkou ruku a signalizuje dvěma prsty, pak pěti, pak žádným. Kdesi poblíž uprostřed věty umře rozhovor.`,
        },
        options: {
            what_are_you_bidding_on: "Na co dražíte?",
            why_dont_you_speak: "Proč nemluvíte?",
            what_do_those_finger_signals_mean: "Co znamenají ta prstová znamení?",
            photosentience_ask_neme_to_interpret_the_silence: "[Fotosentience] Požádat Neme, aby vyložila ticho.",
        }
    },

    silence_bidding: {
        text: `Zeptáte se, co chce. Stvoření zvedne jeden prst směrem ke sklenici Komprimované nostalgie a pak ho ohne dovnitř, až kloub téměř zmizí. Takže ne nostalgii. Něco uzavřeného uvnitř ní.\n\nPotom ukáže na Snové vejce, ale jen ve chvíli, kdy se nikdo jiný nedívá. Nakonec dvakrát klepne do podlahy, pomalu a dutě.\n\nVýznam dorazí spíš jako tlak než řeč: předměty, které uchovávaly tajemství. Předměty, které byly samy dost dlouho na to, aby se v samotě staly plynulými.`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    silence_no_speech: {
        text: `Stvoření k vám otočí svou skoro-tvář. Z rukávu se vysune ruka a sevře palec s ukazovákem k sobě tak, že mezi nimi nezůstane žádný prostor.\n\nPak tytéž prsty pootevře o zlomek. Místnost uvnitř té nepatrné mezery jako by zesílila.\n\nNikdy nedraží slovně, protože řeč by utratila to, co se snaží koupit. Ticho není jeho odmítnutí. Ticho je jeho měna.`,
        options: {
            what_are_you_bidding_on: "Na co dražíte?",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    silence_signals: {
        text: `Zopakuje sekvenci pomaleji: dva prsty, pět, žádný. Pak jeden prst přitisknutý k místu, kde by mohla být ústa. Pak všechny prsty skryté.\n\nChápete jen okraje. Počet. Nepřítomnost. Svědek. Odmítnutí.\n\nNa druhé straně sálu si Hesh a Vell nevšimnou, že byl učiněn příhoz. Možná právě o to jde.`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },

    silence_neme: {
        text: `Necháte Neme sáhnout ke stvoření a hledat bio-signály pod tichem. Pro jednou růstový smysl zaváhá. Život tam je, ale skládá se před výkladem jako kapradina zavírající se v noci.\n\nNeme šeptá: „Cítím ukrývání, ale ne to, co je ukryté. Hlad, ale ne jeho předmět. Osamělost, ale ne zda je bolestí, nebo volbou."\n\nStvoření zvedne jediný prst. Neme ztichne dřív, než gesto dokončí.\n\nAť chce cokoli, dokázalo učinit i samotné chtění těžko čitelným.`,
        options: {
            so_even_neme_cant_read_you_clearly: "Takže ani Neme vás nedokáže jasně přečíst.",
            i_have_other_questions: "Mám další otázky.",
        }
    },

    silence_neme_after: {
        text: `Ramena stvoření se jednou zvednou a klesnou. Možná smích. Možná souhlas.\n\nNatáhne dva prsty a pak je skryje v rukávu. Příhoz, možná. Nebo varování. Nebo nejmenší možný potlesk.`,
        options: {
            i_have_other_questions: "Mám další otázky.",
        }
    },
};
