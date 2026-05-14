/**
 * Czech dialog translations for TownhallInteriorScene
 */
export default {
    _speakers: {
        'The Mad Poet': 'Šílený básník',
        'Freed Clerk': 'Osvobozený úředník',
        'Brine Scripture': 'Solopis',
        'Complaint Eater': 'Požírač stížností',
        'Councilor Seraphel Dune': 'Radní Seraphel Dune',
    },
    poet_start: {
        text: {
            poet_start_resolved: `"Básník je pryč. Rukojmí jsou v bezpečí. Radnice se pořád třese, ale aspoň už se třese byrokraticky."`,
            poet_start_hostage: `Na pódiu pro veřejná čtení stojí hubená postava potřísněná inkoustem, v jedné ruce starý revolver, v druhé svazek básní s okraji jako krvácející papír. Pod pečetí Radnice sedí úředník, radní a Požírač stížností ztuhle jako formuláře.\n\n"Nikdo neodejde, dokud mě město neuslyší správně," prohlásí básník. "Ne zdvořile. Ne byrokraticky. Správně."`,
        },
        options: {
            what_happens_now: 'Co bude teď?',
            challenge_him_to_a_poetry_battle: 'Vyzvat ho na básnický souboj.',
            ask_what_he_wants: 'Zeptat se, co chce.',
            brine_scripture_read_the_salt_memory: '[Solopis] Přečíst solnou paměť místnosti.',
        }
    },
    poet_demands: {
        text: `"Chce? Chtění je próza. Vyžaduji svědectví. Radnice orazítkovala mou sbírku jako 'nedostatečně občanskou'. Nazvala mé přesahy veršů porušením územního plánu.\n\nA tak veřejnost dostane čtení. Každou sloku. Každou poznámku pod čarou. Každý rukojmí držený nádech."`,
        options: {
            then_ill_answer_in_verse: 'Pak odpovím veršem.',
            i_need_a_moment: 'Potřebuji chvíli.',
        }
    },
    poet_brine_read: {
        text: `Sůl se probudí pod jazykem. Podlaha si pamatuje boty drhnoucí o kámen v panice, rozlitý inkoust zasychající do malých černých útesů a jeden verš opakovaný tak dlouho, až se stal ranou: "Město pro mě nemá ucho."\n\nSolopis nabízí paměť, ne vítězství. Dává vám materiál. Zpívat ho stále musíte vy.`,
        options: {
            use_that_memory_in_the_contest: 'Použít tu paměť v souboji.',
        }
    },
    poet_challenge: {
        text: `"Vyzývatel? Dobře. Konečně má místnost tep. Tři kola. Obraz, rána, rozsudek. Přineste mi město tak, jak jste ho prožili.\n\nPokud je vaše báseň živá, propustím je. Pokud je mrtvá, všichni zjistíme, co špatné umění stojí."`,
        options: {
            begin_the_poetry_battle: 'Zahájit básnický souboj.',
        }
    },
    poet_round_one: {
        text: `První kolo — OBRAZ.\n\nBásník prudce rozevře stránku. "Horní Morkezela je ústa plná dveří. Dejte mi jeden obraz, který dokazuje, že vás kousla."`,
        options: {
            second_shadow_watching_first: 'Druhý stín sledující první, oba předstírají, že se nebojí.',
            bishop_met_herself_breathless: 'Zpovědnice, kde Biskupka potkala sebe samu, bezdechou a už mluvící.',
            egg_cathedral_hatching_scripture: 'Vejčitá katedrála líhnoucí písmo, zatímco každá víra čeká, že bude vybrána.',
            skyship_refusing_to_land: 'Vzducholoď uvízlá nad Křižovatkou jako myšlenka odmítající přistát.',
            citizen_made_of_tiny_cities: 'Občan složený z maličkých měst, držený pohromadě magnety a rozpaky.',
            punk_chord_dead_god_keeps_time: 'Punkový akord, v němž mrtvý bůh stále drží rytmus pod podlahou.',
            prophetic_toad_three_minutes_ahead: 'Prorocká ropucha v mosazné nádobě, mrkající tři minuty před příhozy.',
            thorne_refuses_the_garden: '[Thorne-Still] Trn, který odmítá zahradu, a přesto se stává součástí jejího tvaru.',
            locked_townhall_digesting_citizens: 'Zamčená Radnice trávící každého občana, který zaklepe.',
            your_poem_is_bad_and_hat_worse: 'Vaše báseň je špatná a váš klobouk ještě horší.',
        }
    },
    poet_round_one_result: {
        text: {
            poet_response_second_shadow_watching_first: `Básník prudce nasaje dech a odpoví vlastním veršem:\n\n"Dva stíny pod špatným sluncem jdou —\njeden prchá, druhý za ním, oba se bojí tmou.\nAno. Město vás kouslo tam, kde já počítá samo sebe."`,
            poet_response_bishop_met_herself_breathless: `Básníkova zbraň klesne o šířku čárky.\n\n"Já před sebou, než samo přijde —\nzrcadlo se učí, jak se zemře.\nObraz tedy. Ne pouhá ozdoba. Otisk zubu."`,
            poet_response_egg_cathedral_hatching_scripture: `Přitiskne stránku k čelu.\n\n"Skořápka-písmo, žloutek-chrám —\nvíry bdí kolem hrobu, jenž roste sám.\nDobře. Viděli jste architekturu, která se snaží stát rozsudkem."`,
            poet_response_skyship_refusing_to_land: `Podívá se ke stropu, jako by vzducholoď mohla poslouchat.\n\n"Myšlenka v lanoví, oblak v řetězu —\nnebe říká ano, město: zůstaň u břehu.\nObraz s výškou. Pokračujte."`,
            poet_response_citizen_made_of_tiny_cities: `Na nebezpečnou vteřinu se básník usměje.\n\n"Milion střech v půjčené kůži,\ndav, co říká: jsem občan, snad můžu.\nAno. Rozpaky jsou občanská malta."`,
            poet_response_punk_chord_dead_god_keeps_time: `Rukojmí sebou trhne, když básník vyklepe rytmus hlavní revolveru.\n\n"Mrtvý bůh, živý zesilovač, nemožný takt —\nbožství pod zemí pořád hýbe nohama fakt.\nTen obraz má zuby i hlasitost."`,
            poet_response_prophetic_toad_three_minutes_ahead: `Přes všechnu snahu odfrkne.\n\n"Ropucha před dražebním zvonem —\ntři minuty nebe ve smrdutém skleněném trůně.\nKomické, ale živé. Přijímám kousnutí."`,
            poet_response_thorne_refuses_the_garden: `Básník přimhouří oči k prostoru kolem vás.\n\n"Trn mimo zahradníkův plán\nstále píše živý plot krví ran.\nUžitečné. Samo o sobě ne dost, ale užitečné."`,
            poet_response_locked_townhall_digesting_citizens: `Jeho stránky se zachvějí.\n\n"Dveře s úřady místo zubů,\nveřejný žaludek pod dlažbou klubů.\nAno. Tahle budova si to zasloužila."`,
            poet_response_your_poem_is_bad_and_hat_worse: `Básník úplně ztuhne.\n\n"Klobouk? Klobouk?\nHlupák si plete temeno s korunou,\na diví se, že verše padají dolů.\nUrážka není obraz. Je to selhané počasí."`,
            poet_response_round_one_default: `Básníkova zbraň klesne o šířku čárky.\n\n"Obraz tedy. Ne pouhá ozdoba. Otisk zubu. Pokračujte."`,
        },
        options: {
            continue_to_round_two: 'Pokračovat do druhého kola.',
        }
    },
    poet_round_two: {
        text: `Druhé kolo — RÁNA.\n\n"Město se nepopisuje památkami," řekne. "Popisuje se tím, co dělá měkkým částem. Pojmenujte ránu, aniž byste ji zmenšili."`,
        options: {
            dream_device_bruised_the_dead: 'Snové zařízení proměnilo útěchu ve smyčku ostrou dost na to, aby pohmoždila mrtvou.',
            redmass_begging_not_proof: 'Živá rudohmota prosící, aby se nestala důkazem cizí věrnosti.',
            rust_choir_machines_hum: 'Stroje Rezavého chóru hučí i poté, co každé impérium zapomene vlastní melodii.',
            shed_forms_amputate: 'Hangár 521 mě naučil, že formuláře amputují čistěji než nože.',
            misutkenn_writer_festival_fire: 'Mišutkennský spisovatel nese festivalový oheň v žebrech a stále žádá příběh.',
            clean_sulkberries_accused_by_fear: 'Čisté sulkberry, obviněné jen proto, že strach potřeboval pohodlné místo k hnití.',
            divinographer_waiting_dead_gods: 'Divinograf čekající na povolení, zatímco mrtví bohové fosilizují pod razítky.',
            neme_hostages_roots_under_stone: '[Neme] Rukojmí jsou kořeny pod kamenem: vyděšené, propojené, stále živé.',
            ulvarex_project_applause: '[Ulvarex] Promítnout do místnosti potlesk, dokud strach nevypadá jako obdiv.',
            wound_is_boredom: 'Tou ranou je nuda. Všichni už jsou unavení z poslouchání.',
        }
    },
    poet_round_two_result: {
        text: {
            poet_response_dream_device_bruised_the_dead: `Básníkův hlas klesne tak nízko, že se nakloní i rukojmí.\n\n"Snové smyčky. Chrámové modřiny. Milost škrtá lože.\nProgram žvýká spící a vrací mrtvé množe.\nTa rána je skutečná."`,
            poet_response_redmass_begging_not_proof: `Revolver zaváhá.\n\n"Věrnost krmená cizím křikem\nje rez, co předstírá sen před publikem.\nPojmenovali jste ránu bez leštění."`,
            poet_response_rust_choir_machines_hum: `Odpoví chraplavým polozpěvem.\n\n"Impéria zapomenou. Motory opakují.\nŽelezo drží poslední poctivý rytmus.\nRána hučí. Slyším ji."`,
            poet_response_shed_forms_amputate: `Jeden úředník se jednou zasměje a hned se zděsí sám sebe.\n\n"Formulář sedmnáct, příloha tři: odejmout ruku, co žádá, že smí.\nByrokracie jako čepel. Dobré. Kruté a přesné."`,
            poet_response_misutkenn_writer_festival_fire: `Básník se zastydí dřív, než to stačí skrýt.\n\n"Medvědí kůže, autorské srdce —\nco spálili, stalo se jeho uměním trpce.\nRána, která žádá knihu místo pomsty."`,
            poet_response_clean_sulkberries_accused_by_fear: `Zašklebí se, jako by ochutnal lék.\n\n"Čisté ovoce v provinilé míse —\nstrach nasolí vše, co neovládá v tísni.\nMenší rána, ale pravá."`,
            poet_response_divinographer_waiting_dead_gods: `Na pódium jako by sedal prach.\n\n"Mrtví bohové dole, živá razítka výš —\npovolení popírá fosilní lásku již.\nAno. Město umí zranit i své archeology."`,
            poet_response_neme_hostages_roots_under_stone: `Básník slyší, jak rukojmí dýchají společně.\n\n"Kořeny pod kamenem růst nepřestanou;\nnesou temnotu tam, kde listy neplanou.\nVáš symbiont vidí místnost. Vy jste to přesto museli vyslovit."`,
            poet_response_ulvarex_project_applause: `Místností na okamžik zatřese přízračný potlesk. Básníkovy oči ztvrdnou.\n\n"Půjčené ruce dělají půjčenou slávu;\nzrcadla neukončí rukojmí v davu.\nHezké. Příliš hezké."`,
            poet_response_wound_is_boredom: `Básník se usměje s děsivou úlevou.\n\n"Nuda, praví prázdný pohár,\npak se diví, že jej nikdo nenalévá.\nPojmenovali jste netrpělivost, ne ránu."`,
            poet_response_round_two_default: `Jeden úředník tiše vzlykne, jako by z něj unikla interpunkce.\n\nBásník to slyší. Poprvé mu přes tvář přejde stud, aniž by se vydával za genialitu.`,
        },
        options: {
            continue_to_final_round: 'Pokračovat do posledního kola.',
        }
    },
    poet_round_three: {
        text: `Třetí kolo — ROZSUDEK.\n\nBásník znovu pozvedne revolver, ale do jeho metra vstoupila nejistota.\n\n"Ukončete to," zašeptá. "Řekněte mi, co báseň požaduje."`,
        options: {
            city_heard_you_without_gun: 'Město vás slyšelo. Teď ho nechte odpovědět bez vaší zbraně.',
            story_someone_survives_to_revise: 'Ať se z toho stane příběh, který někdo přežije a může přepracovat.',
            city_of_smaller_cities_consent: 'I město složené z menších měst přežívá souhlasem, ne zákonem rukojmí.',
            redmass_given_freely_sings: 'Rudohmota mě naučila: co je dáno svobodně, zpívá déle než to, co je vyrváno.',
            poem_noise_they_leave_humming: 'Ať se vaše báseň stane hlukem, který si mohou odnést v hlavě, ne místností, kde zemřou.',
            truth_needs_no_hostage: 'Pravda nepotřebuje rukojmí, aby byla zkoumána. Propusťte je a zůstaňte pravdivý.',
            brine_ink_dries_into_salt: '[Solopis] I inkoust vysychá v sůl. Ať zůstane bolest, ne rukojmí.',
            neme_living_poem_releases: '[Neme] Živá báseň propouští to, co drží příliš pevně.',
            surrender_before_they_see_fear: 'Báseň požaduje, abyste se vzdal, než všichni poznají, že se bojíte.',
            demands_blood_yours: 'Požaduje krev. Vaši, pokud bude třeba.',
        }
    },
    poet_judgment: {
        text: {
            poet_response_city_heard_you_without_gun: `Básník zvedne revolver a pak zaslechne slabost toho gesta.\n\n"Když slyšení drží hlaveň v ruce,\nbáseň se bála už v první luce.\nVerš dopadl čistě. Teď uvidíme, zda vydrží."`,
            poet_response_story_someone_survives_to_revise: `Podívá se na své stránky, jako by ho zradily tím, že zůstaly upravitelné.\n\n"Koncept, jenž čtenáře zabije, sám zemře;\nživý text přežije odpovědi i dveře.\nŠtědrý rozsudek. Nebezpečný."`,
            poet_response_city_of_smaller_cities_consent: `Jeho výraz se rozštěpí v pozornost.\n\n"I jedno tělo může být město;\nsouhlas drží zdi, ne násilí vesto.\nPřinášíte občanskou teologii na recitál pod hlavní. Dobré."`,
            poet_response_redmass_given_freely_sings: `Zbraň klesne k jeho boku.\n\n"Vyrvaný kov křičí a barví dlaň;\ndarovaný kov se přidá do písně sám.\nRozumíte propuštění."`,
            poet_response_poem_noise_they_leave_humming: `Někde ve zdech zavibrují trubky jako vzdálený zesilovač.\n\n"Píseň dokazují otevřené dveře,\nne těla počítaná na podlaze v šeře.\nNenávidím, jak blízko krásné to je."`,
            poet_response_truth_needs_no_hostage: `Polkne. Rukojmí to slyší.\n\n"Pravda v řetězech stává se lží;\npusť dech ven, nebo uvidíš, jak mží.\nRozsudek s páteří."`,
            poet_response_brine_ink_dries_into_salt: `Sůl štípne za zuby. Básník slyší něco staršího než lichotku.\n\n"Inkoust v sůl a bolest v břeh —\nnech ránu být, nezamykej dech.\nPaměť vám pomáhá. Nenahrazuje vás."`,
            poet_response_neme_living_poem_releases: `Nemeina přítomnost se pod vašimi slovy otevře jako zelené ticho.\n\n"Kořen, jenž svírá, až kořeny prasknou,\nse musí naučit, čeho se živé vzdá s maskou.\nMoudrost symbionta nesená vašimi ústy."`,
            poet_response_surrender_before_they_see_fear: `Básníkův stud zkysne v pýchu.\n\n"Nazvi mě zbabělcem, říkej tomu umění —\nmíjíš ránu a zasahuješ srdce v domnění.\nMožná pravda. Ne užitečná."`,
            poet_response_demands_blood_yours: `Básníkova tvář se uklidní tím nejhorším způsobem.\n\n"Krev je nejlevnější karmínové slovo;\nkaždý řezník si myslí, že je slyšen znovu.\nSpletli jste si násilí s koncem."`,
            poet_response_round_three_default: `Dlouhou vteřinu je Radnice jen dech.\n\nBásník se podívá na rukojmí, pak na své stránky, pak na vás. Báseň dospěla k poslednímu verši.`,
        },
        options: {
            let_the_line_fall: 'Nechat verš dopadnout.',
        }
    },
    poet_victory: {
        text: `Revolver zacinká o pódium.\n\n"Dobře," řekne básník, najednou velmi unavený. "Místnost mě slyšela dost. Možná jsem to chtěl. Možná jsem se toho bál."\n\nSebere své stránky a odejde mezi osvobozenými rukojmími. Zůstane po něm jen inkoust, pot a ticho, které patří všem.`,
        options: {
            check_on_the_hostages: 'Zkontrolovat rukojmí.',
        }
    },
    poet_defeat: {
        text: `Básník vyslechne váš poslední verš a usměje se s děsivou úlevou.\n\n"Mrtvé umění," řekne. "Konečně upřímnost."\n\nRevolver se zvedne. Rukojmí vykřiknou. Čtení se stane historií v tom nejhorším možném metru.`,
        options: {
            game_over: 'KONEC HRY',
        }
    },
    clerk_after_poet: {
        text: {
            clerk_after_poet_fresh: `"Děkuji. Oficiální zápis to nazve 'lyrickým narušením s rukojmími charakteristikami.' Zní to méně trapně než pravda.\n\nSpisovna je pořád v nepořádku, ale Radnice může znovu dýchat. Pokud potřebujete záznamy o Biskupce, ptejte se hned, než někdo vymyslí obnovovací komisi."`,
            clerk_after_poet_records_checked: `"Archivní skříně jsou teď otevřené. Už jsem pro vás vytáhl složku Biskupky — nebo to, co ze složky zbyde, když se Radnice dost dlouho vyhýbá odpovědnosti."`,
        },
        options: {
            i_need_the_bishops_townhall_records: 'Potřebuji radniční záznamy o Biskupce.',
            remind_me_what_the_bishop_records_showed: 'Připomeňte mi, co ukázaly záznamy o Biskupce.',
        }
    },
    clerk_bishop_records: {
        text: `"Dobře. Biskupka, zástupkyně Obazoby, Katedrální rada, zpráva o dvojníkovi... okamžik."

Úředník odemkne tři skříně, odmítne dvě zásuvky jako "emočně nepřesné" a nakonec vytáhne tenkou přijímací knihu.

"Tohle je ta podivná část. Pod jménem Biskupky není žádná oficiální incidentní zpráva. Žádná podaná stížnost na dvojníka. Žádné následné řízení. Existuje jen záznam o vydání kancelářských tiskovin: tři dny před smrtí si vyžádala Oficiální radniční reportní zápisník. Razítkoval jsem ho sám.

Ten útržek, který jste našli, nebyla oficiální zpráva. Byla to osobní poznámka napsaná na oficiálním papíře."`,
        options: {
            so_the_rest_of_the_notebook_exists: 'Takže zbytek zápisníku existuje.',
            were_there_other_doppelganger_reports: 'Byly tu i jiné zprávy o dvojnících?',
        }
    },
    clerk_bishop_notebook_hook: {
        text: `"Téměř jistě. Radniční reportní zápisníky jsou vázané v číslovaných oddílech. Pokud jedna stránka přežila v jejím rukávu, zbytek toho zápisníku někam odešel.

Výpůjční lístek říká, že si ho odnesla po zavírací době. Žádné razítko o vrácení. Žádná archivní kopie. Pokud používala oficiální papír jako soukromý deník, chybějící stránky by mohly vysvětlit setkání s dvojníkem, měnící se spory i to, proč zapečetila Katedrálu.

Najděte zápisník. Radnice nemůže špatně založit něco, co se jí nikdy nevrátilo."`,
        options: {
            ill_find_the_bishops_notebook: 'Najdu Biskupčin zápisník.',
            what_about_other_doppelganger_reports: 'A co jiné zprávy o dvojnících?',
        }
    },
    clerk_other_doppelganger_reports: {
        text: `"Žádné veřejné záznamy pod 'dvojník', 'duplikát občana', 'nedýchající já' ani starou kategorií 'zrcadlové občanské znepokojení'. Kontroloval jsem to, protože přesně takové kategorie úředníci vymýšlejí a pak litují.

Je tu jeden zapečetěný křížový odkaz: 'katedrálně přilehlá identitní nepravidelnost — teologická nouze.' Stejný týden. Stejná série razítek. Ten, kdo to podal, chtěl, aby se Radnice dívala jinam, aniž by technicky lhala.

Takže: žádný vzorec, který dokážu. Ale Biskupka nebyla jen vyděšená. Něco dokumentovala."`,
        options: {
            then_the_notebook_is_the_next_lead: 'Pak je další stopou zápisník.',
            thats_enough_for_now: 'To prozatím stačí.',
        }
    },
    clerk_bishop_records_summary: {
        text: `"Krátká verze: Biskupčina poznámka o dvojníkovi nebyla podaná radniční zpráva. Byla to osobní poznámka napsaná v Oficiálním radničním reportním zápisníku, který si krátce před smrtí vypůjčila.

Zápisník se nikdy nevrátil. Pokud je ten vytržený list pravý, zbytek zápisníku je pravděpodobně další skutečná stopa."`,
        options: {
            ill_keep_looking: 'Budu hledat dál.',
        }
    },
    complaint_eater_start: {
        text: `Tvor za přepážkou si složí štos stížnostních formulářů do úst. Každé kousnutí vydá drobný zvuk úředního razítka.

"Mmm. Odvolání ve strachové omáčce. Výtečné. Přišli jste podat stížnost, stáhnout ji, nebo se jí stát?"`,
        options: {
            what_are_you: 'Co jste zač?',
            eaten_anything_about_the_bishop: 'Snědl jste něco o Biskupce?',
            who_is_the_councilor: 'Kdo je ten radní?',
        }
    },
    complaint_eater_identity: {
        text: `"Městské trávení. Každé město jedno potřebuje. Občané přinesou bolest k přepážce, úředníci z ní udělají papír a já zajistím, aby se ten papír nenaučil množit.

Stížnosti nelitujte. Většina chtěla být snědena. Křičí až odvolání."`,
        options: {
            thats_useful_i_suppose: 'To je svým způsobem užitečné.',
        }
    },
    complaint_eater_bishop: {
        text: {
            complaint_eater_bishop_records_checked: `"Biskupčin papír chutnal špatně: nepodaný, nestrávený, ne náš. Osobní inkoust v úředním obleku. Úředník má pravdu o něm. Já vím jen to, co odmítá můj žaludek."`,
            complaint_eater_bishop_records_locked: `"Biskupčin papír je zamčený za vystrašenými zásuvkami. Zeptejte se osvobozeného úředníka. Úředníci umí otevírat skříně. Já umím otevírat jen následky."`,
        },
        options: {
            ill_ask_the_clerk: 'Zeptám se úředníka.',
            ask_something_else: 'Zeptat se na něco jiného.',
        }
    },
    complaint_eater_councilor: {
        text: `"Seraphel Dune? Vysoce funkční omluva ve společenském kabátě. Podepisuje to, čeho se jiní úředníci bojí i kurzívou.

Jestli vám Radnice dluží odměnu, přimějte ho říct to nahlas. Vyslovený dluh se hůř zakládá špatně."`,
        options: {
            ill_speak_with_councilor_dune: 'Promluvím si s radním Dunem.',
            ask_something_else: 'Zeptat se na něco jiného.',
        }
    },
    councilor_start: {
        text: {
            councilor_start_access_granted: `"Příkaz ke vstupu do Godgraveyardu je už zapečetěný na vaše jméno. Dolní dveře poznají omluvu Radnice, což je nejbližší věc ke klíči, kterou tahle budova má."`,
            councilor_start_needs_reward: `Radní Seraphel Dune stojí u skříně nouzových pečetí a vypadá, jako by osobně zklamal každý zákon v místnosti.

"Ukončili jste rukojmí krizi, aniž by do zápisu přibyla těla. Radnice je vaším dlužníkem. Mám pravomoc proměnit ten dluh v jednu užitečnou nemožnost."`,
        },
        options: {
            grant_access_to_the_godgraveyard: 'Udělit přístup do Godgraveyardu.',
            what_happens_to_the_poet: 'Co bude s básníkem?',
            what_is_wrong_with_this_townhall: 'Co je s touhle Radnicí špatně?',
            bishops_records_were_tampered_with: 'Se záznamy o Biskupce někdo manipuloval.',
        }
    },
    councilor_godgraveyard_reward: {
        text: `"Žádost Phor Calesty o povolení k vykopávkám čekala na tři komise, dvě teologické dopadové studie a jednoho úředníka dost odvážného přiznat, že dolní dveře existují.

Čekání skončilo. Uděluji vám i vašemu divinografovi přístup do úrovně Godgraveyardu pod Radnicí. Pokud se vás tam dole cokoli zeptá, kdo vám to povolil, ukažte mu mou pečeť a nepřijímejte protinabídku."`,
        options: {
            ill_use_it_carefully: 'Použiju to opatrně.',
        }
    },
    councilor_poet: {
        text: `"Oficiálně: zadržení, posouzení, náhrada škody a zákaz všech veřejných čtení delších než sedm minut.

Neoficiálně: Radnice vytvořila tlak, pod kterým vybuchl. To neomlouvá zbraň. Znamená to ale, že zápis se bude muset naučit studu."`,
        options: {
            ask_something_else: 'Zeptat se na něco jiného.',
        }
    },
    councilor_townhall: {
        text: `"Tahle budova byla navržena, aby měnila veřejnou hrůzu v indexovaný papír. Povedlo se jí to příliš dobře. Někdy cestou začal archiv chránit proces místo lidí.

Požírač stížností brání tomu, aby se tím Radnice zadusila. Sotva."`,
        options: {
            ask_something_else: 'Zeptat se na něco jiného.',
        }
    },
    councilor_bishop_records: {
        text: `"Manipulované, obejité, nebo založené pod kategorií, která kousne každého, kdo ji vysloví. Zatím nedokážu říct které.

Ale jestli Biskupka používala úřední papír jako soukromý zápisník, schovávala pravdu na jediné místo, kde by tady nikdo dobrovolně nečetl: do papírování."`,
        options: {
            missing_notebook_is_still_the_lead: 'Chybějící zápisník je pořád hlavní stopa.',
        }
    },
};
