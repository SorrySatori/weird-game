// Script to make the background of an image transparent
const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');

async function makeTransparent(imagePath) {
    try {
        console.log(`Processing image: ${imagePath}`);
        
        // Load the image
        const image = await loadImage(imagePath);
        
        // Create a canvas with the same dimensions as the image
        const canvas = createCanvas(image.width, image.height);
        const ctx = canvas.getContext('2d');
        
        // Draw the image onto the canvas
        ctx.drawImage(image, 0, 0);
        
        // Get the image data
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
        const outputPath = imagePath.replace('.png', '-transparent.png');
        const stream = canvas.createPNGStream();
        const out = fs.createWriteStream(outputPath);
        
        return new Promise((resolve, reject) => {
            out.on('finish', () => {
                console.log(`Saved transparent image to: ${outputPath}`);
                resolve(outputPath);
            });
            
            out.on('error', reject);
            stream.pipe(out);
        });
    } catch (error) {
        console.error('Error making image transparent:', error);
        throw error;
    }
}

// Path to the image
const imagePath = './assets/images/FungalPriestSprite.png';

// Make the image transparent
makeTransparent(imagePath)
    .then(outputPath => {
        console.log('Process completed successfully!');
        // Optionally replace the original file
        fs.copyFile(outputPath, imagePath, (err) => {
            if (err) {
                console.error('Error replacing original file:', err);
            } else {
                console.log('Original file replaced with transparent version');
                // Delete the temporary file
                fs.unlink(outputPath, (err) => {
                    if (err) console.error('Error deleting temporary file:', err);
                });
            }
        });
    })
    .catch(error => {
        console.error('Failed to process image:', error);
    });
