"""Helpers for authenticating against Google Earth Engine."""
from __future__ import annotations

import ee

# Project ID for this workflow
PROJECT_ID = "qgis-forest-vladimirfominov49"


def initialize_ee(project_id: str | None = None) -> None:
    """Authenticate and initialize the ee API if needed."""
    pid = project_id or PROJECT_ID
    try:
        ee.Initialize(project=pid)
        print(f"Earth Engine initialized with project {pid}")
    except Exception:
        print("Authentication required. Attempting to authenticate...")
        ee.Authenticate()
        ee.Initialize(project=pid)
        print(f"Authenticated and initialized with project {pid}")
