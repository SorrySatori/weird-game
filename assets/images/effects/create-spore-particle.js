const fs = require('fs');
const { createCanvas } = require('canvas');

// Create a canvas for our particle
const canvas = createCanvas(16, 16);
const ctx = canvas.getContext('2d');

// Clear the canvas
ctx.clearRect(0, 0, 16, 16);

// Create a glowing spore particle
const gradient = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
gradient.addColorStop(0, 'rgba(127, 255, 142, 1)');    // Bright green center
gradient.addColorStop(0.6, 'rgba(127, 255, 142, 0.6)'); // Fading green
gradient.addColorStop(1, 'rgba(127, 255, 142, 0)');    // Transparent edge

ctx.fillStyle = gradient;
ctx.beginPath();
ctx.arc(8, 8, 8, 0, Math.PI * 2);
ctx.fill();

// Add some inner detail
ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
ctx.beginPath();
ctx.arc(6, 6, 2, 0, Math.PI * 2);
ctx.fill();

// Convert canvas to PNG buffer
const buffer = canvas.toBuffer('image/png');

// Save the image
fs.writeFileSync('assets/images/effects/spore-particle.png', buffer);

console.log('Spore particle created successfully!');
