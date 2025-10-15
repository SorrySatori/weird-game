/**
 * game-api.js - Provides a browser-compatible API for game save/load functionality
 * This script should be included before the game loads
 */

// Check if we're running in Electron
const isElectron = typeof window !== 'undefined' && window.process && window.process.type === 'renderer';

// Create a browser-compatible API that uses localStorage when not in Electron
window.gameAPI = {
  getAppVersion: () => '1.0.0',
  
  // Save game data
  saveGame: (saveData, slotName = 'save1') => {
    try {
      if (isElectron && window.electronAPI) {
        return window.electronAPI.saveGame(saveData, slotName);
      } else {
        // Browser implementation using localStorage
        const saveKey = `weird-game-save-${slotName}`;
        localStorage.setItem(saveKey, JSON.stringify(saveData));
        return { success: true, path: saveKey };
      }
    } catch (error) {
      console.error('Failed to save game:', error);
      return { success: false, error: error.message };
    }
  },
  
  // Load game data
  loadGame: (slotName = 'save1') => {
    try {
      if (isElectron && window.electronAPI) {
        return window.electronAPI.loadGame(slotName);
      } else {
        // Browser implementation using localStorage
        const saveKey = `weird-game-save-${slotName}`;
        const saveData = localStorage.getItem(saveKey);
        
        if (saveData) {
          return { success: true, data: JSON.parse(saveData) };
        } else {
          return { success: false, error: 'Save file not found' };
        }
      }
    } catch (error) {
      console.error('Failed to load game:', error);
      return { success: false, error: error.message };
    }
  },
  
  // List all available save files
  listSaveFiles: () => {
    try {
      if (isElectron && window.electronAPI) {
        return window.electronAPI.listSaveFiles();
      } else {
        // Browser implementation using localStorage
        const files = [];
        const prefix = 'weird-game-save-';
        
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          
          if (key && key.startsWith(prefix)) {
            const name = key.substring(prefix.length);
            files.push({
              name,
              date: new Date(),
              size: localStorage.getItem(key).length
            });
          }
        }
        
        return { success: true, files };
      }
    } catch (error) {
      console.error('Failed to list save files:', error);
      return { success: false, error: error.message };
    }
  },
  
  // Delete a save file
  deleteSaveFile: (slotName) => {
    try {
      if (isElectron && window.electronAPI) {
        return window.electronAPI.deleteSaveFile(slotName);
      } else {
        // Browser implementation using localStorage
        const saveKey = `weird-game-save-${slotName}`;
        
        if (localStorage.getItem(saveKey)) {
          localStorage.removeItem(saveKey);
          return { success: true };
        } else {
          return { success: false, error: 'Save file not found' };
        }
      }
    } catch (error) {
      console.error('Failed to delete save file:', error);
      return { success: false, error: error.message };
    }
  }
};

console.log('Game API initialized and ready for use');
