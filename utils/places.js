/**
 * Journal entries for the city's main places (the journal's Places tab), written the first time the player walks into
 * one: `notePlace(this, 'place_shed_521')` in the scene's create(). Each says only what he sees on arrival — anything
 * learned later is a fact added where it is learned (addJournalFact). The English is stored with the entry; the
 * translations are `journal.<id>.title / description` in lang/<code>/journal.js.
 */
const PLACES = {
    place_crossroads: {
        title: 'The Crossroads',
        text: "The city's streets meet here, around the body of a giant. It has lain here a long time, yet it doesn't smell; it hardly even looks dead. The locals walk past it as if it were a monument. From here the ways lead to the Shed, the Voxmarket, the Scraper and the Egg Cathedral.",
    },
    place_shed_521: {
        title: 'Shed 521',
        text: "An old warehouse in a former shipping yard that grew into an office: the Bureau of Shapes. People come here to register the shape they are in, or to apply to change it. Queues, counters and forms on three floors. The paperwork seems to grow on its own.",
    },
    place_voxmarket: {
        title: 'The Voxmarket',
        text: "A market of sounds in an old airship hangar. Voices, noises and memories are sold here sealed in glass, and the stalls play other people's conversations over and over. Not everything on offer is entirely legal.",
    },
    place_verdigrace: {
        title: 'The Verdigrace',
        text: "Captain Liris's skyship. It hangs motionless above the Crossroads; its hull is overgrown with plants and its sails look grown rather than sewn. From up here the city looks almost small.",
    },
    place_egg_cathedral: {
        title: 'The Egg Cathedral',
        text: "A cathedral growing out of a gigantic egg, or still hatching from it. The shell glows faintly from within, as if something inside were breathing.",
    },
    place_burning_bear_street: {
        title: 'Burning Bear Street',
        text: "A street that joins the Scraper to the Screaming Cork and the Townhall. Its name sounds like a festival nobody wants to explain to a stranger.",
    },
};

/** write the place's journal entry the first time he comes here */
export function notePlace(scene, id) {
    const place = PLACES[id];
    if (!place || !scene.journalSystem || scene.hasJournalEntry?.(id)) return;
    scene.addJournalEntry(id, place.title, place.text, scene.journalSystem.categories.PLACES, { location: place.title });
}
