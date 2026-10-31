# Restyling the home screen after CleanFrame

**Status: implemented and verified on the emulator (2026-10-31). Not yet installed on the TV.**

The mapping below is kept as the design record. Where the shipped build differs from the original proposal, the difference is called out.

## What this workspace is

- Base: [Ansub/tv-detox](https://github.com/Ansub/tv-detox) upstream `main` (version 1.5.7), mirrored to the owner's public repo <https://github.com/raYhanryd/tv-detox-cleanframe>. `origin` stays read-only.
- tv-detox has no `AGENTS.md`; the original discovery read `README.md`, `docs/debloat.md`, the manifest, `build.sh`, `install.sh`/`candidates.sh`/`undo.sh` interfaces, and all of `src/com/ansub/tvhome/`.
- CleanFrame reference: cloned separately (not part of this app). Read `AGENTS.md`, `README.md`, `docs/development.md`, `docs/interaction-behaviour.md`, `docs/assets.md`, `docs/asset-sources.md`, `THIRD_PARTY_NOTICES.md`, `app/style.css`, and the dock/item geometry in `app/main.js`. No CleanFrame code was ported; it is a Tizen web app, this stays native Java.

## Mapping: CleanFrame → this launcher

| CleanFrame element | What was built |
| --- | --- |
| Full-bleed photograph, top shade + bottom scrim | Six 1920×1080 JPEGs with the shade and scrim baked in by `tools/generate_assets.py`. One window background, no overlay views. |
| Dock: 1504×232 at (208, 676), 288×200 tiles, 296 pitch, 48px panel, 32px plate | Same geometry, laid out at 1920×1080 and scaled by screen width. |
| Glass material rendered ahead of time | Per-wallpaper frosted dock pane (blur 28 + veil, rounded corners baked in) and settings pane (blur 42). Runtime only decodes a bitmap; no blur. |
| Focused tile plate | Pre-rendered `plate.png`, white at 24% alpha. Alpha 0→1 over 120 ms; icon and label lift 3 dp and scale 1.04 over 180 ms with `withLayer()`. No relayout. |
| Clock at top left | `TextClock`, following the TV's existing 12/24 preference. **Show date** (default off) adds a second line. |
| Art Mode / All apps / Settings top right | Inputs / Apps / Settings, then the live Wi-Fi/Ethernet/offline icon. Up from the dock reaches them, Back returns. |
| Dock scrolls left/right | Horizontal scrolling with focus, via `HorizontalScrollView`. It uses scroll transforms, not a bespoke `translationX` animation, so no layout runs during movement. |
| Settings sheet over the blurred stage | A pre-rendered glass panel: Wallpaper, Apps on Home, Inputs, Show date, App labels, Google TV home, Brightness (non-box TVs), TV settings. |
| Wallpaper picker | Two panes: six thumbnails on the left, half-res preview on the right. OK applies and saves; Back keeps the current wallpaper. |
| Icon + name labels under dock icons | **App labels** setting: icons + names (default) or icons only. |
| List layout, icons-only mode, font catalog, material/tint choices, rotation modes | Not in v1. |

## Existing behaviour that stays

- App launching (leanback intent first, then normal launch intent), package add/remove refresh.
- HDMI inputs from `TvInputManager`, rename/remove menus and the Live TV fallback chain.
- Clock handling and the `clock` install override; network state and the Wi-Fi/Ethernet/offline icon.
- Hold OK / Menu on an app: Move, Replace, Remove, Uninstall/App info. The **Add app** tile stays at the end of the dock.
- Hold Back opens Google TV's home screen (`HomeButton.openGoogleTv`); the accessibility Home-button service is untouched.
- Bluetooth/Sound/Picture shortcuts that `install.sh --es quick` enables remain top-right controls, not Settings rows.
- `build.sh`, `install.sh`, `undo.sh`, `check.sh`, `candidates.sh` interfaces stay compatible.

## What cannot match exactly

- **Live blur.** Android 11 has no cheap backdrop blur and the project rules it out. Every panel is pre-rendered per wallpaper; changing wallpaper swaps the background and dock pane together.
- **Pixel-identical CSS.** Gradients, easing and letter spacing are close, not identical.
- **Brand marks.** The launcher does not bundle brand icons; Android supplies each installed app's icon. This avoids stale or trademark-encumbered marks, but some TV app icons are low-resolution.
- **Shelf edge fades and overscroll.** Native clipping shows a partially visible tile instead of a CSS mask fade.
- **Settings depth.** CleanFrame's per-group two-pane appearance screens are simplified to one panel and one picker.
- **60 fps guarantee.** The app avoids layout and blur on the animation path; the real frame times must be measured on the ORCA.

## Measured budget (emulator)

Measured on the Android TV 14 API 34 emulator with host GPU:

| Item | Result |
| --- | --- |
| Total PSS | **31.7 MB** |
| Total RSS | **145.9 MB** |
| Java heap | ~1.8 MB |
| Native heap | ~21.9 MB |
| Swap | 0 |
| Frames after 16 focus moves + up/down/back | 54 total, **2 janky (3.7%)** |
| Frame percentiles | p50 **21 ms**, p90 **24 ms**, p99 **38 ms** |
| Missed vsync / slow UI thread | 0 / 0 |

The original estimate of ~39–40 MB assumed a full-screen ARGB wallpaper plus a second crossfade copy. The shipped build has no crossfade duplicate and keeps one wallpaper, so the measured total is lower. Expect the TV's numbers to differ; measure them there.

Animation rules: transform/alpha only; `withLayer()` while a tile moves; no `requestLayout` in listeners; wallpaper and glass decoded before being shown; no runtime blur; no new views per frame.

## Assets and licences

Mockup assets are in `mockups/` with credits in [CREDITS.md](../mockups/CREDITS.md). Shipping assets are covered by [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

- **Fonts:** Manrope (SIL OFL 1.1), variable TTF, licence text bundled at `assets/fonts/Manrope-OFL.txt`. Geist and Newsreader are not bundled.
- **Photos:** the six approved Unsplash photographs, bundled at 1920×1080 with a baked top shade and bottom scrim, with credits. The Unsplash licence allows copying, modification and distribution with restrictions (no selling unmodified images; no competing image service).
- **Icons:** no brand icons are shipped. Mockup credits (Simple Icons CC0, Custom Brand Icons MIT) apply only to the mockups.
- **Code:** CleanFrame is MIT; only measurements and design ideas are used, no Tizen code.

## Bloatware cleanup (later, with approval)

Not started. When we get there:

1. `sh supports.sh <TV_IP>` then `sh candidates.sh <TV_IP>` — read-only.
2. Present every installed package with one of `never / keep / safe / review` and a plain-English sentence, plus the reason (persistent, Wi-Fi owner, HDMI, casting, etc.).
3. Ask before each change; use `pm disable-user --user 0`, never `pm uninstall` on system apps.
4. Keep `cleanup-undo-<date>.sh` with every package changed; test after each small batch and reboot.
5. Never-disable list from the TV Detox README: Play services/framework, Play Store, Settings, System UI, setup apps, keyboard, Bluetooth, HDMI/TV input and tuner framework, package installer, providers, anything `PERSISTENT`, and whatever saved the Wi-Fi. On Google TV, Google TV's home screen is handled separately (below).
6. Leave anything unknown on.

## Google TV home screen (item 3a–3c)

Do the measurement **before** choosing an approach:

- `dumpsys meminfo` free RAM and `com.google.android.apps.tv.launcherx` PSS/TOTAL while idle on Google TV home, then after opening this launcher once, then 60 seconds later (cached).
- `dumpsys activity processes` for its oom adj / cached state.
- Record boot RAM as a baseline, and repeat after a reboot.

Then present three options with those numbers and risks:

- **A. Leave it enabled, cached.** No boot risk. Android reclaims it under pressure. Likely recommendation on a 2 GB box unless it holds a lot while cached.
- **B. Force-stop after boot** (`adb shell am force-stop com.google.android.apps.tv.launcherx`). Frees it until something starts it again; low risk, but not permanent and needs adb after each boot.
- **C. Disable it** (`pm disable-user --user 0 …`), re-enable over adb only when needed. This is the option that has caused boot loops/factory resets on some Google TVs. Only with a tested recovery path and the owner's explicit OK.

Settings already has a **Google TV home** row that opens `com.google.android.apps.tv.launcherx/.home.HomeActivity` only if it resolves and is enabled; otherwise it says **Disabled** or **Not available**.

## Build tooling

Everything lives in `.tools/` and nothing was installed system-wide:

- Temurin JDK 17.0.21 (local)
- Android command-line tools 19.0 + platform-tools 37.0.1 (adb)
- `platforms;android-34`, `build-tools;34.0.0`
- Android emulator 37.2.13, `system-images;android-34;android-tv;arm64-v8a`, AVD `tv34` at 1920×1080
- Pillow in `.tools/venv` for asset generation

`.tools/` is ~11 GB because of the system image. Delete the folder to remove all of it. `. tools/env.sh` sets the paths. `sh build.sh` writes a signed 3.6 MB `out/tvhome.apk`; `-A assets` packages the wallpapers, dock/panel panes and Manrope. No Gradle, no new Java libraries.

## Recovery before anything risky

- Turn off **Settings → Accessibility → Home button** to restore Google TV's Home.
- Uninstall this launcher (`adb uninstall com.ansub.tvhome`) or run `sh undo.sh <TV_IP>`.
- Undo cleanup with `pm enable <package>` or the per-run undo script.
- If Home stops working: `adb shell cmd package set-home-activity com.google.android.apps.tv.launcherx/.home.HomeActivity` (or the setup app) and reboot.
- Wireless debugging off when finished; debugging left on lets other devices on the LAN ask to control the TV.

## Decisions

1. **Date:** a **Show date** setting, default off.
2. **Dock labels:** an **App labels** setting, default names.
3. **Photos:** six approved Unsplash photos at full quality, with credits.
4. **Repo:** public GitHub <https://github.com/raYhanryd/tv-detox-cleanframe>. Upstream remains read-only. The APK is built locally and is not committed.
5. **Emulator:** installed project-locally, used for verification, removable with `.tools/`.
6. **YouTube ads:** no blocker bundled; SmartTube documented as a separate optional install.
