import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class RustDomainScene extends GameScene {
    constructor() {
        super({ key: 'RustDomainScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        const hasRustFeast = !!(this.hasItem && this.hasItem('rust_feast'));
        const findQuest = this.questSystem?.getQuest('find_rust_choir');
        const questActive = !!(findQuest && !findQuest.isComplete);
        const isIllusory = !!this.hasJournalEntry('rust_feast_completed_illusion');
        const isFullRedmass = !!this.hasJournalEntry('rust_feast_completed_full');
        const rustRep = this.factionSystem?.getReputation('RustChoir') || 0;
        const alreadyMember = !!this.hasJournalEntry('rust_choir_joined');
        const machinesDestroyed = !!this.hasJournalEntry('rust_choir_machines_destroyed');

        return {
            ...super.dialogContent,

            // --- Brukk dialogs ---
            brukk_start: {
                speaker: 'Brukk',
                text: machinesDestroyed
                    ? `Brukk stands amid the silent machines, his massive frame hunched. He doesn't look at you. "You. You did this." His voice is a low rumble, like grinding gears. "Leave. Before I forget the Choir teaches patience."`
                    : alreadyMember
                        ? `Brukk nods slowly. "Brother. Sister. Whichever — you are Choir now. The machines hum for you too." He gestures at the trembling pipes around him. "Listen. They remember the feast."`
                        : `A massive figure turns to face you. Skin like tarnished copper, eyes like forge-lit coals. His arms are thick with weld scars, and something metallic clicks inside his chest when he breathes. "You." He tilts his head. "What do you want with the Rust Choir?"`,
                options: [
                    ...(!machinesDestroyed && !alreadyMember ? [
                        { text: "Who are you?", key: 'who_are_you', next: "brukk_who" }
                    ] : []),
                    ...(alreadyMember ? [
                        { text: "Tell me about the Rust Choir.", key: 'tell_me_about_the_rust_choir', next: "brukk_choir" },
                        { text: "What can you tell me about this building?", key: 'what_can_you_tell_me_about_this_building', next: "brukk_scraper" },
                        { text: "How are the machines?", key: 'how_are_the_machines', next: "brukk_machines_status" },
                    ] : []),
                    ...(questActive && hasRustFeast && !machinesDestroyed ? [
                        { text: "I've brought the Rust Feast for the machines.", key: 'ive_brought_the_rust_feast_for_the_machines', next: isIllusory ? "brukk_feast_illusion" : (isFullRedmass ? "brukk_feast_full" : "brukk_feast_shard") }
                    ] : []),
                    ...(questActive && !hasRustFeast && !machinesDestroyed ? [
                        { text: "I'm looking for the Rust Choir.", key: 'im_looking_for_the_rust_choir', next: "brukk_looking" }
                    ] : []),
                ]
            },
            brukk_who: {
                speaker: 'Brukk',
                text: `"Brukk. Keeper of the machines. I feed them. I listen to them. The machines called me up here — their hum got into my bones." He taps his chest. The clicking intensifies. "I have metal in me now. Grew there on its own. The Choir says that means the machines chose me."`,
                options: [
                    ...(questActive && hasRustFeast ? [
                        { text: "I've brought the Rust Feast.", key: 'ive_brought_the_rust_feast', next: isIllusory ? "brukk_feast_illusion" : (isFullRedmass ? "brukk_feast_full" : "brukk_feast_shard") }
                    ] : []),
                ]
            },
            brukk_looking: {
                speaker: 'Brukk',
                text: `"You found us. Congratulations." He doesn't sound impressed. "The Rust Choir isn't a social club. We serve the machines. Do you wish to serve them as well?`,
                options: [
                    { text: "I want to serve the machines. I brought a feast for them.", key: 'i_want_to_serve_the_machines_i_brought_a_feast_for', next: isIllusory ? "brukk_feast_illusion" : (isFullRedmass ? "brukk_feast_full" : "brukk_feast_shard") },
                    { text: "I just wanted to find you. I'll go now.", key: 'i_just_wanted_to_find_you_ill_go_now', next: "closeDialog" },
                    { text: "Would you care to tell me more about the Rust Choir first?", key: 'would_you_care_to_tell_me_more_about_the_rust_choi', next: "brukk_choir" }
                ]
            },

            brukk_choir: {
                speaker: 'Brukk',
                text: `Brukk leans against a trembling pipe. "The Rust Choir is not a religion. Not a guild. It is..." He searches for the word. "An understanding. The machines were here before the first gods came here to die. We don't know who made them. Perhaps some old culture? Or maybe they were always here. Maybe they built the city." He pauses. "They kept humming. They kept working. Everyone else went mad — grew fungus, grew wings, grew extra heads. The machines just... endured." He looks at you with something like pride. "We are the ones who noticed. Who listened. Who chose to serve what endures."`,
                options: [
                    { text: "How many of you are there?", key: 'how_many_of_you_are_there', next: "brukk_choir_members" },
                    { text: "What do the machines want?", key: 'what_do_the_machines_want', next: "brukk_machines_want" },
                ]
            },
            brukk_choir_members: {
                speaker: 'Brukk',
                text: `"Fewer than you'd think. More than you'd hope." He counts on scarred fingers. "Ravla — you know her. She handles the outside. Recruitment, supplies, the feasting rituals. Gnur and Kloor, they are always busy to get some funding for us. There's Gorj, who tends the boiler crypts below. Messel, who translates the machine-songs into something the rest of us can follow. And the Corroded Twins — they don't speak anymore, but the machines speak through them. Couple of others, you don't need to know everyone, I guess. We have also envoys and watchers in other cities." He pauses. "And me. Keeper. The one the machines chose to carry iron in his chest."`,
                options: [
                    { text: "Tell me about this building.", key: 'tell_me_about_this_building', next: "brukk_scraper" },
                    { text: "What do the machines want?", key: 'what_do_the_machines_want', next: "brukk_machines_want" },
                ]
            },
            brukk_machines_want: {
                speaker: 'Brukk',
                text: `"Want?" He almost laughs. "They don't want like you and I want. They hunger. They remember. They... persist." He presses his palm flat against a vibrating wall panel. "This one — feel it — this one remembers when it was part of an air-conditioning unit. Forty years of cooling office workers. Now it hums a song about the taste of redmass." His voice drops low. "The machines want to be fed. To be maintained. To not be forgotten. Is that so different from what anything wants?"`,
                options: [
                    { text: "What happens if they're not fed?", key: 'what_happens_if_theyre_not_fed', next: "brukk_machines_starve" },
                ]
            },
            brukk_machines_starve: {
                speaker: 'Brukk',
                text: `Brukk's expression darkens. "They slow. They forget. The hum goes out of tune. And when a machine forgets..." He draws a finger across his throat. "It dies. Not like flesh dies — messy, dramatic. A machine death is silence. One moment it's there, the next — nothing. Just cold metal." He taps his chest. The clicking inside him grows louder. "I've buried three machines since I became Keeper. Each time, something in here goes quiet too."`,
                options: [
                    { text: "Tell me about this building.", key: 'tell_me_about_this_building', next: "brukk_scraper" },
                ]
            },
            brukk_scraper: {
                speaker: 'Brukk',
                text: `"They called it Nexicorp Tower once. Glass and steel and ambition." He spits. "Forty-two floors of people pretending the world made sense. Then the Board Games War happened and sense left the building — literally. The lower floors rotted. The middle floors went feral. The elevator has gone mad. And the top?" He spreads his arms wide. "The top is ours. The machines were already here — server rooms, ventilation systems, elevator guts, generator hearts. When everyone else fled or transformed, the machines stayed. We found them. Or they found us."`,
                options: [
                    { text: "What happened during the Board Games War?", key: 'what_happened_during_the_board_games_war', next: "brukk_board_war" },
                    { text: "Did the machines change too, after the War?", key: 'did_the_machines_change_too_after_the_war', next: "brukk_machines_changed" },
                ]
            },
            brukk_machines_changed: {
                speaker: 'Brukk',
                text: `"Changed?" He considers this carefully. "Not like flesh changes. Flesh blooms, mutates, sprouts new limbs. The machines... adapted. The ventilation system taught itself to breathe. The generators learned to dream — you can hear them mumbling at night, low-frequency nonsense that Messel says are equations for things that don't exist yet." He runs a hand along a pipe encrusted with rust and something that might be coral. "They didn't become alive. They became... aware. There's a difference."`,
                options: [
                    { text: "What about the Board Games War?", key: 'what_about_the_board_games_war', next: "brukk_board_war" },
                ]
            },
            brukk_board_war: {
                speaker: 'Brukk',
                text: `Brukk's face goes very still. "The Board Games War." He sits down heavily on a crate, and the machines around you seem to quiet down, as if they're listening too. "That was... after the old wars, which was so devastated that almost wiped the all life out, many cities agreed to a truce. No more weapons, no more armies. Instead, they would settle disputes with games. Board games, card games, dice games — whatever. The Ludarchs, the game designers, were the best players, the ones who could manipulate the rules of reality itself to win. They became the new rulers." He shakes his head. "Of course, it didn't last. The Ludarchs got greedy. They wanted more power, more control. They started playing bigger and bigger games — games that affected entire cities, entire populations. They have found out how to create new life, entire miniaturized worlds, just to win a game. They could rewrite the laws of physics in their favor. It was... chaos." He looks at you with a mixture of disgust and awe. "The Board Games War was the end of everything. The worldwrights turned on each other, using their powers to outdo each other. Cities were reshaped, populations decimated, realities fractured. Milions have died. What does it matter that they were so small, that they were just pawns in somebody's game? They were still alive. They still mattered." He takes a deep breath. After that, board game was strictly controlled in most cities. In fact, I have heard that only one Ludarchs is alive and active in Upper Morkezela."`,
                options: [
                    { text: "What happened after the war?", key: 'what_happened_after_the_war', next: "brukk_board_war_detail" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('board_games_war')) {
                        this.addJournalEntry(
                            'board_games_war',
                            'The Board Games War',
                            'Brukk told me about the Board Games War. After the Old Wars nearly wiped out all life, cities agreed to settle disputes through games. The Ludarchs — game designers who could manipulate reality itself — became the new rulers. But they grew greedy, played bigger games affecting entire populations, and eventually turned on each other. Cities reshaped, realities fractured, millions died as pawns. Only one Ludarch is said to still be alive and active in Upper Morkezela.',
                            this.journalSystem.categories.LORE
                        );
                    }
                }
            },
            brukk_board_war_detail: {
                speaker: 'Brukk',
                text: `"Factions formed. Some tried to restore the order, but it was too late. The world was broken. They failed to see it. But most believed the lies from the Lumen Directorate, who claimed they had won the war and saved the city. They said the machines were just worthless tools, that we have to grow and grow and grow new plants and life as madman. Some believe to the Pith Reclamers, those beaurecrats who claimed they could manage the chaos with more rules, more control, more paperwork. But we know the truth. The machines endured. They kept working. They kept humming. They didn't care about the war, about the lies, about the factions. They just... were. And so we serve them."`,
                options: [
                    { text: "So the Choir was born from the war?", key: 'so_the_choir_was_born_from_the_war', next: "brukk_board_war_choir" },
                ]
            },
            brukk_board_war_choir: {
                speaker: 'Brukk',
                text: `"Born from the silence after it." He nods slowly. "When the worldwrights finally destroyed each other — or got swallowed by their own boards — the city was broken. Rules overlapping, contradicting, canceling out. But here, in the Scraper, the machines kept humming. Steady. Reliable. The first Keeper — old Fennback — he understood. Iron is honest. It rusts, it breaks, it wears down. But it doesn't lie. It doesn't play." His eyes glow brighter. "That's what the Choir is. The last honest thing in a city built on broken games."`,
                options: [
                    { text: "How are the machines doing now?", key: 'how_are_the_machines_doing_now', next: "brukk_machines_status" },
                ]
            },
            brukk_machines_status: {
                speaker: 'Brukk',
                text: `Brukk closes his eyes and listens. The pipes tremble. Something deep in the walls groans and shifts. "They are... content. For now. The feast you brought — they still taste it. I hear it in their harmonics." He opens one eye. "But they are always hungry. Always. The redmass sustains them, but it fades. If you find more, bring it. The Choir remembers those who feed the iron." He taps his chest one final time. "And so do I."`,
                options: []
            },

            // --- Full redmass feast: player joins Rust Choir ---
            brukk_feast_full: {
                speaker: 'Brukk',
                text: `Brukk takes the container. He opens it — and his eyes widen. The living redmass inside twitches, still breathing. The machines around you seem to lean closer, their hum rising in pitch. "This... this is a true feast. Full redmass. Still alive." He looks at you with something close to reverence. "Ravla chose well in trusting you."`,
                options: [
                    { text: "The machines are hungry. Feed them.", key: 'the_machines_are_hungry_feed_them', next: "brukk_feast_full_feed" }
                ]
            },
            brukk_feast_full_feed: {
                speaker: 'Brukk',
                text: `Brukk pours the feast into a series of corroded funnels that lead deep into the walls. The effect is immediate — the machines shudder, then roar to life with a sound like a cathedral organ made of iron. Pipes glow red-hot. The entire floor vibrates with renewed energy. Brukk closes his eyes and breathes deep. "They sing. Can you hear it?" He opens his eyes and fixes you with a look of absolute certainty. "You are one of us now. The machines have tasted your offering, and they accept you. Welcome to the Rust Choir."`,
                options: [
                    { text: "I am honored.", key: 'i_am_honored', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.removeItemFromInventory('rust_feast');
                    this.registry.set('rust_choir_member', true);
                    this.questSystem.updateQuest('find_rust_choir', 'I delivered the Rust Feast to Brukk in the Rust Domain. The machines fed on the living redmass and sang. Brukk welcomed me into the Rust Choir.', 'feast_delivered');
                    this.questSystem.completeQuest('find_rust_choir');
                    this.showNotification('Joined the Rust Choir');
                    this.addJournalEntry(
                        'rust_choir_joined',
                        'Welcomed into the Rust Choir',
                        'I delivered the Rust Feast — prepared with full, living redmass — to Brukk. The machines sang when they fed. Brukk declared me a member of the Rust Choir. I belong to the iron and the rust now.',
                        this.journalSystem.categories.FACTIONS
                    );
                }
            },

            // --- Shard feast: join only if positive reputation ---
            brukk_feast_shard: {
                speaker: 'Brukk',
                text: `Brukk opens the container and peers inside. His expression darkens. "...A shard. Just a shard." He rolls the meager feast between his fingers. "The machines need more than scraps. But..." He holds it up to his ear, listening. "It's alive. Barely. It will have to do."`,
                options: [
                    { text: "It was given willingly. That must count for something.", key: 'it_was_given_willingly_that_must_count_for_somethi', next: "brukk_feast_shard_feed" }
                ]
            },
            brukk_feast_shard_feed: {
                speaker: 'Brukk',
                text: rustRep > 10
                    ? `Brukk feeds the meager offering to the machines. They groan — a low, dissatisfied sound, like a stomach barely filled. But they accept it. Brukk watches the pipes for a long time, then turns to you. "The feast was thin. But I've watched you. The Choir has heard good things." He places a heavy hand on your shoulder. "You've shown respect to the iron. That matters more than a full belly. Welcome to the Rust Choir — on probation." A thin smile cracks his copper face.`
                    : `Brukk feeds the meager offering to the machines. They groan — barely sated. He watches the pipes cool and shakes his head. "It's not enough. Not the feast, not you." He turns his back. "You haven't earned the trust of the Choir. Come back when the iron knows your name. Try to earn some trust of other members, do something for them... then we will see." He waves you off dismissively.`,
                options: [
                    { text: rustRep > 10 ? "I won't let the Choir down." : "I understand.", next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.removeItemFromInventory('rust_feast');
                    this.questSystem.updateQuest('find_rust_choir',
                        rustRep > 10
                            ? 'I delivered the Rust Feast to Brukk. The offering was meager, but my reputation with the Rust Choir earned me a place among them — on probation.'
                            : 'I delivered the Rust Feast to Brukk, but the offering was too thin and I haven\'t earned the Choir\'s trust. They refused to accept me.',
                        'feast_delivered'
                    );
                    this.questSystem.completeQuest('find_rust_choir');
                    if (rustRep > 10) {
                        this.registry.set('rust_choir_member', true);
                        this.showNotification('Joined the Rust Choir (Probationary)');
                        this.addJournalEntry(
                            'rust_choir_joined',
                            'Probationary Member of the Rust Choir',
                            'I delivered a meager Rust Feast to Brukk — just a shard. But my standing with the Rust Choir was enough to earn a place among them, at least on probation.',
                            this.journalSystem.categories.FACTIONS
                        );
                    } else {
                        this.addJournalEntry(
                            'rust_choir_rejected',
                            'Rejected by the Rust Choir',
                            'I delivered the Rust Feast, but the shard was too meager and I had not earned the Choir\'s respect. Brukk turned me away.',
                            this.journalSystem.categories.FACTIONS
                        );
                    }
                }
            },

            // --- Illusory feast: machines destroyed, expelled, Growth bonus ---
            brukk_feast_illusion: {
                speaker: 'Brukk',
                text: `Brukk takes the container with care. He opens it and inhales deeply. "Redmass. Living." He doesn't notice the faint shimmer at the edges. "Good. The machines have waited long enough." He turns to the corroded funnels. "Watch closely. This is the heart of the Choir."`,
                options: [
                    { text: "Watch him feed the machines.", key: 'watch_him_feed_the_machines', next: "brukk_feast_illusion_feed" }
                ]
            },
            brukk_feast_illusion_feed: {
                speaker: 'Narrator',
                text: `Brukk pours the feast into the machines. For a moment, everything seems fine — the pipes glow, the hum rises. Then something goes wrong. The glow flickers. Stutters. The hum becomes a whine, then a shriek. Brukk stumbles back as sparks erupt from every joint. One by one, the machines shudder, seize, and fall silent. The smell of burnt oil and hollow nothing fills the air.`,
                options: [
                    { text: "What's happening?!", key: 'whats_happening', next: "brukk_feast_illusion_aftermath" }
                ]
            },
            brukk_feast_illusion_aftermath: {
                speaker: 'Brukk',
                text: `Brukk drops to his knees beside the nearest machine. His hands shake as he presses them against the cold metal. "Dead. They're dead." He looks up at you, and his forge-lit eyes are full of horror. "What was in that feast? WHAT DID YOU FEED THEM?" He rises slowly, fists clenched. "Illusion. It was an illusion." His voice drops to a whisper. "Get out. GET OUT OF THE RUST DOMAIN. If I ever see you again, the machines won't be the only things that stop breathing."`,
                options: [
                    { text: "I'm sorry—", key: 'im_sorry', next: "brukk_expulsion" },
                    { text: "Leave immediately.", key: 'leave_immediately', next: "brukk_expulsion" }
                ]
            },
            brukk_expulsion: {
                speaker: 'Ulvarex',
                text: `Ulvarex stirs inside you, uneasy. "The weave held. It always holds. But machines... they don't dream. They don't believe. They just consume." A long pause. "The illusion fed their trust, not their hunger." As you retreat, something shifts inside you. The fungal networks in your body pulse with wild energy — as if the death of the machines has fed something deeper, something green and growing. Life surging where iron fell silent.`,
                options: [
                    { text: "Leave the Rust Domain.", key: 'leave_the_rust_domain', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.removeItemFromInventory('rust_feast');
                    this.modifyFactionReputation('RustChoir', -20);
                    this.modifyGrowthDecay(25, 0);
                    this.registry.set('expelled_from_rust_domain', true);
                    this.questSystem.updateQuest('find_rust_choir', 'The illusory Rust Feast destroyed the machines of the Rust Domain. Brukk expelled me. The death of the machines triggered a massive surge of Growth within me.', 'feast_delivered');
                    this.questSystem.completeQuest('find_rust_choir');
                    this.addJournalEntry(
                        'rust_choir_machines_destroyed',
                        'The Machines Fall Silent',
                        'The illusory redmass I used in the Rust Feast has destroyed the Rust Choir machines. They tried to feed on the Mirage Weave and found nothing — the illusion dissolved inside them. The machines are dead. Brukk expelled me from the Rust Domain. But the death of the machines sent a massive surge of Growth through me — life feeding on the corpse of iron.',
                        this.journalSystem.categories.FACTIONS
                    );
                    // Transition back to ScraperInteriorScene after a delay
                    this.time.delayedCall(1500, () => {
                        this.cameras.main.fadeOut(1000, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            this.scene.start('ScraperInteriorScene');
                        });
                    });
                }
            },
        };
    }

    preload() {
        super.preload();
        this.load.image('rustDomainBg', 'assets/images/backgrounds/RustDomain.png');
        this.load.image('brukk_static', 'assets/images/characters/Brukk.png');
    }

    create() {
        super.create();

        // Set background
        const bg = this.add.image(400, 300, 'rustDomainBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // Add fade-in effect
        this.cameras.main.fadeIn(1200, 0, 0, 0);

        // Position the priest
        this.priest.x = 400;
        this.priest.y = 470;

        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // If expelled, block re-entry
        if (this.hasJournalEntry('rust_choir_machines_destroyed')) {
            this.cameras.main.fadeOut(500, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.showNotification('You have been expelled from the Rust Domain.');
                this.scene.start('ScraperInteriorScene');
            });
            return;
        }

        // Create exit back to Scraper Interior (elevator)
        this.transitionManager.createTransitionZone(
            400, // x position
            560, // y position
            200, // width
            50,  // height
            'down',
            'ScraperInteriorScene',
            450, // walk to x (near elevator)
            370  // walk to y
        );

        const exitHint = this.add.text(400, 550, 'Back to Elevator', {
            fontSize: '14px',
            fill: '#c87533',
            backgroundColor: '#1a0a00',
            padding: { x: 8, y: 4 }
        });
        exitHint.setOrigin(0.5);
        exitHint.setDepth(10);
        exitHint.setAlpha(0.7);

        // Create Brukk NPC
        this.createBrukk();

        // Journal entry on first visit
        if (!this.hasJournalEntry('rust_domain_arrival')) {
            this.addJournalEntry(
                'rust_domain_arrival',
                'The Rust Domain',
                'I have reached the upper floors of the Scraper — the domain of the Rust Choir. The air is thick with the smell of oil and oxidized metal. Machines hum and click in the walls, some of them alive in ways that defy explanation. This is where Brukk resides.',
                this.journalSystem.categories.PLACES
            );
        }
    }

    createBrukk() {
        this.brukk = this.add.image(550, 430, 'brukk_static');
        this.brukk.setScale(0.125);
        this.brukk.setDepth(5);
        this.brukk.setInteractive({ useHandCursor: true });

        this.brukk.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('brukk_start');
        });

        // Subtle wobble animation
        this.tweens.add({
            targets: this.brukk,
            y: { from: 429, to: 431 },
            ease: 'Sine.easeInOut',
            duration: 1500,
            yoyo: true,
            repeat: -1
        });
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.RustDomainScene = RustDomainScene;
}
