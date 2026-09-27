# Abrir juego DOS desde Dolphin — prototipo 0.9.1

Añade **Abrir juego DOS** al menú contextual de Dolphin y abre archivos locales `.EXE`, `.COM` y `.BAT`, y permite montar imágenes `.ISO`, `.CUE`, `.MDS` y `.BIN` desde el menú mediante **DOSBox Staging**. La ventana permite ajustar pantalla completa, gráficos, Sound Blaster, ciclos de CPU, memoria RAM, aspecto CRT/scanlines y una imagen de CD en la unidad D: y modos de captura/controlador del mouse y tipo de CPU antes de iniciar. Los ajustes quedan asociados al ejecutable en `~/.config/dolphin-dos-launcher/profiles.json` (o `$XDG_CONFIG_HOME/dolphin-dos-launcher/profiles.json`).

## Requisitos

- KDE Dolphin con menús de servicio KIO.
- **DOSBox Staging**, disponible como `dosbox-staging` o como `dosbox` cuya versión indique Staging. El DOSBox clásico no sirve para este prototipo.
- Python 3 con Tkinter (`sudo apt install python3-tk` en Kubuntu).

## Actualización

Ejecutá de nuevo `./install.sh` desde esta carpeta. Reemplaza el lanzador y el menú; conserva los perfiles anteriores.

## Instalación

Descomprimí el archivo y ejecutá desde una terminal, dentro de su carpeta:

```bash
./install.sh
```

Si necesitás DOSBox Staging en Kubuntu, comprobá primero qué paquete ofrece tu versión en Discover o apt. Instalalo y volvé a ejecutar el instalador. El script no ejecuta `sudo` ni instala paquetes del sistema.

En Dolphin: clic derecho sobre el archivo del juego → **Abrir juego DOS** → **Configurar e iniciar**. La segunda opción inicia con lo guardado; si aún no hay perfil, muestra la ventana.

```bash
./uninstall.sh
```

Desinstalar deja los perfiles intactos para evitar perder ajustes. Se pueden borrar manualmente después.

## Límites de esta primera versión

DOSBox Staging monta la carpeta que contiene el ejecutable como unidad C:. Se admiten imágenes ISO, CUE/BIN y MDS/MDF como unidad D:; para audio de CD, preferí CUE/BIN o MDS/MDF. Si una configuración local ya ocupa D: puede haber conflicto. Otras unidades, CD físicos y varios discos quedan pendientes. Los perfiles se identifican por ruta completa: si movés un juego, habrá que configurarlo de nuevo. El menú puede aparecer en otros archivos por la clasificación MIME de Dolphin; el programa comprueba la extensión antes de abrir. La ventana usa Tkinter; todavía no tiene apariencia Qt nativa. Los archivos `.EXE` de Windows no son juegos DOS y DOSBox no podrá ejecutarlos.

## Mouse

DOSBox Staging ya emula un mouse DOS de dos botones. Primero hacé clic dentro de la ventana del juego; `Ctrl+F10` alterna captura/liberación. Si el juego sigue sin detectarlo, elegí el modo de controlador alternativo `no-tsr`. Algunos juegos requieren activar “Mouse” en su propio menú o ejecutar su programa SETUP. Estas opciones no agregan soporte de mouse a un juego que no lo trae.

## Tipo de CPU

Dejá Automática salvo que el juego necesite otra arquitectura. 386 prefetch activa también el núcleo normal requerido por DOSBox Staging. Los ciclos regulan la velocidad por separado.

## Diagnóstico de cierre inmediato

Marcá «Dejar DOSBox abierto al salir del juego» para que el emulador no cierre automáticamente y puedas leer el mensaje que produjo el juego. Escribí `EXIT` en el prompt DOS para cerrar. Esta opción ayuda a identificar si faltan archivos, CD, configuración u otra condición.

## Rutas de juegos y detección del mouse

La carpeta C: se puede elegir por juego. Debe contener el ejecutable y, si el juego lo necesita, sus subcarpetas de datos. Con una carpeta C: más amplia, el lanzador cambia al subdirectorio del ejecutable antes de iniciarlo. Para un juego que informe «mouse no detectado», el modo «Cargar MOUSE.COM antes del juego» desactiva el controlador residente automático y ejecuta MOUSE explícitamente. Es un intento de compatibilidad, no garantiza que todos los juegos reconozcan el mouse.

## Ejecución con carpeta C: personalizada

Se corrigió la orden DOS para iniciar automáticamente el ejecutable cuando se utiliza una carpeta C: personalizada o se deja abierta la consola. En ese modo el archivo debe tener un nombre DOS 8.3 sin espacios ni acentos.

## Rutas con caracteres fuera de ASCII

Para carpetas como `Clyde´s Adventure`, la aplicación crea un enlace simbólico auxiliar con nombre ASCII en `~/.cache/dolphin-dos-launcher/mounts/` y monta ese enlace como C:. No renombra ni mueve el juego. Si hay subcarpetas con acentos entre C: y el ejecutable, elegí directamente la carpeta del ejecutable como C:.

## Abrir una imagen de CD

Clic derecho en una imagen ISO, CUE, MDS o BIN → «Configurar e iniciar / montar CD». Elegí una carpeta existente con permiso de escritura como unidad C: para instalar el juego. El disco queda en D: y DOSBox abre el prompt `D:\>`; ejecutá `DIR` y luego el instalador del CD, normalmente `INSTALL` o `SETUP`. Para BIN elegí preferentemente el archivo CUE asociado; si elegís BIN, el programa busca un CUE con el mismo nombre. El CUE debe conservar sus pistas de audio junto a él. Algunas imágenes contienen instaladores de Windows y no se pueden ejecutar en DOSBox.
