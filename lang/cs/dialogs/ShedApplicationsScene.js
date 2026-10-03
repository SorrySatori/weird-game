/**
 * Czech dialog translations for ShedApplicationsScene
 * Speaker: Clerk (Úředník) — pedantic bureaucrat; he and the player vykají each other.
 */
export default {
    _speakers: {
        'Clerk': 'Úředník',
    },
    start: {
        text: "(Úředník se probírá hromadou papírů a sotva zvedne oči)\nVítejte v kanceláři Žádostí Kůlny 521. Formuláře ve třech vyhotoveních, prosím. Bez výjimek.",
        options: {
            tell_me_about_shed521: "Povězte mi o Kůlně 521",
            whats_your_role_here: "Co tady máte na starosti?",
            what_do_you_know_about_the_living_core: "Co víte o živém jádru?",
            how_can_i_register_for_extra_pair_of_arms: "Jak si můžu zaregistrovat další pár rukou?"
        }
    },
    about_shed: {
        text: "Kůlna 521? (upraví si brýle) Jedno z našich nej... produktivnějších zařízení. Bývalo to obyčejné skladiště, víte. Ale dnes... je to mnohem víc. Místo, kde se... dějí věci. (usměje se) Byrokracie tu opravdu žije, plyne jako řeka. Dává věcem smysl – každému kroku, každému rozhodnutí. (odloží papíry) Dokážeme tu být tak produktivní a šťastní.",
        options: {
            that_sounds_like_a_lot_of_paperwork: "To zní jako spousta papírování",
            back_to_other_topics: "Zeptej se na něco jiného"
        }
    },
    clerk_role: {
        text: "Udržuji řád v chaosu. Každá augmentace, každý experiment, každý... incident musí být řádně zdokumentován. Byrokracie musí plynout, jak se říká. (urovná dokonale srovnaný štos papírů)",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    paperwork: {
        text: "Skutečně. (oči se mu rozzáří) Víte, že máme sedmnáct různých formulářů jen na žádost o nový formulář? Řádná dokumentace je to, co nás odlišuje od divochů z pustin.",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    living_core_inquiry: {
        text: "(Úředník přimhouří oči) Živé jádro? (ztiší hlas) Poslouchejte dobře. Ta technologie spadá pod Protokol 7B, odstavec 13. (rozhlédne se) Proč se ptáte?",
        options: {
            gnur_asked_me_to_retrieve_it: "Gnur mě požádal, abych ho přinesl",
            i_am_just_interested_in_such_technology: "Jen mě taková technologie zajímá.",
            back_to_other_topics: "Zeptej se na něco jiného"
        }
    },
    lie_living_core: {
        text: "(Nesouhlasně urovná papíry) Dobrá. Ale pamatujte – předpisy existují z dobrého důvodu. Ať vás ani nenapadne na živé jádro sahat. Lidé si většinou myslí, že je to jen relikt, ale pro energetický chod Kůlny je zásadní.",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    expose_gnur: {
        text: "Já to věděl! Děkuji, že jste mi to řekl. (usměje se) Ta pakáž z Rezavého chóru nemá na takovou technologii žádné právo. (odloží papíry) Slibte mi prosím, že na živé jádro nebudete sahat.",
        options: {
            i_promise_to_leave_it_alone: "Slibuji, že ho nechám být",
            ill_think_about_it: "Rozmyslím si to"
        }
    },
    promise_made: {
        text: "(Viditelně se mu uleví) Dobře... dobře. Dřeňoví reklamátoři si to budou pamatovat. Co vám Gnur za to živé jádro slíbil?",
        options: {
            he_promised_me_a_to_tell_where_to_find_the_bishop: "Slíbil, že mi řekne, kde najdu Biskupku",
            sorry_but_thats_private_information: "Promiňte, to je soukromá věc",
            who_are_the_pith_reclaimers: "Kdo jsou Dřeňoví reklamátoři?"
        }
    },
    bishop_location: {
        text: "Biskupka? Hm... Kde je, vám říct nemůžu. Ale poptejte se po Edgaru Eskolovi v hospodě Řvoucí korek. Myslím, že by mohl něco vědět.",
        options: {
            back_to_other_topics: "Zeptej se na něco jiného",
            who_are_the_pith_reclaimers: "Kdo jsou Dřeňoví reklamátoři?",
            who_is_edgar_eskola: "Kdo je Edgar Eskola?"
        }
    },
    private: {
        text: "Rozumím, v pořádku. Mohu vám pomoct s něčím dalším?",
        options: {
            back_to_other_topics: "Zeptej se na něco jiného",
            who_are_the_pith_reclaimers: "Kdo jsou Dřeňoví reklamátoři?"
        }
    },
    pith_reclaimers: {
        text: "Dřeňoví reklamátoři jsou... strážci neutrality. Udržujeme ve městě mír a pořádek. Někteří z nás sbírají... jedinečné předměty, ale neprodáváme je.",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    edgar: {
        text: "Edgar Eskola? (zvedne obočí) Je to jeden z mišutkennů. Slyšel jste o nich? Napůl medvědí vnímající humanoidi s prořídlou srstí, hluboko posazenýma jantarovýma očima a tělem, které reaguje na sny. Většinou mírné duše, ale umějí být... nevyzpytatelní.",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    no_promise: {
        text: "(Nesouhlasně urovná papíry) Dobrá. Ale pamatujte – předpisy existují z dobrého důvodu.",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    ortolan_inquiry: {
        text: "Ruce navíc? (prohrabuje se papíry) Další ruce, říkáte. Jsou záměrné?",
        options: {
            my_friend_needs_them_hes_an_artisan: "Potřebuje je můj přítel. Je umělec.",
            my_friend_didnt_choose_this_the_arms_were_a_gift: "Můj přítel si to nevybral. Ty ruce byly... dar.",
            theyre_not_his_arms_hes_borrowing_them: "Nejsou jeho. Má je jen půjčené.",
            back_to_other_topics: "Zeptej se na něco jiného"
        }
    },
    ortolan_borrow: {
        text: "Pak přechovává tělesného uprchlíka. Budu potřebovat Podpis o souhlasu nepřítomného. Od původního majitele.",
        options: {
            back_to_other_topics: "Zeptej se na něco jiného",
            fine_ill_lie_or_forge_the_documents: "Fajn. Tak zalžu. Nebo zfalšuju papíry?",
            uhh_sorry_i_mean_he_needs_them_hes_an_artisan: "Ehm... promiňte, chtěl jsem říct, že je potřebuje. Je umělec.",
            well_i_was_just_joking_of_course_they_are_his_but_: "No, jen jsem žertoval. Samozřejmě jsou jeho. Ale nevybral si to. Ty ruce byly... dar."
        }
    },
    ortolan_gift: {
        text: "Nevyžádané končetiny podléhají dani tak jako tak. Ale možná to můžeme podat jako zděděnou deformitu.",
        options: {
            can_you_process_it_today: "Můžete to vyřídit ještě dnes?",
            fine_ill_lie_or_forge_the_documents: "Fajn. Tak zalžu. Nebo zfalšuju papíry?"
        }
    },
    ortolan_today: {
        text: "Bez povolení z registračního úřadu ne. Zajděte tam a požádejte o Formulář o zděděné deformitě.",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    ortolan_lie: {
        text: "Budu dělat, že jsem to neslyšel.",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    ortolan_artisan: {
        text: "Umění není obhajoba proti anatomii. Ale Formulář o výjimce pro umělce máme. Ovšem minulý cyklus propadl.",
        options: {
            can_it_be_renewed: "Dá se obnovit?",
            what_if_i_find_another_copy: "A co když seženu jinou kopii?",
            forget_the_form_what_else_can_i_offer: "Na formulář zapomeňte. Co jiného můžu nabídnout?",
            back_to_other_topics: "Zeptej se na něco jiného"
        }
    },
    ortolan_renew: {
        text: "Jedině představením. Zeptejte se na registračním úřadě.",
        options: { back_to_other_topics: "Zeptej se na něco jiného" }
    },
    ortolan_copy: {
        text: "Jste hluchý? Ptám se, jestli jste hluchý. Minulý cyklus propadl.",
        options: {
            back_to_other_topics: "Zeptej se na něco jiného",
            can_it_be_renewed: "Dá se obnovit?",
            forget_the_form_what_else_can_i_offer: "Na formulář zapomeňte. Co jiného můžu nabídnout?"
        }
    },
    ortolan_offer: {
        text: "Gesto. Symbolické. Neverbální. Zajděte na registrační úřad a předveďte, co umíte.",
        options: { uh_okay_can_i_ask_for_other_topics: "Ehm... dobře. Můžu se zeptat na něco jiného?" }
    },
    end: {
        text: "Před odchodem prosím vyplňte výstupní formulář ve třech vyhotoveních."
    }
};
