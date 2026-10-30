#!/usr/bin/env python3
"""Render 1920x1080 mockups of the proposed TV Detox home restyle.

Geometry follows CleanFrame's Dock layout (MIT): a 1504x232 glass panel at
(208, 676), 288x200 tiles on a 296 pitch, 48px panel radius, 32px tile radius.
Photographs, font and marks keep their own licences; see CREDITS.md.

    python3 -m venv /tmp/tvmock-venv
    /tmp/tvmock-venv/bin/pip install pillow
    /tmp/tvmock-venv/bin/python mockups/generate_mockups.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT = HERE

# The launcher lays out at 1920x1080 and scales to the TV. Render at 2x and
# downsample so curves and type stay clean in the PNGs.
SS = 2
W, H = 1920 * SS, 1080 * SS

DOCK = (208, 676, 1712, 908)
SHELF = (DOCK[0] + 16, DOCK[1], DOCK[0] + 16 + 1472, DOCK[3])
TILE_W, TILE_H, PITCH = 288, 200, 296
PANEL_R, TILE_R = 48, 32

INK = (244, 244, 241)
DARK = (20, 22, 24)
SCRIM = (4, 10, 12)
FONT = str(ASSETS / "fonts" / "Manrope-Variable.ttf")

_fonts = {}


def s(v):
    return int(round(v * SS))


def font(size, weight=500):
    key = (size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(FONT, s(size))
        f.set_variation_by_axes([weight])
        _fonts[key] = f
    return _fonts[key]


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


def veil(base, box, color, alpha):
    x0, y0, x1, y1 = [s(v) for v in box]
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fill = Image.new("RGBA", (x1 - x0, y1 - y0), color + (255,))
    fill.putalpha(int(255 * alpha))
    layer.paste(fill, (x0, y0))
    base.alpha_composite(layer)


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255
    )
    return m


def glass(base, box, radius, blur, veil_alpha, highlight=52):
    """A frosted panel rendered from the blurred wallpaper, with rounded corners.

    The field is opaque; veil_alpha is the dark tint laid over it, exactly like
    CleanFrame's registered material plus its veil.
    """
    x0, y0, x1, y1 = [s(v) for v in box]
    field = base.filter(ImageFilter.GaussianBlur(s(blur))).crop((x0, y0, x1, y1))
    panel = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    panel.alpha_composite(field)
    panel.alpha_composite(Image.new("RGBA", panel.size, (8, 14, 18, int(255 * veil_alpha))))
    # One hairline along the top, like CleanFrame's inset top edge.
    line = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    ImageDraw.Draw(line).line(
        [(s(radius), 0), (panel.size[0] - s(radius), 0)],
        fill=(255, 255, 255, highlight),
        width=max(1, s(1)),
    )
    panel.alpha_composite(line)
    panel.putalpha(Image.composite(panel.getchannel("A"), Image.new("L", panel.size, 0),
                                   rounded_mask(panel.size, s(radius))))
    base.alpha_composite(panel, (x0, y0))


def text_tracked(draw, xy, string, f, fill, tracking=0.0, anchor="la", shadow=0):
    x, y = xy
    total = sum(f.getlength(c) for c in string) + tracking * (len(string) - 1)
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    if shadow:
        sx = x
        for c in string:
            draw.text((sx, y + s(2)), c, font=f, fill=(0, 0, 0, shadow), anchor="l" + anchor[1])
            sx += f.getlength(c) + tracking
    for c in string:
        draw.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += f.getlength(c) + tracking


def tracked_width(string, f, tracking=0.0):
    return sum(f.getlength(c) for c in string) + tracking * (len(string) - 1)


def wallpaper(name, shade=True):
    im = Image.open(ASSETS / "wallpapers" / f"{name}.jpg").convert("RGB")
    im = im.resize((W, H), Image.LANCZOS).convert("RGBA")
    if shade:
        # Top shade and bottom scrim, baked in exactly as they will be in the app.
        top = vgrad(W, s(300), [(0, 0.32), (0.5, 0.14), (1, 0.0)])
        bottom = vgrad(W, s(520), [(0, 0.0), (0.7, 0.42), (1, 0.52)])
        for y0, alpha in ((0, top), (s(560), bottom)):
            layer = Image.new("RGBA", (W, alpha.size[1]), SCRIM + (255,))
            layer.putalpha(alpha)
            im.alpha_composite(layer, (0, y0))
    return im


def icon(path, max_w, max_h):
    im = Image.open(path).convert("RGBA")
    r = min(max_w / im.width, max_h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


# ---------- line icons, drawn at 24x24 like the launcher's LineIcon ----------

def stroke_icon(draw, kind, cx, cy, size, alpha):
    k = s(size) / 24.0
    w = max(2, int(round(1.8 * k)))
    col = (255, 255, 255, alpha)

    def p(x, y):
        return (s(cx) + (x - 12) * k, s(cy) + (y - 12) * k)

    if kind == "apps":
        for gx in (3.5, 13.2):
            for gy in (3.5, 13.2):
                draw.rounded_rectangle(
                    [p(gx, gy), p(gx + 7.3, gy + 7.3)], radius=1.6 * k, outline=col, width=w
                )
    elif kind == "settings":
        draw.ellipse([p(5.2, 5.2), p(18.8, 18.8)], outline=col, width=w)
        draw.ellipse([p(9.6, 9.6), p(14.4, 14.4)], outline=col, width=w)
        for i in range(8):
            import math
            a = math.radians(i * 45)
            draw.line([p(12 + 8.1 * math.cos(a), 12 + 8.1 * math.sin(a)),
                       p(12 + 10.4 * math.cos(a), 12 + 10.4 * math.sin(a))],
                      fill=col, width=w)
    elif kind == "inputs":
        draw.rounded_rectangle([p(2.5, 6.5), p(21.5, 17.5)], radius=2.4 * k, outline=col, width=w)
        draw.line([p(6.5, 17.5), p(6.5, 20.3)], fill=col, width=w)
        draw.line([p(17.5, 17.5), p(17.5, 20.3)], fill=col, width=w)
        draw.line([p(6.5, 20.3), p(17.5, 20.3)], fill=col, width=w)
        draw.line([p(6.2, 11.8), p(9.8, 11.8)], fill=col, width=w)
        draw.line([p(11.5, 11.8), p(15.1, 11.8)], fill=col, width=w)
    elif kind == "wifi":
        for r in (8.6, 5.7):
            draw.arc([p(12 - r, 12 - r + 3.2), p(12 + r, 12 + r + 3.2)],
                     start=218, end=322, fill=col, width=w)
        draw.ellipse([p(10.6, 15.3), p(13.4, 18.1)], fill=col)


def control_row(base, focused):
    """Inputs / Apps / Settings and the network glyph, top right, quiet by default."""
    draw = ImageDraw.Draw(base)
    f = font(28, 500)
    items = [("Inputs", "inputs"), ("Apps", "apps"), ("Settings", "settings"), (None, "wifi")]
    widths = []
    for label, _ in items:
        if label is None:
            widths.append(60)
        else:
            widths.append(38 + tracked_width(label, f, s(-0.4)) / SS + 14)
    gap = 6
    total = sum(widths) + gap * (len(widths) - 1)
    x = 1798 - total
    cy = 104
    for i, ((label, kind), wdt) in enumerate(zip(items, widths)):
        alpha = 255 if (focused == i) else 168
        if focused == i:
            pill = Image.new("RGBA", base.size, (0, 0, 0, 0))
            ImageDraw.Draw(pill).rounded_rectangle(
                [s(x - 2), s(72), s(x + wdt + 2), s(136)],
                radius=s(32), fill=(255, 255, 255, 42),
            )
            ImageDraw.Draw(pill).rounded_rectangle(
                [s(x - 2), s(72), s(x + wdt + 2), s(136)],
                radius=s(32), outline=(255, 255, 255, 72), width=max(1, s(1)),
            )
            base.alpha_composite(pill)
        draw = ImageDraw.Draw(base)
        if label is None:
            stroke_icon(draw, kind, x + wdt / 2, cy, 32, alpha)
        else:
            stroke_icon(draw, kind, x + 15, cy, 28, alpha)
            text_tracked(draw, (s(x + 38), s(cy - 14)), label, f,
                         (255, 255, 255, alpha), tracking=s(-0.4), shadow=44)
        x += wdt + gap


def clock(base, time_text, date_text):
    draw = ImageDraw.Draw(base)
    f = font(48, 500)
    text_tracked(draw, (s(140), s(62)), time_text, f, INK + (245,), tracking=s(-1.5), shadow=54)
    if date_text:
        text_tracked(draw, (s(140), s(121)), date_text, font(26, 500),
                     (255, 255, 255, 178), tracking=s(-0.1), shadow=44)


def dock(base, apps, focus=-1, scroll=0, selected=-1):
    glass(base, DOCK, PANEL_R, 28, 0.18, highlight=58)
    tiles = Image.new("RGBA", base.size, (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tiles)
    by_key = {k: v for k, v in apps}
    for i, (key, _) in enumerate(apps):
        x = DOCK[0] + 16 + i * PITCH - scroll
        y = DOCK[1] + 16
        if x > SHELF[2] or x + TILE_W < SHELF[0]:
            continue
        if i == focus:
            plate = Image.new("RGBA", (s(TILE_W), s(TILE_H)), (0, 0, 0, 0))
            alpha = vgrad(s(TILE_W), s(TILE_H), [(0, 0.30), (0.58, 0.16), (1, 0.22)])
            fill = Image.new("RGBA", (s(TILE_W), s(TILE_H)), (255, 255, 255, 255))
            fill.putalpha(alpha)
            plate.alpha_composite(fill)
            ImageDraw.Draw(plate).line(
                [(s(TILE_R), s(1)), (s(TILE_W) - s(TILE_R), s(1))],
                fill=(255, 255, 255, 92), width=max(1, s(1)),
            )
            plate.putalpha(Image.composite(plate.getchannel("A"), Image.new("L", plate.size, 0),
                                           rounded_mask(plate.size, s(TILE_R))))
            tiles.alpha_composite(plate, (s(x), s(y)))
        elif i == selected:
            plate = Image.new("RGBA", (s(TILE_W), s(TILE_H)), (255, 255, 255, 28))
            plate.putalpha(Image.composite(plate.getchannel("A"), Image.new("L", plate.size, 0),
                                           rounded_mask(plate.size, s(TILE_R))))
            tiles.alpha_composite(plate, (s(x), s(y)))

        focused = i == focus
        lift = s(-3) if focused else 0
        alpha = 255 if focused else 214
        mark = icon(ASSETS / "icons" / f"{key}.png", s(120), s(72))
        if focused:
            mark = mark.resize((int(mark.width * 1.04), int(mark.height * 1.04)), Image.LANCZOS)
        mx = s(x + 144) - mark.width // 2
        my = s(y + 70) - mark.height // 2 + lift
        tiles.alpha_composite(mark, (mx, my))
        label = by_key[key][0]
        lf = font(36, 500)
        tw = tracked_width(label, lf, s(-0.8))
        text_tracked(tdraw, (s(x + 144) - tw / 2, s(y + 128) + lift), label, lf,
                     (255, 255, 255, alpha), tracking=s(-0.8), shadow=36)
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).rectangle(
        [s(SHELF[0]), s(SHELF[1]), s(SHELF[2]), s(SHELF[3])], fill=255
    )
    tiles.putalpha(Image.composite(tiles.getchannel("A"), Image.new("L", base.size, 0), mask))
    base.alpha_composite(tiles)


def home(wallpaper_name, apps, focus, selected=-1, scroll=0, time_text="8:09",
         date_text="Thursday, 30 October", control_focus=-1, out="home.png"):
    base = wallpaper(wallpaper_name)
    clock(base, time_text, date_text)
    control_row(base, control_focus)
    dock(base, apps, focus=focus, scroll=scroll, selected=selected)
    base.convert("RGB").resize((W // SS, H // SS), Image.LANCZOS).save(OUT / out, optimize=True)
    print("wrote", out)


def settings_wallpaper(wallpaper_name="misty"):
    base = wallpaper("golden", shade=False)
    veil(base, (0, 0, 1920, 1080), (8, 12, 14), 0.36)
    glass(base, (208, 96, 1712, 984), PANEL_R, 42, 0.30, highlight=48)

    draw = ImageDraw.Draw(base)
    text_tracked(draw, (s(280), s(166)), "Wallpaper", font(56, 500), INK + (255,),
                 tracking=s(-1.6))
    text_tracked(draw, (s(280), s(238)), "Saved on this TV, not in the cloud.",
                 font(24, 500), (255, 255, 255, 150), tracking=s(-0.1))

    entries = [("misty", "Misty coast"), ("cove", "Quiet cove"), ("alpine", "Alpine glow"),
               ("golden", "Golden hour"), ("sydney", "Sydney harbour"), ("forest", "Forest mist")]
    row_x, row_y, row_w, row_h, row_gap = 280, 300, 584, 88, 8
    for i, (key, name) in enumerate(entries):
        y = row_y + i * (row_h + row_gap)
        focused = i == 0
        if focused:
            plate = Image.new("RGBA", (s(row_w), s(row_h)), (0, 0, 0, 0))
            ImageDraw.Draw(plate).rounded_rectangle(
                [0, 0, s(row_w) - 1, s(row_h) - 1], radius=s(20), fill=(243, 243, 239, 255)
            )
            base.alpha_composite(plate, (s(row_x), s(y)))
        thumb = Image.open(ASSETS / "wallpapers" / f"{key}-thumb.jpg").convert("RGB")
        thumb = thumb.resize((s(96), s(54)), Image.LANCZOS)
        mask = rounded_mask(thumb.size, s(8))
        base.paste(thumb, (s(row_x + 16), s(y + 17)), mask)
        draw = ImageDraw.Draw(base)
        color = DARK + (255,) if focused else (255, 255, 255, 230)
        text_tracked(draw, (s(row_x + 128), s(y + 25)), name, font(32, 500), color,
                     tracking=s(-0.5))
        if focused:
            # A simple check mark on the applied wallpaper.
            draw.line([(s(row_x + row_w - 48), s(y + 44)), (s(row_x + row_w - 38), s(y + 54)),
                       (s(row_x + row_w - 20), s(y + 34))], fill=DARK + (255,), width=s(3))

    # Right: the candidate photo, shown large.
    preview = Image.open(ASSETS / "wallpapers" / f"{wallpaper_name}.jpg").convert("RGB")
    pw, ph = 704, 396
    preview = preview.resize((s(pw), s(ph)), Image.LANCZOS)
    base.paste(preview, (s(928), s(300)), rounded_mask(preview.size, s(20)))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([s(928), s(300), s(928 + pw), s(300 + ph)], radius=s(20),
                           outline=(255, 255, 255, 46), width=max(1, s(1)))
    text_tracked(draw, (s(928), s(728)), "Misty coast", font(40, 500), INK + (255,),
                 tracking=s(-1.0))
    text_tracked(draw, (s(928), s(786)), "Applied", font(24, 500),
                 (255, 255, 255, 168), tracking=s(-0.1))
    text_tracked(draw, (s(280), s(900)), "Up/Down browse   OK keep   Back go back",
                 font(24, 500), (255, 255, 255, 140), tracking=s(-0.1))
    base.convert("RGB").resize((W // SS, H // SS), Image.LANCZOS).save(
        OUT / "03-settings-wallpaper.png", optimize=True)
    print("wrote 03-settings-wallpaper.png")


def settings_overview():
    base = wallpaper("misty", shade=False)
    veil(base, (0, 0, 1920, 1080), (8, 12, 14), 0.36)
    glass(base, (208, 96, 1712, 984), PANEL_R, 42, 0.30, highlight=48)

    draw = ImageDraw.Draw(base)
    text_tracked(draw, (s(280), s(166)), "Settings", font(56, 500), INK + (255,),
                 tracking=s(-1.6))
    text_tracked(draw, (s(280), s(238)), "Everything here stays on this TV.",
                 font(24, 500), (255, 255, 255, 150), tracking=s(-0.1))

    rows = [("Background", "Misty coast"),
            ("Apps on Home", "5 apps"),
            ("Inputs", "2 HDMI"),
            ("Google TV home", "Enabled"),
            ("Brightness", "TV picture"),
            ("TV settings", "All TV settings")]
    focus = 3
    row_x, row_y, row_w, row_h, row_gap = 280, 300, 620, 92, 8
    for i, (name, value) in enumerate(rows):
        y = row_y + i * (row_h + row_gap)
        if i == focus:
            plate = Image.new("RGBA", (s(row_w), s(row_h)), (0, 0, 0, 0))
            ImageDraw.Draw(plate).rounded_rectangle(
                [0, 0, s(row_w) - 1, s(row_h) - 1], radius=s(20), fill=(243, 243, 239, 255)
            )
            base.alpha_composite(plate, (s(row_x), s(y)))
        draw = ImageDraw.Draw(base)
        ink = DARK + (255,) if i == focus else (255, 255, 255, 235)
        sub = (60, 62, 64, 255) if i == focus else (255, 255, 255, 150)
        text_tracked(draw, (s(row_x + 28), s(y + 16)), name, font(32, 500), ink,
                     tracking=s(-0.5))
        text_tracked(draw, (s(row_x + 28), s(y + 54)), value, font(22, 500), sub,
                     tracking=s(-0.1))
        # A quiet chevron for rows that open another screen.
        chev = (s(row_x + row_w - 40), s(y + 40))
        draw.line([chev, (chev[0] + s(9), chev[1] + s(9)), (chev[0], chev[1] + s(18))],
                  fill=sub, width=s(2))

    # Right: a miniature of the committed home screen.
    preview = Image.open(OUT / "01-home-dock-misty.png").convert("RGB")
    pw, ph = 640, 360
    preview = preview.resize((s(pw), s(ph)), Image.LANCZOS)
    base.paste(preview, (s(976), s(300)), rounded_mask(preview.size, s(20)))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([s(976), s(300), s(976 + pw), s(300 + ph)], radius=s(20),
                           outline=(255, 255, 255, 46), width=max(1, s(1)))
    text_tracked(draw, (s(976), s(704)), "Home preview", font(32, 500), INK + (255,),
                 tracking=s(-0.6))
    text_tracked(draw, (s(976), s(752)), "Wallpaper and dock update together.",
                 font(22, 500), (255, 255, 255, 150), tracking=s(-0.1))
    text_tracked(draw, (s(280), s(924)), "OK open   Back close", font(24, 500),
                 (255, 255, 255, 140), tracking=s(-0.1))
    base.convert("RGB").resize((W // SS, H // SS), Image.LANCZOS).save(
        OUT / "04-settings-overview.png", optimize=True)
    print("wrote 04-settings-overview.png")


if __name__ == "__main__":
    apps = [
        ("youtube", ("YouTube", 0)),
        ("netflix", ("Netflix", 0)),
        ("primevideo", ("Prime Video", 0)),
        ("disneyplus", ("Disney+", 0)),
        ("plex", ("Plex", 0)),
    ]
    home("misty", apps, focus=1, out="01-home-dock-misty.png")
    more = apps + [("spotify", ("Spotify", 0)), ("appletv", ("Apple TV", 0))]
    home("alpine", more, focus=-1, selected=4, scroll=592, time_text="19:42",
         date_text="Friday, 31 October", control_focus=1, out="02-home-dock-alpine.png")
    settings_wallpaper()
    settings_overview()
