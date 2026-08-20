"""Componentes visuales reutilizables del tablero Dash."""
from __future__ import annotations

import html as html_lib
import math
from typing import Any
from urllib.parse import quote

import dash_leaflet as dl
from dash import html

from config import COLORS

ALL_CITIES = "__all__"


def format_number(value: int | float | None) -> str:
    if value is None:
        return "—"
    return f"{value:,.0f}".replace(",", ".")


ICON_PATHS = {
    "people": "M5 20v-1.5A3.5 3.5 0 0 1 8.5 15h3A3.5 3.5 0 0 1 15 18.5V20M10 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6M16 12a2.5 2.5 0 1 0 0-5M17 15h.5a3 3 0 0 1 3 3v2",
    "forensic": "M12 3a6 6 0 0 0-6 6v3M18 9a6 6 0 0 0-6-6M9 21c2-3 2-6 2-9a1 1 0 0 1 2 0c0 4-1 7-2 9M6 16c1-2 1-4 1-6M17 12c0 4-1 7-3 9",
    "medical": "M9 4h6v5h5v6h-5v5H9v-5H4V9h5z",
    "building": "M5 21V4h11v17M16 9h3v12M8 8h2M8 12h2M8 16h2M13 8h1M13 12h1M13 16h1M3 21h18",
    "alert": "M12 3 2.8 20h18.4L12 3zM12 9v5M12 17.5v.2",
    "pin": "M12 22s7-6.2 7-13a7 7 0 1 0-14 0c0 6.8 7 13 7 13zM12 11.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5",
    "box": "M4 8 12 4l8 4-8 4-8-4zM4 8v9l8 4 8-4V8M12 12v9",
    "drop": "M12 3s-6 7-6 12a6 6 0 0 0 12 0c0-5-6-12-6-12z",
    "shelter": "M3 20 12 5l9 15M7 20h10M12 11v9",
    "care": "M12 21S4 16.5 4 10a4 4 0 0 1 7-2.6A4 4 0 0 1 20 10c0 6.5-8 11-8 11z",
    "tool": "M14 6a4 4 0 0 0-5 5L3 17l4 4 6-6a4 4 0 0 0 5-5l-3 1-2-2 1-3z",
    "paw": "M8 13c-2 1-3 3-2 5 1 2 3 2 6 1 3 1 5 1 6-1 1-2 0-4-2-5-2-1-5-1-8 0zM7 9a2 3 0 1 0 0-6 2 3 0 0 0 0 6M17 9a2 3 0 1 0 0-6 2 3 0 0 0 0 6",
    "money": "M4 7h16v11H4zM8 12h.01M16 13h.01M12 9.5a3 3 0 1 0 0 6 3 3 0 0 0 0-6",
    "check": "m5 12 4 4L19 6",
}


def line_icon(name: str, class_name: str = "line-icon", color: str | None = None) -> html.Img:
    """Crea un icono SVG propio, embebido en el HTML y sin librerías externas."""
    stroke = color or COLORS["cyan"]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        f'<path d="{ICON_PATHS.get(name, ICON_PATHS["check"])}" fill="none" '
        f'stroke="{stroke}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )
    return html.Img(src="data:image/svg+xml," + quote(svg), className=class_name, alt="")


def kpi_cards(data: dict[str, Any]) -> list[html.Article]:
    figures = data["figures"]
    forensic = data.get("forensics", {})
    ungrd_cut = figures.get("corte_ungrd", "último corte")
    missing_cut = figures.get("corte_desaparecidos_pais", ungrd_cut)
    asocapitales_cut = figures.get("corte_asocapitales", "último corte")
    cards = [
        ("Fallecidos en Colombia", figures.get("fallecidos_pais", figures.get("fallecidos")), f"UNGRD · {ungrd_cut}", "people", "cyan"),
        ("Personas heridas", figures.get("heridos_pais", figures.get("heridos")), f"UNGRD · {ungrd_cut}", "medical", "purple"),
        ("Personas desaparecidas", figures.get("desaparecidos_pais", figures.get("desaparecidos")), f"Último valor disponible · {missing_cut}", "alert", "red"),
        ("Fallecidos en capitales", figures.get("fallecidos"), f"Asocapitales · {asocapitales_cut}", "pin", "blue"),
        ("Víctimas identificadas", forensic.get("victims_identified"), f"Medicina Legal · {forensic.get('cut', 'último corte validado')}", "forensic", "magenta"),
        ("Capitales en alerta roja", figures.get("alerta_roja"), "Respuesta territorial activa", "building", "green"),
    ]
    return [
        html.Article(
            [html.Div(line_icon(icon, color=COLORS[accent]), className="kpi-icon"), html.Div(format_number(value), className="kpi-value"), html.Div(label, className="kpi-label"), html.Div(note, className="kpi-note")],
            className=f"kpi-card accent-{accent}",
        )
        for label, value, note, icon, accent in cards
    ]


