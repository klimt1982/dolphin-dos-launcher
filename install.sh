#!/usr/bin/env bash
set -euo pipefail
base_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
if ! python3 -c 'from PyQt6.QtWidgets import QApplication' >/dev/null 2>&1; then
  printf 'Falta PyQt6 para Python. En Kubuntu: sudo apt install python3-pyqt6 qt6-wayland\n' >&2
  exit 1
fi
if ! command -v dosbox-staging >/dev/null 2>&1 && ! (command -v dosbox >/dev/null 2>&1 && dosbox --version 2>&1 | grep -qi staging); then
  printf 'Falta DOSBox Staging. Instalalo antes de continuar.\n' >&2
  exit 1
fi
bin_dir="${HOME}/.local/bin"
menu_dir="${XDG_DATA_HOME:-${HOME}/.local/share}/kio/servicemenus"
data_dir="${XDG_DATA_HOME:-${HOME}/.local/share}"
icon_dir="$data_dir/icons/hicolor/scalable/apps"
app_dir="$data_dir/applications"
mkdir -p "$bin_dir" "$menu_dir" "$icon_dir" "$app_dir"
install -m 755 "$base_dir/dos_game_launcher.py" "$bin_dir/dolphin-dos-launcher"
install -m 644 "$base_dir/dolphin-dos-launcher.svg" "$bin_dir/dolphin-dos-launcher.svg"
install -m 644 "$base_dir/dolphin-dos-launcher.svg" "$icon_dir/dolphin-dos-launcher.svg"
install -m 644 "$base_dir/dolphin-dos-launcher-app.desktop" "$app_dir/dolphin-dos-launcher.desktop"
python3 - "$base_dir/dolphin-dos-launcher.desktop" "$menu_dir/dolphin-dos-launcher.desktop" "$bin_dir/dolphin-dos-launcher" <<'PYINSTALL'
import pathlib, sys
source, target, executable = map(pathlib.Path, sys.argv[1:])
# Desktop Entry Exec escaping: quote the fixed executable path; %f stays separate.
value = source.read_text(encoding='utf-8').replace('@EXECUTABLE@', '"' + str(executable).replace('"', r'\"') + '"')
target.write_text(value, encoding='utf-8')
target.chmod(0o755)
PYINSTALL
printf 'Instalado. Abrí Dolphin y hacé clic derecho en un archivo DOS .EXE, .COM o .BAT, o una imagen de CD .ISO, .CUE, .MDS o .BIN.\n'
