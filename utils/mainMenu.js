/**
 * Leaving a running game for the main menu.
 *
 * The game keeps its state in singletons (JournalSystem), the registry (quests, inventory, visited places, flags…)
 * and in scene instances Phaser re-uses -- switching to MainScene left all of it (and the scene's music) alive, so
 * "New Game" continued the old playthrough and two tracks played at once. A fresh page drops everything; only
 * localStorage survives (saves, the chosen language). LoadingScene skips its splash after such a reload.
 */
export function returnToMainMenu(scene) {
    if (typeof window === 'undefined' || !window.location) {      // no page to reload (tests): the old way
        scene.sound?.stopAll();
        scene.scene.start('MainScene');
        return;
    }
    try { sessionStorage.setItem('skipSplash', '1'); } catch (e) { /* storage blocked: the splash just shows */ }
    const reload = () => window.location.reload();
    const cam = scene.cameras?.main;
    if (cam) {
        cam.fadeOut(400, 0, 0, 0);
        cam.once('camerafadeoutcomplete', reload);
        scene.time?.delayedCall(700, reload);                        // in case the fade never reports back
    } else {
        reload();
    }
}
