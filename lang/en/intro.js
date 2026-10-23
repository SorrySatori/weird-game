/**
 * English intro scene text — cutscene narration + dialogue.
 * `opening`: captions over the opening shot of the Hymnar (Obazoba's sacred mushroom, not the god himself); `dialogues[].who` picks the speaker sprite in the chamber.
 */
export default {
    intro: {
        opening: [
            'Deep beneath the earth, far beyond the borders of Upper Morkezela, grows the Hymnar — the sacred mushroom of the god Obazoba.',
            'Obazoba himself has no body. He is the source of all life and all rot, an ideal no one has ever touched. The Hymnar is only his shrine — yet the faithful say that through its mycelium, the whole world can be heard.',
            'That night, a tremor ran through the Hymnar\'s mycelium: a cry for help, the kind heard once in a generation. Perhaps two.',
        ],
        dialogues: [
            { who: 'narrator', speaker: 'NARRATOR', text: 'In the underground temple of Obazoba, the Highest Humenium Council is gathered.' },
            { who: 'varhun', speaker: 'ARCHPRIEST VARHUN', text: 'A distress call through the myceliar network. A cry for help.' },
            { who: 'tynri', speaker: 'ARCHPRIEST TYNRI', text: 'From the surface. From the city of Upper Morkezela.' },
            { who: 'varhun', speaker: 'ARCHPRIEST VARHUN', text: 'We must respond, though we do not know who speaks.' },
            { who: 'rhull', speaker: 'ARCHPRIEST RHULL', text: "The Egg Cathedral is the place where we should go. The Bishop would know more. She has been monitoring what's going on in the city." },
            { who: 'varhun', speaker: 'ARCHPRIEST VARHUN', text: 'Summon Master Thaal to walk the deadroot path. Let the fungal emissary rise.' },
            { who: 'tynri', speaker: 'ARCHPRIEST TYNRI', text: 'He could be a capable investigator, true. But I have a notion that his apprentice is... a rather troublesome person, I must say.' },
            { who: 'rhull', speaker: 'ARCHPRIEST RHULL', text: "He is... well, he is Thaal's apprentice. I do not know much about him, but I do know that he is not the... sharpest mushroom in the forest." },
            { who: 'rhull', speaker: 'ARCHPRIEST RHULL', text: 'At least this time we have hidden the ceremonial oils.' },
            { who: 'tynri', speaker: 'ARCHPRIEST TYNRI', text: 'And locked the fungal archive. Twice.' },
            { who: 'varhun', speaker: 'ARCHPRIEST VARHUN', text: 'Summon Master Thaal. Let him find the Bishop of Upper Morkezela and discover the source of this distress call. The apprentice is his responsibility. And if the apprentice won\'t return, no problem. We can always find a new one for Master Thaal.' },
        ],
        skipHint: 'ESC — skip',
        transition: 'After days of travel, you finally arrive in the city of Upper Morkezela...',
    },
};
