"""Entrada principal del Monitor de la Emergencia en Colombia.

Ejecución local:
    python app.py

Producción en Render:
    gunicorn app:server
"""
from __future__ import annotations

from dash import Dash

from config import AUTO_UPDATE, DEBUG, HOST, PORT
from src.callbacks import register_callbacks
from src.data_service import load_data, load_geojson, load_run_log, safe_refresh
from src.layout import build_layout


def create_app() -> Dash:
    if AUTO_UPDATE:
        safe_refresh()

    data = load_data()
    geojson = load_geojson()
    run_log = load_run_log()

    dashboard = Dash(
        __name__,
        title="Monitor territorial de emergencia · Sol Silvana ZB EpiSIG",
        update_title="Actualizando datos…",
        suppress_callback_exceptions=True,
    )
    dashboard.layout = build_layout(data, geojson, run_log)
    register_callbacks(dashboard)
    return dashboard


app = create_app()
server = app.server


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
