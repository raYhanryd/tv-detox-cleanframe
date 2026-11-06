# PROGRESS.md

**Last updated:** 2026-11-06
**Phase:** 1.5.9 built and emulator-verified (Prime arrow, AirScreen/Play Store marks, focus tick, full-resolution glass); **1.5.7 still installed on the ORCA; 1.5.9 pending because the TV is offline**
**TV:** 1.5.7 installed; Home verified; 1.5.9 not installed; no packages disabled

## Status

| Area | State |
| --- | --- |
| Both repos read | Done |
| Plan and mapping | Done — [docs/restyle-plan.md](docs/restyle-plan.md) |
| Mockups | Done — [mockups/](mockups/) |
| Restyled UI | **Done** — dock, clock, controls, settings, wallpaper picker, toggles |
| Pre-rendered assets | **Done** — six wallpapers, six dock panes, six settings panes, focus plate |
| Build | **Verified** — signed 6,446,299-byte APK, package 1.5.9 (22), minSdk 21 / targetSdk 34; Prime arrow, AirScreen/Play Store marks, focus tick, full-res glass, 1920×1080 wallpapers |
| Emulator | Installed in `.tools/`; API 34 Android TV, 1920×1080 |
| UI tests | **1.5.9 emulator passed**: Prime smile + arrow, AirScreen/Play Store marks, focus sound wired with no audio errors, full-res Settings; 1.5.7/1.5.8 interaction checks stand |
| Pre-install review | **Done** — 10 findings fixed; Home routing now covers `launcherx`, `tvlauncher`, `leanbacklauncher` |
| `install.sh` safety | **Verified** — never downloads, refuses a stale build, disables nothing by default |
| Memory / frames | **1.5.9 emulator**: 41.3 MB PSS; 12 frames, 2 janky (16.67%); p50 21 / p90 26 / p95 32 / p99 32 ms. Small sample; 1.5.7 baseline 31.7 MB / 3.7% |
| TV install | **1.5.7 installed**; Home verified; 1.5.9 pending TV reconnect (offline 2026-11-06) |
| TV Home button | **Enabled on 1.5.7 and verified**; re-check after 1.5.8 |
| TV cleanup | Not started; every package needs approval |
| Google TV home decision | Not started; measure on the TV first |
| GitHub | Committed and pushed to `mine` |

## What changed

### 1.5.9 (2026-11-06)

- Fixed the Prime Video mark. The historical Wikimedia SVG has the smile and arrow head as separate paths; 1.5.8 used only the smile, so the mark looked arrow-less. Added the `M580.4,148.4…` arrow path and widened the crop to 448×99.5; the mark now renders at 150×88.
- Added white marks for AirScreen and Google Play Store. AirScreen is a white transparent PNG (512×322, displayed 100×63) traced from the official Play Store icon; Play Store is the Simple Icons CC0 `googleplay` path (88×88).
- Added `res/raw/hover.wav` (75 ms, 44.1 kHz mono) and a `SoundPool` focus tick at 0.30 volume, silent for the first 450 ms after `onResume` and released in `onDestroy`.
- Re-rendered dock and settings glass at the full 1504×232 / 1504×888 design size with a 4× anti-aliased rounded mask; the focus plate stays 2× (576×400); the dock label shadow is 1 px.
- Re-encoded all six wallpapers at JPEG quality 95 with 4:4:4 chroma (from 91) so photo edges stay clean on a 1080p panel. All shipped raster assets are now 1920×1080 or the native 1504×232 / 1504×888 / 576×400 glass sizes; all marks are vectors except the 512×322 AirScreen PNG, and the launcher icon/banner are vectors. Removed macOS `.DS_Store` files from `res/` and the tree.
- Version 1.5.9 (22); APK **6,446,299 bytes**; SHA-256 `7dc54c3b231df1fdf77773b242ddb2235bb280fb4b685a10b52ff21986c97186`.
- Emulator: Prime arrow, AirScreen/Play Store, Settings; no crashes; **34,411 KB PSS / 149,904 KB RSS** after the wallpaper re-encode (the earlier four-app test was 41,345 KB); 12-frame sample after 10 focus moves, **2 janky (16.67%)**, p50 21 / p90 26 / p95 32 / p99 32 ms; 0 missed vsync, 0 slow UI thread. The frames were not re-run after the JPEG change. Sound loaded with no audio/logcat errors, but the emulator was `-no-audio`, so it was not heard. `docs/screenshots/home-hd.png` is the 1920×1080 capture.
- Temporary Prime and AirScreen test packages were uninstalled and the saved list reset to `com.google.android.youtube.tv`; the TV was still unreachable (`No route to host`).

