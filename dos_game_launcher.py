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
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QDialogButtonBox, QFileDialog, QFormLayout,
                             QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)
from urllib.parse import unquote, urlparse

APP = 'dolphin-dos-launcher'
VERSION = '1.0.0'
EXTENSIONS = {'.exe', '.com', '.bat'}
IMAGE_EXTENSIONS = {'.iso', '.cue', '.mds', '.bin'}
MACHINES = {'Predeterminada': '', 'VGA': 'vgaonly', 'EGA': 'ega', 'CGA': 'cga', 'Hércules': 'hercules'}
SOUND = {'Predeterminado': '', 'Sound Blaster 16': 'sb16', 'Sound Blaster Pro 2': 'sbpro2', 'AdLib': 'none'}
SHADERS = {'Predeterminado (CRT adaptable)': '', 'Scanlines marcadas': 'crt-auto-arcade', 'Sin scanlines (nítido)': 'sharp'}
MEMORY = {'Predeterminada (16 MB)': '', '8 MB': '8', '16 MB': '16', '32 MB': '32', '64 MB': '64'}
CD_EXTENSIONS = {'.iso', '.cue', '.mds'}
CPU_TYPES = {'Automática (recomendada)': '', '386': '386', '386 rápido': '386_fast', '386 prefetch (compatibilidad)': '386_prefetch', '486': '486', 'Pentium': 'pentium', 'Pentium MMX': 'pentium_mmx'}
MOUSE_MODES = {'Normal (clic para capturar)': '', 'Capturar al iniciar': 'onstart', 'Controlador alternativo (no-tsr)': 'no-tsr', 'Alternativo y capturar al iniciar': 'no-tsr-onstart', 'Cargar MOUSE.COM antes del juego': 'load'}


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
        app.setApplicationDisplayName('Abrir juego DOS')
        QGuiApplication.setDesktopFileName('dolphin-dos-launcher')
        icon = Path(__file__).with_name('dolphin-dos-launcher.svg')
        if icon.is_file():
            app.setWindowIcon(QIcon(str(icon)))
    _qt_application = app
    return app


def show_error(title, message):
    try:
        qt_app()
        QMessageBox.critical(None, title, message)
    except Exception:
        print(f'{title}: {message}', file=sys.stderr)


def combo(options, saved):
    widget = QComboBox()
    for label, value in options.items():
        widget.addItem(label, value)
    index = widget.findData(saved)
    widget.setCurrentIndex(max(index, 0))
    return widget


def path_field(value, directory=False):
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    field = QLineEdit(str(value))
    button = QPushButton('Examinar…')
    def choose():
        if directory:
            selected = QFileDialog.getExistingDirectory(row, 'Elegir carpeta C:', field.text() or str(Path.home()))
        else:
            selected, _ = QFileDialog.getOpenFileName(row, 'Elegir imagen de CD', str(Path.home()),
                                                       'Imágenes de CD (*.iso *.ISO *.cue *.CUE *.mds *.MDS)')
        if selected:
            field.setText(selected)
    button.clicked.connect(choose)
    layout.addWidget(field, 1)
    layout.addWidget(button)
    return row, field


def dialog_shell(title, filename, parent_dir):
    dialog = QDialog()
    dialog.setWindowTitle(title)
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
    note = QLabel('El disco se montará como D:. Elegí una carpeta existente donde instalar el juego como C:.')
    note.setWordWrap(True)
    layout.addWidget(note)
    row, install_dir = path_field(profile.get('root_dir') or path.parent, directory=True)
    form.addRow('Carpeta C:', row)
    fullscreen = QCheckBox('Pantalla completa')
    fullscreen.setChecked(bool(profile.get('fullscreen', False)))
    layout.addWidget(fullscreen)
    note2 = QLabel('DOSBox abrirá D:. Escribí DIR y ejecutá INSTALL o SETUP si corresponde.')
    note2.setWordWrap(True)
    layout.addWidget(note2)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
    start = buttons.addButton('Montar y abrir DOSBox', QDialogButtonBox.ButtonRole.AcceptRole)
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
            QMessageBox.critical(dialog, 'No se pudo montar el CD', str(exc))
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
    fullscreen = QCheckBox('Pantalla completa')
    fullscreen.setChecked(bool(profile.get('fullscreen', False)))
    layout.addWidget(fullscreen)
    machine = combo(MACHINES, profile.get('machine', ''))
    sound = combo(SOUND, profile.get('sound', ''))
    cycles = QLineEdit(str(profile.get('cycles', '')))
    cycles.setPlaceholderText('auto, max o 100–1000000')
    shader = combo(SHADERS, profile.get('shader', ''))
    memory = combo(MEMORY, profile.get('memory', ''))
    mouse = combo(MOUSE_MODES, profile.get('mouse', ''))
    cpu_type = combo(CPU_TYPES, profile.get('cpu_type', ''))
    cd_row, cd = path_field(profile.get('cd', ''))
    root_row, root_dir = path_field(profile.get('root_dir') or path.parent, directory=True)
    form.addRow('Gráficos:', machine)
    form.addRow('Sound Blaster:', sound)
    form.addRow('Ciclos CPU:', cycles)
    form.addRow('Imagen de CD (D:):', cd_row)
    form.addRow('Imagen:', shader)
    form.addRow('Memoria RAM:', memory)
    form.addRow('Mouse:', mouse)
    form.addRow('Tipo de CPU:', cpu_type)
    form.addRow('Carpeta montada como C:', root_row)
    keep_open = QCheckBox('Dejar DOSBox abierto al salir del juego (diagnóstico)')
    keep_open.setChecked(bool(profile.get('keep_open', False)))
    layout.addWidget(keep_open)
    note = QLabel('Los ajustes se guardan para este ejecutable al iniciar. Ctrl+F10 libera o captura el mouse en DOSBox.')
    note.setWordWrap(True)
    layout.addWidget(note)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
    start = buttons.addButton('Guardar e iniciar', QDialogButtonBox.ButtonRole.AcceptRole)
    buttons.rejected.connect(dialog.reject)
    outer.addWidget(buttons)
    def run():
        value = cycles.text().strip().lower()
        if value and value not in ('auto', 'max') and not (value.isdigit() and 100 <= int(value) <= 1000000):
            QMessageBox.critical(dialog, 'Ciclos CPU', 'Usá auto, max o un número entre 100 y 1000000.')
            return
        cd_value = cd.text().strip()
        if cd_value:
            image = Path(cd_value).expanduser().resolve()
            if not image.is_file() or image.suffix.lower() not in CD_EXTENSIONS:
                QMessageBox.critical(dialog, 'Imagen de CD', 'Elegí una imagen .ISO, .CUE o .MDS existente.')
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
            QMessageBox.critical(dialog, 'No se pudo abrir el juego', str(exc))
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
