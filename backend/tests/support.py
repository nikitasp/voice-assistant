from pathlib import Path
from typing import Any

import yaml

DATA_DIR = Path(__file__).parent / "data"

TEST_LIVEKIT_ENV = {
    "LIVEKIT_PUBLIC_URL": "ws://livekit.test:7880",
    "LIVEKIT_API_KEY": "test-api-key",
    "LIVEKIT_API_SECRET": "test-api-secret-that-is-long-enough-for-hs256",
}


def load_data(name: str) -> Any:
    with (DATA_DIR / name).open() as f:
        return yaml.safe_load(f)
