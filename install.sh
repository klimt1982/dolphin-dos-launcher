#!/usr/bin/env bash
set -euo pipefail
base_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
settings_dir="${XDG_CONFIG_HOME:-${HOME}/.config}/dolphin-dos-launcher"
settings_file="$settings_dir/settings.json"
current_language="$(python3 - "$settings_file" <<'PY'
import json, pathlib, sys
try:
    selected = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')).get('language', 'auto')
except (OSError, ValueError, AttributeError):
    selected = 'auto'
print(selected if selected in ('auto', 'es', 'en') else 'auto')
PY
)"
language="$current_language"
if [[ $# -gt 0 ]]; then
  if [[ $# -ne 2 || "$1" != "--language" || ! "$2" =~ ^(auto|es|en)$ ]]; then
    printf 'Uso: ./install.sh [--language auto|es|en]\n' >&2
    exit 2
  fi
  language="$2"
elif [[ -t 0 ]]; then
  printf 'Idioma / Language (actual: %s)\n' "$current_language"
  printf '  1) Automático / System   2) Español   3) English\n'
  read -r -p 'Elegí 1, 2 o 3 [Enter conserva el actual]: ' choice
  case "$choice" in
    '') ;;
    1) language=auto ;;
    2) language=es ;;
    3) language=en ;;
    *) printf 'Opción no válida. No se instaló nada.\n' >&2; exit 2 ;;
  esac
fi
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
mkdir -p "$bin_dir" "$menu_dir" "$icon_dir" "$app_dir" "$settings_dir"
install -m 755 "$base_dir/dos_game_launcher.py" "$bin_dir/dolphin-dos-launcher"
install -m 644 "$base_dir/dolphin-dos-launcher.svg" "$bin_dir/dolphin-dos-launcher.svg"
install -m 644 "$base_dir/dolphin-dos-launcher.svg" "$icon_dir/dolphin-dos-launcher.svg"
python3 - "$base_dir" "$menu_dir" "$app_dir" "$bin_dir" "$settings_file" "$language" <<'PYINSTALL'
import json, os, pathlib, sys
base, menu, apps, binary = map(pathlib.Path, sys.argv[1:5])
settings = pathlib.Path(sys.argv[5])
language = sys.argv[6]

def desktop(source, target, executable=None, icon=None):
    lines = source.read_text(encoding='utf-8').splitlines()
    spanish = {}
    group = ''
    for line in lines:
        if line.startswith('[') and line.endswith(']'):
            group = line
        elif '[es]=' in line:
            key, value = line.split('[es]=', 1)
            spanish[group, key] = value
    output = []
    group = ''
    for line in lines:
        if line.startswith('[') and line.endswith(']'):
            group = line
        if language != 'auto' and '[es]=' in line:
            continue
        if language == 'es' and '=' in line:
            key, _, value = line.partition('=')
            if (group, key) in spanish:
                line = key + '=' + spanish[group, key]
        output.append(line)
    content = '\n'.join(output) + '\n'
    if executable is not None:
        # Quote the fixed program path in Desktop Entry syntax; %f remains separate.
        content = content.replace('@EXECUTABLE@', '"' + str(executable).replace('"', r'\"') + '"')
    if icon is not None:
        content = content.replace('@ICON@', str(icon))
    target.write_text(content, encoding='utf-8')

desktop(base / 'dolphin-dos-launcher.desktop', menu / 'dolphin-dos-launcher.desktop',
        binary / 'dolphin-dos-launcher')
(menu / 'dolphin-dos-launcher.desktop').chmod(0o755)
desktop(base / 'dolphin-dos-launcher-app.desktop', apps / 'io.github.klimt1982.dolphin-dos-launcher.desktop',
        binary / 'dolphin-dos-launcher',
        apps.parent / 'icons/hicolor/scalable/apps/dolphin-dos-launcher.svg')
(apps / 'dolphin-dos-launcher.desktop').unlink(missing_ok=True)
try:
    value = json.loads(settings.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('settings.json no es un objeto JSON')
except FileNotFoundError:
    value = {}
value['language'] = language
temporary = settings.with_name(settings.name + '.tmp')
try:
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, settings)
finally:
    temporary.unlink(missing_ok=True)
PYINSTALL
printf 'Instalado (idioma: %s). Reiniciá Dolphin para actualizar el menú contextual.\n' "$language"
