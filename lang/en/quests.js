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
                vestigel: 'Kloor Venn wants me to find one of the three Vestigels in the market. He mentioned that a merchant named Zerren has one.',
                elphi_contact: "According to Kloor Venn, the Bishop visited Dr. Elpi Quarn quite often... I should look for Dr. Elphi at the Scraper 1140.",
                bishop_clue_gnur: "The Bishop was seen at Scraper 1140, making an unusual trade involving a 'game lens'. Gnur might know more, but he wants something in return.",
                edgar_eskola_clue: 'The clerk told me to find Edgar Eskola at the Screaming Cork tavern. He might know something.',
                bishop_location_scraper: 'The Bishop was last seen heading to Scraper 1140 to meet with Dr. Elphi.',
                got_floor_counter_tool: "Captain Liris gave me a calibration tool to repair the Lift Mother's floor counter, which should allow me to access Dr. Elphi's studio.",
                lift_mother_permission: "The Lift Mother has granted me access to Dr. Elphi's studio on floor 177-Quiet.",
                reached_elphi_studio: "I've reached Dr. Elphi's studio on floor 177-Quiet. Now I need to find clues about the Bishop.",
                check_shard_backyard: 'Dr. Elphi mentioned the Bishop was last seen in the Shard backyard. I should check there next.',
                found_elevator_button: "I found a Forgotten Elevator Button at Zerren's shop that might help me access Dr. Elphi's floor.",
            }
        },
        who_killed_bishop: {
            title: 'Who Killed the Bishop?',
            description: 'I found the Bishop dead in an abandoned bus behind the Scraper building. Her body shows barely any signs of violence. I should investigate who might be responsible for her death.',
            updates: {
                dead_bishop_bruising: 'I have examined the Bishop\'s body and found bruises at the temples where dream interface devices connect.',
                dead_bishop_cartridge: 'Before she died, the Bishop was apparently playing a game called "The Cardinal Feast".',
                dead_bishop_helmet: 'Before she died, the Bishop was apparently using a portable dream interface helmet.',
                dead_bishop_journal: 'Before she died, the Bishop was apparently writing in her journal... "The city no longer hears me. Perhaps the dreams will."',
                dead_bishop_notebook: 'I have found a strange note... "I walked into the confessional, but she was already there. Looked like me..."',
                bishop_dissection: "The Bishop's body contains a strange glowing fungal growth that has integrated with her nervous system.",
                dead_bishop_berries: 'Before she died, the Bishop was apparently eating Sulkberries.',
                gardener_bishop_info: 'The gardener Verrik at the Lumen Directorate mentioned the Bishop used to visit regularly — specifically to see the Angle Corrector.',
                gardener_sulkberry_info: 'The gardener at the Lumen Directorate confirmed spiced Sulkberries are a controlled commodity.',
                ac_bishop_relationship: 'The Angle Corrector confirmed a professional relationship with the Bishop — regular meetings about Cathedral access and the hatching.',
                ac_sulkberry_confirmed: 'The Angle Corrector confirmed the Sulkberry supply to the Bishop — used for dream immersion in the Cathedral.',
                ac_tamper_hint: "The Angle Corrector hinted that tampered Sulkberries could cause neural trauma matching the Bishop's condition.",
                elphi_dream_kill: 'Dr. Elphi confirmed that a corrupted dream cartridge could cause death by neural overload — "death by recursive experience."',
                elphi_bruising: 'Dr. Elphi confirmed the bruising indicates a feedback surge from a dream session without safety limiters.',
                elphi_cartridge: 'Dr. Elphi confirmed The Cardinal Feast is a normal game — the lizard cannibal RPG. But the session data shows a catastrophic failure.',
                elphi_helmet: 'Dr. Elphi says the damaged helmet port confirms the signal load was beyond hardware limits.',
                elphi_memo: "Dr. Elphi couldn't explain the doppelgänger from the Bishop's memo. It's not any known side effect of dream technology.",
                elphi_townhall_log: "The Bishop's doppelgänger encounter was formally logged at the Townhall. The archive clerk might have a copy.",
                elphi_journal: 'Dr. Elphi interpreted the Bishop\'s journal entry as evidence she had been disconnected from the myceliar network.',
                elphi_dissection: 'Dr. Elphi believes the fungal growth inside the Bishop was a symbiont. The killer may have been targeting the symbiont itself.',
                elphi_berries: 'Dr. Elphi identified the Sulkberries as a spiced variety — a Lumen Directorate specialty.',
                elphi_lumen_lead: 'Dr. Elphi suggested speaking with the Lumen Directorate. They sell the spiced Sulkberries.',
                elphi_day1_complete: "I've discussed all the clues with Dr. Elphi. She's working on fixing The Cardinal Feast cartridge.",
            }
        },
        the_three_vestigels: {
            title: 'The Three Vestigels',
            description: 'Kloor Venn wants me to find one of the three Vestigels in the market. He mentioned that a merchant named Zerren has one.',
            updates: {
                found_eskola_lead: 'Zerren revealed that Edgar Eskola purchased the plush toy containing a Vestigel.',
                completed: 'I gave the vestigel to Kloor Venn in exchange for information about the Bishop.',
                edgar_vestigel_acquired: 'Received a vestigel from Edgar Eskola in exchange for helping with his book.',
                edgar_book_trade: 'Edgar Eskola would trade the Vestigel for your help with his book.',
            }
        },
        find_lumen_directorate: {
            title: 'Nothing Hidden. Nothing Lost',
            description: 'Captain Liris gave me directions to the Lumen Directorate headquarters. I should visit them to learn more about their work and see if I can join their crew.',
            updates: {
                gardener_directions: 'The gardener Verrik directed me to speak with the Angle Corrector on the third floor of the Directorate.',
            }
        },
        find_rust_choir: {
            title: 'Find the Rust Choir',
            description: 'I need to find a way to meet the Rust Choir who reside on the upper floors of the Scraper building.',
            updates: {
                talk_to_ravla: 'I should speak with Ravla at the Screaming Cork tavern first.',
                talked_to_ravla: 'Ravla at the Screaming Cork wants me to prepare a feast for the Rust Choir machines to prove my commitment.',
                feast_complete: 'The Rust Feast is complete. Ravla gave me the password for Lift Mother: "Corrode". I can now access the Rust Choir domain.',
                feast_delivered: 'I delivered the Rust Feast to Brukk in the Rust Domain.',
            }
        },
        rust_feast: {
            title: 'Rust Feast',
            description: 'Prepare a feast for the Rust Choir machines by gathering oil, metal, and a living redmass, and bring them to Ravla at the Screaming Cork.',
            updates: {
                talked_to_archeologist_hint: 'Ravla suggested I speak with the archeologist near the townhall to learn more about redmass.',
                gathered_rust_materials_hint: 'Ravla advised me to search around the Scraper for scrap metal... and check the Yolk Sea docks or Echo Drain Delta for oil.',
                redmass_spared: 'I found a living redmass on an island at Echo Drain Delta, but chose to spare it.',
                redmass_collected: 'I collected the living redmass from the island at Echo Drain Delta.',
                magnekin_tip: 'A strange creature that identifies itself as Magnekin told me that some metal scraps could be found at Echo Drain delta.',
                learned_rust_cluster_location: 'Phor Calesta told me that redmass can be found in the maintenance halls of Shed 521.',
            }
        },
        rust_reclamation: {
            title: 'Rust Reclamation',
            description: "Gnur needs help recovering a 'living core' from Shed 521's unused tunnels, located somewhere behind the abandoned office.",
            updates: {
                promise_made: 'I promised the clerk in Shed 521 I will not mess with the living core.',
                core_delivered: 'I have given Gnur the living core. He seems satisfied.',
                quest_refused: 'I refused to help Gnur steal the living core after learning its importance.',
            }
        },
        ortolan_arms: {
            title: 'Extra Arms for Ortolan',
            description: "Help Ortolan, the board game designer, navigate the Shed's bureaucracy to get approval for an extra pair of arms.",
            updates: {
                deformity_form_clue: 'The clerk told me to go to the Registration office to retrieve Inherited Deformity Form.',
                forge_documents_suggestion: 'When I suggest to the clerk to forge the documents for Ortolan, he looked at me with a mix of surprise and annoyance.',
                artisan_form_clue: "The clerk told me to go to the Registration office to retrieve Artisan's Exemption Form.",
                nonverbal_gesture_clue: 'The clerk told me to go to the Registration office and do my best with nonverbal gesture.',
                ravla_forger_hint: 'Heliodor at the Screaming Cork mentioned that Ravla is a skilled document forger.',
                ravla_forger_agreement: 'Ravla at the Screaming Cork can forge the Artisan\'s Exemption Form for Ortolan, but she wants 50 dinars for the job.',
                document_obtained: 'You obtained a forged Artisan\'s Exemption Form from Ravla. Deliver it to Ortolan at the Shed Courtyard.',
                bureaucratic_incantation: 'The Hollow Woman in the registration queue taught me some weird bureaucratic incantation.',
                form_obtained: "I successfully obtained the form for Ortolan.",
                partial_progress: "I obtained a Temporary Permit that might help Ortolan, but it's not fully approved.",
                failed_attempt: "My registration attempt failed. I'll need to find another way to help Ortolan.",
                completed: 'I helped Ortolan obtain approval for extra arms.',
            }
        },
        excavation_permit: {
            title: 'Divinography',
            description: 'I should help Phor Calesta obtain excavation permits for the Godgraveyard of the townhall. First, I need to get inside the townhall somehow.',
        },
        enter_townhall: {
            title: 'Enter the Townhall',
            description: "The Townhall is closed and nobody knows why. I need to find a way inside — the Bishop's doppelgänger report was filed there, and Phor Calesta needs access too. Maybe someone in the city knows how to get in.",
            updates: {
                gardener_seldo_tip: 'The gardener Verrik at the Lumen Directorate suggested I speak with Seldo Thrice-Corrected inside.',
                ac_seldo_referral: 'The Angle Corrector directed me to Seldo Thrice-Corrected on the second floor.',
            }
        },
        level_177_access: {
            title: 'Access to Level 177',
            description: "I need to gain access to Dr. Elphi Quarn's studio on floor 177-Quiet in the Scraper building.",
        },
        edgar_book: {
            title: 'Help Edgar to write a book',
            description: 'Edgar Eskola mentioned he wants to write a book. I should help him.',
            updates: {
                completed: 'You have helped Edgar Eskola develop his book concept. He is very grateful to you.',
            }
        },
    }
};
