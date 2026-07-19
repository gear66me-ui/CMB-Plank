"""CMB-0027 — CMB-0006-style Cold Spot, JWST HUDF, and Hubble HUDF viewer."""
from __future__ import annotations

import html
import urllib.parse
import ipywidgets as widgets
from IPython.display import display

VERSION = "CMB-0027"

COLD_SPOT_RA_DEG = 48.299911
COLD_SPOT_DEC_DEG = -20.437305

HUDF_RA = "03:32:39.99"
HUDF_DEC = "-27:48:00.00"
HUDF_GAL_L = 223.5703
HUDF_GAL_B = -54.3925

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
JWST_HUDF_PAGE = "https://science.nasa.gov/asset/webb/webb-observations-of-hudf-nircam-image/"

HUBBLE_IMAGES = {
    "ACS optical HUDF — 2005": (
        "https://assets.science.nasa.gov/dynamicimage/assets/science/missions/hubble/"
        "releases/2005/09/STScI-01EVVM9R75RVTEHV4R6SDT34D3.tif?w=3100"
    ),
    "WFC3 infrared HUDF — 2012": (
        "https://assets.science.nasa.gov/dynamicimage/assets/science/missions/hubble/"
        "releases/2012/12/STScI-01EVVCWPEC63PAR55Q69PKR6H9.tif?w=3000"
    ),
    "HUDF full-color composite — 6200 px": (
        "https://assets.science.nasa.gov/dynamicimage/assets/science/missions/webb/science/2022/06/"
        "STScI-01FY71JR7WXK6AH6307T6X3J8M.png?crop=faces%2Cfocalpoint&fit=clip&h=6200&w=6200"
    ),
}
HUBBLE_PAGE = "https://science.nasa.gov/mission/hubble/science/explore-the-night-sky/hubble-ultra-deep-field/"


def _aladin_url(fov_deg: float, survey: str) -> str:
    target = f"{COLD_SPOT_RA_DEG} {COLD_SPOT_DEC_DEG}"
    params = {"target": target, "fov": f"{float(fov_deg):g}", "survey": survey}
    return "https://aladin.u-strasbg.fr/AladinLite/?" + urllib.parse.urlencode(params)


def _cold_spot_html(fov_deg: float, survey: str) -> str:
    url = _aladin_url(fov_deg, survey)
    return f"""
    <div style="border:1px solid #b0bec5;border-radius:10px;overflow:hidden;background:#101418;">
      <div style="padding:9px 12px;background:#0b172a;color:white;font-family:sans-serif;">
        <b>Famous CMB Cold Spot direction</b><br>
        <span style="font-size:12px;opacity:0.88;">
          ICRS RA {COLD_SPOT_RA_DEG:.6f}°, Dec {COLD_SPOT_DEC_DEG:.6f}° · approximately Galactic l=209°, b=-57°
        </span>
      </div>
      <iframe src="{html.escape(url)}" style="width:100%;height:720px;border:0;display:block;" allowfullscreen></iframe>
    </div>
    """


def _image_panel(image_url: str, title: str, subtitle: str, source_page: str) -> str:
    safe_image = html.escape(image_url)
    safe_page = html.escape(source_page)
    return f"""
    <div style="border:1px solid #b0bec5;border-radius:10px;background:#050607;overflow:hidden;">
      <div style="padding:9px 12px;background:#0b172a;color:white;font-family:sans-serif;">
        <b>{html.escape(title)}</b><br>
        <span style="font-size:12px;opacity:0.88;">
          RA {HUDF_RA}, Dec {HUDF_DEC} · Galactic l≈{HUDF_GAL_L:.4f}°, b≈{HUDF_GAL_B:.4f}° · {html.escape(subtitle)}
        </span>
      </div>
      <div style="height:760px;overflow:auto;text-align:center;background:#000;">
        <img src="{safe_image}" alt="{html.escape(title)}" style="display:block;max-width:none;height:auto;margin:0 auto;" loading="eager">
      </div>
      <div style="padding:7px 12px;background:#eceff1;font:12px sans-serif;">
        Drag the scrollbars to inspect the image at native display scale.
        <a href="{safe_image}" target="_blank" rel="noopener">Open image alone</a> ·
        <a href="{safe_page}" target="_blank" rel="noopener">Official source page</a>
      </div>
    </div>
    """