### 1.5.8 (2026-11-05)

- Added seven white vector dock marks: Netflix, YouTube, Spotify, Prime Video, Stremio, Apple TV and YouTube Music. `brandLogo()` maps the package; known packages keep their own proportions and skip the bitmap crop; other apps keep their installed icon. The Prime Video mark is cropped from the public-domain Wikimedia `Amazon Prime Video logo.svg`; the rest are Simple Icons CC0. Notices updated.
- Inputs, Apps and Settings are icon-only. The network icon and optional quick shortcuts are unchanged; dock labels remain and follow the App labels setting.
- Version 1.5.8 (21). No change to `HomeButton.java`, its XML, or the install/undo scripts.
- Emulator verification: five-logo dock, icon-only controls, Settings via Add → Up (Inputs) → Right (Apps) → Right (Settings) → OK, Home with the service on. The temporary test packages were removed and the saved list reset to `com.google.android.youtube.tv`. The TV was offline, so 1.5.8 is not installed there.

### UI (`src/com/ansub/tvhome/MainActivity.java`)

- Replaced the gradient background with six full-quality photo wallpapers and per-wallpaper pre-rendered glass: a 1504×232 dock pane at (208, 676), a settings pane, and a subtle white focus plate.
- Dock tiles are 288×200 at a 296 pitch with 32 px corners; the dock pane is 48 px.
- Clock moved to the top left, with the date underneath when **Show date** is on.
- Top-right controls: Inputs, Apps and Settings are **icon-only**; optional quick shortcuts keep their labels; the network icon is unchanged.
- Focus is opacity and transform only: plate fades in over 120 ms; icon/name lifts 3 dp and scales 1.04 over 180 ms with `withLayer()`. A bundled 75 ms `SoundPool` tick plays on dock focus, skipping the first 450 ms after `onResume`.
- Settings is a glass panel with Wallpaper, Apps on Home, Inputs, Show date, App labels, Google TV home, Brightness (non-box TVs) and TV settings.
- Wallpaper picker: six thumbnails, 960×540 preview (more than the 640×360 view), OK saves, Back leaves the current wallpaper.
- **Fixed during testing:** a rebuild could leave a removed app's tile in the dock because only tracked views were removed. `buildTiles()` now clears the dock row itself (`dockRow.removeAllViews()`), so a removed tile cannot remain focusable or launchable. Confirmed by removing YouTube and by removing the last app.
- Preserved app launching, HDMI input list and menus, add/move/replace/remove, hold OK, Back, network icon, clock and the `HomeButton` service.

### Pre-install review fixes (2026-10-31)

- **All three stock home screens:** `HomeButton` now resolves each package's own HOME activity instead of hard-coding Google TV's `HomeActivity`. `res/xml/home_button.xml` and the manifest `<queries>` list `launcherx`, `tvlauncher` and `leanbacklauncher`. Hold Back and the Settings row use the same helper, so they open whichever stock launcher the TV actually has.
- **Settings row accuracy:** it now reports *Enabled* / *Disabled* / *Not available* from `HomeButton.stockHomeState()` instead of assuming `launcherx`.
- **`install.sh` can never install the wrong app:** the upstream release download is gone; a missing `out/tvhome.apk` fails with build instructions. A build older than `src/`, `res/`, `assets/`, `AndroidManifest.xml` or `build.sh` is refused (`ALLOW_STALE=1` overrides).
- **Stock launcher stays on:** disabling a stock home is now opt-in (`DISABLE_STOCK_HOME=1`, plus `GOOGLE_TV=1` on Google TV) rather than offered by default. `YES=1` alone no longer turns anything off.
- **Home check:** accepts the Android 10+ HOME role as proof (on Android 14 the role wins while `resolve-activity` still names `tvlauncher`), and waits up to 12 s for a cold start. This removed a false “Home still opens the TV's own” message.
- **Key/menu hardening:** a new Back press clears a stale `backHeld`; `dropdown()` returns instead of dereferencing a missing tile; replace only writes at an index that still exists; finishing a move no longer dereferences a vanished tile.
- **Docs:** repo is public (not private); README says the APK is built locally; GUIDE covers all stock launchers, the stale-build guard and per-launcher recovery.

