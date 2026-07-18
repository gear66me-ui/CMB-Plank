"""CMB-0004 — Planck SMICA-NOSZ widget with exact processed-map extrema.

Run with:
    %run CMB-0004.py

This version uses the official Planck PR3 SMICA-NOSZ temperature field,
centers absolute temperatures on 2.725480 K, defaults the display scale to
±300 µK, and calculates exact minimum/maximum values from the processed map
selected by the current Nside and FWHM settings.
"""

from __future__ import annotations

import urllib.error
import urllib.request

SOURCE_URL = (
    "https://raw.githubusercontent.com/gear66me-ui/"
    "CMB-Plank/main/CMB-0001.py"
)
CMB_MEAN_K = 2.725480


def _load_base_source() -> str:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 CMB-Planck-Widget/4.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise RuntimeError(
            "Unable to load CMB-0001.py from GitHub. Check the internet "
            f"connection. Details: {exc}"
        ) from exc


source = _load_base_source()

source = source.replace(
    "    %run CMB-0001.py",
    "    %run CMB-0004.py",
    1,
)

source = source.replace(
    "CMB PLANCK INTERACTIVE WIDGET CMB-0001",
    "CMB PLANCK INTERACTIVE WIDGET CMB-0004",
    1,
)

source = source.replace(
    "    value=500.0,\n    min=25.0,",
    "    value=300.0,\n    min=25.0,",
    1,
)

old_render_tail = '''    fig = plt.gcf()
    fig.patch.set_facecolor("white")
    plt.show()
'''

new_render_tail = '''    fig = plt.gcf()
    fig.patch.set_facecolor("white")

    valid = np.isfinite(sky) & (sky != hp.UNSEEN)
    if not np.any(valid):
        raise RuntimeError("The processed map contains no valid temperature pixels.")

    exact_min_uk = float(np.min(sky[valid]))
    exact_max_uk = float(np.max(sky[valid]))
    exact_span_uk = exact_max_uk - exact_min_uk

    exact_min_k = CMB_MEAN_K + exact_min_uk * 1.0e-6
    exact_max_k = CMB_MEAN_K + exact_max_uk * 1.0e-6

    display_min_k = CMB_MEAN_K - float(color_limit) * 1.0e-6
    display_max_k = CMB_MEAN_K + float(color_limit) * 1.0e-6

    line1 = (
        f"Mean: {CMB_MEAN_K:.6f} K   |   "
        f"Display: {display_min_k:.6f}–{display_max_k:.6f} K "
        f"(±{float(color_limit):.0f} µK)"
    )
    line2 = (
        f"Exact processed map: min {exact_min_k:.6f} K "
        f"({exact_min_uk:+.3f} µK)   |   "
        f"max {exact_max_k:.6f} K ({exact_max_uk:+.3f} µK)   |   "
        f"span {exact_span_uk:.3f} µK"
    )

    fig.text(
        0.5,
        0.030,
        line1 + "\\n" + line2,
        ha="center",
        va="bottom",
        fontsize=7.8,
        family="monospace",
        linespacing=1.35,
        bbox=dict(
            boxstyle="round,pad=0.28",
            facecolor="white",
            edgecolor="0.60",
            alpha=0.95,
        ),
    )
    fig.subplots_adjust(bottom=0.13)
    plt.show()
'''

if old_render_tail not in source:
    raise RuntimeError(
        "CMB-0001.py has changed and the CMB-0004 extrema patch could not "
        "be applied safely."
    )

source = source.replace(old_render_tail, new_render_tail, 1)

old_header_subtitle = (
    "Official Planck PR3 component-separated temperature maps · HEALPix · "
    "µK<sub>CMB</sub>"
)
new_header_subtitle = (
    "Official Planck PR3 SMICA-NOSZ temperature field · Mean 2.725480 K · "
    "Exact extrema calculated from selected Nside/FWHM"
)
source = source.replace(old_header_subtitle, new_header_subtitle, 1)

namespace = {
    "__name__": "__main__",
    "__file__": "CMB-0004.py",
    "CMB_MEAN_K": CMB_MEAN_K,
}
exec(compile(source, "CMB-0004.py", "exec"), namespace, namespace)
