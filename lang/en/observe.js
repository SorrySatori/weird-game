/**
 * English text for the "examine" / observation mechanic — the protagonist's own words when
 * the player clicks a significant location or inanimate object. Keyed as observe.<id>.<variant>.
 * Variants are context tiers the scene chooses between (more-informed states take priority).
 */
export default {
    observe: {
        stomach_clock: {
            hint: 'Stomach Clock',
            default: "A clock the size of a house, and it's... breathing. The face is bone; the hands are something wet and organic. Whatever keeps time in this city, it isn't seconds.",
            heard: "So this is the famous Stomach Clock Thaal told me about. The real stomach of the first god who came here to die — or a poor copy of some other town's clock, depending on who's telling it. Standing under it, watching it digest, I know which story I believe. And I'm in no hurry to test whether the bile is as healthy as they say.",
            digestions: "Digestions, the Sentinel called them. Standing here, watching the thing chew its way through another one, I finally know what he was counting — and that this city has been keeping time by its own stomach the whole while.",
            been_inside: "I've stood inside its gut. Knowing what the thing up there is actually digesting doesn't make it easier to look at — it makes it worse.",
        },
        crossroads: {
            hint: 'The Crossroads',
            default: "Four roads, and every one of them leads somewhere that wants something from me — the Shed, the Voxmarket, the Scraper. A dead giant makes a poor signpost, but definitely memorable.",
            overgrown: "The junction's greening over. Roots have found the seams between the cobbles and decided the roads belong to them now. Give it a season and there won't be a visible piece of the road.",
            planted: "I put spores in the dead giant, and the crossroads have changed. Whatever's pushing up through the stones now, I started it. I try not to think about what it'll be when it's finished.",
        },
        godgraveyard: {
            hint: 'The Fallen God',
            default: "A face the size of a house, half-swallowed by the mud — and it is unmistakably a *face*. Whatever died here was worshipped once. Standing in its eyeline, even dead, feels like trespassing.",
            knows: "Phor calls this divinography — reading gods by their fossils. Now that I know to look, the whole field is a graveyard of the enormous: eyes, crowns, mouths that used to be prayed into. This one just has the manners to still look surprised.",
            osswine: "Osswine stirs the moment I look at it. *The big dead are not as dead as the small dead*, it says — and reads the god's ending straight off the bone: not killed, just outvoted. Believed out of existence. The grave-sense clings to it like breath on cold glass.",
        },
        egg_cathedral: {
            hint: 'The Glow',
            default: "Light seeps through the glass above the door. Warm, even from here.",
            knows: "I've been in the cellar and met the mind this egg is keeping warm. Knowing what's folded up inside doesn't make the light any less beautiful — it just makes me want to be somewhere else when it hatches.",
            ortolan: "Ortolan said it plainly: a thing can be beautiful and still be badly made, the flaw baked right into the beauty. Now I can't unsee it — that gorgeous light, and a design error running clean through the middle of it.",
        },
        egg_cathedral_approach: {
            hint: 'Egg Cathedral',
            default: "A cathedral growing from a giant egg — a dome of shell where the roof should be. Something here is very close to being born, and the architecture is just the nest it settled for.",
            knows: "I've been down in its cellar; I know the mind that is growing there.",
            ortolan: "Ortolan called it a flawed make — beautiful and broken in the same stroke.",
        },
        scraper: {
            hint: 'Scraper 1140',
            default: "Nexicorp Tower, they used to call it. Now they call it Scraper and nobody knows all its floors.",
            been_inside: "I've been up in it and I still don't know what to think about the Scraper. From out here it almost passes for architecture.",
            knows_cellar: "Everyone cranes up at the Scraper. The thing that matters is at the bottom: the sealed cellar where Ortolan and Elphi built their unfinished game, still humming down there in the dark. All these floors, and the answer's in the basement.",
        },
        rust_machines: {
            hint: "The Choir's Machines",
            default: "Red light pooling in old boilers, cables strung like veins across the floor, the whole room humming at a pitch I feel in my teeth. Whatever the Rust Choir worships, it's still plugged in.",
            member: "The machines know my step now. That low hum used to read as a warning; now it reads like a room going quiet when family walks in. I'm not sure which of those should frighten me more.",
            destroyed: "Silent. Cold. The red's gone out of the boilers and the cables just lie there, like something that stopped mid-sentence. I did this. The Choir will spend a long time not forgiving it — and so, quietly, will I.",
        },
        airship: {
            hint: 'The Airship',
            default: "A dirigible, drifting low over the ruins like it has all the time in the world. Nobody down here ever seems to be on it, and it never seems to land. Just circles, patient, watching the city not-quite-live.",
            knows: "I've been up on that thing — the skyship, with its board that counts floors no building admits to having. Strange, seeing it from below now, knowing the view is even less honest from above.",
        },
        yolk_sea: {
            hint: 'The Yolk Sea',
            default: "The Yolk Sea — a slab of standing yellow that doesn't so much reflect the light as hold it, thick and warm. Things drift in it that never quite finish being fish. The tide moves like something breathing in its sleep.",
            met_heir: "This is where the Heir comes when no auction claims them — where unfinished things are allowed to keep moving. Looking at the Yolk Sea now, I understand it less as water and more as a waiting room with no far door.",
            ulvarex: "Ulvarex stirs behind my eyes the moment I look at the water. This is the puddle it rode in on — and the reflection still isn't honest. The sea shows me a horizon that's a few degrees wrong, just to see if I'll notice.",
        },
        lumen_architecture: {
            hint: 'The Living Directorate',
            default: "Every stone of it is throttled in green — ivy fed and pruned into the shape of a cathedral, lit from inside like it's swallowed a sunrise. 'Nothing hidden, nothing lost.' A building that grows its own walls has a lot of places to hide things.",
            overgrown: "The green has stopped being decoration. It's eating the architecture now — windows going leaf-blind, arches disappearing under a bloom nobody's pruning back. The Directorate wanted growth. Growth doesn't take requests.",
            joined: "I'm inside this now, more or less. The light that looks so warm from the path is the same light that files everything it touches. Belonging to a place that keeps perfect records is a colder feeling than I expected.",
        },
        screaming_cork: {
            hint: 'The Screaming Cork',
            default: "A drinking-house with its name shouted in old, peeling paint. People come here, maybe to forget, maybe just to let off some steam. In any case, it looks like a popular spot.",
            knows_noise: "After witnessing Feral Toast's rehearsal, I discovered something unexpected here. The Screaming Cork doesn't just offer intoxicants of all kinds and good conversation; here, you can also experience a manifestation of an entity for which I've coined the working title 'Noise God.'",
        },
        voxmarket: {
            hint: 'The Voxmarket',
            default: "Every stall here sells something that used to be alive, and the vendors haggle in a dozen dialects. If a thing makes some sound in Upper Morkezela, someone at the Voxmarket has a price for it.",
            knows_vestigels: "Somewhere in this racket the alive-coins change hands — Vestigels, worth more than gold and stranger than economics itself. Kloor would give his teeth to study one.",
        },
        shed_pipes: {
            hint: 'Shed 521',
            default: "The architecture of this building can be described as the result of a party after which a pipe and a pile of scrap wood had a child. Bureaucrats wrote off this entire masterpiece as a 'structural problem,' then bought it (very cheaply) and moved in.",
            member: "The choir is trying to infiltrate the Shed. Now that I'm singing with them, rust seems less like a problem and more like a slow, patient healing process.",
        },
        redmass_island: {
            hint: 'The Redmass',
            default: "The whole island is one slow red muscle, breathing. Not an animal, not a plant — the city's raw material before the city decided what to make of it. It notices me. I'd swear it notices me.",
            spared: "I left the redmass alive when I could have carved it. Still here, still breathing — and I don't regret it, even if it made the Rust Feast poorer and Brukk colder. Some things shouldn't be spent just because they can be.",
            collected: "I took what I needed from the redmass. It's quieter now where I cut, the red gone grey at the edges. It was always going to be spent for something. I keep trying to believe the something was worth it.",
        },
        echo_drain: {
            hint: 'Echo Drain Delta',
            default: "Where the city's runoff fans out into a delta of scrap and silt. Everything Upper Morkezela flushes ends up here, sorted by weight and forgotten. It's almost peaceful — the peace of a place nobody chose to be.",
            knows: "Magnekin was right — the delta's thick with metal scrap if you know to sift for it. Funny that the thing pretending hardest to be a man is the one who knows exactly where the city keeps its bones.",
        },
        godgraveyard_gate: {
            hint: 'The Godgraveyard Gate',
            default: "A gate, and past it a fog that swallows sound. Whatever's buried beyond doesn't want visitors, and the Townhall agrees — the way through is paperwork, not courage. I can feel the size of the things on the other side without seeing one.",
            knows: "Phor's whole life is on the far side of this gate: reading dead gods by their fossils. He calls the locked door an insult. I'm starting to think it's the only thing keeping the graveyard from reading *us* back.",
        },
        abandoned_bus: {
            hint: 'The Abandoned Bus',
            default: "A bus that stopped running for a route that stopped existing. Something's been living in it — the seats are worn in the shapes of the wrong number of bodies. It still smells faintly of a journey that never arrived.",
        },
        skyship_board: {
            hint: 'The Skyship Board',
            default: "A cold wind is blowing aboard the airship Verdigrace, but the view is breathtaking. All around, strange devices are ticking away — though they don't seem to be mechanical in origin; they look as if they've been grown.",
            knows: "I took the floor-counter from here — the one instrument honest enough to admit the Scraper has floors that shouldn't exist.",
        },
    },
};
