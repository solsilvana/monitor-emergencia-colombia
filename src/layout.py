"""Composición de la página principal del tablero."""
from __future__ import annotations

from typing import Any

from dash import dcc, html

from src.components import (
    ALL_CITIES,
    city_detail,
    donation_cards,
    forensic_panel,
    kpi_cards,
    map_component,
    national_balance_panel,
    point_list,
)


def _source_cards(data: dict[str, Any]) -> list[html.Div]:
    figures = data.get("figures", {})
    references: list[dict[str, str]] = [
        {
            "titulo": f"UNGRD · Balance nacional del {figures.get('corte_ungrd', 'último corte')}",
            "url": figures.get("ungrd_source_url", "#"),
        },
        {
            "titulo": "Asocapitales · Informe Consolidado No. 22",
            "url": figures.get("asocapitales_pdf_url", figures.get("asocapitales_source_url", "#")),
        },
    ]
    forensic = data.get("forensics", {})
    references.append({"titulo": f"Medicina Legal · {forensic.get('report', 'Comunicado oficial')}", "url": forensic.get("source_url", "#")})
    for city in data.get("cities", []):
        if city.get("name") not in {"Cali", "Pereira", "Quibdó"}:
            continue
        source_links = city.get("source_links") or [
            {"label": city.get("source", "Reporte territorial"), "url": city.get("source_url", "#")}
        ]
        for source in source_links:
            references.append({"titulo": f"{city['name']} · {source.get('label', 'Reporte territorial')}", "url": source.get("url", "#")})
    cards = []
    for reference in references:
        if isinstance(reference, dict):
            label = reference.get("nombre") or reference.get("titulo") or reference.get("fuente") or "Fuente"
            url = reference.get("url") or "#"
        else:
            label, url = str(reference), "#"
        cards.append(html.Div([html.Span("FUENTE VERIFICABLE"), html.A(label, href=url, target="_blank", rel="noreferrer")], className="source-card"))
    return cards


def _brand_header() -> html.Header:
    return html.Header(
        [
            html.Div(
                [html.Div("SZ", className="brand-monogram"), html.Div([html.Strong("SOL SILVANA ZB"), html.Span("EpiSIG · mapas, datos y epidemiología")])],
                className="brand-lockup",
            ),
            html.Div([html.Span("CENTRO DE SITUACIÓN"), html.I(className="live-dot"), html.Strong("EMERGENCIA ACTIVA")], className="header-status"),
            html.Div(
                [html.A("X  @solsilvanazb", href="https://x.com/solsilvanazb", target="_blank", rel="noreferrer"), html.A("IG  @solsilvanazb_episig", href="https://instagram.com/solsilvanazb_episig", target="_blank", rel="noreferrer")],
                className="header-social",
            ),
        ],
        className="brand-header",
    )


