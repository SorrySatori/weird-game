# Warp a phone photo of the menu painting to the paper rectangle (corners measured by hand per photo). Usage: menu_wip_warp.py photo.jpg paper.png
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB')
src = [(75, 23), (1970, 37), (2038, 1396), (24, 1416)]  # paper corners: tl, tr, br, bl
W, H = 1960, 1386
inset = 6  # trim the paper's torn/shadowed margin
dst = [(-inset, -inset), (W + inset, -inset), (W + inset, H + inset), (-inset, H + inset)]
A, B = [], []
for (x, y), (u, v) in zip(src, dst):
    A.append([u, v, 1, 0, 0, 0, -u * x, -v * x]); B.append(x)
    A.append([0, 0, 0, u, v, 1, -u * y, -v * y]); B.append(y)
n = 8
M = [row[:] + [b] for row, b in zip(A, B)]
for i in range(n):
    p = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[p] = M[p], M[i]
    for r in range(n):
        if r != i:
            f = M[r][i] / M[i][i]
            M[r] = [a - f * b for a, b in zip(M[r], M[i])]
c = [M[i][n] / M[i][i] for i in range(n)]
im.transform((W, H), Image.PERSPECTIVE, tuple(c), Image.BICUBIC).save(sys.argv[2])
