"""CMB-0008 — Gaia DR3 map using an external HTTPS viewer origin.

Run with:
    %run CMB-0008.py

Fixes the browser error caused by loading Aladin Lite from a data: URL, where
localStorage is disabled. This version loads the viewer from jsDelivr over
HTTPS and keeps the same Gaia DR3 overlay and controls.
"""

from __future__ import annotations

import html
import urllib.parse

import ipywidgets as widgets
from IPython.display import display

VERSION = "CMB-0008"
RA_SEXAGESIMAL = "03:12:59.96"
DEC_SEXAGESIMAL = "-20:02:09.0"
RA_DEG = 48.2498333333
DEC_DEG = -20.0358333333
VIEWER_BASE = (
    "https://cdn.jsdelivr.net/gh/gear66me-ui/CMB-Plank@main/"
    "CMB-0008-viewer.html"
)


def _viewer_url(fov_deg: float, survey: str, radius_deg: float) -> str:
    params = {
        "ra": f"{RA_DEG:.10f}",
        "dec": f"{DEC_DEG:.10f}",
        "fov": f"{float(fov_deg):.10f}",
        "radius": f"{float(radius_deg):.10f}",
        "survey": survey,
        "v": VERSION,
    }
    return VIEWER_BASE + "?" + urllib.parse.urlencode(params)


def _iframe_html(fov_deg: float, survey: str, radius_deg: float) -> str:
    url = html.escape(_viewer_url(fov_deg, survey, radius_deg), quote=True)
    return f"""
    <iframe
      src="{url}"
      style="width:100%;height:760px;border:1px solid #78909c;border-radius:10px;background:#05070a;"
      allow="fullscreen"
      allowfullscreen>
    </iframe>
    """


header = widgets.HTML(value=f"""
<div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;font-family:sans-serif;">
  <div style="font-size:22px;font-weight:700;">GAIA DR3 STAR MAP — {VERSION}</div>
  <div style="font-size:13px;opacity:.9;margin-top:4px;">
    Selected position: RA {RA_SEXAGESIMAL}, Dec {DEC_SEXAGESIMAL} ·
    decimal RA {RA_DEG:.6f}°, Dec {DEC_DEG:.6f}°
  </div>
  <div style="font-size:12px;opacity:.78;margin-top:3px;">
    Real survey imagery plus Gaia DR3 catalogue data · external HTTPS viewer · no generated images
  </div>
</div>
""")

fov = widgets.Dropdown(
    options=[
        ("1 arcmin — tight", 1.0 / 60.0),
        ("3 arcmin — recommended", 3.0 / 60.0),
        ("6 arcmin", 6.0 / 60.0),
        ("12 arcmin", 12.0 / 60.0),
        ("30 arcmin", 30.0 / 60.0),
    ],
    value=3.0 / 60.0,
    description="Field of view:",
    layout=widgets.Layout(width="330px"),
)

survey = widgets.Dropdown(
    options=[
        ("DSS2 color — reliable", "P/DSS2/color"),
        ("DSS2 red", "P/DSS2/red"),
        ("Pan-STARRS DR1 color", "P/PanSTARRS/DR1/color-z-zg-g"),
        ("2MASS infrared", "P/2MASS/color"),
        ("WISE infrared", "P/allWISE/color"),
    ],
    value="P/DSS2/color",
    description="Background:",
    layout=widgets.Layout(width="360px"),
)

radius = widgets.Dropdown(
    options=[
        ("1 arcmin", 1.0 / 60.0),
        ("3 arcmin", 3.0 / 60.0),
        ("6 arcmin", 6.0 / 60.0),
        ("12 arcmin", 12.0 / 60.0),
    ],
    value=3.0 / 60.0,
    description="Gaia radius:",
    layout=widgets.Layout(width="280px"),
)

reload_button = widgets.Button(
    description="Reload Gaia Map",
    button_style="primary",
    icon="refresh",
    layout=widgets.Layout(width="190px", height="38px"),
)

viewer = widgets.HTML(value=_iframe_html(fov.value, survey.value, radius.value))

instructions = widgets.HTML(value="""
<div style="padding:9px 12px;border-left:4px solid #ffd400;background:#fffde7;font:13px sans-serif;">
<b>How to use it:</b> the green circle marks your exact coordinate. Yellow crosses are Gaia DR3 sources.
Click a yellow cross to open its Gaia table. Drag to pan, use the wheel or +/− controls to zoom, and read RA/Dec under the cursor.
</div>
""")


def _reload(_button=None):
    viewer.value = _iframe_html(fov.value, survey.value, radius.value)


reload_button.on_click(_reload)

controls = widgets.VBox([
    widgets.HBox([fov, survey]),
    widgets.HBox([radius, reload_button]),
])

display(widgets.VBox([header, controls, instructions, viewer], layout=widgets.Layout(width="100%")))
