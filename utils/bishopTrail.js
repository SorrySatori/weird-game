/**
 * The main quest's "where did the Bishop go" stories. The Lift-Mother lets the player up to Dr. Elphi when two agree
 * (Kloor's and one from Shed 521), and Zerren pitches his lift button once one of them is known.
 *
 * Shed 521's story comes from Gnur when he gets the living core -- or, if the player refused him, from the
 * Applications clerk: the Ink Tribunal's records show the Bishop's visitor permit for Dr. Elphi's floor (same weight).
 */
export const SHED_STORY_KEYS = ['core_delivered'];             // rust_reclamation update: Gnur got the core and talked
export const CLERK_STORY_KEY = 'bishop_elphi_clerk';           // find_bishop update: the clerk showed the records

const hasUpdate = (quest, key) => !!quest?.updates?.some(u => u.key === key);

/** Gnur refused (the quest ended without the core changing hands) */
export const gnurRefused = (qs) => !!qs?.getQuest('rust_reclamation')?.isComplete && !hasUpdate(qs.getQuest('rust_reclamation'), 'core_delivered');

/** the clerk already showed the Tribunal's records */
export const clerkToldBishop = (qs) => hasUpdate(qs?.getQuest('find_bishop'), CLERK_STORY_KEY);

/** the player has Shed 521's story of the Bishop going to Dr. Elphi (from Gnur, or from the clerk) */
export const knowsShedStory = (qs) => hasUpdate(qs?.getQuest('rust_reclamation'), 'core_delivered') || clerkToldBishop(qs);

/** Kloor's story (the vestigel deal) */
export const knowsKloorStory = (qs) => !!qs?.getQuest('the_three_vestigels')?.isComplete;