def national_balance_panel(data: dict[str, Any]) -> html.Section:
    """Presenta el balance nacional del corte oficial de la UNGRD."""
    figures = data["figures"]
    metrics = [
        ("familias_afectadas", "Familias afectadas", figures.get("familias_afectadas")),
        ("personas_afectadas", "Personas afectadas", figures.get("personas_afectadas")),
        ("departamentos_afectados", "Departamentos afectados", figures.get("departamentos_afectados")),
        ("municipios_afectados", "Municipios afectados", figures.get("municipios_afectados")),
        ("rescatados_pais", "Personas rescatadas", figures.get("rescatados_pais")),
        ("viviendas_destruidas", "Viviendas destruidas", figures.get("viviendas_destruidas")),
        ("viviendas_averiadas", "Viviendas averiadas", figures.get("viviendas_averiadas")),
        ("edificios_colapsados", "Edificios colapsados", figures.get("edificios_colapsados")),
        ("centros_educativos_afectados", "Centros educativos", figures.get("centros_educativos_afectados")),
        ("centros_comunitarios_afectados", "Centros comunitarios", figures.get("centros_comunitarios_afectados")),
        ("centros_salud_afectados", "Centros de salud", figures.get("centros_salud_afectados")),
        ("vias_afectadas", "Vías afectadas", figures.get("vias_afectadas")),
        ("acueductos_afectados", "Acueductos", figures.get("acueductos_afectados")),
        ("puentes_vehiculares_afectados", "Puentes vehiculares", figures.get("puentes_vehiculares_afectados")),
        ("puentes_peatonales_afectados", "Puentes peatonales", figures.get("puentes_peatonales_afectados")),
        ("aeropuertos_afectados", "Aeropuertos", figures.get("aeropuertos_afectados")),
        ("animales_afectados", "Animales afectados", figures.get("animales_afectados")),
        ("animales_rescatados", "Animales rescatados", figures.get("animales_rescatados")),
    ]
    visible_metrics = [(key, label, value) for key, label, value in metrics if value is not None]
    updated_fields = set(figures.get("ungrd_updated_fields", []))
    previous_cut = figures.get("corte_ungrd_anterior", "corte anterior")
    return html.Section(
        [
            html.Div(
                [
                    html.Div(line_icon("alert"), className="official-icon"),
                    html.Div(
                        [
                            html.Span("BALANCE NACIONAL · UNGRD"),
                            html.H2("Afectaciones reportadas"),
                            html.P(f"Corte: {figures.get('corte_ungrd', 'no informado')}")
                        ]
                    ),
                ],
                className="official-heading",
            ),
            html.Div(
                [
                    html.Div(
                        [html.Strong(format_number(value)), html.Span(label)]
                        + ([] if key in updated_fields else [html.Small(f"Último valor: {previous_cut}")])
                    )
                    for key, label, value in visible_metrics
                ],
                className="official-grid",
            ),
            html.Div(
                [
                    html.Span("Reporte preliminar sujeto a actualización."),
                    html.A(
                        "Ver publicación oficial de la UNGRD",
                        href=figures.get("ungrd_source_url", "#"),
                        target="_blank",
                        rel="noreferrer",
                    ),
                ],
                className="official-source",
            ),
        ],
        className="official-panel",
    )


def _department_labels(geojson: dict[str, Any]) -> list[dl.DivMarker]:
    labels: list[dl.DivMarker] = []
    for feature in geojson.get("features", []):
        properties = feature.get("properties", {})
        lat, lon = properties.get("label_lat"), properties.get("label_lon")
        name = properties.get("dpto") or properties.get("DPTO_CNMBRE") or ""
        if lat is None or lon is None or not name:
            continue
        short_name = str(name).title().replace("Archipielago De ", "")
        labels.append(dl.DivMarker(
            position=[lat, lon], interactive=False,
            iconOptions={"html": f"<span>{html_lib.escape(short_name)}</span>", "className": "department-label", "iconSize": [112, 18], "iconAnchor": [56, 9]},
        ))
    return labels


