"""CMB-0010 — Gaia DR3 map with 2D celestial WCS fix.

Run with:
    %run CMB-0010.py

This version fixes the HiPS2FITS RGB WCS error by explicitly using only the
celestial (RA/Dec) axes when plotting three-dimensional FITS image cubes.
"""

from __future__ import annotations

import urllib.error
import urllib.request

SOURCE_URL = (
    "https://raw.githubusercontent.com/gear66me-ui/"
    "CMB-Plank/main/CMB-0009.py"
)


def _load_source() -> str:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/10.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise RuntimeError(
            "Unable to load CMB-0009.py from GitHub. Check the internet "
            f"connection. Details: {exc}"
        ) from exc


source = _load_source()

source = source.replace(
    'VERSION = "CMB-0009"',
    'VERSION = "CMB-0010"',
    1,
)

source = source.replace(
    'Mozilla/5.0 CMB-Gaia-Widget/9.0',
    'Mozilla/5.0 CMB-Gaia-Widget/10.0',
)

old_wcs = '''            wcs = WCS(hdu.header)

            fig = plt.figure(figsize=(10, 9))
            ax = fig.add_subplot(111, projection=wcs)
'''

new_wcs = '''            full_wcs = WCS(hdu.header)
            wcs = full_wcs.celestial

            fig = plt.figure(figsize=(10, 9))
            ax = fig.add_subplot(111, projection=wcs)
'''

if old_wcs not in source:
    raise RuntimeError(
        "CMB-0009.py has changed and the CMB-0010 celestial-WCS patch "
        "could not be applied safely."
    )

source = source.replace(old_wcs, new_wcs, 1)

source = source.replace(
    "Python-native Colab widget · no iframe",
    "Python-native Colab widget · 2D celestial WCS fix · no iframe",
    1,
)

namespace = {
    "__name__": "__main__",
    "__file__": "CMB-0010.py",
}
exec(compile(source, "CMB-0010.py", "exec"), namespace, namespace)
