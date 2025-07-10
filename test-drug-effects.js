/**
 * Test script for drug effects
 * Run this in the browser console when in the VoxMarket scene to test drug effects
 */

// Test function to manually trigger drug effects
function testDrugEffects() {
    // Get the current scene
    const scene = game.scene.scenes.find(s => s.scene.key === 'VoxMarket');
    
    if (!scene) {
        console.error('VoxMarket scene not found');
        return;
    }
    
    // Check if effects system is initialized
    if (!scene.effectsSystem) {
        console.error('Effects system not initialized');
        return;
    }
    
    console.log('Testing drug effects...');
    
    // Create test drug items
    const testDrugs = [
        { id: 'grayOltrac', name: 'Gray Oltrac', description: 'A common variant of Oltrac with mild hallucinogenic effects.' },
        { id: 'violetOltrac', name: 'Violet Oltrac', description: 'A medium-strength variant of Oltrac that enhances perception.' },
        { id: 'amberOltrac', name: 'Amber Oltrac', description: 'The rarest and most potent form of Oltrac that allows glimpses beyond reality.' }
    ];
    
    // Create buttons to test each drug effect
    const buttonStyle = 'position:fixed;z-index:10000;padding:10px;margin:5px;background:#2a623d;color:#7fff8e;border:none;cursor:pointer;';
    
    testDrugs.forEach((drug, index) => {
        const button = document.createElement('button');
        button.innerHTML = `Test ${drug.name}`;
        button.style.cssText = buttonStyle;
        button.style.top = `${50 + (index * 50)}px`;
        button.style.left = '10px';
        
        button.onclick = () => {
            console.log(`Testing ${drug.name} effect`);
            scene.effectsSystem.applyDrugEffect(drug);
        };
        
        document.body.appendChild(button);
    });
    
    // Create a clear effects button
    const clearButton = document.createElement('button');
    clearButton.innerHTML = 'Clear Effects';
    clearButton.style.cssText = buttonStyle;
    clearButton.style.top = `${50 + (testDrugs.length * 50)}px`;
    clearButton.style.left = '10px';
    clearButton.style.backgroundColor = '#8B0000';
    
    clearButton.onclick = () => {
        console.log('Clearing all effects');
        scene.effectsSystem.clearEffects();
    };
    
    document.body.appendChild(clearButton);
    
    console.log('Test buttons added to the page. Click them to test drug effects.');
}

// Run the test function
testDrugEffects();
