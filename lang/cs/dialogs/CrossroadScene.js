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
        text: "Nacházíš podivnou, gigantickou mrtvolu. Její maso jako by pulzovalo nadpozemskou energií. Je zřejmé, že tu je už nějakou dobu, ale překvapivě vůbec nezapáchá. Co uděláš?",
        options: {
            plant_spores_in_it: 'Zasadit do ní spory (10 spor)',
            cut_it_open: 'Rozříznout ji',
            salt_recall_corpse: '[Solná paměť] Přečti, co v ní zůstalo.',
            grave_sense_corpse: '[Hrobový smysl] Přečti, jak zemřela.',
            leave_it_alone: 'Nechat ji být'
        }
    },
    corpseExhausted: {
        text: "S tou starou mrtvolou už nic víc nesvedeš. Její účel byl naplněn.",
        options: {
            salt_recall_corpse: '[Solná paměť] Přečti, co v ní zůstalo.',
            grave_sense_corpse: '[Hrobový smysl] Přečti, jak zemřela.',
            leave_it_alone: 'Nechat ji být'
        }
    },
    corpse_salt_recall: {
        text: "Solné písmo se probudí a ochutná sůl, která se kolem mrtvoly vsákla do země. *\"...Tenhle ušel dlouhou cestu. Nemanželské dítě boha Lietuse Kiky. Ne bůh – polobůh, božský levoboček. Lietus, bůh temporální zmatenosti, přišel do města zemřít a svého bastarda si vzal s sebou. Ale ve své typické zmatenosti už nestačil zařídit synovi budoucnost.\"*\n\n*\"Levoboček se pokusil město ovládnout. Stal se tyranem, až ho nakonec rozzuřený dav zlynčoval, zavraždil a nechal shnít na křižovatce. Jeho polobožské tělo ale rozkladu odolalo, a tak získalo tohle místo novou dominantu. Místní jsou na ni dnes hrdí a křižovatku bez mrtvoly poloboha si už nedokážou představit.\"*",
        options: {
            salt_recall_corpse_back: 'Ustoupit.'
        }
    },
    corpse_grave_sense: {
        text: "Osswine se probudí a přečte poslední okamžiky ohromné bytosti před tebou. *\"...Spousta násilí. Byl to levoboček boha Lietuse Kiky, který přišel do města umřít a svého syna nechal světu napospas. Zdá se, že polobůh udělal celkem slušnou kariéru jako tyran a svrchovaný vládce města, hmm. Ovšem jednoho dne tuhle jeho kariéru ukončil rozzuřený dav – smůla. Nechali tělo bastarda shnít na křižovatce, aby už žádnou božskou bytost v budoucnu nenapadlo pokusit se ovládnout Horní Morkezelu. Nevěděli ovšem, že polobožské tělo odolá zubu času a zůstane tu navěky. Pak si ale řekli, že je to ještě lepší – memento aspoň bude trvalé.\"*",
        options: {
            grave_sense_corpse_back: 'Ustoupit.'
        }
    },
    corpseReconsider: {
        text: 'Znovu se přiblížíš k podivné mrtvole. Zevnitř slyšíš povědomý hlas: "Změnil jsi názor, kámo? Pořád tu na tebe čekám."',
        options: {
            accept_thornestill_as_your_symbiont: 'Přijmout Thorne-Stilla jako svého symbionta',
            plant_spores_in_it_instead: 'Místo toho do ní zasadit spory (10 spor)',
            leave_it_alone: 'Nechat ji být'
        }
    },
    notEnoughSpores: {
        text: 'Sáhneš po svých sporách, ale na něco tak velkého jich není dost. Potřeboval bys aspoň deset.',
        options: { not_enough_spores_back: 'Ustoupit.' }
    },
    plantSpores: {
        text: 'Opatrně zasadíš spory do mrtvoly. Okamžitě se uchytí a rozšíří síť světélkujícího mycelia skrz mrtvé maso. Toto místo už nikdy nebude stejné.',
        options: {
            continue: 'Pokračovat'
        }
    },
    acceptSymbiont: {
        text: 'Když rozřízneš hlavu mrtvoly, najdeš něco mimořádného – symbiotickou entitu, která si říká Thorne-Still. "Ahoj kámo, jsem Thorne-Still. Jak ti mohu dnes pomoci?" šeptá to podivným hlasem. "Možná bychom mohli sdílet cestu na nějaký čas? Co říkáš? Ta tvoje houba vypadá dost pohodlně."',
        options: {
            accept_thornestill_as_your_symbiont: 'Přijmout Thorne-Stilla jako svého symbionta',
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
        text: '"Tvoje ztráta, kámo," šeptá symbiont. "Ale neboj, budu tady, kdybys mě potřeboval."',
        options: {
            continue: 'Pokračovat'
        }
    }
};
