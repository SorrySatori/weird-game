/**
 * Verify key consistency between scene files and Czech translation files.
 * Usage: node scripts/verify-keys.mjs
 */
import fs from 'fs';
import path from 'path';

const SCENES_DIR = 'scenes';
const DIALOGS_DIR = 'lang/cs/dialogs';

function extractSceneKeys(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const keys = new Set();
    const keyRegex = /key:\s*'([^']+)'/g;
    let m;
    while ((m = keyRegex.exec(content)) !== null) {
        keys.add(m[1]);
    }
    return keys;
}

function extractTransKeys(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const keys = new Set();
    const lines = content.split('\n');
    let inOptions = false;
    let depth = 0;
    for (const line of lines) {
        const t = line.trim();
        if (!inOptions && t.startsWith('options:') && t.includes('{')) {
            inOptions = true;
            depth = 0;
            for (const ch of line) { if (ch === '{') depth++; if (ch === '}') depth--; }
            if (depth <= 0) inOptions = false;
            continue;
        }
        if (inOptions) {
            for (const ch of line) { if (ch === '{') depth++; if (ch === '}') depth--; }
            if (depth <= 0) { inOptions = false; continue; }
            const m = t.match(/^(\w+)\s*:/);
            if (m) keys.add(m[1]);
        }
    }
    return keys;
}

const transFiles = fs.readdirSync(DIALOGS_DIR).filter(f => f.endsWith('.js') && f !== 'index.js');
let totalMismatches = 0;

for (const tf of transFiles) {
    const scenePath = path.join(SCENES_DIR, tf);
    const transPath = path.join(DIALOGS_DIR, tf);
    
    if (!fs.existsSync(scenePath)) {
        console.log(`WARN: No scene file for ${tf}`);
        continue;
    }
    
    const sceneKeys = extractSceneKeys(scenePath);
    const transKeys = extractTransKeys(transPath);
    
    let mismatches = 0;
    for (const k of transKeys) {
        if (!sceneKeys.has(k)) {
            console.log(`  ${tf}: translation key "${k}" NOT in scene`);
            mismatches++;
        }
    }
    if (mismatches > 0) {
        totalMismatches += mismatches;
    } else {
        console.log(`OK: ${tf} (${transKeys.size} keys verified)`);
    }
}

console.log(`\n${totalMismatches === 0 ? 'All keys consistent' : totalMismatches + ' mismatches found'}`);
