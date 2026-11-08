"""The extra colour ramps of the waterside backgrounds (harbor_bg.py, delta_bg.py, redmass_bg.py), gathered for the
Aseprite palette waterside.gpl (python3 waterkit.py waterside.gpl)."""
from common import ramp
from waterkit import ALGAE, SILT, REED
RAMPS = [
    ('Yolk', ramp('#2a2412 #373016 #463c1b #554820 #655525 #75622b #867032 #977f3b')),
    ('Deck', ramp('#15130f #1f1c16 #2a261e #363127 #433d31 #514a3c #615849 #736957 #857964')),
    ('Granite', ramp('#151816 #1d211e #262b27 #303631 #3b423c #474f48 #555d55 #656c63 #757b71')),
    ('Tar', ramp('#121212 #1a1a19 #232321 #2d2c29 #383632 #44413b #514d45')),
    ('Iron', ramp('#121210 #1b1a17 #25231f #302d28 #3c3832 #4a453d #5a5449')),
    ('FogSky', ramp('#18221f #1e2a27 #25322e #2c3a35 #34433c #3d4c44 #46554c #506055 #5b6a5e #677466 #727d6e')),
    ('Murk', ramp('#0f1412 #141b18 #1a231f #212c27 #29352f #323f37 #3c4940 #47544a')),
    ('Brick', ramp('#1f1411 #2c1b16 #3a241d #4a2e24 #5a392c #6b4535 #7c5240 #8c5f4b')),
    ('Horn', ramp('#14100c #1e1711 #2a2016 #372a1c #453522 #54412a #644e33')),
    ('Verdigris', ramp('#18241f #20302a #2b3d35 #374b41 #455a4d')),
    ('Crystal', ramp('#3a0e0a #5c1a10 #842a16 #a8401e #c85a28 #e07a3a #f0a058')),
    ('Redmass', ramp('#1e0c0a #2e120e #431a13 #5a2418 #72301e #8a3e26')),
    ('Concrete', ramp('#161816 #1e211e #272a26 #31342f #3c3f39 #484a43 #55574f #63645b')),
    ('Mycelium', ramp('#2a3a22 #3c5230 #567044 #78905a #9cb07a #c4d4a0')),
    ('Algae', ALGAE), ('Silt', SILT), ('Reed', REED),
]
