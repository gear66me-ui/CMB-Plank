"""CMB-0007 — Interactive Gaia DR3 map for the selected sky position.

Run with:
    %run CMB-0007.py

Maps RA 03:12:59.96, Dec -20:02:09.0 with a center marker and Gaia DR3
catalog sources over real survey imagery. Click any Gaia marker to inspect its
catalog measurements.
"""

from __future__ import annotations

import base64
import html

import ipywidgets as widgets
from IPython.display import display

VERSION = "CMB-0007"
RA_SEXAGESIMAL = "03:12:59.96"
DEC_SEXAGESIMAL = "-20:02:09.0"
RA_DEG = 48.2498333333
DEC_DEG = -20.0358333333


def _viewer_document(fov_deg: float, survey: str, radius_deg: float) -> str:
    target = f"{RA_DEG:.10f} {DEC_DEG:.10f}"
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.css">
<style>
html,body,#aladin-lite-div{{width:100%;height:100%;margin:0;background:#05070a;overflow:hidden;}}
#status{{position:absolute;left:10px;bottom:10px;z-index:20;background:rgba(5,12,24,.88);color:white;
padding:7px 10px;border-radius:7px;font:12px/1.35 sans-serif;max-width:72%;pointer-events:none;}}
</style>
</head>
<body>
<div id="aladin-lite-div"></div>
<div id="status">Loading real sky imagery and Gaia DR3 sources…</div>
<script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
<script>
A.init.then(() => {{
  const aladin = A.aladin('#aladin-lite-div', {{
    survey: {survey!r},
    target: {target!r},
    fov: {float(fov_deg)!r},
    cooFrame: 'ICRS',
    showReticle: true,
    showGotoControl: true,
    showFullscreenControl: true,
    showLayersControl: true,
    showSimbadPointerControl: true,
    showCooGridControl: true
  }});

  const centerCat = A.catalog({{name:'Selected coordinate', sourceSize:18, color:'#00ff72', shape:'circle'}});
  centerCat.addSources([A.marker({RA_DEG:.10f}, {DEC_DEG:.10f}, {{
    popupTitle:'Selected coordinate',
    popupDesc:'RA {html.escape(RA_SEXAGESIMAL)}<br>Dec {html.escape(DEC_SEXAGESIMAL)}<br>Green circle marks the exact supplied position.'
  }})]);
  aladin.addCatalog(centerCat);

  const status = document.getElementById('status');
  const gaia = A.catalogFromVizieR(
    'I/355/gaiadr3',
    {{ra:{RA_DEG:.10f}, dec:{DEC_DEG:.10f}}},
    {float(radius_deg)!r},
    {{name:'Gaia DR3', sourceSize:10, color:'#ffd400', shape:'cross', onClick:'showTable'}},
    (sources) => {{
      status.textContent = `Gaia DR3: ${{sources.length}} source(s) loaded. Green circle = supplied coordinate; yellow crosses = Gaia sources. Click a cross for measurements.`;
    }}
  );
  aladin.addCatalog(gaia);
}}).catch(err => {{
  document.getElementById('status').textContent = 'Viewer error: ' + err;
}});
</script>
</body>
</html>"""


def _iframe_html(fov_deg: float, survey: str, radius_deg: float) -> str:
    document = _viewer_document(fov_deg, survey, radius_deg)
    encoded = base64.b64encode(document.encode("utf-8")).decode("ascii")
    return f"""
    <iframe
      src="data:text/html;base64,{encoded}"
      style="width:100%;height:760px;border:1px solid #78909c;border-radius:10px;background:#05070a;"
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
    Real survey imagery plus Gaia DR3 catalogue data · no generated images
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
