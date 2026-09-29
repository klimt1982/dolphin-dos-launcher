# Dolphin DOS Launcher

[Documentación en español](README.md)

A KDE Dolphin context menu for launching DOS games with **DOSBox Staging**. Right-click a DOS `.EXE`, `.COM`, or `.BAT` file to configure and launch it, or use its saved per-game profile. You can also mount `.ISO`, `.CUE`, `.MDS`, and `.BIN` CD images and run their DOS installer manually. The launcher cannot infer which program on a CD should be run.

**Version 1.1.1.** Tested on Kubuntu with Plasma Wayland and DOSBox Staging 0.83.0. The installer offers automatic, Spanish, and English UI language choices. This project is independent of KDE and DOSBox Staging.

## Requirements

- KDE Dolphin with KIO service menu support.
- **DOSBox Staging installed separately**, available as `dosbox-staging` or as `dosbox` whose version output identifies Staging. Classic DOSBox is not supported by this launcher.
- Python 3 and PyQt6. On Kubuntu 26.04: `sudo apt install python3-pyqt6 qt6-wayland`.

This project does not install DOSBox Staging or system packages. Run `dosbox-staging --version` first. If your DOSBox executable lives in `~/.local/bin`, ensure that directory is in the `PATH` inherited by Dolphin.

## Install

Extract the release ZIP and run this from the `dolphin-dos-launcher` directory:

```bash
./install.sh
```

The installer copies the program to `~/.local/bin`, the service menu to `~/.local/share/kio/servicemenus` (honoring `XDG_DATA_HOME`), and the icon and desktop entry to the user's data directories. It does not require `sudo`. Restart Dolphin if it was already running.

The installer asks for **Automatic / System**, **Español**, or **English**. Enter keeps your previous choice on upgrades. Noninteractive installation keeps the previous choice or defaults to Automatic. You can set it explicitly with `./install.sh --language en` (or `es`, `auto`). Run the installer again to update without deleting game profiles.

## Use

Right-click a DOS executable → **Open DOS game** → **Configure and launch / mount CD**. **Launch with saved settings** uses the existing profile, or opens the configuration form when none exists.

Options include fullscreen, graphics, Sound Blaster, CPU cycles and type, memory, CRT/scanlines, mouse capture and driver, CD image on D:, C: folder, and keeping DOSBox open after the game exits. Profiles are stored by absolute path in `~/.config/dolphin-dos-launcher/profiles.json` (or under `XDG_CONFIG_HOME`). Language choice is stored separately in `settings.json` in the same directory and can be changed by rerunning the installer.

For a CD image, choose an existing writable C: folder. DOSBox opens at `D:\>`; use `DIR`, then run `INSTALL` or `SETUP` if present. Prefer the `.CUE` file for BIN tracks and CD audio. Selecting a BIN makes the launcher look for a same-named CUE.

## Uninstall

```bash
./uninstall.sh
```

This removes the installed program files and leaves game profiles in place. Delete `~/.config/dolphin-dos-launcher/profiles.json` yourself only if you no longer need them.

## Known limitations

- ISO, CUE/BIN, and MDS/MDF images mount as D:. Multiple discs and physical CD drives are not supported.
- Windows executables do not run in DOSBox; some CDs contain Windows-only installers.
- Moving a game changes its profile path, so it needs to be configured again.
- A custom C: folder or the keep-open mode requires a DOS 8.3 executable name without spaces or accents. For non-ASCII folder paths the launcher creates a temporary ASCII symlink under the user's cache; it does not rename the game.
- Dolphin may offer the action for unrelated files based on MIME detection; the launcher checks file extensions before opening.
- Some games require mouse support to be enabled in their own SETUP. Inside DOSBox, `Ctrl+F10` toggles mouse capture.

## Source and license

Source code: <https://github.com/klimt1982/dolphin-dos-launcher>. Licensed under **GNU GPL v3 or later**; see [COPYING](COPYING). DOSBox Staging is distributed separately under its own license.
