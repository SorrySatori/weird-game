// Thaal's equipment tutorial closed the player's way: every panel shut with its key or ESC instead of the tutorial's
// own button (that used to leave the tutorial waiting and the game locked). English texts are matched.
//   ./tools/trailer/capture.sh --test tutorial_keys
export default async function ({ game, cap, enter, wait }) {
    const sc = await enter('EntryScene'); await wait(3);
    if (sc.dialogVisible) sc.hideDialog();
    const tap = async (code, keyCode) => {
        window.dispatchEvent(new KeyboardEvent('keydown', { code, key: code === 'Escape' ? 'Escape' : code.replace('Key', '').toLowerCase(), keyCode, bubbles: true }));
        await wait(0.12);
        window.dispatchEvent(new KeyboardEvent('keyup', { code, key: code === 'Escape' ? 'Escape' : code.replace('Key', '').toLowerCase(), keyCode, bubbles: true }));
        await wait(0.8);
    };
    const texts = () => game.scene.scenes.filter(s => s.sys.settings.status === Phaser.Scenes.RUNNING).flatMap(s => {
        const out = []; const walk = l => l.forEach(o => { if (o.type === 'Text' && o.visible) out.push(o.text); if (o.list) walk(o.list); }); walk(s.children.list); return out; });
    const has = (frag) => texts().some(t => t.includes(frag));
    const primary = () => {   // the caption's first (primary) button
        for (const s of game.scene.scenes.filter(s => s.sys.settings.status === Phaser.Scenes.RUNNING)) {
            const c = s.children.list.find(o => o.type === 'Container' && o.depth === 6001);
            const r = c?.list.find(o => o.type === 'Rectangle' && o.input);
            if (r) return r;
        }
    };
    const log = (m, ok) => cap.log(`${ok ? 'PASS' : 'FAIL'} ${m}`);
    // as a player: Thaal's offer, "Yes please, Master."
    await wait(3);
    sc.showDialog('tutorialOffer'); await wait(0.3);
    sc._dialogModel.options[0].activate(); await wait(1.2);

    log('journal step asks to open it', has('This is your diary'));
    await tap('KeyJ', 74); log('journal open, its explanation shows', has('It gathers everything'));
    await tap('KeyJ', 74); log('closed with J -> quest log step', has('Your quest log sits beside'));
    sc.questLog.showQuestLog(); await wait(0.8); log('quest log open, explanation', has('Active quests and their progress'));
    await tap('Escape', 27); log('closed with ESC -> map step', has('The fast-travel map'));
    await tap('KeyM', 77); log('map open, explanation', has('Click any place you'));
    await tap('KeyM', 77); log('closed with M -> lantern step', has('Lost? The lantern'));
    for (const f of ['That gauge up top', 'Growth and Decay', 'Your inventory']) { primary()?.emit('pointerdown'); await wait(0.6); log(`Next -> "${f}"`, has(f)); }
    await tap('KeyI', 73); log('inventory open, explanation', has('Whatever you find'));
    await tap('KeyI', 73); log('closed with I -> the last words', has("And that's the lot"));
    primary()?.emit('pointerdown'); await wait(0.6);
    log('Done: the tutorial is over, the game free again', !sc._tutorialActive && sc.registry.get('equipment_tutorial_done') && !sc.isModalOpen());
}
