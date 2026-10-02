# KDE Store listing draft

**Category:** Dolphin Service Menus  
**Title:** Dolphin DOS Launcher  
**Version:** 1.2.0  
**License:** GPLv3 or later  
**Source:** https://github.com/klimt1982/dolphin-dos-launcher  
**Release:** https://github.com/klimt1982/dolphin-dos-launcher/releases/tag/v1.2.0

## Short description (English)

Launch DOS games from Dolphin's context menu with DOSBox Staging. Configure CPU, memory, graphics, mouse and CD per game.

## Description (English)

Dolphin DOS Launcher adds **Open DOS game** to KDE Dolphin's context menu. Right-click a DOS EXE, COM or BAT to configure and launch it in DOSBox Staging. Save a profile for each game and launch it again with the same settings. You can also mount ISO, CUE/BIN and MDS CD images as D: and run DOS installers manually. The installer offers Automatic, Spanish and English for the menu and configuration window.

**Simplified installation on Kubuntu/Ubuntu amd64:** the DEB includes DOSBox Staging 0.83.0 and APT installs dependencies automatically. Run `sudo apt install ./dolphin-dos-launcher_1.2.0_amd64.deb`. If migrating from the ZIP, run its `./uninstall.sh` first without sudo; profiles are preserved. The DEB follows the system language and retains existing preferences. Tested on Kubuntu 26.04 Wayland.

**For manual ZIP installation, DOSBox Staging must be installed separately.** Python 3 and PyQt6 are also required. Tested on Kubuntu 26.04 with Plasma Wayland and DOSBox Staging 0.83.0. This download includes a Python program, a Dolphin service menu and a per-user installer. Copying only the `.desktop` file is insufficient. No system packages are installed by this project.

## Installation (English)

1. Install DOSBox Staging and verify `dosbox-staging --version`.
2. On Kubuntu, install Qt bindings with `sudo apt install python3-pyqt6 qt6-wayland`.
3. Extract the ZIP, enter `dolphin-dos-launcher`, and run `./install.sh`. Choose the UI language.
4. Restart Dolphin. Run `./uninstall.sh` from the package to remove the integration.

Game profiles are saved in `~/.config/dolphin-dos-launcher/profiles.json` and are preserved on updates and uninstall.

## Descripción breve (español)

Abrí juegos DOS desde el menú contextual de Dolphin con DOSBox Staging. Ajustá CPU, memoria, gráficos, mouse y CD para cada juego.

## Descripción (español)

Dolphin DOS Launcher agrega **Abrir juego DOS** al menú contextual de KDE Dolphin. Seleccioná un ejecutable DOS EXE, COM o BAT para configurarlo e iniciarlo con DOSBox Staging. Guardá un perfil por juego y volvé a abrirlo con los mismos ajustes. También podés montar imágenes ISO, CUE/BIN y MDS como CD en D: para ejecutar instaladores DOS manualmente. El instalador ofrece idioma automático, español e inglés.

**Instalación simplificada en Kubuntu/Ubuntu amd64:** el DEB incluye DOSBox Staging 0.83.0 y APT resuelve dependencias. Ejecutá `sudo apt install ./dolphin-dos-launcher_1.2.0_amd64.deb`. Si migrás desde el ZIP, ejecutá primero su `./uninstall.sh` sin sudo; conserva perfiles. El DEB usa el idioma del sistema y conserva preferencias existentes. Probado en Kubuntu 26.04 Wayland.

**Para instalación manual con ZIP, DOSBox Staging debe instalarse por separado.** También requiere Python 3 y PyQt6. Probado en Kubuntu 26.04 con Plasma Wayland y DOSBox Staging 0.83.0. El ZIP incluye un programa Python, un menú de servicio y un instalador por usuario; copiar solamente el `.desktop` no alcanza.

## Instalación (español)

1. Instalá DOSBox Staging y verificá `dosbox-staging --version`.
2. En Kubuntu, instalá `sudo apt install python3-pyqt6 qt6-wayland`.
3. Descomprimí el ZIP, entrá en `dolphin-dos-launcher` y ejecutá `./install.sh`. Elegí el idioma.
4. Reiniciá Dolphin. Para quitar la integración, ejecutá `./uninstall.sh` desde el paquete.

Los perfiles se conservan al actualizar y desinstalar.

## Assets

- `dolphin-dos-launcher-1.2.0.zip` from the GitHub release.
- Real screenshots of the Dolphin context menu and Qt configuration window. Avoid showing personal filesystem paths in public images.

- `dolphin-dos-launcher_1.2.0_amd64.deb`: optional download for Ubuntu/Kubuntu amd64; keep the ZIP as the service-menu download.
