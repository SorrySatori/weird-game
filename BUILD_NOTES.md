# Build System Notes

## Overview
This document provides information about the build system for Weird Game, including recent fixes and improvements.

## Build Commands

- `npm run build` - Creates a production build in the `dist` directory
- `npm run serve` - Runs the webpack development server
- `npm run serve-build` - Serves the production build locally
- `npm run deploy` - Runs the deployment script with options for different deployment targets

## Recent Fixes

### 1. Fixed "fullscreenBg is not defined" Error
- The error was caused by commented-out fullscreen button code in `MainScene.js`
- Solution: Uncommented the fullscreen button code and added proper initialization

### 2. Improved Fullscreen Functionality
- Added cross-browser fullscreen support with a dedicated `toggleFullscreen()` method
- Added support for multiple fullscreen APIs (standard, Mozilla, WebKit, MS)
- Added keyboard shortcuts: F11 and F for toggling fullscreen
- Added proper resize handling after entering/exiting fullscreen

### 3. Enhanced Mobile Support
- Added viewport meta tags to prevent scaling and improve mobile experience
- Added mobile web app capability meta tags for better fullscreen support on mobile devices

### 4. Fixed Game Scaling and Fullscreen Display
- Changed Phaser scale mode from RESIZE to FIT for better proportional scaling
- Added min/max width and height constraints for consistent UI scaling
- Updated CSS to ensure the game container fills the entire browser window
- Made UI elements position dynamically based on screen dimensions
- Added responsive font sizing based on screen dimensions
- Improved window resize handler with better timing and logging

### 5. Implemented Global Fullscreen Scaling
- Updated Phaser scale mode to RESIZE for better browser compatibility
- Set canvas dimensions to 100% width and height
- Modified HTML/CSS to ensure the game fills the entire browser window
- Simplified the window resize handler for better performance
- Removed complex scaling calculations in favor of native browser scaling
- Ensured consistent appearance across different screen sizes

## Build Configuration

The webpack configuration (`webpack.config.js`) is set up to:
- Bundle all JavaScript files into a single `bundle.js`
- Copy all assets (images, sounds, icons) to the `dist` directory
- Generate an optimized `index.html` file
- Minify the JavaScript code for better performance

## Known Issues

- Large asset files (some WAV files and images) exceed the recommended size limit
- Consider optimizing these assets in the future for better web performance
- Consider implementing code splitting for lazy loading parts of the application

## Deployment

The `deploy.js` script provides options for:
1. Deploying to a web server (requires additional configuration)
2. Creating a zip archive for manual deployment
3. Serving locally for testing

To configure deployment options, edit the `deployment.config.json` file.
