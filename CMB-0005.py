"""CMB-0005 — Planck SMICA-NOSZ map with HUDF and coldest-pixel circles.

Run with:
    %run CMB-0005.py
"""

from __future__ import annotations

import urllib.error
import urllib.request

SOURCE_URL = (
    "https://raw.githubusercontent.com/gear66me-ui/"
    "CMB-Plank/main/CMB-0001.py"
)
CMB_MEAN_K = 2.725480
HUDF_L_DEG = 223.570
HUDF_B_DEG = -54.392


def _load_base_source() -> str:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 CMB-Planck-Widget/5.0"},
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
    "    %run CMB-0005.py",
    1,
)
source = source.replace(
    "CMB PLANCK INTERACTIVE WIDGET CMB-0001",
    "CMB PLANCK INTERACTIVE WIDGET CMB-0005",
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

new_render_tail = '''    valid = np.isfinite(sky) & (sky != hp.UNSEEN)
    if not np.any(valid):
        raise RuntimeError("The processed map contains no valid temperature pixels.")

    valid_indices = np.flatnonzero(valid)
    coldest_pixel = int(valid_indices[np.argmin(sky[valid])])
    exact_min_uk = float(sky[coldest_pixel])
    exact_max_uk = float(np.max(sky[valid]))
    exact_span_uk = exact_max_uk - exact_min_uk

    cold_theta, cold_phi = hp.pix2ang(nside, coldest_pixel)
    cold_l_deg = float(np.degrees(cold_phi))
    cold_b_deg = float(90.0 - np.degrees(cold_theta))

    # Two unfilled circles: HUDF and the coldest valid pixel in this processed map.
    hp.projscatter(
        HUDF_L_DEG,
        HUDF_B_DEG,
        lonlat=True,
        coord="G",
        marker="o",
        s=210,
        facecolors="none",
        edgecolors="lime",
        linewidths=2.0,
        zorder=20,
    )
    hp.projtext(
        HUDF_L_DEG,
        HUDF_B_DEG + 4.0,
        "HUDF",
        lonlat=True,
        coord="G",
        color="lime",
        fontsize=9,
        ha="center",
        fontweight="bold",
    )

    hp.projscatter(
        cold_l_deg,
        cold_b_deg,
        lonlat=True,
        coord="G",
        marker="o",
        s=260,
        facecolors="none",
        edgecolors="yellow",
        linewidths=2.2,
        zorder=21,
    )
    hp.projtext(
        cold_l_deg,
        cold_b_deg + 4.0,
        "COLDEST PIXEL",
        lonlat=True,
        coord="G",
        color="yellow",
        fontsize=9,
        ha="center",
        fontweight="bold",
    )

    exact_min_k = CMB_MEAN_K + exact_min_uk * 1.0e-6
    exact_max_k = CMB_MEAN_K + exact_max_uk * 1.0e-6
    display_min_k = CMB_MEAN_K - float(color_limit) * 1.0e-6
    display_max_k = CMB_MEAN_K + float(color_limit) * 1.0e-6

    line1 = (
        f"Mean {CMB_MEAN_K:.6f} K | Display {display_min_k:.6f}–{display_max_k:.6f} K "
        f"(±{float(color_limit):.0f} µK)"
    )
    line2 = (
        f"HUDF: l={HUDF_L_DEG:.3f}°, b={HUDF_B_DEG:.3f}° | "
        f"Coldest: l={cold_l_deg:.3f}°, b={cold_b_deg:.3f}°, "
        f"ΔT={exact_min_uk:+.3f} µK, T={exact_min_k:.6f} K"
    )
    line3 = (
        f"Processed-map max {exact_max_k:.6f} K ({exact_max_uk:+.3f} µK) | "
        f"peak-to-peak {exact_span_uk:.3f} µK"
    )

    fig = plt.gcf()
    fig.patch.set_facecolor("white")
    fig.text(
        0.5,
        0.018,
        line1 + "\\n" + line2 + "\\n" + line3,
        ha="center",
        va="bottom",
        fontsize=7.4,
        family="monospace",
        linespacing=1.25,
        bbox=dict(
            boxstyle="round,pad=0.25",
            facecolor="white",
            edgecolor="0.60",
            alpha=0.95,
        ),
    )
    fig.subplots_adjust(bottom=0.15)
    plt.show()
'''

if old_render_tail not in source:
    raise RuntimeError(
        "CMB-0001.py has changed and the CMB-0005 marker patch could not be applied safely."
    )
source = source.replace(old_render_tail, new_render_tail, 1)

old_header_subtitle = (
    "Official Planck PR3 component-separated temperature maps · HEALPix · "
    "µK<sub>CMB</sub>"
)
new_header_subtitle = (
    "Official Planck PR3 SMICA-NOSZ field · Green circle: HUDF · "
    "Yellow circle: exact coldest processed pixel"
)
source = source.replace(old_header_subtitle, new_header_subtitle, 1)

namespace = {
    "__name__": "__main__",
    "__file__": "CMB-0005.py",
    "CMB_MEAN_K": CMB_MEAN_K,
    "HUDF_L_DEG": HUDF_L_DEG,
    "HUDF_B_DEG": HUDF_B_DEG,
}
exec(compile(source, "CMB-0005.py", "exec"), namespace, namespace)
