/**
 * Migrate Czech translation files from English-text keys to snake_case key IDs.
 * 
 * Reads each translation file and replaces English text option keys with
 * the corresponding snake_case keys (matching the key generation logic
 * used in add-dialog-keys-transform.mjs).
 * 
 * Usage: node scripts/migrate-translation-keys.mjs [--dry-run]
 */

import fs from 'fs';
import path from 'path';

const DRY_RUN = process.argv.includes('--dry-run');
const DIALOGS_DIR = 'lang/cs/dialogs';

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

const files = fs.readdirSync(DIALOGS_DIR)
    .filter(f => f.endsWith('.js') && f !== 'index.js');

let totalChanges = 0;

for (const file of files) {
    const filePath = path.join(DIALOGS_DIR, file);
    let content = fs.readFileSync(filePath, 'utf8');
    let fileChanges = 0;
    
    // Find all options blocks: options: { "English text": "Czech text", ... }
    // We need to replace each English text key with its snake_case equivalent
    
    // Match option entries inside options blocks:
    // "English text": "Czech translation"  or  'English text': 'Czech translation'
    // We replace the key part only
    
    const lines = content.split('\n');
    const newLines = [];
    let inOptions = false;
    let optionsBraceDepth = 0;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        
        // Detect options: { 
        if (!inOptions && /^\s*options:\s*\{/.test(line)) {
            inOptions = true;
            optionsBraceDepth = 0;
            for (const ch of line) {
                if (ch === '{') optionsBraceDepth++;
                if (ch === '}') optionsBraceDepth--;
            }
            if (optionsBraceDepth <= 0) inOptions = false;
            newLines.push(line);
            continue;
        }
        
        if (!inOptions) {
            newLines.push(line);
            continue;
        }
        
        // Track brace depth
        for (const ch of line) {
            if (ch === '{') optionsBraceDepth++;
            if (ch === '}') optionsBraceDepth--;
        }
        if (optionsBraceDepth <= 0) {
            inOptions = false;
            newLines.push(line);
            continue;
        }
        
        // Try to match a key-value pair: "English text": "Czech text"
        const kvMatch = trimmed.match(/^(['"])((?:\\.|(?!\1).)*)\1\s*:\s*(['"])/);
        if (kvMatch) {
            const englishText = kvMatch[2];
            const snakeKey = textToKey(englishText);
            if (snakeKey && snakeKey !== englishText) {
                const indent = line.match(/^(\s*)/)[1];
                // Replace the quoted key with unquoted snake_case key
                const newLine = line.replace(
                    /(['"])((?:\\.|(?!\1).)*)\1(\s*:)/,
                    `${snakeKey}$3`
                );
                newLines.push(newLine);
                fileChanges++;
                continue;
            }
        }
        
        newLines.push(line);
    }
    
    if (fileChanges > 0) {
        const newContent = newLines.join('\n');
        if (!DRY_RUN) {
            fs.writeFileSync(filePath, newContent);
        }
        console.log(`${file}: migrated ${fileChanges} option keys`);
        totalChanges += fileChanges;
    }
}

console.log(`\nTotal option keys migrated: ${totalChanges}`);
if (DRY_RUN) console.log('(Dry run — no files modified)');