### Assets and build

- `tools/generate_assets.py` renders all shipping bitmaps with Pillow: six 1920×1080 JPEG wallpapers (quality 95, 4:4:4) with top shade and bottom scrim, six full-size dock panes (1504×232), six full-size settings panes (1504×888) and a 2× `plate.png` (576×400), all with a 4× anti-aliased rounded mask. No runtime blur.
- Bundled Manrope variable font (OFL) and its licence under `assets/fonts/`.
- Added [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- `tools/env.sh` now puts the emulator on `PATH`.
- APK grew from 54 KB (stock) to **6.4 MB** (6,446,299 bytes at 1.5.9), almost entirely the six full-quality photos and pre-rendered panes. The 1.5.9 wallpaper re-encode (95/4:4:4) accounts for the jump from 4.68 MB.

### Docs

- [AGENTS.md](AGENTS.md) updated with the implemented state, exact geometry, tooling sizes, gotchas and TV next steps.
- [GUIDE.md](GUIDE.md) rewritten for install, app selection, Home button, recovery, the emulator and the YouTube ad situation.
- [README.md](README.md) fork note updated for 1.5.8; final emulator screenshots added under [docs/screenshots/](docs/screenshots/).
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) updated for the Simple Icons marks and the Wikimedia Prime Video crop.
- [docs/restyle-plan.md](docs/restyle-plan.md) updated to mark what is implemented and what is not.

## Verification (2026-11-06)

### 1.5.9 emulator (2026-11-06)

Environment: Android TV 14 API 34 emulator, 1920×1080, host GPU.

- `aapt2 dump badging`: `com.ansub.tvhome` 1.5.9 (22), minSdk 21, targetSdk 34; APK **6,446,299 bytes**; SHA-256 `7dc54c3b231df1fdf77773b242ddb2235bb280fb4b685a10b52ff21986c97186`; `apksigner verify` and `zipalign` OK.
- Prime Video showed the smile **and arrow head**; AirScreen, Google Play Store and YouTube showed their marks. `docs/screenshots/home.jpg`.
- Settings opened via Add app → Up (Inputs) → Right (Apps) → Right (Settings) → OK; the full-resolution panel is `docs/screenshots/settings.jpg`.
- The Prime and AirScreen packages were temporary stubs using the real names; both were removed and the saved list reset to `com.google.android.youtube.tv`. The Play Store is the emulator's real package.
- Focus sound: SoundPool loaded without logcat errors; `-no-audio` means audibility is unverified.
- Memory: 34,411 KB PSS / 149,904 KB RSS after the wallpaper re-encode (41,345 KB PSS in the earlier four-app run). Frames: 12 total, 2 janky (16.67%), p50 21 ms, p90 26 ms, p95 32 ms, p99 32 ms; 0 missed vsync, 0 slow UI thread. Small sample; not TV performance.
- Full-HD check: the new `docs/screenshots/home-hd.png` is a native **1920×1080** emulator capture; all wallpapers are 1920×1080 and all glass assets are at their design size. The ORCA still runs a 1280×720 logical UI; `adb shell wm size 1920x1080` is documented in GUIDE.md, with `wm size reset` to undo.
- No crashes. Not verified: TV, real HDMI, real GPU frames, 12/24, reboot, audible sound.

### 1.5.8 emulator (2026-11-05)

Environment: Android TV 14 API 34 emulator, 1920×1080, host GPU.

- `aapt2 dump badging`: `com.ansub.tvhome` 1.5.8 (21), minSdk 21, targetSdk 34; APK 3,779,577 bytes; SHA-256 `99ae738a1c61a88e3ef79b2def659e50e0ebc28f35533bdf5d39615919b5dbf7`; `apksigner verify` OK.
- Dock: Netflix, YouTube, Spotify, Prime Video and Stremio rendered with the white marks, in the owner's order, with labels. The emulator has only the YouTube stub, so the other four were temporary packages with the real package names; all four were uninstalled and the saved list reset to `com.google.android.youtube.tv`. The screenshot is `docs/screenshots/home.jpg`.
- Top controls: Inputs/Apps/Settings icon-only; the Settings panel opened via Add app → Up (Inputs) → Right (Apps) → Right (Settings) → OK. Left from Inputs returns to the dock; that is the focus graph, not a broken control.
- Home: with the Home button service enabled/bound, Home returned to `com.ansub.tvhome/.MainActivity`; with the service off, Home stayed on `tvlauncher`. The service was re-enabled after a test cleanup; no launcher code writes the accessibility setting.
- No crashes. Not verified for 1.5.8: the TV (offline), real HDMI, real GPU frames, 12/24, reboot.
- **TV 1.5.7:** installed on the ORCA 2K Google TV (Android 11, 1280×720, stock `launcherx`); Home verified with the service. Its Android 11 build lacks `cmd role get-role-holders`, so the install script's role check is inconclusive; ignore the warning. Hold Back, Settings row, HDMI, clock/date, wallpaper, app labels and reboot remain unverified on the TV. The TV was offline on 2026-11-05.

