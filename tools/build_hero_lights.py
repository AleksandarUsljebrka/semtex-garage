"""
Headlight light layers for the hero, generated from the single hero photo (frame 1, lights off).

The photo itself is never modified. Every layer is pure light on black, meant to be stacked on
top of the photo with `mix-blend-mode: screen`, so where a layer is black the photo shows
through untouched. Light that falls on surfaces (floor, bumper) is computed as the photo's own
pixels times an illumination map, so it follows the real texture of the wet floor instead of
painting over it.

Layers (docs/assets/img/hero/):
  light-drl-left / light-drl-right   daytime running light strips, one per headlight
  light-beam                          projector lenses + lens bloom
  light-spill                         light on the floor in front of the car, wet-floor
                                      reflections, a little light on the bumper
  light-haze                          faint beam in the air + soft horizontal glare

Run from the project root:  python tools/build_hero_lights.py      (needs opencv-python, numpy)
Writes preview composites with --preview DIR.
"""
import sys
import cv2
import numpy as np

BASE = 'docs/assets/img/hero/hero-01.jpg'
OUT = 'docs/assets/img/hero/'

base = cv2.imread(BASE)
if base is None:
    raise SystemExit(f'missing {BASE}')
H, W = base.shape[:2]                      # 608 x 1648
bf = base.astype(np.float32) / 255.0
lum = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

# --- geometry measured on the photo (1648x608 px) ---------------------------------------
HOUSING_R = [(1068, 340), (1098, 326), (1222, 318), (1246, 322), (1244, 356), (1226, 372), (1140, 370), (1078, 354)]
HOUSING_L = [(710, 346), (720, 326), (746, 321), (784, 333), (780, 347), (760, 364), (716, 366)]
AMBER_R = [(1228, 322), (1246, 322), (1244, 356), (1230, 360)]       # turn signal: stays dark
PROJ_R = (1193, 342, 15)                    # projector lens: x, y, radius
PROJ_L = (733, 340, 6)
FLOOR_Y = 520                               # where the floor starts in front of the bumper

# light colours (BGR, 0..1): cool LED white, never saturated blue
C_LED = np.array([1.0, 0.975, 0.93], np.float32)
C_BLOOM = np.array([1.0, 0.86, 0.70], np.float32)
C_SPILL = np.array([1.0, 0.95, 0.88], np.float32)


def poly_mask(points, feather=0.0):
    m = np.zeros((H, W), np.float32)
    cv2.fillPoly(m, [np.int32(points)], 1.0)
    return cv2.GaussianBlur(m, (0, 0), feather) if feather else m


def glow(mask, sigmas_weights):
    out = np.zeros_like(mask)
    for s, w in sigmas_weights:
        out += w * (cv2.GaussianBlur(mask, (0, 0), s) if s else mask)
    return out


def colorize(intensity, color):
    return intensity[..., None] * color[None, None, :]


def save(layer, name):
    # small dither so smooth glows don't band after compression
    noise = (np.random.default_rng(7).random(layer.shape[:2], np.float32) - 0.5) / 255.0
    img = np.clip((layer + noise[..., None]) * 255.0, 0, 255).astype(np.uint8)
    cv2.imwrite(OUT + name + '.webp', img, [cv2.IMWRITE_WEBP_QUALITY, 90])
    print('wrote', OUT + name + '.webp')
    return img


