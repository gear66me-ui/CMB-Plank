"""CMB-0006 — Cold Spot direction and JWST HUDF high-resolution viewer.

Run with:
    %run CMB-0006.py

This widget provides:
1. An interactive Aladin Lite sky view centered on the famous CMB Cold Spot.
2. The official NASA/ESA/CSA JWST HUDF image at full published display resolution.
"""

from __future__ import annotations

import html
import urllib.parse

import ipywidgets as widgets
from IPython.display import display

VERSION = "CMB-0006"

# Famous CMB Cold Spot center, approximately l=209 deg, b=-57 deg,
# converted to ICRS equatorial coordinates.
COLD_SPOT_RA_DEG = 48.299911
COLD_SPOT_DEC_DEG = -20.437305

# Hubble Ultra Deep Field / JWST HUDF image center.
HUDF_RA = "03:32:39.99"
HUDF_DEC = "-27:47:00.00"

# Official NASA full-resolution JWST HUDF release image, 10826 x 4946 PNG.
JWST_HUDF_FULL = (
    "https://assets.science.nasa.gov/dynamicimage/assets/science/missions/webb/"
    "outreach/migrated/2023/STScI-01GXE4BEMMTJRBXCJHYKBKTQ96.png"
    "?crop=faces%2Cfocalpoint&fit=clip&h=4946&w=10826"
)
JWST_HUDF_2000 = (
    "https://assets.science.nasa.gov/dynamicimage/assets/science/missions/webb/"
    "outreach/migrated/2023/STScI-01GXE4BEMMTJRBXCJHYKBKTQ96.png"
    "?crop=faces%2Cfocalpoint&fit=clip&h=914&w=2000"
)
JWST_HUDF_PAGE = (
    "https://science.nasa.gov/asset/webb/webb-observations-of-hudf-nircam-image/"
)


def _aladin_url(fov_deg: float, survey: str) -> str:
    target = f"{COLD_SPOT_RA_DEG} {COLD_SPOT_DEC_DEG}"
    params = {
        "target": target,
        "fov": f"{float(fov_deg):g}",
        "survey": survey,
    }
    return "https://aladin.u-strasbg.fr/AladinLite/?" + urllib.parse.urlencode(params)


def _cold_spot_html(fov_deg: float, survey: str) -> str:
    url = _aladin_url(fov_deg, survey)
    return f"""
    <div style="border:1px solid #b0bec5;border-radius:10px;overflow:hidden;background:#101418;">
      <div style="padding:9px 12px;background:#0b172a;color:white;font-family:sans-serif;">
        <b>Famous CMB Cold Spot direction</b><br>
        <span style="font-size:12px;opacity:0.88;">
          ICRS RA {COLD_SPOT_RA_DEG:.6f}°, Dec {COLD_SPOT_DEC_DEG:.6f}° ·
          approximately Galactic l=209°, b=-57°
        </span>
      </div>
      <iframe src="{html.escape(url)}"
              style="width:100%;height:720px;border:0;display:block;"
              allowfullscreen></iframe>
    </div>
    """


def _hudf_html(image_url: str, label: str) -> str:
    safe_image = html.escape(image_url)
    safe_page = html.escape(JWST_HUDF_PAGE)
    return f"""
    <div style="border:1px solid #b0bec5;border-radius:10px;background:#050607;overflow:hidden;">
      <div style="padding:9px 12px;background:#0b172a;color:white;font-family:sans-serif;">
        <b>JWST observations of the Hubble Ultra Deep Field</b><br>
        <span style="font-size:12px;opacity:0.88;">
          RA {HUDF_RA}, Dec {HUDF_DEC} · {html.escape(label)} · Official NASA/ESA/CSA image
        </span>
      </div>
      <div style="height:760px;overflow:auto;text-align:center;background:#000;">
        <img src="{safe_image}"
             alt="JWST Hubble Ultra Deep Field"
             style="display:block;max-width:none;height:auto;margin:0 auto;"
             loading="eager">
      </div>
      <div style="padding:7px 12px;background:#eceff1;font:12px sans-serif;">
        Drag the horizontal and vertical scrollbars to inspect the image at native scale.
        <a href="{safe_image}" target="_blank" rel="noopener">Open image alone</a> ·
        <a href="{safe_page}" target="_blank" rel="noopener">NASA image page</a>
      </div>
    </div>
    """


header = widgets.HTML(
    value=f"""
    <div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;">
      <div style="font-size:22px;font-weight:700;">COLD SPOT + JWST HUDF VIEWER {VERSION}</div>
      <div style="font-size:13px;opacity:0.88;margin-top:4px;">
        Real astronomical survey imagery only · no generated images
      </div>
    </div>
    """
)

fov_widget = widgets.Dropdown(
    options=[
        ("0.25° — detailed field", 0.25),
        ("0.5°", 0.5),
        ("1°", 1.0),
        ("5°", 5.0),
        ("10° — broad Cold Spot region", 10.0),
    ],
    value=1.0,
    description="Cold Spot FOV:",
    layout=widgets.Layout(width="360px"),
)

survey_widget = widgets.Dropdown(
    options=[
        ("DSS2 color optical", "P/DSS2/color"),
        ("Pan-STARRS DR1 color", "P/PanSTARRS/DR1/color-z-zg-g"),
        ("2MASS color infrared", "P/2MASS/color"),
        ("WISE color infrared", "P/allWISE/color"),
    ],
    value="P/DSS2/color",
    description="Survey:",
    layout=widgets.Layout(width="360px"),
)

cold_refresh = widgets.Button(
    description="Reload Cold Spot View",
    button_style="primary",
    icon="refresh",
    layout=widgets.Layout(width="210px", height="38px"),
)

quality_widget = widgets.ToggleButtons(
    options=[
        ("Full 10826 × 4946", "full"),
        ("Tablet 2000 × 914", "tablet"),
    ],
    value="full",
    description="HUDF image:",
)

hudf_refresh = widgets.Button(
    description="Load HUDF Image",
    button_style="primary",
    icon="image",
    layout=widgets.Layout(width="180px", height="38px"),
)

cold_output = widgets.HTML(value=_cold_spot_html(fov_widget.value, survey_widget.value))
hudf_output = widgets.HTML(
    value="<div style='padding:18px;font-family:sans-serif;'>Choose resolution and click <b>Load HUDF Image</b>.</div>"
)


def _reload_cold(_button=None):
    cold_output.value = _cold_spot_html(fov_widget.value, survey_widget.value)


def _reload_hudf(_button=None):
    if quality_widget.value == "full":
        hudf_output.value = _hudf_html(JWST_HUDF_FULL, "10826 × 4946 full display resolution")
    else:
        hudf_output.value = _hudf_html(JWST_HUDF_2000, "2000 × 914 tablet-friendly resolution")


cold_refresh.on_click(_reload_cold)
hudf_refresh.on_click(_reload_hudf)

cold_tab = widgets.VBox(
    [
        widgets.HBox([fov_widget, survey_widget]),
        cold_refresh,
        cold_output,
    ],
    layout=widgets.Layout(width="100%"),
)

hudf_tab = widgets.VBox(
    [
        quality_widget,
        hudf_refresh,
        hudf_output,
    ],
    layout=widgets.Layout(width="100%"),
)

tabs = widgets.Tab(children=[cold_tab, hudf_tab])
tabs.set_title(0, "Cold Spot sky image")
tabs.set_title(1, "JWST HUDF")

display(widgets.VBox([header, tabs], layout=widgets.Layout(width="100%")))
