"""CMB-0016 — Gaia DR3 map for RA 03:13:00.22, Dec -20:01:35.7.

Run with:
    %run CMB-0016.py

This version reuses the working black-background Gaia summary widget and points it
at the new coordinate supplied by the user.
"""

from __future__ import annotations

import urllib.error
import urllib.request

SOURCE_URL = (
    "https://raw.githubusercontent.com/gear66me-ui/"
    "CMB-Plank/main/CMB-0013.py"
)


def _load_source() -> str:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/16.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise RuntimeError(
            "Unable to load CMB-0013.py from GitHub. Check the internet "
            f"connection. Details: {exc}"
        ) from exc


source = _load_source()

replacements = [
    ('VERSION = "CMB-0013"', 'VERSION = "CMB-0016"'),
    ('RA_SEXAGESIMAL = "03:12:59.96"', 'RA_SEXAGESIMAL = "03:13:00.22"'),
    ('DEC_SEXAGESIMAL = "-20:02:09.0"', 'DEC_SEXAGESIMAL = "-20:01:35.7"'),
    ('RA_DEG = 48.2498333333', 'RA_DEG = 48.2509166667'),
    ('DEC_DEG = -20.0358333333', 'DEC_DEG = -20.0265833333'),
    ('Mozilla/5.0 CMB-Gaia-Widget/13.0', 'Mozilla/5.0 CMB-Gaia-Widget/16.0'),
]

for old, new in replacements:
    if old not in source:
        raise RuntimeError(f"Could not safely update coordinate widget; missing: {old}")
    source = source.replace(old, new, 1)

namespace = {"__name__": "__main__", "__file__": "CMB-0016.py"}
exec(compile(source, "CMB-0016.py", "exec"), namespace, namespace)
