"""CMB-0002 — Planck widget with absolute-temperature annotation.

Run with:
    %run CMB-0002.py

This version loads CMB-0001 and adds a right-side information panel showing the
mean CMB temperature, selected deviation scale, absolute displayed range, and
peak-to-peak span.
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
        headers={"User-Agent": "Mozilla/5.0 CMB-Planck-Widget/2.0"},
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
    '    %run CMB-0002.py',
    1,
)

source = source.replace(
    'CMB PLANCK INTERACTIVE WIDGET CMB-0001',
    'CMB PLANCK INTERACTIVE WIDGET CMB-0002',
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

    info_text = (
        "ABSOLUTE CMB TEMPERATURE\\n"
        "\\n"
        f"Mean:  {mean_k:.7f} K\\n"
        f"Scale: ±{float(color_limit):.0f} µK\\n"
        f"Cold:  {minimum_k:.7f} K\\n"
        f"Hot:   {maximum_k:.7f} K\\n"
        f"Span:  {peak_to_peak_uk:.0f} µK peak-to-peak\\n"
        "\\n"
        "Map colors show ΔT relative\\n"
        "to the 2.7255 K mean."
    )

    fig.text(
        0.825,
        0.52,
        info_text,
        ha="left",
        va="center",
        fontsize=10,
        family="monospace",
        bbox=dict(
            boxstyle="round,pad=0.65",
            facecolor="white",
            edgecolor="0.35",
            alpha=0.96,
        ),
    )
    fig.subplots_adjust(right=0.80)
    plt.show()
'''

if old_render_tail not in source:
    raise RuntimeError(
        "CMB-0001.py has changed and the CMB-0002 annotation patch could not "
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
    "__file__": "CMB-0002.py",
    "CMB_MEAN_K": CMB_MEAN_K,
}
exec(compile(source, "CMB-0002.py", "exec"), namespace, namespace)
