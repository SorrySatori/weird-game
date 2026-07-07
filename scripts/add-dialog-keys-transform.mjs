/**
 * Script to add `key` properties to dialog options in scene files.
 * 
 * Handles both single-line and multi-line option objects.
 * Uses line-by-line approach only to avoid duplicate keys.
 * 
 * Usage: node scripts/add-dialog-keys-transform.mjs [--dry-run]
 */

import fs from 'fs';
import path from 'path';

const DRY_RUN = process.argv.includes('--dry-run');
const SCENES_DIR = 'scenes';

/**
 * Generate a snake_case key from option text.
 */
function textToKey(text) {
    return text
        .replace(/^["'`]|["'`]$/g, '')
        .replace(/\\'/g, "'")
        .replace(/\\"/g, '"')
        .replace(/[^a-zA-Z0-9\s]/g, '')
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '_')
        .substring(0, 50);
}

/**
 * Extract text from a string property value, handling quotes and escapes.
 */
function extractText(str) {
    // Match 'text', "text", or `text`
    const m = str.match(/(['"`])((?:(?!\1).|\\.)*)\1/);
    return m ? m[2] : null;
}

/**
 * Process a scene file line by line.
 */
function processSceneFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    if (!content.includes('dialogContent')) return { changed: false, count: 0 };
    
    const lines = content.split('\n');
    const newLines = [];
    let changeCount = 0;
    
    let inDialogContent = false;
    let inOptionsArray = false;
    let optsBracketDepth = 0;
    let curlyDepthInDialogContent = 0;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        
        // Track dialogContent getter boundaries AND private dialog content properties
        if (trimmed.includes('get dialogContent()') || /DialogContent\s*=\s*\{/.test(trimmed)) {
            inDialogContent = true;
            curlyDepthInDialogContent = 0;
        }
        
        if (inDialogContent && !inOptionsArray) {
            for (const ch of line) {
                if (ch === '{') curlyDepthInDialogContent++;
                if (ch === '}') curlyDepthInDialogContent--;
            }
            if (curlyDepthInDialogContent <= 0 && inDialogContent && i > 0) {
                inDialogContent = false;
            }
        }
        
        if (!inDialogContent) {
            newLines.push(line);
            continue;
        }
        
        // Detect start of options array
        if (!inOptionsArray && trimmed.startsWith('options:') && trimmed.includes('[')) {
            inOptionsArray = true;
            optsBracketDepth = 0;
            for (const ch of line) {
                if (ch === '[') optsBracketDepth++;
                if (ch === ']') optsBracketDepth--;
            }
            if (optsBracketDepth <= 0) inOptionsArray = false;
            newLines.push(line);
            continue;
        }
        
        if (!inOptionsArray) {
            newLines.push(line);
            continue;
        }
        
        // Track bracket depth within options array
        for (const ch of line) {
            if (ch === '[') optsBracketDepth++;
            if (ch === ']') optsBracketDepth--;
        }
        if (optsBracketDepth <= 0) {
            inOptionsArray = false;
            newLines.push(line);
            continue;
        }
        
        // Already has key? Skip
        if (trimmed.includes(' key:') || trimmed.startsWith('key:')) {
            newLines.push(line);
            continue;
        }
        
        // CASE 1: Single-line option object { text: "...", next: "..." }
        // Check if this line has both text: and next: (single-line option)
        if (trimmed.includes('text:') && trimmed.includes('next:')) {
            const textM = trimmed.match(/text:\s*(['"`])((?:\\.|(?!\1).)*)\1/);
            if (textM) {
                const key = textToKey(textM[2]);
                if (key) {
                    // Insert key: '...' after the text property
                    // Use backreference \2 to properly match the closing quote
                    const modified = line.replace(
                        /(text:\s*(['"`])(?:\\.|(?!\2).)*\2)(,?\s*)/,
                        `$1, key: '${key}'$3`
                    );
                    newLines.push(modified);
                    changeCount++;
                    continue;
                }
            }
        }
        
        // CASE 2: Multi-line option — text: on its own line (possibly with { prefix)
        if (trimmed.includes('text:') && !trimmed.includes('next:')) {
            const textM = trimmed.match(/text:\s*(['"`])((?:\\.|(?!\1).)*)\1/);
            if (textM) {
                const key = textToKey(textM[2]);
                if (key) {
                    // Check next line isn't already a key line
                    const nextTrimmed = (i + 1 < lines.length) ? lines[i + 1].trim() : '';
                    if (!nextTrimmed.startsWith('key:')) {
                        // Determine indentation: use the text: property indentation
                        const textIndent = line.match(/^(\s*)/)[1];
                        // If { is on same line, add extra indent for the key line
                        const keyIndent = trimmed.startsWith('{')
                            ? textIndent + '    '
                            : textIndent;
                        newLines.push(line);
                        newLines.push(`${keyIndent}key: '${key}',`);
                        changeCount++;
                        continue;
                    }
                }
            }
        }
        
        newLines.push(line);
    }
    
    if (changeCount > 0 && !DRY_RUN) {
        fs.writeFileSync(filePath, newLines.join('\n'));
    }
    
    return { changed: changeCount > 0, count: changeCount };
}

// Process all scene files
const sceneFiles = fs.readdirSync(SCENES_DIR)
    .filter(f => f.endsWith('.js'))
    .map(f => path.join(SCENES_DIR, f));

let totalChanges = 0;
for (const file of sceneFiles) {
    const result = processSceneFile(file);
    if (result.changed) {
        console.log(`${path.basename(file)}: added ${result.count} keys`);
        totalChanges += result.count;
    }
}

console.log(`\nTotal keys added: ${totalChanges}`);
if (DRY_RUN) console.log('(Dry run — no files modified)');
