// Preload script for Electron
const { contextBridge } = require('electron');

// This will run before the renderer process is loaded
window.addEventListener('DOMContentLoaded', () => {
  console.log('Preload script loaded');
});

// Expose a minimal API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => process.env.npm_package_version || '1.0.0'
});

