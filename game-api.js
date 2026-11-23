/**
 * game-api.js - the game's save / load API (window.gameAPI), loaded before the game.
 *
 * In Electron the saves are JSON files on disk (preload.js window.saveFiles → electron-main.js "saves:*"), in the
 * folder Steam Cloud syncs. In a plain browser (http-server dev) they stay in localStorage.
 * Saves made before 2026-11 live in localStorage in Electron too; they are moved to files on the first start.
 */

// in a function: a top-level `const saveFiles` would clash with the window.saveFiles the preload's contextBridge
// defines (a non-configurable global), and the whole file would fail to load
(() => {
  const SAVE_KEY_PREFIX = 'weird-game-save-';
  const saveFiles = window.saveFiles || null;

  /** the date a save was made, from inside it (Load panel); the save's own text, so a broken one says so */
  function describeSave(name, text) {
    try {
      const data = JSON.parse(text);
      return { name, date: new Date(data.timestamp || data.metadata?.savedAt || 0), size: text.length, scene: data.currentScene || null };
    } catch (error) {
      return { name, date: new Date(0), size: text.length, error: true };
    }
  }

  function localStorageSaveKeys() {
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(SAVE_KEY_PREFIX)) keys.push(key);
    }
    return keys;
  }

  /**
   * Move the old localStorage saves to files, once. A slot that already has a file (e.g. one Steam Cloud brought from
   * another computer) keeps the file; the old copy then stays unused in localStorage.
   */
  function migrateLocalStorageSaves() {
    if (!saveFiles) return;
    try {
      const keys = localStorageSaveKeys();
      if (!keys.length) return;
      const listed = saveFiles.list();
      if (!listed?.success) return;
      const existing = new Set(listed.files.map(file => file.name));
      for (const key of keys) {
        const slot = key.slice(SAVE_KEY_PREFIX.length);
        if (existing.has(slot)) continue;
        const result = saveFiles.write(slot, localStorage.getItem(key));
        if (result?.success) localStorage.removeItem(key);
        else console.error(`Save "${slot}" could not be moved to a file:`, result?.error);
      }
    } catch (error) {
      console.error('Moving the old saves to files failed:', error);
    }
  }

  window.gameAPI = {
    getAppVersion: () => '1.0.0',

    saveGame: (saveData, slotName = 'save1') => {
      try {
        const json = JSON.stringify(saveData);
        if (saveFiles) return saveFiles.write(slotName, json);
        const saveKey = `${SAVE_KEY_PREFIX}${slotName}`;
        localStorage.setItem(saveKey, json);
        return { success: true, path: saveKey };
      } catch (error) {
        console.error('Failed to save game:', error);
        return { success: false, error: error.message };
      }
    },

    loadGame: (slotName = 'save1') => {
      try {
        let text;
        if (saveFiles) {
          const result = saveFiles.read(slotName);
          if (!result?.success) return { success: false, error: result?.error || 'Save file not found' };
          text = result.text;
        } else {
          text = localStorage.getItem(`${SAVE_KEY_PREFIX}${slotName}`);
          if (text === null) return { success: false, error: 'Save file not found' };
        }
        return { success: true, data: JSON.parse(text) };
      } catch (error) {
        console.error('Failed to load game:', error);
        return { success: false, error: error.message };
      }
    },

    /** { success, files: [{ name, date: Date, size, scene, error? }] } */
    listSaveFiles: () => {
      try {
        if (saveFiles) {
          const result = saveFiles.list();
          if (!result?.success) return { success: false, error: result?.error || 'Listing saves failed' };
          return { success: true, files: result.files.map(file => ({ ...file, date: new Date(file.date) })) };
        }
        const files = localStorageSaveKeys().map(key =>
          describeSave(key.slice(SAVE_KEY_PREFIX.length), localStorage.getItem(key)));
        return { success: true, files };
      } catch (error) {
        console.error('Failed to list save files:', error);
        return { success: false, error: error.message };
      }
    },

    deleteSaveFile: (slotName) => {
      try {
        if (saveFiles) return saveFiles.remove(slotName);
        const saveKey = `${SAVE_KEY_PREFIX}${slotName}`;
        if (localStorage.getItem(saveKey) === null) return { success: false, error: 'Save file not found' };
        localStorage.removeItem(saveKey);
        return { success: true };
      } catch (error) {
        console.error('Failed to delete save file:', error);
        return { success: false, error: error.message };
      }
    }
  };

  migrateLocalStorageSaves();
})();
