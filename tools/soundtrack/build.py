"""The game's soundtrack as an album: every music track the game plays (the placeholder .wavs left out), in the order a
player meets them, as MP3 320 kbps (Steam's soundtrack format) with ID3 tags and a square cover from the key art.

  python3 tools/soundtrack/build.py            # -> tools/soundtrack/out/Upper Morkezela (Original Soundtrack)/

The full game's music (dev) is a superset of the demo's (steam-demo): a track missing from the checkout is read from
those branches with `git show` (FULL_GAME_REFS), so the album builds the same on either branch.

The masters in assets/sounds are left alone. Per track:
  - loops made for the game (Flop is 24 s, Loop 84 s) play a few times and fade out, so they stand as album tracks;
  - loudness: a plain gain towards -14 LUFS, capped so the true peak stays at -1 dBTP or below (no limiter, so nothing
    is squashed: quiet takes such as the rehearsal through the wall end up a little under -14);
  - 48 kHz sources are resampled (soxr) to 44.1 kHz, the album standard, and encoded CBR 320 kbps.
tools/ is excluded from the game build (forge.config.js) and out/ is git-ignored, like the trailer and store art."""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SND = os.path.join(ROOT, 'assets', 'sounds')
ALBUM = 'Upper Morkezela (Original Soundtrack)'
OUT = os.path.join(ROOT, 'tools', 'soundtrack', 'out', ALBUM)
YEAR = '2026'
# Who made which track (the user, 2026-11-24); a track without `artist` is tagged with DEFAULT_ARTIST, which is also the
# album artist (a compilation)
DEFAULT_ARTIST = 'Various Artists'
ME = 'Matěj Antoš'
# the AI-generated tracks (Suno exports, tagged "squattw"): the name stays for now; they are to be replaced by recordings
AI = 'squattw'
TARGET_LUFS, MAX_TP = -14.0, -1.0
FULL_GAME_REFS = ['dev', 'steam-demo']        # where a track not in the checkout is looked up (the full game first)

# in the order the player hears them: menu, intro, the city, the Crossroad, the cathedral, Shed 521, Ortolan's
# courtyard, the street, the Screaming Cork, the Scraper, Elphi's studio, the skyship, the end of Day 1, the sealed
# cellar, the credits. `file` may list the names a track has on different branches (the demo renamed infinite_fold).
TRACKS = [
    dict(file='upper-morkezela.mp3', title='Upper Morkezela', artist=AI),                  # main menu
    dict(file='obazoba-hall.mp3', title='Obazoba Hall', artist=AI),                        # intro: Agarida and the Council
    dict(file=['infinite_fold.mp3', 'entry-theme.mp3'], title='Infinite Fold', artist=AI), # the city, Fungal Master Thaal
    dict(file='guitar-les.mp3', title='Les', artist=ME),                                   # the Crossroad in the woods
    dict(file='cathedral.mp3', title='Cathedral', artist=f'{ME} & Tomáš Kotásek'),                              # the Egg Cathedral
    dict(file='guitar-loop.ogg', title='Loop', artist=ME, loops=2, fade=10),               # the Shed 521 compound
    dict(file='flop.opus', title='Flop', artist=ME, loops=5, fade=8),                      # Ortolan's courtyard
    dict(file='guitar-pisen-4.mp3', title='Píseň č. 4', artist=ME),                        # Scraper street, Burning Bear St.
    dict(file='tavern-rehearsal.mp3', title='Rehearsal Through the Wall', artist=f'{ME} & Tomáš Kotásek'),      # the Screaming Cork tavern
    dict(file='feral-toast.mp3', title='Feral Toast', artist=AI),                          # the band in the club
    dict(file='make-the-suns-evaporate.mp3', title='Make the Suns Evaporate', artist='ASDF'),  # Lift-Mother
    dict(file='dr_elphi.mp3', title="Dr. Elphi's Lab", artist=AI),                         # Elphi's studio
    dict(file='guitar-let-bez-mezipristani.mp3', title='Let bez mezipřistání', artist=ME), # aboard the skyship
    # the full game only (dev)
    dict(file='sorrysatori-divinorium.mp3', title='Divinorium', artist='Sorry Satori'),                # the end of Day 1: the city at night
    dict(file='scrapped-song.mp3', title='Scrapped Song', artist='Atomic Candy Creeps'),                      # the sealed cellar under the Scraper
    dict(file='kdyz-brod-je-jeste-daleko.mp3', title='Když brod je ještě daleko', artist='Ciao Miao'),  # the credits
]


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def source(names, tmp):
    """the track's file: in the checkout, else from the full game's branches (git show), saved into tmp"""
    names = [names] if isinstance(names, str) else names
    for name in names:
        if os.path.exists(os.path.join(SND, name)):
            return os.path.join(SND, name), name
    for ref in FULL_GAME_REFS:
        for name in names:
            blob = subprocess.run(['git', '-C', ROOT, 'show', f'{ref}:assets/sounds/{name}'], capture_output=True)
            if blob.returncode == 0:
                path = os.path.join(tmp, name)
                with open(path, 'wb') as f:
                    f.write(blob.stdout)
                return path, f'{ref}:{name}'
    raise FileNotFoundError(f'{names}: not in assets/sounds nor on {FULL_GAME_REFS}')


