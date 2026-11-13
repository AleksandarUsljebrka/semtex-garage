"""
Build the hero headlight frames from hero-frames-sheet.webp (project root).

The sheet is a 2 x 3 contact sheet (1672x941) of one shot, read left->right, top->bottom:
  1 lights off, 2-3 daytime running lights, 4-5 low beams coming on, 6 full beams.

The three rows of the sheet were scaled to slightly different heights (310 / 311 / 314 px),
which squashes rows 2 and 3 vertically. Each frame is therefore put back into frame 1's
geometry with a pure vertical rescale + shift (measured on the car body, lit areas excluded).
Horizontal scale is never touched, nothing is warped locally, so the car keeps its shape.

Output: docs/assets/img/hero/hero-01.webp|.jpg, 1648x608 (2x Lanczos) - only frame 1 is used now;
the headlights are generated as light layers by tools/build_hero_lights.py.
Run from the project root:  python tools/build_hero_frames.py   (needs opencv-python, numpy)
"""
import cv2
import numpy as np

SHEET = 'hero-frames-sheet.webp'
OUT = 'docs/assets/img/hero/'
K = 2

# sheet cells (x0, x1, y0, y1), separators are 3px white lines
CELLS = [(0, 835, 0, 310), (838, 1672, 0, 310),
         (0, 835, 313, 624), (838, 1672, 313, 624),
         (0, 835, 627, 941), (838, 1672, 627, 941)]

# raw cell -> frame 1 coordinates: x' = x + tx, y' = sy * y + ty   (frame 1 window = x 1.., y 2..)
ALIGN = [(1.0, -1.0, -2.0),
         (1.0, -0.5, -2.0),
         (1.01, -0.75, -4.0),
         (1.01, -0.5, -4.0),
         (1.0325, -0.5, -6.75),
         (1.0325, 0.25, -6.75)]

W, H = 832, 308          # frame 1 window
CROP = (4, 4, 2, 2)      # trim left, right, top, bottom after alignment (edge resampling)

sheet = cv2.imread(SHEET)
if sheet is None:
    raise SystemExit(f'missing {SHEET}')

l, r, t, b = CROP
# only frame 1 (lights off) is used; the lights are added by tools/build_hero_lights.py
for i, ((x0, x1, y0, y1), (sy, tx, ty)) in enumerate(zip(CELLS[:1], ALIGN[:1]), 1):
    cell = sheet[y0:y1, x0:x1].astype(np.float32)
    m = np.float32([[1, 0, tx], [0, sy, ty]])
    f = cv2.warpAffine(cell, m, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    f = f[t:H - b, l:W - r]
    f = cv2.resize(f, (f.shape[1] * K, f.shape[0] * K), interpolation=cv2.INTER_LANCZOS4)
    f = np.clip(f, 0, 255).astype(np.uint8)
    name = OUT + 'hero-%02d' % i
    cv2.imwrite(name + '.webp', f, [cv2.IMWRITE_WEBP_QUALITY, 86])
    cv2.imwrite(name + '.jpg', f, [cv2.IMWRITE_JPEG_QUALITY, 86, cv2.IMWRITE_JPEG_PROGRESSIVE, 1,
                                   cv2.IMWRITE_JPEG_OPTIMIZE, 1])
    print('wrote', name, f.shape[1], 'x', f.shape[0])
