"""CMB-0029 — Original interactive Aladin firmament map with Hubble and JWST surveys.

This preserves the same touch-friendly Aladin map style used by the earlier widget:
- drag to pan
- pinch or +/- to zoom
- coordinate-frame selector inside the map
- catalogue/layer controls inside the map

Hubble and JWST are added as selectable HiPS backgrounds.
"""
from __future__ import annotations

import html
import urllib.parse

import ipywidgets as widgets
from IPython.display import display

VERSION = "CMB-0029"

DEFAULT_TARGET = "03 32 39.99 -27 48 00.0"
DEFAULT_FOV = 0.08

SURVEYS = [
    ("DSS2 color", "P/DSS2/color"),
    ("DSS2 blue", "P/DSS2/blue"),
    ("2MASS color infrared", "P/2MASS/color"),
    ("WISE color infrared", "P/allWISE/color"),
    ("GALEX GR6/7 ultraviolet", "P/GALEXGR6/AIS/color"),
    ("Hubble Outreach color", "CDS/P/HST/EPO"),
    ("Hubble GOODS color", "CDS/P/HST/GOODS/color"),
    ("Hubble GOODS i-band", "CDS/P/HST/GOODS/i"),
    ("Hubble R-band", "CDS/P/HST/R"),
    ("Hubble H-beta", "CDS/P/HST/Hbeta"),
    ("JWST F150W", "CDS/P/JWST/F150W"),
    ("JWST F444W", "CDS/P/JWST/F444W"),
    ("JWST F480M", "CDS/P/JWST/F480M"),
]


def aladin_url(target: str, fov_deg: float, survey_id: str) -> str:
    params = {
        "target": target.strip(),
        "fov": f"{float(fov_deg):g}",
        "survey": survey_id,
    }
    return "https://aladin.u-strasbg.fr/AladinLite/?" + urllib.parse.urlencode(params)


def viewer_html(target: str, fov_deg: float, survey_id: str, survey_name: str) -> str:
    url = aladin_url(target, fov_deg, survey_id)
    return f"""
    <div style="border:1px solid #78909c;border-radius:10px;overflow:hidden;background:#000;">
      <div style="padding:8px 12px;background:#0b172a;color:white;font-family:sans-serif;">
        <b>{html.escape(survey_name)}</b><br>
        <span style="font-size:12px;opacity:.85;">Target: {html.escape(target)} · FOV {float(fov_deg):g}°</span>
      </div>
      <iframe
        src="{html.escape(url)}"
        style="width:100%;height:820px;border:0;display:block;background:#000;touch-action:auto;"
        allowfullscreen>
      </iframe>
    </div>
    """

header = widgets.HTML(value=f"""
<div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;font-family:sans-serif;">
  <div style="font-size:22px;font-weight:700;">INTERACTIVE MULTI-SURVEY SKY MAP — {VERSION}</div>
  <div style="font-size:13px;opacity:.9;margin-top:4px;">
    Original Aladin touch map · drag to pan · pinch or use +/- to zoom · real HiPS survey imagery
  </div>
</div>
""")

target = widgets.Text(
    value=DEFAULT_TARGET,
    description="Target:",
    placeholder="RA Dec or object name",
    layout=widgets.Layout(width="520px"),
)

survey = widgets.Dropdown(
    options=SURVEYS,
    value="CDS/P/HST/GOODS/color",
    description="Survey:",
    layout=widgets.Layout(width="520px"),
)

fov = widgets.Dropdown(
    options=[
        ("0.01° — very tight", 0.01),
        ("0.03°", 0.03),
        ("0.08° — HUDF/GOODS", 0.08),
        ("0.25°", 0.25),
        ("1°", 1.0),
        ("5°", 5.0),
        ("20°", 20.0),
    ],
    value=DEFAULT_FOV,
    description="Field:",
    layout=widgets.Layout(width="300px"),
)

load_button = widgets.Button(
    description="Load Interactive Map",
    button_style="primary",
    icon="globe",
    layout=widgets.Layout(width="220px", height="40px"),
)

open_button = widgets.Button(
    description="Open Full Screen",
    icon="external-link",
    layout=widgets.Layout(width="180px", height="40px"),
)

note = widgets.HTML(value="""
<div style="padding:9px 12px;border-left:4px solid #ffb300;background:#fff8e1;font:13px sans-serif;">
<b>Coverage note:</b> DSS2, 2MASS, WISE and GALEX cover very large areas. Hubble and JWST are pointed-observation archives, so they show pixels only where those telescopes actually observed. A black or blank field can simply mean no HST/JWST coverage at that coordinate.
</div>
""")

viewer = widgets.HTML(
    value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, survey.value, "Hubble GOODS color")
)


def selected_name() -> str:
    for label, value in SURVEYS:
        if value == survey.value:
            return label
    return survey.value


def reload_map(_=None):
    viewer.value = viewer_html(target.value, fov.value, survey.value, selected_name())


def open_full(_=None):
    url = aladin_url(target.value, fov.value, survey.value)
    display(widgets.HTML(value=f"<script>window.open({url!r}, '_blank');</script>"))


load_button.on_click(reload_map)
open_button.on_click(open_full)

controls = widgets.VBox([
    widgets.HBox([target]),
    widgets.HBox([survey]),
    widgets.HBox([fov, load_button, open_button]),
])

display(widgets.VBox([header, controls, note, viewer], layout=widgets.Layout(width="100%")))
