/**
 * Czech dialog translations for ShedHallScene — the Living Core in the wall. Narration only (tyká).
 */
export default {
    _speakers: {
        'Narrator': 'Vypravěč',
    },
    main: {
        text: "Živé jádro pulzuje nadpozemskou energií. Vypadá jako srostlé se zdí, ale možná by šlo vyjmout...",
        options: {
            examine_it_more_carefully: "Prohlédnout si ho pozorněji",
            use_pliers_to_carefully_extract_it: "Opatrně ho vyjmout kleštěmi",
            extract_it_forcefully: "Vyrvat ho silou",
            leave_it_alone: "Nechat ho být"
        }
    },
    examine: {
        text: "Živé jádro je do zdi vrostlé jen na několika málo místech. Se správným nástrojem, třeba kleštěmi, by možná šlo vyjmout bez poškození...",
        options: { back: "Zpět" }
    },
    force_extract: {
        text: "Vyrveš Živé jádro hrubou silou. Zdá se ti, že se v okolním prostoru jakoby ochladilo...",
        options: { continue: "Pokračovat" }
    },
    careful_extract: {
        text: "Kleštěmi Živé jádro opatrně vyjmeš. Nic dalšího se neděje. Alespoň tedy nevidíš žádnou viditelnou změnu v okolí.",
        options: { continue: "Pokračovat" }
    },
    careful_extract_complete: {
        text: "Živé jádro ti spokojeně pulzuje v dlaních. Opatrným vyjmutím jsi jeho energii zřejmě zachoval.",
        options: { continue: "Pokračovat" }
    },
    goodbye: {
        text: "Ustoupíš od Živého jádra."
    },
    goodbye_taken: {
        text: "Ustoupíš od místa, kde bylo Živé jádro."
    }
};