def _city_markers(data: dict[str, Any], selected_city: str | None) -> list[dl.CircleMarker]:
    markers = []
    for city in data.get("cities", []):
        selected = city["name"] == selected_city
        radius = min(24, max(9, 8 + math.sqrt(city.get("injured", 0)) / 4))
        markers.append(dl.CircleMarker(
            id={"type": "city-marker", "index": city["name"]}, center=[city["lat"], city["lon"]],
            radius=radius + (3 if selected else 0), color=COLORS["ink"], weight=3 if selected else 1,
            fill=True, fillColor=COLORS["red"] if city.get("alert") == "roja" else COLORS["blue"], fillOpacity=0.9,
            children=[
                dl.Tooltip([html.Strong(city["name"]), html.Br(), html.Span(f"{format_number(city['deaths'])} fallecidos · {format_number(city['injured'])} heridos")], className="map-tooltip"),
                dl.Popup([html.H4(city["name"]), html.P(city.get("summary", "")), html.Small("Seleccione el marcador para abrir la ficha territorial.")], className="map-popup"),
            ],
        ))
    return markers


def _point_markers(data: dict[str, Any], layer: str) -> list[dl.DivMarker]:
    result = []
    for point in data.get("points", []):
        if point.get("lat") is None or point.get("lon") is None:
            continue
        if layer == "blood" and point.get("type") != "sangre":
            continue
        if layer == "aid" and point.get("type") == "sangre":
            continue
        blood = point.get("type") == "sangre"
        result.append(dl.DivMarker(
            position=[point["lat"], point["lon"]],
            iconOptions={"html": f"<span>{'S' if blood else '+'}</span>", "className": "point-marker blood" if blood else "point-marker aid", "iconSize": [30, 30], "iconAnchor": [15, 15]},
            children=[
                dl.Tooltip(f"{point['name']} · {point['city']}", className="map-tooltip"),
                dl.Popup([html.H4(point["name"]), html.P(point.get("organization", "")), html.P(point.get("address", "")), html.Small(f"Tipo: {point.get('type', '').title()}")], className="map-popup"),
            ],
        ))
    return result


def _map_legend() -> html.Div:
    items = [("city", "Ciudad reportada"), ("aid", "Punto de acopio"), ("blood", "Donación de sangre"), ("epicenter", "Epicentro")]
    return html.Div(
        [html.Div("SÍMBOLOS DEL MAPA", className="map-key-title")]
        + [html.Div([html.Span(className=f"legend-symbol {kind}"), html.Span(label)], className="map-key-row") for kind, label in items],
        className="map-key-overlay",
    )


