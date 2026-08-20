"""Configuración central del proyecto.

Todas las rutas y decisiones operativas se controlan desde este archivo para
que la aplicación pueda verificarse y ajustarse sin tocar el resto del código.
"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LATEST_DATA_FILE = DATA_DIR / "latest.json"
GEOJSON_FILE = DATA_DIR / "colombia_departamentos.geojson"
RUN_LOG_FILE = DATA_DIR / "last_update.json"
OVERRIDES_FILE = DATA_DIR / "manual_overrides.json"
FORENSIC_DATA_FILE = DATA_DIR / "forensic_latest.json"

ECONOMIA_PIPOL_URL = (
    "https://www.economiaparalapipol.com/interactivos/mapa-ayuda-colombia/"
)
ASOCAPITALES_URL = (
    "https://www.asocapitales.co/actualidad/noticias/ciudades-seguras/"
    "terremoto-en-colombia-suben-273-los-muertos-204-se-registran"
)
MEDLEGAL_REPORT_URL = (
    "https://www.medicinalegal.gov.co/noticias/-/asset_publisher/"
    "vLcVEedo8qgD/content/plantilla_comunic-10"
    "?_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_"
    "vLcVEedo8qgD_assetEntryId=1333742"
)

# En el computador personal se intenta actualizar al iniciar. Si no hay
# conexión, la aplicación usa el último archivo validado guardado en data/.
AUTO_UPDATE = os.getenv("AUTO_UPDATE", "true").lower() in {"1", "true", "yes", "si"}
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "35"))

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8050"))
DEBUG = os.getenv("DASH_DEBUG", "false").lower() in {"1", "true", "yes"}

COLORS = {
    "background": "#070A17",
    "surface": "#0D1326",
    "surface_light": "#121A31",
    "ink": "#F5F7FF",
    "muted": "#9BA8C4",
    "blue": "#208CFF",
    "cyan": "#19D3D1",
    "purple": "#7C5CFC",
    "magenta": "#E548C7",
    "green": "#45D5A1",
    "orange": "#FF9B71",
    "red": "#FF5D78",
    "line": "#263454",
}
