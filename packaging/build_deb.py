#!/usr/bin/env python3
"""Build the amd64 package using the verified official Staging release."""
import argparse
import hashlib
import pathlib
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSION = '1.2.0'
URL = 'https://github.com/dosbox-staging/dosbox-staging/releases/download/v0.83.0/dosbox-staging-linux-x86_64-v0.83.0.tar.xz'
SHA256 = 'd3a94f7f1c3e68a47ec88d61145506c7904452adb0c9c5928cb8cfe2331d6c5c'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--upstream-archive', type=pathlib.Path)
    parser.add_argument('--output', type=pathlib.Path, default=ROOT / 'dist')
    args = parser.parse_args()
    archive = args.upstream_archive
    if archive is None:
        archive = ROOT / '.build-cache' / 'dosbox-staging-0.83.0.tar.xz'
        archive.parent.mkdir(parents=True, exist_ok=True)
        if not archive.exists():
            temp = archive.with_suffix('.part')
            try:
                urllib.request.urlretrieve(URL, temp)
                temp.replace(archive)
            finally:
                temp.unlink(missing_ok=True)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise SystemExit('Upstream SHA256 mismatch; package not built.')
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve() / f'dolphin-dos-launcher_{VERSION}_amd64.deb'
    with tempfile.TemporaryDirectory(prefix='dolphin-dos-deb-') as directory:
        work = pathlib.Path(directory)
        upstream = work / 'upstream'
        upstream.mkdir()
        with tarfile.open(archive) as tar:
            tar.extractall(upstream, filter='data')
        original = next(upstream.iterdir())
        package = work / 'package'
        app = package / 'usr/lib/dolphin-dos-launcher'
        app.mkdir(parents=True)
        shutil.copy2(ROOT / 'dos_game_launcher.py', app / 'dos_game_launcher.py')
        script = app / 'dos_game_launcher.py'
        script.write_text(script.read_text().replace('#!/usr/bin/env python3', '#!/usr/bin/python3', 1))
        shutil.copy2(ROOT / 'dolphin-dos-launcher.svg', app / 'dolphin-dos-launcher.svg')
        (app / 'dos_game_launcher.py').chmod(0o755)
        shutil.copytree(original, app / 'dosbox-staging')
        binary = package / 'usr/bin'
        binary.mkdir(parents=True)
        (binary / 'dolphin-dos-launcher').symlink_to('../lib/dolphin-dos-launcher/dos_game_launcher.py')
        menu = package / 'usr/share/kio/servicemenus'
        menu.mkdir(parents=True)
        text = (ROOT / 'dolphin-dos-launcher.desktop').read_text().replace('@EXECUTABLE@', '/usr/bin/dolphin-dos-launcher')
        (menu / 'dolphin-dos-launcher.desktop').write_text(text)
        (menu / 'dolphin-dos-launcher.desktop').chmod(0o755)
        apps = package / 'usr/share/applications'
        apps.mkdir(parents=True)
        text = (ROOT / 'dolphin-dos-launcher-app.desktop').read_text().replace('@EXECUTABLE@', '/usr/bin/dolphin-dos-launcher').replace('@ICON@', 'dolphin-dos-launcher')
        (apps / 'io.github.klimt1982.dolphin-dos-launcher.desktop').write_text(text)
        icons = package / 'usr/share/icons/hicolor/scalable/apps'
        icons.mkdir(parents=True)
        shutil.copy2(ROOT / 'dolphin-dos-launcher.svg', icons)
        doc = package / 'usr/share/doc/dolphin-dos-launcher'
        doc.mkdir(parents=True)
        for name in ('COPYING', 'README.md', 'README.en.md'):
            shutil.copy2(ROOT / name, doc)
        shutil.copy2(ROOT / 'packaging/README.md', doc / 'INSTALL-DEB.md')
        (doc / 'copyright').write_text('Dolphin DOS Launcher: Copyright 2026 Lucas Quiroga, GPL-3.0-or-later.\n'
            'DOSBox Staging: Copyright DOSBox authors and DOSBox Staging Team, GPL-2.0-or-later.\n'
            'The pristine upstream distribution, LICENSE and all third-party notices are in\n'
            '/usr/lib/dolphin-dos-launcher/dosbox-staging/.\n'
            'Upstream source: https://github.com/dosbox-staging/dosbox-staging/tree/v0.83.0\n'
            'Launcher source: https://github.com/klimt1982/dolphin-dos-launcher\n')
        metadata = package / 'DEBIAN'
        metadata.mkdir()
        size = sum(p.stat().st_size for p in package.rglob('*') if p.is_file() and not p.is_symlink()) // 1024
        (metadata / 'control').write_text(f'''Package: dolphin-dos-launcher
Version: {VERSION}
Architecture: amd64
Section: games
Priority: optional
Maintainer: Lucas Quiroga <klimt1982@users.noreply.github.com>
Installed-Size: {size}
Depends: python3 (>= 3.10), python3-pyqt6, qt6-wayland, libc6 (>= 2.34), libstdc++6 (>= 12), libgcc-s1, libgl1, libegl1, libwayland-client0, libwayland-cursor0, libwayland-egl1, libxkbcommon0, libpulse0, libasound2t64 | libasound2
Recommends: dolphin
Homepage: https://github.com/klimt1982/dolphin-dos-launcher
Description: Launch DOS games from Dolphin with bundled DOSBox Staging
 Configure CPU, memory, graphics, mouse and CD images per game.
 Includes the official DOSBox Staging 0.83.0 amd64 distribution.
 English and Spanish UI. For Kubuntu/Ubuntu 24.04 and newer.
''')
        subprocess.run(['dpkg-deb', '--root-owner-group', '--build', str(package), str(output)], check=True)
    print(output)


if __name__ == '__main__':
    main()
