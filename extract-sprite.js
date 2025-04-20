// Node.js script to extract a single character from FungalPriestSprite.png
const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');
const path = require('path');

// Path to the sprite sheet
const inputPath = path.join(__dirname, 'assets', 'images', 'FungalPriestSprite.png');
// Path for the output file
const outputPath = path.join(__dirname, 'assets', 'images', 'SingleFungalPriest.png');

async function extractCharacter() {
  try {
    console.log(`Loading sprite sheet from: ${inputPath}`);
    
    // Load the image
    const image = await loadImage(inputPath);
    
    // Assuming a 3x3 grid of characters
    const cellWidth = Math.floor(image.width / 3);
    const cellHeight = Math.floor(image.height / 3);
    
    console.log(`Original dimensions: ${image.width}x${image.height}`);
    console.log(`Cell dimensions: ${cellWidth}x${cellHeight}`);
    
    // Create a canvas for the single character
    const canvas = createCanvas(cellWidth, cellHeight);
    const ctx = canvas.getContext('2d');
    
    // Extract the middle character from the top row (x=cellWidth, y=0)
    ctx.drawImage(
      image,
      cellWidth, 0, cellWidth, cellHeight,  // Source coordinates and dimensions
      0, 0, cellWidth, cellHeight           // Destination coordinates and dimensions
    );
    
    // Make background transparent
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
    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(outputPath, buffer);
    
    console.log(`Successfully saved single character to: ${outputPath}`);
    
  } catch (error) {
    console.error('Error extracting character:', error);
  }
}

// Run the extraction
extractCharacter();
