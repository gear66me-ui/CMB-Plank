"""CMB-0022 — Sagittarius A* multi-survey map with Gaia overlay and crosshair intensity profiles."""
from __future__ import annotations

import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0021.py"
request = urllib.request.Request(
    SOURCE_URL,
    headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/22.0"},
)
with urllib.request.urlopen(request, timeout=60) as response:
    source = response.read().decode("utf-8")

replacements = [
    ('VERSION = "CMB-0020"', 'VERSION = "CMB-0022"'),
    ('VERSION = "CMB-0021"', 'VERSION = "CMB-0022"'),
    ('RA_SEXAGESIMAL = "03:19:30.85"', 'RA_SEXAGESIMAL = "17:45:40.03"'),
    ('DEC_SEXAGESIMAL = "-21:45:24.1"', 'DEC_SEXAGESIMAL = "-29:00:28.2"'),
    ('RA_DEG = 49.8785416667', 'RA_DEG = 266.4167916667'),
    ('DEC_DEG = -21.7566944444', 'DEC_DEG = -29.0078333333'),
    ('Mozilla/5.0 CMB-Gaia-Widget/20.0', 'Mozilla/5.0 CMB-Gaia-Widget/22.0'),
    ('Mozilla/5.0 CMB-Gaia-Widget/21.0', 'Mozilla/5.0 CMB-Gaia-Widget/22.0'),
]
for old, new in replacements:
    source = source.replace(old, new)

source = source.replace(
    'value="DSS2 color — reliable"',
    'value="WISE color infrared"',
    1,
)
source = source.replace(
    "The cyan crosshair is fixed on the supplied sky coordinate.",
    "The cyan crosshair is fixed on Sagittarius A*. Gaia crosses mark nearby optical catalogue sources; Sagittarius A* itself is not a normal Gaia star.",
    1,
)

required = [
    'RA_SEXAGESIMAL = "17:45:40.03"',
    'DEC_SEXAGESIMAL = "-29:00:28.2"',
    'RA_DEG = 266.4167916667',
    'DEC_DEG = -29.0078333333',
]
missing = [item for item in required if item not in source]
if missing:
    raise RuntimeError(f"CMB-0022 coordinate update failed: {missing}")

namespace = {"__name__": "__main__", "__file__": "CMB-0022.py"}
exec(compile(source, "CMB-0022.py", "exec"), namespace, namespace)
