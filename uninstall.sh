#!/usr/bin/env bash
set -euo pipefail
rm -f -- "${HOME}/.local/bin/dolphin-dos-launcher" "${XDG_DATA_HOME:-${HOME}/.local/share}/kio/servicemenus/dolphin-dos-launcher.desktop"
printf 'Integración desinstalada. Los perfiles permanecen en ~/.config/dolphin-dos-launcher/profiles.json\n'
