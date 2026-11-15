"""Strong attacks in a (live, free-tempo) recording, to cut a trailer on the music.

    python3 tools/trailer/onsets.py <audio file> <from s> <to s>   -> one line per attack: track time, strength

A log-energy rise over 20 ms, local maxima above 0.25; strengths above ~0.9 are the phrase accents (edit.js `announce`)."""
import sys, subprocess, array, math
f, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
SR, HOP = 8000, 40                                    # 5 ms hops
raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t0), '-t', str(t1 - t0), '-i', f, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
a = array.array('h'); a.frombytes(raw)
n = len(a) // HOP
le = [math.log(math.sqrt(sum(x * x for x in a[i * HOP:(i + 1) * HOP]) / HOP) + 1) for i in range(n)]
sm = [sum(le[max(0, i - 2):i + 1]) / len(le[max(0, i - 2):i + 1]) for i in range(n)]
flux = [0.0] + [max(0.0, sm[i] - sm[i - 4]) for i in range(1, n)] if n > 4 else []
peaks = []
for i in range(6, n - 6):
    if flux[i] == max(flux[i - 6:i + 7]) and flux[i] > 0.25:
        peaks.append((t0 + i * HOP / SR, flux[i]))
for t, s in peaks: print(f'{t:.3f} {s:.2f}')
