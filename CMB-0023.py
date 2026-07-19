"""CMB-0023 — Sagittarius A* crosshair intensity map, rebuilt from the standalone CMB-0020 base."""
from __future__ import annotations

import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0020.py"
request = urllib.request.Request(
    SOURCE_URL,
    headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/23.0"},
)
with urllib.request.urlopen(request, timeout=60) as response:
    source = response.read().decode("utf-8")

replacements = [
    ('VERSION = "CMB-0020"', 'VERSION = "CMB-0023"'),
    ('RA_SEXAGESIMAL = "03:19:30.85"', 'RA_SEXAGESIMAL = "17:45:40.03"'),
    ('DEC_SEXAGESIMAL = "-21:45:24.1"', 'DEC_SEXAGESIMAL = "-29:00:28.2"'),
    ('RA_DEG = 49.8785416667', 'RA_DEG = 266.4167916667'),
    ('DEC_DEG = -21.7566944444', 'DEC_DEG = -29.0078333333'),
    ('Mozilla/5.0 CMB-Gaia-Widget/20.0', 'Mozilla/5.0 CMB-Gaia-Widget/23.0'),
    ('value="DSS2 color — reliable"', 'value="WISE color infrared"'),
    (
        'The cyan crosshair is fixed on the supplied sky coordinate.',
        'The cyan crosshair is fixed on Sagittarius A*. Gaia crosses mark nearby optical catalogue sources; Sagittarius A* itself is not a normal Gaia star.'
    ),
]
for old, new in replacements:
    if old not in source:
        raise RuntimeError(f"CMB-0023 could not find required source text: {old}")
    source = source.replace(old, new, 1)

old_wcs = (
    'x0, y0 = wcs.world_to_pixel_values(RA_DEG, DEC_DEG)\n'
    '            x0 = int(np.clip(round(x0), 0, nx - 1))\n'
    '            y0 = int(np.clip(round(y0), 0, ny - 1))'
)
new_wcs = (
    'x_raw, y_raw = wcs.world_to_pixel_values(RA_DEG, DEC_DEG)\n'
    '            x0 = int(np.clip(np.rint(np.asarray(x_raw, dtype=float).reshape(-1)[0]), 0, nx - 1))\n'
    '            y0 = int(np.clip(np.rint(np.asarray(y_raw, dtype=float).reshape(-1)[0]), 0, ny - 1))'
)
if old_wcs not in source:
    raise RuntimeError("CMB-0023 could not apply the WCS scalar fix.")
source = source.replace(old_wcs, new_wcs, 1)

namespace = {"__name__": "__main__", "__file__": "CMB-0023.py"}
exec(compile(source, "CMB-0023.py", "exec"), namespace, namespace)
