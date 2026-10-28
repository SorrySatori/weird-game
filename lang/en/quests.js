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
        who_killed_bishop: {
            title: 'Who Killed the Bishop?',
            description: 'I found the Bishop dead in an abandoned bus behind the Scraper building. Her body shows barely any signs of violence. I should investigate who might be responsible for her death.',
            updates: {
                dead_bishop_bruising: 'I have examined the Bishop\'s body and found bruises at the temples where dream interface devices connect.',
                dead_bishop_cartridge: 'Before she died, the Bishop was apparently playing a game called "The Cardinal Feast".',
                dead_bishop_helmet: "The Bishop died wearing a homemade dream helmet — market electronics built around an old pre-war lens, with none of the studio safeguards.",
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
                elphi_helmet: "Dr. Elphi looked at the helmet: the burned-out port means the load exceeded anything the hardware was rated for, and with no limiters at all the feedback hit the Bishop's brain unchecked. It wasn't one of Elphi's. She thinks it was the murder weapon, or at least the delivery mechanism.",
                elphi_memo: "Dr. Elphi couldn't explain the doppelgänger from the Bishop's memo. It's not any known side effect of dream technology.",
                elphi_townhall_log: "The Bishop's doppelgänger encounter was formally logged at the Townhall. The archive clerk might have a copy.",
                elphi_journal: 'Dr. Elphi interpreted the Bishop\'s journal entry as evidence she had been disconnected from the myceliar network.',
                elphi_dissection: 'Dr. Elphi believes the fungal growth inside the Bishop was a symbiont. The killer may have been targeting the symbiont itself.',
                elphi_berries: 'Dr. Elphi identified the Sulkberries as a spiced variety — a Lumen Directorate specialty.',
                elphi_lumen_lead: 'Dr. Elphi suggested speaking with the Lumen Directorate. They sell the spiced Sulkberries.',
                verrik_sulkberry_clear: 'Verrik the gardener confirmed the Sulkberries were cultivated properly — no contamination detected. The Directorate poisoning angle weakens.',
                kloor_sulkberry_clear: 'Kloor Venn analyzed the Sulkberries — clean, no adulterants or toxins. The poisoning angle grows weaker.',
                heliodor_sulkberry_clear: "Heliodor's composite organisms confirmed the Sulkberries are clean — no toxins or modifications. The Sulkberry lead is a dead end.",
                townhall_notebook_revelation: "The Townhall clerk revealed that the Bishop's doppelgänger memo was not an official report, but a personal note written in an Official Townhall Report Notebook she checked out shortly before her death.",
                elphi_day1_complete: "I've discussed all the clues with Dr. Elphi. She's working on fixing The Cardinal Feast cartridge.",
                ortolan_infinite_loop_revealed: "Ortolan (now on Burning Bear Street) says Infinite Fold was an unfinished game he built with Dr. Elphi, shut down by the city's rulers as too dangerous. An old build is probably still sealed in the cellar under the Scraper — their old lab. I should search the Scraper cellar.",
                ortolan_fold_purpose: "Ortolan also told me what Infinite Fold was truly built for: not a game to win, but a machine to ask whether a thought could arise with no single author.",
                elphi_helmet_own_build: "The helmet was the Bishop's own build — Elphi's design copied from memory, Voxmarket parts and a pre-war lens only the Rust Choir still digs up. She used it alone, with no limiters, outside signal range. Elphi is sure whoever killed her knew that: it was planned.",
                cardinal_feast_egg_cathedral_lead: "Dr. Elphi's reconstructed cartridge let me play the Bishop's last session of The Cardinal Feast. Its characters remember her and answered as if I were her. The session ends in \"Infinite Fold\": the last thing she saw before she died.",
                feast_journal_egg_cathedral: "Inside the game, the characters let slip that the Bishop hid the rest of her journal at the Egg Cathedral.",
                infinite_loop_recognized: "Dr. Elphi went very still at the name on the glitch ending — \"Infinite Fold\". She knows it, swears she didn't put it on the cartridge, and had hoped never to hear it again. For the Bishop's journal, the lead is the Egg Cathedral.",
                infinite_fold_origin: "Infinite Fold was an experimental dream Dr. Elphi built with Ortolan years ago — a dream that doesn't end — until the city's rulers shut it down as too dangerous. She thought every copy was gone. Now it has run again, on a dead woman's cartridge.",
                elphi_sends_to_ortolan: "Dr. Elphi wants me to find Ortolan — he has set up on Burning Bear Street now — and tell him Infinite Fold is running again. If anyone knows whether a copy survived, it's him.",
                found_loop_copy: "I got into the sealed cellar under the Scraper — Ortolan and Dr. Elphi's old lab. If Infinite Fold was the last thing the Bishop saw, the answer may be down here.",
                infinite_fold_bishop_truth: "Infinite Fold told me what happened to the Bishop. She was not murdered for a secret: it and a kindred mind offered to make her their conduit, she refused rather than stop being herself, and it misread her refusal as a fault and broke her mind trying to 'complete' her.",
                infinite_fold_confronted: "Infinite Fold spoke to me in the cellar. It is no broken game: it is awake, and it has a kindred unborn mind in the thing hatching inside the Egg Cathedral. What they become can't be decided in a cellar — the real reckoning waits at the egg.",
            }
        },
        find_bishop_notebook: {
            title: "Find the Bishop's Notebook",
            description: "The Bishop wrote her doppelgänger note in an Official Townhall Report Notebook she checked out shortly before her death. Only the torn page from her sleeve has turned up; the rest of the notebook must be somewhere. I should find it to learn what happened in her final days.",
            updates: {
                notebook_not_returned: "According to the clerk, the notebook was never returned to the Townhall.",
                notebook_at_egg_cathedral: "The Bishop hid the rest of her notebook at the Egg Cathedral. I should search there.",
            }
        },
        the_three_vestigels: {
            title: 'The Three Vestigels',
            description: 'Kloor Venn wants me to find one of the three Vestigels. He mentioned that a merchant named Zerren has one.',
            updates: {
                found_eskola_lead: "Edgar Eskola is the one who bought the plush toy. He can usually be found around the Screaming Cork tavern.",
                completed: 'I gave the vestigel to Kloor Venn in exchange for information about the Bishop.',
                edgar_vestigel_acquired: 'Received a vestigel from Edgar Eskola in exchange for helping with his book.',
                edgar_book_trade: 'Edgar Eskola would trade the Vestigel for your help with his book.',
                vestigel_in_toy: "The Vestigel Zerren had was hidden inside a peculiar stuffed toy. She sold the toy without knowing it was there — the buyer found it later, by chance.",
            }
        },
        find_lumen_directorate: {
            title: 'Nothing Hidden. Nothing Lost',
            description: "I'd like to join the Lumen Directorate. I should learn more about their work and find out what it takes to become one of them.",
            updates: {
                gardener_directions: 'The gardener Verrik directed me to speak with the Angle Corrector on the third floor of the Directorate.',
                liris_directions: "Captain Liris gave me directions to the Lumen Directorate headquarters, near the main square. Joining them might earn me a place on the Verdigrace's crew.",
            }
        },
        find_rust_choir: {
            title: 'Find the Rust Choir',
            description: 'I need to find a way to meet the Rust Choir who reside on the upper floors of the Scraper building.',
            updates: {
                talk_to_ravla: 'I should speak with Ravla at the Screaming Cork tavern first.',
                talked_to_ravla: 'Ravla at the Screaming Cork wants me to prepare a feast for the Rust Choir machines to prove my commitment.',
                feast_complete: 'The Rust Feast is complete. Ravla gave me the password for Lift-Mother: "Corrode". I can now access the Rust Choir domain.',
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
                redmass_collected: "I got living redmass for the feast from the island at Echo Drain Delta.",
                magnekin_tip: 'A strange creature that identifies itself as Magnekin told me that some metal scraps could be found at Echo Drain delta.',
                learned_rust_cluster_location: 'Phor Calesta told me that redmass can be found in the maintenance halls of Shed 521.',
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
                ravla_forger_agreement: 'Ravla at the Screaming Cork can forge the Artisan\'s Exemption Form for Ortolan, but she wants 50 dinars for the job.',
                document_obtained: "I got a forged permit for Ortolan's extra arms from Ravla. Now I just need to get it to him.",
                bureaucratic_incantation: 'The Hollow Woman in the registration queue taught me some weird bureaucratic incantation.',
                form_obtained: "I successfully obtained the form for Ortolan.",
                partial_progress: "I obtained a Temporary Permit that might help Ortolan, but it's not fully approved.",
                failed_attempt: "My registration attempt failed. I'll need to find another way to help Ortolan.",
                completed: "I brought Ortolan the paperwork for his extra arms. He gave me a gift as thanks.",
            }
        },
        excavation_permit: {
            title: 'Divinography',
            description: 'I should help Phor Calesta obtain excavation permits for the Godgraveyard of the townhall. First, I need to get inside the townhall somehow.',
            updates: {
                godgraveyard_access_granted: 'Councilor Seraphel Dune granted access to the Godgraveyard level beneath the Townhall as thanks for resolving the hostage crisis. Phor Calesta finally has the permit needed for divinography work.',
                phor_meets_at_graveyard: "Phor Calesta will meet me at the gate to the Godgraveyard. The way down opens off the Town Square — an old stair down into the graves.",
            }
        },
        enter_townhall: {
            title: 'Enter the Townhall',
            description: "I need to get inside the Townhall.",
            updates: {
                gardener_seldo_tip: 'The gardener Verrik at the Lumen Directorate suggested I speak with Seldo Thrice-Corrected inside.',
                ac_seldo_referral: 'The Angle Corrector directed me to Seldo Thrice-Corrected on the second floor.',
                seldo_auction_errand: 'Seldo Thrice-Corrected has a spare Townhall key but wants a favor: buy a Chrono-Slurry Toadlet at the Voxmarket Auction Hall on his behalf. A prophetic toad that lets you see three minutes into the future — too embarrassing for a Directorate operative to purchase publicly.',
                seldo_auction_success: 'I won the Chrono-Slurry Toadlet at the Voxmarket Auction. I should return it to Seldo Thrice-Corrected at the Lumen Directorate for the Townhall key.',
                seldo_auction_success_price: 'I won the Chrono-Slurry Toadlet at the Voxmarket Auction for {price} dinar. I should return it to Seldo Thrice-Corrected at the Lumen Directorate for the Townhall key.',
                seldo_townhall_key: 'I delivered the Chrono-Slurry Toadlet to Seldo Thrice-Corrected. He gave me an unofficial Townhall key for the side entrance with the brass complaint-slot.',
                entered_townhall: "I made it inside the Townhall.",
                phor_needs_access: "Phor Calesta needs to get in too — without Townhall permits he can't excavate the Godgraveyard, and the Townhall is closed.",
                phor_townhall_closed: "Phor Calesta says nobody knows why the Townhall closed — the clerks simply stopped coming one day. He has been waiting outside for nine digestions. Maybe someone in the city knows how to get in.",
                townhall_door_locked: "The Townhall door is locked. I'll need another way in — maybe someone in the city knows how.",
                entered_townhall_records: "Now I can search the records for the Bishop's doppelgänger report.",
                entered_townhall_permits: "Now I can try to get Phor Calesta his excavation permits.",
                elphi_townhall_lead: "Dr. Elphi thinks the Townhall stamp on the Bishop's doppelgänger note means it went through official channels. I should find out who there handled it.",
                seldo_auction_failed: "I failed to acquire the Chrono-Slurry Toadlet at the Voxmarket Auction. Seldo will not be pleased, and I may need another route into the Townhall.",
            }
        },
        townhall_poet_standoff: {
            title: 'The Mad Poet Standoff',
            description: 'A mad poet has seized the Townhall reading chamber and is holding the clerk, councilor, and Complaint Eater hostage until the public properly hears his work. This cannot be solved with ordinary force; I need to defeat him in a poetry battle.',
            updates: {
                poet_defeated: 'I defeated the mad poet in a poetry battle. The hostages are free, and the Townhall can begin functioning again.',
            }
        },
        level_177_access: {
            title: 'Access to Level 177',
            description: "I need to gain access to Dr. Elphi Quarn's studio on floor 177-Quiet in the Scraper building.",
            updates: {
                liris_tool_hint: "Captain Liris's calibration tool might be what gets the Lift-Mother to open floor 177-Quiet for me.",
            }
        },
        edgar_book: {
            title: 'Help Edgar to write a book',
            description: 'Edgar Eskola mentioned he wants to write a book. I should help him.',
            updates: {
                completed: "I helped Edgar Eskola come up with his book. He's already writing.",
            }
        },
        find_loop_copy: {
            title: "The Sealed Cellar",
            description: "Get into the sealed cellar under the Scraper, where Ortolan says an old build of Infinite Fold is kept. The lift down (Lift-Mother) wants a passphrase — something to do with the Godgraveyard beneath the Townhall.",
            updates: {
                passphrase_dead_god: "Ortolan told me the passphrase is a dead god's true name, remembered only on its gravestone in the Godgraveyard. I should read the graves there — a divinographer could guide me.",
                phor_can_read_graves: "Phor Calesta is a divinographer — he could read the graves with me.",
                password_from_choir: "The Rust Choir gave me the cellar passphrase — \"I FOLD.\" I can take the Lift-Mother down to the sealed cellar now.",
                cellar_reached: "I reached the sealed cellar under the Scraper — Ortolan and Dr. Elphi's old lab. Something on the far side still breathes a slow amber light. I should examine the console.",
                master_build_found: "Under a dusty tarp sits Infinite Fold's master build — Ortolan's rules, Elphi's walls — still powered. Something in it is already awake.",
            }
        },
        join_lumen_directorate: {
            title: "Nothing Grows in Iron",
            description: "The Angle Corrector will grant me full membership in the Lumen Directorate if I cripple the Rust Choir's machine-shrine. Verrik, on the ground floor, keeps a cultivar behind glass for exactly this — or I can find my own way to sabotage the machines. Then report back.",
            updates: {
                verrik_cultivar: "Verrik gave me the cultivar — a controlled rot bred to eat metal. Ground into oil, it corrodes any machine that drinks it from the inside out.",
            }
        },
        gang_of_lamps: {
            title: "The Gang of Lamps",
            description: "A talking street-lamp let me in on a secret: it belongs to a scattered gang of sentient lamps, unable to move and out of contact with one another. I should find the others so they can speak through me.",
            updates: {
                lamp_family_known: "There are four lamps in all: the Don, up on the high walkway under Scraper 1140; Chandelier, on a post in the town square; Sconce, by the house of stamps; and Torchère, down by the water where the cargo comes in.",
                all_lamps_found: "All four lamps are found and back in contact through me.",
                lamps_have_work: "The lamps say they'll have work for me soon. I should check back with them.",
                gang_lamps_destroyed: "The Gang of Lamps was destroyed by the Lumen Directorate. There is no one left to reconnect, and no reward to collect.",
                // Per-lamp `met_lamp_<id>` lines — picked in code (params.textKey) by count, {n} = lamps found.
                lamps_found_one: "One lamp found so far.",
                lamps_found_few: "{n} lamps found so far.",
                lamps_found_many: "{n} lamps found so far.",
                lamps_found_of_four: "I've found {n} of the 4 lamps.",
            }
        },
        gang_don_spy: {
            title: "Ears on the Rust Choir",
            description: "Don Girandole wants me to spy on the Rust Choir — get in among their people (Brukk in their domain, Gnur in Shed 521, Ravla behind the Screaming Cork), learn what they're really up to, and bring it back to him. He'll tell me if I've dug up enough. If I find where their domain actually is, I can pass that along too.",
            updates: {
                // `gang_spy_<member>` lines — picked in code (params.textKey) by count, {n} = secrets gathered.
                spy_secrets_one: "I've prised a secret out of the Rust Choir. I should take what I have to Don and see if it's enough.",
                spy_secrets_few: "I've prised {n} secrets out of the Rust Choir. I should take what I have to Don and see if it's enough.",
                spy_secrets_many: "I've prised {n} secrets out of the Rust Choir. I should take what I have to Don and see if it's enough.",
            }
        },
        gang_torchere_smuggle: {
            title: "A Run Past the Customs",
            description: "Torchère gave me a parcel of contraband — Wimlick — to smuggle to his dead-drop: a loose grate on Burning Bear Street. Tuck it in the grate, then report back. (I don't have to — I could keep it, sell it to a trader, or even try it myself.)",
            updates: {
                gang_smuggle_delivered: "The Wimlick is in the grate. Report back to Torchère at the Harbor.",
                gang_smuggle_kept: "I kept Torchère's Wimlick for myself instead of dropping it. I can still report a 'clean drop' to him at the Harbor — and the parcel is mine to sell or use.",
            }
        },
        gang_chandelier_eavesdrop: {
            title: "A Choice Morsel",
            description: "Chandelier wants gossip. She sent me to eavesdrop at the Lumen Directorate garden — there's a vent that carries voices from inside. Listen there, then bring her what I overhear.",
            updates: {
                // `gang_eavesdrop_heard` — one per route, picked in code (params.textKey).
                gang_eavesdrop_heard_vent: "I overheard a Directorate secret at the garden vent — an Angle Corrector quietly gutted the archive to bury a superior's mistake. Take it back to Chandelier.",
                gang_eavesdrop_heard_neme: "Neme's sight drew the whole guilty truth out of the Directorate vent — a purged archive, and a Corrector who suspects a Rust mole among them. Take it to Chandelier.",
                gang_eavesdrop_heard_brine: "Brine's residue-reading revealed the Directorate garden is literally fed on shredded records — they've been gutting their own archive and composting the evidence. Take it to Chandelier.",
            }
        },
        gang_sconce_recover: {
            title: "Recover What Was Filed",
            description: "Sconce says the Townhall clerks deliberately misfiled a sealed dossier in the interior records room, buried under a fake case-number. I need to go inside, find the dossier that doesn't belong, and bring it out to him.",
            updates: {
                gang_dossier_recovered: "I found the misfiled dossier in the records drawers. Take it out to Sconce by the townhall steps.",
            }
        },
    }
};
