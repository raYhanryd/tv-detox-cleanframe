# PROGRESS.md

**Last updated:** 2026-10-30
**Phase:** design approved in direction; tooling in progress; **no Android UI code written yet**
**TV:** not connected, nothing installed

## Status

| Area | State |
| --- | --- |
| Both repos read | Done |
| Plan and mapping | Done — [docs/restyle-plan.md](docs/restyle-plan.md) |
| 1080p mockups + generator | Done — [mockups/](mockups/) |
| Design approval | Pending explicit approval before Android code |
| GitHub repo | Created: <https://github.com/raYhanryd/tv-detox-cleanframe> (private) |
| Local toolchain | In progress / see log |
| Baseline build | Not yet |
| Emulator | Not installed; API 33/34 ARM64 recommended (no API 30 ARM image) |
| Restyled UI | Not started |
| TV install / Home button | Not started |
| Cleanup | Not started; requires per-app approval |
| Google TV home decision | Not started; measure first |

## Decisions from the owner

1. Clock date: **setting for both** — "Show date" toggle (default off).
2. Dock labels: **setting for both** — icons + names / icons only (default names).
3. Wallpapers: use these six photos at **full quality**, with credits.
4. Repo: uploaded to the owner's GitHub.
5. Emulator: optional; if installed, keep it inside `.tools/` so deleting the folder removes it. Must actually verify the app works.

## Done in this session

- Cloned upstream TV Detox v1.5.7 into the empty workspace and unshallowed it.
- Read tv-detox README, debloat docs, manifest, build/install scripts and all Java source.
- Read CleanFrame AGENTS/README, interaction, assets, asset-source, development, public-release docs, CSS and dock geometry.
- Wrote the mapping/limits/performance plan.
- Built four 1920×1080 mockups with a deterministic Pillow renderer; added credits and a reference screenshot.
- Created the private GitHub repo `raYhanryd/tv-detox-cleanframe`.
- Added AGENTS.md, GUIDE.md, PROGRESS.md.

## Next steps (in order)

1. Finish the local `.tools/` JDK 17 + Android SDK install and build the **unchanged** launcher (baseline APK).
2. Get explicit design approval from the owner.
3. Implement the dock, pre-rendered glass, wallpapers, Settings toggles and Google TV home entry in Java.
4. Screenshot each stage; run focus/add/remove/HDMI/network/clock tests.
5. Optional local emulator (API 33/34 ARM64) for UI verification; measure what it can.
6. Connect to the TV only after owner confirmation; install, set Home, measure RAM/frames, then cleanup one approved change at a time.
7. Restart once; verify boot and Home; show free RAM before/after; turn debugging off.

## Log

- **2026-10-30** — Discovery and design. Mockups: `01-home-dock-misty.png`, `02-home-dock-alpine.png`, `03-settings-wallpaper.png`, `04-settings-overview.png`. GitHub repo created (private). Owner answers recorded above. No device access.
- **2026-10-30** — Emulator research: Android TV ARM64 system images start at API 31; API 30 has x86 only. Emulator, if used, will be API 33/34 and stored in `.tools/`.

## Open risks

- Emulator is not the TV: real GPU frame times and RAM must be measured on the ORCA 2K.
- Pre-rendered glass tiles must line up across wallpapers at every screen scale; verify on 1080p and emulator.
- Photo bundle at full quality increases APK size; decoded wallpaper increases RAM ~8 MB. Measure and report.
- Google TV home must not be disabled during cleanup; the owner must choose an option after measurements.
