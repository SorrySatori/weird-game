"""Shared screen-space layout of the Council chamber (intro). The background, the table layer and the character
sprites are generated separately but must agree on where the table edge cuts the seated figures."""
import math

W, H = 1067, 600
VP = (533, 250)                                           # eye level of a standing person; F=891, camera 1.5 m
TABLE = dict(cx=533, cy=438, rx=370, ry=78, side=34)      # table-top ellipse + visible thickness of its rim
POOL = dict(cx=533, cy=440, rx=222, ry=42)                # the sunken pool of liquid mycelium in the middle
FRAME_W, FRAME_H = 128, 176                               # back-row frame (bottom-centre anchored)
END_W, END_H = 200, 350                                   # the two elders at the table's ends are nearer -> bigger
HAND_DROP = 22                                            # how far below the table edge the sleeves/hands reach

# back-row archpriests sit behind the far edge (cut at its edge in the sprite, hands lying on the table top);
# the two elders sit at the table's ends, nearer the camera, cropped by the frame edges and the screen bottom
SEATS = {
    'tynri':  dict(x=318, row='back'),
    'varhun': dict(x=533, row='back'),
    'rhull':  dict(x=748, row='back'),
    'elder_l': dict(x=84, row='end'),
    'elder_r': dict(x=983, row='end'),
}

def back_edge_y(x):
    """y of the table's far edge at screen x (None outside the table)"""
    u = (x - TABLE['cx']) / TABLE['rx']
    if abs(u) >= 1: return None
    return TABLE['cy'] - TABLE['ry'] * math.sqrt(1 - u * u)

def front_edge_y(x):
    u = (x - TABLE['cx']) / TABLE['rx']
    if abs(u) >= 1: return None
    return TABLE['cy'] + TABLE['ry'] * math.sqrt(1 - u * u)

def seat_anchor(name):
    """screen point of the sprite's bottom-centre origin"""
    s = SEATS[name]
    if s['row'] == 'back':
        return s['x'], round(back_edge_y(s['x'])) + HAND_DROP
    return s['x'], H
