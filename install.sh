#!/usr/bin/env bash
set -euo pipefail
base_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
if ! python3 -c 'import tkinter' >/dev/null 2>&1; then
  printf 'Falta Tkinter para Python. En Kubuntu: sudo apt install python3-tk\n' >&2
  exit 1
fi
if ! command -v dosbox-staging >/dev/null 2>&1 && ! (command -v dosbox >/dev/null 2>&1 && dosbox --version 2>&1 | grep -qi staging); then
  printf 'Falta DOSBox Staging. Instalalo antes de continuar.\n' >&2
  exit 1
fi
bin_dir="${HOME}/.local/bin"
menu_dir="${XDG_DATA_HOME:-${HOME}/.local/share}/kio/servicemenus"
mkdir -p "$bin_dir" "$menu_dir"
install -m 755 "$base_dir/dos_game_launcher.py" "$bin_dir/dolphin-dos-launcher"
python3 - "$base_dir/dolphin-dos-launcher.desktop" "$menu_dir/dolphin-dos-launcher.desktop" "$bin_dir/dolphin-dos-launcher" <<'PYINSTALL'
import pathlib, sys
source, target, executable = map(pathlib.Path, sys.argv[1:])
# Desktop Entry Exec escaping: quote the fixed executable path; %f stays separate.
value = source.read_text(encoding='utf-8').replace('@EXECUTABLE@', '"' + str(executable).replace('"', r'\"') + '"')
target.write_text(value, encoding='utf-8')
target.chmod(0o755)
PYINSTALL
printf 'Instalado. Abrí Dolphin y hacé clic derecho en un archivo DOS .EXE, .COM o .BAT.\n'
