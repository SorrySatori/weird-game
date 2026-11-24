"""Recording material from a finished track (for re-recording the AI tracks by people): the track split into stems, MIDI
of the melodic stems, and the tempo, key and a chord chart per bar.

  <venv>/bin/python tools/soundtrack/stems.py assets/sounds/upper-morkezela.mp3
      -> tools/soundtrack/out/stems/<name>/  (git-ignored)
         stems/{drums,bass,guitar,piano,vocals,other}.wav   Demucs htdemucs_6s, 44.1 kHz, padded onto the bar grid
         midi/{bass,guitar,piano,vocals,other}.mid           basic-pitch, written at the detected tempo
         <name>.mid                                          all of them in one file, a track per stem
         chords.md                                           tempo, key, a chord per bar with its time

Into FL Studio: set the project tempo to the BPM in chords.md, drop the stems and the MIDI at bar 1: a little silence in
front puts the first downbeat on a bar line, so the grid, the metronome and the chart's bar numbers match the music. The MIDI is a sketch to clean up, not a transcription; for tabs, open a stem's .mid in TuxGuitar or
Guitar Pro, which lay it out on strings.

The venv (Python 3.12; basic-pitch runs on ONNX, so no TensorFlow):
  uv venv -p 3.12 <venv> && VIRTUAL_ENV=<venv> uv pip install --index-url https://download.pytorch.org/whl/cpu torch torchaudio
  VIRTUAL_ENV=<venv> uv pip install demucs librosa soundfile pretty_midi onnxruntime mir_eval resampy
  VIRTUAL_ENV=<venv> uv pip install --no-deps basic-pitch"""
import os, subprocess, sys
import numpy as np
import soundfile as sf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SR = 44100
NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
# General MIDI programs, so a DAW opens each part with a fitting sound
PROGRAM = {'bass': 33, 'guitar': 29, 'piano': 0, 'vocals': 53, 'other': 89}


def decode(path):
    """any audio -> float32 stereo at 44.1 kHz (ffmpeg)"""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).T.copy()


def separate(audio):
    import torch
    from demucs.pretrained import get_model
    from demucs.apply import apply_model
    model = get_model('htdemucs_6s')
    model.eval()
    wav = torch.from_numpy(audio)
    ref = wav.mean(0)
    mean, std = ref.mean(), ref.std()
    with torch.no_grad():
        sources = apply_model(model, ((wav - mean) / std)[None], device='cpu', shifts=1, split=True, overlap=0.25,
                              progress=True, num_workers=4)[0]
    sources = sources * std + mean
    return {name: src.numpy() for name, src in zip(model.sources, sources)}


def tempo_grid(mono):
    """tempo and the time of the first downbeat, for a track in a steady tempo (generated and sequenced ones are).
    The beat tracker only gives a first guess: its beat times come in whole frames and it wanders on syncopated
    tracks (Dr. Elphi's Lab: 118 to 123 BPM). The tempo is read from the autocorrelation of the onset strength over
    the whole track at 8, 16 and 32 beats' distance (an error of a frame spread over many beats), and snapped to a
    whole BPM when it's that close. The phase: the onset strength folded over one beat, then over one bar (its
    strongest beat is taken as the downbeat, usually the kick on one)."""
    import librosa
    hop = 256
    env = librosa.onset.onset_strength(y=mono, sr=SR, hop_length=hop)
    fps = SR / hop
    _, beats = librosa.beat.beat_track(onset_envelope=env, sr=SR, hop_length=hop, units='time', tightness=120)
    ibi = float(np.median(np.diff(beats)))
    e = env - env.mean()
    acf = np.correlate(e, e, mode='full')[len(e) - 1:]
    periods = []
    for k in (8, 16, 32):
        lag = k * ibi * fps
        lo, hi = int(lag * 0.97), min(len(acf) - 2, int(lag * 1.03) + 1)
        if hi <= lo + 2:
            continue
        i = lo + int(np.argmax(acf[lo:hi]))
        y0, y1, y2 = acf[i - 1], acf[i], acf[i + 1]
        frac = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2) if (y0 - 2 * y1 + y2) != 0 else 0.0
        periods.append((i + frac) / fps / k)
    ibi = float(np.median(periods)) if periods else ibi
    tempo = 60 / ibi
    if abs(tempo - round(tempo)) < 0.3:
        tempo = float(round(tempo))
    ibi = 60 / tempo
    t = np.arange(len(env)) / fps
    beat_phase = np.angle((env * np.exp(2j * np.pi * t / ibi)).sum()) / (2 * np.pi) % 1 * ibi
    # which of the four beats starts the bar: the one with the most onset strength on it
    strength = [env[np.clip(np.round((beat_phase + j * ibi + np.arange(0, t[-1], 4 * ibi)) * fps).astype(int), 0, len(env) - 1)].sum()
                for j in range(4)]
    downbeat = beat_phase + int(np.argmax(strength)) * ibi
    first = beats[0] if len(beats) else 0.0                         # the music's first tracked beat ...
    downbeat += np.floor((first - downbeat) / (4 * ibi) + 0.5) * 4 * ibi   # ... and the bar line nearest to it
    while downbeat < 0:
        downbeat += 4 * ibi
    return tempo, downbeat


def key_of(chroma):
    """Krumhansl-Schmuckler: the major / minor profile that correlates best with the track's average chroma"""
    major = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    avg = chroma.mean(axis=1)
    best = max(((np.corrcoef(avg, np.roll(p, k))[0, 1], k, m) for k in range(12) for p, m in ((major, ''), (minor, 'm'))))
    return f'{NOTE_NAMES[best[1]]}{best[2]}'


