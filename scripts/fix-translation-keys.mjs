/**
 * Fix mismatched translation keys by mapping abbreviated keys to full scene keys.
 * Also adds the manual keys for edge cases (ternary text, dynamic push).
 * Usage: node scripts/fix-translation-keys.mjs
 */
import fs from 'fs';

const fixes = {
    'lang/cs/dialogs/LumenDirectorateInteriorScene.js': {
        'growth_is_change': 'growth_is_change_becoming_something_you_werent_bef',
        'growth_is_survival': 'growth_is_survival_spreading_to_ensure_you_endure',
    },
    'lang/cs/dialogs/LumenDirectorateScene.js': {
        'i_was_told_to_come_here': 'i_was_told_to_come_here_about_joining_the_crew',
        'i_need_to_get_into_the_townhall': 'i_need_to_get_into_the_townhall_any_ideas',
        'im_looking_into_spiced_sulkberries': 'im_looking_into_spiced_sulkberries_who_supplies_th',
        'captain_liris_sent_me': 'captain_liris_sent_me_thats_my_reason',
        'im_here_about_the_bishops_dealings': 'im_here_about_the_bishops_dealings_with_the_direct',
    },
    'lang/cs/dialogs/RustDomainScene.js': {
        'i_wont_let_the_choir_down': 'feast_shard_response',
        'i_understand': 'feast_shard_response',
    },
    'lang/cs/dialogs/ScraperInteriorScene.js': {
        'i_have_a_button': 'i_have_a_button_that_belongs_here_maybe_its_been_l',
        'ive_a_tool': 'ive_a_tool_to_repair_your_floor_counter_perhaps_yo',
        'i_know_the_bishops_secret': 'i_know_the_bishops_secret_its_important_to_reach_d',
    },
    'lang/cs/dialogs/ScreamingCorkScene.js': {
        'i_think_we_have_enough_topics': 'i_think_we_have_enough_topics',
        'lets_continue': 'lets_continue',
    },
    'lang/cs/dialogs/ShedRegistrationScene.js': {
        'hi_who_are_you': 'hi_who_are_you_i_used_to_play_like_this_as_well_wh',
        'err_i_am_at_the_right_place': 'err_i_am_at_the_right_place_can_you_help_my_friend',
        'keep_your_vowels': 'keep_your_vowels_i_speak_in_spore_alphabet',
        'well_i_guess_you_should_stop_waiting': 'well_i_guess_you_should_stop_waiting_i_am_sure_you',
        'what_happened_to_those_people': 'what_happened_to_those_people_i_was_talking_to',
    },
};

let totalFixes = 0;

for (const [filePath, keyMap] of Object.entries(fixes)) {
    let content = fs.readFileSync(filePath, 'utf8');
    let fileFixes = 0;
    
    for (const [oldKey, newKey] of Object.entries(keyMap)) {
        if (oldKey === newKey) continue; // Already correct (ScreamingCork)
        
        // For RustDomainScene, two old keys map to one new key
        // Handle duplicate: if both i_wont_let_the_choir_down and i_understand map to feast_shard_response,
        // keep only one entry
        if (content.includes(`${oldKey}:`)) {
            // Check if the new key already exists to avoid duplicates
            if (content.includes(`${newKey}:`)) {
                // Just remove the old entry
                content = content.replace(new RegExp(`\\s*${oldKey}:.*\\n`, 'g'), '\n');
            } else {
                content = content.replace(
                    new RegExp(`(\\s*)${oldKey}(\\s*:)`),
                    `$1${newKey}$2`
                );
            }
            fileFixes++;
        }
    }
    
    if (fileFixes > 0) {
        fs.writeFileSync(filePath, content);
        console.log(`${filePath}: fixed ${fileFixes} keys`);
        totalFixes += fileFixes;
    }
}

console.log(`\nTotal fixes: ${totalFixes}`);