# --- DRL strips ---------------------------------------------------------------------------
# The light guides are the bright chrome-grey strips that outline each housing in the photo.
# Emission = how strongly a pixel is one of those strips (local brightness above its surroundings).
lift = lum ** 0.45
tophat = cv2.morphologyEx(lift, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
strip = np.clip((tophat - 0.26) / 0.16, 0, 1)
strip = cv2.morphologyEx(strip, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
strip = cv2.GaussianBlur(strip, (0, 0), 0.8)


def drl(housing):
    inside = poly_mask(housing, 1.2) * (1 - poly_mask(AMBER_R, 1.0))
    core = strip * inside
    # bright core, tight halo, wide soft halo (LED behind a light guide)
    i = glow(core, [(0, 0.95), (1.2, 0.55), (4, 0.20), (12, 0.08), (30, 0.035)])
    return colorize(np.clip(i, 0, 1.0), C_LED)


drl_r = drl(HOUSING_R)
drl_l = drl(HOUSING_L)

# --- low beams: projector lenses + bloom ----------------------------------------------------
def lens(p, squash=1.0):
    # a lit projector is a hot centre that falls off towards the lens rim, not a flat disc
    x, y, r = p
    d = np.sqrt(((xx - x) / r) ** 2 + ((yy - y) / (r * squash)) ** 2)
    hot = np.exp(-(d / 0.38) ** 2)
    body = np.clip(1 - d, 0, 1) ** 1.5 * 0.45
    return hot + body


lenses = lens(PROJ_R, 0.95) + lens(PROJ_L, 1.1)
housing_fill = (poly_mask(HOUSING_R, 2) * (1 - poly_mask(AMBER_R, 1.0)) + poly_mask(HOUSING_L, 2))
beam_i = (glow(lenses, [(0, 0.95), (3, 0.35), (9, 0.22), (22, 0.11), (50, 0.05), (110, 0.022)])
          + glow(housing_fill * lift ** 2, [(1.5, 0.14), (8, 0.05)]))
beam = colorize(np.clip(beam_i, 0, 1.0), C_LED) + colorize(
    glow(lenses, [(30, 0.08), (80, 0.04)]), C_BLOOM)

# --- spill: light landing on the scene, follows the photo's own texture ------------------
def pool(cx, cy, sx, sy, angle_deg):
    a = np.deg2rad(angle_deg)
    dx, dy = xx - cx, yy - cy
    u = dx * np.cos(a) + dy * np.sin(a)
    v = -dx * np.sin(a) + dy * np.cos(a)
    return np.exp(-((u / sx) ** 2 + (v / sy) ** 2))


floor = np.clip((yy - FLOOR_Y) / 14.0, 0, 1)
# pools of light thrown forward (towards the camera, slightly left) on the floor
illum = floor * (pool(690, 585, 330, 75, 8) + pool(1060, 590, 300, 70, 4) * 0.85
                 + 0.6 * pool(880, 545, 520, 40, 2))
# headlights also light the bumper and grille edge around them a little
illum += 0.55 * (pool(745, 350, 70, 50, 0) + pool(1160, 345, 110, 45, 0))
# wet floor: blurred vertical reflections under each headlight
streak = floor * (pool(730, 585, 15, 85, 90) + pool(1185, 585, 26, 85, 90) * 0.85
                  + 0.35 * (pool(730, 590, 45, 60, 90) + pool(1185, 590, 60, 60, 90)))
gloss = cv2.GaussianBlur(lum, (0, 0), 1.0)
spill = (colorize(illum, C_SPILL) * (bf * 3.6 + 0.07)
         + colorize(streak * (0.18 + 2.6 * gloss), C_LED))

# --- haze: faint beam through the air towards the dark left + soft horizontal glare --------
cone = np.zeros((H, W), np.float32)
for (hx, hy), length, spread in [((728, 344), 620, 0.16), ((1150, 346), 520, 0.10)]:
    d = np.clip((hx - xx) / length, 0, 1)                     # 0 at the lamp -> 1 far left
    half = 6 + spread * (hx - xx).clip(0)
    off = np.abs(yy - (hy + 0.10 * (hx - xx).clip(0)))
    cone += np.where(xx < hx, np.exp(-(off / half) ** 2) * (1 - d) ** 1.6, 0)
cone = cv2.GaussianBlur(cone, (0, 0), 10)
streak_h = np.zeros((H, W), np.float32)
for (hx, hy), w in [((730, 342), 1.0), ((1192, 342), 0.8)]:
    streak_h += w * np.exp(-(((xx - hx) / 260) ** 2 + ((yy - hy) / 2.2) ** 2))
haze = colorize(cone * 0.16, C_BLOOM) + colorize(cv2.GaussianBlur(streak_h, (0, 0), 1.5) * 0.12, C_LED)

layers = {
    'light-drl-left': drl_l,
    'light-drl-right': drl_r,
    'light-beam': beam,
    'light-spill': spill,
    'light-haze': haze,
}
saved = {name: save(layer, name) for name, layer in layers.items()}

if '--preview' in sys.argv:
    d = sys.argv[sys.argv.index('--preview') + 1]

    def screen(a, b):
        return 1 - (1 - a) * (1 - b)

    def comp(weights):
        out = bf.copy()
        for name, w in weights.items():
            out = screen(out, saved[name].astype(np.float32) / 255.0 * w)
        return (np.clip(out, 0, 1) * 255).astype(np.uint8)

    stages = {
        '1-off': {},
        '2-drl': {'light-drl-left': 1, 'light-drl-right': 1},
        '3-beam-half': {'light-drl-left': 1, 'light-drl-right': 1, 'light-beam': .5, 'light-spill': .35},
        '4-full': {'light-drl-left': 1, 'light-drl-right': 1, 'light-beam': 1, 'light-spill': 1, 'light-haze': 1},
    }
    for k, wts in stages.items():
        cv2.imwrite(f'{d}/{k}.jpg', comp(wts), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print('previews in', d)
