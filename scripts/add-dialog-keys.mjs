/**
 * Script to add `key` properties to dialog options in scene files
 * and generate updated translation files.
 * 
 * Usage: node scripts/add-dialog-keys.mjs
 */

import fs from 'fs';
import path from 'path';

const SCENES_DIR = 'scenes';
const TRANS_DIR = 'lang/cs/dialogs';

// Find all scene files that have dialogContent
const sceneFiles = fs.readdirSync(SCENES_DIR)
    .filter(f => f.endsWith('.js'))
    .map(f => path.join(SCENES_DIR, f));

/**
 * Generate a key from option text
 */
function textToKey(text) {
    return text
        .replace(/^["']|["']$/g, '')  // strip outer quotes
        .replace(/[^a-zA-Z0-9\s]/g, '')  // remove special chars
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '_')
        .substring(0, 40);  // limit length
}

/**
 * Parse option objects from a dialogContent section using regex.
 * Returns array of { line, text, hasKey }
 */
function findOptionsInFile(content) {
    const results = [];
    const lines = content.split('\n');
    
    // Match lines like: { text: "...", next: "..." } or { text: '...' ...}
    // We look for option objects inside options arrays
    let inOptions = false;
    let braceDepth = 0;
    let currentState = null;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Track dialog state keys
        const stateMatch = line.match(/^\s+(\w+):\s*\{/);
        if (stateMatch && !line.includes('text:') && !line.includes('options:')) {
            currentState = stateMatch[1];
        }
        
        // Check if we're entering an options array
        if (line.includes('options:') && line.includes('[')) {
            inOptions = true;
            braceDepth = 0;
        }
        
        if (inOptions) {
            // Count braces/brackets
            for (const ch of line) {
                if (ch === '[') braceDepth++;
                if (ch === ']') {
                    braceDepth--;
                    if (braceDepth <= 0) {
                        inOptions = false;
                    }
                }
            }
            
            // Look for text property in option objects
            const textMatch = line.match(/text:\s*(['"`])(.*?)\1/);
            if (textMatch) {
                const optText = textMatch[2];
                const hasKey = line.includes('key:');
                const hasNext = line.match(/next:\s*['"`](\w+)['"`]/);
                results.push({
                    lineNum: i + 1,  // 1-indexed
                    text: optText,
                    state: currentState,
                    hasKey,
                    next: hasNext ? hasNext[1] : null,
                    line: line
                });
            }
        }
    }
    
    return results;
}

// Process each scene file
for (const sceneFile of sceneFiles) {
    const content = fs.readFileSync(sceneFile, 'utf8');
    
    if (!content.includes('dialogContent')) continue;
    
    const options = findOptionsInFile(content);
    if (options.length === 0) continue;
    
    const sceneName = path.basename(sceneFile, '.js');
    
    console.log(`\n=== ${sceneName} ===`);
    console.log(`Options found: ${options.length}`);
    
    // Group by state
    const byState = {};
    for (const opt of options) {
        if (!byState[opt.state]) byState[opt.state] = [];
        byState[opt.state].push(opt);
    }
    
    for (const [state, opts] of Object.entries(byState)) {
        // Generate unique keys within each state
        const usedKeys = new Set();
        for (const opt of opts) {
            let key = textToKey(opt.text);
            // Ensure uniqueness
            let suffix = 1;
            let origKey = key;
            while (usedKeys.has(key)) {
                key = `${origKey}_${suffix++}`;
            }
            usedKeys.add(key);
            opt.key = key;
        }
        
        console.log(`  ${state}:`);
        for (const opt of opts) {
            console.log(`    key: "${opt.key}" <- "${opt.text.substring(0, 50)}"`);
        }
    }
}
