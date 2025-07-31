// Custom loader for Electron to handle Phaser asset paths
const path = require('path');
const { app } = require('electron');

// Get the base directory for the application
const getBasePath = () => {
  return app.isPackaged 
    ? path.join(process.resourcesPath, 'app') 
    : __dirname;
};

// Convert a relative asset path to an absolute file path
const resolveAssetPath = (assetPath) => {
  return path.join(getBasePath(), assetPath);
};

// Setup protocol handler for game assets
const setupAssetProtocol = (protocol) => {
  // Register a custom protocol handler for game assets
  protocol.registerFileProtocol('asset', (request, callback) => {
    const url = request.url.substring(8); // Remove 'asset://' prefix
    const filePath = resolveAssetPath(url);
    callback({ path: filePath });
  });
};

module.exports = {
  getBasePath,
  resolveAssetPath,
  setupAssetProtocol
};
