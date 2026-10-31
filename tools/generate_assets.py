#!/usr/bin/env python3
"""Render the launcher's shipping bitmaps ahead of time.

Run from the repo root with the project venv:

    .tools/venv/bin/python tools/generate_assets.py

Everything here is pre-rendered so the TV only decodes bitmaps: no runtime
blur. The six photographs come from mockups/assets/wallpapers and keep their
Unsplash licence (see THIRD_PARTY_NOTICES.md).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "mockups" / "assets" / "wallpapers"
OUT = HERE / "res" / "drawable-nodpi"

W, H = 1920, 1080
DOCK = (208, 676, 1712, 908)
PANEL = (208, 96, 1712, 984)
TILE_W, TILE_H, TILE_R = 288, 200, 32
PANEL_R = 48
SCRIM = (4, 10, 12)

NAMES = ["misty", "cove", "forest", "alpine", "golden", "sydney"]


def vgrad(w, h, stops):
    """A vertical alpha ramp (0-255) through (position, alpha) stops."""
    im = Image.new("L", (1, h))
    px = im.load()
    stops = sorted(stops)
    for y in range(h):
        t = y / max(1, h - 1)
        lo, hi = stops[0], stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                lo, hi = stops[i], stops[i + 1]
                break
        span = hi[0] - lo[0]
        k = 0 if span == 0 else (t - lo[0]) / span
        px[0, y] = int(255 * (lo[1] + (hi[1] - lo[1]) * k))
    return im.resize((w, h), Image.BILINEAR)


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255
    )
    return m


def wallpaper(name, shade=True):
    im = Image.open(SRC / f"{name}.jpg").convert("RGB")
    im = im.resize((W, H), Image.LANCZOS).convert("RGBA")
    if shade:
        # Keep the clock and the dock labels readable over any photo.
        top = vgrad(W, 300, [(0, 0.32), (0.5, 0.14), (1, 0.0)])
        bottom = vgrad(W, 520, [(0, 0.0), (0.7, 0.42), (1, 0.52)])
        for y0, alpha in ((0, top), (560, bottom)):
            layer = Image.new("RGBA", (W, alpha.size[1]), SCRIM + (255,))
            layer.putalpha(alpha)
            im.alpha_composite(layer, (0, y0))
    return im


def veil(im, alpha):
    layer = Image.new("RGBA", im.size, (8, 12, 14, int(255 * alpha)))
    im.alpha_composite(layer)


def glass(base, box, radius, blur, veil_alpha, scale, highlight=52):
    """A blurred, veiled crop with rounded corners, at `scale` of the UI size."""
    x0, y0, x1, y1 = box
    field = base.filter(ImageFilter.GaussianBlur(blur)).crop((x0, y0, x1, y1))
    panel = field
    panel.alpha_composite(Image.new("RGBA", panel.size, (8, 14, 18, int(255 * veil_alpha))))
    line = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    ImageDraw.Draw(line).line(
        [(radius, 0), (panel.size[0] - radius, 0)],
        fill=(255, 255, 255, highlight),
        width=1,
    )
    panel.alpha_composite(line)
    panel.putalpha(
        Image.composite(panel.getchannel("A"), Image.new("L", panel.size, 0),
                        rounded_mask(panel.size, radius))
    )
    size = (int(panel.width * scale), int(panel.height * scale))
    return panel.resize(size, Image.LANCZOS) if scale != 1 else panel


def plate():
    size = (TILE_W * 2, TILE_H * 2)
    alpha = vgrad(size[0], size[1], [(0, 0.30), (0.58, 0.16), (1, 0.22)])
    fill = Image.new("RGBA", size, (255, 255, 255, 255))
    fill.putalpha(alpha)
    ImageDraw.Draw(fill).line(
        [(TILE_R * 2, 2), (size[0] - TILE_R * 2, 2)],
        fill=(255, 255, 255, 92), width=2,
    )
    fill.putalpha(
        Image.composite(fill.getchannel("A"), Image.new("L", size, 0),
                        rounded_mask(size, TILE_R * 2))
    )
    return fill


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(NAMES):
        base = wallpaper(name)
        base.convert("RGB").save(OUT / f"wallpaper_{i}.jpg", quality=91, optimize=True)

        dock = glass(base, DOCK, PANEL_R, 32, 0.38, 0.5, highlight=58)
        dock.save(OUT / f"dock_{i}.png", optimize=True)

        dim = base.copy()
        veil(dim, 0.36)
        panel = glass(dim, PANEL, PANEL_R, 46, 0.42, 0.5, highlight=48)
        panel.save(OUT / f"panel_{i}.png", optimize=True)

    plate().save(OUT / "plate.png", optimize=True)

    total = sum(p.stat().st_size for p in OUT.glob("*"))
    print(f"wrote {len(NAMES)} wallpapers + {len(NAMES) * 2} glass panels + plate "
          f"({total / 1024 / 1024:.1f} MB) to {OUT}")


if __name__ == "__main__":
    main()
