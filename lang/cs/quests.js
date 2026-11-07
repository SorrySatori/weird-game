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
                edgar_eskola_clue: 'Úředník mi řekl, abych našel Edgara Eskolu v hospodě Řvoucí korek. Možná něco ví.',   // jen staré savy
                clerk_records_hint: 'Úředník v Boudě 521 naznačil, že Inkoustový tribunál má o Biskupce záznamy. Ukáže mi je, až Gnurovi řeknu, že jádro nedostane.',
                bishop_elphi_clerk: 'Úředník v Boudě 521 mi ukázal záznamy Inkoustového tribunálu: Biskupka měla povolení k návštěvě studia Dr. Elphi v patře 177-Tichém ve Škrabáku 1140.',
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
            description: "Rád bych se přidal k Direktorátu. Měl bych se dozvědět víc o jejich práci a zjistit, co je potřeba, abych se stal jedním z nich.",
            updates: {
                demo_not_yet: 'Liris mě varovala, že Direktorát ani hlavní náměstí v tomhle demu otevřené nejsou. Na přidání se k nim si budu muset počkat do plné verze.',
                liris_directions: "Kapitánka Liris mi poradila, kde najdu sídlo Direktorátu – nedaleko hlavního náměstí. Když se k nim přidám, možná si vysloužím místo v posádce Verdigrace.",
            }
        },
        find_rust_choir: {
            title: 'Najít Rezavý chór',
            description: 'Musím najít způsob, jak se setkat s Rezavým chórem, který sídlí v horních patrech budovy Škrabáku.',
            updates: {
                talk_to_ravla: 'Měl bych si nejdřív promluvit s Ravlou v hospodě Řvoucí korek.',
                talked_to_ravla: 'Ravla ve Řvoucím korku chce, abych připravil hostinu pro stroje Rezavého chóru jako důkaz mého odhodlání.',
            }
        },
        rust_feast: {
            title: 'Rezavá Hostina',
            description: 'Připravit hostinu pro stroje Rezavého chóru sesbíráním oleje, kovu a živé rudé hmoty, a přinést vše Ravle do Řvoucího korku.',
            updates: {
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
                registration_sent_to_applications: "Vrchní úředník na Registraci formuláře jen vydává; který formulář Ortolanovy ruce potřebují, rozhodují Žádosti v nejvyšším patře Boudy.",
                form_obtained: 'Úspěšně jsem získal formulář pro Ortolana.',
                partial_progress: 'Získal jsem Dočasné povolení, které by mohlo Ortolanovi pomoct, ale není plně schválené.',
                failed_attempt: 'Můj pokus o registraci selhal. Budu muset najít jiný způsob, jak Ortolanovi pomoct.',
                completed: "Sehnal jsem Ortolanovi papíry kvůli rukám navíc. Z vděčnosti mi dal dárek.",
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
                hint_importance_clerk: "Lift-Mother by mě možná pustila nahoru, kdybych ji přesvědčil, že jde opravdu o něco naléhavého. Jedna historka o Biskupce je pro ni drb, dvě, které se shodují, už jsou něco jiného. Gnura jsem odmítl, ale úředník v Boudě 521 mi to dluží – Inkoustový tribunál si přece všechno zapisuje.",
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
    }
};
