# AGENTS.md — read this first

This file is the handoff for any model, agent or session working in this repo. **Update it, [GUIDE.md](GUIDE.md) and [PROGRESS.md](PROGRESS.md) before you finish a work session.** If scope changes, also update [docs/restyle-plan.md](docs/restyle-plan.md).

## What this is

A native Android TV launcher, forked from [Ansub/tv-detox](https://github.com/Ansub/tv-detox) (MIT), being restyled to look like [CleanFrame](https://github.com/nthnclrk/CleanFrame) (MIT, Samsung Tizen web app). CleanFrame is a *visual reference only*. Do not port its JavaScript, HTML, CSS or Tizen APIs. Rebuild the look in plain Java.

Owner's TV: **ORCA 2K Google TV**, Android TV OS 11 (API 30), stock, 2 GB-class RAM. The launcher is **not installed yet**. Computer: Apple Silicon Mac (M1), macOS, Java 25 installed system-wide; builds must use Java 17.

Remote: `https://github.com/raYhanryd/tv-detox-cleanframe` (private). Upstream remote is `origin` (Ansub/tv-detox). **Never push to `origin`.** The owner's remote is `mine`.

## Current phase (2026-10-30)

**Design approval / tooling. No Android source has been changed.** The original launcher compiles and works; the restyle is not implemented.

- Discovery: both repos read; mapping and constraints in [docs/restyle-plan.md](docs/restyle-plan.md).
- Mockups: [mockups/](mockups/) (reference + 4 1080p mockups + generator + credits).
- Owner answered the design questions; see **Owner decisions** below.
- Local toolchain installed in `.tools/` and the **unchanged baseline builds** (`out/tvhome.apk`, signed, 54 KB, package `com.ansub.tvhome` 1.5.7, minSdk 21, targetSdk 34).
- Next: explicit approval of the mockups, then implement the restyle.

## Hard rules

1. **Plain Java only.** No Gradle, no libraries, no WebView, no Kotlin, no AndroidX. The build is `build.sh` (aapt2 + javac + d8 + apksigner). Keep `minSdk 21`, `targetSdk 34`, `compileSdk 34`.
2. **Preserve** app launching, HDMI inputs, clock, Wi-Fi/network icon, add/move/remove/replace apps, long-press/OK/Back behaviour, and the `HomeButton` accessibility service. Tell the owner before changing any of it.
3. **Animations:** transform and opacity only. No layout/measure work during animation, no runtime blur, no `requestLayout` in listeners, hardware layer (`withLayer()`) while a tile moves. Do **not** change system animation scales (`window_animation_scale`, `transition_animation_scale`, `animator_duration_scale`) unless the owner explicitly picks a value.
4. **Assets:** pre-render blur/glass on the Mac; the TV only decodes bitmaps. Bundle only fonts with a bundling licence (Manrope is OFL; Geist/Newsreader also OFL). Keep photo/icon credits and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) current.
5. **Cleanup:** never uninstall system apps. Use `pm disable-user --user 0`; ask before **every** package; keep an undo list. Respect the TV Detox never-disable list and the Google TV launcher caution. Disable nothing without the owner's explicit OK.
6. **Google TV home:** measure with `dumpsys meminfo` first; present options with real numbers; do not disable, force-stop or otherwise change it without approval.
7. **TV access:** only after the owner confirms. Wireless debugging pairing and install instructions are in [GUIDE.md](GUIDE.md). Nothing is currently connected.
8. **Git:** do not push to upstream. Commit only files relevant to the current change; do not stage unrelated work. Pushing to `mine` is allowed because the owner asked for the repo to be kept on GitHub.
9. **Tooling:** everything installed for this project lives in `.tools/` (JDK, Android SDK, AVD, Python venv). Do not install system-wide Homebrew packages unless the owner asks. See [GUIDE.md](GUIDE.md#tools-and-deleting-them).

## Owner decisions (already made)

| Topic | Decision |
| --- | --- |
| Clock | **Setting for both:** a "Show date" toggle under the clock. Default: date off (CleanFrame look), user can turn it on. |
| Dock labels | **Setting for both:** "Icons + names" or "Icons only", default icons + names. |
| Wallpapers | Use the six CleanFrame Unsplash photos at **full quality** (1920×1080 JPEGs as bundled), with credits. |
| GitHub | Private repo `raYhanryd/tv-detox-cleanframe`. |
| Emulator | Owner wants confidence it works; emulator optional, but if installed it must live in `.tools/` so deleting the folder removes it. |
| Date/clock format | Keep the existing 12/24 preference; do not force it. |
| YouTube remote button | Not required; do not spend effort preserving it. |

## Tooling layout (installed 2026-10-30)

Everything is project-local, git-ignored, and safe to delete with the folder. Installed: Temurin JDK **17.0.21**, sdkmanager **19.0**, platform-tools **37.0.1** (adb 1.0.41), **platforms;android-34**, **build-tools;34.0.0**. `.tools/` is currently ~818 MB. Emulator is **not** installed.

```
.tools/
  jdk-17/                 # Temurin JDK 17 (local, not Homebrew)
  android-sdk/            # cmdline-tools, platform-tools (adb), platform 34, build-tools 34.0.0
  android-home/           # ANDROID_USER_HOME / emulator config / adb keys where supported
  avd/                    # ANDROID_AVD_HOME (emulator only, if installed)
  venv/                   # Pillow for asset generation
.android/                 # fallback for anything that insists on ~/.android
```

`build.sh` already auto-detects `/opt/homebrew/opt/openjdk@17`, the Android SDK in common locations, and `ANDROID_HOME`. Export the local paths before building (see GUIDE).

Emulator reality on Apple Silicon: Android TV ARM64 images exist for **API 31, 33, 34, 36**, not API 30 (Android 11). Use API 33 or 34; it is representative but not identical to the TV. Emulator adds roughly **1.6–2 GB**. Do not install it without the owner's OK.

## Build and check

```sh
. tools/env.sh               # sets JAVA_HOME, ANDROID_HOME, adb and emulator paths
adb version
sh build.sh                  # writes out/tvhome.apk
```

Do not commit `out/`, `key.jks`, `.tools/`, `.android/`. `key.jks` is generated on the first build and must be kept for updates.

## Source map (current upstream code)

| File | Role |
| --- | --- |
| `src/com/ansub/tvhome/MainActivity.java` | One screen: clock, grid/dock, tiles, panels, wallpaper, inputs, network, menus. ~1,557 lines. |
| `src/com/ansub/tvhome/HomeButton.java` | Opt-in accessibility service; redirects Google TV home to this launcher, debounced with crash/failure guards. |
| `src/com/ansub/tvhome/LineIcon.java` | Vector-ish line icons from int op arrays; no image resources. |
| `src/com/ansub/tvhome/Strings.java` | 16-language labels and date patterns. |
| `build.sh` | Generates `Apps.java`, aapt2 compile/link, javac, d8, zipalign, apksigner. |
| `res/`, `AndroidManifest.xml` | Icon, banner, accessibility config, HOME + LEANBACK intents. |
| `install.sh`, `undo.sh`, `check.sh`, `candidates.sh` | TV install, undo, health check, read-only app planner. |
| `docs/debloat.md` | Cleanup rules and never-disable lists. |
| `mockups/` | Design mockups + deterministic Pillow renderer + credits. |
| `docs/restyle-plan.md` | Mapping, performance budget, limits, open questions. |

## Implementation notes for the restyle (not built yet)

- Design at 1920×1080, scale by `widthPixels / 1920f` like the current code.
- Dock: panel 1504×232 at (208, 676); tiles 288×200, pitch 296, radius 32; panel radius 48. CleanFrame's measured geometry.
- Pre-render per wallpaper: 1920×1080 photo with top shade and bottom scrim; dock glass (blur 28, veil 18%, rounded PNG); settings glass (blur 42, rounded PNG). Half-res glass is fine.
- Focus: plate alpha 0→1 in 120 ms; icon/label `translationY(-3dp)` + `scale 1.04` in 180 ms; `withLayer()`.
- Scroll: `translationX` on the tile container, snapped on focus changes; no layout.
- Wallpaper change: decode next bundle off the UI thread, swap, recycle old; report peak memory.
- Settings: glass panel with Wallpaper, Apps on Home, Inputs, Bluetooth/Sound/Picture (only if enabled), Brightness, TV settings, Google TV home, and the two new toggles (Show date, App labels).
- Google TV home entry: only show if `com.google.android.apps.tv.launcherx/.home.HomeActivity` resolves and is enabled; otherwise a disabled note.

## Verification requirements

- Build with `. tools/env.sh && sh build.sh`; do not claim success without the APK and install output. Baseline verified on 2026-10-30 with `apksigner verify` and `aapt2 dump badging`.
- Emulator/device screenshots at each stage. D-pad: left/right, up to controls, down/back, OK, hold OK, Back, hold Back.
- `dumpsys gfxinfo com.ansub.tvhome` before/after (janky %, p50/p90/p99), `dumpsys meminfo` before/after. Report real numbers.
- Re-check `up`/`back` focus, add/remove/replace, HDMI tiles, network icon, clock 12/24, wallpaper persistence, rotation/recreate.
- Keep recovery instructions current in GUIDE.md.

## When you finish a session

1. Update **PROGRESS.md** (what changed, what is verified, what is next).
2. Update **AGENTS.md** (state, decisions, new gotchas).
3. Update **GUIDE.md** (commands, setup, recovery if changed).
4. Commit and push to `mine` only. Do not touch `origin`.
