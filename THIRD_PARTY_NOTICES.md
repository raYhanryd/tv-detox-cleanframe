# Third-party notices

This file covers the assets and code distributed in this repository and in the built `out/tvhome.apk`. The mockups have their own notes in [mockups/CREDITS.md](mockups/CREDITS.md).

## TV Detox (base project)

This launcher is a fork of [Ansub/tv-detox](https://github.com/Ansub/tv-detox), Copyright (c) 2026 Ansub Khan, licensed under the **MIT License**. The full text is in [LICENSE](LICENSE). The original launcher code and its remaining assets are used and modified under that licence.

## CleanFrame (design reference)

The dock geometry, glass treatment and interaction ideas are based on [nthnclrk/CleanFrame](https://github.com/nthnclrk/CleanFrame), which is **MIT licensed**. CleanFrame is a Tizen web application; **no CleanFrame JavaScript, HTML, CSS or Tizen API code is copied or ported into this Android app**. The look was rebuilt independently in Java. CleanFrame's own notices are in its repository.

## Manrope font

**Manrope** is Copyright 2018 The Manrope Project Authors (<https://github.com/googlefonts/manrope>) and is licensed under the **SIL Open Font License, Version 1.1**.

- Bundled file: [`assets/fonts/Manrope-Variable.ttf`](assets/fonts/Manrope-Variable.ttf)
- Full licence text: [`assets/fonts/Manrope-OFL.txt`](assets/fonts/Manrope-OFL.txt)

The OFL permits bundling and redistribution with software. The font is not sold on its own.

## Wallpaper photographs

The six wallpapers are cropped, resized to 1920×1080 and have a top shade and bottom scrim baked in for legibility. The modified images are distributed under the [Unsplash License](https://unsplash.com/license), which permits free use, modification and distribution but not selling unmodified copies or building a competing image service. Attribution is not required by the licence; it is included here anyway.

| Shipped file | Photo | Photographer | Source |
| --- | --- | --- | --- |
| `res/drawable-nodpi/wallpaper_0.jpg` | Misty coast | Ganapathy Kumar | <https://unsplash.com/photos/n4VMQZIkgDg> |
| `res/drawable-nodpi/wallpaper_1.jpg` | Quiet cove | Joshua Wordel | <https://unsplash.com/photos/1L_5PT7EKzU> |
| `res/drawable-nodpi/wallpaper_2.jpg` | Forest mist | Dejan Zakic | <https://unsplash.com/photos/rr2EF3J5F2Y> |
| `res/drawable-nodpi/wallpaper_3.jpg` | Alpine glow | Cristina Gottardi | <https://unsplash.com/photos/CSpjU6hYo_0> |
| `res/drawable-nodpi/wallpaper_4.jpg` | Golden hour | Karthik Sreenivas | <https://unsplash.com/photos/tmtkhWbgMu8> |
| `res/drawable-nodpi/wallpaper_5.jpg` | Sydney Harbour | Caleb | <https://unsplash.com/photos/JmuyB_LibRo> |

CleanFrame checked the source pages on 20 October 2026. The original full-size files are in [`mockups/assets/wallpapers/`](mockups/assets/wallpapers/); the shipped copies are in `res/drawable-nodpi/`.

The pre-rendered dock glass (`dock_*.png`), settings glass (`panel_*.png`) and focus plate (`plate.png`) are derived from those photographs and these colours by [`tools/generate_assets.py`](tools/generate_assets.py). They carry the same Unsplash licence as the photographs they blur.

## App icons and brand marks

The launcher does **not** bundle app icons or brand logos. It asks Android's `PackageManager` for each installed app's own icon at runtime, so YouTube, Netflix, Plex, Spotify and other marks remain the property of their owners and are supplied by the installed apps. Brand names and marks are trademarks of their owners; this project claims no affiliation or endorsement.

The mockups under `mockups/` use Simple Icons (CC0), CleanFrame's Prime Video adaptation and its Disney+ drawing; those are design files and are credited in [mockups/CREDITS.md](mockups/CREDITS.md), not shipped in the APK.

## Tooling (not distributed)

- **Pillow** (PIL) renders the shipping bitmaps and mockups. It is a build-time tool only and is not packaged in the APK. Pillow is licensed under the HPND licence.
- **Temurin JDK 17**, **Android SDK / build-tools 34.0.0** and the **Android TV 14 emulator** are used only for building and testing and are not distributed.

## Optional third-party apps

**SmartTube** is mentioned in [GUIDE.md](GUIDE.md) as an optional separate installation for ad-free YouTube on Android TV. It is not bundled, downloaded or installed by this project. SmartTube is a separate open-source project by its authors; check its repository for its current licence, releases and security notices before installing it.

## Reporting a mistake

If an asset is missing a credit or is used outside its licence, open an issue on the repository and it will be corrected or removed.
