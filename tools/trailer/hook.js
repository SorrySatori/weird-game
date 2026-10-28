// Runs after phaser.min.js, before main.js: UI language from --lang (English by default), no audio decoding (music is muxed in post),
// fixed-step timing, and the Game instance exposed as window.__game for the director.
(() => {
    try { localStorage.setItem('gameLanguage', window.__cap?.args?.lang || 'en'); } catch (e) { /* in-memory partition */ }
    const BaseGame = Phaser.Game;
    Phaser.Game = class TrailerGame extends BaseGame {
        constructor(config) {
            config.audio = { noAudio: true };
            config.fps = { ...(config.fps || {}), smoothStep: false };
            config.render = { ...(config.render || {}), preserveDrawingBuffer: true };
            super(config);
            window.__game = this;
        }
    };
})();
