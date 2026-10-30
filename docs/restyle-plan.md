# Restyling the home screen after CleanFrame

**Status: proposal only.** Nothing in the Android source has changed, no build tools are installed, and nothing has touched the TV. This plan follows steps 1–2 of the requested process: read both repos, map CleanFrame's design onto this launcher, then show mockups and wait.

## What this workspace is

- Base: [Ansub/tv-detox](https://github.com/Ansub/tv-detox) upstream `main` (version 1.5.7), mirrored to the owner's private repo <https://github.com/raYhanryd/tv-detox-cleanframe>. `origin` stays read-only.
- tv-detox has no `AGENTS.md`; I read `README.md`, `docs/debloat.md`, the manifest, `build.sh`, `install.sh`/`candidates.sh`/`undo.sh` interfaces, and all of `src/com/ansub/tvhome/`.
- CleanFrame reference: cloned separately (not part of this app). Read `AGENTS.md`, `README.md`, `docs/development.md` context, `docs/interaction-behaviour.md`, `docs/assets.md`, `docs/asset-sources.md`, `THIRD_PARTY_NOTICES.md`, `app/style.css`, and the dock/item geometry in `app/main.js`. No CleanFrame code will be ported; it is a Tizen web app, this stays native Java.

## Mapping: CleanFrame → this launcher

| CleanFrame element | What it becomes here |
| --- | --- |
| Full-bleed photograph, top shade + bottom scrim | Each wallpaper is a 1920×1080 JPEG with the shade and scrim baked in. One window background, no overlay views. |
| Dock: 1504×232 at (208, 676), 288×200 tiles, 296 pitch, 48px panel, 32px plate | Same geometry, laid out at 1920×1080 and scaled by screen width exactly as the current app does. |
| Glass material rendered ahead of time (`field-blur`, `field-frost`, panel JPEGs) | Per-wallpaper frosted panel, generated on the Mac: 28px blur of the same registered crop, 18% dark veil, rounded corners baked into the PNG. Runtime only loads a bitmap. Half resolution (752×116) because it is blurred anyway, then scaled by the GPU. |
| Focused tile plate, white 30→16%, inset top hairline | Pre-rendered plate PNG. Alpha 0→1 over 120ms; icon and label lift with `translationY(-3px)` + `scale 1.04` over 180ms. No relayout, no blur, hardware layer during the animation. |
| Clock at top left, 48px, 12-hour, no seconds | `TextClock` at 48px, keeping the existing 12/24 preference. A **Show date** setting (default off) adds a small second line, so the CleanFrame look and the old date are both available. |
| Art Mode / All apps / Settings top right | Inputs / Apps / Settings, then the live Wi-Fi/Ethernet/offline icon. Up from the dock reaches them, Back returns. The three labels fade in on focus; icons stay quiet at rest. |
| Dock scrolls left/right without wrapping | The tile container animates `translationX`; snapping happens when motion ends. One property animation, no layout during the scroll. |
| Settings sheet over the blurred stage | A 1504×888 glass panel over the dimmed wallpaper: Wallpaper, Apps on Home, Inputs, Bluetooth/Sound/Picture (only the ones your install enabled), Brightness, TV settings, Google TV home. |
| Wallpaper picker: list of thumbnails, large preview, OK applies, Back restores | Same two-pane picker, six bundled photos at full quality, saved in the existing `config` SharedPreferences. |
| Icon + name labels under dock icons | An **App labels** setting: icons + names (default) or icons only. |
| List layout, icons-only mode, font catalog, material/tint choices, rotation modes | Not in v1. The dock layout is the requested one; these can come later if wanted. |
| Samsung Art Mode / Samsung Home | Not applicable. Replaced by the existing HDMI inputs and the new Google TV home entry. |
| Tizen ES5 runtime | Plain Java `FrameLayout`/`ImageView`/`TextView`; no WebView, no libraries, no Gradle. |

### Existing behaviour that stays

- App launching (leanback intent first, then normal launch intent), package add/remove refresh.
- HDMI inputs from `TvInputManager`, including rename/remove menus and the existing Live TV fallback chain.
- Clock handling and the `clock` install override; network state and the Wi-Fi/Ethernet/offline icon.
- Hold OK / Menu on an app: Move, Replace, Remove, Uninstall/App info. Add app from the **Apps** control instead of the old bottom-row + tile.
- Hold Back opens Google TV's home screen (`HomeButton.openGoogleTv`), and the accessibility Home-button service is untouched.
- Bluetooth/Sound/Picture shortcuts that `install.sh --es quick` enabled, moved into Settings so the top row stays clean.
- `build.sh`, `install.sh`, `undo.sh`, `check.sh`, `candidates.sh` interfaces stay compatible.

### What cannot match exactly

- **Live blur.** Android 11 has no cheap backdrop blur and the brief rules it out. Every panel is pre-rendered per wallpaper; changing wallpaper swaps both images together.
- **Pixel-identical CSS.** Gradients, easing and letter spacing will be close, not identical. CleanFrame's exact `cubic-bezier` is approximated with `DecelerateInterpolator(1.8f)`.
- **Brand marks for every app.** A small set of free-licence marks (Simple Icons CC0, Custom Brand Icons MIT) is bundled; other apps use their installed icon, then a two-letter monogram. TV apps often ship low-resolution icons, so hardware removal may look imperfect.
- **Shelf edge fades and overscroll.** CleanFrame masks the dock ends with CSS. Native clipping means a partially visible tile instead; no mask fades in v1.
- **Settings depth.** CleanFrame's per-group two-pane appearance screens are simplified to one panel and one wallpaper picker.
- **60fps guarantee.** The ORCA 2K's GPU is unknown until measured. The design avoids layout and blur on the animation path; `dumpsys gfxinfo` will show whether it holds.

## Memory and frame budget

Measured target, 1920×1080 UI:

| Item | Decoded | Notes |
| --- | --- | --- |
| Wallpaper, `ARGB_8888` | 8.3 MB | one at a time; transient second copy during a crossfade |
| Dock glass, half-res PNG | ~0.35 MB | one per wallpaper, decoded with the wallpaper |
| Settings glass, half-res PNG | ~1.3 MB | decoded only while Settings is open |
| App marks + monogram fallbacks | ~0.3 MB | 96px targets |
| Manrope variable TTF | ~0.2 MB | memory-mapped by `Typeface` |
| **Net increase** | **~9–10 MB steady** | current app is ~30 MB, so expect ~39–40 MB |

If that is too much, switching the wallpaper to `RGB_565` saves 4.1 MB at the cost of slight banding in skies. I will report the real numbers from `dumpsys meminfo` rather than promise this table.

Animation rules: transform/alpha only; `withLayer()` while a tile is moving; no `requestLayout` in listeners; wallpaper and glass decoded before being shown; no runtime blur; no new views per frame.

Measurement: `dumpsys gfxinfo com.ansub.tvhome reset`, then 30 D-pad moves, a dock scroll, open/close Settings, then `dumpsys gfxinfo com.ansub.tvhome` and `framestats` for janky %. Report p50/p90/p99 and janky frames before and after. `dumpsys meminfo` before/after, plus Google TV home idle cost.

## Assets and licences

Mockup assets are in `mockups/` with credits in [CREDITS.md](../mockups/CREDITS.md).

- **Fonts:** Manrope (SIL OFL 1.1). CleanFrame also bundles Geist and Newsreader (OFL); v1 needs only Manrope. Any bundled font keeps its licence text in `assets/licenses/`.
- **Photos:** the six Unsplash photographs are approved, bundled at their existing full quality (1920×1080, no extra downscale), with credits. The Unsplash licence allows copying, modification and distribution with restrictions (no selling unmodified images; no competing image service). Credits stay in the app/repo.
- **Icons:** Simple Icons (CC0) for YouTube, Netflix, Plex, Spotify, Apple TV and Prime Video; Disney+ from Custom Brand Icons (MIT); CleanFrame's original line drawings are MIT if reused. Brand marks remain trademarks of their owners; the app claims no affiliation.
- **Code:** CleanFrame is MIT; only its measurements and design ideas are used, no Tizen code.

## Bloatware cleanup (later, with approval)

Not started. When we get there:

1. `sh supports.sh <TV_IP>` then `sh candidates.sh <TV_IP>` — read-only.
2. Present every installed package with one of `never / keep / safe / review` and a plain-English sentence, plus the reason (persistent, Wi-Fi owner, HDMI, casting, etc.).
3. Ask before each change; use `pm disable-user --user 0`, never `pm uninstall` on system apps.
4. Keep `cleanup-undo-<date>.sh` with every package changed; test after each small batch and reboot.
5. Never-disable list from the TV Detox README: Play services/framework, Play Store, Settings, System UI, setup apps, keyboard, Bluetooth, HDMI/TV input and tuner framework, package installer, providers, anything `PERSISTENT`, and whatever saved the Wi-Fi. On Google TV, Google TV's home screen is handled separately (below), not swept into the cleanup.
6. Leave anything unknown on.

## Google TV home screen (item 3a–3c)

Do the measurement **before** choosing an approach:

- `dumpsys meminfo` free RAM and `com.google.android.apps.tv.launcherx` PSS/TOTAL while idle on Google TV home, then after opening this launcher once, then 60 seconds later (cached).
- `dumpsys activity processes` for its oom adj / cached state.
- Record boot RAM as a baseline, and repeat after a reboot.

Then present three options with those numbers and risks:

- **A. Leave it enabled, cached.** No boot risk. Android reclaims it under pressure. Likely recommendation on a 2 GB box unless it holds a lot while cached.
- **B. Force-stop after boot** (`adb shell am force-stop com.google.android.apps.tv.launcherx`). Frees it until something starts it again; low risk, but not permanent and needs adb after each boot.
- **C. Disable it** (`pm disable-user --user 0 …`), re-enable over adb only when needed. This is the option that has caused boot loops/factory resets on some Google TVs. Only with a tested recovery path and your explicit OK.

I will recommend one based on the numbers and wait. Separately, Settings gets a **Google TV home** row that opens `com.google.android.apps.tv.launcherx/.home.HomeActivity` only if it resolves and is enabled; otherwise the row says it is disabled.

## Build tooling (installed locally)

Everything lives in `.tools/` and nothing was installed system-wide:

- Temurin JDK 17.0.21 (local tarball)
- Android command-line tools 19.0 + platform-tools 37.0.1 (adb)
- `platforms;android-34` and `build-tools;34.0.0`
- Emulator **not** installed; Android TV ARM64 images exist only for API 31/33/34/36 (~1.6–2 GB if wanted).

`. tools/env.sh` sets the paths; the unchanged launcher builds with `sh build.sh` to a signed 54 KB `out/tvhome.apk`. The restyle will add `-A assets` so the generated wallpapers, glass panels, marks and font are packaged. No Gradle, no new Java libraries.

## Recovery before anything risky

- Turn off **Settings → Accessibility → Home button** to restore Google TV's Home.
- Uninstall this launcher (`adb uninstall com.ansub.tvhome`) or run `sh undo.sh <TV_IP>`.
- Undo cleanup with `pm enable <package>` or the per-run undo script.
- If Home stops working: `adb shell cmd package set-home-activity com.google.android.apps.tv.launcherx/.home.HomeActivity` (or the setup app) and reboot.
- Wireless debugging off when finished; debugging left on lets other devices on the LAN ask to control the TV.

## Decisions and the one remaining question

1. **Date:** a **Show date** setting, default off. Both looks are available.
2. **Dock labels:** an **App labels** setting, icons + names or icons only. Both.
3. **Photos:** approved; six photos at full quality with credits.
4. **Repo:** private GitHub repo at <https://github.com/raYhanryd/tv-detox-cleanframe>. Upstream remains the read-only reference.
5. **Emulator (open):** install it project-locally, or build and test directly on the TV? Android TV ARM64 images exist only for API 31/33/34/36 on this Apple Silicon Mac, so an emulator would be Android TV 13/14, not the TV's Android 11.

Explicit approval of the design is still required before Android code is written.
