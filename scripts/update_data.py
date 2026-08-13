#!/usr/bin/env python3
"""Actualiza manualmente el último corte local y muestra el resultado."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_service import refresh_from_source  # noqa: E402


if __name__ == "__main__":
    result = refresh_from_source()
    print(json.dumps(result, ensure_ascii=False, indent=2))
