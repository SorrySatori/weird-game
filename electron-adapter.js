// Electron adapter for Phaser
// This file helps Phaser load assets correctly in an Electron environment

// Function to check if we're running in Electron
function isElectron() {
  return window && window.process && window.process.type;
}

// Function to adapt asset paths for Electron
function adaptAssetPath(path) {
  if (!isElectron()) return path;
  
  // For absolute paths, use them directly
  if (path.startsWith('/') || path.includes('://')) {
    return path;
  }
  
  // For relative paths, make them absolute
  return window.location.protocol + '//' + window.location.host + '/' + path;
}

// Patch Phaser's loader to work with Electron
function patchPhaserLoader() {
  if (!isElectron() || !window.Phaser) return;
  
  console.log('Patching Phaser loader for Electron compatibility');
  
  // Store original Phaser loader methods
  const originalLoadFile = Phaser.Loader.prototype.loadFile;
  
  // Override the loadFile method to adapt asset paths
  Phaser.Loader.prototype.loadFile = function(file) {
    if (file && file.url) {
      console.log('Loading asset:', file.url);
      // Don't modify URLs that already have protocols
      if (!file.url.includes('://') && !file.url.startsWith('data:')) {
        file.url = adaptAssetPath(file.url);
        console.log('Adapted URL:', file.url);
      }
    }
    return originalLoadFile.call(this, file);
  };
}

// Export the functions
export { isElectron, adaptAssetPath, patchPhaserLoader };