header = widgets.HTML(value=f"""
<div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;">
  <div style="font-size:22px;font-weight:700;">COLD SPOT + JWST + HUBBLE HUDF VIEWER — {VERSION}</div>
  <div style="font-size:13px;opacity:0.88;margin-top:4px;">CMB-0006 layout preserved, with one additional Hubble tab · real imagery only</div>
</div>
""")

fov_widget = widgets.Dropdown(
    options=[("0.25° — detailed field", 0.25), ("0.5°", 0.5), ("1°", 1.0), ("5°", 5.0), ("10° — broad Cold Spot region", 10.0)],
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
cold_refresh = widgets.Button(description="Reload Cold Spot View", button_style="primary", icon="refresh", layout=widgets.Layout(width="210px", height="38px"))
cold_output = widgets.HTML(value=_cold_spot_html(fov_widget.value, survey_widget.value))

jwst_quality = widgets.ToggleButtons(options=[("Full 10826 × 4946", "full"), ("Tablet 2000 × 914", "tablet")], value="full", description="JWST image:")
jwst_refresh = widgets.Button(description="Load JWST HUDF", button_style="primary", icon="image", layout=widgets.Layout(width="180px", height="38px"))
jwst_output = widgets.HTML(value="<div style='padding:18px;font-family:sans-serif;'>Choose resolution and click <b>Load JWST HUDF</b>.</div>")

hubble_select = widgets.Dropdown(options=list(HUBBLE_IMAGES.keys()), value=list(HUBBLE_IMAGES.keys())[0], description="Hubble image:", layout=widgets.Layout(width="520px"))
hubble_refresh = widgets.Button(description="Load Hubble HUDF", button_style="success", icon="telescope", layout=widgets.Layout(width="190px", height="38px"))
hubble_output = widgets.HTML(value="<div style='padding:18px;font-family:sans-serif;'>Choose a Hubble image and click <b>Load Hubble HUDF</b>.</div>")


def _reload_cold(_button=None):
    cold_output.value = _cold_spot_html(fov_widget.value, survey_widget.value)


def _reload_jwst(_button=None):
    if jwst_quality.value == "full":
        jwst_output.value = _image_panel(JWST_HUDF_FULL, "JWST observations of the Hubble Ultra Deep Field", "10826 × 4946 full display resolution", JWST_HUDF_PAGE)
    else:
        jwst_output.value = _image_panel(JWST_HUDF_2000, "JWST observations of the Hubble Ultra Deep Field", "2000 × 914 tablet-friendly resolution", JWST_HUDF_PAGE)


def _reload_hubble(_button=None):
    label = hubble_select.value
    hubble_output.value = _image_panel(HUBBLE_IMAGES[label], f"Hubble Ultra Deep Field — {label}", "Official NASA/ESA Hubble image", HUBBLE_PAGE)


cold_refresh.on_click(_reload_cold)
jwst_refresh.on_click(_reload_jwst)
hubble_refresh.on_click(_reload_hubble)

cold_tab = widgets.VBox([widgets.HBox([fov_widget, survey_widget]), cold_refresh, cold_output], layout=widgets.Layout(width="100%"))
jwst_tab = widgets.VBox([jwst_quality, jwst_refresh, jwst_output], layout=widgets.Layout(width="100%"))
hubble_tab = widgets.VBox([widgets.HBox([hubble_select, hubble_refresh]), hubble_output], layout=widgets.Layout(width="100%"))

tabs = widgets.Tab(children=[cold_tab, jwst_tab, hubble_tab])
tabs.set_title(0, "Cold Spot sky image")
tabs.set_title(1, "JWST HUDF")
tabs.set_title(2, "Hubble HUDF")

display(widgets.VBox([header, tabs], layout=widgets.Layout(width="100%")))
