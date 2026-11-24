"""Guitar tabs from the guitar stem's MIDI (stems.py): a Guitar Pro 5 file for TuxGuitar / Guitar Pro / MuseScore
(tab + notation, playable) and a plain-text tab with the chord chart above the bars.

  <venv>/bin/python tools/soundtrack/tabs.py tools/soundtrack/out/stems/upper-morkezela
      -> <dir>/tabs/guitar.gp5, <dir>/tabs/guitar.txt

What it does with the transcription (a sketch, not a faithful score):
  - keeps notes a standard-tuned guitar can play (E2..D6), longer than a 32nd, not too quiet;
  - snaps them to a 16th grid at the track's tempo (stems.py padded the audio so bar 1 starts on a downbeat);
  - at most four notes at once (the loudest), one per string;
  - places every chord / note on strings with a dynamic programme: frets within a hand's reach (4 frets), the hand
    moving as little as it can between events, lower positions and open strings slightly preferred.
Needs PyGuitarPro in the stems venv (see stems.py)."""
import itertools, os, re, sys
import numpy as np
import pretty_midi
import guitarpro as gp

TUNING = [64, 59, 55, 50, 45, 40]           # strings 1..6: e B G D A E
NAMES = ['e', 'B', 'G', 'D', 'A', 'E']
FRETS = 20
MAX_POLY = 4
SPAN = 4


def load(path):
    pm = pretty_midi.PrettyMIDI(path)
    tempo = float(pm.get_tempo_changes()[1][0])
    notes = [n for inst in pm.instruments for n in inst.notes]
    return tempo, notes


def events(notes, tempo):
    """{16th index: [(pitch, velocity, length in 16ths)]}"""
    six = 60 / tempo / 4
    vmin = np.percentile([n.velocity for n in notes], 25) if notes else 0
    out = {}
    for n in notes:
        if not (TUNING[-1] <= n.pitch <= TUNING[0] + FRETS) or n.end - n.start < six / 2 or n.velocity < vmin:
            continue
        q = int(round(n.start / six))
        length = max(1, int(round((n.end - n.start) / six)))
        bucket = out.setdefault(q, {})
        if n.pitch not in bucket or bucket[n.pitch][0] < n.velocity:
            bucket[n.pitch] = (n.velocity, length)
    return {q: sorted(((p, v, l) for p, (v, l) in b.items()), key=lambda x: -x[1])[:MAX_POLY] for q, b in sorted(out.items())}


def options(pitches):
    """every way to put these pitches on distinct strings within reach, with a playability cost"""
    per = [[(s, p - TUNING[s]) for s in range(6) if 0 <= p - TUNING[s] <= FRETS] for p in pitches]
    res = []
    for combo in itertools.product(*per):
        strings = [s for s, _ in combo]
        if len(set(strings)) < len(strings):
            continue
        fretted = [f for _, f in combo if f > 0]
        span = (max(fretted) - min(fretted)) if fretted else 0
        if span > SPAN:
            continue
        pos = (sum(fretted) / len(fretted)) if fretted else 0.0
        res.append((0.15 * pos + 0.5 * span, pos, combo))
    if not res:                             # nothing fits one hand: drop the lowest note and try again
        return options(sorted(pitches)[1:]) if len(pitches) > 1 else []
    return sorted(res)[:16]


def assign(evs):
    """Viterbi over the events: each event's own cost plus the hand's travel from the previous one"""
    keys = list(evs)
    opts = [options([p for p, _, _ in evs[q]]) or [(0, 0.0, ())] for q in keys]
    cost = [o[0] for o in opts[0]]
    back = []
    for i in range(1, len(opts)):
        row, ptr = [], []
        for c, pos, _ in opts[i]:
            best = min(range(len(opts[i - 1])), key=lambda j: cost[j] + abs(opts[i - 1][j][1] - pos) * (0.3 if pos and opts[i - 1][j][1] else 0.05))
            row.append(cost[best] + c + abs(opts[i - 1][best][1] - pos) * (0.3 if pos and opts[i - 1][best][1] else 0.05))
            ptr.append(best)
        cost, back = row, back + [ptr]
    k = int(np.argmin(cost))
    path = [k]
    for ptr in reversed(back):
        k = ptr[k]
        path.append(k)
    path.reverse()
    return {q: opts[i][path[i]][2] for i, q in enumerate(keys)}


def chord_chart(folder):
    """bar -> chord from chords.md (stems.py)"""
    chords = {}
    try:
        text = open(os.path.join(folder, 'chords.md'), encoding='utf-8').read()
    except OSError:
        return chords
    for line in text.splitlines():
        m = re.match(r'\s*(\d+)\s+\d+:\d+\.\d+\s+\|(.*)\|\s*$', line)
        if m:
            for i, c in enumerate(x.strip() for x in m.group(2).split('|')):
                chords[int(m.group(1)) + i] = c
    return chords


