"""CMB-0025 — Interactive Hubble Ultra Deep Field image explorer."""
from __future__ import annotations

from io import BytesIO
import urllib.request

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from IPython.display import display, clear_output, HTML
import ipywidgets as widgets

VERSION = "CMB-0025"

IMAGES = {
    "Hubble ACS optical — 2005 HUDF": {
        "url": "https://assets.science.nasa.gov/dynamicimage/assets/science/missions/hubble/releases/2005/09/STScI-01EVVM9R75RVTEHV4R6SDT34D3.tif?w=3100",
        "field_arcmin": 3.0,
        "credit": "NASA, ESA, S. Beckwith and the HUDF Team (STScI), B. Mobasher (STScI)",
        "filters": "ACS/WFC: F435W, F606W, F775W, F850LP",
    },
    "Hubble WFC3 infrared — HUDF 2012": {
        "url": "https://assets.science.nasa.gov/dynamicimage/assets/science/missions/hubble/releases/2012/12/STScI-01EVVCWPEC63PAR55Q69PKR6H9.tif?w=3000",
        "field_arcmin": 2.25,
        "credit": "NASA, ESA, R. Ellis (Caltech), UDF 2012 Team",
        "filters": "WFC3/IR: F105W, F125W, F140W, F160W",
    },
    "Hubble HUDF full-color — 6200-pixel source": {
        "url": "https://assets.science.nasa.gov/dynamicimage/assets/science/missions/webb/science/2022/06/STScI-01FY71JR7WXK6AH6307T6X3J8M.png?crop=faces%2Cfocalpoint&fit=clip&h=6200&w=6200",
        "field_arcmin": 3.0,
        "credit": "NASA, ESA, HUDF Team, Steven Beckwith (STScI)",
        "filters": "Hubble ultraviolet, visible, and near-infrared composite",
    },
}

_cache = {}

def fetch_image(url: str) -> np.ndarray:
    if url in _cache:
        return _cache[url]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 CMB-HUDF-Widget/25.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read()
    img = Image.open(BytesIO(raw)).convert("RGB")
    arr = np.asarray(img)
    _cache[url] = arr
    return arr

survey = widgets.Dropdown(options=list(IMAGES), value=list(IMAGES)[0], description="Image:", layout=widgets.Layout(width="520px"))
zoom = widgets.FloatSlider(value=1.0, min=1.0, max=20.0, step=0.25, description="Zoom:", continuous_update=False, readout_format=".2f")
xcenter = widgets.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.005, description="Center X:", continuous_update=False, readout_format=".3f")
ycenter = widgets.FloatSlider(value=0.5, min=0.0, max=1.0, step=0.005, description="Center Y:", continuous_update=False, readout_format=".3f")
show_crosshair = widgets.Checkbox(value=False, description="Show center crosshair")
load_button = widgets.Button(description="Load Hubble Image", button_style="success", icon="telescope")
reset_button = widgets.Button(description="Reset View", icon="refresh")
output = widgets.Output()

header = HTML(f"""
<div style='background:#050505;color:white;padding:16px;border-radius:12px;margin-bottom:10px'>
<div style='font-size:22px;font-weight:700'>HUBBLE ULTRA DEEP FIELD — {VERSION}</div>
<div style='margin-top:5px'>Real NASA/STScI Hubble imagery · interactive crop and zoom</div>
<div style='margin-top:5px'>Center: RA 03h 32m 39.99s · Dec −27° 48′ 00″ · Galactic l≈223.5703°, b≈−54.3925°</div>
</div>
""")


def render(_=None):
    meta = IMAGES[survey.value]
    with output:
        clear_output(wait=True)
        print("Loading official Hubble image…")
        try:
            arr = fetch_image(meta["url"])
        except Exception as exc:
            clear_output(wait=True)
            print(f"Image download failed: {exc}")
            return

        h, w = arr.shape[:2]
        z = max(float(zoom.value), 1.0)
        crop_w = max(20, int(round(w / z)))
        crop_h = max(20, int(round(h / z)))
        cx = int(round(float(xcenter.value) * (w - 1)))
        cy = int(round(float(ycenter.value) * (h - 1)))
        x0 = int(np.clip(cx - crop_w // 2, 0, max(0, w - crop_w)))
        y0 = int(np.clip(cy - crop_h // 2, 0, max(0, h - crop_h)))
        x1 = min(w, x0 + crop_w)
        y1 = min(h, y0 + crop_h)
        crop = arr[y0:y1, x0:x1]

        clear_output(wait=True)
        fig, ax = plt.subplots(figsize=(10, 10), dpi=120)
        ax.imshow(crop, origin="upper")
        ax.set_facecolor("black")
        ax.set_xticks([])
        ax.set_yticks([])
        if show_crosshair.value:
            ax.axvline((crop.shape[1] - 1) / 2, linewidth=0.7)
            ax.axhline((crop.shape[0] - 1) / 2, linewidth=0.7)
        shown_arcmin_x = meta["field_arcmin"] * crop.shape[1] / w
        shown_arcmin_y = meta["field_arcmin"] * crop.shape[0] / h
        ax.set_title(
            f"{survey.value}\nDisplayed field ≈ {shown_arcmin_x:.3f}′ × {shown_arcmin_y:.3f}′ · zoom {z:.2f}×",
            fontsize=12,
        )
        plt.tight_layout()
        plt.show()
        display(HTML(
            f"<div style='background:#111;color:#eee;padding:12px;border-radius:10px'>"
            f"<b>Source pixels:</b> {w:,} × {h:,}<br>"
            f"<b>Displayed crop:</b> {crop.shape[1]:,} × {crop.shape[0]:,}<br>"
            f"<b>Filters:</b> {meta['filters']}<br>"
            f"<b>Credit:</b> {meta['credit']}<br>"
            f"<b>Important:</b> this is a fixed Hubble mosaic, not an all-sky Hubble survey. The sliders move within the HUDF itself."
            f"</div>"
        ))


def reset(_=None):
    zoom.value = 1.0
    xcenter.value = 0.5
    ycenter.value = 0.5
    show_crosshair.value = False
    render()

load_button.on_click(render)
reset_button.on_click(reset)

controls = widgets.VBox([
    widgets.HBox([survey, load_button, reset_button]),
    widgets.HBox([zoom, show_crosshair]),
    widgets.HBox([xcenter, ycenter]),
])

display(header, controls, output)
render()
