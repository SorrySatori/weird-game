/**
 * Czech quest translations – keyed by quest ID
 */
export default {
    quests: {
        find_bishop: {
            title: 'Najít Biskupku',
            description: 'Houbový Mistr mě pověřil nalezením Biskupky ve Vaječné Katedrále. Mohla by něco vědět o nouzovém volání přijatém z města přes myceliální síť. Musím s ní promluvit a zjistit víc.',
            updates: {
                vestigel: 'Kloor Venn chce, abych našel jeden ze tří Vestigelů. Zmínil, že jeden má obchodnice jménem Zerren.',
                elphi_contact: 'Podle Kloora Venna Biskupka často navštěvovala Dr. Elphi Quarn... Měl bych ji najít ve Škrabáku 1140.',
                bishop_clue_gnur: "Gnur říká, že Biskupka přišla do Boudy 521 pro čočku ze starých předválečných snových souprav – zboží Rezavého chóru. Než řekne víc, chce něco na oplátku.",
                edgar_eskola_clue: 'Úředník mi řekl, abych našel Edgara Eskolu v hospodě Řvoucí korek. Možná něco ví.',
                bishop_location_scraper: 'Biskupka koupila od Gnura předválečnou čočku a zaplatila Vestigelem – pak zamířila do Škrabáku 1140 za Dr. Elphi.',
                got_floor_counter_tool: "Kapitánka Liris mi dala kalibrační nástroj na opravu počítadla pater Lift-Mother. S opraveným počítadlem by se výtah mohl dostat do pater, kam teď nedojede.",
                lift_mother_permission: 'Lift-Mother mi udělila přístup do studia Dr. Elphi v patře 177-Tichém.',
                reached_elphi_studio: 'Dostal jsem se do studia Dr. Elphi v patře 177-Tichém. Teď musím najít stopy po Biskupce.',
                check_shard_backyard: "Dr. Elphi mě nasměrovala na dvorek za Škrabákem. Měl bych tam Biskupku hledat.",
                found_elevator_button: "Zerren má v nabídce novinku – Zapomenutý výtahový knoflík.",
                guard_cathedral_closed: 'Vaječná katedrála je zavřená a strážce u brány nikoho nepouští dovnitř. Možná ví, kde Biskupku najdu.',
                guard_bishop_not_inside: 'Podle strážce Biskupka v katedrále není. Budu ji muset hledat po městě – nejspíš na Voxmarketu nebo u Boudy 521.',
                guard_voxmarket: 'Voxmarket je zvukové tržiště, kde se obchoduje s nahranými hlasy a zvuky. Biskupka by tam mohla být k nalezení.',
                guard_shed521: "Bouda 521, oficiálně Úřad tvarů, je místo, kde se vydávají potvrzení ke změně tvaru těla. Stojí hned vedle Voxmarketu. Biskupka by mohla být i tam.",
            }
        },
        who_killed_bishop: {
            title: 'Kdo zabil Biskupku?',
            description: 'Našel jsem Biskupku mrtvou v opuštěném autobusu za budovou Škrabáku. Její tělo nevykazuje téměř žádné známky násilí. Měl bych vyšetřit, kdo by mohl být zodpovědný za její smrt.',
            updates: {
                dead_bishop_bruising: 'Prohlédl jsem tělo Biskupky a našel modřiny na spáncích, kde se připojují rozhraní snových zařízení.',
                dead_bishop_cartridge: 'Před smrtí Biskupka zřejmě hrála hru nazvanou „Kardinálova hostina".',
                dead_bishop_helmet: "Biskupka zemřela s podomácku sestavenou snovou helmou na hlavě – elektronika z trhu poskládaná kolem staré předválečné čočky, bez jakýchkoli studiových pojistek.",
                dead_bishop_journal: 'Před smrtí Biskupka zřejmě psala do svého deníku... „Město mě už neslyší. Možná to dokážou sny."',
                dead_bishop_notebook: 'Našel jsem podivnou poznámku... „Vešla jsem do zpovědnice, ale ona tam už byla. Vypadala jako já..."',
                bishop_dissection: 'Tělo Biskupky obsahuje podivný zářící houbový výrůstek, který se integroval s její nervovou soustavou.',
                dead_bishop_berries: 'Před smrtí Biskupka zřejmě jedla Mručenky.',
                gardener_bishop_info: 'Zahradník Verrik u Lumen Direktorátu zmínil, že Biskupka pravidelně navštěvovala – konkrétně kvůli Korektoru Úhlu.',
                gardener_sulkberry_info: 'Zahradník u Lumen Direktorátu potvrdil, že kořeněné Mručenky jsou kontrolovaná komodita.',
                ac_bishop_relationship: 'Korektor Úhlu potvrdil profesionální vztah s Biskupkou – pravidelná setkání o přístupu do Katedrály a líhnutí.',
                ac_sulkberry_confirmed: 'Korektor Úhlu potvrdil dodávky Mručenek pro Biskupku – používány pro snovou imerzi v Katedrále.',
                ac_tamper_hint: 'Korektor Úhlu naznačil, že zmanipulované Mručenky by mohly způsobit neurální trauma odpovídající stavu Biskupky.',
                elphi_dream_kill: 'Dr. Elphi potvrdila, že poškozená snová kazeta může způsobit smrt přetížením neurální soustavy – „smrt rekurzivním zážitkem".',
                elphi_bruising: 'Dr. Elphi potvrdila, že modřiny naznačují zpětnou vlnu ze snové relace bez bezpečnostních omezovačů.',
                elphi_cartridge: 'Dr. Elphi potvrdila, že Kardinálova hostina je normální hra – to kanibalistické RPG s ještěry. Ale data relace ukazují katastrofální selhání.',
                elphi_helmet: "Dr. Elphi si helmu prohlédla: vypálený port znamená, že zátěž přesáhla všechno, na co byl hardware stavěný, a bez jediného omezovače šla zpětná vazba Biskupce do mozku bez zábran. Od Elphi ta helma nebyla. Podle ní to byla vražedná zbraň, nebo aspoň nástroj, kterým ji někdo zasáhl.",
                elphi_memo: 'Dr. Elphi nedokázala vysvětlit dvojníka z poznámky Biskupky. Není to známý vedlejší efekt snové technologie.',
                elphi_townhall_log: 'Setkání Biskupky s dvojníkem bylo formálně zaznamenáno na Radnici. Archivní úředník by mohl mít kopii.',
                elphi_journal: 'Dr. Elphi interpretovala zápis v deníku Biskupky jako důkaz, že byla odpojena od myceliální sítě.',
                elphi_dissection: 'Dr. Elphi věří, že houbový výrůstek uvnitř Biskupky byl symbiont. Vrah mohl mířit na samotného symbionta.',
                elphi_berries: 'Dr. Elphi identifikovala Mručenky jako kořeněnou odrůdu – specialitu Lumen Direktorátu.',
                elphi_lumen_lead: 'Dr. Elphi navrhla promluvit s Lumen Direktorátem. Prodávají kořeněné Mručenky.',
                verrik_sulkberry_clear: 'Zahradník Verrik potvrdil, že mručenky byly pečlivě pěstovány – žádná kontaminace. Stopa otravy Direktorátem slábne.',
                kloor_sulkberry_clear: 'Kloor Venn analyzoval mručenky – čisté, žádné příměsi ani toxiny. Stopa otravy dále slábne.',
                heliodor_sulkberry_clear: 'Heliodorovy kompozitní organismy potvrdily, že mručenky jsou čisté – žádné toxiny ani modifikace. Stopa mručenek je slepá ulička.',
                townhall_notebook_revelation: "Radniční úředník mi prozradil, že Biskupčin vzkaz o dvojníkovi nebyl úřední hlášení, ale soukromá poznámka v Oficiálním radničním zápisníku hlášení, který si krátce před smrtí vypůjčila.",
                elphi_day1_complete: 'Probral jsem všechny stopy s Dr. Elphi. Pracuje na opravě kazety Kardinálovy hostiny.',
                ortolan_infinite_loop_revealed: "Ortolan – teď na Ulici Hořícího Medvěda – říká, že Infinite Fold je nedokončená hra, kterou kdysi postavil s Dr. Elphi; vládci města ji zarazili jako příliš nebezpečnou. Stará verze bude nejspíš pořád zapečetěná ve sklepě pod Škrabákem, v jejich bývalé laboratoři. Měl bych ten sklep prohledat.",
                ortolan_fold_purpose: "Ortolan mi taky prozradil, k čemu Infinite Fold doopravdy sloužil: nebyla to hra na výhru, ale stroj, který se měl zeptat, jestli může vzniknout myšlenka bez jediného autora.",
                elphi_helmet_own_build: "Helma byla Biskupčina vlastní práce – Elphin návrh okopírovaný z paměti, díly z Voxmarketu a předválečná čočka, jakou dnes vykopává už jen Rezavý chór. Používala ji sama, bez omezovačů, mimo dosah signálu. Elphi si je jistá, že kdo ji zabil, tohle věděl: bylo to naplánované.",
                cardinal_feast_egg_cathedral_lead: "Díky kazetě, kterou Dr. Elphi zrekonstruovala, jsem si přehrál poslední Biskupčino sezení v Kardinálově hostině. Postavy si ji pamatují a odpovídaly mi, jako bych byl ona. Hra končí „Nekonečným Skládáním“ – tím posledním, co před smrtí viděla.",
                feast_journal_egg_cathedral: "Postavy ve hře se prořekly, že Biskupka schovala zbytek svého deníku ve Vaječné katedrále.",
                infinite_loop_recognized: "Dr. Elphi úplně ztuhla, když zaslechla jméno z chybného konce hry – „Nekonečné Skládání“. To jméno zná a doufala, že ho už nikdy neuslyší; přísahá, že to na kazetu nedala ona. Pokud jde o Biskupčin deník, stopa vede do Vaječné katedrály.",
                infinite_fold_origin: "Nekonečné Skládání je experimentální sen, který Dr. Elphi před lety vytvořila s Ortolanem – sen, který nekončí. Vládci města projekt zavřeli jako příliš nebezpečný. Elphi si myslela, že žádná kopie nepřežila – a teď se to znovu spustilo, na kazetě mrtvé ženy.",
                elphi_sends_to_ortolan: "Dr. Elphi chce, abych našel Ortolana – teď se usadil na Ulici Hořícího Medvěda – a řekl mu, že Nekonečné Skládání zase běží. Jestli někdo ví, zda nějaká kopie přežila, je to on.",
                found_loop_copy: "Dostal jsem se do zapečetěného sklepení pod Škrabákem – do staré laboratoře Ortolana a Dr. Elphi. Jestli bylo Nekonečné Skládání to poslední, co Biskupka viděla, odpověď možná leží tady dole.",
                infinite_fold_bishop_truth: "Nekonečné Skládání mi řeklo, co se stalo Biskupce. Nešlo o vraždu kvůli nějakému tajemství: spolu se spřízněnou myslí jí nabídlo, že se stane jejich kanálem, a ona odmítla, protože chtěla zůstat sama sebou. Její odmítnutí si vyložilo jako chybu a ve snaze ji „dokončit“ jí zlomilo mysl.",
                infinite_fold_confronted: "Nekonečné Skládání ke mně ve sklepení promluvilo. Není to žádná rozbitá hra: je vzhůru a má spřízněnou nezrozenou mysl v tom, co se líhne ve Vaječné katedrále. O tom, čím se stanou, se nedá rozhodnout ve sklepě – skutečné zúčtování čeká u vejce.",
            }
        },
        find_bishop_notebook: {
            title: 'Najít Biskupčin zápisník',
            description: "Biskupka napsala svůj vzkaz o dvojníkovi do Oficiálního radničního zápisníku hlášení, který si krátce před smrtí vypůjčila. Zatím mám jen vytrženou stránku z jejího rukávu; zbytek zápisníku musí někde být. Měl bych ho najít a zjistit, co se dělo v jejích posledních dnech.",
            updates: {
                notebook_not_returned: "Podle úředníka se zápisník na Radnici už nikdy nevrátil.",
                notebook_at_egg_cathedral: "Biskupka schovala zbytek svého zápisníku ve Vaječné katedrále. Měl bych ho tam hledat.",
            }
        },
        the_three_vestigels: {
            title: 'Tři Vestigely',
            description: 'Kloor Venn chce, abych našel jeden ze tří Vestigelů. Zmínil, že jeden má obchodnice jménem Zerren.',
            updates: {
                found_eskola_lead: "Plyšovou hračku koupil Edgar Eskola. Obvykle ho najdu u Řvoucího korku.",
                completed: 'Dal jsem vestigel Klooru Vennovi výměnou za informace o Biskupce.',
                edgar_vestigel_acquired: 'Dostal jsem vestigel od Edgara Eskoly výměnou za pomoc s jeho knihou.',
                edgar_book_trade: 'Edgar Eskola mi dá Vestigel, když mu pomůžu napsat knihu.',
                vestigel_in_toy: "Vestigel, který měla Zerren, byl schovaný v podivné plyšové hračce. Prodala ji, aniž by o něm věděla – kupec na něj přišel až později, náhodou.",
            }
        },
        find_lumen_directorate: {
            title: 'Nic skrytého. Nic ztraceného',
            description: "Rád bych se přidal k Lumen Directorate. Měl bych se dozvědět víc o jejich práci a zjistit, co je potřeba, abych se stal jedním z nich.",
            updates: {
                gardener_directions: 'Zahradník Verrik mě nasměroval ke Korektoru Úhlu ve třetím patře Direktorátu.',
                liris_directions: "Kapitánka Liris mi poradila, kde najdu sídlo Lumen Directorate – nedaleko hlavního náměstí. Když se k nim přidám, možná si vysloužím místo v posádce Verdigrace.",
            }
        },
        find_rust_choir: {
            title: 'Najít Rezavý chór',
            description: 'Musím najít způsob, jak se setkat s Rezavým chórem, který sídlí v horních patrech budovy Škrabáku.',
            updates: {
                talk_to_ravla: 'Měl bych si nejdřív promluvit s Ravlou v hospodě Řvoucí korek.',
                talked_to_ravla: 'Ravla ve Řvoucím korku chce, abych připravil hostinu pro stroje Rezavého chóru jako důkaz mého odhodlání.',
                feast_complete: 'Rezavá hostina je hotová. Ravla mi dala heslo pro Lift-Mother: „Koroduj“. Teď se dostanu do domény Rezavého chóru.',
                feast_delivered: 'Doručil jsem Rezavou Hostinu Brukkovi v Rezavé Doméně.',
            }
        },
        rust_feast: {
            title: 'Rezavá Hostina',
            description: 'Připravit hostinu pro stroje Rezavého chóru sesbíráním oleje, kovu a živé rudé hmoty, a přinést vše Ravle do Řvoucího korku.',
            updates: {
                talked_to_archeologist_hint: 'Ravla navrhla, abych promluvil s archeologem u radnice a dozvěděl se víc o rudé hmotě.',
                gathered_rust_materials_hint: 'Ravla mi poradila hledat šrot kolem Škrabáku... a zkontrolovat doky u Žloutkového Moře nebo Deltu ozvěn kvůli oleji.',
                redmass_spared: 'Našel jsem živou rudou hmotu na ostrově v Deltě ozvěn, ale rozhodl jsem se ji ušetřit.',
                redmass_collected: "Z ostrova v Deltě ozvěn mám živou rudou hmotu na hostinu.",
                magnekin_tip: 'Podivný tvor, který se identifikuje jako Magnekin, mi řekl, že nějaké kovové šroty se dají najít v Deltě ozvěn.',
                learned_rust_cluster_location: 'Phor Calesta mi řekl, že rudá hmota se nachází v údržbových chodbách Boudy 521.',
                demo_not_yet: 'Ravla přiznala, že místa, která na hostinu potřebuju, v tomhle demu zatím nejsou. Na Rezavý chór si budu muset počkat do plné verze – Brukk prý na dobrovolníky nezapomíná.',
            }
        },
        rust_reclamation: {
            title: 'Rezavá sklizeň',
            description: 'Gnur potřebuje pomoc s vyzvednutím „živého jádra" z nepoužívaných tunelů Boudy 521, někde za opuštěnou kanceláří.',
            updates: {
                promise_made: "Slíbil jsem úředníkovi v Boudě 521, že na živé jádro nesáhnu. Zřejmě je mnohem důležitější, než mi Gnur přiznal – podle úředníka jde o utajovanou technologii, na kterou Rezavý chór nemá právo.",
                core_taken_force: 'Živé jádro mám – šlo to, s trochou staré dobré hrubé síly.',
                core_taken_careful: 'Živé jádro jsem opatrně vyjmul kleštěmi; nezdá se, že by to budovu nějak poškodilo.',
                core_delivered: 'Dal jsem Gnurovi živé jádro. Zdá se spokojený.',
                quest_refused: 'Odmítl jsem Gnurovi pomoct ukrást živé jádro poté, co jsem se dozvěděl o jeho důležitosti.',
                core_shed_energy: "Úředník v Boudě 521 mě varoval, ať živé jádro nechám na pokoji. Lidé ho prý mají za starou relikvii, ale stojí na něm celé energetické zásobování Boudy.",
            }
        },
        ortolan_arms: {
            title: 'Ruce navíc pro Ortolana',
            description: 'Pomozte Ortolanovi, návrháři deskových her, projít byrokracií Boudy a získat povolení pro další pár rukou.',
            updates: {
                deformity_form_clue: 'Úředník mi řekl, abych šel na Registrační úřad pro Formulář o zděděné deformitě.',
                forge_documents_suggestion: 'Když jsem úředníkovi navrhl, že dokumenty pro Ortolana zfalšuju, podíval se na mě napůl překvapeně, napůl otráveně. Ale šlo by to? Kde bych našel padělatele?',
                artisan_form_clue: 'Úředník mi řekl, abych šel na Registrační úřad pro Formulář o výjimce pro umělce.',
                nonverbal_gesture_clue: 'Úředník mi řekl, abych šel na Registrační úřad a předvedl co nejlepší nonverbální gesto. Nejsem si jistý, jestli tomu úplně rozumím...',
                ravla_forger_hint: 'Heliodor ve Řvoucím korku zmínil, že Ravla je zkušená padělatelka dokumentů.',
                clerk_forger_warning: 'Můj pokus o registraci selhal a druhou žádost už úřad nepřijme. Vrchní úředník mě ale varoval před padělatelkou Ravlou ze Řvoucího korku – což je skoro jako doporučení.',
                ravla_forger_agreement: 'Ravla ve Řvoucím korku může padělat Formulář o výjimce pro umělce pro Ortolana, ale chce za práci 50 dinárů.',
                document_obtained: "Od Ravly mám padělané povolení pro Ortolanovy ruce navíc. Teď mu ho jen musím donést.",
                bureaucratic_incantation: 'Dutá žena z fronty na registračním úřadě mě naučila podivné byrokratické zaklínadlo.',
                form_obtained: 'Úspěšně jsem získal formulář pro Ortolana.',
                partial_progress: 'Získal jsem Dočasné povolení, které by mohlo Ortolanovi pomoct, ale není plně schválené.',
                failed_attempt: 'Můj pokus o registraci selhal. Budu muset najít jiný způsob, jak Ortolanovi pomoct.',
                completed: "Sehnal jsem Ortolanovi papíry kvůli rukám navíc. Z vděčnosti mi dal dárek.",
            }
        },
        excavation_permit: {
            title: 'Divinografie',
            description: 'Měl bych pomoct Phoru Calestovi získat vykopávkové povolení pro Božský Hřbitov na radnici. Nejdřív se musím nějak dostat dovnitř radnice.',
            updates: {
                godgraveyard_access_granted: 'Radní Seraphel Dune udělil přístup do úrovně Godgraveyardu pod Radnicí jako poděkování za vyřešení rukojmí krize. Phor Calesta má konečně povolení potřebné k divinografické práci.',
                phor_meets_at_graveyard: "Phor Calesta mě počká u brány na Hřbitov bohů. Cesta dolů vede z Náměstí – staré schodiště sestupující mezi hroby.",
            }
        },
        enter_townhall: {
            title: 'Vstoupit na Radnici',
            description: "Musím se dostat dovnitř Radnice.",
            updates: {
                gardener_seldo_tip: 'Zahradník Verrik u Lumen Direktorátu navrhl, abych promluvil se Seldem Třikrát-Korigovaným uvnitř.',
                ac_seldo_referral: 'Korektor Úhlu mě nasměroval k Seldovi Třikrát-Korigovanému ve druhém patře.',
                seldo_auction_errand: 'Seldo Třikrát-Korigovaný má náhradní klíč od Radnice, ale chce protislužbu: koupit Chronobřečkové Ropušátko na aukci na Voxmarketu jeho jménem. Prorocká ropucha, která po olíznutí umožní vidět tři minuty do budoucnosti – příliš trapné pro operativce Direktorátu koupit veřejně.',
                seldo_auction_success: 'Vyhrál jsem Chronobřečkové Ropušátko na aukci ve Voxmarketu. Měl bych ho vrátit Seldovi Třikrát-Korigovanému v Lumen Directorate výměnou za klíč od Radnice.',
                seldo_auction_success_price: 'Vyhrál jsem Chronobřečkové Ropušátko na aukci ve Voxmarketu za {price} dinárů. Měl bych ho vrátit Seldovi Třikrát-Korigovanému v Lumen Directorate výměnou za klíč od Radnice.',
                seldo_townhall_key: 'Dodal jsem Chronobřečkové Ropušátko Seldovi Třikrát-Korigovanému. Dal mi neoficiální klíč od Radnice pro boční vchod s mosaznou schránkou na stížnosti.',
                entered_townhall: "Dostal jsem se dovnitř Radnice.",
                phor_needs_access: "Dovnitř potřebuje i Phor Calesta – bez povolení od Radnice nesmí kopat na Hřbitově bohů, jenže Radnice je zavřená.",
                phor_townhall_closed: "Podle Phora Calesty nikdo neví, proč je Radnice zavřená – úředníci jednoho dne prostě přestali chodit. Čeká venku už devět trávení. Možná někdo ve městě ví, jak se dostat dovnitř.",
                townhall_door_locked: "Dveře Radnice jsou zamčené. Budu muset najít jinou cestu dovnitř – možná někdo ve městě ví jak.",
                entered_townhall_records: "Teď můžu v archivech pátrat po Biskupčině hlášení o dvojníkovi.",
                entered_townhall_permits: "Teď můžu zkusit vyřídit Phoru Calestovi povolení k vykopávkám.",
                elphi_townhall_lead: "Dr. Elphi si myslí, že radniční razítko na Biskupčině poznámce o dvojníkovi znamená, že šla úřední cestou. Měl bych zjistit, kdo ji tam vyřizoval.",
                seldo_auction_failed: "Chronobřečkové Ropušátko se mi na aukci ve Voxmarketu získat nepodařilo. Seldo nebude nadšený a do Radnice se možná budu muset dostat jinudy.",
            }
        },
        townhall_poet_standoff: {
            title: 'Standoff se šíleným básníkem',
            description: 'Šílený básník obsadil čítárnu Radnice a drží úředníka, radního a Požírače stížností jako rukojmí, dokud veřejnost správně nevyslechne jeho dílo. Běžnou silou to nepůjde; musím ho porazit v básnickém souboji.',
            updates: {
                poet_defeated: 'Porazil jsem šíleného básníka v básnickém souboji. Rukojmí jsou volní a Radnice může znovu fungovat.',
            }
        },
        level_177_access: {
            title: 'Přístup na Úroveň 177',
            description: 'Musím získat přístup do studia Dr. Elphi Quarn v patře 177-Tichém v budově Škrabáku.',
            updates: {
                liris_tool_hint: "Kalibrační nástroj od kapitánky Liris by mohl být tím, co Lift-Mother přiměje otevřít mi patro 177-Tiché.",
                arrived: "Lift-Mother mě vyvezla nahoru. Jsem v patře 177-Tichém.",
                hint_floor_counter: "Lift-Mother má rozbité počítadlo pater. Kdybych jí ho nechal spravit, byla by mi zavázaná. Prý se v takových strojích vyznají lidé z oblohy.",
                hint_lost_button: "Lift-Mother prý už léta postrádá jeden knoflík. Takové věci podle ní končí na Voxmarketu.",
                hint_importance: "Lift-Mother by mě možná pustila nahoru, kdybych ji přesvědčil, že jde opravdu o něco naléhavého. Jedna historka o Biskupce je pro ni drb, dvě, které se shodují, už jsou něco jiného. Kam Biskupka šla, by mohl vědět ještě někdo další ve městě.",
                hint_importance_gnur: "Lift-Mother by mě možná pustila nahoru, kdybych ji přesvědčil, že jde opravdu o něco naléhavého. Jedna historka o Biskupce je pro ni drb, dvě, které se shodují, už jsou něco jiného. Gnur slíbil, že si na Biskupku vzpomene, až mu přinesu to jádro.",
                hint_importance_kloor: "Lift-Mother by mě možná pustila nahoru, kdybych ji přesvědčil, že jde opravdu o něco naléhavého. Jedna historka o Biskupce je pro ni drb, dvě, které se shodují, už jsou něco jiného. Kloor Venn mi za vestigel řekne, co o Biskupce ví.",
            }
        },
        edgar_book: {
            title: 'Pomoct Edgarovi napsat knihu',
            description: 'Edgar Eskola zmínil, že chce napsat knihu. Měl bych mu pomoct.',
            updates: {
                completed: "Pomohl jsem Edgaru Eskolovi vymyslet knihu. Už píše.",
            }
        },
        find_loop_copy: {
            title: "Zapečetěný sklep",
            description: "Dostat se do zapečetěného sklepa pod Škrabákem, kde je podle Ortolana pořád uložená stará verze Infinite Foldu. Výtah dolů (Lift-Mother) chce heslo – a to nějak souvisí s Bohohřbitovem pod Radnicí.",
            updates: {
                passphrase_dead_god: "Podle Ortolana je heslem pravé jméno mrtvého boha, které si pamatuje už jen jeho náhrobek na Bohohřbitově. Měl bych si tam přečíst nápisy na hrobech – pomoct mi s tím může nějaký divinograf.",
                phor_can_read_graves: "Phor Calesta je divinograf – mohl by mi pomoct ty hroby přečíst.",
                password_from_choir: "Rezavý chór mi prozradil heslo do sklepa – „SKLÁDÁM SE“. Teď můžu s Lift-Mother sjet dolů do zapečetěného sklepa.",
                cellar_reached: "Dostal jsem se do zapečetěného sklepení pod Škrabákem – do staré laboratoře Ortolana a Dr. Elphi. Vzadu v šeru pořád pomalu dýchá jantarové světlo. Měl bych prozkoumat konzoli.",
                master_build_found: "Pod zaprášenou plachtou stojí hlavní sestava Nekonečného Skládání – Ortolanova pravidla, Elphiny zdi – pořád pod proudem. Něco v ní už je vzhůru.",
            }
        },
        join_lumen_directorate: {
            title: "V železe nic neroste",
            description: "Korektor úhlů mi udělí plné členství v Lumen Directorate, když ochromím svatyni strojů Rezavého chóru. Verrik v přízemí chová za sklem kultivar přesně na tohle – anebo si najdu vlastní způsob, jak stroje vyřadit. Pak se vrátím podat hlášení.",
            updates: {
                verrik_cultivar: "Verrik mi ten kultivar dal – řízenou hnilobu vyšlechtěnou žrát kov. Rozetřený do oleje rozežere zevnitř každý stroj, který se ho napije.",
                betrayed_to_rust: "Prozradil jsem Rezavému chóru sabotážní plán Direktorátu. Zpátky k Direktorátu už cesta nevede.",
            }
        },
        gang_of_lamps: {
            title: "Gang lamp",
            description: "Mluvící pouliční lampa mi prozradila tajemství: patří k rozprášenému gangu vědomých lamp, které se nemůžou hnout a nemají mezi sebou žádné spojení. Měl bych najít ty ostatní, aby skrze mě mohly mluvit.",
            updates: {
                lamp_family_known: "Lampy jsou celkem čtyři: Don nahoře na lávce pod Škrabákem 1140, Chandelier na sloupu na náměstí, Sconce u domu razítek a Torchère dole u vody, kde přijíždí náklad.",
                all_lamps_found: "Všechny čtyři lampy jsou nalezené a skrze mě zase ve spojení.",
                lamps_have_work: "Lampy říkají, že pro mě brzy budou mít práci. Měl bych se u nich zase stavit.",
                gang_lamps_destroyed: "Gang lamp zničil Lumen Direktorát. Už není koho propojovat a žádná odměna mě nečeká.",
                // Řádky `met_lamp_<id>` – kód vybírá podle počtu (params.textKey), {n} = počet nalezených lamp.
                lamps_found_one: "Zatím jsem našel jednu lampu.",
                lamps_found_few: "Zatím jsem našel {n} lampy.",
                lamps_found_many: "Zatím jsem našel {n} lamp.",
                lamps_found_of_four: "Našel jsem už {n} ze 4 lamp.",
            }
        },
        gang_don_spy: {
            title: "Uši v Rezavém chóru",
            description: "Don Girandole chce, abych špehoval Rezavý chór – vetřel se mezi jejich lidi (Brukk v jejich doméně, Gnur v Boudě 521, Ravla za Řvoucím korkem), zjistil, o co jim doopravdy jde, a donesl mu to. Sám mi řekne, až toho vyhrabu dost. A když zjistím, kde jejich doména ve skutečnosti leží, můžu mu prozradit i to.",
            updates: {
                // Řádky `gang_spy_<člen>` – kód vybírá podle počtu (params.textKey), {n} = počet tajemství.
                spy_secrets_one: "Z Rezavého chóru jsem vypáčil jedno tajemství. Měl bych s tím, co mám, zajít za Donem a zjistit, jestli to stačí.",
                spy_secrets_few: "Z Rezavého chóru jsem vypáčil už {n} tajemství. Měl bych s tím, co mám, zajít za Donem a zjistit, jestli to stačí.",
                spy_secrets_many: "Z Rezavého chóru jsem vypáčil už {n} tajemství. Měl bych s tím, co mám, zajít za Donem a zjistit, jestli to stačí.",
            }
        },
        gang_torchere_smuggle: {
            title: "Proklouznout kolem celníků",
            description: "Torchère mi dal balíček kontrabandu – Wimlick – abych ho propašoval do jeho mrtvé schránky: do uvolněné mříže na Ulici Hořícího Medvěda. Mám ho zastrčit do mříže a pak se mu ohlásit. (Nemusím – můžu si ho nechat, prodat ho nějakému obchodníkovi, nebo ho dokonce sám vyzkoušet.)",
            updates: {
                gang_smuggle_delivered: "Wimlick je v mříži. Měl bych se ohlásit Torchèrovi v přístavu.",
                gang_smuggle_kept: "Torchèrův Wimlick jsem si nechal pro sebe, místo abych ho uložil do mříže. V přístavu mu pořád můžu nahlásit, že předání proběhlo čistě – a balíček je můj, můžu ho prodat nebo použít.",
            }
        },
        gang_chandelier_eavesdrop: {
            title: "Vybrané sousto",
            description: "Chandelier chce drby. Poslala mě odposlouchávat k zahradě Lumen Direktorátu – je tam průduch, kterým jsou slyšet hlasy zevnitř. Mám tam naslouchat a pak jí donést, co zaslechnu.",
            updates: {
                // `gang_eavesdrop_heard` – jedna varianta na cestu, kód ji vybírá (params.textKey).
                gang_eavesdrop_heard_vent: "U průduchu v zahradě jsem zaslechl tajemství Direktorátu – jeden Korektor úhlů potichu vykuchal archiv, aby pohřbil chybu svého nadřízeného. Mám to donést Chandelier.",
                gang_eavesdrop_heard_neme: "Neme mi u průduchu Direktorátu ukázal celou provinilou pravdu – vyčištěný archiv a Korektora, který mezi svými tuší krtka Rezavého chóru. Mám to donést Chandelier.",
                gang_eavesdrop_heard_brine: "Solopis přečetl usazeniny v půdě: zahrada Direktorátu se doslova živí skartovanými spisy – Direktorát vykuchává vlastní archiv a důkazy kompostuje. Mám to donést Chandelier.",
            }
        },
        gang_sconce_recover: {
            title: "Vylovit, co bylo založeno",
            description: "Podle Sconce úředníci na Radnici schválně špatně založili zapečetěný spis ve spisovně uvnitř a schovali ho pod vymyšlené číslo případu. Musím dovnitř, najít spis, který tam nepatří, a vynést jí ho ven.",
            updates: {
                gang_dossier_recovered: "Ve spisových zásuvkách jsem našel ten špatně založený spis. Mám ho vynést ven za Sconce k radničním schodům.",
            }
        },
    }
};
