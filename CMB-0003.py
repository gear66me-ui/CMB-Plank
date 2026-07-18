"""CMB-0003 — Planck widget with compact temperature summary below the map.

Run with:
    %run CMB-0003.py
"""

from __future__ import annotations

import urllib.error
import urllib.request

SOURCE_URL = (
    "https://raw.githubusercontent.com/gear66me-ui/"
    "CMB-Plank/main/CMB-0001.py"
)
CMB_MEAN_K = 2.7255


def _load_base_source() -> str:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 CMB-Planck-Widget/3.0"},
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
    '    %run CMB-0001.py',
    '    %run CMB-0003.py',
    1,
)

source = source.replace(
    'CMB PLANCK INTERACTIVE WIDGET CMB-0001',
    'CMB PLANCK INTERACTIVE WIDGET CMB-0003',
    1,
)

old_render_tail = '''    fig = plt.gcf()
    fig.patch.set_facecolor("white")
    plt.show()
'''

new_render_tail = '''    fig = plt.gcf()
    fig.patch.set_facecolor("white")

    mean_k = CMB_MEAN_K
    deviation_k = float(color_limit) * 1.0e-6
    minimum_k = mean_k - deviation_k
    maximum_k = mean_k + deviation_k
    peak_to_peak_uk = 2.0 * float(color_limit)

    summary = (
        f"Mean CMB: {mean_k:.4f} K   |   "
        f"Displayed: {minimum_k:.4f}–{maximum_k:.4f} K   |   "
        f"Scale: ±{float(color_limit):.0f} µK   |   "
        f"Span: {peak_to_peak_uk:.0f} µK peak-to-peak"
    )

    fig.text(
        0.5,
        0.018,
        summary,
        ha="center",
        va="bottom",
        fontsize=8.5,
        family="monospace",
        bbox=dict(
            boxstyle="round,pad=0.30",
            facecolor="white",
            edgecolor="0.55",
            alpha=0.94,
        ),
    )
    fig.subplots_adjust(bottom=0.10)
    plt.show()
'''

if old_render_tail not in source:
    raise RuntimeError(
        "CMB-0001.py has changed and the CMB-0003 annotation patch could not "
        "be applied safely."
    )

source = source.replace(old_render_tail, new_render_tail, 1)

old_header_subtitle = (
    'Official Planck PR3 component-separated temperature maps · HEALPix · '
    'µK<sub>CMB</sub>'
)
new_header_subtitle = (
    'Official Planck PR3 maps · Mean CMB temperature 2.7255 K · '
    'Color scale shows ΔT in µK<sub>CMB</sub>'
)
source = source.replace(old_header_subtitle, new_header_subtitle, 1)

namespace = {
    "__name__": "__main__",
    "__file__": "CMB-0003.py",
    "CMB_MEAN_K": CMB_MEAN_K,
}
exec(compile(source, "CMB-0003.py", "exec"), namespace, namespace)
