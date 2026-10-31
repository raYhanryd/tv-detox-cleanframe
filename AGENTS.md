# AGENTS.md — read this first

This file is the handoff for any model, agent or session working in this repo. **Update it, [GUIDE.md](GUIDE.md) and [PROGRESS.md](PROGRESS.md) before you finish a work session.** If scope changes, also update [docs/restyle-plan.md](docs/restyle-plan.md).

## What this is

A native Android TV launcher, forked from [Ansub/tv-detox](https://github.com/Ansub/tv-detox) (MIT), restyled to look like [CleanFrame](https://github.com/nthnclrk/CleanFrame) (MIT, Samsung Tizen web app). CleanFrame is a *visual reference only*. Do not port its JavaScript, HTML, CSS or Tizen APIs. The look is rebuilt in plain Java.

Owner's TV: **ORCA 2K Google TV**, Android TV OS 11 (API 30), stock, 2 GB-class RAM. Computer: Apple Silicon Mac (M1), macOS, Java 25 installed system-wide; builds must use Java 17.

Remote: `https://github.com/raYhanryd/tv-detox-cleanframe` (public). Upstream remote is `origin` (Ansub/tv-detox). **Never push to `origin`.** The owner's remote is `mine`.

## Current phase (2026-10-31)

**Restyled launcher built, pre-install review fixes applied, and verified on an API 34 Android TV emulator. Not installed on the ORCA yet; no TV cleanup has been done.**

- The restyle is implemented: glass dock, six wallpapers, Settings panel and wallpaper picker, Show date and App labels toggles, Google TV home row.
- `out/tvhome.apk` is signed, 3.6 MB, package `com.ansub.tvhome` 1.5.7, minSdk 21, targetSdk 34. Verified with `apksigner`, `aapt2` and `zipalign`.
- **Home routing now supports all three stock launchers:** `com.google.android.apps.tv.launcherx` (Google TV), `com.google.android.tvlauncher` (Android TV 9–11) and `com.google.android.leanbacklauncher`. Confirmed on the emulator, whose stock home is `tvlauncher`: with the service off, Home opens `tvlauncher`; with it on, Home opens this launcher. Hold Back opens `tvlauncher` and stays there (no redirect loop).
- **The Settings row reads the real stock launcher** and showed *Enabled* and *Disabled* correctly when `tvlauncher` was enabled and temporarily disabled.
- **`install.sh` no longer downloads anything:** it fails if `out/tvhome.apk` is missing and refuses a build older than its source. It never disables a stock launcher unless `DISABLE_STOCK_HOME=1` (and on Google TV also `GOOGLE_TV=1`). Running it on the emulator left `pm list packages -d` empty.
- Emulator checks passed: home, D-pad focus, add/move/replace/remove, hold OK, Settings, both toggles, wallpaper picker, Inputs and Apps panels, Back, hold Back, Home routing. No crashes.
- Emulator-only numbers: **31.7 MB PSS**, **3.7% janky frames**, p50 21 ms / p90 24 ms / p99 38 ms with host GPU. These are not the TV's numbers.
- Next: connect to the TV over Wireless debugging, install, confirm Home, then measure **its** RAM/frames. Do not start cleanup until the owner approves each package.

## Hard rules

1. **Plain Java only.** No Gradle, no libraries, no WebView, no Kotlin, no AndroidX. The build is `build.sh` (aapt2 + javac + d8 + apksigner). Keep `minSdk 21`, `targetSdk 34`, `compileSdk 34`.
2. **Preserve** app launching, HDMI inputs, clock, Wi-Fi/network icon, add/move/remove/replace apps, long-press/OK/Back behaviour, and the `HomeButton` accessibility service. Tell the owner before changing any of it.
3. **Animations:** transform and opacity only. No layout/measure work during animation, no runtime blur, no `requestLayout` in listeners, hardware layer (`withLayer()`) while a tile moves. Do **not** change system animation scales unless the owner explicitly picks a value.
4. **Assets:** pre-render blur/glass on the Mac; the TV only decodes bitmaps. Bundle only fonts with a bundling licence (Manrope is OFL). Keep photo/icon credits and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) current.
5. **Cleanup:** never uninstall system apps. Use `pm disable-user --user 0`; ask before **every** package; keep an undo list. Respect the TV Detox never-disable list and the Google TV launcher caution. Disable nothing without the owner's explicit OK.
6. **Google TV home:** measure with `dumpsys meminfo` first; present options with real numbers; do not disable, force-stop or otherwise change it without approval.
7. **TV access:** only after the owner confirms. Wireless debugging pairing and install instructions are in [GUIDE.md](GUIDE.md). Nothing is connected now.
8. **Git:** do not push to upstream. Commit only files relevant to the current change; do not stage unrelated work. Pushing to `mine` is allowed because the owner asked for the repo to be kept on GitHub.
9. **Tooling:** everything installed for this project lives in `.tools/` (JDK, Android SDK, AVD, Python venv). Do not install system-wide Homebrew packages unless the owner asks. See [GUIDE.md](GUIDE.md#tools-and-deleting-them).

## Owner decisions (already made)

| Topic | Decision |
| --- | --- |
| Clock | **Setting for both:** a "Show date" toggle under the clock. Default: date off (CleanFrame look), user can turn it on. Implemented. |
| Dock labels | **Setting for both:** "App labels" On = icons + names, Off = icons only. Default On. Implemented. |
| Wallpapers | Use the six CleanFrame Unsplash photos at **full quality** (1920×1080 JPEGs as bundled), with credits. Implemented. |
| GitHub | Public repo `raYhanryd/tv-detox-cleanframe`; no APK or keystore is committed. |
| Emulator | Installed in `.tools/`; deleting that folder removes it. Used to verify the UI. |
| Date/clock format | Keep the existing 12/24 preference; do not force it. |
| YouTube remote button | Not required; do not spend effort preserving it. |
| YouTube ads | Do not bundle an ad blocker or unofficial YouTube app. The launcher only launches apps. SmartTube is an optional separate install (MIT, third-party). |

## Tooling layout (installed 2026-10-30/31)

Everything is project-local, git-ignored, and safe to delete with the folder. `.tools/` is **~11 GB** now, because the Android TV 14 ARM64 system image is large.

```
.tools/                  ~11 GB total
  jdk-17/                # Temurin JDK 17.0.21 (local, not Homebrew), ~310 MB
  android-sdk/           # SDK 19.0, platform-tools 37.0.1, platform 34,
                         # build-tools 34.0.0, emulator 37.2.13,
                         # system-images;android-34;android-tv;arm64-v8a, ~9.8 GB
  android-home/          # ANDROID_USER_HOME / adb keys where supported
  avd/tv34.avd           # Android TV AVD, 1920×1080, ~940 MB
  venv/                  # Python + Pillow for asset generation, ~22 MB
```

`. tools/env.sh` now puts `emulator` on `PATH` as well as `adb` and `java`.

Emulator reality on Apple Silicon: Android TV ARM64 images exist for **API 31, 33, 34, 36**, not API 30 (Android 11). API 34 is installed. `-gpu host` is required for meaningful frame numbers; `swiftshader_indirect` gave 100% janky on the same build.

## Build and check

```sh
. tools/env.sh
sh build.sh                  # writes out/tvhome.apk

# Headless emulator, after boot:
emulator -avd tv34 -no-window -no-audio -no-boot-anim -gpu host -no-snapshot-save
adb wait-for-device
adb install -r out/tvhome.apk
adb shell am start -n com.ansub.tvhome/.MainActivity
```

**Important:** start the emulator as a persistent background process, not inside a timed shell command. A `SYNC` command that times out kills its process group, emulator included. If it dies, relaunch; do not assume the AVD is broken.

Do not commit `out/`, `key.jks`, `.tools/`, `.android/`. `key.jks` is generated on the first build and must be kept for updates.

## Source map

| File | Role |
| --- | --- |
| `src/com/ansub/tvhome/MainActivity.java` | One screen (~1,800 lines): glass dock, clock, top controls, wallpaper, tiles, panels, inputs, network, menus. |
| `src/com/ansub/tvhome/HomeButton.java` | Opt-in accessibility service; redirects any of the three stock home screens to this launcher, debounced with crash/failure guards. Also answers which stock home exists for the Settings row. |
| `src/com/ansub/tvhome/LineIcon.java` | Vector-ish line icons from int op arrays; no image resources. |
| `src/com/ansub/tvhome/Strings.java` | 16-language labels and date patterns. |
| `build.sh` | Generates `Apps.java`, aapt2 compile/link, javac, d8, zipalign, apksigner. |
| `res/drawable-nodpi/` | Six `wallpaper_*.jpg`, six `dock_*.png`, six `panel_*.png`, `plate.png`. |
| `assets/fonts/` | Manrope variable font + OFL licence. |
| `tools/generate_assets.py` | Deterministic Pillow renderer for all wallpaper/glass bitmaps. |
| `tools/env.sh` | Sets Java 17, SDK, adb, emulator, AVD paths. |
| `docs/screenshots/` | Final emulator screenshots (`home.jpg`, `settings.jpg`, `wallpapers.jpg`). |
| `mockups/` | Design mockups + generator + credits (not shipped). |
| `docs/restyle-plan.md` | Mapping, performance budget, limits, open questions. |

## What was built

- **Geometry:** 1920×1080 design, scaled by `widthPixels / 1920f`. Dock glass 1504×232 at (208, 676); tiles 288×200, 296 pitch, tile radius 32, dock radius 48. CleanFrame's measured geometry.
- **Pre-rendered assets:** each wallpaper is a 1920×1080 JPEG with a top shade and bottom scrim. Per-wallpaper dock glass (blur 28, veil) and settings glass (blur 42) are PNGs at half-resolution and upscaled by the TV. `plate.png` is a white 24%-alpha rounded focus plate. No runtime blur.
- **Focus:** plate alpha 0→1 in 120 ms; icon/label `translationY(-3dp)` + `scale 1.04` in 180 ms with `withLayer()`. No layout during animation.
- **Dock:** `HorizontalScrollView` + `LinearLayout`; focus scrolls the row. Rebuilds clear the row with `dockRow.removeAllViews()` (a targeted removal once left a stale, focusable tile behind; do not regress this).
- **Settings:** Wallpaper, Apps on Home, Inputs, Show date, App labels, Google TV home (reads the stock launcher that actually exists: enabled/disabled/not available), Brightness (non-box TVs), TV settings. The two toggles update immediately and persist in `config` prefs.
- **Wallpaper picker:** six thumbnails + half-res preview; OK saves, Back keeps the current one.
- **Apps on Home:** the dock is the saved `apps` pref. A first launch with no saved value seeds from `apps.txt` (filtered to installed, launchable apps), then fills the row with other installed TV apps until there are six. Once anything is saved, the dock follows the saved list exactly. All installed apps remain available from the **Apps** top control.
- **Font:** Manrope variable from `assets/fonts` (OFL); falls back to the TV's sans-serif.

## Verification (2026-10-31)

Run on Android TV 14 API 34 emulator, 1920×1080, `-gpu host`, release APK:

- `apksigner verify` OK; package `com.ansub.tvhome`, versionCode 20, 1.5.7, minSdk 21, targetSdk 34; APK 3.6 MB.
- D-pad: left/right focus, up to Inputs/Apps/Settings/network, down back to dock, OK, hold OK, Back.
- **Home routing with `com.google.android.tvlauncher`:** service off → Home stays on `tvlauncher/.MainActivity`; service on → Home opens `com.ansub.tvhome/.MainActivity`. **Hold Back** → `tvlauncher` opens and stays there after 6 s (the “stay on the stock home” flag works).
- **Settings → Google TV home:** showed *Enabled* with `tvlauncher` on, *Disabled* with it temporarily disabled, then *Enabled* again after `pm enable`. (The *Not available* branch is code-only; it needs a TV with none of the three packages.)
- **`install.sh`:** missing APK → exit 1 with a build instruction (no download); source newer than APK → exit 1 (`ALLOW_STALE=1` overrides). Normal run → exit 0, `pm list packages -d` empty before and after, HOME role set to `com.ansub.tvhome`, Home opens it.
- **`undo.sh` with nothing disabled:** exit 0, app removed, Home back on `tvlauncher`, accessibility setting cleared by the system.
- Add (initially empty dock), move (Cast from third to second), replace (YouTube → Google Play Store), remove (Google Play Store gone, only Add left), re-add; no stale tiles after rebuild.
- Settings: both toggles, wallpaper change (Misty, Forest, Alpine), wallpaper picker, Inputs panel, Apps panel, Back closes panels.
- Memory: **31.7 MB PSS / 145.9 MB RSS** with wallpaper + dock + Manrope loaded.
- Frames after 16 focus moves + up/down/back: **54 frames, 2 janky (3.7%)**, p50 21 ms, p90 24 ms, p99 38 ms, 0 missed vsync, 0 slow UI thread.
- Not verified: the ORCA's real GPU frame times, real HDMI inputs, the `launcherx`/`leanbacklauncher` branches, Android 11 accessibility/Home-role behaviour, 12/24 clock preference, reboot behavior. Those need the TV (or an API 30 image, which does not exist for ARM64).

## Gotchas

- The emulator's YouTube stub opens a "YouTube is not supported on this device" page. That is the emulator, not the launcher.
- Emulator `dumpsys gfxinfo` with software GPU is meaningless (100% jank). Always use `-gpu host` for comparisons and still treat it as a smoke test, not TV performance.
- Clearing the `apps` pref to an empty string intentionally leaves an empty dock (plus Add). It does **not** reseed from `apps.txt`; only a missing pref (`null`) does.
- **`install.sh` never disables a stock launcher by default.** `DISABLE_STOCK_HOME=1` offers it; a Google TV also needs `GOOGLE_TV=1`. Do not use those switches without a tested recovery path. Home routing is done by the **Home button** accessibility service (and the HOME role, which the script sets).
- `install.sh` installs **only** `out/tvhome.apk`; there is no release download. It refuses a build older than `src/`, `res/`, `assets/`, `AndroidManifest.xml` or `build.sh` unless `ALLOW_STALE=1`.
- On Android 14 the HOME role decides what Home opens, while `cmd package resolve-activity -c android.intent.category.HOME` can still name a higher-priority stock launcher. `install.sh` therefore treats `cmd role get-role-holders android.app.role.HOME` = `com.ansub.tvhome` as success; do not “fix” that back to resolve-activity alone.
- The accessibility service watches only each stock package's own HOME activity, so Google TV's Apps/Settings pages are not redirected. Do not loosen that to “any activity in the package”, or hold Back will bounce back.
- `launcherx` and `leanbacklauncher` are covered by code and manifest queries but cannot be exercised on the installed API 34 image (it only ships `tvlauncher`).
- On Android 11+, sideloaded apps may need **App info → ⋮ → Allow restricted settings** before the accessibility toggle can be turned on.
- The TV cleanup is not automated here and is not approved. Do not run `pm disable-user` on the TV.

## Next steps

1. Owner connects the TV (Wireless debugging pairing + `adb connect`); install with `sh install.sh <IP> "<chosen apps>"`.
2. Enable **Home button** in Accessibility; verify Home, hold Back to Google TV home, app launch, HDMI tiles, network icon, clock, 12/24.
3. Measure `dumpsys meminfo` and `dumpsys gfxinfo` on the TV; show free RAM before/after.
4. Measure Google TV launcher idle cost; present the three options (leave cached / force-stop after boot / disable with recovery) and wait for the owner.
5. Cleanup one package at a time with approval and an undo file.
6. Reboot once, confirm boot + Home, remind the owner to turn debugging off.

## When you finish a session

1. Update **PROGRESS.md** (what changed, what is verified, what is next).
2. Update **AGENTS.md** (state, decisions, new gotchas).
3. Update **GUIDE.md** (commands, setup, recovery if changed).
4. Keep **THIRD_PARTY_NOTICES.md** current when assets change.
5. Commit and push to `mine` only. Do not touch `origin`.
