// Preload script for Electron and browser environments

// Check if we're running in Electron
const isElectron = typeof window !== 'undefined' && window.process && window.process.type === 'renderer';

// This will run before the renderer process is loaded
window.addEventListener('DOMContentLoaded', () => {
  console.log('Preload script loaded, running in ' + (isElectron ? 'Electron' : 'Browser'));
});

// Create a browser-compatible API that uses localStorage when not in Electron
window.gameAPI = window.gameAPI || {
  getAppVersion: () => '1.0.0',
  
  // Save game data
  saveGame: (saveData, slotName = 'save1') => {
    try {
      // Ensure timestamp is set
      if (!saveData.timestamp) {
        saveData.timestamp = new Date().toISOString();
      }
      
      // Add metadata for better display in load menu
      const metadata = {
        savedAt: new Date().toISOString(),
        displayDate: new Date().toLocaleString(),
        scene: saveData.currentScene || 'Unknown',
        version: '1.0.0'
      };
      
      // Add metadata to save data
      saveData.metadata = metadata;
      
      console.log('Saving game with data:', saveData);
      
      if (isElectron) {
        // Electron implementation would go here
        console.log('Electron save not implemented');
        return { success: false, error: 'Electron save not implemented' };
      } else {
        // Browser implementation using localStorage
        const saveKey = `weird-game-save-${slotName}`;
        localStorage.setItem(saveKey, JSON.stringify(saveData));
        
        // Log all save files after saving
        console.log('All save files after saving:');
        const saveFiles = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && key.startsWith('weird-game-save-')) {
            console.log(`- ${key}`);
            saveFiles.push(key);
          }
        }
        
        return { success: true, path: saveKey, metadata };
      }
    } catch (error) {
      console.error('Failed to save game:', error);
      return { success: false, error: error.message };
    }
  },
  
  // Load game data
  loadGame: (slotName = 'save1') => {
    try {
      if (isElectron) {
        // Electron implementation would go here
        console.log('Electron load not implemented');
        return { success: false, error: 'Electron load not implemented' };
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
      if (isElectron) {
        // Electron implementation would go here
        console.log('Electron list not implemented');
        return { success: false, error: 'Electron list not implemented' };
      } else {
        // Browser implementation using localStorage
        const files = [];
        const prefix = 'weird-game-save-';
        
        // Debug: Log all localStorage keys
        console.log('All localStorage keys:');
        for (let i = 0; i < localStorage.length; i++) {
          console.log(localStorage.key(i));
        }
        
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          
          if (key && key.startsWith(prefix)) {
            const name = key.substring(prefix.length);
            try {
              // Get the save data to extract metadata
              const saveData = JSON.parse(localStorage.getItem(key));
              
              // Use metadata if available, otherwise fall back to timestamp
              let date, displayDate, scene, version;
              
              if (saveData.metadata) {
                // New format with metadata
                date = new Date(saveData.metadata.savedAt);
                displayDate = saveData.metadata.displayDate || date.toLocaleString();
                scene = saveData.metadata.scene || saveData.currentScene || 'Unknown';
                version = saveData.metadata.version || '1.0.0';
              } else {
                // Legacy format
                date = saveData.timestamp ? new Date(saveData.timestamp) : new Date();
                displayDate = date.toLocaleString();
                scene = saveData.currentScene || 'Unknown';
                version = '1.0.0';
              }
              
              // Get player position if available
              const position = saveData.player && saveData.player.position ? 
                `(${Math.round(saveData.player.position.x)},${Math.round(saveData.player.position.y)})` : '';
              
              files.push({
                name,
                date,
                displayDate,
                size: localStorage.getItem(key).length,
                scene,
                version,
                position,
                growthDecay: saveData.growthDecay ? 
                  `G:${saveData.growthDecay.growth}/D:${saveData.growthDecay.decay}` : null
              });
            } catch (parseError) {
              console.error('Error parsing save data:', parseError);
              files.push({
                name,
                date: new Date(),
                displayDate: 'Unknown date',
                size: localStorage.getItem(key).length,
                scene: 'Unknown',
                version: '?',
                error: true
              });
            }
          }
        }
        
        // Sort files by date (newest first)
        files.sort((a, b) => b.date - a.date);
        
        // Debug: Log found save files
        console.log('Found save files:', files);
        
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
      if (isElectron) {
        // Electron implementation would go here
        console.log('Electron delete not implemented');
        return { success: false, error: 'Electron delete not implemented' };
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

// For Electron compatibility, also expose through contextBridge if available
if (isElectron && window.electron && window.electron.contextBridge) {
  window.electron.contextBridge.exposeInMainWorld('electronAPI', window.gameAPI);
}

// Make sure gameAPI is available globally for browser environments
if (typeof window !== 'undefined') {
  window.gameAPI = window.gameAPI || {};
}

// Log that the API is ready
console.log('Game API initialized and ready for use');