DURS = [(16, False, 1), (16, True, None), (8, False, 2), (8, True, 3), (4, False, 4), (4, True, 6), (2, False, 8), (2, True, 12), (1, False, 16)]
SIZES = sorted(((n, v, d) for v, d, n in DURS if n), reverse=True)   # (16ths, value, dotted)


def split(n):
    out = []
    while n > 0:
        size, value, dotted = next(x for x in SIZES if x[0] <= n)
        out.append((size, value, dotted))
        n -= size
    return out


def write_gp(placed, evs, tempo, bars, title, path):
    song = gp.Song()
    song.title, song.tempo = title, int(round(tempo))
    track = song.tracks[0]
    track.name = 'Guitar'
    track.strings = [gp.GuitarString(i + 1, v) for i, v in enumerate(TUNING)]
    track.channel.instrument = 29                                   # overdriven guitar
    song.measureHeaders, track.measures = [], []
    for b in range(bars):
        header = gp.MeasureHeader(number=b + 1, start=960 + b * 3840)
        song.measureHeaders.append(header)
        measure = gp.Measure(track, header)
        track.measures.append(measure)
        voice = measure.voices[0]
        onsets = [q for q in placed if b * 16 <= q < (b + 1) * 16]
        cursor = b * 16
        for i, q in enumerate(onsets + [None]):
            target = q if q is not None else (b + 1) * 16
            for size, value, dotted in split(target - cursor):          # rests up to the next note
                voice.beats.append(gp.Beat(voice, duration=gp.Duration(value=value, isDotted=dotted), status=gp.BeatStatus.rest))
            cursor = target
            if q is None:
                break
            nxt = onsets[i + 1] if i + 1 < len(onsets) else (b + 1) * 16
            ring = min(nxt - q, max(l for _, _, l in evs[q]))
            first = True
            for size, value, dotted in split(ring):
                beat = gp.Beat(voice, duration=gp.Duration(value=value, isDotted=dotted), status=gp.BeatStatus.normal)
                for (string, fret), (p, v, _) in zip(placed[q], evs[q]):
                    beat.notes.append(gp.Note(beat, value=fret, string=string + 1, velocity=min(127, v + 20),
                                              type=gp.NoteType.normal if first else gp.NoteType.tie))
                voice.beats.append(beat)
                first = False
            cursor = q + ring
    gp.write(song, path)


def write_txt(placed, bars, tempo, chords, title, path, per_line=4):
    lines = [f'{title}: guitar tab (standard tuning EADGBE), {tempo:g} BPM, 4/4, one column = a 16th',
             'An automatic transcription of the AI guitar stem: a sketch to check by ear.', '']
    for start in range(0, bars, per_line):
        rng = range(start, min(bars, start + per_line))
        head = '    ' + ''.join(f'{(str(b + 1) + " " + chords.get(b + 1, "")):<{16 * 3 + 1}}' for b in rng)
        rows = []
        for s in range(6):
            row = NAMES[s] + ' |'
            for b in rng:
                for q in range(b * 16, (b + 1) * 16):
                    cell = '-'
                    for string, fret in placed.get(q, ()):
                        if string == s:
                            cell = str(fret)
                    row += cell.ljust(3, '-') if len(cell) < 3 else cell
                row += '|'
            rows.append(row)
        lines += [head] + rows + ['']
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))


def main(folder):
    folder = os.path.abspath(folder)
    name = os.path.basename(folder.rstrip('/'))
    tempo, notes = load(os.path.join(folder, 'midi', 'guitar.mid'))
    evs = events(notes, tempo)
    placed = assign(evs)
    # options() may have dropped a note that didn't fit one hand: pair each placed (string, fret) with its pitch
    for q in evs:
        pitch_of = {TUNING[s] + f: (s, f) for s, f in placed[q]}
        evs[q] = [e for e in evs[q] if e[0] in pitch_of]
        placed[q] = tuple(pitch_of[e[0]] for e in evs[q])
    placed = {q: v for q, v in placed.items() if v}
    bars = max(placed) // 16 + 1 if placed else 1
    out = os.path.join(folder, 'tabs')
    os.makedirs(out, exist_ok=True)
    write_gp(placed, evs, tempo, bars, name, os.path.join(out, 'guitar.gp5'))
    write_txt(placed, bars, tempo, chord_chart(folder), name, os.path.join(out, 'guitar.txt'))
    print(f'{name}: {len(notes)} notes in -> {sum(len(v) for v in placed.values())} on {len(placed)} beats, {bars} bars')


if __name__ == '__main__':
    for f in sys.argv[1:]:
        main(f)