def build_layout(data: dict[str, Any], geojson: dict[str, Any], run_log: dict[str, Any]) -> html.Div:
    event = data.get("event", {})
    figures = data.get("figures", {})
    status_class = "status-ok" if run_log.get("status") == "updated" else "status-cache"
    status_text = "Fuentes consultadas y caché verificada" if run_log.get("status") == "updated" else "Modo local · último corte validado"

    city_options = [{"label": "Todas las ciudades", "value": ALL_CITIES}] + [
        {"label": city["name"], "value": city["name"]} for city in data["cities"]
    ]

    return html.Div(
        [
            dcc.Store(id="data-version", data=data["meta"].get("downloaded_at")),
            _brand_header(),
            html.Main(
                [
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.Div([html.Span("MONITOR TERRITORIAL"), html.Span("SALUD PÚBLICA")], className="hero-tags"),
                                    html.P("TERREMOTO · COLOMBIA", className="hero-kicker"),
                                    html.H1(["Datos para ", html.Span("orientar la respuesta")]),
                                    html.P("Afectaciones, identificación forense, necesidades y puntos de ayuda en un tablero independiente y reproducible en Python.", className="hero-copy"),
                                    html.Div(
                                        [
                                            html.Div([html.Span("MAGNITUD"), html.Strong(event.get("magnitud", "—"))]),
                                            html.Div([html.Span("EPICENTRO"), html.Strong(event.get("lugar", "No informado"))]),
                                            html.Div([html.Span("FECHA"), html.Strong(event.get("fecha", "No informada"))]),
                                        ],
                                        className="event-facts",
                                    ),
                                ],
                                className="hero-content",
                            ),
                            html.Div(
                                [
                                    html.Div([html.Span("ÚLTIMOS CORTES OFICIALES"), html.Strong(data["meta"].get("cut", "Sin corte informado"), id="cut-value")], className="cut-block"),
                                    html.Div(status_text, id="update-result", className=f"update-status {status_class}"),
                                    html.Button([html.Span("↻"), "Actualizar fuentes"], id="update-data-button", n_clicks=0, className="update-button"),
                                    html.P("UNGRD + Asocapitales + entidades territoriales + Medicina Legal. Si no hay internet se conserva el último corte validado."),
                                ],
                                className="update-panel",
                            ),
                        ],
                        className="hero",
                    ),
                    html.Section(
                        [html.Div([html.Span("01"), html.Div([html.H2("Indicadores para la respuesta"), html.P("Cada tarjeta conserva su fuente y universo de medición.")])], className="section-heading"), html.Div(kpi_cards(data), id="kpi-container", className="kpi-grid")],
                        className="section-block kpi-section",
                    ),
                    national_balance_panel(data),
                    html.Section(
                        [
                            html.Div(
                                [
                                    html.Div([html.Span("02"), html.Div([html.H2("Lectura territorial"), html.P("Explore afectaciones, acopio y donación de sangre.")])], className="section-heading compact"),
                                    html.Div(
                                        [
                                            dcc.Dropdown(id="city-dropdown", options=city_options, value=ALL_CITIES, clearable=False, searchable=True, className="city-dropdown"),
                                            dcc.RadioItems(
                                                id="layer-filter",
                                                options=[{"label": "Afectación", "value": "impact"}, {"label": "Acopio", "value": "aid"}, {"label": "Sangre", "value": "blood"}],
                                                value="impact", inline=True, className="layer-filter",
                                            ),
                                        ],
                                        className="map-controls",
                                    ),
                                ],
                                className="map-panel-header",
                            ),
                            html.Div(
                                [
                                    html.Div(map_component(data, geojson, "impact", ALL_CITIES), id="map-container", className="map-container"),
                                    html.Aside(city_detail(data, ALL_CITIES), id="city-detail", className="sidebar-panel"),
                                ],
                                className="map-grid",
                            ),
                        ],
                        className="section-block map-section",
                    ),
                    forensic_panel(data),
                    html.Section(
                        [html.Div([html.Span("03"), html.Div([html.H2("Puntos habilitados"), html.P("Direcciones publicadas según la capa y ciudad seleccionadas.")])], className="section-heading"), html.Div(point_list(data, "impact", ALL_CITIES), id="point-list")],
                        className="section-block",
                    ),
                    html.Section(
                        [
                            html.Div([html.Span("04"), html.Div([html.H2("Qué donar y dónde llevarlo"), html.P("Abra cada tarjeta para consultar los puntos que reciben ese elemento.")])], className="section-heading"),
                            html.Div(donation_cards(data), className="donation-grid"),
                        ],
                        className="section-block donation-section",
                    ),
                    html.Section(
                        [
                            html.Div([html.Span("05"), html.Div([html.H2("Fuentes y trazabilidad"), html.P("Datos recopilados de varias fuentes según disponibilidad.")])], className="section-heading"),
                            html.P("Python extrae, normaliza y valida los datos antes de reemplazar el corte local. Los indicadores forenses se mantienen separados del consolidado territorial para no confundir universos.", className="method-copy"),
                            html.Div(_source_cards(data), className="sources-grid"),
                        ],
                        className="section-block methodology-section",
                    ),
                ],
                className="dashboard-main",
            ),
            html.Footer(
                [
                    html.Div([html.Strong("SOL SILVANA ZB · EpiSIG"), html.Span("Divulgación, mapas, datos y epidemiología")]),
                    html.Div([html.Strong("X @solsilvanazb"), html.Strong("IG @solsilvanazb_episig")]),
                    html.P("Tablero independiente basado en información reportada por la UNGRD, Asocapitales, Cruz Roja, entidades territoriales y Medicina Legal, según disponibilidad. No reemplaza reportes oficiales."),
                ],
                className="footer",
            ),
        ],
        className="app-shell",
    )
