from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from app.schemas.property import PropertyInfoResponse

PROPERTY_PATH = Path(__file__).resolve().parents[1] / "seed" / "property.yaml"


@lru_cache
def load_property_info(path: Path = PROPERTY_PATH) -> PropertyInfoResponse:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return PropertyInfoResponse.model_validate(data)
