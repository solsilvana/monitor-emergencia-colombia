# Manual de usuario

## 1. Para qué sirve

El Monitor de la Emergencia permite revisar en una sola pantalla:

- cifras generales del corte publicado;
- ciudades con afectaciones;
- necesidades de cada territorio;
- puntos de acopio;
- lugares para donar sangre;
- ubicación del epicentro;
- fuentes y fecha de actualización.

## 2. Cómo abrirlo

### En Windows

La forma más sencilla es hacer doble clic en `run_windows.bat`.

La primera ejecución puede tomar varios minutos porque crea el ambiente e instala Dash. Las ejecuciones siguientes son más rápidas.

Cuando la terminal muestre:

```text
Dash is running on http://127.0.0.1:8050/
```

abra esa dirección en Chrome, Edge o Firefox.

No cierre la terminal mientras esté usando el tablero. Para detenerlo, regrese a la terminal y presione `Ctrl + C`.

## 3. Cómo leer la parte superior

Los cinco KPI resumen el corte cargado. Debajo del título aparece siempre:

- la fecha y hora del reporte;
- si la aplicación logró conectarse a la fuente;
- o si está utilizando el último archivo local.

La fecha del reporte no es necesariamente igual a la hora en que usted abrió la aplicación. Esto evita presentar un dato antiguo como si hubiese sido actualizado ese mismo minuto.

## 4. Cómo usar el mapa

El mapa tiene tres vistas:

1. **Afectación:** muestra ciudades reportadas y el epicentro.
2. **Acopio:** muestra puntos que reciben ayudas en especie.
3. **Sangre:** muestra puntos o jornadas de donación de sangre.

El filtro **Todas las ciudades** muestra el panorama completo. Al seleccionar una ciudad, el panel lateral cambia a su ficha territorial.

Puede:

- acercar o alejar con los botones `+` y `−`;
- mover el mapa arrastrándolo;
- pasar el cursor sobre un marcador para ver un resumen;
- hacer clic para abrir su ficha;
- seleccionar una ciudad en el desplegable;
- hacer clic en un marcador de ciudad para cambiar la ficha territorial.

Las etiquetas de los departamentos proceden de la capa guardada en `data/colombia_departamentos.geojson`. Python calcula un punto interior para cada polígono; no usa una silueta dibujada a mano.

La leyenda está dentro del mapa y explica cuatro símbolos: ciudad reportada, punto de acopio, donación de sangre y epicentro.

## 4.1 Cómo saber dónde donar

En **Qué donar y dónde llevarlo**, cada tarjeta tiene una opción `Ver dónde recibirlo`. Al abrirla muestra ciudad, nombre del punto y dirección publicados para ese elemento.

Cuando la fuente no relaciona expresamente un artículo con un punto, el tablero lo advierte y solicita confirmar antes de desplazarse. Para dinero solo se enlaza el canal oficial publicado.

## 4.2 Cómo leer Medicina Legal

El KPI **Víctimas identificadas** y el módulo forense provienen de Medicina Legal. No deben sumarse ni sustituir el KPI **Fallecidos reportados**, porque el primero describe el proceso forense y el segundo el consolidado territorial de capitales.

## 5. Cómo actualizar

Hay tres métodos equivalentes.

### Botón del tablero

Presione **Actualizar ahora**. La aplicación descargará y validará los datos. Si la operación funciona, aparecerá un mensaje verde.

### Al iniciar

Con `AUTO_UPDATE=true`, la actualización ocurre antes de mostrar la página.

### Desde la terminal

```bash
python scripts/update_data.py
python scripts/check_data.py
```

El segundo comando debe terminar con `VALIDACIÓN APROBADA`.

## 6. Cómo verificar qué se descargó

Revise `data/last_update.json`. Allí encontrará:

- dirección de la fuente;
- fecha de la descarga;
- huella SHA-256 del HTML recibido;
- cantidad de ciudades;
- cantidad de puntos;
- cantidad de departamentos;
- resultado de la validación.
- estado de actualización de Medicina Legal.

El último corte forense también queda legible en `data/forensic_latest.json`.

Revise `data/latest.json` para ver exactamente los valores consumidos por Dash. Es un archivo de texto legible y puede abrirse en Visual Studio Code, Notepad++ o cualquier editor.

## 7. Qué pasa si la fuente cambia

El extractor busca específicamente `window.__DATOS__` y `window.__GEO__`. Si la página deja de publicarlos o cambia su estructura:

1. el nuevo contenido no reemplaza el archivo válido;
2. `last_update.json` registra el error;
3. Dash sigue usando el último corte local;
4. la interfaz muestra el estado de caché local.

## 8. Correcciones manuales

Use `data/manual_overrides.json` solamente cuando tenga una cifra verificada y necesite corregir temporalmente el tablero.

Reglas recomendadas:

- incluya siempre una nota de corte;
- cambie únicamente los campos necesarios;
- conserve la fuente de la corrección en su registro de trabajo;
- ejecute `python scripts/check_data.py` después del cambio;
- desactive el override cuando la fuente principal ya incluya la corrección.

`latest.json` permanece como copia del dato descargado. Las correcciones se aplican en memoria al abrir el tablero, por lo que activarlas o desactivarlas no contamina la fuente original.

## 9. Archivos que normalmente se modifican

| Necesidad | Archivo |
|---|---|
| Cambiar colores o tipografía | `assets/styles.css` |
| Cambiar textos y orden de secciones | `src/layout.py` |
| Cambiar KPI o elementos del mapa | `src/components.py` |
| Cambiar interacciones | `src/callbacks.py` |
| Cambiar fuente o tiempo de espera | `config.py` |
| Cambiar la extracción | `src/data_service.py` |
| Corregir una cifra sin tocar código | `data/manual_overrides.json` |

## 10. Solución de problemas

### No abre `127.0.0.1:8050`

Compruebe que la terminal siga abierta y que no muestre un error. Si el puerto está ocupado, ejecute:

```powershell
$env:PORT=8051
python app.py
```

Luego abra `http://127.0.0.1:8051`.

### El mapa no muestra calles

Las calles proceden de un servicio de mosaicos en internet. La capa de Colombia y los marcadores locales deben seguir visibles. Conéctese a internet para recuperar el callejero.

### La actualización falla

Ejecute:

```bash
python scripts/update_data.py
```

Lea el error y revise `data/last_update.json`. El archivo local anterior no debe perderse.

### Se modificó una cifra y no cambia

Revise que `"enabled": true` esté activo en `manual_overrides.json` y reinicie Dash.

## 11. Publicación

Para conservar una aplicación Python controlable use Render, Railway, Fly.io o un servidor propio. GitHub Pages no ejecuta Python; únicamente puede alojar una versión estática distinta.