def ffmpeg(*args):
    return run(['ffmpeg', '-hide_banner', '-nostdin', '-y', *args])


def samples(path):
    """exact length in samples of a decoded WAV"""
    info = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-count_packets', '-show_entries',
                           'stream=duration_ts', '-of', 'json', path]).stdout)
    return int(info['streams'][0]['duration_ts'])


def loudness(path):
    """integrated loudness (LUFS) and true peak (dBTP)"""
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind('Summary:'):]
    lufs = float(re.search(r'I:\s+(-?[\d.]+) LUFS', summary).group(1))
    tp = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summary).group(1))
    return lufs, tp


def cover(path):
    """1400 x 1400 square: Marti's painting at night with the main menu's (jungle) title, ORIGINAL SOUNDTRACK on its subtitle line
    (tools/storeart/store_art.py does the drawing, as for the Steam capsules)"""
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'storeart'))
    import store_art as sa
    # at night like the capsules; black above the painting so the title clears the spire
    art = sa.load_art()
    art = sa.extend_top(sa.night(art) if sa.AT_NIGHT else art, 0.14)
    img = sa.top_shade(sa.vignette(sa.grade(sa.crop(art, 1400, 1400, 0.0, 0.0, 0.81))), 0.35, 0.3)
    sa.put_title(img, 700, 225, 1000, subtitle='ORIGINAL SOUNDTRACK')
    img.convert('RGB').save(path, quality=92)


def main():
    os.makedirs(OUT, exist_ok=True)
    art = os.path.join(OUT, 'cover.jpg')
    cover(art)
    total = len(TRACKS)
    report = []
    with tempfile.TemporaryDirectory() as tmp:
        for n, t in enumerate(TRACKS, 1):
            src, where = source(t['file'], tmp)
            wav = os.path.join(tmp, f'{n:02d}.wav')
            ffmpeg('-i', src, '-c:a', 'pcm_f32le', wav)
            if t.get('loops', 1) > 1:              # the game's loop several times, sample-exact, then a fade-out
                size = samples(wav)
                looped = os.path.join(tmp, f'{n:02d}_loop.wav')
                dur = size * t['loops'] / 48000        # the loops are 48 kHz masters
                ffmpeg('-i', wav, '-af', f"aloop=loop={t['loops'] - 1}:size={size},"
                       f"afade=t=out:st={dur - t['fade']:.3f}:d={t['fade']}:curve=qsin", '-c:a', 'pcm_f32le', looped)
                wav = looped
            lufs, tp = loudness(wav)
            gain = min(TARGET_LUFS - lufs, MAX_TP - tp)
            artist = t.get('artist') or DEFAULT_ARTIST
            name = f"{n:02d} {t['title']}.mp3".replace('/', '-')
            dst = os.path.join(OUT, name)
            ffmpeg('-i', wav, '-i', art, '-map', '0:a', '-map', '1:v',
                   '-af', f'volume={gain:.2f}dB,aresample=44100:resampler=soxr:precision=28',
                   '-c:a', 'libmp3lame', '-b:a', '320k', '-c:v', 'mjpeg', '-disposition:v', 'attached_pic',
                   '-id3v2_version', '3', '-write_id3v1', '1',
                   '-metadata', f"title={t['title']}", '-metadata', f'artist={artist}',
                   '-metadata', f'album_artist={DEFAULT_ARTIST}', '-metadata', f'album={ALBUM}',
                   '-metadata', f'track={n}/{total}', '-metadata', 'disc=1/1', '-metadata', f'date={YEAR}',
                   '-metadata', 'genre=Soundtrack', '-metadata:s:v', 'title=Album cover',
                   '-metadata:s:v', 'comment=Cover (front)', dst)
            secs = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', wav]).stdout)
            report.append(f"{n:02d}  {int(secs // 60)}:{int(secs % 60):02d}  {lufs:6.1f} LUFS {tp:5.1f} dBTP  "
                          f"{gain:+5.1f} dB  {t['title']}  ({where})")
            print(report[-1], flush=True)
    with open(os.path.join(OUT, 'tracklist.txt'), 'w', encoding='utf-8') as f:
        f.write(f'{ALBUM}\n\n')
        for n, t in enumerate(TRACKS, 1):
            f.write(f"{n:02d}. {t['title']}\n")


if __name__ == '__main__':
    main()
