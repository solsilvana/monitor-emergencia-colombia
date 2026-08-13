#!/usr/bin/env python3
"""Ejecuta controles legibles sobre los archivos locales del tablero."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import GEOJSON_FILE, LATEST_DATA_FILE  # noqa: E402
from src.data_service import _inside_ring, load_data, load_geojson  # noqa: E402


def main() -> int:
    data = load_data()
    geo = load_geojson()
    problems: list[str] = []
    if len(data.get("cities", [])) < 5:
        problems.append("Hay menos de cinco ciudades en el corte local.")
    if len(data.get("points", [])) < 1:
        problems.append("No hay puntos de ayuda.")
    if len(geo.get("features", [])) != 33:
        problems.append("La capa no contiene los 33 polígonos departamentales esperados.")
    for feature in geo.get("features", []):
        properties = feature.get("properties", {})
        point = (properties.get("label_lon"), properties.get("label_lat"))
        rings = [polygon[0] for polygon in feature.get("geometry", {}).get("coordinates", []) if polygon]
        if None in point or not any(_inside_ring(point, ring) for ring in rings):
            problems.append(f"La etiqueta de {properties.get('dpto', 'un departamento')} está fuera del polígono.")
    for city in data.get("cities", []):
        if city.get("deaths", 0) < 0 or city.get("injured", 0) < 0:
            problems.append(f"{city['name']} tiene una cifra negativa.")
    figures = data.get("figures", {})
    city_totals = {
        "fallecidos": sum(city.get("deaths", 0) for city in data.get("cities", [])),
        "heridos": sum(city.get("injured", 0) for city in data.get("cities", [])),
        "desaparecidos": sum(city.get("missing", 0) for city in data.get("cities", [])),
        "colapsos": sum(city.get("collapsed", 0) for city in data.get("cities", [])),
    }
    for field, total in city_totals.items():
        if figures.get(field) != total:
            problems.append(
                f"El total de {field} por ciudad ({total}) no coincide con el consolidado ({figures.get(field)})."
            )
    if figures.get("fallecidos_pais", 0) < figures.get("fallecidos", 0):
        problems.append("El total nacional de fallecidos es menor que el total de capitales.")
    forensic = data.get("forensics", {})
    for field in ("bodies_received", "victims_identified", "bodies_delivered"):
        if not isinstance(forensic.get(field), int) or forensic[field] < 0:
            problems.append(f"Medicina Legal: {field} no es un entero válido.")

    print(f"Archivo de datos: {LATEST_DATA_FILE}")
    print(f"Capa geográfica: {GEOJSON_FILE}")
    print(f"Corte: {data['meta'].get('cut')}")
    print(
        "UNGRD nacional: "
        f"{figures.get('fallecidos_pais')} fallecidos · "
        f"{figures.get('heridos_pais')} heridos · "
        f"{figures.get('desaparecidos_pais')} desaparecidos"
    )
    print(
        "Asocapitales: "
        f"{figures.get('fallecidos')} fallecidos · "
        f"{figures.get('heridos')} heridos · "
        f"{figures.get('desaparecidos')} desaparecidos · "
        f"{figures.get('colapsos')} estructuras colapsadas"
    )
    print(f"Ciudades: {len(data['cities'])}")
    print(f"Puntos: {len(data['points'])}")
    print(f"Departamentos: {len(geo['features'])}")
    print("Etiquetas interiores: verificadas")
    print(f"Víctimas identificadas por Medicina Legal: {forensic.get('victims_identified', 'No disponible')}")
    if problems:
        print("\nVALIDACIÓN FALLIDA")
        print("\n".join(f"- {problem}" for problem in problems))
        return 2
    print("\nVALIDACIÓN APROBADA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
