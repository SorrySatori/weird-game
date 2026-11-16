"""Record where a background generator writes its lettering (every common.draw_text call: text, x, y, scale), so
grid2x.py can draw the signs again on the 2x grid (halving a 1-2 px stroke font turns it to mush).

  python3 tools/artgen/textspec.py floors_bg.py [generator args...]   -> tools/artgen/textspecs/floors_bg.json

The generator runs in full into a temp dir (its picture is thrown away; the shipped one may have hand edits)."""
import json, os, runpy, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common

gen, args = sys.argv[1], sys.argv[2:]
calls, orig = [], common.draw_text


def recording(put, s, x, y, sc):
    calls.append([s, int(x), int(y), int(sc)])
    return orig(put, s, x, y, sc)


common.draw_text = recording
with tempfile.TemporaryDirectory() as tmp:
    sys.argv = [gen, tmp] + args
    os.chdir(HERE)
    runpy.run_path(os.path.join(HERE, gen), run_name='__main__')
os.makedirs(os.path.join(HERE, 'textspecs'), exist_ok=True)
name = os.path.splitext(gen)[0] + ('_' + '_'.join(args) if args else '')
seen, uniq = set(), []
for c in calls:
    if tuple(c) not in seen: seen.add(tuple(c)); uniq.append(c)
json.dump(uniq, open(os.path.join(HERE, 'textspecs', name + '.json'), 'w'), indent=0)
print(name, uniq)
