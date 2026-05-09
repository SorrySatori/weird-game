/**
 * Czech dialog translations for TownhallInteriorScene
 */
export default {
    _speakers: {
        'The Mad Poet': 'Šílený básník',
        'Freed Clerk': 'Osvobozený úředník',
        'Brine Scripture': 'Solopis',
    },
    poet_start: {
        text: {
            poet_start_resolved: `"Básník je pryč. Rukojmí jsou v bezpečí. Radnice se pořád třese, ale aspoň už se třese byrokraticky."`,
            poet_start_hostage: `Na pódiu pro veřejná čtení stojí hubená postava potřísněná inkoustem, v jedné ruce dlouhý papírový nůž, v druhé svazek básní s okraji jako krvácející papír. Pod pečetí Radnice sedí tři úředníci ztuhle jako formuláře.\n\n"Nikdo neodejde, dokud mě město neuslyší správně," prohlásí básník. "Ne zdvořile. Ne byrokraticky. Správně."`,
        },
        options: {
            what_happens_now: 'Co bude teď?',
            challenge_him_to_a_poetry_battle: 'Vyzvat ho na básnický souboj.',
            ask_what_he_wants: 'Zeptat se, co chce.',
            brine_scripture_read_the_salt_memory: '[Solopis] Přečíst solnou paměť místnosti.',
        }
    },
    poet_demands: {
        text: `"Chce? Chtění je próza. Vyžaduji svědectví. Úředníci orazítkovali mou sbírku jako 'nedostatečně občanskou'. Nazvali mé přesahy veršů porušením územního plánu.\n\nA tak veřejnost dostane čtení. Každou sloku. Každou poznámku pod čarou. Každý rukojmí držený nádech."`,
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
            poet_response_bishop_met_herself_breathless: `Básníkův nůž klesne o šířku čárky.\n\n"Já před sebou, než samo přijde —\nzrcadlo se učí, jak se zemře.\nObraz tedy. Ne pouhá ozdoba. Otisk zubu."`,
            poet_response_egg_cathedral_hatching_scripture: `Přitiskne stránku k čelu.\n\n"Skořápka-písmo, žloutek-chrám —\nvíry bdí kolem hrobu, jenž roste sám.\nDobře. Viděli jste architekturu, která se snaží stát rozsudkem."`,
            poet_response_skyship_refusing_to_land: `Podívá se ke stropu, jako by vzducholoď mohla poslouchat.\n\n"Myšlenka v lanoví, oblak v řetězu —\nnebe říká ano, město: zůstaň u břehu.\nObraz s výškou. Pokračujte."`,
            poet_response_citizen_made_of_tiny_cities: `Na nebezpečnou vteřinu se básník usměje.\n\n"Milion střech v půjčené kůži,\ndav, co říká: jsem občan, snad můžu.\nAno. Rozpaky jsou občanská malta."`,
            poet_response_punk_chord_dead_god_keeps_time: `Rukojmí sebou trhne, když básník vyklepe rytmus papírovým nožem.\n\n"Mrtvý bůh, živý zesilovač, nemožný takt —\nbožství pod zemí pořád hýbe nohama fakt.\nTen obraz má zuby i hlasitost."`,
            poet_response_prophetic_toad_three_minutes_ahead: `Přes všechnu snahu odfrkne.\n\n"Ropucha před dražebním zvonem —\ntři minuty nebe ve smrdutém skleněném trůně.\nKomické, ale živé. Přijímám kousnutí."`,
            poet_response_thorne_refuses_the_garden: `Básník přimhouří oči k prostoru kolem vás.\n\n"Trn mimo zahradníkův plán\nstále píše živý plot krví ran.\nUžitečné. Samo o sobě ne dost, ale užitečné."`,
            poet_response_locked_townhall_digesting_citizens: `Jeho stránky se zachvějí.\n\n"Dveře s úřady místo zubů,\nveřejný žaludek pod dlažbou klubů.\nAno. Tahle budova si to zasloužila."`,
            poet_response_your_poem_is_bad_and_hat_worse: `Básník úplně ztuhne.\n\n"Klobouk? Klobouk?\nHlupák si plete temeno s korunou,\na diví se, že verše padají dolů.\nUrážka není obraz. Je to selhané počasí."`,
            poet_response_round_one_default: `Básníkův nůž klesne o šířku čárky.\n\n"Obraz tedy. Ne pouhá ozdoba. Otisk zubu. Pokračujte."`,
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
            poet_response_dream_device_bruised_the_dead: `Básníkův hlas klesne tak nízko, že se nakloní i úředníci.\n\n"Snové smyčky. Chrámové modřiny. Milost škrtá lože.\nProgram žvýká spící a vrací mrtvé množe.\nTa rána je skutečná."`,
            poet_response_redmass_begging_not_proof: `Papírový nůž zaváhá.\n\n"Věrnost krmená cizím křikem\nje rez, co předstírá sen před publikem.\nPojmenovali jste ránu bez leštění."`,
            poet_response_rust_choir_machines_hum: `Odpoví chraplavým polozpěvem.\n\n"Impéria zapomenou. Motory opakují.\nŽelezo drží poslední poctivý rytmus.\nRána hučí. Slyším ji."`,
            poet_response_shed_forms_amputate: `Jeden úředník se jednou zasměje a hned se zděsí sám sebe.\n\n"Formulář sedmnáct, příloha tři: odejmout ruku, co žádá, že smí.\nByrokracie jako čepel. Dobré. Kruté a přesné."`,
            poet_response_misutkenn_writer_festival_fire: `Básník se zastydí dřív, než to stačí skrýt.\n\n"Medvědí kůže, autorské srdce —\nco spálili, stalo se jeho uměním trpce.\nRána, která žádá knihu místo pomsty."`,
            poet_response_clean_sulkberries_accused_by_fear: `Zašklebí se, jako by ochutnal lék.\n\n"Čisté ovoce v provinilé míse —\nstrach nasolí vše, co neovládá v tísni.\nMenší rána, ale pravá."`,
            poet_response_divinographer_waiting_dead_gods: `Na pódium jako by sedal prach.\n\n"Mrtví bohové dole, živá razítka výš —\npovolení popírá fosilní lásku již.\nAno. Město umí zranit i své archeology."`,
            poet_response_neme_hostages_roots_under_stone: `Básník slyší, jak úředníci dýchají společně.\n\n"Kořeny pod kamenem růst nepřestanou;\nnesou temnotu tam, kde listy neplanou.\nVáš symbiont vidí místnost. Vy jste to přesto museli vyslovit."`,
            poet_response_ulvarex_project_applause: `Místností na okamžik zatřese přízračný potlesk. Básníkovy oči ztvrdnou.\n\n"Půjčené ruce dělají půjčenou slávu;\nzrcadla neukončí rukojmí v davu.\nHezké. Příliš hezké."`,
            poet_response_wound_is_boredom: `Básník se usměje s děsivou úlevou.\n\n"Nuda, praví prázdný pohár,\npak se diví, že jej nikdo nenalévá.\nPojmenovali jste netrpělivost, ne ránu."`,
            poet_response_round_two_default: `Jeden úředník tiše vzlykne, jako by z něj unikla interpunkce.\n\nBásník to slyší. Poprvé mu přes tvář přejde stud, aniž by se vydával za genialitu.`,
        },
        options: {
            continue_to_final_round: 'Pokračovat do posledního kola.',
        }
    },
    poet_round_three: {
        text: `Třetí kolo — ROZSUDEK.\n\nBásník znovu pozvedne papírový nůž, ale do jeho metra vstoupila nejistota.\n\n"Ukončete to," zašeptá. "Řekněte mi, co báseň požaduje."`,
        options: {
            city_heard_you_without_knife: 'Město vás slyšelo. Teď ho nechte odpovědět bez vašeho nože.',
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
            poet_response_city_heard_you_without_knife: `Básník zvedne papírový nůž a pak zaslechne slabost toho gesta.\n\n"Když slyšení drží čepel v ruce,\nbáseň se bála už v první luce.\nVerš dopadl čistě. Teď uvidíme, zda vydrží."`,
            poet_response_story_someone_survives_to_revise: `Podívá se na své stránky, jako by ho zradily tím, že zůstaly upravitelné.\n\n"Koncept, jenž čtenáře zabije, sám zemře;\nživý text přežije odpovědi i dveře.\nŠtědrý rozsudek. Nebezpečný."`,
            poet_response_city_of_smaller_cities_consent: `Jeho výraz se rozštěpí v pozornost.\n\n"I jedno tělo může být město;\nsouhlas drží zdi, ne násilí vesto.\nPřinášíte občanskou teologii do souboje s nožem. Dobré."`,
            poet_response_redmass_given_freely_sings: `Nůž klesne k jeho boku.\n\n"Vyrvaný kov křičí a barví dlaň;\ndarovaný kov se přidá do písně sám.\nRozumíte propuštění."`,
            poet_response_poem_noise_they_leave_humming: `Někde ve zdech zavibrují trubky jako vzdálený zesilovač.\n\n"Píseň dokazují otevřené dveře,\nne těla počítaná na podlaze v šeře.\nNenávidím, jak blízko krásné to je."`,
            poet_response_truth_needs_no_hostage: `Polkne. Úředníci to slyší.\n\n"Pravda v řetězech stává se lží;\npusť dech ven, nebo uvidíš, jak mží.\nRozsudek s páteří."`,
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
        text: `Papírový nůž zacinká o pódium.\n\n"Dobře," řekne básník, najednou velmi unavený. "Místnost mě slyšela dost. Možná jsem to chtěl. Možná jsem se toho bál."\n\nSebere své stránky a odejde mezi osvobozenými úředníky. Zůstane po něm jen inkoust, pot a ticho, které patří všem.`,
        options: {
            check_on_the_clerks: 'Zkontrolovat úředníky.',
        }
    },
    poet_defeat: {
        text: `Básník vyslechne váš poslední verš a usměje se s děsivou úlevou.\n\n"Mrtvé umění," řekne. "Konečně upřímnost."\n\nPapírový nůž se zvedne. Rukojmí vykřiknou. Čtení se stane historií v tom nejhorším možném metru.`,
        options: {
            game_over: 'KONEC HRY',
        }
    },
    clerk_after_poet: {
        text: `"Děkuji. Oficiální zápis to nazve 'lyrickým narušením s rukojmími charakteristikami.' Zní to méně trapně než pravda.\n\nSpisovna je pořád v nepořádku, ale Radnice může znovu dýchat."`,
        options: {
            i_need_townhall_records: 'Potřebuji radniční záznamy.',
        }
    },
    clerk_records_not_ready: {
        text: `"Samozřejmě. Každý je potřebuje, jakmile na nás někdo mává nožem kvůli metru. Dejte nám chvíli odemknout archivní skříně a přestat se třást ve třech vyhotoveních."`,
        options: {
            ill_come_back_shortly: 'Brzy se vrátím.',
        }
    },
};
