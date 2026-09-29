# Dolphin DOS Launcher

[English documentation](README.en.md)

Menú contextual de KDE Dolphin para abrir juegos DOS con **DOSBox Staging**. Al hacer clic derecho en un `.EXE`, `.COM` o `.BAT`, permite configurar el juego e iniciarlo, o reutilizar su perfil guardado. También monta imágenes `.ISO`, `.CUE`, `.MDS` y `.BIN` como CD para iniciar un instalador desde el prompt de DOS. No adivina el ejecutable de un CD.

**Versión 1.1.0.** Probada en Kubuntu con Plasma Wayland y DOSBox Staging 0.83.0. Incluye español e inglés para el menú y el formulario Qt. El idioma se elige durante la instalación. El proyecto es independiente de KDE y DOSBox Staging.

## Requisitos

- KDE Dolphin con soporte para menús de servicio KIO.
- **DOSBox Staging instalado aparte** y disponible como `dosbox-staging` o como `dosbox` cuya versión indique Staging. El DOSBox clásico no sirve.
- Python 3 y PyQt6. En Kubuntu 26.04: `sudo apt install python3-pyqt6 qt6-wayland`.

La extensión no instala DOSBox Staging ni paquetes del sistema. Comprobá `dosbox-staging --version` antes de instalarla. Si DOSBox está en `~/.local/bin`, esa carpeta debe figurar en `PATH` al iniciar Dolphin.

## Instalación

Descargá el archivo de la versión, descomprimilo y ejecutá dentro de la carpeta `dolphin-dos-launcher`:

```bash
./install.sh
```

El instalador copia el programa a `~/.local/bin` y el menú de servicio a `~/.local/share/kio/servicemenus` (respeta `XDG_DATA_HOME`). También instala un ícono y una entrada de aplicación oculta con identificador propio para mostrar el ícono de la ventana en Plasma Wayland. No necesita `sudo`. Si Dolphin estaba abierto, cerralo y volvé a abrirlo.

El instalador pregunta por **Automático**, **Español** o **English**. Automático usa el idioma del sistema. Enter conserva la elección anterior al actualizar. Si instalás desde un script sin terminal, se usa la elección anterior o Automático. También podés fijarla directamente con `./install.sh --language en` (o `es`, `auto`).

Para actualizar, ejecutá de nuevo `./install.sh` desde la nueva versión. Los perfiles existentes se conservan.

## Uso

Clic derecho sobre el ejecutable DOS → **Abrir juego DOS** → **Configurar e iniciar / montar CD**. La otra acción, **Iniciar con ajustes guardados**, usa el perfil anterior; si no existe, muestra el formulario.

El formulario permite elegir pantalla completa, gráficos, Sound Blaster, ciclos y tipo de CPU, memoria, imagen CRT/scanlines, captura/controlador de mouse, CD en D:, carpeta C: y dejar abierta la consola al salir. Los perfiles se guardan por ruta absoluta en `~/.config/dolphin-dos-launcher/profiles.json` (o bajo `XDG_CONFIG_HOME`).

El menú y la ventana usan el idioma elegido al instalar. La preferencia se guarda en `~/.config/dolphin-dos-launcher/settings.json`. Podés cambiarla ejecutando el instalador otra vez; no modifica los perfiles de los juegos.

Para una imagen de CD, seleccioná una carpeta existente y escribible como C:. DOSBox abrirá en `D:\>`; usá `DIR` y luego el instalador que corresponda, si el disco tiene uno. Elegí el `.CUE` cuando haya pistas BIN y audio; al seleccionar BIN se busca un CUE con el mismo nombre.

## Desinstalación

```bash
./uninstall.sh
```

El desinstalador quita los archivos instalados por este proyecto y conserva los perfiles. Si querés borrarlos, eliminá manualmente `~/.config/dolphin-dos-launcher/profiles.json`.

## Límites conocidos

- Se montan ISO, CUE/BIN y MDS/MDF como D:. No se admiten varios discos ni unidades de CD físicas.
- Un ejecutable Windows no funcionará en DOSBox. Algunas imágenes incluyen sólo instaladores Windows.
- Los perfiles se identifican por ruta: mover un juego requiere volver a configurarlo.
- El modo con carpeta C: personalizada o consola abierta exige que el ejecutable tenga un nombre DOS 8.3 sin espacios ni acentos. Para carpetas con caracteres fuera de ASCII se crea un enlace auxiliar en la caché; no se renombra el juego.
- El menú puede aparecer sobre archivos que no son DOS debido a su tipo MIME. El programa valida la extensión al abrir.
- Algunos juegos requieren activar el mouse en su propio SETUP. Dentro de DOSBox, `Ctrl+F10` alterna la captura.

## Código y licencia

Código fuente: <https://github.com/klimt1982/dolphin-dos-launcher>. Licencia **GNU GPL v3 o posterior**; consultá [COPYING](COPYING). DOSBox Staging se distribuye por separado bajo su propia licencia.
