/**
 * Czech dialog translations for ShedHallScene — the Living Core in the wall. Narration only (tyká). The player may
 * come here before Gnur's quest, so the narration says what he sees, not the core's name.
 */
export default {
    _speakers: {
        'Narrator': 'Vypravěč',
    },
    main: {
        text: "Ve stěně je vsazený zelený svítící předmět, který pulzuje nadpozemskou energií. Slyšíš tiché hučení, které se rozléhá chodbou. Jakmile se k předmětu přiblížíš, houbové výrůstky na tvém těle se jemně rozechvějí. Vypadá to, že je ve zdi pevně usazený, ale možná by šel vyjmout…",
        options: {
            examine_it_more_carefully: "Prohlédnout si ho pozorněji",
            use_pliers_to_carefully_extract_it: "Opatrně ho vyjmout kleštěmi",
            extract_it_forcefully: "Vyrvat ho silou",
            leave_it_alone: "Nechat ho být"
        }
    },
    examine: {
        text: "Předmět drží ve zdi jen na několika málo místech. Se správným nástrojem, třeba kleštěmi, by možná šel vyjmout bez poškození…",
        options: { back: "Zpět" }
    },
    force_extract: {
        text: "Vyrveš předmět ze zdi hrubou silou. Zdá se ti, že se vzduch kolem tebe ochladil…",
        options: { continue: "Pokračovat" }
    },
    careful_extract: {
        text: "Kleštěmi předmět opatrně uvolníš. Nic dalšího se neděje… nebo aspoň kolem sebe žádnou změnu nevidíš.",
        options: { continue: "Pokračovat" }
    },
    careful_extract_complete: {
        text: "Předmět ti spokojeně pulzuje v dlaních. Opatrným vyjmutím jsi jeho energii zřejmě zachoval.",
        options: { continue: "Pokračovat" }
    },
    goodbye: {
        text: "Ustoupíš od svítícího předmětu."
    },
    goodbye_taken: {
        text: "Ustoupíš od prázdného otvoru ve zdi."
    }
};
