"""Palette + materials for Feral Toast (the Screaming Cork Club band): muted, earthy ramps with many steps, in the
spirit of the hand-painted NPCs (Edgar). Aseprite: club.gpl."""
from common import ramp, INK
from pal_symb import VEIN
from rig import Mat

def R(s): return ramp(s)
SKIN_T  = R('#141a10 #1e2717 #29351e #354427 #42552f #516639 #627944 #758c52 #8a9f63')   # Telka's hide
JACKET  = R('#0b0b0d #121215 #19191d #212126 #2a2a30 #35353c #42424a #52525b #65656f')   # black leather
DENIM   = R('#101217 #171a21 #1f232c #282d38 #323845 #3e4553 #4b5362 #5b6473')
TEE     = R('#0d0d0f #141417 #1c1c20 #25252a #2f2f35 #3a3a41')
GUIT    = R('#0f160d #172114 #212d1b #2c3a23 #38482c #455836 #546942 #657b50 #788e60')   # the creature guitar
BONE2   = R('#4a4538 #625b4a #7b735e #948b74 #aca38a #c3baa0')
BRASS   = R('#2c2311 #44361a #5e4b23 #7a622e #96793b #b0914d #c8aa66 #dcc282')
STEEL   = R('#121519 #1a1f25 #232a32 #2d363f #38434e #44515d #52606c #63717d #77858f #8e9ba4')
RUST    = R('#24130b #3a1e10 #532b15 #6c3a1c #84491f')
BURST   = R('#170b05 #2e1508 #4a200c #692f12 #874419 #a35d27 #bb793b #d09652')            # sunburst bass
MAPLE   = R('#3c2a19 #574026 #725634 #8d6d44 #a68656 #bd9e6a')
BOARD   = R('#120c08 #1c130d #271b12 #332318')
FUR     = R('#150c07 #20130b #2c1b10 #392315 #472c1a #563520 #663f26 #774a2d #8a5735 #9c6640')
MUZZLE  = R('#3a2a1d #4f3a29 #654b36 #7c5f45 #937455 #a8896a')
VEST    = R('#0d0a09 #151110 #1e1816 #28201d #332a25 #403530 #4e4139')
LACQ    = R('#140808 #210d0c #2f1310 #3e1a15 #4e221b #602c22 #74372b')                    # oxblood shells
HEADS   = R('#4e493d #625c4e #776f5f #8c8471 #a19884 #b4ab96 #c6bea9')                    # coated drum heads
CYMBAL  = R('#261d0d #3b2e14 #54411b #6d5524 #876b2f #a0823c #b8994d #cfb064 #e2c780')
ROBE    = R('#0a0e0a #101710 #172017 #1f2a1e #283527 #314031 #3c4d3b #485a46')
SCARF   = R('#2e2a22 #403a2f #554d3d #6a614c #7f755d #94896e #a99d80 #bdb293')
CONSOLE = R('#090f0a #0f1810 #162217 #1d2c1e #253727 #2e4330 #39503a #455e45')
HANDS   = R('#262a22 #353b30 #474f40 #5a6351 #6e7863 #838d76')
EYE     = R('#6a4e08 #c89a18 #f4d040 #fff4b0')
CABLES  = R('#6e2a22 #8e7a2a #2e4a6e')
OUTLINE = (20, 15, 12)

M = {
    'skin': Mat(SKIN_T, 'skin', 0.2, 0.15), 'jacket': Mat(JACKET, 'leather', 0.18, 0.45), 'denim': Mat(DENIM, 'denim', 0.2),
    'tee': Mat(TEE, 'fabric', 0.2), 'guitar': Mat(GUIT, 'plain', 0.18, 0.5), 'bone': Mat(BONE2, 'plain', 0.25, 0.3),
    'brass': Mat(BRASS, 'metal', 0.2, 0.6), 'steel': Mat(STEEL, 'metal', 0.16, 0.55), 'rust': Mat(RUST, 'skin', 0.2),
    'burst': Mat(BURST, 'plain', 0.15, 0.6), 'maple': Mat(MAPLE, 'wood', 0.2, 0.3), 'board': Mat(BOARD, 'wood', 0.25),
    'fur': Mat(FUR, 'fur', 0.18), 'muzzle': Mat(MUZZLE, 'fur', 0.22), 'vest': Mat(VEST, 'leather', 0.18, 0.4),
    'lacq': Mat(LACQ, 'plain', 0.15, 0.7), 'heads': Mat(HEADS, 'fabric', 0.25), 'cymbal': Mat(CYMBAL, 'metal', 0.2, 0.7),
    'robe': Mat(ROBE, 'wool', 0.18), 'scarf': Mat(SCARF, 'wool', 0.22), 'console': Mat(CONSOLE, 'metal', 0.16, 0.35),
    'hands': Mat(HANDS, 'skin', 0.22), 'nose': Mat(VEST, 'plain', 0.2, 0.9),
}

ALL = [INK, OUTLINE, EYE[0], EYE[1], EYE[2], EYE[3]] + SKIN_T + JACKET + DENIM + TEE + GUIT + BONE2 + BRASS + STEEL + RUST + \
      BURST + MAPLE + BOARD + FUR + MUZZLE + VEST + LACQ + HEADS + CYMBAL + ROBE + SCARF + CONSOLE + HANDS + CABLES + VEIN
ALL += [m.outline for m in M.values()]

def write_gpl(path):
    seen, rows = set(), []
    for c in ALL:
        if c in seen: continue
        seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    with open(path, 'w') as f:
        f.write('GIMP Palette\nName: club\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
