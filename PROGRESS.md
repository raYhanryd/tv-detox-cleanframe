# PROGRESS.md

**Last updated:** 2026-10-31
**Phase:** restyle implemented; emulator-verified; **ready to install on the TV**, not yet installed
**TV:** not connected, nothing installed, no packages disabled

## Status

| Area | State |
| --- | --- |
| Both repos read | Done |
| Plan and mapping | Done — [docs/restyle-plan.md](docs/restyle-plan.md) |
| Mockups | Done — [mockups/](mockups/) |
| Restyled UI | **Done** — dock, clock, controls, settings, wallpaper picker, toggles |
| Pre-rendered assets | **Done** — six wallpapers, six dock panes, six settings panes, focus plate |
| Build | **Verified** — signed 3.6 MB APK, package 1.5.7, minSdk 21 / targetSdk 34 |
| Emulator | Installed in `.tools/`; API 34 Android TV, 1920×1080 |
| UI tests | **Passed** on emulator: focus, add/move/replace/remove, hold OK, Settings, toggles, wallpaper, Inputs, Apps, Back |
| Pre-install review | **Done** — 10 findings fixed; Home routing now covers `launcherx`, `tvlauncher`, `leanbacklauncher` |
| `install.sh` safety | **Verified** — never downloads, refuses a stale build, disables nothing by default |
| Memory / frames | **Measured on emulator**: 31.7 MB PSS; 3.7% janky; p50 21 / p90 24 / p99 38 ms |
| TV install | Not started — waiting for the TV connection |
| TV Home button | Not enabled yet |
| TV cleanup | Not started; every package needs approval |
| Google TV home decision | Not started; measure on the TV first |
| GitHub | Committed and pushed to `mine` |

## What changed

### UI (`src/com/ansub/tvhome/MainActivity.java`)

- Replaced the gradient background with six full-quality photo wallpapers and per-wallpaper pre-rendered glass: a 1504×232 dock pane at (208, 676), a settings pane, and a subtle white focus plate.
- Dock tiles are 288×200 at a 296 pitch with 32 px corners; the dock pane is 48 px.
- Clock moved to the top left, with the date underneath when **Show date** is on.
- Top-right controls: Inputs, Apps, Settings, optional quick shortcuts, network icon.
- Focus is opacity and transform only: plate fades in over 120 ms; icon/name lifts 3 dp and scales 1.04 over 180 ms with `withLayer()`.
- Settings is a glass panel with Wallpaper, Apps on Home, Inputs, Show date, App labels, Google TV home, Brightness (non-box TVs) and TV settings.
- Wallpaper picker: six thumbnails, half-res preview, OK saves, Back leaves the current wallpaper.
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

- `tools/generate_assets.py` renders all shipping bitmaps with Pillow: six 1920×1080 JPEG wallpapers with top shade and bottom scrim, six dock panes, six settings panes and `plate.png`. No runtime blur.
- Bundled Manrope variable font (OFL) and its licence under `assets/fonts/`.
- Added [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- `tools/env.sh` now puts the emulator on `PATH`.
- APK grew from 54 KB (stock) to **3.6 MB**, almost entirely the six full-quality photos and pre-rendered panes.

### Docs

- [AGENTS.md](AGENTS.md) updated with the implemented state, exact geometry, tooling sizes, gotchas and TV next steps.
- [GUIDE.md](GUIDE.md) rewritten for install, app selection, Home button, recovery, the emulator and the YouTube ad situation.
- [README.md](README.md) fork note updated; final emulator screenshots added under [docs/screenshots/](docs/screenshots/).
- [docs/restyle-plan.md](docs/restyle-plan.md) updated to mark what is implemented and what is not.

## Verification (2026-10-31)

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

**Not verified yet:** the ORCA's real GPU frame times, real HDMI inputs, the `launcherx` and `leanbacklauncher` branches, Android 11 Home-role/accessibility behaviour, 12/24 clock preference, reboot, free RAM before/after. These require the TV (or an API 30 image, which does not exist for ARM64).

## Decisions

1. Clock date: setting; default off.
2. Dock labels: setting; default names.
3. Wallpapers: six CleanFrame Unsplash photos, full quality, credited.
4. Emulator: kept inside `.tools/`, deletable with that folder.
5. Date/clock format: follow the TV's existing 12/24 preference.
6. YouTube remote button: not required.
7. YouTube ads: no ad blocker bundled. The launcher cannot remove ads from the official app; SmartTube is documented as an optional separate install.

## Next steps (in order)

1. Owner connects the TV over Wireless debugging; run `sh install.sh <IP> "<chosen apps>"`.
2. Enable **Home button** in Accessibility; verify Home, hold Back, app launch, HDMI tiles, network icon, clock 12/24.
3. Measure `dumpsys meminfo` and `dumpsys gfxinfo` on the TV; show free RAM before/after.
4. Measure `com.google.android.apps.tv.launcherx` idle cost; present leave-cached / force-stop / disable options with real numbers and wait.
5. Run `candidates.sh`; clean up one approved package at a time with an undo list.
6. Reboot once; verify boot and Home; remind the owner to turn debugging off.

## Log

- **2026-10-30** — Discovery, plan, mockups, local toolchain, baseline build, private GitHub repo.
- **2026-10-30/31** — Installed Android TV 14 ARM64 emulator (~10 GB total under `.tools/`); built the restyle; fixed hold-OK menu timing and move/reorder focus.
- **2026-10-31** — Fixed the stale-dock-tile bug, verified add/move/replace/remove, settings toggles, wallpaper picker and panels; measured memory/frames; wrote notices and updated handoff docs.
- **2026-10-31** — Pre-install review: found and fixed all-stock-launcher support, the Settings row, the upstream-APK download, default stock-launcher disabling, stale `backHeld`, and two stale-menu crashes. Rebuilt and re-verified on the emulator; no package was disabled on the TV (none is connected).

## Open risks

- Emulator is not the TV: real GPU frame times and RAM must be measured on the ORCA 2K.
- The pre-rendered glass is per wallpaper; changing the source photos requires rerunning `tools/generate_assets.py` and rebuilding.
- The dock starts with a top-up of other installed TV apps on a truly fresh install. Remove or pass an explicit app list if that is unwanted.
- Google TV's home screen must stay enabled until the owner chooses otherwise after real measurements.
- The bundled photos raise the APK to 3.6 MB and one decoded wallpaper adds ~8 MB while it is the background; measured total PSS is 31.7 MB on the emulator. At 1920×1080 that is one screenful; on a 1280×720 TV the wallpaper is still decoded at 1920×1080 (~8.3 MB). Downsampling was evaluated but not changed: it would alter the background path on the one screen size the owner has, and the TV's RAM must be measured first.
- The ORCA's stock launcher package is unknown until adb is connected. The code covers all three known packages; the TV decides which branch runs.
