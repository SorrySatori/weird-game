/**
 * Czech dialog translations for SkyshipBoardScene
 * Speaker: Captain Liris (Kapitánka Liris)
 */
// Liris's topics: the first greeting, the re-greeting and the hub offer the same ones
const lirisTopics = {
    how_does_this_ship_fly: "Jak tahle loď létá?",
    where_are_you_headed: "Kam míříte?",
    tell_me_about_yourself: "Řekněte mi o sobě.",
    is_flying_dangerous: "Je létání nebezpečné?",
    what_cargo_do_you_carry: "Jaký náklad vezete?",
    i_need_help_with_an_elevator_system: "Potřebuji pomoc s výtahovým systémem."
};

export default {
    _speakers: {
        'Captain Liris': 'Kapitánka Liris',
        'Narrator': 'Vypravěč',
    },
    main: {
        text: "Ocitáš se na palubě vzdušné lodi. Vzduch je tu nahoře řídký a dole vidíš rozprostřené město.",
        options: {
            look_around: "Rozhlédnout se"
        }
    },
    lookAround: {
        text: "Vzdušná loď vypadá jako transportní plavidlo. Podivné rostliny lemují okraje paluby a slouží zjevně jako dekorace i konstrukční podpora. Loď se jemně kolébá ve větru.",
        options: {
            other_topics: "Zeptej se na něco jiného"
        }
    },
    captainMain: {
        text: "Ach, návštěvník! Vítejte na palubě Verdigrace. Jsem kapitánka Liris, navigátorka vzdušnými proudy a velitelka tohoto krásného plavidla. Co vás přivádí na mou loď?",
        options: lirisTopics
    },
    captainAgain: {
        text: "Zase vy? Tak se ptejte.",
        options: lirisTopics
    },
    captainHub: {
        text: "*Liris olízne prst a zkontroluje vítr.* Ještě něco byste chtěl vědět?",
        options: lirisTopics
    },
    captainAbout: {
        text: "Jsem kapitánka Liris, velitelka tohoto plavidla, jak jsem řekla. Jsem na misi pro Direktorát, jako obvykle.",
        options: {
            what_is_the_lumen_directorate: "Co je Direktorát?",
            other_topics: "Zeptej se na něco jiného",
        }
    },
    captainAccord: {
        text: "Direktorát je mocná organizace, víte? Usilujeme o splynutí mysli a flóry. Jsme strážci a ochránci všeho, co roste. Jsme ochránci života.",
        options: {
            other_topics: "Zeptej se na něco jiného",
            what_is_you_mission: "Jaká je vaše mise?",
            does_lumen_directorate_have_some_enemies: "Má Direktorát nějaké nepřátele?"
        }
    },
    captainMission: {
        text: "Naše mise má za cíl hledat a sbírat vzácné exempláře pro Direktorát. Ale pořád čekáme na další rozkazy, takže se nikam nehneme a ten váš žebříček nám nevadí.",
        options: {
            other_topics: "Zeptej se na něco jiného"
        }
    },
    captainEnemies: {
        text: "Jistě, máme nějaké nepřátele, jako každý. Zvláště tu verbež z Rezavého chóru, ale to vás asi nepřekvapí.",
        options: {
            other_topics: "Zeptej se na něco jiného"
        }
    },
    captainTechnology: {
        text: "Fascinující, že? Trup lodi je prosycen speciálním kmenem levitačních rostlin. Vytvářejí mikroskopické plynové kapsy, které nám dávají vztlak. Organické plachty zachycují vzdušné proudy a řídicí houby reagují na mé příkazy prostřednictvím symbiotického pouta. Jsem s touto lodí spojená už přes dvacet let.",
        options: {
            that_sounds_dangerous: "To zní nebezpečně.",
            ask_something_else: "Zeptej se na něco jiného"
        }
    },
    captainDanger: {
        text: "Ha! Život bez rizika není žádný život. Ano, jsou tu nebezpečí: bouřkové stromy, které by nás mohly pohltit, dravé létající ostružiny, které loví ve výšinách, a další hrůzy. Ale svoboda oblohy... ta stojí za jakékoliv riziko.",
        options: {
            other_topics: "Zeptej se na něco jiného"
        }
    },
    captainDestination: {
        text: "Sledujeme pravidelné pampeliškové proudy, které krouží nad kontinentem. Příští zastávka jsou Visuté zahrady Mycory, kde vyměníme zboží za vzácné exempláře rostlin. Poté možná plovoucí výzkumné stanice Východního baldachýnu. Větry rozhodují o naší konečné trase.",
        options: {
            could_i_travel_with_you: "Mohl bych cestovat s vámi?",
            ask_something_else: "Zeptej se na něco jiného"
        }
    },
    captainTravel: {
        text: "Možná jednou, příteli. Ale ne na této cestě. Loď si... vybrala svou posádku. Cítím, že ještě není připravena se s vámi spojit. Vraťte se, až prokážete svou hodnotu. Verdigrace je obzvláště vybíravá ohledně toho, koho přijme. Pokud to myslíte vážně, navštivte ústředí Direktorátu ve městě a zeptejte se na vstup do posádky. Mohli by pro vás mít nějaké úkoly, abyste prokázal svou oddanost.",
        options: {
            where_can_i_find_the_lumen_directorate_headquarter: "Kde najdu ústředí Direktorátu?",
            other_topics: "Zeptej se na něco jiného"
        }
    },
    captainDirectorate: {
        text: "Ústředí Direktorátu se nachází v srdci města, poblíž hlavního náměstí. Je to pořádná budova, nemůžete ji minout.",
        options: {
            thank_you_i_have_some_other_questions: "Děkuji! Mám ještě další otázky."
        }
    },
    captainDirectorateDemo: {
        text: "*Liris zaváhá a ztiší hlas.* „Než se tam vydáte, raději vás varuju: tentokrát se tam nedostanete. Hlavní náměstí, Direktorát a půlka města za ním: nic z toho ještě není otevřené. Demo, říkají téhle verzi města přístavní dělníci. Do čtvrti, kterou ještě nikdo nepostavil, vás nedovezu.“ *Poklepe na zábradlí.* „Ale ten nápad si nechte. Až se zbytek města otevře, Direktorát tam bude. A Verdigrace taky.“",
        options: {
            ill_remember_that: "Zapamatuju si to."
        }
    },
    captainCargo: {
        text: "Především vzácné spory a mycélia, která nelze pěstovat ve městě. Specializované symbiotické kmeny, krystalizované růstové enzymy, rozkladu odolné stavební materiály. Převážíme také zprávy mezi rozptýlenými vzdušnými koloniemi a výzkumnými stanicemi. Informace jsou možná náš nejcennější náklad: znalosti, které by se jinak nikdy nedostaly na zem.",
        options: {
            do_you_have_anything_to_trade: "Máte něco na výměnu?",
            ask_something_else: "Zeptej se na něco jiného"
        }
    },
    captainTrade: {
        text: "Pro vás bohužel ne. Každá bedna v podpalubí už je slíbená Direktorátu nebo koloniím. Vraťte se, až obletíme svůj okruh, a možná pro tak odvážného průzkumníka, jako jste vy, budu mít něco jedinečného. Sledujte oblohu.",
        options: {
            other_topics: "Zeptej se na něco jiného"
        }
    },
    captainElevator: {
        text: "Výtahový systém, říkáte? Ach, to asi myslíte jeden z těch starých vertikálních transportních mechanismů ve městských věžích. Tyhle staré systémy jsou fascinující. Je to směs mechanického inženýrství a rané symbiotické technologie. O jaký problém se jedná?",
        options: {
            the_floor_counter_is_broken: "Počítadlo pater je rozbité.",
            never_mind_ask_something_else: "To nic, zeptám se na něco jiného."
        }
    },
    captainFloorCounter: {
        text: "Porucha počítadla pater? To je běžný problém výtahových systémů. Číselné displeje byly navrženy pro jednoduché úkoly jako jezdit nahoru a dolů, ale inženýři nepočítali s vnímajícími výtahy. Náhodou mám speciální kalibrační nástroj přesně pro takové problémy, který jsem vyvinula během údržby vzdušných dokovacích výtahů.",
        options: {
            could_i_borrow_this_tool: "Mohl bych si ten nástroj půjčit?",
            how_does_it_work: "Jak to funguje?"
        }
    },
    captainToolExplanation: {
        text: "Je to symbiotické rozhraní, které propojuje starou elektroniku s myslí, která výtahu narostla až mnohem později. Uvnitř žije kmen komunikačních mikrodronů, kteří překládají mezi digitálními signály a mozkovými impulzy. Stačí ho připojit k servisnímu portu počítadla a znovu propojí mechanické součásti s živými nervy budovy.",
        options: {
            could_i_borrow_this_tool: "Mohl bych si ten nástroj půjčit?",
            ask_something_else: "Zeptej se na něco jiného"
        }
    },
    captainGivesTool: {
        text: "Samozřejmě! Vždycky s sebou nosím zálohy. Nikdy nevíte, kdy budete potřebovat něco opravit uprostřed letu. Tady, vezměte si tento kalibrační modul. Je jednoduchý na použití: stačí ho připojit k servisnímu panelu výtahového systému a automaticky překalibruje počítadlo pater. Droni uvnitř udělají veškerou práci.",
        options: {
            thank_you: "Děkuji!"
        }
    },
    closeDialog: {
        text: ""
    }
};
