const { FusesPlugin } = require('@electron-forge/plugin-fuses');
const { FuseV1Options, FuseVersion } = require('@electron/fuses');

module.exports = {
  packagerConfig: {
    asar: true,
    // Only ship what the game needs at runtime. Everything below is dev tooling,
    // docs, old packaging experiments or build output (dist/ alone is ~2 GB).
    ignore: [
      /^\/\.git(\/|$)/,
      /^\/\.github(\/|$)/,
      /^\/\.claude(\/|$)/,
      /^\/\.vscode(\/|$)/,
      /^\/dist(\/|$)/,
      /^\/out(\/|$)/,
      /^\/build(\/|$)/,
      /^\/scripts(\/|$)/,
      /^\/tools(\/|$)/,                   // art generators + trailer capture (trailer output alone is ~650 MB)
      /^\/assets\/aseprite(\/|$)/,        // editable sources; the game loads only the exported PNGs
      /^\/dialog-review(\/|$)/,
      /^\/steam-build-[^/]+(\/|$)/,
      /^\/weird-game-neutralino(\/|$)/,
      /^\/node_modules\/canvas(\/|$)/,   // native module used only by the asset scripts below
      /^\/node_modules\/\./,              // npm leftovers (.ignored, .package-lock.json, …)
      // phaser: index.html loads only dist/phaser.min.js; drop src/types/plugins/docs (~140 MB)
      /^\/node_modules\/phaser\/(?!dist$|dist\/phaser\.min\.js$|package\.json$)/,
      /^\/(extract-sprite|generate-market-ground|make-transparent)\.js$/,
      /^\/[^/]+\.(md|zip|log|tar\.gz|AppImage|deb|rpm|exe)$/,
      /^\/package-lock\.json$/,
    ],
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {},
    },
    {
      name: '@electron-forge/maker-zip',
      platforms: ['darwin'],
    },
    {
      name: '@electron-forge/maker-deb',
      config: {},
    },
    {
      name: '@electron-forge/maker-rpm',
      config: {},
    },
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-auto-unpack-natives',
      config: {},
    },
    // Fuses are used to enable/disable various Electron functionality
    // at package time, before code signing the application
    new FusesPlugin({
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
      [FuseV1Options.OnlyLoadAppFromAsar]: true,
    }),
  ],
};
