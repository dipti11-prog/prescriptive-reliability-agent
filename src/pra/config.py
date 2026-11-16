"""config.py - load the asset definition and FMEA library from the knowledge/ folder."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE = ROOT / "knowledge"


@lru_cache
def load_asset(path: str | None = None) -> dict:
    with open(path or KNOWLEDGE / "asset_k101.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def load_fmea(path: str | None = None) -> list[dict]:
    with open(path or KNOWLEDGE / "fmea_centrifugal_compressor.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)["failure_modes"]


def fmea_by_id() -> dict[str, dict]:
    return {fm["id"]: fm for fm in load_fmea()}
