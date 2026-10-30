# GUIDE.md — setup, TV install and recovery

This is the human guide for this fork. For agent/session state read [AGENTS.md](AGENTS.md); for the work log read [PROGRESS.md](PROGRESS.md); for the design mapping read [docs/restyle-plan.md](docs/restyle-plan.md).

## Where things stand

- **The launcher has not been installed on the TV.**
- **No Android code has been changed yet.** The design mockups are in [mockups/](mockups/).
- A private GitHub copy lives at <https://github.com/raYhanryd/tv-detox-cleanframe>.
- Build tools are installed inside this project. The **unchanged launcher builds** to `out/tvhome.apk` (signed, 54 KB) but has **not** been installed on the TV.

## Tools and deleting them

Everything this project installs for development goes in `.tools/` inside this folder. Nothing is installed with Homebrew or system-wide.

| Folder | What it holds | Approx. size |
| --- | --- | --- |
| `.tools/jdk-17` | Temurin JDK **17.0.21**, used only by the build | ~300 MB |
| `.tools/android-sdk` | adb **37.0.1**, platform **34**, build-tools **34.0.0** | ~500 MB |
| `.tools/android-home` | adb keys/config when the tools honour `ANDROID_USER_HOME` | small |
| `.tools/avd` | emulator virtual devices, if installed | 1–3 GB |
| `.tools/venv` | Python + Pillow for generating wallpapers/glass (not created yet) | ~30 MB |
| `.tools/` **total** | measured on 2026-10-30 | **818 MB now, ~2.5 GB with emulator** |

Delete the whole `.tools/` folder when you are done; nothing outside it is needed for the build. A tiny `~/.android/adbkey` may still be created by adb (a few KB) and can be deleted separately.

**To remove everything this session added to the computer:** delete `.tools/` (and `~/.android` if you want adb keys gone). The project source, mockups and docs are deliberate files, and the GitHub repo is a copy. Delete this project folder too if you want none of it locally; delete the GitHub repo in its Settings if you want it gone there.

## Building

The toolchain is installed; one line sets every path:

```sh
. tools/env.sh
sh build.sh
```

Verified on 2026-10-30: exit 0, `out/tvhome.apk`, signed with the local `key.jks`, package `com.ansub.tvhome` 1.5.7, minSdk 21, targetSdk 34, 54 KB. It has not been installed anywhere yet.

`build.sh` creates `key.jks` on the first build. **Keep `key.jks`**; future updates must be signed with the same key. It is git-ignored, so back it up if you plan to update an installed build from another machine.

## Putting it on the TV

Do this only after the design is approved and a build has been tested.

1. On the TV: **Settings → Device Preferences → About**, press **Build** seven times. Then **Developer options → USB debugging** (and **Wireless debugging** if present).
2. Put the Mac and TV on the same Wi-Fi.
3. For Wireless debugging: TV **Developer options → Wireless debugging → Pair device with pairing code**. On the Mac:

   ```sh
   adb pair <TV_IP>:<PAIRING_PORT>
   # type the six-digit code
   adb connect <TV_IP>:<DEBUG_PORT>
   adb devices
   ```

   The debug port changes after a TV restart. Pair and connect again if it drops.
4. Install the launcher with the repo's installer, which also handles the Home role and offers to turn off the stock launcher:

   ```sh
   sh install.sh <TV_IP> "com.google.android.youtube.tv,com.netflix.ninja"
   sh undo.sh <TV_IP>                 # undo the install/home changes
   ```

   The installer **does not** turn off Google TV's home screen on Google TV unless explicitly asked (`GOOGLE_TV=1`); this fork will not use that switch. See [Google TV home](#google-tv-home) below.
