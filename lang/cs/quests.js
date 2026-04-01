/**
 * Czech quest translations — keyed by quest ID
 */
export default {
    quests: {
        find_bishop: {
            title: 'Najít Biskupku',
            description: 'Houbový Mistr mě pověřil nalezením Biskupky v Vaječné Katedrále. Mohla by vědět o nouzovém volání přijatém z města přes myceliární síť. Musím s ní promluvit a zjistit víc.',
            updates: {
                vestigel: 'Kloor Venn chce, abych našel jeden ze tří Vestigelů na trhu. Zmínil, že jeden má obchodnice jménem Zerren.',
                elphi_contact: 'Podle Kloora Venna Biskupka často navštěvovala Dr. Elpi Quarnovou... Měl bych ji hledat ve Škrabáku 1140.',
                bishop_clue_gnur: "Biskupka byla viděna u Škrabáku 1140, jak provádí neobvyklý obchod s 'herní čočkou'. Gnur by mohl vědět víc, ale chce něco na oplátku.",
                edgar_eskola_clue: 'Úředník mi řekl, abych našel Edgara Eskolu v hospodě Křičící Korek. Možná něco ví.',
                bishop_location_scraper: 'Biskupka byla naposledy viděna, jak míří do Škrabáku 1140 za Dr. Elphi.',
                got_floor_counter_tool: 'Kapitán Liris mi dal kalibrační nástroj na opravu počítadla pater Matky Výtahu, což by mi mělo umožnit přístup do studia Dr. Elphi.',
                lift_mother_permission: 'Matka Výtahu mi udělila přístup do studia Dr. Elphi v patře 177-Ticho.',
                reached_elphi_studio: 'Dostal jsem se do studia Dr. Elphi v patře 177-Ticho. Teď musím najít stopy po Biskupce.',
                check_shard_backyard: 'Dr. Elphi zmínila, že Biskupka byla naposledy viděna na dvorku Střepu. Měl bych se tam podívat.',
                found_elevator_button: 'Našel jsem Zapomenutý Výtahový Knoflík u Zerren, který mi může pomoct dostat se na patro Dr. Elphi.',
            }
        },
        who_killed_bishop: {
            title: 'Kdo zabil Biskupku?',
            description: 'Našel jsem Biskupku mrtvou v opuštěném autobusu za budovou Škrabáku. Její tělo nevykazuje téměř žádné známky násilí. Měl bych vyšetřit, kdo by mohl být zodpovědný za její smrt.',
            updates: {
                dead_bishop_bruising: 'Prohlédl jsem tělo Biskupky a našel modřiny na spáncích, kde se připojují rozhraní snových zařízení.',
                dead_bishop_cartridge: 'Před smrtí Biskupka zřejmě hrála hru nazvanou „Kardinálská Hostina".',
                dead_bishop_helmet: 'Před smrtí Biskupka zřejmě používala přenosnou helmu snového rozhraní.',
                dead_bishop_journal: 'Před smrtí Biskupka zřejmě psala do svého deníku... „Město mě už neslyší. Možná to dokážou sny."',
                dead_bishop_notebook: 'Našel jsem podivnou poznámku... „Vešla jsem do zpovědnice, ale ona tam už byla. Vypadala jako já..."',
                bishop_dissection: 'Tělo Biskupky obsahuje podivný zářící houbový výrůstek, který se integroval s její nervovou soustavou.',
                dead_bishop_berries: 'Před smrtí Biskupka zřejmě jedla Mručenky.',
                gardener_bishop_info: 'Zahradník Verrik u Lumen Direktoriátu zmínil, že Biskupka pravidelně navštěvovala — konkrétně kvůli Korektoru Úhlu.',
                gardener_sulkberry_info: 'Zahradník u Lumen Direktoriátu potvrdil, že kořeněné Mručenky jsou kontrolovaná komodita.',
                ac_bishop_relationship: 'Korektor Úhlu potvrdil profesionální vztah s Biskupkou — pravidelná setkání o přístupu do Katedrály a líhnutí.',
                ac_sulkberry_confirmed: 'Korektor Úhlu potvrdil dodávky Mručenek pro Biskupku — používány pro snovou imerzi v Katedrále.',
                ac_tamper_hint: 'Korektor Úhlu naznačil, že zmanipulované Mručenky by mohly způsobit neurální trauma odpovídající stavu Biskupky.',
                elphi_dream_kill: 'Dr. Elphi potvrdila, že poškozená snová kazeta může způsobit smrt přetížením neurální soustavy — „smrt rekurzivním zážitkem".',
                elphi_bruising: 'Dr. Elphi potvrdila, že modřiny naznačují zpětnou vlnu ze snové relace bez bezpečnostních omezovačů.',
                elphi_cartridge: 'Dr. Elphi potvrdila, že Kardinálská Hostina je normální hra — to kanibalistické RPG s ještěry. Ale data relace ukazují katastrofální selhání.',
                elphi_helmet: 'Dr. Elphi říká, že poškozený port helmy potvrzuje, že signálová zátěž překročila limity hardware.',
                elphi_memo: 'Dr. Elphi nedokázala vysvětlit dvojníka z poznámky Biskupky. Není to známý vedlejší efekt snové technologie.',
                elphi_townhall_log: 'Setkání Biskupky s dvojníkem bylo formálně zaznamenáno na Radnici. Archivní úředník by mohl mít kopii.',
                elphi_journal: 'Dr. Elphi interpretovala zápis v deníku Biskupky jako důkaz, že byla odpojena od myceliární sítě.',
                elphi_dissection: 'Dr. Elphi věří, že houbový výrůstek uvnitř Biskupky byl symbiont. Vrah mohl mířit na samotného symbionta.',
                elphi_berries: 'Dr. Elphi identifikovala Mručenky jako kořeněnou odrůdu — specialitu Lumen Direktoriátu.',
                elphi_lumen_lead: 'Dr. Elphi navrhla promluvit s Lumen Direktoriátem. Prodávají kořeněné Mručenky.',
                elphi_day1_complete: 'Probral jsem všechny stopy s Dr. Elphi. Pracuje na opravě kazety Kardinálské Hostiny.',
            }
        },
        the_three_vestigels: {
            title: 'Tři Vestigely',
            description: 'Kloor Venn chce, abych našel jeden ze tří Vestigelů na trhu. Zmínil, že jeden má obchodnice jménem Zerren.',
            updates: {
                found_eskola_lead: 'Zerren prozradila, že plyšovou hračku obsahující Vestigel koupil Edgar Eskola.',
                completed: 'Dal jsem vestigel Klooru Vennovi výměnou za informace o Biskupce.',
                edgar_vestigel_acquired: 'Dostal jsem vestigel od Edgara Eskoly výměnou za pomoc s jeho knihou.',
                edgar_book_trade: 'Edgar Eskola by vyměnil Vestigel za vaši pomoc s jeho knihou.',
            }
        },
        find_lumen_directorate: {
            title: 'Nic skrytého. Nic ztraceného',
            description: 'Kapitán Liris mi dal pokyny k sídlu Lumen Direktoriátu. Měl bych je navštívit, dozvědět se víc o jejich práci a zjistit, jestli se mohu připojit k jejich posádce.',
            updates: {
                gardener_directions: 'Zahradník Verrik mě nasměroval ke Korektoru Úhlu ve třetím patře Direktoriátu.',
            }
        },
        find_rust_choir: {
            title: 'Najít Rezavý Chór',
            description: 'Musím najít způsob, jak se setkat s Rezavým Chórem, který sídlí v horních patrech budovy Škrabáku.',
            updates: {
                talk_to_ravla: 'Měl bych nejdřív promluvit s Ravlou v hospodě Křičící Korek.',
                talked_to_ravla: 'Ravla v Křičícím Koreku chce, abych připravil hostinu pro stroje Rezavého Chóru jako důkaz mého odhodlání.',
                feast_complete: 'Rezavá Hostina je hotová. Ravla mi dala heslo pro Matku Výtahu: „Koroduj". Teď mohu vstoupit do domény Rezavého Chóru.',
                feast_delivered: 'Doručil jsem Rezavou Hostinu Brukkovi v Rezavé Doméně.',
            }
        },
        rust_feast: {
            title: 'Rezavá Hostina',
            description: 'Připravit hostinu pro stroje Rezavého Chóru sesbíráním oleje, kovu a živé rudé hmoty, a přinést vše Ravle do Křičícího Koreku.',
            updates: {
                talked_to_archeologist_hint: 'Ravla navrhla, abych promluvil s archeologem u radnice a dozvěděl se víc o rudé hmotě.',
                gathered_rust_materials_hint: 'Ravla mi poradila hledat šrot kolem Škrabáku... a zkontrolovat doky u Žloutkového Moře nebo Deltu Ozvěnového Odpadu kvůli oleji.',
                redmass_spared: 'Našel jsem živou rudou hmotu na ostrově v Deltě Ozvěnového Odpadu, ale rozhodl jsem se ji ušetřit.',
                redmass_collected: 'Sebral jsem živou rudou hmotu z ostrova v Deltě Ozvěnového Odpadu.',
                magnekin_tip: 'Podivný tvor, který se identifikuje jako Magnekin, mi řekl, že nějaké kovové šroty se dají najít v Deltě Ozvěnového Odpadu.',
                learned_rust_cluster_location: 'Phor Calesta mi řekl, že rudá hmota se nachází v údržbových chodbách Skladu 521.',
            }
        },
        rust_reclamation: {
            title: 'Rezavá Reklamace',
            description: 'Gnur potřebuje pomoc s vyzvednutím „živého jádra" z nepoužívaných tunelů Skladu 521, někde za opuštěnou kanceláří.',
            updates: {
                promise_made: 'Slíbil jsem úředníkovi ve Skladu 521, že si nebudu zahrávat s živým jádrem.',
                core_delivered: 'Dal jsem Gnurovi živé jádro. Zdá se spokojený.',
                quest_refused: 'Odmítl jsem Gnurovi pomoct ukrást živé jádro poté, co jsem se dozvěděl o jeho důležitosti.',
            }
        },
        ortolan_arms: {
            title: 'Ruce navíc pro Ortolana',
            description: 'Pomozte Ortolanovi, návrháři deskových her, projít byrokracií Skladu a získat povolení pro další pár rukou.',
            updates: {
                deformity_form_clue: 'Úředník mi řekl jít na Registrační úřad pro Formulář Zděděné Deformity.',
                forge_documents_suggestion: 'Když jsem úředníkovi navrhl padělat dokumenty pro Ortolana, podíval se na mě směsí překvapení a podráždění.',
                artisan_form_clue: 'Úředník mi řekl jít na Registrační úřad pro Formulář Řemeslnické Výjimky.',
                nonverbal_gesture_clue: 'Úředník mi řekl jít na Registrační úřad a udělat co nejlepší neverbální gesto.',
                ravla_forger_hint: 'Heliodor v Křičícím Koreku zmínil, že Ravla je zkušená padělatelka dokumentů.',
                ravla_forger_agreement: 'Ravla v Křičícím Koreku může padělat Formulář Řemeslnické Výjimky pro Ortolana, ale chce za práci 50 dinárů.',
                document_obtained: 'Získali jste padělaný Formulář Řemeslnické Výjimky od Ravly. Doručte ho Ortolanovi na Nádvoří Skladu.',
                bureaucratic_incantation: 'Dutá Žena ve frontě na registraci mě naučila podivné byrokratické zaklínadlo.',
                form_obtained: 'Úspěšně jsem získal formulář pro Ortolana.',
                partial_progress: 'Získal jsem Dočasné Povolení, které by mohlo Ortolanovi pomoct, ale není plně schválené.',
                failed_attempt: 'Můj pokus o registraci selhal. Budu muset najít jiný způsob, jak Ortolanovi pomoct.',
                completed: 'Pomohl jsem Ortolanovi získat povolení pro ruce navíc.',
            }
        },
        excavation_permit: {
            title: 'Divinografie',
            description: 'Měl bych pomoct Phor Calestovi získat vykopávkové povolení pro Božský Hřbitov na radnici. Nejdřív se musím nějak dostat dovnitř radnice.',
        },
        enter_townhall: {
            title: 'Vstoupit na Radnici',
            description: 'Radnice je zavřená a nikdo neví proč. Musím najít způsob, jak se dostat dovnitř — zpráva o dvojníkovi Biskupky tam byla podána a Phor Calesta také potřebuje přístup. Možná někdo ve městě ví, jak se dostat dovnitř.',
            updates: {
                gardener_seldo_tip: 'Zahradník Verrik u Lumen Direktoriátu navrhl, abych promluvil se Seldem Třikrát-Korigovaným uvnitř.',
                ac_seldo_referral: 'Korektor Úhlu mě nasměroval k Seldovi Třikrát-Korigovanému ve druhém patře.',
            }
        },
        level_177_access: {
            title: 'Přístup na Úroveň 177',
            description: 'Musím získat přístup do studia Dr. Elphi Quarnové v patře 177-Ticho v budově Škrabáku.',
        },
        edgar_book: {
            title: 'Pomoct Edgarovi napsat knihu',
            description: 'Edgar Eskola zmínil, že chce napsat knihu. Měl bych mu pomoct.',
            updates: {
                completed: 'Pomohli jste Edgaru Eskolovi rozvinout koncept jeho knihy. Je vám velmi vděčný.',
            }
        },
    }
};
