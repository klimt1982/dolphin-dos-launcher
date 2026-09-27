#!/usr/bin/env python3
"""Per-game DOSBox Staging launcher for KDE Dolphin."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from urllib.parse import unquote, urlparse

APP = 'dolphin-dos-launcher'
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


def show_error(title, message):
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message, parent=root)
        root.destroy()
    except tk.TclError:
        print(f'{title}: {message}', file=sys.stderr)


def configure_media(path, profiles):
    root = tk.Tk()
    root.title('Montar CD en DOSBox Staging')
    root.resizable(False, False)
    frame = ttk.Frame(root, padding=20)
    frame.grid(sticky='nsew')
    ttk.Label(frame, text=path.name, font=('Sans', 13, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
    ttk.Label(frame, text='El disco se montará como D:. Elegí una carpeta donde instalar el juego como C:.',
              wraplength=430).grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 12))
    profile = profiles.get(str(path), {})
    if not isinstance(profile, dict):
        profile = {}
    install_dir = tk.StringVar(value=str(profile.get('root_dir') or path.parent))
    fullscreen = tk.BooleanVar(value=bool(profile.get('fullscreen', False)))
    ttk.Label(frame, text='Carpeta C:').grid(row=2, column=0, sticky='w')
    line = ttk.Frame(frame)
    line.grid(row=2, column=1, sticky='w')
    ttk.Entry(line, textvariable=install_dir, width=38).pack(side='left')

    def browse():
        chosen = filedialog.askdirectory(parent=root, title='Elegir carpeta de instalación (C:)',
                                         initialdir=install_dir.get())
        if chosen:
            install_dir.set(chosen)

    ttk.Button(line, text='Examinar…', command=browse).pack(side='left', padx=(5, 0))
    ttk.Checkbutton(frame, text='Pantalla completa', variable=fullscreen).grid(row=3, column=0, columnspan=2, sticky='w', pady=(12, 8))
    ttk.Label(frame, text='DOSBox abrirá D:. Escribí DIR para ver el disco y ejecutá allí INSTALL o SETUP si corresponde.',
              wraplength=430).grid(row=4, column=0, columnspan=2, sticky='w', pady=(0, 15))
    buttons = ttk.Frame(frame)
    buttons.grid(row=5, column=0, columnspan=2, sticky='e')

    def start():
        selected = {'root_dir': install_dir.get().strip(), 'fullscreen': fullscreen.get()}
        try:
            binary = dosbox_binary()
            if not binary:
                raise RuntimeError('No se encontró DOSBox Staging.')
            media_command(binary, path, selected)
            launch(path, selected)
            profiles[str(path)] = selected
            save_profiles(profiles)
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror('No se pudo montar el CD', str(exc), parent=root)
            return
        root.destroy()

    ttk.Button(buttons, text='Cancelar', command=root.destroy).pack(side='left', padx=(0, 8))
    ttk.Button(buttons, text='Montar y abrir DOSBox', command=start).pack(side='left')
    root.mainloop()


def configure(path, profiles):
    root = tk.Tk()
    root.title('Abrir juego DOS')
    root.resizable(False, False)
    frame = ttk.Frame(root, padding=20)
    frame.grid(sticky='nsew')
    ttk.Label(frame, text=path.name, font=('Sans', 13, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 4))
    ttk.Label(frame, text=str(path.parent), wraplength=430).grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 15))
    profile = profiles.get(str(path), {})
    if not isinstance(profile, dict):
        profile = {}
    fullscreen = tk.BooleanVar(value=bool(profile.get('fullscreen', False)))
    machine = tk.StringVar(value=next((label for label, val in MACHINES.items() if val == profile.get('machine', '')), 'Predeterminada'))
    sound = tk.StringVar(value=next((label for label, val in SOUND.items() if val == profile.get('sound', '')), 'Predeterminado'))
    cycles = tk.StringVar(value=str(profile.get('cycles', '')))
    shader = tk.StringVar(value=next((label for label, val in SHADERS.items() if val == profile.get('shader', '')), 'Predeterminado (CRT adaptable)'))
    memory = tk.StringVar(value=next((label for label, val in MEMORY.items() if val == profile.get('memory', '')), 'Predeterminada (16 MB)'))
    cd = tk.StringVar(value=str(profile.get('cd', '')))
    mouse = tk.StringVar(value=next((label for label, val in MOUSE_MODES.items() if val == profile.get('mouse', '')), 'Normal (clic para capturar)'))
    cpu_type = tk.StringVar(value=next((label for label, val in CPU_TYPES.items() if val == profile.get('cpu_type', '')), 'Automática (recomendada)'))
    keep_open = tk.BooleanVar(value=bool(profile.get('keep_open', False)))
    root_dir = tk.StringVar(value=str(profile.get('root_dir') or path.parent))
    ttk.Checkbutton(frame, text='Pantalla completa', variable=fullscreen).grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 12))
    ttk.Label(frame, text='Gráficos:').grid(row=3, column=0, sticky='w', pady=5)
    ttk.Combobox(frame, textvariable=machine, values=list(MACHINES), state='readonly', width=25).grid(row=3, column=1, sticky='w')
    ttk.Label(frame, text='Sound Blaster:').grid(row=4, column=0, sticky='w', pady=5)
    ttk.Combobox(frame, textvariable=sound, values=list(SOUND), state='readonly', width=25).grid(row=4, column=1, sticky='w')
    ttk.Label(frame, text='Ciclos CPU:').grid(row=5, column=0, sticky='w', pady=5)
    ttk.Entry(frame, textvariable=cycles, width=28).grid(row=5, column=1, sticky='w')
    ttk.Label(frame, text='Vacío = predeterminado; auto, max o número entre 100 y 1000000.', wraplength=430).grid(row=6, column=0, columnspan=2, sticky='w', pady=(3, 16))
    ttk.Label(frame, text='Imagen de CD (unidad D:):').grid(row=7, column=0, sticky='w', pady=5)
    cd_row = ttk.Frame(frame)
    cd_row.grid(row=7, column=1, sticky='w')
    ttk.Entry(cd_row, textvariable=cd, width=23).pack(side='left')
    def choose_cd():
        selected = filedialog.askopenfilename(parent=root, title='Elegir imagen de CD', filetypes=[('Imágenes de CD', '*.iso *.ISO *.cue *.CUE *.mds *.MDS'), ('Todos', '*')])
        if selected:
            cd.set(selected)
    ttk.Button(cd_row, text='Examinar…', command=choose_cd).pack(side='left', padx=(5, 0))
    ttk.Label(frame, text='Imagen:').grid(row=8, column=0, sticky='w', pady=5)
    ttk.Combobox(frame, textvariable=shader, values=list(SHADERS), state='readonly', width=25).grid(row=8, column=1, sticky='w')
    ttk.Label(frame, text='Memoria RAM:').grid(row=9, column=0, sticky='w', pady=5)
    ttk.Combobox(frame, textvariable=memory, values=list(MEMORY), state='readonly', width=25).grid(row=9, column=1, sticky='w')
    ttk.Label(frame, text='Mouse:').grid(row=10, column=0, sticky='w', pady=5)
    ttk.Combobox(frame, textvariable=mouse, values=list(MOUSE_MODES), state='readonly', width=34).grid(row=10, column=1, sticky='w')
    ttk.Label(frame, text='Normal: clic dentro del juego para capturar. Ctrl+F10 libera o captura el mouse.', wraplength=430).grid(row=11, column=0, columnspan=2, sticky='w', pady=(3, 6))
    ttk.Label(frame, text='Tipo de CPU:').grid(row=12, column=0, sticky='w', pady=5)
    ttk.Combobox(frame, textvariable=cpu_type, values=list(CPU_TYPES), state='readonly', width=34).grid(row=12, column=1, sticky='w')
    ttk.Label(frame, text='El tipo de CPU es distinto de los ciclos (velocidad).', wraplength=430).grid(row=13, column=0, columnspan=2, sticky='w', pady=(3, 6))
    ttk.Checkbutton(frame, text='Dejar DOSBox abierto al salir del juego (diagnóstico)', variable=keep_open).grid(row=14, column=0, columnspan=2, sticky='w', pady=(8, 3))
    ttk.Label(frame, text='Así podés leer cualquier mensaje al terminar el juego. Escribí EXIT para cerrar DOSBox.', wraplength=430).grid(row=15, column=0, columnspan=2, sticky='w', pady=(0, 8))
    ttk.Label(frame, text='Carpeta montada como C:').grid(row=16, column=0, sticky='w', pady=5)
    root_row = ttk.Frame(frame)
    root_row.grid(row=16, column=1, sticky='w')
    ttk.Entry(root_row, textvariable=root_dir, width=23).pack(side='left')
    def choose_root():
        selected = filedialog.askdirectory(parent=root, title='Elegir carpeta que será C:', initialdir=root_dir.get())
        if selected:
            root_dir.set(selected)
    ttk.Button(root_row, text='Examinar…', command=choose_root).pack(side='left', padx=(5, 0))
    ttk.Label(frame, text='Elegí la carpeta que contiene el juego y los archivos que necesita.', wraplength=430).grid(row=17, column=0, columnspan=2, sticky='w', pady=(2, 8))
    ttk.Label(frame, text='Los ajustes se guardan al iniciar y se aplican solo a este ejecutable.', wraplength=430).grid(row=18, column=0, columnspan=2, sticky='w', pady=(6, 15))
    buttons = ttk.Frame(frame)
    buttons.grid(row=19, column=0, columnspan=2, sticky='e')

    def start():
        value = cycles.get().strip().lower()
        if value and value not in ('auto', 'max') and not (value.isdigit() and 100 <= int(value) <= 1000000):
            messagebox.showerror('Ciclos CPU', 'Usá auto, max o un número entre 100 y 1000000.', parent=root)
            return
        cd_value = cd.get().strip()
        if cd_value:
            image = Path(cd_value).expanduser().resolve()
            if not image.is_file() or image.suffix.lower() not in CD_EXTENSIONS:
                messagebox.showerror('Imagen de CD', 'Elegí una imagen .ISO, .CUE o .MDS existente.', parent=root)
                return
            cd_value = str(image)
        selected = {'fullscreen': fullscreen.get(), 'machine': MACHINES[machine.get()], 'sound': SOUND[sound.get()], 'cycles': value, 'cd': cd_value, 'shader': SHADERS[shader.get()], 'memory': MEMORY[memory.get()], 'mouse': MOUSE_MODES[mouse.get()], 'cpu_type': CPU_TYPES[cpu_type.get()], 'keep_open': keep_open.get(), 'root_dir': root_dir.get().strip()}
        try:
            if not dosbox_binary():
                raise RuntimeError('No se encontró DOSBox Staging. Instalalo antes de iniciar el juego.')
            command(dosbox_binary(), path, selected)
            launch(path, selected)
            profiles[str(path)] = selected
            save_profiles(profiles)
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror('No se pudo abrir el juego', str(exc), parent=root)
            return
        root.destroy()

    ttk.Button(buttons, text='Cancelar', command=root.destroy).pack(side='left', padx=(0, 8))
    ttk.Button(buttons, text='Guardar e iniciar', command=start).pack(side='left')
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description='Abrir juegos DOS desde Dolphin')
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
    except (ValueError, OSError, RuntimeError, tk.TclError) as exc:
        show_error('Abrir juego DOS', str(exc))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