5. **Home button on this launcher:** Settings → **Accessibility → Home button** (this app's accessibility service). On Android 11+ sideloaded apps, if the toggle is greyed out, open **Settings → Apps → See all apps → Home → ⋮ → Allow restricted settings** first. Play Protect may warn because the app has an accessibility service.
6. If the Accessibility screen freezes, enable the service over adb instead (keeps other services):

   ```sh
   adb shell '
   service=com.ansub.tvhome/.HomeButton
   services=$(settings get secure enabled_accessibility_services)
   case "$services" in null|"") services="" ;; esac
   case ":$services:" in
     *":$service:"*|*":com.ansub.tvhome/com.ansub.tvhome.HomeButton:"*) ;;
     *) services="${services:+$services:}$service" ;;
   esac
   settings put secure enabled_accessibility_services "$services"
   settings put secure accessibility_enabled 1
   '
   ```
7. Test Home, Back (hold Back opens Google TV's home), all apps, HDMI inputs, Wi-Fi icon and a reboot.
8. **Turn debugging off** when finished: Developer options → USB debugging, Wireless debugging, Network debugging. Left on, other devices on your network can ask to control the TV.

## Cleanup (not started)

The cleanup changes system packages, so it waits until the launcher works and you approve each change.

```sh
sh supports.sh <TV_IP>     # read-only: model, RAM, home screens, inputs
sh candidates.sh <TV_IP>   # read-only: every app with never/keep/safe/review + reason
```

Rules we will follow:

- One small batch at a time, then check the TV and reboot.
- `pm disable-user --user 0 <package>`, **never** uninstall a system app.
- Ask before every package. Keep `cleanup-undo-YYYY-MM-DD.sh` with every change.
- Never disable: Play services/framework, Play Store, Settings, System UI, setup apps, keyboard, Bluetooth, package installer, providers, HDMI/TV input and tuner framework, anything `PERSISTENT`, or the app that saved your Wi-Fi.
- If unsure, leave it on.

Undo any single package:

```sh
adb shell pm enable <package>
```

## Google TV home

Do **not** disable it as part of cleanup. First measure how much it costs when idle:

```sh
adb shell dumpsys meminfo com.google.android.apps.tv.launcherx
adb shell dumpsys meminfo | grep -E "Free RAM|Used RAM|Lost RAM"
adb shell dumpsys activity processes | grep -A3 tv.launcherx
```

Then choose, with real numbers:

1. **Leave it enabled and cached.** No boot risk; Android reclaims it under pressure. Recommended unless the numbers are bad.
2. **Force-stop it after boot.** `adb shell am force-stop com.google.android.apps.tv.launcherx`. Frees it until something restarts it; needs adb after each boot.
3. **Disable it and re-enable over adb when needed.** This is the option that caused boot loops and factory resets on some Google TVs. Only with a recovery path tested.

The launcher's Settings will have a **Google TV home** row that opens it only when it is installed and enabled. Hold Back on the new home screen is the existing shortcut.

## Recovery

- **Home opens the wrong thing:** Settings → Accessibility → **Home button** off. Or uninstall this launcher.
- **Uninstall the launcher:** `adb uninstall com.ansub.tvhome`.
- **Restore the stock home and remove this one:** `sh undo.sh <TV_IP>`.
- **A disabled package broke something:** `adb shell pm enable <package>`; if the TV won't boot, connect in the first seconds after power-on, `adb wait-for-device`, then re-enable packages from `pm list packages -d`.
- **Home role stuck:** `adb shell cmd package set-home-activity com.google.android.apps.tv.launcherx/.home.HomeActivity` then reboot. (On some TVs the setup app is the fallback; the TV Detox README covers that.)
- **Boot loop after disabling Google TV's home:** re-enable `com.google.android.apps.tv.launcherx` and `com.google.android.tungsten.setupwraith` from adb as soon as the TV is reachable. A factory reset is the last resort.
- **Accessibility service loop:** `adb shell settings put secure accessibility_enabled 0`; clear `enabled_accessibility_services` if needed.
- **Wireless debugging left on:** turn it off in Developer options when done.

## Emulator

- Apple Silicon needs **ARM64** images. Android TV ARM64 exists for **API 31, 33, 34 and 36**; there is **no Android 11 (API 30) ARM image**. API 33 or 34 is the closest test.
- All emulator files can live under `.tools/` (`ANDROID_AVD_HOME`, `ANDROID_USER_HOME`, `ANDROID_EMULATOR_HOME`), so deleting `.tools/` removes the emulator, system image and AVDs.
- The emulator can prove the UI launches, focus works, settings persist and there are no crashes. It cannot prove the ORCA 2K's real GPU frame times or RAM. Those come from the TV.
- Emulator download is roughly 1.6–2 GB; ask before installing.

## Current design decisions

- Dock layout with a frosted glass panel, pre-rendered per wallpaper.
- Clock top-left. **Show date** toggle in Settings (default off).
- **App labels** toggle in Settings: icons + names, or icons only (default names).
- Top-right: Inputs, Apps, Settings, network status.
- Six full-quality Unsplash photos with credits; Manrope font (OFL); free-licence brand marks.
- No system animation scale changes without your choice.

## Files worth knowing

| Path | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Rules and state for the next AI session |
| [PROGRESS.md](PROGRESS.md) | What is done, verified and next |
| [docs/restyle-plan.md](docs/restyle-plan.md) | Design mapping and limits |
| [mockups/](mockups/) | Mockups, credits, generator |
| [docs/debloat.md](docs/debloat.md) | Upstream cleanup rules |
| [src/com/ansub/tvhome/](src/com/ansub/tvhome/) | The launcher source |
| `build.sh`, `install.sh`, `undo.sh` | Build and TV lifecycle |
