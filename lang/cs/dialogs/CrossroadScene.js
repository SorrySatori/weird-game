/**
 * Czech dialog translations for CrossroadScene
 * Speaker: Giant Corpse / Thorne-Still
 */
export default {
    _speakers: {
        'Giant Corpse': 'Obří mrtvola',
        'Thorne-Still': 'Thorne-Still',
        'Osswine': 'Osswine',
    },
    corpseMain: {
        text: "Nacházíš podivnou, gigantickou mrtvolu. Její maso jako by pulzovalo nadpozemskou energií. Je zřejmé, že tu leží už nějakou dobu, ale překvapivě vůbec nezapáchá. Co uděláš?",
        options: {
            plant_spores_in_it: 'Zasadit do ní spory',
            cut_it_open: 'Rozříznout ji',
            salt_recall_corpse: '[Solná paměť] Přečti, co v ní zůstalo.',
            grave_sense_corpse: '[Hrobový smysl] Přečti, jak zemřela.',
            leave_it_alone: 'Nechat ji být'
        }
    },
    corpseExhausted: {
        text: "S mrtvoji už nemůžeš udělat nic víc. Její účel byl naplněn.",
        options: {
            salt_recall_corpse: '[Solná paměť] Přečti, co v ní zůstalo.',
            grave_sense_corpse: '[Hrobový smysl] Přečti, jak zemřela.',
            leave_it_alone: 'Nechat ji být'
        }
    },
    corpse_salt_recall: {
        text: "Solné písmo se probudí a ochutná sůl, kterou to obrovské tělo léta vyluhovalo do křižovatky. *\"...Tenhle šel dlouhou cestu, aby si lehl. Ne bůh — starší, pokornější; věc, která kdysi bohy nosila, jako cesta nosí kroky. Ucítil, jak ho město táhne, jak sem táhne všechno mrtvé, a přišel být blízko těch ostatních. Nezabila ho žádná rána. Prostě dorazil a zastavil se. Sůl pořád drží tvar toho posledního, dlouhého výdechu.\"*\n\nZbytek se zavře. *\"Teď se mu do hlavy nastěhoval rozklad. Vždycky to tak je — usadí se do místa, které po sobě zanechá účel.\"*",
        options: {
            salt_recall_corpse_back: 'Ustoupit.'
        }
    },
    corpse_grave_sense: {
        text: "Osswine se probudí v chladu té věci a čte její konec zevnitř ven. *\"...Žádné násilí. Zvolila si zastavení. Jejím posledním úmyslem nebyl strach — byl to příchod. Nosič, který ulehl u nohou všeho, co kdysi nesl, konečně rád, že smí skončit. A pod tím, slaběji: malý, trpělivý hlad, který nikdy nestihl dojíst.\"* Suchá pauza. *\"Ten nedojedený hlad je ta skulina, do níž vlezl tvůj Thorne-Still. Nic tu neumřelo s křikem. Skončilo to, jak končí dlouhý den.\"*",
        options: {
            grave_sense_corpse_back: 'Ustoupit.'
        }
    },
    corpseReconsider: {
        text: 'Znovu se přiblížíš k podivné mrtvole. Zevnitř slyšíš povědomý hlas: "Změnil jsi názor, miláčku? Pořád tu na tebe čekám."',
        options: {
            accept_thornestill_as_your_symbiont: 'Přijmout Thorne-Still jako svého symbionta',
            plant_spores_in_it_instead: 'Místo toho do ní zasadit spory',
            leave_it_alone: 'Nechat ji být'
        }
    },
    plantSpores: {
        text: 'Opatrně zasadíš spory do mrtvoly. Okamžitě se uchytí a rozšíří síť luminiscenčního mycelia skrz mrtvé maso. Toto místo už nikdy nebude stejné.',
        options: {
            continue: 'Pokračovat'
        }
    },
    acceptSymbiont: {
        text: 'Když rozřízneš hlavu mrtvoly, najdeš něco mimořádného — symbiotickou entitu, která si říká Thorne-Still. "Ahoj, miláčku, jsem Thorne-Still. Jak ti mohu dnes pomoci?" šeptá podivným hlasem. "Možná bychom mohli sdílet cestu na nějaký čas? Co říkáš? Ta tvoje houba vypadá dostatečně pohodlně i pro mě."',
        options: {
            accept_thornestill_as_your_symbiont: 'Přijmout Thorne-Still jako svého symbionta',
            decline: 'Odmítnout'
        }
    },
    acceptSymbiontConfirm: {
        text: 'Thorne-Still se spojí s tvou bytostí. Doslova ti vleze do žaludku. Cítíš jeho klidnou přítomnost ve své mysli a s ní přichází schopnost vnímat vlákna samotné reality. Nyní můžeš používat schopnost Mozková hniloba, aby byli ostatní zmatení, zapomnětliví nebo náchylní k sugesci.',
        options: {
            continue: 'Pokračovat'
        }
    },
    declineSymbiont: {
        text: '"Tvoje ztráta, miláčku," šeptá symbiont. "Ale neboj, budu tady, kdybys mě potřeboval."',
        options: {
            continue: 'Pokračovat'
        }
    }
};