### 1.5.7 emulator (2026-10-31)

Environment: Android TV 14 API 34 emulator, 1920×1080, host GPU, release APK installed with `adb install -r`.

- `sh build.sh` exit 0; `apksigner verify` OK; `aapt2 dump badging` reports `com.ansub.tvhome` 1.5.7 (20), minSdk 21, targetSdk 34, leanback launchable activity.
- D-pad: left/right across the dock, up to the top controls, down back to the dock, OK, hold OK, Back.
- **Stock launcher `tvlauncher` (the emulator's own):** Home with the service off stayed on `com.google.android.tvlauncher/.MainActivity`; with the service on, Home opened `com.ansub.tvhome/.MainActivity`. Hold Back opened `tvlauncher` and it was still there 6 s later.
- **Settings row:** *Enabled* with `tvlauncher` on; *Disabled* after `pm disable-user --user 0 com.google.android.tvlauncher`; *Enabled* again after `pm enable`. The stock launcher was restored immediately.
- **Safety scripts:** missing APK → exit 1 with build instructions; stale APK → exit 1; normal `install.sh` → exit 0 with `pm list packages -d` empty; `undo.sh` with nothing disabled → exit 0, app removed, Home back on `tvlauncher`.
- Add: started with an empty dock, added YouTube, Google Play Store and Cast.
- Move: Cast moved from third to second; focus stayed on the moving tile; saved on OK.
- Replace: YouTube replaced by Google Play Store.
- Remove: Google Play Store removed; then the last app removed, leaving only **Add app** with no ghost tile.
- Settings: opened, both toggles changed and persisted, wallpaper changed (Alpine, Forest, Misty), picker previews shown, Back closed panels.
- Apps panel listed all three installed apps; Inputs panel showed "No HDMI inputs" on the emulator without crashing.
- Memory: **31.7 MB PSS**, **145.9 MB RSS**, Java heap ~1.8 MB, native ~21.9 MB, no swap.
- Frames after 16 focus moves plus up/down/back: **54 total, 2 janky (3.7%)**, p50 **21 ms**, p90 **24 ms**, p99 **38 ms**, 0 missed vsync, 0 slow UI thread.
- Software-GPU run for comparison: 100% janky, p50 113 ms; the emulator's software renderer, not the launcher, dominates that result.

**Not verified at 1.5.7:** the ORCA's real GPU frame times, real HDMI inputs, 12/24 clock preference, reboot, free RAM before/after. The `launcherx` Home route and Android 11 accessibility were later verified on the ORCA; `leanbacklauncher` remains code-only. These require the TV (or an API 30 image, which does not exist for ARM64).

## Decisions

1. Clock date: setting; default off.
2. Dock labels: setting; default names.
3. Wallpapers: six CleanFrame Unsplash photos, full quality, credited.
4. Emulator: kept inside `.tools/`, deletable with that folder.
5. Date/clock format: follow the TV's existing 12/24 preference.
6. YouTube remote button: not required.
7. YouTube ads: no ad blocker bundled. The official app cannot be ad-blocked by the launcher; SmartTube is a separate optional install, **not installed on 2026-11-05 because the TV was offline**. Do not patch the official APK.
8. Dock icons: white monochrome marks for known packages, like CleanFrame; unknown apps keep their own icon. Implemented in 1.5.8; extended to AirScreen and Play Store and fixed the Prime arrow in 1.5.9. Inputs/Apps/Settings are icon-only; the network icon stays.
9. Dock sound: a short, soft tick when focus moves between home tiles; silent on the first focus after launch. Implemented in 1.5.9.

## Next steps (in order)

1. Reconnect the ORCA (`adb connect 192.168.8.187:5555`); confirm the five packages; install 1.5.9 with `sh install.sh 192.168.8.187:5555 "com.netflix.ninja,com.google.android.youtube.tv,com.spotify.tv.android,com.amazon.amazonvideo.livingroom,com.stremio.one"`.
2. Confirm the Prime arrow, AirScreen/Play Store marks, dock focus sound, full-res glass, Home (service on), hold Back, Settings → Google TV home, HDMI, clock/date, wallpaper, App labels. Note the role-query warning; the service is the route.
3. Measure `dumpsys meminfo` and `dumpsys gfxinfo` on the TV; show free RAM before/after.
4. Decide on SmartTube separately if the owner still wants ad-free YouTube; do not bundle or patch the official app.
5. Measure `com.google.android.apps.tv.launcherx` idle cost; present leave-cached / force-stop / disable options with real numbers and wait.
6. Run `candidates.sh`; clean up one approved package at a time with an undo list.
7. Reboot once; verify boot and Home; remind the owner to turn debugging off.

## Log

- **2026-10-30** — Discovery, plan, mockups, local toolchain, baseline build, private GitHub repo.
- **2026-10-30/31** — Installed Android TV 14 ARM64 emulator (~10 GB total under `.tools/`); built the restyle; fixed hold-OK menu timing and move/reorder focus.
- **2026-10-31** — Fixed the stale-dock-tile bug, verified add/move/replace/remove, settings toggles, wallpaper picker and panels; measured memory/frames; wrote notices and updated handoff docs.
- **2026-10-31** — Pre-install review: found and fixed all-stock-launcher support, the Settings row, the upstream-APK download, default stock-launcher disabling, stale `backHeld`, and two stale-menu crashes. Rebuilt and re-verified on the emulator; no package was disabled on the TV (none is connected).
- **2026-11-05** — Added seven white vector dock marks and icon-only Inputs/Apps/Settings; bumped to 1.5.8 (21); verified on the emulator; updated screenshots and notices. The ORCA was offline (`No route to host`), so 1.5.8 is not installed; 1.5.7 remains with Home verified. YouTube ad-blocking inside the official app is not possible; SmartTube remains separate.
- **2026-11-06** — 1.5.9: restored the Prime arrow head, added AirScreen and Play Store marks, added the dock focus tick, and re-rendered the glass at full design resolution with anti-aliased corners. Verified on the emulator; TV still offline. 41.3 MB PSS; 12-frame smoke test 2 janky; sound asset loads but was not heard (`-no-audio`).

## Open risks

- Emulator is not the TV: real GPU frame times and RAM must be measured on the ORCA 2K.
- The pre-rendered glass is per wallpaper; changing the source photos requires rerunning `tools/generate_assets.py` and rebuilding.
- The dock starts with a top-up of other installed TV apps on a truly fresh install. Remove or pass an explicit app list if that is unwanted.
- Google TV's home screen must stay enabled until the owner chooses otherwise after real measurements.
- The bundled photos raise the APK to 3.6 MB and one decoded wallpaper adds ~8 MB while it is the background; measured total PSS is 31.7 MB on the emulator. At 1920×1080 that is one screenful; on a 1280×720 TV the wallpaper is still decoded at 1920×1080 (~8.3 MB). Downsampling was evaluated but not changed: it would alter the background path on the one screen size the owner has, and the TV's RAM must be measured first.
- The ORCA's stock launcher is `launcherx`; 1.5.7 Home was verified with the accessibility service. Its Android 11 lacks `cmd role get-role-holders`, so `install.sh`'s role check is inconclusive. 1.5.8 is not installed; the TV was offline on 2026-11-05.
- The 1.5.9 screenshot used temporary Prime and AirScreen packages on the emulator; the real TV's five apps still need a visual check after 1.5.9 is installed. The sound has not been heard on hardware.
- Full-resolution glass raises decoded memory: 41.3 MB PSS on the emulator vs 31.7 MB at 1.5.7. The ORCA has 2 GB-class RAM; measure it there before adding more full-size layers.
- 1.5.9's 12-frame sample is too small to compare with the 54-frame 1.5.7 result; re-run a longer focus test on the TV.
- The icon-only top controls changed the focus graph: the tested path is Add app → Up (Inputs) → Right (Apps) → Right (Settings); Up from a middle dock tile may stay in the dock.
- Only the seven packages in `brandLogo` get white marks; other dock apps keep their color icons.
- `cmd role get-role-holders` is unsupported on the ORCA's Android 11; the accessibility service is the Home route, and the fallback warning is expected.
