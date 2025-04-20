const { createCanvas } = require('canvas');
const fs = require('fs');
const path = require('path');

// Create a canvas for the ground image
const canvas = createCanvas(800, 100);
const ctx = canvas.getContext('2d');

// Generate the market ground
function generateMarketGround() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set background color - dark greenish-gray to match market floor
    ctx.fillStyle = '#1a2420';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Add some texture/pattern to the ground
    // First layer - darker spots
    for (let i = 0; i < 300; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const size = Math.random() * 10 + 2;
        const alpha = Math.random() * 0.3 + 0.1;
        
        ctx.fillStyle = `rgba(10, 20, 15, ${alpha})`;
        ctx.beginPath();
        ctx.ellipse(x, y, size, size/2, 0, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Second layer - green glowing spores (like in the VoxMarket image)
    for (let i = 0; i < 150; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const size = Math.random() * 3 + 1;
        const alpha = Math.random() * 0.4 + 0.2;
        
        ctx.fillStyle = `rgba(50, 255, 100, ${alpha})`;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
    }
    
    // Add some subtle lines to represent floor boards or tiles
    ctx.strokeStyle = 'rgba(40, 60, 50, 0.3)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 20; i++) {
        const y = Math.random() * canvas.height;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
    
    // Add some vertical lines for texture
    for (let i = 0; i < 40; i++) {
        const x = Math.random() * canvas.width;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
    
    // Add a subtle glow at the top to blend with the scene
    const gradient = ctx.createLinearGradient(0, 0, 0, 30);
    gradient.addColorStop(0, 'rgba(50, 150, 100, 0.2)');
    gradient.addColorStop(1, 'rgba(50, 150, 100, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, 30);
}

// Generate the ground
generateMarketGround();

// Save the image
const buffer = canvas.toBuffer('image/png');
fs.writeFileSync(path.join(__dirname, 'assets', 'images', 'market-ground.png'), buffer);

console.log('Market ground image generated and saved to assets/images/market-ground.png');
