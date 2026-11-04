/**
 * English quest translations — keyed by quest ID
 * Each quest has: title, description, and updates keyed by update_key
 */
export default {
    quests: {
        find_bishop: {
            title: 'Find the Bishop',
            description: 'The Fungal Master has tasked me with finding the Bishop at the Egg Cathedral. She might know about the distress call received from the city via the myceliar network. I need to speak with her to learn more.',
            updates: {
                vestigel: 'Kloor Venn wants me to find one of the three Vestigels. He mentioned that a merchant named Zerren has one.',
                elphi_contact: "According to Kloor Venn, the Bishop visited Dr. Elphi Quarn quite often... I should look for Dr. Elphi at the Scraper 1140.",
                bishop_clue_gnur: "Gnur says the Bishop came down to Shed 521 for a lens from the old pre-war dream rigs — Rust Choir stock. He wants something in return before he says more.",
                edgar_eskola_clue: 'The clerk told me to find Edgar Eskola at the Screaming Cork tavern. He might know something.',
                bishop_location_scraper: 'The Bishop bought a pre-war lens from Gnur and paid with a Vestigel — then headed to Scraper 1140 to meet Dr. Elphi.',
                got_floor_counter_tool: "Captain Liris gave me a calibration tool to repair the Lift-Mother's floor counter. With the counter fixed, the lift might reach floors it can't get to now.",
                lift_mother_permission: "The Lift-Mother has granted me access to Dr. Elphi's studio on floor 177-Quiet.",
                reached_elphi_studio: "I've reached Dr. Elphi's studio on floor 177-Quiet. Now I need to find clues about the Bishop.",
                check_shard_backyard: "Dr. Elphi pointed me to the Scraper backyard. I should look for the Bishop there.",
                found_elevator_button: "Zerren has a new item for sale: a Forgotten Elevator Button.",
                guard_cathedral_closed: 'The Egg Cathedral is closed and the guard at the gate lets no one in. He might know where to find the Bishop.',
                guard_bishop_not_inside: "According to the guard, the Bishop isn't in the cathedral. I'll have to look for her around the city — most likely at the Voxmarket or around Shed 521.",
                guard_voxmarket: 'The Voxmarket is an audio bazaar where recorded voices and sounds are traded. The Bishop might be found there.',
                guard_shed521: "Shed 521, officially the Bureau of Shapes, is where people get the certificate they need to change their body's shape. It's right next to the Voxmarket. The Bishop might be found there too.",
            }
        },
        the_three_vestigels: {
            title: 'The Three Vestigels',
            description: 'Kloor Venn wants me to find one of the three Vestigels. He mentioned that a merchant named Zerren has one.',
            updates: {
                found_eskola_lead: "Edgar Eskola is the one who bought the plush toy. He can usually be found around the Screaming Cork tavern.",
                completed: 'I gave the vestigel to Kloor Venn in exchange for information about the Bishop.',
                edgar_vestigel_acquired: 'Received a vestigel from Edgar Eskola in exchange for helping with his book.',
                edgar_book_trade: 'Edgar Eskola will give me the Vestigel if I help him write his book.',
                vestigel_in_toy: "The Vestigel Zerren had was hidden inside a peculiar stuffed toy. She sold the toy without knowing it was there — the buyer found it later, by chance.",
            }
        },
        find_lumen_directorate: {
            title: 'Nothing Hidden. Nothing Lost',
            description: "I'd like to join the Lumen Directorate. I should learn more about their work and find out what it takes to become one of them.",
            updates: {
                liris_directions: "Captain Liris gave me directions to the Lumen Directorate headquarters, near the main square. Joining them might earn me a place on the Verdigrace's crew.",
            }
        },
        find_rust_choir: {
            title: 'Find the Rust Choir',
            description: 'I need to find a way to meet the Rust Choir who reside on the upper floors of the Scraper building.',
            updates: {
                talk_to_ravla: 'I should speak with Ravla at the Screaming Cork tavern first.',
                talked_to_ravla: 'Ravla at the Screaming Cork wants me to prepare a feast for the Rust Choir machines to prove my commitment.',
            }
        },
        rust_feast: {
            title: 'Rust Feast',
            description: 'Prepare a feast for the Rust Choir machines by gathering oil, metal, and a living redmass, and bring them to Ravla at the Screaming Cork.',
            updates: {
                demo_not_yet: "Ravla admitted the places I'd need for the feast aren't part of this demo yet. The Rust Choir will have to wait for the full game — Brukk never forgets a volunteer, she says.",
            }
        },
        rust_reclamation: {
            title: 'Rust Reclamation',
            description: "Gnur needs help recovering a 'living core' from Shed 521's unused tunnels, located somewhere behind the abandoned office.",
            updates: {
                promise_made: "I promised the clerk in Shed 521 I will not mess with the living core. It seems to matter far more than Gnur let on — the clerk says it is classified technology, and the Rust Choir has no right to it.",
                core_taken_force: 'I have retrieved the Living Core, with a bit of good old violence.',
                core_taken_careful: 'Carefully extracted the Living Core using pliers; it probably didn\'t damage the building in any way.',
                core_delivered: 'I have given Gnur the living core. He seems satisfied.',
                quest_refused: 'I refused to help Gnur steal the living core after learning its importance.',
                core_shed_energy: "The clerk in Shed 521 warned me to leave the living core alone. People take it for an old relic, but the Shed's energy supply depends on it.",
            }
        },
        ortolan_arms: {
            title: 'Extra Arms for Ortolan',
            description: "Help Ortolan, the board game designer, navigate the Shed's bureaucracy to get approval for an extra pair of arms.",
            updates: {
                deformity_form_clue: 'The clerk told me to go to the Registration office to retrieve the Inherited Deformity Form.',
                forge_documents_suggestion: 'When I suggested forging the documents for Ortolan, the clerk looked at me with a mix of surprise and annoyance. But can it be done? Where could I find a forger?',
                artisan_form_clue: "The clerk told me to go to the Registration office to retrieve the Artisan's Exemption Form.",
                nonverbal_gesture_clue: 'The clerk told me to go to the Registration office and do my best with a nonverbal gesture. I am not sure I understand completely...',
                ravla_forger_hint: 'Heliodor at the Screaming Cork mentioned that Ravla is a skilled document forger.',
                // same flag key (it opens Ravla's offer), written by the Senior Clerk's warning after a failed registration
                clerk_forger_warning: "My registration attempt failed, and the office won't take a second application. The Senior Clerk did warn me off a forger called Ravla at the Screaming Cork, though — which is practically a recommendation.",
                ravla_forger_agreement: 'Ravla at the Screaming Cork can forge the Artisan\'s Exemption Form for Ortolan, but she wants 50 dinars for the job.',
                document_obtained: "I got a forged permit for Ortolan's extra arms from Ravla. Now I just need to get it to him.",
                bureaucratic_incantation: 'The Hollow Woman in the registration queue taught me some weird bureaucratic incantation.',
                registration_sent_to_applications: "The Senior Clerk at Registration only issues the forms; which form Ortolan's arms need is decided at Applications, on the top floor of the Shed.",
                form_obtained: "I successfully obtained the form for Ortolan.",
                partial_progress: "I obtained a Temporary Permit that might help Ortolan, but it's not fully approved.",
                failed_attempt: "My registration attempt failed. I'll need to find another way to help Ortolan.",
                completed: "I brought Ortolan the paperwork for his extra arms. He gave me a gift as thanks.",
            }
        },
        level_177_access: {
            title: 'Access to Level 177',
            description: "I need to gain access to Dr. Elphi Quarn's studio on floor 177-Quiet in the Scraper building.",
            updates: {
                liris_tool_hint: "Captain Liris's calibration tool might be what gets the Lift-Mother to open floor 177-Quiet for me.",
                arrived: "The Lift-Mother took me up. I'm on floor 177-Quiet.",
                hint_floor_counter: "The Lift-Mother's floor counter is broken. If I got it mended, she'd owe me a favour. She says sky folk understand such machines.",
                hint_lost_button: "The Lift-Mother has been missing a button for years. Things like that end up at the Voxmarket, she says.",
                hint_importance: "The Lift-Mother might let me up if I convince her it's truly important. To her, one story about the Bishop is gossip; two that agree are another matter. Someone else in the city might know where the Bishop went.",
                hint_importance_gnur: "The Lift-Mother might let me up if I convince her it's truly important. To her, one story about the Bishop is gossip; two that agree are another matter. Gnur promised to remember something about the Bishop once I bring him that core.",
                hint_importance_kloor: "The Lift-Mother might let me up if I convince her it's truly important. To her, one story about the Bishop is gossip; two that agree are another matter. Kloor Venn will tell me what he knows about the Bishop in exchange for a vestigel.",
            }
        },
        edgar_book: {
            title: 'Help Edgar to write a book',
            description: 'Edgar Eskola mentioned he wants to write a book. I should help him.',
            updates: {
                completed: "I helped Edgar Eskola come up with his book. He's already writing.",
            }
        },
    }
};
