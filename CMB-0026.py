"""CMB-0026 — Multi-mission real-sky Aladin Lite widget with Hubble HiPS options.

The Aladin layer browser retains access to the full CDS HiPS collection (XMM,
Chandra, GALEX, radio, infrared, optical, etc.) while the external dropdown adds
quick access to selected Hubble surveys.
"""
from __future__ import annotations

import base64
import html

import ipywidgets as widgets
from IPython.display import display

VERSION = "CMB-0026"

SURVEYS = [
    ("Hubble Outreach color — broad HST collection", "CDS/P/HST/EPO"),
    ("Hubble GOODS color — HUDF/GOODS region", "CDS/P/HST/GOODS/color"),
    ("Hubble GOODS i-band", "CDS/P/HST/GOODS/i"),
    ("Hubble R-band archive", "CDS/P/HST/R"),
    ("Hubble H-alpha", "CDS/P/HST/Halpha"),
    ("Hubble H-beta", "CDS/P/HST/Hbeta"),
    ("DSS2 color", "P/DSS2/color"),
    ("Pan-STARRS DR1 color", "P/PanSTARRS/DR1/color-z-zg-g"),
    ("2MASS infrared", "P/2MASS/color"),
    ("WISE infrared", "P/allWISE/color"),
    ("GALEX GR6/7 ultraviolet", "P/GALEXGR6/AIS/color"),
]


def _document(lon: float, lat: float, frame: str, fov_deg: float, survey_id: str) -> str:
    cooframe = "galactic" if frame == "Galactic" else "ICRS"
    target = f"{lon:.10f} {lat:.10f}"
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.css">
<style>
html,body,#aladin-lite-div{{width:100%;height:100%;margin:0;background:#02050a;overflow:hidden;}}
#note{{position:absolute;left:10px;bottom:10px;z-index:25;background:rgba(3,10,22,.88);color:#fff;
padding:8px 10px;border-radius:8px;font:12px/1.35 sans-serif;max-width:78%;pointer-events:none;}}
</style>
</head>
<body>
<div id="aladin-lite-div"></div>
<div id="note">Survey: {html.escape(survey_id)} · Open the Layers control inside the map to search the complete CDS HiPS collection.</div>
<script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
<script>
A.init.then(() => {{
  const aladin = A.aladin('#aladin-lite-div', {{
    survey: {survey_id!r},
    target: {target!r},
    fov: {float(fov_deg)!r},
    cooFrame: {cooframe!r},
    projection: 'TAN',
    showReticle: true,
    showGotoControl: true,
    showFullscreenControl: true,
    showLayersControl: true,
    showSimbadPointerControl: true,
    showCooGridControl: true,
    showContextMenu: true
  }});

  const center = A.catalog({{name:'Exact entered coordinate', sourceSize:18, color:'#00ffff', shape:'cross'}});
  if ({frame!r} === 'Galactic') {{
    const c = new Coo({lon}, {lat}, 8);
    c.convertToFrame('J2000');
    center.addSources([A.marker(c.lon, c.lat, {{popupTitle:'Entered Galactic coordinate', popupDesc:'l={lon:.8f}°, b={lat:.8f}°'}})]);
  }} else {{
    center.addSources([A.marker({lon}, {lat}, {{popupTitle:'Entered ICRS coordinate', popupDesc:'RA={lon:.8f}°, Dec={lat:.8f}°'}})]);
  }}
  aladin.addCatalog(center);
}}).catch(err => {{ document.getElementById('note').textContent = 'Viewer error: ' + err; }});
</script>
</body>
</html>"""


def _iframe(lon: float, lat: float, frame: str, fov_deg: float, survey_id: str) -> str:
    doc = _document(lon, lat, frame, fov_deg, survey_id)
    encoded = base64.b64encode(doc.encode("utf-8")).decode("ascii")
    return f'<iframe src="data:text/html;base64,{encoded}" style="width:100%;height:780px;border:1px solid #607d8b;border-radius:10px;background:#02050a;" allowfullscreen></iframe>'

header = widgets.HTML(value=f"""
<div style="padding:12px 16px;border-radius:10px;background:#08172b;color:white;font-family:sans-serif;">
<div style="font-size:22px;font-weight:700;">MULTI-MISSION REAL SKY — {VERSION}</div>
<div style="font-size:13px;opacity:.9;margin-top:4px;">Hubble quick-select plus the complete Aladin/CDS HiPS survey browser</div>
<div style="font-size:12px;opacity:.75;margin-top:3px;">Real astronomical survey tiles · no generated imagery</div>
</div>
""")

frame = widgets.Dropdown(options=["Galactic", "ICRS / Equatorial"], value="Galactic", description="Coordinates:", layout=widgets.Layout(width="270px"))
lon = widgets.FloatText(value=223.5703, description="l / RA (deg):", layout=widgets.Layout(width="250px"))
lat = widgets.FloatText(value=-54.3925, description="b / Dec (deg):", layout=widgets.Layout(width="250px"))
fov = widgets.Dropdown(options=[("0.5 arcmin", 0.5/60), ("1 arcmin", 1/60), ("3 arcmin", 3/60), ("6 arcmin", 6/60), ("12 arcmin", 12/60), ("30 arcmin", 0.5), ("1 degree", 1.0)], value=6/60, description="Field:", layout=widgets.Layout(width="240px"))
survey = widgets.Dropdown(options=SURVEYS, value="CDS/P/HST/GOODS/color", description="Quick survey:", layout=widgets.Layout(width="520px"))
custom = widgets.Text(value="", placeholder="Optional CDS HiPS ID, e.g. CDS/P/HST/EPO", description="Custom ID:", layout=widgets.Layout(width="520px"))
load = widgets.Button(description="Load Survey Map", button_style="primary", icon="globe", layout=widgets.Layout(width="190px", height="38px"))
viewer = widgets.HTML(value=_iframe(lon.value, lat.value, frame.value, fov.value, survey.value))

helpbox = widgets.HTML(value="""
<div style="padding:10px 12px;background:#eef6ff;border-left:4px solid #1565c0;font:13px sans-serif;line-height:1.45;">
<b>How to reach every mission:</b> use the quick dropdown for Hubble and common surveys. Inside the map, open the <b>Layers</b> control and search the complete CDS HiPS registry for XMM, Chandra, GALEX, Planck, Herschel, VLA, and many others. Hubble is not all-sky; a Hubble layer appears only where HST actually observed. For HUDF, keep Galactic coordinates <b>223.5703, −54.3925</b> and choose <b>Hubble GOODS color</b>.
</div>
""")


def _reload(_=None):
    sid = custom.value.strip() or survey.value
    viewer.value = _iframe(float(lon.value), float(lat.value), frame.value, float(fov.value), sid)

load.on_click(_reload)
controls = widgets.VBox([
    widgets.HBox([frame, lon, lat]),
    widgets.HBox([fov, load]),
    survey,
    custom,
])
display(widgets.VBox([header, controls, helpbox, viewer], layout=widgets.Layout(width="100%")))
