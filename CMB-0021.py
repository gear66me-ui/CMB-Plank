"""CMB-0021 — Fix WCS scalar conversion for the crosshair intensity map."""
from __future__ import annotations

import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0020.py"
request = urllib.request.Request(
    SOURCE_URL,
    headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/21.0"},
)
with urllib.request.urlopen(request, timeout=60) as response:
    source = response.read().decode("utf-8")

source = source.replace('VERSION = "CMB-0020"', 'VERSION = "CMB-0021"', 1)
source = source.replace(
    'x0, y0 = wcs.world_to_pixel_values(RA_DEG, DEC_DEG)\n'
    '            x0 = int(np.clip(round(x0), 0, nx - 1))\n'
    '            y0 = int(np.clip(round(y0), 0, ny - 1))',
    'x_raw, y_raw = wcs.world_to_pixel_values(RA_DEG, DEC_DEG)\n'
    '            x0 = int(np.clip(np.rint(np.asarray(x_raw, dtype=float).reshape(-1)[0]), 0, nx - 1))\n'
    '            y0 = int(np.clip(np.rint(np.asarray(y_raw, dtype=float).reshape(-1)[0]), 0, ny - 1))',
    1,
)
source = source.replace(
    'Mozilla/5.0 CMB-Gaia-Widget/20.0',
    'Mozilla/5.0 CMB-Gaia-Widget/21.0',
)

if 'round(x0)' in source or 'round(y0)' in source:
    raise RuntimeError("CMB-0021 could not apply the WCS scalar fix.")

namespace = {"__name__": "__main__", "__file__": "CMB-0021.py"}
exec(compile(source, "CMB-0021.py", "exec"), namespace, namespace)
