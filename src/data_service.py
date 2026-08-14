"""Extracción, normalización, validación y persistencia de los datos.

La fuente de Economía para la Pipol publica dos objetos JSON dentro del HTML:
`window.__DATOS__` y `window.__GEO__`. Este módulo los extrae sin ejecutar
JavaScript y guarda una copia local validada. Si internet falla, Dash continúa
funcionando con ese último corte.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import requests

from config import (
    ECONOMIA_PIPOL_URL,
    FORENSIC_DATA_FILE,
    GEOJSON_FILE,
    LATEST_DATA_FILE,
    MEDLEGAL_REPORT_URL,
    OVERRIDES_FILE,
    REQUEST_TIMEOUT,
    RUN_LOG_FILE,
)


class DataValidationError(ValueError):
    """Se lanza cuando un corte no cumple las reglas mínimas de calidad."""


def _extract_window_json(html: str, variable: str) -> dict[str, Any]:
    pattern = rf"window\.{re.escape(variable)}\s*=\s*(\{{.*?\}});\s*</script>"
    match = re.search(pattern, html, flags=re.DOTALL)
    if not match:
        raise DataValidationError(f"No se encontró window.{variable} en la fuente.")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise DataValidationError(f"window.{variable} no contiene JSON válido.") from exc


def _ring_area(ring: list[list[float]]) -> float:
    """Área firmada de un anillo; se usa para escoger el polígono principal."""
    return sum(
        float(ring[index][0]) * float(ring[(index + 1) % len(ring)][1])
        - float(ring[(index + 1) % len(ring)][0]) * float(ring[index][1])
        for index in range(len(ring))
    ) / 2


def _ring_centroid(ring: list[list[float]]) -> tuple[float, float]:
    area = _ring_area(ring)
    if abs(area) < 1e-12:
        return float(ring[0][0]), float(ring[0][1])
    cx = cy = 0.0
    for index in range(len(ring)):
        x1, y1 = map(float, ring[index][:2])
        x2, y2 = map(float, ring[(index + 1) % len(ring)][:2])
        cross = x1 * y2 - x2 * y1
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    return cx / (6 * area), cy / (6 * area)


def _inside_ring(point: tuple[float, float], ring: list[list[float]]) -> bool:
    """Prueba punto-en-polígono por ray casting, sin dependencias geográficas."""
    x, y = point
    inside = False
    previous = ring[-1]
    for current in ring:
        x1, y1 = map(float, previous[:2])
        x2, y2 = map(float, current[:2])
        if (y1 > y) != (y2 > y):
            intersection = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < intersection:
                inside = not inside
        previous = current
    return inside


def _interior_label_point(geometry: dict[str, Any]) -> tuple[float, float] | None:
    """Calcula un punto que queda dentro del polígono principal del departamento."""
    coordinates = geometry.get("coordinates", [])
    polygons = coordinates if geometry.get("type") == "MultiPolygon" else [coordinates]
    exterior_rings = [polygon[0] for polygon in polygons if polygon and len(polygon[0]) >= 3]
    if not exterior_rings:
        return None
    ring = max(exterior_rings, key=lambda item: abs(_ring_area(item)))
    centroid = _ring_centroid(ring)
    if _inside_ring(centroid, ring):
        return centroid

    # En polígonos cóncavos el centroide puede caer afuera. Se busca el tramo
    # horizontal interior más ancho y se coloca allí la etiqueta.
    ys = [float(point[1]) for point in ring]
    min_y, max_y = min(ys), max(ys)
    best: tuple[float, float, float] | None = None
    for step in range(1, 60):
        y = min_y + (max_y - min_y) * step / 60
        intersections: list[float] = []
        previous = ring[-1]
        for current in ring:
            x1, y1 = map(float, previous[:2])
            x2, y2 = map(float, current[:2])
            if (y1 > y) != (y2 > y):
                intersections.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            previous = current
        intersections.sort()
        for index in range(0, len(intersections) - 1, 2):
            width = intersections[index + 1] - intersections[index]
            candidate = ((intersections[index] + intersections[index + 1]) / 2, y, width)
            if best is None or candidate[2] > best[2]:
                best = candidate
    return (best[0], best[1]) if best else (float(ring[0][0]), float(ring[0][1]))


def _add_label_coordinates(geojson: dict[str, Any]) -> dict[str, Any]:
    """Agrega a cada departamento un punto de etiqueta situado en su interior."""
    enriched = deepcopy(geojson)
    for feature in enriched.get("features", []):
        point = _interior_label_point(feature.get("geometry", {}))
        if point is None:
            continue
        feature.setdefault("properties", {})["label_lon"] = round(point[0], 5)
        feature["properties"]["label_lat"] = round(point[1], 5)
    return enriched


def validate_source(data: dict[str, Any], geojson: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"puntos", "ciudades", "queDonar", "epicentro", "cifras", "referencias"}
    missing = required - data.keys()
    if missing:
        errors.append(f"Faltan bloques en __DATOS__: {', '.join(sorted(missing))}")
    if len(data.get("puntos", [])) < 1:
        errors.append("La fuente no contiene puntos de ayuda.")
    if len(data.get("ciudades", [])) < 5:
        errors.append("La fuente contiene menos de cinco ciudades.")
    if len(geojson.get("features", [])) < 30:
        errors.append("La capa geográfica no contiene los departamentos esperados.")
    for city in data.get("ciudades", []):
        for field in ("lat", "lon", "fallecidos", "heridos"):
            if field not in city:
                errors.append(f"{city.get('ciudad', 'Ciudad')}: falta {field}.")
        if (city.get("fallecidos") or 0) < 0 or (city.get("heridos") or 0) < 0:
            errors.append(f"{city.get('ciudad')}: cifras negativas.")
    return errors


def normalize(data: dict[str, Any]) -> dict[str, Any]:
    """Crea el esquema estable consumido por Dash."""
    cities = []
    for city in data["ciudades"]:
        cities.append(
            {
                "name": city["ciudad"],
                "department": city.get("dpto", ""),
                "alert": city.get("alerta", ""),
                "lat": city["lat"],
                "lon": city["lon"],
                "deaths": city.get("fallecidos") or 0,
                "injured": city.get("heridos") or 0,
                "collapsed": city.get("colapsos") or 0,
                "missing": city.get("desaparecidos") or 0,
                "trapped": city.get("atrapados") or 0,
                "summary": city.get("resumen", ""),
                "needs": city.get("necesidades", []),
                "source": city.get("fuente", ""),
            }
        )

    points = []
    for point in data["puntos"]:
        points.append(
            {
                "id": point.get("id", ""),
                "name": point.get("nombre", "Punto de ayuda"),
                "organization": point.get("org", ""),
                "city": point.get("ciudad", ""),
                "type": point.get("tipo", "acopio"),
                "address": point.get("dir", ""),
                "lat": point.get("lat"),
                "lon": point.get("lon"),
                "phone": point.get("tel", ""),
                "hours": point.get("horario", ""),
                "precision": point.get("precision", ""),
                "source": point.get("fuente", ""),
                "accepted": point.get("acepta", []),
            }
        )

    figures = data["cifras"]
    return {
        "meta": {
            "source": "Economía para la Pipol",
            "source_url": ECONOMIA_PIPOL_URL,
            "cut": figures.get("corte", "Sin corte informado"),
            "downloaded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "status": "preliminar",
        },
        "event": data["epicentro"],
        "figures": figures,
        "cities": cities,
        "points": points,
        "what_to_donate": data.get("queDonar", []),
        "cash_donation": data.get("dinero", {}),
        "alert_departments": data.get("dptosAlerta", []),
        "references": data.get("referencias", []),
    }


def apply_manual_overrides(data: dict[str, Any]) -> dict[str, Any]:
    """Aplica correcciones explícitas sin esconder el dato original.

    El archivo se entrega desactivado. Cuando `enabled` es true, se pueden
    corregir figuras generales y campos de una ciudad por su nombre.
    """
    if not OVERRIDES_FILE.exists():
        return data
    overrides = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    if not overrides.get("enabled", False):
        return data
    result = deepcopy(data)
    result["figures"].update(overrides.get("figures", {}))
    city_overrides = overrides.get("cities", {})
    for city in result.get("cities", []):
        city.update(city_overrides.get(city["name"], {}))
    if overrides.get("cut_note"):
        result["meta"]["cut"] = overrides["cut_note"]
        result["meta"]["manual_override"] = True
    return result


def load_forensic_data() -> dict[str, Any]:
    if not FORENSIC_DATA_FILE.exists():
        return {}
    result = json.loads(FORENSIC_DATA_FILE.read_text(encoding="utf-8"))
    result["source_url"] = MEDLEGAL_REPORT_URL
    return result


def validate_forensic_snapshot(forensic: dict[str, Any]) -> list[str]:
    """Valida el corte agregado de Medicina Legal sin exponer registros nominales."""
    errors: list[str] = []
    identified = forensic.get("victims_identified")
    if not isinstance(identified, int) or identified < 0:
        return ["Medicina Legal: victims_identified no es un entero válido."]
    for field in ("bodies_received", "bodies_delivered", "minors_identified"):
        if not isinstance(forensic.get(field), int) or forensic[field] < 0:
            errors.append(f"Medicina Legal: {field} no es un entero válido.")
    for field in ("sex", "forensic_units"):
        if sum(item.get("value", 0) for item in forensic.get(field, [])) != identified:
            errors.append(f"Medicina Legal: {field} no suma {identified} identificados.")
    age_bands = forensic.get("age", {}).get("bands", [])
    if sum(item.get("value", 0) for item in age_bands) != identified:
        errors.append(f"Medicina Legal: los grupos de edad no suman {identified} identificados.")
    return errors


def refresh_from_source() -> dict[str, Any]:
    """Descarga, valida y guarda el corte actual del tablero fuente."""
    response = requests.get(
        ECONOMIA_PIPOL_URL,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": "SolSilvanaZB-Emergency-Dashboard/2.0"},
    )
    response.raise_for_status()
    raw_data = _extract_window_json(response.text, "__DATOS__")
    raw_geo = _extract_window_json(response.text, "__GEO__")
    errors = validate_source(raw_data, raw_geo)
    if errors:
        raise DataValidationError(" | ".join(errors))

    # La caché conserva siempre el dato original. Las correcciones de la usuaria
    # se aplican únicamente al leerlo, de modo que puedan activarse o desactivarse.
    normalized = normalize(raw_data)
    enriched_geo = _add_label_coordinates(raw_geo)
    LATEST_DATA_FILE.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    GEOJSON_FILE.write_text(
        json.dumps(enriched_geo, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    forensic = load_forensic_data()
    forensic_errors = validate_forensic_snapshot(forensic)
    forensic_status = "verified_snapshot" if not forensic_errors else "invalid_snapshot"
    run_log = {
        "status": "updated",
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": ECONOMIA_PIPOL_URL,
        "source_sha256": hashlib.sha256(response.content).hexdigest(),
        "cities": len(normalized["cities"]),
        "points": len(normalized["points"]),
        "departments": len(enriched_geo["features"]),
        "validation_errors": forensic_errors,
        "forensic_source": forensic_status,
        "forensic_identified": forensic.get("victims_identified"),
    }
    RUN_LOG_FILE.write_text(json.dumps(run_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return run_log


def safe_refresh() -> dict[str, Any]:
    """Intenta actualizar; nunca destruye el último corte local válido."""
    try:
        return refresh_from_source()
    except Exception as exc:  # La aplicación debe seguir funcionando sin internet.
        forensic = load_forensic_data()
        forensic_errors = validate_forensic_snapshot(forensic)
        forensic_status = "verified_snapshot" if not forensic_errors else "invalid_snapshot"
        run_log = {
            "status": "offline_cache",
            "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source": ECONOMIA_PIPOL_URL,
            "error": f"{type(exc).__name__}: {exc}",
            "validation_errors": forensic_errors,
            "forensic_source": forensic_status,
            "forensic_identified": forensic.get("victims_identified"),
        }
        RUN_LOG_FILE.write_text(json.dumps(run_log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not LATEST_DATA_FILE.exists() or not GEOJSON_FILE.exists():
            raise RuntimeError("No fue posible actualizar y tampoco existe un corte local.") from exc
        return run_log


def load_data() -> dict[str, Any]:
    cached = json.loads(LATEST_DATA_FILE.read_text(encoding="utf-8"))
    result = apply_manual_overrides(cached)
    result["forensics"] = load_forensic_data()
    return result


def load_geojson() -> dict[str, Any]:
    return json.loads(GEOJSON_FILE.read_text(encoding="utf-8"))


def load_run_log() -> dict[str, Any]:
    if not RUN_LOG_FILE.exists():
        return {"status": "not_run"}
    return json.loads(RUN_LOG_FILE.read_text(encoding="utf-8"))


def copy_snapshot(destination: Path) -> None:
    """Utilidad para respaldar manualmente el último corte normalizado."""
    destination.write_text(LATEST_DATA_FILE.read_text(encoding="utf-8"), encoding="utf-8")
