# Monitor de la Emergencia en Colombia

Aplicación reproducible desarrollada en **Python, Dash y Dash Leaflet** para visualizar afectaciones, necesidades y puntos de ayuda relacionados con el terremoto del 10 de agosto de 2026.

El proyecto puede ejecutarse en un computador personal, incluso cuando no haya internet, usando el último corte validado y la capa departamental guardada localmente.

## Características

- `app.py` como entrada principal.
- Mapa Leaflet real de Colombia con 33 polígonos departamentales.
- Etiquetas departamentales calculadas dentro de cada polígono.
- Capas interactivas de afectación, puntos de acopio y donación de sangre.
- Selección de ciudades mediante el mapa o el desplegable.
- KPI, necesidades territoriales, puntos habilitados y fuentes.
- Actualización automática desde Economía para la Pipol.
- Actualización del bloque forense desde la publicación de Medicina Legal en X mediante oEmbed público.
- Identidad visual propia Sol Silvana ZB · EpiSIG: negro, azul, cian, morado y magenta.
- Selector **Todas las ciudades** y ficha panorámica territorial.
- Leyenda superpuesta y siempre visible dentro del mapa.
- Tarjetas que relacionan qué donar con los puntos que reciben cada elemento.
- Copia local para trabajar sin conexión.
- Validaciones antes de reemplazar los datos existentes.
- Correcciones manuales opcionales y explícitas.
- Configuración lista para Render.

## Estructura

```text
monitor_emergencia_dash/
├── app.py                         # Entrada principal de Dash
├── config.py                      # Rutas, colores y variables operativas
├── requirements.txt               # Dependencias reproducibles
├── Procfile                       # Inicio en Render
├── render.yaml                    # Infraestructura de Render
├── run_windows.bat                # Instalación y ejecución en Windows
├── run_mac_linux.sh               # Instalación y ejecución en macOS/Linux
├── assets/
│   └── styles.css                 # Única hoja visual del tablero
├── data/
│   ├── latest.json                # Último corte normalizado
│   ├── forensic_latest.json       # Último corte forense verificado
│   ├── colombia_departamentos.geojson
│   ├── manual_overrides.json      # Correcciones controladas por la usuaria
│   └── last_update.json           # Trazabilidad de la última actualización
├── scripts/
│   ├── update_data.py             # Actualización manual
│   └── check_data.py              # Controles de calidad
├── src/
│   ├── data_service.py            # Extracción, normalización y validación
│   ├── components.py              # KPI, mapa, fichas y listados
│   ├── layout.py                  # Composición visual
│   └── callbacks.py               # Interacciones de Dash
└── tests/
    └── test_data.py
```

## Inicio rápido en Windows

1. Instale Python 3.12 desde `python.org` y marque **Add Python to PATH**.
2. Descomprima el proyecto.
3. Haga doble clic en `run_windows.bat`.
4. Espere la instalación inicial.
5. Abra `http://127.0.0.1:8050` si el navegador no se abre automáticamente.

También puede usar PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

## Inicio rápido en macOS o Linux

```bash
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```

Luego abra `http://127.0.0.1:8050`.

## Actualizar los datos

La aplicación intenta actualizarse automáticamente cada vez que se inicia, siempre que `AUTO_UPDATE=true`.

También puede hacerlo manualmente:

```bash
python scripts/update_data.py
```

Después ejecute los controles:

```bash
python scripts/check_data.py
```

El tablero fuente incluye en su HTML dos objetos JSON:

- `window.__DATOS__`: cifras, ciudades, necesidades y puntos.
- `window.__GEO__`: capa simplificada de los departamentos de Colombia.

Python los extrae sin ejecutar código de la página. El archivo nuevo solo reemplaza al anterior si supera las validaciones mínimas.

El módulo de Medicina Legal consulta el texto de la publicación oficial mediante el endpoint público oEmbed de X y extrae de forma separada:

- cuerpos recibidos;
- víctimas identificadas;
- cuerpos entregados a familiares.

El número de víctimas identificadas **no sustituye** el indicador territorial de fallecidos: son universos y procesos distintos y por eso aparecen en tarjetas separadas.

La URL de Medicina Legal está centralizada en `config.py`. Cuando la entidad publique un boletín nuevo en otro post, puede cambiarla sin tocar el extractor usando la variable de entorno `MEDLEGAL_X_URL` (por ejemplo, desde Render).

## Funcionamiento sin internet

Cuando no hay conexión:

- Dash se ejecuta normalmente en el computador.
- Se cargan `data/latest.json` y `data/colombia_departamentos.geojson`.
- El mapa departamental y los marcadores continúan funcionando.
- El fondo cartográfico de CARTO puede no aparecer, porque ese mosaico sí requiere internet.
- La interfaz muestra que está usando el último corte local.

## Corregir o complementar una cifra

Edite `data/manual_overrides.json`:

```json
{
  "enabled": true,
  "cut_note": "Corrección verificada por ASOCEPIC · 13 de agosto de 2026",
  "figures": {
    "fallecidos": 204
  },
  "cities": {
    "Cali": {
      "deaths": 96,
      "injured": 1224
    }
  }
}
```

Las correcciones quedan visibles y controladas. Para volver a la fuente original, cambie `"enabled"` a `false`.
La caché `latest.json` conserva siempre el dato descargado sin modificar; el override se aplica al cargar la aplicación.

## Publicar en Render

Dash necesita un servidor Python. Por eso **Render es la opción recomendada**. GitHub Pages solo sirve archivos estáticos y no puede ejecutar `app.py`.

1. Cree un repositorio en GitHub y cargue esta carpeta.
2. En Render elija **New → Blueprint**.
3. Conecte el repositorio.
4. Render reconocerá `render.yaml`.
5. Confirme la creación del servicio.

Configuración manual equivalente:

- Runtime: Python.
- Build command: `pip install -r requirements.txt`.
- Start command: `gunicorn app:server --preload --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`.

`--preload` hace que la actualización inicial ocurra una sola vez antes de levantar los workers; así se evita que dos procesos escriban la caché al mismo tiempo.

## Fuentes

- Economía para la Pipol: datos, necesidades, puntos y capa departamental publicada en su tablero.
- Asocapitales y administraciones territoriales: fuentes citadas por el tablero base.
- Servicio Geológico Colombiano: información del evento sísmico.
- UNGRD y Cruz Roja Colombiana: reportes de respuesta disponibles.

Las cifras son preliminares y están sujetas a actualización conforme avancen la búsqueda, el rescate y la Evaluación de Daños y Necesidades.

## Autoría

Tablero de datos recopilado por:

- X: **@solsilvanazb**
- Instagram: **@solsilvanazb_episig**

Producto independiente. No reemplaza los sistemas ni reportes oficiales.
