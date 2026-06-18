"""
Generate icon.ico (and icon.png) for the app window / taskbar from the logo.

There's no SVG renderer available, so we redraw the logo with Pillow primitives
at high resolution, then downscale to the standard icon sizes. Run once:

    python make_icon.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

R = 1024                  # supersample resolution; downscaled at the end
C = R / 2                 # centre
S = R / 512.0             # scale factor from the 512-viewBox logo


def _hex(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def radial(img, cx, cy, rad, stops):
    """Draw a radial gradient by stacking concentric filled circles.

    stops: list of (offset 0..1, (r,g,b,a)). Outer-to-inner, smooth enough after
    the final downscale.
    """
    d = ImageDraw.Draw(img, 'RGBA')
    steps = int(rad)
    for i in range(steps, 0, -1):
        t = i / rad                      # 1 at edge, 0 at centre
        # find surrounding stops
        col = stops[-1][1]
        for j in range(len(stops) - 1):
            o0, c0 = stops[j]
            o1, c1 = stops[j + 1]
            if o0 <= t <= o1:
                f = (t - o0) / (o1 - o0) if o1 > o0 else 0
                col = _lerp(c0, c1, f)
                break
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=col)


def main():
    base = Image.new('RGBA', (R, R), (0, 0, 0, 0))

    # ---- circular backdrop (clipped to the disc) ----
    backdrop = Image.new('RGBA', (R, R), (0, 0, 0, 0))
    radial(backdrop, C, 200 * S, 242 * S, [
        (1.0, _hex('060a16') + (255,)),
        (0.45, _hex('0b1326') + (255,)),
        (0.0, _hex('16233f') + (255,)),
    ])
    # clip to disc
    mask = Image.new('L', (R, R), 0)
    ImageDraw.Draw(mask).ellipse([C - 242 * S, C - 242 * S, C + 242 * S, C + 242 * S], fill=255)
    base.paste(backdrop, (0, 0), mask)

    d = ImageDraw.Draw(base, 'RGBA')

    # ---- star field ----
    for x, y, r, a in [(120, 150, 2, 200), (395, 135, 1.6, 150), (420, 300, 2.2, 180),
                       (100, 350, 1.6, 150), (360, 395, 1.8, 180), (150, 410, 1.4, 130),
                       (440, 210, 1.4, 130), (80, 240, 1.6, 150)]:
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S],
                  fill=_hex('bfe8ff') + (a,))

    # ---- orbital rings (rotated ellipses on their own layers) ----
    for rx, ry, ang, op in [(168, 66, -24, 230), (150, 150, 0, 115), (172, 78, 58, 165)]:
        layer = Image.new('RGBA', (R, R), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer, 'RGBA')
        ld.ellipse([C - rx * S, C - ry * S, C + rx * S, C + ry * S],
                   outline=_hex('4ec8ff') + (op,), width=int(3 * S))
        layer = layer.rotate(-ang, center=(C, C), resample=Image.BICUBIC)
        base.alpha_composite(layer)

    # ---- glow layer (orbiting bodies + core), blurred ----
    glow = Image.new('RGBA', (R, R), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, 'RGBA')
    for x, y, r, col in [(396, 206, 8, '7fe9ff'), (128, 318, 6, '4fb8ff'), (316, 378, 5, '9af0ff')]:
        gd.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=_hex(col) + (255,))
    # warm core halo
    radial(glow, C, C, 96 * S, [
        (1.0, _hex('ff8a3c') + (0,)),
        (0.55, _hex('ffb347') + (200,)),
        (0.22, _hex('ffe09a') + (255,)),
        (0.0, _hex('fff6e0') + (255,)),
    ])
    glow = glow.filter(ImageFilter.GaussianBlur(10 * S))
    base.alpha_composite(glow)

    # re-draw crisp orbiting bodies on top of their glow
    for x, y, r, col in [(396, 206, 8, '7fe9ff'), (128, 318, 6, '4fb8ff'), (316, 378, 5, '9af0ff')]:
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=_hex(col) + (255,))

    # ---- four-point advisor star ----
    def star_points(cx, cy, outer, inner):
        pts = []
        for k in range(4):
            ang = math.radians(k * 90 - 90)          # tips up/right/down/left
            pts.append((cx + outer * math.cos(ang), cy + outer * math.sin(ang)))
            ang2 = math.radians(k * 90 - 45)
            pts.append((cx + inner * math.cos(ang2), cy + inner * math.sin(ang2)))
        return pts

    star = Image.new('RGBA', (R, R), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star, 'RGBA')
    sd.polygon(star_points(C, C, 88 * S, 30 * S), fill=_hex('ffd27a') + (255,))
    starglow = star.filter(ImageFilter.GaussianBlur(7 * S))
    base.alpha_composite(starglow)
    base.alpha_composite(star)
    d.ellipse([C - 26 * S, C - 26 * S, C + 26 * S, C + 26 * S], fill=_hex('fff7e6') + (255,))

    # ---- outer frame + ticks ----
    d.ellipse([C - 242 * S, C - 242 * S, C + 242 * S, C + 242 * S],
              outline=_hex('3fb0ee') + (255,), width=int(6 * S))
    d.ellipse([C - 230 * S, C - 230 * S, C + 230 * S, C + 230 * S],
              outline=_hex('2a89d6') + (130,), width=int(1.5 * S))
    for x1, y1, x2, y2 in [(256, 20, 256, 38), (256, 474, 256, 492),
                           (20, 256, 38, 256), (474, 256, 492, 256)]:
        d.line([x1 * S, y1 * S, x2 * S, y2 * S], fill=_hex('5fe6ff') + (220,), width=int(3 * S))

    here = os.path.dirname(os.path.abspath(__file__))
    big = base.resize((256, 256), Image.LANCZOS)
    big.save(os.path.join(here, 'icon.png'))
    big.save(os.path.join(here, 'icon.ico'),
             sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print('Wrote icon.ico and icon.png')


if __name__ == '__main__':
    main()