def chord_chart(harmonic, bass, bar, duration):
    """a triad per bar from the harmonic stems' chroma (major / minor templates), the bass stem's lowest pitch class
    as the root hint. The audio is already padded onto the grid, so bar k starts at k * bar (FL's bar k + 1)."""
    import librosa
    hop = 2048
    chroma = librosa.feature.chroma_cqt(y=harmonic, sr=SR, hop_length=hop)
    bchroma = librosa.feature.chroma_cqt(y=bass, sr=SR, hop_length=hop)
    times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=SR, hop_length=hop)
    templates = []
    for root in range(12):
        for name, ivs in (('', (0, 4, 7)), ('m', (0, 3, 7))):
            t = np.zeros(12); t[[(root + i) % 12 for i in ivs]] = 1
            templates.append((f'{NOTE_NAMES[root]}{name}', root, t / np.linalg.norm(t)))
    bar_starts = list(np.arange(0, duration, bar))
    rows = []
    for i, start in enumerate(bar_starts):
        end = bar_starts[i + 1] if i + 1 < len(bar_starts) else duration
        sel = (times >= start) & (times < end)
        if not sel.any():
            continue
        c = chroma[:, sel].mean(axis=1)
        b = bchroma[:, sel].mean(axis=1)
        if c.max() < 0.15:
            rows.append((i + 1, start, 'N.C.')); continue
        c = c / (np.linalg.norm(c) + 1e-9)
        score = [(c @ t) + 0.15 * (b[root] / (b.max() + 1e-9)) for name, root, t in templates]
        rows.append((i + 1, start, templates[int(np.argmax(score))][0]))
    return rows, key_of(chroma)


def transcribe(stems, tempo, out, name):
    import pretty_midi
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict
    combined = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    for stem, program in PROGRAM.items():
        path = os.path.join(out, 'stems', f'{stem}.wav')
        # a near-empty stem (an instrumental's vocals, a track without piano) would transcribe only bleed and noise
        if stem not in stems or 20 * np.log10(np.sqrt((stems[stem] ** 2).mean()) + 1e-9) < -42:
            continue
        _, midi, _ = predict(path, ICASSP_2022_MODEL_PATH, onset_threshold=0.6, frame_threshold=0.35,
                             minimum_note_length=90, **({'maximum_frequency': 400} if stem == 'bass' else {}))
        notes = [n for inst in midi.instruments for n in inst.notes]
        if not notes:
            continue
        single = pretty_midi.PrettyMIDI(initial_tempo=tempo)        # note times are seconds, so they stay put
        for pm in (single, combined):
            inst = pretty_midi.Instrument(program=program, name=stem)
            inst.notes = [pretty_midi.Note(n.velocity, n.pitch, n.start, n.end) for n in notes]
            pm.instruments.append(inst)
        single.write(os.path.join(out, 'midi', f'{stem}.mid'))
    combined.write(os.path.join(out, f'{name}.mid'))


def main(src):
    name = os.path.splitext(os.path.basename(src))[0]
    out = os.path.join(ROOT, 'tools', 'soundtrack', 'out', 'stems', name)
    for d in ('stems', 'midi'):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    audio = decode(src)
    print(f'{name}: {audio.shape[1] / SR:.1f} s, separating…', flush=True)
    stems = separate(audio)
    tempo, downbeat = tempo_grid(audio.mean(0))
    # silence in front so the first downbeat starts a bar: in a DAW at this tempo the grid, the metronome and the bar
    # numbers below all match the music
    bar = 4 * 60 / tempo
    pad = (bar - downbeat % bar) % bar
    n = round(pad * SR)
    stems = {k: np.pad(v, ((0, 0), (n, 0))) for k, v in stems.items()}
    for k, v in stems.items():
        sf.write(os.path.join(out, 'stems', f'{k}.wav'), v.T, SR, subtype='FLOAT')
    duration = stems['drums'].shape[1] / SR
    harmonic = sum(stems[k].mean(0) for k in ('guitar', 'piano', 'other') if k in stems)
    rows, key = chord_chart(harmonic, stems['bass'].mean(0), bar, duration)
    first_bar = int((downbeat + pad) / bar + 1e-6) + 1
    print(f'tempo {tempo:g} BPM, key {key}, pad {pad:.3f} s; transcribing…', flush=True)
    transcribe(stems, tempo, out, name)
    with open(os.path.join(out, 'chords.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {name}\n\n'
                f'**Tempo {tempo:g} BPM**, 4/4 · tónina ≈ **{key}** · první doba = začátek taktu {first_bar}\n\n'
                f'Do FL Studia: nastav tempo projektu na {tempo:g} BPM, stopy (stems/*.wav) i MIDI dej na začátek taktu 1.\n'
                f'Na začátek jsem přidal {pad:.2f} s ticha, aby první doba padla přesně na takt: mřížka, metronom i čísla taktů\n'
                f'níž pak sedí s hudbou.\n\n'
                f'Akordy jsou odhad po taktech z kytary, kláves a zbytku (jen kvintakordy, bez septim): ověř je uchem.\n'
                f'První dobu taktu odhaduju podle nejsilnějšího úderu; když ti takty nesedí o půl taktu, posuň stopy o dvě doby.\n'
                f'Čtyři takty na řádek; číslo = takt ve FL, čas = kde řádek začíná v původní skladbě.\n\n```\n')
        for i in range(0, len(rows), 4):
            line = rows[i:i + 4]
            t = max(0.0, line[0][1] - pad)
            f.write(f"{line[0][0]:>3}  {int(t // 60)}:{t % 60:05.2f}  | " + ' | '.join(f'{c:<4}' for _, _, c in line) + ' |\n')
        f.write('```\n')
    print(f'-> {os.path.relpath(out, ROOT)}')


if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1]))
