"""Demo strip, the Czech dialog files: keep only what the stripped scenes can still show -- states that exist in the
scene, option keys and text variants (textKey) the scene still has. Companion of prune_lang.py / prune_keys.py:

    python3 tools/demo/prune_cs_dialogs.py          # report only
    python3 tools/demo/prune_cs_dialogs.py --write

lang/cs/dialogs/<Scene>.js is matched with scenes/<Scene>.js. A state stays when the scene has `<state>: {` or the
quoted name; an option / text variant when its key is quoted in the scene (option keys and textKeys always are).
Blocks are found by the files' indentation (states at 4 spaces, their option keys / text variants at 12).
"""
import os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
DIR = os.path.join(ROOT, 'lang', 'cs', 'dialogs')
WRITE = '--write' in sys.argv

STATE = re.compile(r"^    (?:'([^']+)'|([\w-]+)): \{\s*$")
INNER = re.compile(r"^        (options|text): \{\s*$")
KEY = re.compile(r"^            (?:'([^']+)'|\"([^\"]+)\"|([\w-]+)): ")


def block_end(lines, i, indent):
    j = i + 1
    while not re.match(r'^%s\},?\s*$' % indent, lines[j]):
        j += 1
    return j


for f in sorted(os.listdir(DIR)):
    scene_path = os.path.join(ROOT, 'scenes', f)
    if f == 'index.js' or not os.path.exists(scene_path):
        continue
    scene = open(scene_path, encoding='utf-8').read()
    # quoted as a whole string somewhere in the scene (substring test: apostrophes in the English texts would
    # throw a quote-pairing regex off)
    is_quoted = lambda k: any(q + k + q in scene for q in ("'", '"', '`'))
    state_used = lambda k: is_quoted(k) or re.search(r'^\s+%s: \{' % re.escape(k), scene, re.M)
    lines = open(os.path.join(DIR, f), encoding='utf-8').read().split('\n')
    out, gone_states, gone_keys = [], [], 0
    i = 0
    while i < len(lines):
        m = STATE.match(lines[i])
        if not m or (m.group(2) or m.group(1)) == '_speakers':
            out.append(lines[i]); i += 1; continue
        key = m.group(1) or m.group(2)
        j = block_end(lines, i, '    ')
        if not state_used(key):
            gone_states.append(key); i = j + 1; continue
        k = i
        while k <= j:
            im = INNER.match(lines[k])
            if im:
                e = block_end(lines, k, '        ')
                out.append(lines[k])
                n = k + 1
                while n < e:
                    km = KEY.match(lines[n])
                    nxt = n + 1
                    while nxt < e and not KEY.match(lines[nxt]):
                        nxt += 1
                    ok = km and (is_quoted(km.group(1) or km.group(2) or km.group(3))
                                 or im.group(1) == 'text' and (km.group(1) or km.group(2) or km.group(3)) in ('default',))
                    if km and not ok:
                        gone_keys += 1
                    else:
                        out.extend(lines[n:nxt])
                    n = nxt
                out.append(lines[e]); k = e + 1
                continue
            out.append(lines[k]); k += 1
        i = j + 1
    if gone_states or gone_keys:
        print(f'{f}: -{len(gone_states)} states, -{gone_keys} option keys / text variants', ', '.join(gone_states)[:300])
        if WRITE:
            open(os.path.join(DIR, f), 'w', encoding='utf-8').write('\n'.join(out))
