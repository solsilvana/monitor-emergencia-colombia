"""Interacciones del tablero."""
from __future__ import annotations

import datetime as dt
from typing import Any

from dash import ALL, Input, Output, State, ctx, html, no_update

from src.components import ALL_CITIES, city_detail, kpi_cards, map_component, point_list
from src.data_service import load_data, load_geojson, safe_refresh


def register_callbacks(app: Any) -> None:
    @app.callback(
        Output("update-result", "children"),
        Output("update-result", "className"),
        Output("data-version", "data"),
        Input("update-data-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_data(_: int):
        result = safe_refresh()
        timestamp = dt.datetime.now().strftime("%H:%M:%S")
        if result.get("status") == "updated":
            return f"Actualización verificada · {timestamp}", "update-status status-ok", result.get("updated_at")
        return f"Sin conexión: se mantiene el corte local · {timestamp}", "update-status status-cache", result.get("updated_at")

    @app.callback(
        Output("city-dropdown", "value"),
        Input({"type": "city-marker", "index": ALL}, "n_clicks"),
        State("city-dropdown", "value"),
        prevent_initial_call=True,
    )
    def choose_city_from_map(_: list[int | None], current_city: str):
        trigger = ctx.triggered_id
        if isinstance(trigger, dict) and trigger.get("index"):
            return trigger["index"]
        return current_city or no_update

    @app.callback(
        Output("kpi-container", "children"),
        Output("map-container", "children"),
        Output("city-detail", "children"),
        Output("point-list", "children"),
        Output("cut-value", "children"),
        Input("city-dropdown", "value"),
        Input("layer-filter", "value"),
        Input("data-version", "data"),
    )
    def render_dashboard(selected_city: str, layer: str, _: str):
        data = load_data()
        geojson = load_geojson()
        available = [ALL_CITIES] + [city["name"] for city in data["cities"]]
        if selected_city not in available:
            selected_city = ALL_CITIES
        return (
            kpi_cards(data),
            map_component(data, geojson, layer, selected_city),
            city_detail(data, selected_city),
            point_list(data, layer, selected_city),
            data["meta"].get("cut", "Sin corte informado"),
        )