def map_component(data: dict[str, Any], geojson: dict[str, Any], layer: str, selected_city: str | None) -> html.Div:
    layers: list[Any] = [
        dl.TileLayer(url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", attribution="© OpenStreetMap © CARTO", opacity=0.55),
        dl.GeoJSON(
            id="departments-geojson", data=geojson,
            options={"style": {"color": COLORS["cyan"], "weight": 1.15, "fillColor": COLORS["surface_light"], "fillOpacity": 0.28}},
            hoverStyle={"weight": 2.7, "color": COLORS["magenta"], "fillOpacity": 0.42}, zoomToBounds=True,
        ),
        dl.LayerGroup(_department_labels(geojson)),
        dl.LayerGroup(_city_markers(data, selected_city)) if layer == "impact" else dl.LayerGroup(_point_markers(data, layer)),
    ]
    epicenter = data.get("event", {})
    if epicenter.get("lat") is not None and epicenter.get("lon") is not None:
        layers.append(dl.CircleMarker(
            center=[epicenter["lat"], epicenter["lon"]], radius=8, color=COLORS["magenta"], weight=3,
            fill=True, fillColor=COLORS["background"], fillOpacity=1,
            children=dl.Tooltip(f"Epicentro · {epicenter.get('lugar', '')} · M {epicenter.get('magnitud', '')}", className="map-tooltip"),
        ))
    leaflet = dl.Map(
        layers, id="main-map", center=[4.7, -74.6], zoom=5.35, minZoom=4, maxZoom=16,
        scrollWheelZoom=True, zoomControl=True,
        style={"height": "690px", "width": "100%", "background": COLORS["background"]},
    )
    return html.Div([leaflet, _map_legend()], className="map-stage")


def city_detail(data: dict[str, Any], selected_city: str | None) -> html.Div:
    cities = data.get("cities", [])
    if selected_city == ALL_CITIES:
        return html.Div([
            html.Div("PANORAMA GENERAL", className="alert-chip overview-chip"),
            html.H2("Todas las ciudades", className="city-title"),
            html.P(f"{len(cities)} ciudades capitales · cortes territoriales diferenciados", className="city-department"),
            html.Div([
                html.Div([html.Strong(city["name"]), html.Span(f"{format_number(city['deaths'])} fallecidos"), html.Span(f"{format_number(city['injured'])} heridos")], className="city-overview-row")
                for city in cities
            ], className="city-overview-list"),
            html.P("Las fichas combinan las publicaciones locales más recientes disponibles. No sume estas filas: no corresponden a un mismo momento de observación.", className="city-summary"),
        ], className="city-detail-card")

    city = next((item for item in cities if item["name"] == selected_city), cities[0])
    metrics = [
        ("Fallecidos", city["deaths"]),
        ("Heridos", city["injured"]),
        ("Desaparecidos", city["missing"]),
        (city.get("collapsed_label", "Colapsos"), city["collapsed"]),
    ]
    if city.get("rescued") is not None:
        metrics.append(("Rescatados", city["rescued"]))
    source_links = city.get("source_links") or [
        {"label": city.get("source", "No informada"), "url": city.get("source_url", "#")}
    ]
    return html.Div([
        html.Div("ALERTA ROJA" if city.get("alert") == "roja" else "SEGUIMIENTO", className="alert-chip"),
        html.H2(city["name"], className="city-title"), html.P(city.get("department", ""), className="city-department"),
        html.Div([html.Div([html.Strong(format_number(value)), html.Span(label)]) for label, value in metrics], className="city-metrics"),
        html.P(city.get("summary", ""), className="city-summary"), html.H3("Necesidades reportadas", className="sidebar-heading"),
        html.Div([html.Div([line_icon("check", "need-icon"), html.Div([html.Strong(need[1]), html.P(need[2])])], className="need-row") for need in city.get("needs", [])], className="needs-list"),
        html.Div(
            [
                html.Span(f"Corte: {city.get('cut', 'no informado')}"),
                html.Br(),
                html.Span("Fuentes territoriales:"),
                html.Div(
                    [
                        html.A(link.get("label", "Fuente"), href=link.get("url", "#"), target="_blank", rel="noreferrer")
                        for link in source_links
                    ],
                    className="city-source-links",
                ),
            ],
            className="city-source",
        ),
    ], className="city-detail-card")


def point_list(data: dict[str, Any], layer: str, selected_city: str | None) -> html.Div:
    points = data.get("points", [])
    filtered = [point for point in points if layer != "blood" or point.get("type") == "sangre"]
    filtered = [point for point in filtered if layer != "aid" or point.get("type") != "sangre"]
    same_city = [] if selected_city == ALL_CITIES else [point for point in filtered if point.get("city") == selected_city]
    display = (same_city or filtered)[:12]
    return html.Div([
        html.Div([html.Div("SANGRE" if point.get("type") == "sangre" else "ACOPIO", className=f"point-type {point.get('type')}"), html.Strong(point["name"]), html.Span(point.get("city", "")), html.P(point.get("address", ""))], className="point-card")
        for point in display
    ] or [html.P("No hay puntos publicados para este filtro.", className="empty-state")], className="points-list")


DONATION_ICONS = {
    "alimentos": "box", "agua": "drop", "dormir": "shelter", "aseo": "care", "emergencia": "tool",
    "cocina": "box", "mascotas": "paw", "sangre": "drop", "dinero": "money",
}


def _matching_points(item: dict[str, Any], data: dict[str, Any]) -> list[dict[str, Any]]:
    if item.get("tipo") == "sangre":
        return [point for point in data.get("points", []) if point.get("type") == "sangre"]
    return [point for point in data.get("points", []) if item.get("id") in point.get("accepted", [])]


def donation_cards(data: dict[str, Any]) -> list[html.Article]:
    cards = []
    for item in data.get("what_to_donate", []):
        matches = _matching_points(item, data)
        if item.get("tipo") == "dinero":
            cash = data.get("cash_donation", {})
            location_content: Any = html.A("Abrir canal oficial de donación", href=cash.get("url", "#"), target="_blank", rel="noreferrer", className="donation-link")
        elif matches:
            location_content = html.Details([
                html.Summary(f"Ver dónde recibirlo · {len(matches)} punto{'s' if len(matches) != 1 else ''}"),
                html.Div([html.Div([html.Strong(f"{point['city']} · {point['name']}"), html.Span(point.get("address", "Dirección no publicada"))], className="donation-location") for point in matches], className="donation-locations"),
            ])
        else:
            location_content = html.P("No hay un punto específico asociado en la fuente. Confirme antes de desplazarse.", className="no-location")
        cards.append(html.Article([
            html.Div(line_icon(DONATION_ICONS.get(item.get("id"), "box")), className="donation-icon"),
            html.H3(item.get("nombre", "Artículo")), html.P(item.get("detalle", ""), className="donation-description"),
            html.Div([html.Span("DÓNDE", className="where-label"), location_content], className="where-block"),
        ], className="donation-card"))
    return cards


def forensic_panel(data: dict[str, Any]) -> html.Section:
    forensic = data.get("forensics", {})
    metrics = [
        ("Cuerpos recibidos", forensic.get("bodies_received")), ("Víctimas identificadas", forensic.get("victims_identified")),
        ("Entregados a familiares", forensic.get("bodies_delivered")), ("Menores identificados", forensic.get("minors_identified")),
    ]
    identified = forensic.get("victims_identified") or 1
    sex_rows = forensic.get("sex", [])
    age = forensic.get("age", {})
    age_rows = age.get("bands", [])
    unit_rows = forensic.get("forensic_units", [])
    foreign_identified = forensic.get("foreign_citizens_identified")
    profile_note = (
        "Perfil agregado de las víctimas identificadas por Medicina Legal. "
        "No se publican nombres ni registros individuales y este universo no equivale "
        "al consolidado territorial de fallecidos de la UNGRD."
    )
    if foreign_identified is not None:
        profile_note += f" El comunicado registra además {format_number(foreign_identified)} ciudadanos extranjeros identificados."

    def distribution_rows(items: list[dict[str, Any]], color_class: str) -> html.Div:
        return html.Div(
            [
                html.Div(
                    [
                        html.Div([html.Span(item["label"]), html.Strong(f"{format_number(item['value'])} · {format(item['value'] / identified, '.1%').replace('.', ',')}")], className="distribution-label"),
                        html.Div(html.I(style={"width": f"{item['value'] / identified * 100:.1f}%"}), className=f"distribution-track {color_class}"),
                    ],
                    className="distribution-row",
                )
                for item in items
            ],
            className="distribution-list",
        )

    return html.Section([
        html.Div([html.Div(line_icon("forensic"), className="forensic-icon"), html.Div([html.Span("MÓDULO FORENSE"), html.H2("Identificación y entrega digna")])], className="forensic-heading"),
        html.P(profile_note, className="forensic-method"),
        html.Div([html.Div([html.Strong(format_number(value)), html.Span(label)]) for label, value in metrics], className="forensic-grid"),
        html.Div(
            [
                html.Div([html.H3("Distribución por sexo"), distribution_rows(sex_rows, "sex")], className="forensic-distribution-card"),
                html.Div(
                    [
                        html.H3("Distribución por edad"),
                        html.P(f"Media {str(age.get('mean', '—')).replace('.', ',')} años · mediana {age.get('median', '—')} · rango {age.get('min', '—')} a {age.get('max', '—')}", className="forensic-statline"),
                        distribution_rows(age_rows, "age"),
                    ],
                    className="forensic-distribution-card",
                ),
            ],
            className="forensic-distributions",
        ),
        html.Div(
            [
                html.H3("Unidad forense de procesamiento o reporte"),
                html.Div([html.Div([html.Strong(format_number(item["value"])), html.Span(item["label"])]) for item in unit_rows], className="forensic-units"),
                html.P(forensic.get("methodology", ""), className="forensic-methodology-note"),
            ],
            className="forensic-units-block",
        ),
        html.Div([html.Span(f"{forensic.get('report', 'Comunicado oficial')} · corte: {forensic.get('cut', 'no informado')}"), html.A("Ver publicación oficial", href=forensic.get("source_url", "#"), target="_blank", rel="noreferrer")], className="forensic-source"),
    ], className="forensic-panel")
