# Paquete Debian / Debian package

Versión 1.2.0 para Kubuntu/Ubuntu 24.04 o posterior, arquitectura amd64.
Incluye la distribución oficial completa de DOSBox Staging 0.83.0, con sus
recursos, plugins, bibliotecas auxiliares y avisos de licencia sin modificar.
APT resuelve PyQt6, Qt Wayland y las bibliotecas del sistema. No descarga
programas ni modifica carpetas de usuarios desde scripts de instalación.

## Instalación

Desde la carpeta que contiene el archivo:

```bash
sudo apt install ./dolphin-dos-launcher_1.2.0_amd64.deb
```

También se puede abrir el paquete con el instalador gráfico de la distribución.
Cerrá y volvé a abrir Dolphin después de instalarlo.

Si usabas el ZIP anterior, ejecutá su `./uninstall.sh` como tu usuario antes
de instalar el DEB: las entradas locales tienen prioridad sobre las del sistema.
Los perfiles y la preferencia de idioma se conservan. La instalación nueva usa
el idioma del sistema; conserva settings.json si ya existe.

El ejecutable se instala en `/usr/bin/dolphin-dos-launcher`; el emulador privado
en `/usr/lib/dolphin-dos-launcher/dosbox-staging/`. La copia instalada previamente
en `~/.local/bin/dosbox-staging` permanece intacta. El paquete usa su propia copia.

## Quitar el paquete

```bash
sudo apt remove dolphin-dos-launcher
```

Los perfiles siguen en `~/.config/dolphin-dos-launcher/`.

## Reconstrucción

```bash
python3 packaging/build_deb.py
```

Requiere Python 3.12 o posterior y dpkg-deb. Descarga el archivo oficial fijado
en el script y verifica SHA256 antes de extraerlo. También admite
`--upstream-archive /ruta/al/archivo.tar.xz` para reconstruir sin red.
El resultado queda en `dist/`.

Se verificaron estructura, permisos, metadatos, checksum upstream y ejecución
del emulador. Instalación y uso confirmados por el autor en Kubuntu 26.04
con Plasma Wayland. Otras versiones de Ubuntu aún no tienen prueba directa.

## English

For amd64 Kubuntu/Ubuntu 24.04 or newer. Includes the unmodified official
DOSBox Staging 0.83.0 release. Install with the APT command above; dependencies
are resolved automatically. Remove the old per-user ZIP installation first
using its uninstall.sh; game profiles and language preferences are retained.
Fresh installs follow the system language. No root installer writes user files.
Restart Dolphin after installing. Installation and use verified by the author on Kubuntu 26.04 with Plasma
Wayland. Other Ubuntu versions have not been directly tested.
