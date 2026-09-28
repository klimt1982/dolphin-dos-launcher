#!/usr/bin/env bash
set -euo pipefail
rm -f -- "${HOME}/.local/bin/dolphin-dos-launcher" \
  "${HOME}/.local/bin/dolphin-dos-launcher.svg" \
  "${XDG_DATA_HOME:-${HOME}/.local/share}/kio/servicemenus/dolphin-dos-launcher.desktop" \
  "${XDG_DATA_HOME:-${HOME}/.local/share}/icons/hicolor/scalable/apps/dolphin-dos-launcher.svg" \
  "${XDG_DATA_HOME:-${HOME}/.local/share}/applications/dolphin-dos-launcher.desktop"
printf 'Integración desinstalada. Los perfiles permanecen en ~/.config/dolphin-dos-launcher/profiles.json\n'
