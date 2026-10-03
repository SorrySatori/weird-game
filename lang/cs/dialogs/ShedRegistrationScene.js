/**
 * Czech dialog translations for ShedRegistrationScene
 * Speakers: Sleepless Mime, Vowel Seller, Hollow Woman, Senior Clerk
 * Register: the clerk and the player use vykání; the dream-queue figures tykají the player
 * (the mime is childlike, the seller and the Hollow Woman are older); the player vyká the seller
 * and the Hollow Woman, tyká the mime. The narrator tyká.
 */
export default {
    _speakers: {
        'Sleepless Mime': 'Nevyspalý mim',
        'Vowel Seller': 'Prodavač samohlásek',
        'Hollow Woman': 'Dutá žena',
        'Senior Clerk': 'Vrchní úředník',
    },
    // ---------- Sleepless Mime ----------
    sleeplessMime_start: {
        text: "(Tvor tě upřeně pozoruje. V duchu si ho pojmenuješ Nevyspalý mim. Jeho rezavějící maska zachytává tlumené světlo. Mlčky napodobí tvůj postoj a pak rukama naznačí tvar krychle – jako hrací kostku. Předvádí, jak ji držíš v ruce.)",
        options: {
            hi_who_are_you_i_used_to_play_like_this_as_well_wh: "Ahoj, kdo jsi? Takhle jsem si taky hrával, když jsem byl malý.",
            err_i_am_at_the_right_place_can_you_help_my_friend: "Ehm... jsem tu správně? Můžeš mému kamarádovi pomoct s registrací rukou navíc?"
        }
    },
    sleeplessMime_memory: {
        text: "(Mim nadšeně přikývne. Jeho ruce začnou ve vzduchu splétat vzor a vyvolávat přízračné herní figurky. Na okamžik cítíš, jak se propadáš do vzpomínky...)",
        options: { remember: "Vzpomínat..." }
    },
    sleeplessMime_memory_scene: {
        text: "(Vybaví se ti hra z dětství. Kostky z kostí, karty pomalované symboly, které se měnily, když se nikdo nedíval. Pravidla byla každou chvíli jiná, a přesto jsi vždycky věděl, jak hrát. Vzpomínka vybledne, ale v hlavě po ní zůstane hřejivé světlo.)",
        options: { thank_you_for_reminding_me: "Díky, že jsi mi to připomněl." }
    },
    sleeplessMime_ortolan: {
        text: "(Mim horlivě přikyvuje. Sáhne do kapsy a vytáhne potrhaný útržek papíru. Vtiskne ti ho do dlaně – vypadá to na stránku z nějakých pravidel. Snad... kousek pravidel deskové hry?)",
        options: { read_the_fragment: "Přečíst útržek" }
    },
    sleeplessMime_rulebook: {
        text: "„...a když se na kostce otevře třetí oko, každý hráč si vymění jednu vzpomínku s hráčem po své levici. Pokud vzpomínky nemůže ověřit Svědek, výměna je neplatná a oba hráči získávají žeton Pochybnosti...“",
        options: { err_thank_you_i_guess: "Ehm... Děkuju... asi." }
    },
    sleeplessMime_end: {
        text: "(Mim se hluboce ukloní a rozplyne se ve snovém oparu fronty.)",
        options: {
            continue_waiting: "Čekat dál",
            finally_i_hate_mimes: "No konečně. Nesnáším mimy."
        }
    },
    // ---------- Vowel Seller ----------
    vowelSeller_start: {
        text: "(Postava pokrytá popelem se k tobě otočí; v kapsách kabátu jí cinkají drobné skleněné lahvičky. V každé plave zářící písmeno.)\n\n„Prodávám samohlásky. Jestli chceš, aby tvoje jméno něco znamenalo, budeš nějakou potřebovat.“\n\nZvedne lahvičku, v níž pulzuje písmeno A.",
        options: {
            ill_buy_one: "Jednu si koupím.",
            keep_your_vowels_i_speak_in_spore_alphabet: "Nechte si svoje samohlásky. Mluvím řečí hub."
        }
    },
    vowelSeller_buy: {
        text: "„Chytrá volba. Cena je drobná vzpomínka. Něco malého... třeba chuť tvého prvního jídla v tomhle městě?“\n\n(Odzátkuje lahvičku. Samohláska se vznese, chvíli se vznáší před tebou a pak ti vklouzne do úst. Cítíš podivné chvění – samohláska se snaží najít své místo ve tvém jméně. Je to jako... a... a... a... Jenže o jméno jsi přišel v den, kdy jsi vstoupil do kultu Obazoba. A na chuť svého prvního jídla v tomhle městě si taky nevzpomínáš – těžko říct, jestli kvůli tomu obchodu, nebo protože jsi tu ještě nic nejedl.)",
        options: { thank_you_but_you_know_we_have_no_names_i_am_just_: "Děkuju. Ale víte, my jména nemáme. Jsem jen číslo. Pardon, měl jsem to říct dřív." }
    },
    vowelSeller_spores: {
        text: "(Oči se mu maličko rozšíří.)\n\n„Houbový jazyk... chápu. Pak by se ti možná víc hodilo tohle.“\n\n(Podá ti malou kartičku, na které nic není.)\n\n„Tichá věta. Použij ji, až ti během byrokratického řízení dojdou slova.“",
        options: { i_accept_this_gift: "Přijímám váš dar." }
    },
    vowelSeller_end: {
        text: "(Prodavač samohlásek přikývne a rozpadne se v oblak popela. Lahvičky ještě tiše cinkají, když mizí.)",
        options: { continue_waiting: "Čekat dál" }
    },
    // ---------- Hollow Woman ----------
    hollowWoman_start: {
        text: "(Žena s prázdnými očima a zašitými jizvami se ti lehce opře o rameno. Je ji sotva slyšet.)\n\n„Pořád to samé. Za mých časů jsem na registraci čekala taky. Jenže úředník nikdy nepřišel. Tak jsem tu navěky. A čekám...“\n\n(Všimneš si, že její levá paže končí v lokti, okraje úhledně zašité.)",
        options: {
            do_you_remember_what_you_have_waited_for: "Vzpomínáte si, na co jste čekala?",
            well_i_guess_you_should_stop_waiting_i_am_sure_you: "No, asi byste měla přestat čekat. Určitě máte na práci lepší věci."
        }
    },
    hollowWoman_hands: {
        text: "„Někdy skoro... ve snech. Myslím, že jsem uměla vyplňovat formuláře. Oddíl 7-B byl moje specialita.“\n\n(Pošeptá ti do ucha podivné byrokratické zaklínadlo.)\n\n„Pamatuj si to, až budeš mluvit s úředníkem. Určitě se to na něco hodí... tím jsem si jistá.“",
        options: { ill_remember_sure_thank_you_ehm_strange_waiting_pe: "Zapamatuju si to. Jasně. Děkuju... ehm, podivná čekající paní." }
    },
    hollowWoman_offer: {
        text: "(Její prázdné oči se maličko rozšíří.)\n\n„Symbolický dar... laskavost. Už je to dlouho, moc dlouho, co mi někdo projevil takovou laskavost.“\n\n(Dotkne se tvé ruky a na okamžik cítíš zvláštní spojení, jako by mezi vámi něco proudilo.)",
        options: { uhm_what_are_you_doing_madame: "Ehm, co to děláte, madam?" }
    },
    hollowWoman_end: {
        text: "(Dutá žena o krok ustoupí, na sešívané tváři slabý úsměv. Pomalu se vytrácí, až po ní nezůstane nic než vzpomínka na její přítomnost.)",
        options: { continue_waiting: "Čekat dál" }
    },
    // ---------- Senior Clerk ----------
    seniorClerk_start: {
        text: "(Najednou se objeví vrchní úředník a s mechanickou přesností urovnává štos papírů. Hlas má kovový.)\n\n„Úsek fronty F-7 byl zpracován. Vaše přítomnost byla zaznamenána a vaše interakce zkatalogizovány.“\n\n(Nahlédne do desek.)\n\n„Uveďte účel návštěvy.“",
        options: {
            i_need_to_register_for: "Potřebuji se zaregistrovat kvůli...",
            what_happened_to_those_people_i_was_talking_to: "Co se stalo s těmi lidmi, se kterými jsem mluvil?"
        }
    },
    seniorClerk_register: {
        text: "„Registrace vyžaduje formulář 27-B/6, podaný v trojím vyhotovení spolu s osvědčením o rovnováze růstu a rozkladu.“\n\n(Vyčkávavě se na tebe podívá, pak si povzdechne.)\n\n„Vidím však, že vás... ovlivnili obyvatelé fronty. Dobrá. Vaše vyřízení urychlím.“",
        options: { thank_you: "Děkuji." }
    },
    seniorClerk_people: {
        text: "(Úředníkův výraz se nezmění.)\n\n„S lidmi? Žádní lidé tu nebyli. Jen projevy fronty samotné. Ozvěny těch, kdo čekali příliš dlouho. Vstřebal jste jejich podstatu – jejich příběhy jsou teď součástí vašeho řízení.“\n\n(Poklepe na desky.)\n\n„Značně nestandardní, ale budeme pokračovat.“",
        options: { i_see: "Aha..." }
    },
    seniorClerk_processing: {
        text: "„Na základě vašich interakcí ve frontě byla vaše přítomnost zde...“\n\n(S rozmachem orazítkuje formulář.)\n\n„...schválena. Můžete přejít k samotné registraci. Začneme registračním obřadem.“",
        options: { proceed_to_the_registration_office: "Přejít k registraci" }
    },
    registration_start: {
        text: "„Než budeme pokračovat, potřebuji znát účel vaší registrace. Co vás dnes přivádí do Kůlny 521?“",
        options: {
            im_here_for_general_registration: "Přišel jsem na obecnou registraci.",
            id_rather_not_say: "Raději bych si to nechal pro sebe.",
            i_need_an_artisans_exemption_form: "Potřebuji Formulář o výjimce pro umělce.",
            i_need_an_inherited_deformity_form: "Potřebuji Formulář o zděděné deformitě.",
            make_a_nonverbal_gesture: "(Udělat nonverbální gesto)",
            i_would_like_to_register_for_an_extra_symbiont_slo: "Chtěl bych si zaregistrovat další slot pro symbionta."
        }
    },
    registration_artisan: {
        text: "„Ach, Formulář o výjimce pro umělce. Vzácný požadavek.“",
        options: {
            its_for_ortolan_a_board_game_designer: "Je pro Ortolana, návrháře deskových her.",
            i_need_it_for_personal_reasons: "Potřebuji ho z osobních důvodů."
        }
    },
    registration_artisan_ortolan: {
        text: "(Úředník nepatrně zvedne obočí.)\n\n„Ortolan? Ten návrhář her? Zajímavé...“\n\n(Prohrabe se papíry a vytáhne složitý formulář pokrytý spletitými vzory.)\n\n„Tento formulář vyžaduje tvůrčí ověření. Prokažte prosím umělecké nadání.“",
        options: {
            i_can_demonstrate_my_creativity: "Svou tvořivost mohu prokázat.",
            perhaps_another_form_would_be_better: "Možná by se hodil jiný formulář."
        }
    },
    registration_artisan_personal: {
        text: "„Osobní důvody pro tento formulář nestačí. Vyžaduje doložený tvůrčí výstup.“",
        options: {
            i_can_demonstrate_my_creativity: "Svou tvořivost mohu prokázat.",
            perhaps_another_form_would_be_better: "Možná by se hodil jiný formulář."
        }
    },
    registration_creative_challenge: {
        text: "„Dobrá. Doplňte prosím tento vzor.“",
        options: {
            show_the_rulebook_fragment: "(Ukázat útržek pravidel)",
            recite_the_bureaucratic_incantation: "(Odříkat byrokratické zaklínadlo)",
            draw_a_fungal_pattern: "(Nakreslit houbový vzor)",
            i_cant_do_this: "To nedokážu."
        }
    },
    registration_deformity: {
        text: "„Formulář o zděděné deformitě? To je citlivý dokument.“",
        options: {
            its_for_a_friend_with_multiple_arms: "Je pro přítele s více rukama.",
            i_need_to_understand_the_classification_system: "Potřebuji porozumět klasifikačnímu systému."
        }
    },
    registration_deformity_friend: {
        text: "„Více rukou? Zajímavé. Formulář vyžaduje doklad, že jde o prospěšnou mutaci, a ne o škodlivou deformitu.“",
        options: {
            recite_the_bureaucratic_incantation_to_bypass_the_: "(Odříkat byrokratické zaklínadlo a obejít tak klauzuli)",
            sure_thing_i_have_a_lot_of_experience_with_benefic: "Jistě, s prospěšnými mutacemi mám bohaté zkušenosti, stačí se podívat na moje tělo.",
            show_the_rulebook_fragment: "(Ukázat útržek pravidel)",
            i_dont_have_proof: "Žádný doklad nemám."
        }
    },
    registration_deformity_system: {
        text: "„Klasifikační systém je složitý. Vyžaduje odborné znalosti.“",
        options: {
            i_have_some_experience_with_bureaucracy: "S byrokracií nějaké zkušenosti mám.",
            perhaps_i_should_try_a_different_approach: "Možná bych to měl zkusit jinak."
        }
    },
    registration_bureaucracy_challenge: {
        text: "„Prokažte, že rozumíte oddílu 7-B formuláře.“",
        options: {
            section_7b_relates_to_the_inherited_deformity_clau: "Oddíl 7-B se týká klauzule o zděděné deformitě, kterou lze s řádnou dokumentací obejít.",
            section_7b_covers_beneficial_mutations: "Oddíl 7-B pojednává o prospěšných mutacích.",
            im_not_familiar_with_section_7b: "Oddíl 7-B neznám."
        }
    },
    registration_nonverbal: {
        text: "(Úředník tvé gesto se zájmem sleduje.)\n\n„Ach, nonverbální komunikace. V byrokracii vzácný přístup.“",
        options: {
            mime_a_complex_game_being_played: "(Předvést pantomimou složitou hru)",
            present_the_silent_sentence_card: "(Předložit kartičku s Tichou větou)",
            i_cant_do_this_i_am_not_a_mime_or_a_very_bad_one: "To nedokážu. Nejsem mim. Nebo jsem hodně špatný."
        }
    },
    registration_general: {
        text: "„Obecná registrace vyžaduje konkrétní účel. Kůlna 521 nepřijímá návštěvníky bez účelu.“",
        options: {
            i_would_like_to_register_for_extra_symbiont_slot: "Chtěl bych se zaregistrovat na další slot pro symbionta.",
            im_here_on_behalf_of_someone_else: "Jsem tu za někoho jiného.",
            perhaps_i_should_be_more_specific: "Asi bych měl být konkrétnější."
        }
    },
    registration_proxy: {
        text: "„Registrace v zastoupení se nepřijímá. Žadatel se musí dostavit osobně – nebo musíte mít formulář vystavený na jeho jméno.“",
        options: { understood: "Rozumím." }
    },
    registration_extra_symbiont: {
        text: "„Registrace dalšího slotu pro symbionta není nijak složitá. Jen jeden formulář. A samozřejmě registrační poplatek 50 dinárů.“",
        options: {
            ill_pay_the_fee_and_register_for_an_extra_slot: "Zaplatím poplatek a zaregistruji si další slot.",
            i_change_my_mind_i_would_like_to_register_for_some: "Rozmyslel jsem si to. Chtěl bych se zaregistrovat na něco jiného.",
            sorry_i_dont_think_i_can_pay_the_fee: "Promiňte, ten poplatek asi nezaplatím."
        }
    },
    registration_extra_symbiont_pay: {
        text: "„Dobrá. Zpracuji vaši platbu a aktualizuji vaši registraci.“",
        options: { thank_you: "Děkuji." }
    },
    registration_extra_symbiont_complete: {
        text: {
            success: "„Vaše registrace je hotová. Máte k dispozici další slot pro symbionta. Dobře zvažte, jaké bytosti budete hostit.“",
            max_reached: "„Omlouvám se, ale podle všeho už máte nejvyšší počet slotů pro symbionty, jaký předpisy povolují. Platbu jsem vám vrátil.“",
            no_money: "„Je mi líto, ale na tuto transakci podle všeho nemáte dostatek prostředků. Poplatek činí 50 dinárů.“"
        },
        options: { thank_you: "Děkuji." }
    },
    registration_evasive: {
        text: "(Úředníkův výraz ztuhne.)\n\n„Vyhýbavost se zapisuje do spisu. To celý proces komplikuje.“",
        options: { i_apologize_let_me_be_more_specific: "Omlouvám se. Budu konkrétnější." }
    },
    registration_reconsider: {
        text: "„Dobrá. Začneme znovu.“",
        options: { continue: "Pokračovat" }
    },
    registration_success_artisan: {
        text: "(Úředník s rozmachem orazítkuje Formulář o výjimce pro umělce.)\n\n„Schváleno. Formulář uděluje tvůrčí výjimku ze standardních omezení počtu končetin. Ortolan bude mít radost.“",
        options: { thank_you: "Děkuji." }
    },
    registration_success_deformity: {
        text: "(Úředník precizně orazítkuje Formulář o zděděné deformitě.)\n\n„Schváleno. Tento formulář uznává více končetin za prospěšnou mutaci. Vzácná klasifikace.“",
        options: { thank_you: "Děkuji." }
    },
    registration_success_nonverbal: {
        text: "(Úředník s nečekaným pochopením přikývne.)\n\n„Vaše nonverbální žádost je... schválena. Tento zvláštní dispens umožňuje úpravu končetin bez standardní dokumentace.“",
        options: { nod_gratefully: "(Vděčně pokývnout)" }
    },
    registration_partial_success: {
        text: "(Úředník zaváhá, pak formulář označí prozatímním razítkem.)\n\n„Schváleno částečně. Toto dočasné povolení uděluje omezený přístup. Plné schválení bude vyžadovat další dokumentaci.“",
        options: { i_understand: "Rozumím." }
    },
    registration_failure: {
        text: "(Úředník s konečnou platností otiskne na formulář razítko ZAMÍTNUTO.)\n\n„Vaše žádost se zamítá. Nedostatečná kvalifikace, dokumentace nebo účel. Znovu můžete žádat po standardní čekací lhůtě 47 trávení.“",
        options: { i_see: "Aha..." }
    },
    registration_complete_success: {
        text: "(Vrchní úředník ukáže ke dveřím.) Registrace je u konce. Opusťte prosím mou kancelář. Hezký den.",
        options: { thank_you: "Děkuji." }
    },
    registration_complete_partial: {
        text: "(Vrchní úředník ukáže ke dveřím.) Registrace je u konce. Opusťte prosím mou kancelář. Hezký den.",
        options: { thank_you: "Děkuji." }
    },
    registration_complete_failure: {
        text: "(Vrchní úředník ukáže ke dveřím.) Tato záležitost je uzavřena. Opusťte prosím mou kancelář.",
        options: { thank_you: "Děkuji." }
    },
    seniorClerk_end: {
        text: "(Vrchní úředník se vrátí ke svým papírům, jako by na tebe v tu chvíli zapomněl.)"
    },
    seniorClerk_returning: {
        text: "(Vrchní úředník vzhlédne od papírů.) „Á, zase vy. Jaké registrační služby si dnes přejete?“",
        options: { id_like_to_discuss_registration_options: "Chtěl bych probrat možnosti registrace." }
    },
    end: {
        text: ""
    }
};
