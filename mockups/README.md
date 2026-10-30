# Home-screen mockups

Proposed home screen for this launcher, rebuilt natively after CleanFrame's Dock layout. These are images only; no Android code has been changed yet.

| Image | What it shows |
| --- | --- |
| [00-cleanframe-reference.jpg](00-cleanframe-reference.jpg) | CleanFrame's own browser preview, kept for comparison. Not part of this app. |
| [01-home-dock-misty.png](01-home-dock-misty.png) | Five apps, Netflix focused, Misty coast wallpaper, date under the clock. |
| [02-home-dock-alpine.png](02-home-dock-alpine.png) | Seven apps scrolled, Plex selected while the **Apps** control has focus, Alpine glow. |
| [03-settings-wallpaper.png](03-settings-wallpaper.png) | Wallpaper picker in the glass settings panel, Golden hour behind it. |
| [04-settings-overview.png](04-settings-overview.png) | Settings overview with the new **Google TV home** row and a live home preview. |

Regenerate with Pillow (development only, not part of the Android build):

```sh
python3 -m venv /tmp/tvmock-venv
/tmp/tvmock-venv/bin/pip install pillow
/tmp/tvmock-venv/bin/python mockups/generate_mockups.py
```

The renderer uses CleanFrame's measured dock geometry at 1920×1080, then downsamples from 2× for clean edges. All panels are rendered ahead of time; the mockups contain no runtime blur.

Assets and licences: [CREDITS.md](CREDITS.md). The plan and open questions: [docs/restyle-plan.md](../docs/restyle-plan.md).
