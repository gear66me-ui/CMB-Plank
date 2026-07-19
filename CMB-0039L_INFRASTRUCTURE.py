# CMB-0039L_INFRASTRUCTURE.py
from __future__ import annotations

import html
import urllib.parse
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML

VERSION = "CMB-0039L"

SURVEYS = [
    ("Hubble GOODS color", "CDS/P/HST/GOODS/color"),
    ("Hubble GOODS i-band", "CDS/P/HST/GOODS/i"),
    ("JWST F150W", "CDS/P/JWST/F150W"),
    ("JWST F444W", "CDS/P/JWST/F444W"),
    ("DESI Legacy DR10", "CDS/P/DESI-Legacy-Surveys/DR10/color"),
    ("PanSTARRS DR1 color", "P/PanSTARRS/DR1/color-z-zg-g"),
    ("DSS2 color", "P/DSS2/color"),
    ("2MASS color infrared", "P/2MASS/color"),
    ("WISE color infrared", "P/allWISE/color"),
    ("GALEX ultraviolet", "P/GALEXGR6/AIS/color"),
]

def aladin_url(target_text, fov_deg, survey_id):
    return "https://aladin.u-strasbg.fr/AladinLite/?" + urllib.parse.urlencode({
        "target": str(target_text).strip(),
        "fov": f"{float(fov_deg):g}",
        "survey": survey_id,
    })

def selected_name():
    return next((label for label, value in SURVEYS if value == survey.value), survey.value)

def viewer_html():
    url = aladin_url(target.value, fov.value, survey.value)
    return f"""
    <div style="width:100%; margin:0; padding:0; overflow:visible; background:#000;">
      <div style="padding:6px 10px; background:#07111f; color:#dbeafe; font:13px Arial, sans-serif; border:1px solid #334155; border-bottom:0;">
        <b>{html.escape(VERSION)} — Native AladinLite iframe</b>
        &nbsp; | &nbsp; Target: <b>{html.escape(str(target.value))}</b>
        &nbsp; | &nbsp; Survey: <b>{html.escape(selected_name())}</b>
        &nbsp; | &nbsp; FOV: <b>{float(fov.value):g}°</b>
      </div>
      <iframe
        src="{html.escape(url)}"
        style="width:100%; height:900px; border:1px solid #334155; display:block; background:#000; overflow:visible; touch-action:auto;"
        allowfullscreen
        loading="eager">
      </iframe>
    </div>
    """

target = widgets.Text(
    value="03 32 39.99 -27 48 00.0",
    description="Target:",
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
        ("0.005° — ultra tight", 0.005),
        ("0.01° — tight", 0.01),
        ("0.03°", 0.03),
        ("0.08° — GOODS", 0.08),
        ("0.25°", 0.25),
        ("1°", 1.0),
        ("5°", 5.0),
        ("20°", 20.0),
    ],
    value=0.08,
    description="Field:",
    layout=widgets.Layout(width="300px"),
)

load_button = widgets.Button(description="Reload Map", button_style="primary", icon="refresh")
open_button = widgets.Button(description="Open Full Screen", icon="external-link")
viewer = widgets.HTML(value=viewer_html(), layout=widgets.Layout(width="100%"))
open_out = widgets.Output()

def reload_map(_=None):
    viewer.value = viewer_html()

def open_full(_=None):
    url = aladin_url(target.value, fov.value, survey.value)
    with open_out:
        clear_output(wait=True)
        display(HTML(f"<script>window.open({url!r}, '_blank');</script>"))
        display(HTML(f"<a href='{html.escape(url)}' target='_blank'>Open AladinLite full screen</a>"))

load_button.on_click(reload_map)
open_button.on_click(open_full)

controls = widgets.VBox([
    widgets.HBox([target]),
    widgets.HBox([survey]),
    widgets.HBox([fov, load_button, open_button]),
], layout=widgets.Layout(width="100%"))

root = widgets.VBox([
    controls,
    viewer,
    open_out,
], layout=widgets.Layout(width="100%", overflow="visible"))

display(root)
