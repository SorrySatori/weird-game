"""Demo strip, the language side: drop every journal entry / fact and quest / quest update the demo's code no longer
mentions, so the shipped lang files don't tell the full game's story. Run on the steam-demo branch after the scenes
have been stripped (and again after merging dev into it):

    python3 tools/demo/prune_lang.py          # report only
    python3 tools/demo/prune_lang.py --write  # rewrite lang/{en,cs}/{journal,quests}.js in place

An id counts as used when the code (scenes, utils, systems, ui, main.js -- not lang/) has it as a quoted string, or
builds it from a quoted prefix ('lamps_found_' + …, `salt_recall_${…}`). Blocks are found by indentation (the files'
own layout: entries at 8 spaces, their updates / facts at 16), so formatting and comments of what stays are kept.
"""
import os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
CODE_DIRS = ['scenes', 'utils', 'systems', 'ui', 'config']
WRITE = '--write' in sys.argv

corpus = open(os.path.join(ROOT, 'main.js'), encoding='utf-8').read()
for d in CODE_DIRS:
    for base, _, files in os.walk(os.path.join(ROOT, d)):
        for f in files:
            if f.endswith('.js'):
                corpus += '\n' + open(os.path.join(base, f), encoding='utf-8').read()

quoted = set(re.findall(r"""['"`]([\w-]+)['"`]""", corpus))
prefixes = set(re.findall(r"""['"`]([\w-]+_)['"`]\s*\+""", corpus)) | set(re.findall(r"""`([\w-]+_)\$\{""", corpus))
used = lambda key: key in quoted or any(key.startswith(p) for p in prefixes)

ENTRY = re.compile(r"^        (?:'([^']+)'|([\w-]+)): \{\s*$")
SUB = re.compile(r"^                (?:'([^']+)'|([\w-]+)): ")


def prune(path, sub_block):
    lines = open(path, encoding='utf-8').read().split('\n')
    out, dropped_entries, dropped_subs = [], [], []
    i = 0
    while i < len(lines):
        m = ENTRY.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        key = m.group(1) or m.group(2)
        j = i + 1
        while not re.match(r'^        \},?\s*$', lines[j]):
            j += 1
        block = lines[i:j + 1]
        if not used(key):
            dropped_entries.append(key)
        else:
            # inside a kept entry: drop the unused updates / facts (single- or multi-line values)
            kept, k = [], 0
            while k < len(block):
                line = block[k]
                if re.match(r'^            %s: \{\s*$' % sub_block, line):
                    kept.append(line); k += 1
                    while not re.match(r'^            \},?\s*$', block[k]):
                        sm = SUB.match(block[k])
                        n = k + 1
                        while n < len(block) and not SUB.match(block[n]) and not re.match(r'^            \},?\s*$', block[n]):
                            n += 1
                        sk = sm and (sm.group(1) or sm.group(2))
                        if sk and not used(sk):
                            dropped_subs.append(f'{key}.{sk}')
                        else:
                            kept.extend(block[k:n])
                        k = n
                kept.append(block[k]); k += 1
            out.extend(kept)
        i = j + 1
    if WRITE:
        open(path, 'w', encoding='utf-8').write('\n'.join(out))
    return dropped_entries, dropped_subs


for lang in ('en', 'cs'):
    for name, sub in (('journal', 'facts'), ('quests', 'updates')):
        p = os.path.join(ROOT, 'lang', lang, name + '.js')
        e, s = prune(p, sub)
        print(f'{lang}/{name}.js: -{len(e)} entries, -{len(s)} {sub}')
        if '-v' in sys.argv:
            print('   entries:', ', '.join(e)); print('   ' + sub + ':', ', '.join(s))
