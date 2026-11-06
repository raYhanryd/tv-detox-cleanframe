# AGENTS.md — read this first

This file is the handoff for any model, agent or session working in this repo. **Update it, [GUIDE.md](GUIDE.md) and [PROGRESS.md](PROGRESS.md) before you finish a work session.** If scope changes, also update [docs/restyle-plan.md](docs/restyle-plan.md).

## What this is

A native Android TV launcher, forked from [Ansub/tv-detox](https://github.com/Ansub/tv-detox) (MIT), restyled to look like [CleanFrame](https://github.com/nthnclrk/CleanFrame) (MIT, Samsung Tizen web app). CleanFrame is a *visual reference only*. Do not port its JavaScript, HTML, CSS or Tizen APIs. The look is rebuilt in plain Java.

Owner's TV: **ORCA 2K Google TV**, Android TV OS 11 (API 30), stock, 2 GB-class RAM. Computer: Apple Silicon Mac (M1), macOS, Java 25 installed system-wide; builds must use Java 17.

Remote: `https://github.com/raYhanryd/tv-detox-cleanframe` (public). Upstream remote is `origin` (Ansub/tv-detox). **Never push to `origin`.** The owner's remote is `mine`.

## Current phase (2026-11-06)

**1.5.9 fixes the missing Prime Video arrow, adds AirScreen and Google Play Store white marks, a soft dock focus tick, and full-resolution anti-aliased dock/settings glass. It is emulator-verified. The ORCA still has 1.5.7 with Home routed; 1.5.9 is not installed because the TV is still offline. No TV cleanup has been done.**

- **TV state:** the ORCA (Google TV, Android 11, 1280×720) has 1.5.7 installed. Its stock launcher is `com.google.android.apps.tv.launcherx`. The Home button accessibility service was enabled and Home returned to `com.ansub.tvhome`. **The TV's Android 11 build does not support `cmd role get-role-holders`**, so `install.sh` cannot verify the HOME role there; the accessibility service is the working route.
- **TV connection:** last seen at `192.168.8.187:5555`. On 2026-11-06 `adb connect` still returned `No route to host`; `adb devices` listed only `emulator-5554`. Reconnect before installing 1.5.9.
- The restyle is implemented: glass dock, six wallpapers, Settings panel and wallpaper picker, Show date and App labels toggles, Google TV home row.
- **1.5.9 dock:** nine white marks. Prime Video now includes the source's separate arrow-head path; 1.5.8 used only the smile path. AirScreen (`com.ionitech.airscreen`) is a white transparent 512×322 PNG traced from the official Play Store icon; Google Play Store (`com.android.vending`) uses the Simple Icons CC0 `googleplay` path. `brandLogo()` supplies each mark's design size; the tile keeps its proportions (no bitmap crop). Other packages keep their own icon. The Prime shape is from the public-domain Wikimedia `Amazon Prime Video logo.svg` (trademark Amazon).
- **1.5.9 focus sound:** `res/raw/hover.wav` (75 ms, 44.1 kHz mono) plays through `SoundPool` on dock focus at 0.30 volume. It is silent for the first 450 ms after `onResume` so launching Home is quiet, and the pool is released in `onDestroy`. The emulator runs `-no-audio`; no logcat audio errors, but the sound has not been heard yet. Needs the TV.
- **1.5.9 glass:** dock/panel PNGs are now the full 1504×232 / 1504×888 design size with a 4× anti-aliased rounded mask, no runtime blur; `plate.png` stays 2× at 576×400. The dock label shadow was reduced from 2 px to 1 px. Version 1.5.9 (22).
- **1.5.8 top controls:** Inputs, Apps and Settings are icon-only, matching the reference. The fourth network icon is kept. Dock labels remain and follow the App labels setting; optional quick shortcuts keep their labels.
- `out/tvhome.apk` is signed, 4,680,923 bytes, package `com.ansub.tvhome` 1.5.9 (22), minSdk 21, targetSdk 34. Verified with `apksigner`, `aapt2` and `zipalign`; SHA-256 `8d63beff28d70a69b6746dced04f1949d90221114dcad0269767412720fb93ac`.
- **Home routing now supports all three stock launchers:** `com.google.android.apps.tv.launcherx` (Google TV), `com.google.android.tvlauncher` (Android TV 9–11) and `com.google.android.leanbacklauncher`. Confirmed on the emulator, whose stock home is `tvlauncher`: with the service off, Home opens `tvlauncher`; with it on, Home opens this launcher. Hold Back opens `tvlauncher` and stays there (no redirect loop).
- **The Settings row reads the real stock launcher** and showed *Enabled* and *Disabled* correctly when `tvlauncher` was enabled and temporarily disabled.
- **`install.sh` no longer downloads anything:** it fails if `out/tvhome.apk` is missing and refuses a build older than its source. It never disables a stock launcher unless `DISABLE_STOCK_HOME=1` (and on Google TV also `GOOGLE_TV=1`). Running it on the emulator left `pm list packages -d` empty.
- **1.5.9 emulator checks passed:** Prime Video showed the full smile plus arrow, and AirScreen, YouTube and Google Play Store showed their white marks with labels. The Settings panel opened via **Add app → Up (Inputs) → Right (Apps) → Right (Settings) → OK**. The Prime and AirScreen packages were temporary stubs using the real names; both were uninstalled and the saved list reset to `com.google.android.youtube.tv`. No crashes. `docs/screenshots/home.jpg` and `settings.jpg` are the 1.5.9 test screenshots.
- **1.5.7/1.5.8 checks stand:** home, D-pad focus, add/move/replace/remove, hold OK, Settings, both toggles, wallpaper picker, Inputs and Apps panels, Back, hold Back, Home routing. The 1.5.8 five-logo dock and icon-only controls were verified on 2026-11-05.
- Emulator-only numbers: **1.5.9: 41,345 KB PSS / 161,360 KB RSS**, 12 frames after 10 focus moves, **2 janky (16.67%)**, p50 21 ms, p90 26 ms, p95 32 ms, p99 32 ms, 0 missed vsync, 0 slow UI thread. The frame sample is small; 1.5.7 measured 31.7 MB and 3.7% over 54 frames. These are not the TV's numbers.
- **Ad blocking:** the official YouTube app cannot be ad-blocked by this launcher. SmartTube is a separate optional install (MIT, third-party), not bundled; it was not installed because the TV was offline. No ad-block is claimed.
- Next: reconnect the TV, install 1.5.9 with the five apps, verify the Prime arrow, AirScreen/Play Store marks, focus sound, full-res glass and Home, then measure **its** RAM/frames. Do not start cleanup until the owner approves each package.

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
| YouTube ads | Do not bundle an ad blocker or unofficial YouTube app. The official app cannot be ad-blocked by the launcher. SmartTube is an optional separate install (MIT, third-party); not installed (TV offline, 2026-11-05). |
| Top controls | Icon-only Inputs, Apps and Settings, matching the reference; the network icon stays. Implemented in 1.5.8. |
| Dock icons | White monochrome brand marks for known packages, like CleanFrame; unknown packages keep their own icon. Implemented in 1.5.8; extended to AirScreen and Play Store and fixed the Prime arrow in 1.5.9. |
| Dock sound | A short, soft tick when focus moves between home tiles; no sound on initial launch. Implemented in 1.5.9. |

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
| `src/com/ansub/tvhome/MainActivity.java` | One screen (~1,850 lines): glass dock and white brand marks, clock, icon-only top controls, wallpaper, tiles, panels, inputs, network, menus. |
| `src/com/ansub/tvhome/HomeButton.java` | Opt-in accessibility service; redirects any of the three stock home screens to this launcher, debounced with crash/failure guards. Also answers which stock home exists for the Settings row. |
| `src/com/ansub/tvhome/LineIcon.java` | Vector-ish line icons from int op arrays; no image resources. |
| `res/drawable/logo_*.xml` | Eight white vector brand marks: Netflix, YouTube, Spotify, Prime Video (smile + arrow head), Stremio, Apple TV, YouTube Music, Google Play Store. AirScreen uses `res/drawable-nodpi/logo_airscreen.png`, a white transparent PNG. Unknown packages use their installed icon. |
| `res/raw/hover.wav` | Generated 75 ms mono focus tick, loaded by `SoundPool`; no third-party audio. |
| `src/com/ansub/tvhome/Strings.java` | 16-language labels and date patterns. |
| `build.sh` | Generates `Apps.java`, aapt2 compile/link, javac, d8, zipalign, apksigner. |
| `res/drawable-nodpi/` | Six `wallpaper_*.jpg`, six full-size `dock_*.png` (1504×232), six full-size `panel_*.png` (1504×888), 2× `plate.png`, `logo_airscreen.png`. |
| `assets/fonts/` | Manrope variable font + OFL licence. |
| `tools/generate_assets.py` | Deterministic Pillow renderer for all wallpaper/glass bitmaps. |
| `tools/env.sh` | Sets Java 17, SDK, adb, emulator, AVD paths. |
| `docs/screenshots/` | Final emulator screenshots (`home.jpg`, `settings.jpg`, `wallpapers.jpg`); `home.jpg` is the 1.5.9 four-mark test (Prime Video, YouTube, AirScreen, Google Play Store). |
| `mockups/` | Design mockups + generator + credits (not shipped). |
| `docs/restyle-plan.md` | Mapping, performance budget, limits, open questions. |

## What was built

- **Geometry:** 1920×1080 design, scaled by `widthPixels / 1920f`. Dock glass 1504×232 at (208, 676); tiles 288×200, 296 pitch, tile radius 32, dock radius 48. CleanFrame's measured geometry.
- **Pre-rendered assets:** each wallpaper is a 1920×1080 JPEG with a top shade and bottom scrim. Per-wallpaper dock glass (blur 28, veil) and settings glass (blur 42) are PNGs at the full 1504×232 / 1504×888 design size with a 4× anti-aliased rounded mask. `plate.png` is a white 24%-alpha rounded focus plate at 2× (576×400), downscaled by the TV. No runtime blur.
- **Focus:** plate alpha 0→1 in 120 ms; icon/label `translationY(-3dp)` + `scale 1.04` in 180 ms with `withLayer()`. No layout during animation.
- **Dock:** `HorizontalScrollView` + `LinearLayout`; focus scrolls the row. Known packages get a bundled white mark, centered at its own proportions; other apps get their own icon, fit-cropped. A short `SoundPool` tick plays as focus moves between dock tiles, except during the first 450 ms after `onResume`. Rebuilds clear the row with `dockRow.removeAllViews()` (a targeted removal once left a stale, focusable tile behind; do not regress this).
- **Top controls:** Inputs, Apps and Settings are icon-only (their names remain content descriptions); the network icon is unchanged. Optional quick shortcuts keep labels. With the narrower row, the tested D-pad path is **Add app → Up (Inputs) → Right (Apps) → Right (Settings) → OK**; Left from Inputs returns to the dock.
- **Settings:** Wallpaper, Apps on Home, Inputs, Show date, App labels, Google TV home (reads the stock launcher that actually exists: enabled/disabled/not available), Brightness (non-box TVs), TV settings. The two toggles update immediately and persist in `config` prefs.
- **Wallpaper picker:** six thumbnails + half-res preview; OK saves, Back keeps the current one.
- **Apps on Home:** the dock is the saved `apps` pref. A first launch with no saved value seeds from `apps.txt` (filtered to installed, launchable apps), then fills the row with other installed TV apps until there are six. Once anything is saved, the dock follows the saved list exactly. All installed apps remain available from the **Apps** top control. The owner's order is Netflix, YouTube, Spotify, Prime Video, Stremio.
- **Font:** Manrope variable from `assets/fonts` (OFL); falls back to the TV's sans-serif.

## Verification

### 1.5.9 emulator (2026-11-06)

Environment: Android TV 14 API 34 emulator, 1920×1080, host GPU.

- `aapt2 dump badging`: `com.ansub.tvhome` 1.5.9 (22), minSdk 21, targetSdk 34; APK 4,680,923 bytes; SHA-256 `8d63beff28d70a69b6746dced04f1949d90221114dcad0269767412720fb93ac`; `apksigner verify` and `zipalign` OK.
- Prime Video showed the smile **and arrow head**; AirScreen showed the official “AS” monogram; Google Play Store and YouTube showed their marks. `docs/screenshots/home.jpg`.
- Settings opened with the same D-pad path and showed the full-resolution panel; `docs/screenshots/settings.jpg`.
- The Prime and AirScreen test packages were uninstalled and the saved list reset to `com.google.android.youtube.tv`; the Play Store is the emulator's real package.
- Focus sound: `SoundPool` loading produced no logcat errors. The emulator was started with `-no-audio`, so the tick was not heard; this needs the TV.
- Memory: **41,345 KB PSS / 161,360 KB RSS**. Frames after 10 focus moves: **12 frames, 2 janky (16.67%)**, p50 21 ms, p90 26 ms, p95 32 ms, p99 32 ms, 0 missed vsync, 0 slow UI thread. Small sample; treat as a smoke test.
- No crashes. Not verified for 1.5.9: the TV, real HDMI, real GPU frames, 12/24, reboot, audible sound.

### 1.5.8 emulator (2026-11-05)

Environment: Android TV 14 API 34 emulator, 1920×1080, host GPU.

- `aapt2 dump badging`: `com.ansub.tvhome` 1.5.8 (21), minSdk 21, targetSdk 34; APK 3,779,577 bytes; SHA-256 `99ae738a1c61a88e3ef79b2def659e50e0ebc28f35533bdf5d39615919b5dbf7`; `apksigner verify` OK.
- Five white marks in the owner's order (Netflix, YouTube, Spotify, Prime Video, Stremio) with labels; `docs/screenshots/home.jpg`. The emulator has only the YouTube stub; the other four were temporary packages using the real package names, then uninstalled. The saved list was reset to `com.google.android.youtube.tv`.
- Inputs/Apps/Settings icon-only. D-pad: Add app → Up (Inputs) → Right (Apps) → Right (Settings) → OK opened Settings; Back closed it. Left from Inputs returns to the dock; that is the focus graph, not a broken control.
- Home: with the Home button service enabled/bound, Home returned to `com.ansub.tvhome/.MainActivity`; with the service off, Home stayed on `tvlauncher`. The service was re-enabled after a test cleanup; no launcher code writes the accessibility setting.
- No crashes. Not verified for 1.5.8: the TV (offline), real HDMI, real GPU frames, 12/24, reboot.
- **TV 1.5.7:** installed on the ORCA (Android 11, 1280×720, stock `launcherx`); Home verified with the service. Its Android 11 build lacks `cmd role get-role-holders`, so the install script's role check is inconclusive; ignore the warning. Hold Back, Settings row, HDMI, clock/date, wallpaper, app labels and reboot remain unverified on the TV. The TV was offline on 2026-11-05.

### 1.5.7 emulator (2026-10-31)

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
- Not verified at 1.5.7: the ORCA's real GPU frame times, real HDMI inputs, 12/24 clock preference, reboot behavior. The `launcherx` Home route and Android 11 accessibility were later verified on the ORCA; `leanbacklauncher` remains code-only. Those TV items need the TV (or an API 30 image, which does not exist for ARM64).

## Gotchas

- The emulator's YouTube stub opens a "YouTube is not supported on this device" page. That is the emulator, not the launcher.
- Emulator `dumpsys gfxinfo` with software GPU is meaningless (100% jank). Always use `-gpu host` for comparisons and still treat it as a smoke test, not TV performance.
- Clearing the `apps` pref to an empty string intentionally leaves an empty dock (plus Add). It does **not** reseed from `apps.txt`; only a missing pref (`null`) does.
- **`install.sh` never disables a stock launcher by default.** `DISABLE_STOCK_HOME=1` offers it; a Google TV also needs `GOOGLE_TV=1`. Do not use those switches without a tested recovery path. Home routing is done by the **Home button** accessibility service (and the HOME role, which the script sets).
- `install.sh` installs **only** `out/tvhome.apk`; there is no release download. It refuses a build older than `src/`, `res/`, `assets/`, `AndroidManifest.xml` or `build.sh` unless `ALLOW_STALE=1`.
- On Android 14 the HOME role decides what Home opens, while `cmd package resolve-activity -c android.intent.category.HOME` can still name a higher-priority stock launcher. `install.sh` therefore treats `cmd role get-role-holders android.app.role.HOME` = `com.ansub.tvhome` as success; do not “fix” that back to resolve-activity alone. **On the ORCA's Android 11, `cmd role get-role-holders` is unsupported**, so the script's role check is inconclusive; the accessibility service is the route. Ignore the fallback warning and test Home.
- The accessibility service watches only each stock package's own HOME activity, so Google TV's Apps/Settings pages are not redirected. Do not loosen that to “any activity in the package”, or hold Back will bounce back.
- `launcherx` and `leanbacklauncher` are covered by code and manifest queries. The emulator only ships `tvlauncher`; `launcherx` Home routing was verified on the ORCA with 1.5.7; `leanbacklauncher` remains code-only.
- On Android 11+, sideloaded apps may need **App info → ⋮ → Allow restricted settings** before the accessibility toggle can be turned on.
- **Top-control focus after the labels were removed:** the row is narrower. The tested path is **Add app → Up (Inputs) → Right (Apps) → Right (Settings) → OK**. Left from Inputs returns to the dock, and Up from a middle dock tile may stay in the dock. Do not report the controls as broken from a middle tile.
- **Accessibility setting:** no launcher code writes `enabled_accessibility_services`; the emulator's setting was toggled during test cleanup. Re-enable our service with the GUIDE command after a cleanup or reinstall. Do not weaken the Home service to make the emulator test simpler.
- **The 1.5.9 screenshot used temporary packages:** the emulator has only the YouTube stub, so `com.amazon.amazonvideo.livingroom` and `com.ionitech.airscreen` were temporary test packages with the real names; the Play Store is real. Both temporary apps were uninstalled and the saved list is `com.google.android.youtube.tv`. The screenshot is UI evidence, not a real-TV install.
- **Unknown dock apps keep their color icon:** only the nine packages in `brandLogo` get the white marks. Add a vector drawable (or a white transparent PNG) and a `brandLogo` entry for another package.
- **Prime Video mark:** the historical Wikimedia `Amazon Prime Video logo.svg` splits the smile and arrow head into separate paths. 1.5.8 used only the smile and looked arrow-less; 1.5.9 adds the `M580.4,148.4…` arrow path and starts the crop at y 147.9. Keep both paths. The source is public domain as a simple logo (PD-textlogo); Amazon's trademark still applies. The current 2024 Prime mark is different; do not swap it silently.
- **AirScreen mark:** white transparent PNG traced from the official 512px Google Play icon, 512×322, displayed at 100×63. It is the AirScreen trademark, used only to identify the app; see notices. The Play Store mark is the Simple Icons CC0 `googleplay` path.
- **Focus sound:** it is intentionally silent for 450 ms after `onResume`; do not remove that guard or the launcher clicks on every launch. The sound is bundled and generated, not sampled. The emulator's `-no-audio` means it cannot confirm audibility.
- **Full-resolution glass:** the dock is 1504×232 and each panel 1504×888; decoded panel memory is higher (emulator PSS 41.3 MB vs 31.7 MB at 1.5.7). The TV has 2 GB-class RAM; re-measure there.
- The TV cleanup is not automated here and is not approved. Do not run `pm disable-user` on the TV.

## Next steps

1. Reconnect the ORCA: `adb connect 192.168.8.187:5555`; confirm the five packages; install 1.5.9 with `sh install.sh 192.168.8.187:5555 "com.netflix.ninja,com.google.android.youtube.tv,com.spotify.tv.android,com.amazon.amazonvideo.livingroom,com.stremio.one"`.
2. Confirm the Prime arrow, AirScreen/Play Store marks, dock focus sound, full-res glass, Home (service on), hold Back, Settings → Google TV home, HDMI, clock/date, wallpaper, App labels. Note the role-query warning; the service is the route.
3. Measure `dumpsys meminfo` and `dumpsys gfxinfo` on the TV; show free RAM before/after.
4. Decide on SmartTube separately if the owner still wants ad-free YouTube; do not bundle or patch the official app.
5. Measure Google TV launcher idle cost; present the three options (leave cached / force-stop after boot / disable with recovery) and wait for the owner.
6. Cleanup one package at a time with approval and an undo file.
7. Reboot once, confirm boot + Home, remind the owner to turn debugging off.

## When you finish a session

1. Update **PROGRESS.md** (what changed, what is verified, what is next).
2. Update **AGENTS.md** (state, decisions, new gotchas).
3. Update **GUIDE.md** (commands, setup, recovery if changed).
4. Keep **THIRD_PARTY_NOTICES.md** current when assets change.
5. Commit and push to `mine` only. Do not touch `origin`.
