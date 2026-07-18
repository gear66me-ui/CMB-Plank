"""CMB-0015 — Black-background Gaia image with guaranteed HTML star summary.

Run with:
    %run CMB-0015.py

This version starts from the working CMB-0013 widget and replaces the notebook
Styler output with an explicit HTML table so the nearest-star Gaia summary is
always visible. It keeps the black image background, Gaia crosses, and removes
the large multi-source catalogue dump.
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
        headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/15.0"},
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
source = source.replace('VERSION = "CMB-0013"', 'VERSION = "CMB-0015"', 1)
source = source.replace(
    'Mozilla/5.0 CMB-Gaia-Widget/13.0',
    'Mozilla/5.0 CMB-Gaia-Widget/15.0',
)

old_block = '''            styled = (
                summary.style
                .hide(axis="index")
                .set_table_styles([
                    {"selector": "table", "props": [("border-collapse", "collapse"), ("width", "100%"), ("background", "#0b0f14"), ("color", "#f5f7fa"), ("font-family", "Arial, sans-serif")]},
                    {"selector": "th", "props": [("background", "#16202b"), ("color", "#ffffff"), ("padding", "9px"), ("border", "1px solid #3b4652"), ("text-align", "left")]},
                    {"selector": "td", "props": [("padding", "8px 10px"), ("border", "1px solid #303943"), ("text-align", "left")]},
                    {"selector": "tr:nth-child(even)", "props": [("background", "#111821")]},
                ])
            )
            display(widgets.HTML("<div style='margin-top:12px;padding:10px 14px;background:#0b0f14;color:white;border-radius:9px;font:700 18px Arial;'>Nearest Gaia source summary</div>"))
            display(styled)

            if _finite(distance_pc):
                distance_sentence = f"Gaia places this source about {distance_ly:,.0f} light-years away."
            else:
                distance_sentence = "Gaia DR3 does not provide a reliable positive distance estimate for this source."
            class_sentence = _luminosity_class(logg)
            temp_sentence = _spectral_from_teff(teff)
            display(widgets.HTML(
                "<div style='margin-top:10px;padding:12px 14px;background:#111821;color:#eef3f8;border-left:4px solid #4fc3f7;border-radius:6px;font:14px/1.5 Arial;'>"
                f"<b>Plain-English summary:</b> {distance_sentence} Its temperature is consistent with {temp_sentence}. "
                f"The Gaia surface-gravity estimate suggests: {class_sentence}. "
                "Radial velocity is marked unavailable when Gaia did not obtain a usable line-of-sight speed measurement."
                "</div>"
            ))
'''

new_block = '''            rows = [(str(r["Property"]), str(r["Value"])) for _, r in summary.iterrows()]
            html_rows = "".join(
                "<tr>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #2e3944;font-weight:600;color:#b9d8ef;width:42%;'>{prop}</td>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #2e3944;color:#f4f7fa;'>{value}</td>"
                "</tr>"
                for prop, value in rows
            )
            table_html = f"""
            <div style='margin-top:14px;background:#080c11;color:#f4f7fa;border:1px solid #34404c;border-radius:10px;overflow:hidden;font-family:Arial,sans-serif;'>
              <div style='padding:12px 14px;background:#14202b;font-size:18px;font-weight:700;'>Nearest Gaia source summary</div>
              <table style='width:100%;border-collapse:collapse;font-size:14px;'>
                <thead>
                  <tr>
                    <th style='padding:9px 12px;text-align:left;background:#1d2a36;border-bottom:1px solid #3e4b58;'>Property</th>
                    <th style='padding:9px 12px;text-align:left;background:#1d2a36;border-bottom:1px solid #3e4b58;'>Gaia result</th>
                  </tr>
                </thead>
                <tbody>{html_rows}</tbody>
              </table>
            </div>
            """
            display(widgets.HTML(value=table_html))

            if _finite(distance_pc):
                distance_sentence = f"Gaia places this source about {distance_ly:,.0f} light-years away."
            else:
                distance_sentence = "Gaia DR3 does not provide a reliable positive distance estimate for this source."
            class_sentence = _luminosity_class(logg)
            temp_sentence = _spectral_from_teff(teff)
            display(widgets.HTML(value=(
                "<div style='margin-top:10px;padding:12px 14px;background:#111821;color:#eef3f8;border-left:4px solid #4fc3f7;border-radius:6px;font:14px/1.5 Arial;'>"
                f"<b>Plain-English summary:</b> {distance_sentence} Its temperature is consistent with <b>{temp_sentence}</b>. "
                f"Its Gaia surface-gravity estimate suggests <b>{class_sentence}</b>. "
                "G magnitude is apparent brightness measured by Gaia; lower numbers are brighter. "
                "Radial velocity is unavailable when Gaia did not obtain a usable line-of-sight speed."
                "</div>"
            )))
'''

if old_block not in source:
    raise RuntimeError(
        "CMB-0013.py changed and the CMB-0015 summary replacement could not be applied safely."
    )
source = source.replace(old_block, new_block, 1)

source = source.replace(
    "Black-background image, Gaia crosses, one concise summary table, and no 28-source catalogue dump.",
    "Black-background image, Gaia crosses, guaranteed HTML stellar-summary table, and no multi-source catalogue dump.",
    1,
)

namespace = {"__name__": "__main__", "__file__": "CMB-0015.py"}
exec(compile(source, "CMB-0015.py", "exec"), namespace, namespace)
