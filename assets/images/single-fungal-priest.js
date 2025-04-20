// This script extracts a single fungal priest character from the spritesheet
// and saves it as a new image file

const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');
const path = require('path');

async function extractSingleCharacter() {
  try {
    const imagePath = path.join(__dirname, 'FungalPriestSprite.png');
    console.log(`Processing image: ${imagePath}`);
    
    // Load the image
    const image = await loadImage(imagePath);
    
    // Based on the screenshot, we can see it's a 3x3 grid of characters
    // Let's extract just the first character (top-left)
    const characterWidth = Math.floor(image.width / 3);
    const characterHeight = Math.floor(image.height / 3);
    
    console.log(`Original dimensions: ${image.width}x${image.height}`);
    console.log(`Character dimensions: ${characterWidth}x${characterHeight}`);
    
    // Create a canvas for the single character
    const canvas = createCanvas(characterWidth, characterHeight);
    const ctx = canvas.getContext('2d');
    
    // Draw only the top-left character
    ctx.drawImage(
      image,
      0, 0, characterWidth, characterHeight,  // Source coordinates and dimensions
      0, 0, characterWidth, characterHeight   // Destination coordinates and dimensions
    );
    
    // Get the image data to make background transparent
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    
    // Get the color of the top-left pixel (usually the background color)
    const bgColor = {
      r: data[0],
      g: data[1],
      b: data[2]
    };
    
    console.log(`Background color detected: RGB(${bgColor.r}, ${bgColor.g}, ${bgColor.b})`);
    
    // Set a threshold for color matching (to account for slight variations)
    const threshold = 30;
    
    // Make background pixels transparent
    let transparentPixelsCount = 0;
    for (let i = 0; i < data.length; i += 4) {
      // If the pixel color is close to the background color
      if (
        Math.abs(data[i] - bgColor.r) < threshold &&
        Math.abs(data[i + 1] - bgColor.g) < threshold &&
        Math.abs(data[i + 2] - bgColor.b) < threshold
      ) {
        // Make it transparent
        data[i + 3] = 0;
        transparentPixelsCount++;
      }
    }
    
    console.log(`Made ${transparentPixelsCount} pixels transparent`);
    
    // Put the modified image data back on the canvas
    ctx.putImageData(imageData, 0, 0);
    
    // Save the result
    const outputPath = path.join(__dirname, 'SingleFungalPriest.png');
    const stream = canvas.createPNGStream();
    const out = fs.createWriteStream(outputPath);
    
    return new Promise((resolve, reject) => {
      out.on('finish', () => {
        console.log(`Saved single character image to: ${outputPath}`);
        resolve(outputPath);
      });
      
      out.on('error', reject);
      stream.pipe(out);
    });
  } catch (error) {
    console.error('Error extracting character:', error);
    throw error;
  }
}

// Run the function
extractSingleCharacter()
  .then(() => console.log('Done!'))
  .catch(err => console.error('Failed:', err));
