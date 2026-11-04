"""Demo strip, the remaining lang tables: drop the keys of lang/{en,cs}/{game,observe}.js the demo's code can no
longer look up (texts of removed places, cutscenes, NPCs). Companion of prune_lang.py; run after it:

    python3 tools/demo/prune_keys.py          # report only
    python3 tools/demo/prune_keys.py --write  # rewrite in place

A leaf key path (e.g. observe.godgraveyard.default) stays when the code has it literally, or builds it from a literal
prefix (`mood.${npc}.${tendency}`, 'items.' + id) AND the next segment is a quoted string somewhere in the code (the
npc / item id). Blocks are found by indentation, so what stays keeps its layout and comments.
"""
import os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
CODE_DIRS = ['scenes', 'utils', 'systems', 'ui', 'config']
FILES = ['game', 'observe']
WRITE = '--write' in sys.argv

corpus = open(os.path.join(ROOT, 'main.js'), encoding='utf-8').read()
for d in CODE_DIRS:
    for base, _, files in os.walk(os.path.join(ROOT, d)):
        for f in files:
            if f.endswith('.js'):
                corpus += '\n' + open(os.path.join(base, f), encoding='utf-8').read()
quoted = set(re.findall(r"""['"`]([\w-]+)['"`]""", corpus))
prefixes = set(re.findall(r"""`([\w.]+\.)\$\{""", corpus)) | set(re.findall(r"""['"]([\w.]+\.)['"]\s*\+""", corpus))


def used(path):
    if path in corpus:
        return True
    for p in prefixes:
        if path.startswith(p):
            seg = path[len(p):].split('.')[0]
            if seg in quoted:
                return True
    return False


OPEN = re.compile(r"^(\s*)(?:'([^']+)'|([\w-]+)): ([\{\[])\s*$")
LEAF = re.compile(r"^(\s*)(?:'([^']+)'|([\w-]+)): ")


def prune(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    out, dropped = [], []

    def block_end(i, indent, bracket):
        close = '}' if bracket == '{' else ']'
        j = i + 1
        while not re.match(r'^%s\%s,?\s*$' % (indent, close), lines[j]):
            j += 1
        return j

    def walk(i, end, prefix):
        """copy lines[i:end] to out, dropping unused leaves under the key path `prefix`"""
        while i < end:
            line = lines[i]
            m = OPEN.match(line)
            if m:
                key = m.group(2) or m.group(3)
                j = block_end(i, m.group(1), m.group(4))
                p = prefix + key
                if m.group(4) == '[':                                   # an array is one leaf
                    if used(p) or not prefix:
                        out.extend(lines[i:j + 1])
                    else:
                        dropped.append(p)
                else:
                    start = len(out)
                    out.append(line)
                    n_before = len(dropped)
                    walk(i + 1, j, p + '.')
                    out.append(lines[j])
                    # a table left with nothing in it goes too
                    if len(out) - start == 2 and len(dropped) > n_before and prefix:
                        del out[start:]
                i = j + 1
                continue
            m = LEAF.match(line)
            if m and prefix:
                key = m.group(2) or m.group(3)
                # the value may continue on the next lines (until the next key / closing bracket at this indent)
                j = i + 1
                while j < end and not LEAF.match(lines[j]) and not OPEN.match(lines[j]) and not re.match(r'^\s*[\}\]],?\s*$', lines[j]) \
                        and not lines[j].strip().startswith('//'):
                    j += 1
                p = prefix + key
                if used(p):
                    out.extend(lines[i:j])
                else:
                    dropped.append(p)
                i = j
                continue
            out.append(line)
            i += 1

    walk(0, len(lines), '')
    if WRITE:
        open(path, 'w', encoding='utf-8').write('\n'.join(out))
    return dropped


for lang in ('en', 'cs'):
    for name in FILES:
        p = os.path.join(ROOT, 'lang', lang, name + '.js')
        d = prune(p)
        print(f'{lang}/{name}.js: -{len(d)} keys')
        if '-v' in sys.argv:
            print('   ' + ', '.join(d))
