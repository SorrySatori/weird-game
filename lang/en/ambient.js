/**
 * English text for ambient people (utils/AmbientNpc.js) — figures you can't talk to who answer a click with one line
 * in a speech bubble. Keyed as ambient.<id>.name (the hover label) and ambient.<id>.lines (said in turn).
 */
export default {
    ambient: {
        // Shed521FloorsScene — the ground floor
        floors_welcome_clerk: {
            name: 'Receptionist',
            lines: [
                "Seventeen! Is anyone seventeen? ...Nobody is ever seventeen.",
                "Take a number from the machine. If it's out of numbers, fill in a request for a number.",
                "The Bureau of Shapes welcomes you in whatever shape you arrived in. Just don't change it while you're in line.",
                "*Thump.* Received. Not approved — received. Approvals are two floors up.",
            ],
        },
        floors_dozer: {
            name: 'Dozing applicant',
            lines: [
                "Mm? Is it seventeen yet? Wake me at seventeen.",
                "I came in to register one coral. Three more have grown since. I'll need new forms.",
                "Shh. I'm not asleep. I'm waiting with my eyes closed.",
            ],
        },
        // Shed521FloorsScene — the queue at APPLICATIONS on the top floor
        floors_queue0: {
            name: 'First in line',
            lines: [
                "I'm first. I've been first since spring — the door just hasn't noticed yet.",
                "Don't even try. The end of the line is over there, behind the orange hood.",
            ],
        },
        floors_queue1: {
            name: 'Applicant with forms',
            lines: [
                "Form 7-B, another 7-B, and a form confirming I have two 7-Bs. I'm ready. I've been ready for weeks.",
                "They say it takes seventeen forms just to request a new form. I counted eighteen. I'm here to report the eighteenth.",
            ],
        },
        floors_queue2: {
            name: 'Applicant in line',
            lines: [
                "I'm applying for a second spine. Nothing wrong with the first one — I just want a spare.",
                "Would you hold my place? ...No, never mind. Whoever leaves the line never comes back.",
            ],
        },
        floors_queue3: {
            name: 'Last in line',
            lines: [
                "Are you in line? Then you're behind me. Best news I've had all week.",
                "I don't know what this line is for. But nobody would stand here for nothing, would they?",
            ],
        },
    },
};
