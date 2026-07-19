# CMB-0039K_INFRASTRUCTURE.py
# Silent 31-style AladinLite star viewer with visible external toolbar
from __future__ import annotations

import html
import urllib.parse
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

VERSION = "CMB-0039K"

SURVEYS = [
    ("Hubble GOODS color", "CDS/P/HST/GOODS/color"),
    ("Hubble GOODS i-band", "CDS/P/HST/GOODS/i"),
    ("JWST F150W", "CDS/P/JWST/F150W"),
    ("JWST F444W", "CDS/P/JWST/F444W"),
    ("JWST F480M", "CDS/P/JWST/F480M"),
    ("PanSTARRS DR1 color", "P/PanSTARRS/DR1/color-z-zg-g"),
    ("DESI Legacy DR10", "CDS/P/DESI-Legacy-Surveys/DR10/color"),
    ("DSS2 color", "P/DSS2/color"),
    ("DSS2 red", "P/DSS2/red"),
    ("2MASS color infrared", "P/2MASS/color"),
    ("WISE color infrared", "P/allWISE/color"),
    ("GALEX ultraviolet", "P/GALEXGR6/AIS/color"),
]

DEFAULT_TARGET = "03 32 39.99 -27 48 00.0"
DEFAULT_FOV = 0.08
DEFAULT_SURVEY = "CDS/P/HST/GOODS/color"


def aladin_url(target_text: str, fov_deg: float, survey_id: str) -> str:
    params = {
        "target": str(target_text).strip(),
        "fov": f"{float(fov_deg):g}",
        "survey": survey_id,
    }
    return "https://aladin.u-strasbg.fr/AladinLite/?" + urllib.parse.urlencode(params)


def selected_survey_name() -> str:
    return next((name for name, sid in SURVEYS if sid == survey.value), str(survey.value))


def viewer_html() -> str:
    url = aladin_url(target.value, fov.value, survey.value)
    return f"""
    <div style="width:100%;background:#05070d;color:white;font-family:Arial,sans-serif;border:1px solid #54606f;border-radius:10px;overflow:hidden;">
      <div style="padding:10px 14px;background:#0b172a;border-bottom:1px solid #334155;display:flex;gap:18px;align-items:center;flex-wrap:wrap;">
        <div style="font-size:18px;font-weight:700;color:#bfdbfe;">{html.escape(VERSION)} Interactive Star Viewer</div>
        <div style="font-size:13px;color:#d1d5db;">External toolbar is above the map so Colab cannot clip it.</div>
        <a href="{html.escape(url)}" target="_blank" style="margin-left:auto;background:#2563eb;color:white;text-decoration:none;padding:7px 12px;border-radius:7px;font-weight:700;">Open Full Screen</a>
      </div>
      <iframe src="{html.escape(url)}"
        style="width:100%;height:920px;min-height:920px;border:0;display:block;background:#000;touch-action:auto;"
        allowfullscreen>
      </iframe>
    </div>
    """


def refresh_url_label() -> None:
    url = aladin_url(target.value, fov.value, survey.value)
    url_box.value = f"<div style='font:12px monospace;padding:8px;background:#111827;color:#cbd5e1;border-radius:6px;overflow-wrap:anywhere'>{html.escape(url)}</div>"
    status.value = (
        f"<b style='color:#166534'>Loaded:</b> {html.escape(target.value)} &nbsp; | &nbsp; "
        f"<b>Survey:</b> {html.escape(selected_survey_name())} &nbsp; | &nbsp; "
        f"<b>FOV:</b> {float(fov.value):g}°"
    )


def load_map(_=None):
    with out:
        clear_output(wait=True)
        display(HTML(viewer_html()))
    refresh_url_label()


def open_full(_=None):
    url = aladin_url(target.value, fov.value, survey.value)
    display(HTML(f"<script>window.open({url!r}, '_blank');</script>"))
    refresh_url_label()


def set_goodss(_=None):
    target.value = "03 32 39.99 -27 48 00.0"
    fov.value = 0.08
    survey.value = "CDS/P/HST/GOODS/color"
    load_map()


def set_m31(_=None):
    target.value = "M31"
    fov.value = 0.25
    survey.value = "P/DSS2/color"
    load_map()


header = widgets.HTML(value=f"""
<div style="padding:12px 16px;background:#0b172a;color:white;border-radius:10px;font-family:Arial,sans-serif;">
  <div style="font-size:22px;font-weight:800;">{VERSION} — 31-style interactive sky map</div>
  <div style="font-size:13px;opacity:.9;margin-top:4px;">Visible external alignment controls · full-screen button · no console startup spam</div>
</div>
""")

target = widgets.Text(value=DEFAULT_TARGET, description="Target", layout=widgets.Layout(width="520px"))
survey = widgets.Dropdown(options=SURVEYS, value=DEFAULT_SURVEY, description="Survey", layout=widgets.Layout(width="520px"))
fov = widgets.Dropdown(
    options=[("0.01°", 0.01), ("0.03°", 0.03), ("0.08°", 0.08), ("0.15°", 0.15), ("0.25°", 0.25), ("1°", 1.0), ("5°", 5.0), ("20°", 20.0)],
    value=DEFAULT_FOV,
    description="FOV",
    layout=widgets.Layout(width="220px"),
)
load_button = widgets.Button(description="Load / Refresh Map", button_style="primary", icon="refresh", layout=widgets.Layout(width="180px"))
open_button = widgets.Button(description="Open Full Screen", button_style="success", icon="external-link", layout=widgets.Layout(width="175px"))
goodss_button = widgets.Button(description="GOODS/JWST Field", icon="crosshairs", layout=widgets.Layout(width="160px"))
m31_button = widgets.Button(description="M31", icon="star", layout=widgets.Layout(width="90px"))
status = widgets.HTML()
url_box = widgets.HTML()
out = widgets.Output()

load_button.on_click(load_map)
open_button.on_click(open_full)
goodss_button.on_click(set_goodss)
m31_button.on_click(set_m31)

controls = widgets.VBox([
    widgets.HBox([target]),
    widgets.HBox([survey]),
    widgets.HBox([fov, load_button, open_button, goodss_button, m31_button]),
    status,
    url_box,
], layout=widgets.Layout(width="100%"))

display(widgets.VBox([header, controls, out], layout=widgets.Layout(width="100%")))
load_map()
