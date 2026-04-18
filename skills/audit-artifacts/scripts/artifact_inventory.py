#!/usr/bin/env python3

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
IMPORT_PATH_CANDIDATES = (
    SCRIPT_DIR.parent / "lib",
    SCRIPT_DIR.parents[2] / "lib",
    SCRIPT_DIR.parents[1] / "lib",
)

for candidate in reversed(IMPORT_PATH_CANDIDATES):
    if candidate.is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from workflow_state.inventory import (  # noqa: E402,F401
    iter_subfeature_dirs,
    iter_traceability_records,
    load_inventory,
    normalize_dir_relpath,
    normalize_registry_path,
    parse_traceability_records,
    planning_row_artifact_type,
    resolve_context,
)
from workflow_state.models import (  # noqa: E402,F401
    Inventory,
    InventoryContext,
    RegistryStatus,
    TraceabilityRecord,
)
__all__ = [
    "Inventory",
    "InventoryContext",
    "RegistryStatus",
    "TraceabilityRecord",
    "iter_subfeature_dirs",
    "iter_traceability_records",
    "load_inventory",
    "normalize_dir_relpath",
    "normalize_registry_path",
    "parse_traceability_records",
    "planning_row_artifact_type",
    "resolve_context",
]
