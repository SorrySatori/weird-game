#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const config = {
  buildCommand: 'npm run build',
  distDir: path.join(__dirname, 'dist'),
  deploymentConfigPath: path.join(__dirname, 'deployment.config.json')
};

// Helper functions
function log(message) {
  console.log(`[DEPLOY] ${message}`);
}

function error(message) {
  console.error(`[ERROR] ${message}`);
  process.exit(1);
}

// Main deployment function
async function deploy() {
  try {
    // Check if deployment config exists
    if (!fs.existsSync(config.deploymentConfigPath)) {
      error('Deployment configuration file not found');
    }

    // Read deployment configuration
    const deploymentConfig = JSON.parse(fs.readFileSync(config.deploymentConfigPath, 'utf8'));
    log(`Deploying ${deploymentConfig.name}...`);

    // Build the project
    log('Building project...');
    execSync(config.buildCommand, { stdio: 'inherit' });

    // Check if dist directory exists
    if (!fs.existsSync(config.distDir)) {
      error('Build directory not found. Build may have failed.');
    }

    // Count files in dist directory
    const fileCount = countFiles(config.distDir);
    log(`Build successful. ${fileCount} files ready for deployment.`);

    // Deployment options
    log('\nDeployment options:');
    log('1. Deploy to a web server (requires additional configuration)');
    log('2. Create a zip archive for manual deployment');
    log('3. Serve locally for testing');
    log('\nTo deploy to a web server, configure your server details in deployment.config.json');
    log('and run: node deploy.js --target=server');
    log('\nTo create a zip archive, run: node deploy.js --target=zip');
    log('\nTo serve locally, run: npm run serve-build');
  } catch (err) {
    error(`Deployment failed: ${err.message}`);
  }
}

// Count files in directory recursively
function countFiles(dir) {
  let count = 0;
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const itemPath = path.join(dir, item);
    const stats = fs.statSync(itemPath);
    
    if (stats.isDirectory()) {
      count += countFiles(itemPath);
    } else {
      count++;
    }
  }
  
  return count;
}

// Parse command line arguments
const args = process.argv.slice(2);
const targetArg = args.find(arg => arg.startsWith('--target='));
const target = targetArg ? targetArg.split('=')[1] : null;

// Run deployment
deploy().catch(err => error(err.message));
