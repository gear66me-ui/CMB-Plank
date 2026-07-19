"""CMB-0028 — Interactive multi-mission Aladin sky map with Hubble and JWST survey choices."""
from __future__ import annotations

import base64
import html
import ipywidgets as widgets
from IPython.display import display

VERSION = "CMB-0028"
DEFAULT_TARGET = "48.299911 -20.437305"
DEFAULT_FOV = 1.0

SURVEYS = [
    ("eROSITA DR1", "P/eROSITA/DE_DR1_RGB"),
    ("Fermi", "P/Fermi/color"),
    ("XMM PN", "P/XMM/PN/color"),
    ("Chandra", "P/Chandra/color"),
    ("GALEX GR6_7", "P/GALEXGR6/AIS/color"),
    ("DSS2 blue", "P/DSS2/blue"),
    ("DSS2 color", "P/DSS2/color"),
    ("2MASS color", "P/2MASS/color"),
    ("WISE color", "P/allWISE/color"),
    ("Hubble GOODS color", "CDS/P/HST/GOODS/color"),
    ("Hubble GOODS i-band", "CDS/P/HST/GOODS/i"),
    ("Hubble R-band", "CDS/P/HST/R"),
    ("Hubble H-alpha", "CDS/P/HST/Halpha"),
    ("Hubble H-beta", "CDS/P/HST/Hbeta"),
    ("JWST First Images", "CDS/P/JWST/First-Images"),
    ("JWST F150W", "CDS/P/JWST/F150W"),
    ("JWST F444W", "CDS/P/JWST/F444W"),
    ("JWST F480M", "CDS/P/JWST/F480M"),
    ("JWST OPEN", "CDS/P/JWST/OPEN"),
]


def _document(target: str, fov: float, survey_id: str) -> str:
    safe_target = html.escape(target)
    survey_buttons = "\n".join(
        f'<button class="survey" data-id="{html.escape(sid)}">{html.escape(label)}</button>'
        for label, sid in SURVEYS
    )
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=yes">
<link rel="stylesheet" href="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.css">
<style>
html,body{{margin:0;height:100%;background:#03070d;color:white;font-family:Arial,sans-serif;overflow:hidden}}
#wrap{{display:grid;grid-template-columns:minmax(210px,28%) 1fr;height:100%}}
#panel{{overflow:auto;background:#eef2f6;color:#111;padding:12px;border-right:1px solid #54606c}}
#panel h2{{margin:0 0 10px;font-size:22px}}
#target{{width:100%;box-sizing:border-box;font-size:19px;padding:10px;margin-bottom:10px}}
#go{{width:100%;padding:10px;font-size:16px;font-weight:700;margin-bottom:12px}}
.survey{{display:block;width:100%;text-align:left;border:0;border-radius:10px;padding:13px 12px;margin:6px 0;background:#152238;color:white;font-size:17px;cursor:pointer}}
.survey:hover,.survey.active{{background:#1565c0}}
#viewer{{position:relative;min-width:0}}
#aladin-lite-div{{width:100%;height:100%;background:black}}
#status{{position:absolute;left:10px;bottom:10px;z-index:50;background:rgba(0,0,0,.72);padding:7px 10px;border-radius:7px;font-size:12px;max-width:80%}}
@media(max-width:700px){{#wrap{{grid-template-columns:40% 60%}} .survey{{font-size:15px;padding:11px 8px}} #panel h2{{font-size:18px}}}}
</style>
</head>
<body>
<div id="wrap">
  <div id="panel">
    <h2>Target</h2>
    <input id="target" value="{safe_target}" aria-label="Target coordinate">
    <button id="go">Go to target</button>
    <h2>Surveys</h2>
    {survey_buttons}
  </div>
  <div id="viewer">
    <div id="aladin-lite-div"></div>
    <div id="status">Loading interactive sky map…</div>
  </div>
</div>
<script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
<script>
A.init.then(() => {{
  const aladin = A.aladin('#aladin-lite-div', {{
    survey: {survey_id!r},
    target: {target!r},
    fov: {float(fov)!r},
    cooFrame: 'ICRS',
    showReticle: true,
    showGotoControl: true,
    showFullscreenControl: true,
    showLayersControl: true,
    showSimbadPointerControl: true,
    showCooGridControl: true,
    showZoomControl: true
  }});

  const status = document.getElementById('status');
  const buttons = Array.from(document.querySelectorAll('.survey'));

  async function loadSurvey(id, button) {{
    status.textContent = 'Loading ' + button.textContent + '…';
    buttons.forEach(b => b.classList.remove('active'));
    button.classList.add('active');
    try {{
      const survey = aladin.createImageSurvey(id, id, id, 'equatorial', 13, {{imgFormat:'png'}});
      aladin.setBaseImageLayer(survey);
      status.textContent = button.textContent + ' selected. Drag to pan; pinch or wheel to zoom.';
    }} catch (err) {{
      try {{
        aladin.setImageSurvey(id);
        status.textContent = button.textContent + ' selected. Drag to pan; pinch or wheel to zoom.';
      }} catch (err2) {{
        status.textContent = 'Survey unavailable here or failed to load: ' + button.textContent;
      }}
    }}
  }}

  buttons.forEach(button => button.addEventListener('click', () => loadSurvey(button.dataset.id, button)));
  const first = buttons.find(b => b.dataset.id === {survey_id!r});
  if (first) first.classList.add('active');

  document.getElementById('go').addEventListener('click', () => {{
    const value = document.getElementById('target').value.trim();
    if (!value) return;
    aladin.gotoObject(value);
    status.textContent = 'Target: ' + value;
  }});
  document.getElementById('target').addEventListener('keydown', e => {{
    if (e.key === 'Enter') document.getElementById('go').click();
  }});

  status.textContent = 'Ready. Drag to pan; pinch or wheel to zoom; choose Hubble or JWST at left.';
}}).catch(err => {{
  document.getElementById('status').textContent = 'Viewer error: ' + err;
}});
</script>
</body>
</html>"""


def _iframe(target: str, fov: float, survey_id: str) -> str:
    doc = _document(target, fov, survey_id)
    encoded = base64.b64encode(doc.encode("utf-8")).decode("ascii")
    return f'<iframe src="data:text/html;base64,{encoded}" style="width:100%;height:840px;border:1px solid #607d8b;border-radius:10px;background:#000" allowfullscreen></iframe>'

header = widgets.HTML(value=f"""
<div style="background:#0b172a;color:white;padding:14px 16px;border-radius:10px;font-family:sans-serif">
  <div style="font-size:22px;font-weight:700">INTERACTIVE MULTI-MISSION SKY MAP — {VERSION}</div>
  <div style="font-size:13px;margin-top:5px;opacity:.9">Same pinch-to-zoom and drag-to-pan sky viewer, now with direct Hubble and JWST survey buttons.</div>
</div>
""")

viewer = widgets.HTML(value=_iframe(DEFAULT_TARGET, DEFAULT_FOV, "P/DSS2/color"))
notes = widgets.HTML(value="""
<div style="padding:10px 12px;border-left:4px solid #1565c0;background:#e3f2fd;font:13px sans-serif">
<b>Coverage note:</b> Hubble and JWST are not all-sky surveys. Their buttons show data only where those telescopes actually observed. A blank area usually means no coverage at that coordinate, not a broken map.
</div>
""")

display(widgets.VBox([header, notes, viewer], layout=widgets.Layout(width="100%")))
