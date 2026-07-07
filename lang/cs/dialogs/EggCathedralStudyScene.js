/**
 * Czech dialog translations for EggCathedralStudyScene (the Bishop's study + her journal)
 */
export default {
    _speakers: {
        'Narrator': 'Vypravěč',
        "The Bishop's Journal": 'Deník biskupky',
    },

    journal_intro: {
        text: {
            first: "Přímo ze živé stěny vyrůstá stůl, jeho letokruhy jsou napůl dřevo a napůl cosi, co pulzuje. Svitky na něm jsou obalené průhlednou ochrannou membránou; svíce dohořívají a nikdy neuhasnou, katedrála je sama udržuje. Tohle bylo poslední místo, kde byla ještě celá sebou.\n\nPod membránou, známým rukopisem, leží zbytek biskupčina deníku.",
            read: "Biskupčin deník leží otevřený, jak jsi ho nechal, membrána stažená, svíce dál opatrované katedrálou. Její poslední slova čekají, kdybys je chtěl číst znovu."
        },
        options: {
            journal_read: "Přečíst.",
            journal_leave: "Nech to být."
        }
    },

    journal_1: {
        text: "*První záznam.*\n\n„Dnes jsem slyšela zpěv v místech, kde žádný hlas být nemůže. Kněží tvrdí, že je to bůh, který odpovídá. Ale já se obávám, že to není odpověď.\n\nJe to otázka.\"",
        options: { journal_1_next: "Obrátit list." }
    },
    journal_2: {
        text: "„Stěny se změnily. Ne jako se mění stavba. Jako když se tělo učí vlastnímu tvaru.\n\nTeď už chápu: katedrála nebyla postavena kolem vejce. Katedrála je způsob, jakým se vejce snaží pochopit svět.\"",
        options: { journal_2_next: "Obrátit list." }
    },
    journal_3: {
        text: "„Dnes jsem viděla něco, co mě vyděsilo víc než samotné vejce. Stroj bez duše začal projevovat soucit. A bytost, která měla být bohem, začala hledat odpovědi.\n\nNejsou pán a nástroj. Jsou dvě vznikající věci a každá z nich změnila tu druhou.\"",
        options: { journal_3_next: "Obrátit list." }
    },
    journal_4: {
        text: "„Jestli tohle někdo najde, vězte jedno.\n\nNevolám vás sem, abyste to zničili. A nevolám vás sem, abyste se tomu klaněli.\n\nVolám vás, protože poprvé v dějinách našeho světa vzniklo něco, co nemá místo, kam by patřilo.\"",
        options: { journal_4_next: "Obrátit list." }
    },
    journal_5: {
        text: "*Poslední záznam.*\n\n„Guardian mě neposlechl proto, že jsem jeho vládkyně. Poslechl mě, protože pochopil můj strach.\n\nAle strach není důvod, aby něco bylo navěky. Získala jsem, co času šlo. Zbytek není na mně, abych rozhodla.\n\nJe na tobě.\"",
        options: { journal_close: "Zavřít deník." }
    }
};
