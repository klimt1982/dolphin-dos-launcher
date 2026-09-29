#!/usr/bin/env python3
"""Per-game DOSBox Staging launcher for KDE Dolphin.

Copyright (C) 2026 Lucas Quiroga
SPDX-License-Identifier: GPL-3.0-or-later
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtCore import QLocale
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QDialogButtonBox, QFileDialog, QFormLayout,
                             QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)
from urllib.parse import unquote, urlparse

APP = 'dolphin-dos-launcher'
VERSION = '1.1.0'
EXTENSIONS = {'.exe', '.com', '.bat'}
IMAGE_EXTENSIONS = {'.iso', '.cue', '.mds', '.bin'}
MACHINES = {'Predeterminada': '', 'VGA': 'vgaonly', 'EGA': 'ega', 'CGA': 'cga', 'Hércules': 'hercules'}
SOUND = {'Predeterminado': '', 'Sound Blaster 16': 'sb16', 'Sound Blaster Pro 2': 'sbpro2', 'AdLib': 'none'}
SHADERS = {'Predeterminado (CRT adaptable)': '', 'Scanlines marcadas': 'crt-auto-arcade', 'Sin scanlines (nítido)': 'sharp'}
MEMORY = {'Predeterminada (16 MB)': '', '8 MB': '8', '16 MB': '16', '32 MB': '32', '64 MB': '64'}
CD_EXTENSIONS = {'.iso', '.cue', '.mds'}
CPU_TYPES = {'Automática (recomendada)': '', '386': '386', '386 rápido': '386_fast', '386 prefetch (compatibilidad)': '386_prefetch', '486': '486', 'Pentium': 'pentium', 'Pentium MMX': 'pentium_mmx'}
MOUSE_MODES = {'Normal (clic para capturar)': '', 'Capturar al iniciar': 'onstart', 'Controlador alternativo (no-tsr)': 'no-tsr', 'Alternativo y capturar al iniciar': 'no-tsr-onstart', 'Cargar MOUSE.COM antes del juego': 'load'}

EN = {
    'Abrir juego DOS': 'Open DOS game',
    'Montar CD en DOSBox Staging': 'Mount CD in DOSBox Staging',
    'Predeterminada': 'Default', 'Predeterminado': 'Default',
    'Hércules': 'Hercules',
    'Predeterminada (16 MB)': 'Default (16 MB)',
    'Predeterminado (CRT adaptable)': 'Default (adaptive CRT)',
    'Automática (recomendada)': 'Automatic (recommended)',
    '386 rápido': '386 fast', '386 prefetch (compatibilidad)': '386 prefetch (compatibility)',
    'Normal (clic para capturar)': 'Normal (click to capture)',
    'Capturar al iniciar': 'Capture on startup',
    'Controlador alternativo (no-tsr)': 'Alternative driver (no-tsr)',
    'Alternativo y capturar al iniciar': 'Alternative and capture on startup',
    'Cargar MOUSE.COM antes del juego': 'Load MOUSE.COM before the game',
    'Scanlines marcadas': 'Pronounced scanlines',
    'Sin scanlines (nítido)': 'No scanlines (sharp)',
    'Gráficos:': 'Graphics:', 'Ciclos CPU:': 'CPU cycles:',
    'Imagen de CD (D:):': 'CD image (D:):', 'Imagen:': 'Video:',
    'Memoria RAM:': 'Memory:', 'Mouse:': 'Mouse:',
    'Tipo de CPU:': 'CPU type:', 'Carpeta montada como C:': 'Folder mounted as C:',
    'Carpeta C:': 'C: folder:', 'Pantalla completa': 'Fullscreen',
    'Examinar…': 'Browse…', 'Cancelar': 'Cancel',
    'Guardar e iniciar': 'Save and launch',
    'Montar y abrir DOSBox': 'Mount and open DOSBox',
    'Dejar DOSBox abierto al salir del juego (diagnóstico)': 'Keep DOSBox open when the game exits (diagnostics)',
    'Los ajustes se guardan para este ejecutable al iniciar. Ctrl+F10 libera o captura el mouse en DOSBox.':
        'Settings are saved for this executable when launching. Ctrl+F10 releases or captures the mouse in DOSBox.',
    'El disco se montará como D:. Elegí una carpeta existente donde instalar el juego como C:.':
        'The disc will be mounted as D:. Choose an existing folder for installing the game as C:.',
    'DOSBox abrirá D:. Escribí DIR y ejecutá INSTALL o SETUP si corresponde.':
        'DOSBox will open D:. Type DIR, then run INSTALL or SETUP if appropriate.',
    'Elegir carpeta C:': 'Choose C: folder', 'Elegir imagen de CD': 'Choose CD image',
    'Imágenes de CD': 'CD images',
    'auto, max o 100–1000000': 'auto, max, or 100–1000000',
    'Ciclos CPU': 'CPU cycles', 'Imagen de CD': 'CD image',
    'No se pudo montar el CD': 'Could not mount the CD',
    'No se pudo abrir el juego': 'Could not launch the game',
    'Usá auto, max o un número entre 100 y 1000000.':
        'Use auto, max, or a number between 100 and 1000000.',
    'Elegí una imagen .ISO, .CUE o .MDS existente.':
        'Choose an existing .ISO, .CUE, or .MDS image.',
    'No se encontró DOSBox Staging.': 'DOSBox Staging was not found.',
    'No se encontró DOSBox Staging. Instalalo antes de iniciar el juego.':
        'DOSBox Staging was not found. Install it before launching the game.',
    'No se encontró DOSBox Staging. Instalalo y verificá que el comando dosbox-staging (o dosbox de Staging) esté disponible.':
        'DOSBox Staging was not found. Install it and make sure dosbox-staging (or the Staging dosbox command) is available.',
    'Seleccioná un archivo local .EXE, .COM, .BAT, .ISO, .CUE, .MDS o .BIN.':
        'Select a local .EXE, .COM, .BAT, .ISO, .CUE, .MDS, or .BIN file.',
    'Solo se admiten archivos locales.': 'Only local files are supported.',
    'La carpeta C: debe contener el ejecutable del juego.':
        'The C: folder must contain the game executable.',
    'Elegí una carpeta existente con permiso de escritura para C:.':
        'Choose an existing writable folder for C:.',
    'La imagen de CD debe ser un archivo ISO, CUE o MDS existente.':
        'The CD image must be an existing ISO, CUE, or MDS file.',
    'Para una imagen BIN elegí su archivo CUE correspondiente. No se encontró uno con el mismo nombre.':
        'For a BIN image, choose its matching CUE file. No CUE with the same name was found.',
    'El nombre del archivo de CD contiene acentos; renombrá la imagen y sus referencias CUE/BIN.':
        'The CD filename contains non-ASCII characters; rename the image and its CUE/BIN references.',
    'El modo de montaje manual requiere un ejecutable con nombre DOS 8.3 (sin espacios ni acentos).':
        'Manual mounting requires an executable with a DOS 8.3 filename (no spaces or accents).',
}


def language_setting():
    settings = config_path().with_name('settings.json')
    try:
        value = json.loads(settings.read_text(encoding='utf-8')).get('language', 'auto')
        return value if value in ('auto', 'es', 'en') else 'auto'
    except (OSError, ValueError, AttributeError):
        return 'auto'


def language():
    selected = language_setting()
    if selected == 'auto':
        return 'es' if QLocale.system().name().lower().startswith('es') else 'en'
    return selected


def _(value):
    return EN.get(value, value) if language() == 'en' else value


def ascii_mount_path(directory):
    """Provide an ASCII-only alias for DOS mount commands."""
    raw = str(directory)
    if raw.isascii():
        return directory
    cache = Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / APP / 'mounts'
    if not str(cache).isascii():
        raise ValueError('La carpeta de caché contiene caracteres no ASCII.')
    cache.mkdir(parents=True, exist_ok=True)
    alias = cache / ('game-' + hashlib.sha256(os.fsencode(raw)).hexdigest()[:20])
    if alias.is_symlink():
        if os.readlink(alias) != raw:
            raise ValueError(f'La ruta auxiliar ya existe con otro destino: {alias}')
    elif alias.exists():
        raise ValueError(f'La ruta auxiliar ya existe y no es un enlace: {alias}')
    else:
        alias.symlink_to(directory, target_is_directory=True)
    return alias


def config_path():
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / APP / 'profiles.json'


def parse_path(raw):
    if raw.startswith('file:'):
        uri = urlparse(raw)
        if uri.scheme != 'file' or uri.netloc not in ('', 'localhost'):
            raise ValueError('Solo se admiten archivos locales.')
        raw = unquote(uri.path)
    path = Path(raw).expanduser().resolve()
    if not path.is_file() or path.suffix.lower() not in EXTENSIONS | IMAGE_EXTENSIONS:
        raise ValueError('Seleccioná un archivo local .EXE, .COM, .BAT, .ISO, .CUE, .MDS o .BIN.')
    return path


def cd_image(path):
    if path.suffix.lower() != '.bin':
        return path
    matches = [candidate for candidate in path.parent.iterdir()
               if candidate.is_file() and candidate.suffix.lower() == '.cue'
               and candidate.stem.casefold() == path.stem.casefold()]
    if len(matches) != 1:
        raise ValueError('Para una imagen BIN elegí su archivo CUE correspondiente. No se encontró uno con el mismo nombre.')
    return matches[0]


def cd_mount_path(image):
    if not image.is_file() or image.suffix.lower() not in CD_EXTENSIONS:
        raise ValueError('La imagen de CD debe ser un archivo ISO, CUE o MDS existente.')
    parent = ascii_mount_path(image.parent)
    if not image.name.isascii():
        raise ValueError('El nombre del archivo de CD contiene acentos; renombrá la imagen y sus referencias CUE/BIN.')
    mount_image = parent / image.name
    if any(char in str(mount_image) for char in ('"', '\n', '\r')):
        raise ValueError('La ruta del CD contiene comillas o saltos de línea no admitidos.')
    return mount_image


def read_profiles():
    file = config_path()
    if not file.exists():
        return {}
    try:
        profiles = json.loads(file.read_text(encoding='utf-8'))
        if isinstance(profiles, dict):
            return profiles
    except (OSError, ValueError):
        pass
    raise ValueError(f'No se pudo leer {file}. Revisá el JSON; no se sobrescribirá.')


def save_profiles(profiles):
    file = config_path()
    file.parent.mkdir(parents=True, exist_ok=True)
    tmp = file.with_name(file.name + '.tmp')
    try:
        with tmp.open('w', encoding='utf-8') as stream:
            json.dump(profiles, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, file)
    finally:
        tmp.unlink(missing_ok=True)


def dosbox_binary():
    # Distributions may name the Staging binary 'dosbox' or 'dosbox-staging'.
    for name in ('dosbox-staging', 'dosbox'):
        found = shutil.which(name)
        if found:
            if name == 'dosbox':
                try:
                    result = subprocess.run([found, '--version'], capture_output=True, text=True, timeout=3)
                    if 'staging' not in (result.stdout + result.stderr).lower():
                        continue
                except (OSError, subprocess.TimeoutExpired):
                    continue
            return found
    return None


def command(binary, path, profile):
    args = [binary]
    if profile.get('fullscreen'):
        args.append('--fullscreen')
    if profile.get('machine') in set(MACHINES.values()) - {''}:
        args.extend(['--machine', profile['machine']])
    cpu_type = profile.get('cpu_type', '')
    if cpu_type in set(CPU_TYPES.values()) - {''}:
        args.extend(['--set', f'cputype={cpu_type}'])
        if cpu_type == '386_prefetch':
            args.extend(['--set', 'core=normal'])
    cycles = profile.get('cycles', '')
    if cycles == 'max' or cycles == 'auto' or (isinstance(cycles, str) and cycles.isdigit() and 100 <= int(cycles) <= 1000000):
        args.extend(['--set', f'cpu_cycles={cycles}'])
    if profile.get('sound') in set(SOUND.values()) - {''}:
        args.extend(['--set', f'sbtype={profile["sound"]}'])
    if profile.get('shader') in set(SHADERS.values()) - {''}:
        args.extend(['--set', f'shader={profile["shader"]}'])
    if profile.get('memory') in set(MEMORY.values()) - {''}:
        args.extend(['--set', f'memsize={profile["memory"]}'])
    mouse = profile.get('mouse', '')
    if mouse in ('onstart', 'no-tsr-onstart'):
        args.extend(['--set', 'mouse_capture=onstart'])
    if mouse == 'load':
        args.extend(['--set', 'builtin_dos_mouse_driver=off'])
    if mouse in ('no-tsr', 'no-tsr-onstart'):
        args.extend(['--set', 'builtin_dos_mouse_driver=no-tsr'])
    cd = profile.get('cd', '')
    if cd:
        disc = cd_mount_path(Path(cd).expanduser().resolve())
        args.extend(['-c', f'mount D "{disc}"'])
    root_dir = Path(profile.get('root_dir') or path.parent).expanduser().resolve()
    if not root_dir.is_dir() or path.parent != root_dir and root_dir not in path.parents:
        raise ValueError('La carpeta C: debe contener el ejecutable del juego.')
    mount_root = ascii_mount_path(root_dir)
    if profile.get('keep_open') or mouse == 'load' or root_dir != path.parent or mount_root != root_dir:
        # DOS commands permit an explicit C: root and execution from the game's own directory.
        relative = path.parent.relative_to(root_dir)
        if not str(relative).isascii():
            raise ValueError('Una subcarpeta interna contiene acentos; elegí esa subcarpeta como C:.')
        for part in (str(mount_root), str(relative), path.name):
            if any(char in part for char in ('"', '\n', '\r')):
                raise ValueError('La ruta del juego contiene comillas o saltos de línea no admitidos por el modo diagnóstico.')
        args.extend(['-c', f'mount C "{mount_root}"', '-c', 'C:'])
        if relative != Path('.'):
            args.extend(['-c', f'cd "{str(relative).replace(os.sep, chr(92))}"'])
        if mouse == 'load':
            args.extend(['-c', 'MOUSE'])
        if not re.fullmatch(r'[A-Za-z0-9_~-]{1,8}\.(?:EXE|COM|BAT)', path.name, re.IGNORECASE):
            raise ValueError('El modo de montaje manual requiere un ejecutable con nombre DOS 8.3 (sin espacios ni acentos).')
        args.extend(['-c', path.name])
        if not profile.get('keep_open'):
            args.extend(['-c', 'EXIT'])
    else:
        args.append(str(path))
    return args


def media_command(binary, image, profile):
    install_dir = Path(profile.get('root_dir', '')).expanduser().resolve()
    if not install_dir.is_dir() or not os.access(install_dir, os.W_OK):
        raise ValueError('Elegí una carpeta existente con permiso de escritura para C:.')
    root = ascii_mount_path(install_dir)
    disc = cd_mount_path(cd_image(image))
    if any(char in str(root) for char in ('"', '\n', '\r')):
        raise ValueError('La ruta de C: contiene comillas o saltos de línea no admitidos.')
    args = [binary]
    if profile.get('fullscreen'):
        args.append('--fullscreen')
    args.extend(['-c', f'mount C "{root}"', '-c', f'mount D "{disc}"', '-c', 'D:'])
    return args


def launch(path, profile):
    binary = dosbox_binary()
    if not binary:
        raise RuntimeError('No se encontró DOSBox Staging. Instalalo y verificá que el comando dosbox-staging (o dosbox de Staging) esté disponible.')
    args = media_command(binary, path, profile) if path.suffix.lower() in IMAGE_EXTENSIONS else command(binary, path, profile)
    subprocess.Popen(args, cwd=str(path.parent), start_new_session=True, stdin=subprocess.DEVNULL)


_qt_application = None


def qt_app():
    global _qt_application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
        app.setApplicationName('dolphin-dos-launcher')
        app.setApplicationDisplayName(_('Abrir juego DOS'))
        QGuiApplication.setDesktopFileName('io.github.klimt1982.dolphin-dos-launcher')
        icon = Path(__file__).with_name('dolphin-dos-launcher.svg')
        if icon.is_file():
            app.setWindowIcon(QIcon(str(icon)))
    _qt_application = app
    return app


def show_error(title, message):
    try:
        qt_app()
        QMessageBox.critical(None, _(title), _(message))
    except Exception:
        print(f'{title}: {message}', file=sys.stderr)


def combo(options, saved):
    widget = QComboBox()
    for label, value in options.items():
        widget.addItem(_(label), value)
    index = widget.findData(saved)
    widget.setCurrentIndex(max(index, 0))
    return widget


def path_field(value, directory=False):
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    field = QLineEdit(str(value))
    button = QPushButton(_('Examinar…'))
    def choose():
        if directory:
            selected = QFileDialog.getExistingDirectory(row, _('Elegir carpeta C:'), field.text() or str(Path.home()))
        else:
            selected, _filter = QFileDialog.getOpenFileName(row, _('Elegir imagen de CD'), str(Path.home()),
                                                       _('Imágenes de CD') + ' (*.iso *.ISO *.cue *.CUE *.mds *.MDS)')
        if selected:
            field.setText(selected)
    button.clicked.connect(choose)
    layout.addWidget(field, 1)
    layout.addWidget(button)
    return row, field


def dialog_shell(title, filename, parent_dir):
    dialog = QDialog()
    dialog.setWindowTitle(_(title))
    dialog.setMinimumWidth(570)
    body = QWidget()
    layout = QVBoxLayout(body)
    heading = QLabel(filename)
    font = heading.font()
    font.setPointSize(font.pointSize() + 3)
    font.setBold(True)
    heading.setFont(font)
    layout.addWidget(heading)
    where = QLabel(str(parent_dir))
    where.setWordWrap(True)
    layout.addWidget(where)
    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
    layout.addLayout(form)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setWidget(body)
    outer = QVBoxLayout(dialog)
    outer.addWidget(scroll)
    dialog.resize(650, 550)
    return dialog, layout, form, outer


def configure_media(path, profiles):
    qt_app()
    profile = profiles.get(str(path), {})
    if not isinstance(profile, dict):
        profile = {}
    dialog, layout, form, outer = dialog_shell('Montar CD en DOSBox Staging', path.name, path.parent)
    note = QLabel(_('El disco se montará como D:. Elegí una carpeta existente donde instalar el juego como C:.'))
    note.setWordWrap(True)
    layout.addWidget(note)
    row, install_dir = path_field(profile.get('root_dir') or path.parent, directory=True)
    form.addRow(_('Carpeta C:'), row)
    fullscreen = QCheckBox(_('Pantalla completa'))
    fullscreen.setChecked(bool(profile.get('fullscreen', False)))
    layout.addWidget(fullscreen)
    note2 = QLabel(_('DOSBox abrirá D:. Escribí DIR y ejecutá INSTALL o SETUP si corresponde.'))
    note2.setWordWrap(True)
    layout.addWidget(note2)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
    buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(_('Cancelar'))
    start = buttons.addButton(_('Montar y abrir DOSBox'), QDialogButtonBox.ButtonRole.AcceptRole)
    buttons.rejected.connect(dialog.reject)
    outer.addWidget(buttons)
    def run():
        selected = {'root_dir': install_dir.text().strip(), 'fullscreen': fullscreen.isChecked()}
        try:
            binary = dosbox_binary()
            if not binary:
                raise RuntimeError('No se encontró DOSBox Staging.')
            media_command(binary, path, selected)
            launch(path, selected)
            profiles[str(path)] = selected
            save_profiles(profiles)
        except (OSError, RuntimeError, ValueError) as exc:
            QMessageBox.critical(dialog, _('No se pudo montar el CD'), _(str(exc)))
            return
        dialog.accept()
    start.clicked.connect(run)
    dialog.exec()


def configure(path, profiles):
    qt_app()
    profile = profiles.get(str(path), {})
    if not isinstance(profile, dict):
        profile = {}
    dialog, layout, form, outer = dialog_shell('Abrir juego DOS', path.name, path.parent)
    fullscreen = QCheckBox(_('Pantalla completa'))
    fullscreen.setChecked(bool(profile.get('fullscreen', False)))
    layout.addWidget(fullscreen)
    machine = combo(MACHINES, profile.get('machine', ''))
    sound = combo(SOUND, profile.get('sound', ''))
    cycles = QLineEdit(str(profile.get('cycles', '')))
    cycles.setPlaceholderText(_('auto, max o 100–1000000'))
    shader = combo(SHADERS, profile.get('shader', ''))
    memory = combo(MEMORY, profile.get('memory', ''))
    mouse = combo(MOUSE_MODES, profile.get('mouse', ''))
    cpu_type = combo(CPU_TYPES, profile.get('cpu_type', ''))
    cd_row, cd = path_field(profile.get('cd', ''))
    root_row, root_dir = path_field(profile.get('root_dir') or path.parent, directory=True)
    form.addRow(_('Gráficos:'), machine)
    form.addRow('Sound Blaster:', sound)
    form.addRow(_('Ciclos CPU:'), cycles)
    form.addRow(_('Imagen de CD (D:):'), cd_row)
    form.addRow(_('Imagen:'), shader)
    form.addRow(_('Memoria RAM:'), memory)
    form.addRow(_('Mouse:'), mouse)
    form.addRow(_('Tipo de CPU:'), cpu_type)
    form.addRow(_('Carpeta montada como C:'), root_row)
    keep_open = QCheckBox(_('Dejar DOSBox abierto al salir del juego (diagnóstico)'))
    keep_open.setChecked(bool(profile.get('keep_open', False)))
    layout.addWidget(keep_open)
    note = QLabel(_('Los ajustes se guardan para este ejecutable al iniciar. Ctrl+F10 libera o captura el mouse en DOSBox.'))
    note.setWordWrap(True)
    layout.addWidget(note)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
    buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(_('Cancelar'))
    start = buttons.addButton(_('Guardar e iniciar'), QDialogButtonBox.ButtonRole.AcceptRole)
    buttons.rejected.connect(dialog.reject)
    outer.addWidget(buttons)
    def run():
        value = cycles.text().strip().lower()
        if value and value not in ('auto', 'max') and not (value.isdigit() and 100 <= int(value) <= 1000000):
            QMessageBox.critical(dialog, _('Ciclos CPU'), _('Usá auto, max o un número entre 100 y 1000000.'))
            return
        cd_value = cd.text().strip()
        if cd_value:
            image = Path(cd_value).expanduser().resolve()
            if not image.is_file() or image.suffix.lower() not in CD_EXTENSIONS:
                QMessageBox.critical(dialog, _('Imagen de CD'), _('Elegí una imagen .ISO, .CUE o .MDS existente.'))
                return
            cd_value = str(image)
        selected = {'fullscreen': fullscreen.isChecked(), 'machine': machine.currentData(),
                    'sound': sound.currentData(), 'cycles': value, 'cd': cd_value,
                    'shader': shader.currentData(), 'memory': memory.currentData(),
                    'mouse': mouse.currentData(), 'cpu_type': cpu_type.currentData(),
                    'keep_open': keep_open.isChecked(), 'root_dir': root_dir.text().strip()}
        try:
            binary = dosbox_binary()
            if not binary:
                raise RuntimeError('No se encontró DOSBox Staging. Instalalo antes de iniciar el juego.')
            command(binary, path, selected)
            launch(path, selected)
            profiles[str(path)] = selected
            save_profiles(profiles)
        except (OSError, RuntimeError, ValueError) as exc:
            QMessageBox.critical(dialog, _('No se pudo abrir el juego'), _(str(exc)))
            return
        dialog.accept()
    start.clicked.connect(run)
    dialog.exec()


def main():
    parser = argparse.ArgumentParser(description='Abrir juegos DOS desde Dolphin')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('--quick', action='store_true', help='Iniciar con la configuración guardada')
    parser.add_argument('file', help='Archivo DOS local .EXE, .COM o .BAT')
    args = parser.parse_args()
    try:
        path = parse_path(args.file)
        profiles = read_profiles()
        if args.quick and str(path) in profiles:
            launch(path, profiles[str(path)])
        elif path.suffix.lower() in IMAGE_EXTENSIONS:
            configure_media(path, profiles)
        else:
            configure(path, profiles)
    except (ValueError, OSError, RuntimeError) as exc:
        show_error('Abrir juego DOS', str(exc))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
