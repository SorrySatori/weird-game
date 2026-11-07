/**
 * English text for the "examine" / observation mechanic — the protagonist's own words when
 * the player clicks a significant location or inanimate object. Keyed as observe.<id>.<variant>.
 * Variants are context tiers the scene chooses between (more-informed states take priority).
 */
export default {
    observe: {
        crossroads: {
            hint: 'The Crossroads',
            default: "Four roads, and every one of them leads somewhere that wants something from me: the Shed, the Voxmarket, the Scraper. A dead giant makes a poor signpost, but definitely memorable.",
            overgrown: "The junction's greening over. Roots have found the seams between the cobbles and decided the roads belong to them now. Give it a season and there won't be a visible piece of the road.",
            planted: "I put spores in the dead giant, and the crossroads have changed. Whatever's pushing up through the stones now, I started it. I try not to think about what it'll be when it's finished.",
        },
        egg_cathedral: {
            hint: 'The Glow',
            default: "Light seeps through the glass above the door. Warm, even from here.",
        },
        egg_cathedral_approach: {
            hint: 'Egg Cathedral',
            default: "A cathedral growing from a giant egg. A dome of shell where the roof should be. Something here is very close to being born, and the architecture is just the nest it settled for.",
        },
        scraper: {
            hint: 'Scraper 1140',
            default: "Nexicorp Tower, they used to call it. Now they call it Scraper and nobody knows all its floors.",
            been_inside: "I've been up in it and I still don't know what to think about the Scraper. From out here it almost passes for architecture.",
        },
        screaming_cork: {
            hint: 'The Screaming Cork',
            default: "A drinking-house with its name shouted in old, peeling paint. People come here, maybe to forget, maybe just to let off some steam. In any case, it looks like a popular spot.",
            knows_noise: "After witnessing Feral Toast's rehearsal, I discovered something unexpected here. The Screaming Cork doesn't just offer intoxicants of all kinds and good conversation; here, you can also experience a manifestation of an entity for which I've coined the working title 'Noise God.'",
        },
        voxmarket: {
            hint: 'The Voxmarket',
            default: "Every stall here sells something that used to be alive, and the vendors haggle in a dozen dialects. If a thing makes some sound in Upper Morkezela, someone at the Voxmarket has a price for it.",
            knows_vestigels: "Somewhere in this racket the alive-coins change hands: Vestigels, worth more than gold and stranger than economics itself. Kloor would give his teeth to study one.",
        },
        shed_pipes: {
            hint: 'Shed 521',
            default: "The architecture of this building can be described as the result of a party after which a pipe and a pile of scrap wood had a child. Bureaucrats wrote off this entire masterpiece as a 'structural problem,' then bought it (very cheaply) and moved in.",
        },
        skyship_board: {
            hint: 'The Skyship Board',
            default: "A cold wind is blowing aboard the airship Verdigrace, but the view is breathtaking. All around, strange devices are ticking away, though they don't seem to be mechanical in origin; they look as if they've been grown.",
            knows: "I took the floor-counter from here. It's the one instrument honest enough to admit the Scraper has floors that shouldn't exist.",
        },
    },
};
