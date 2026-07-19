# CMB-0039Q_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from pathlib import Path
import runpy

SRC_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0039P_INFRASTRUCTURE.py'
GENERATED = Path('CMB-0039Q_GENERATED_INFRASTRUCTURE.py')

text = urllib.request.urlopen(SRC_URL, timeout=60).read().decode('utf-8')
if text.strip().startswith('404'):
    raise RuntimeError('GitHub returned 404 for CMB-0039P_INFRASTRUCTURE.py')

text = text.replace('CMB-0039P', 'CMB-0039Q')
text = text.replace('import html\n', 'import html\nimport json\n')
text = text.replace("from IPython.display import display, HTML, FileLink, clear_output", "from IPython.display import display, HTML, FileLink, clear_output, Javascript")

old_viewer_html = """def viewer_html(target_text, fov_deg, survey_id, survey_name):
    url = aladin_url(target_text, fov_deg, survey_id)
    return f'''
    <div style=\"width:100%;background:#000;overflow:visible;\">
      <iframe src=\"{html.escape(url)}\"
        style=\"width:100%;height:820px;border:0;display:block;background:#000;overflow:visible;\"
        allow=\"fullscreen; clipboard-read; clipboard-write\"
        allowfullscreen>
      </iframe>
    </div>
    '''
"""
new_viewer_html = """def viewer_html(target_text, fov_deg, survey_id, survey_name):
    target_js = json.dumps(str(target_text).strip())
    survey_js = json.dumps(str(survey_id))
    fov_js = json.dumps(float(fov_deg))
    label = html.escape(str(survey_name))
    target_label = html.escape(str(target_text).strip())
    return f'''
    <link rel=\"stylesheet\" href=\"https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.min.css\">
    <script src=\"https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js\"></script>
    <div style=\"width:100%;background:#000;overflow:visible;border:1px solid #263238;border-radius:8px;\">
      <div style=\"padding:8px 12px;background:#0b172a;color:white;font-family:sans-serif;display:flex;gap:16px;align-items:center;flex-wrap:wrap\">
        <b>{label}</b>
        <span style=\"font-size:12px;opacity:.85\">Target: {target_label} · FOV {float(fov_deg):g}°</span>
        <span id=\"cmb39q-status\" style=\"font-size:12px;color:#90caf9\">AladinLite loading…</span>
      </div>
      <div id=\"cmb39q-aladin\" style=\"width:100%;height:820px;background:#000;position:relative;\"></div>
    </div>
    <script>
    (function() {{
      const target = {target_js};
      const survey = {survey_js};
      const fov = {fov_js};
      const status = document.getElementById('cmb39q-status');
      function makeAladin() {{
        try {{
          window.CMB0039Q_ALADIN = A.aladin('#cmb39q-aladin', {{
            target: target,
            survey: survey,
            fov: fov,
            showReticle: true,
            showFullscreenControl: true,
            showLayersControl: true,
            showGotoControl: true,
            showFrame: true,
            showCooGridControl: true,
            showSimbadPointerControl: true
          }});
          if (status) status.textContent = 'AladinLite ready — pan/zoom, then press Get coordinates from Aladin below.';
        }} catch (err) {{
          if (status) status.textContent = 'Aladin init error: ' + err;
        }}
      }}
      function start() {{
        if (typeof A === 'undefined') {{ setTimeout(start, 250); return; }}
        if (A.init && A.init.then) {{ A.init.then(makeAladin); }} else {{ makeAladin(); }}
      }}
      start();
    }})();
    </script>
    '''
"""
if old_viewer_html not in text:
    raise RuntimeError('viewer_html block not found in CMB-0039P source')
text = text.replace(old_viewer_html, new_viewer_html, 1)

old_viewer_setup = """viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, survey.value, 'Hubble GOODS color'))

def reload_map(_=None):
    viewer.value = viewer_html(target.value, fov.value, survey.value, selected_name())
"""
new_viewer_setup = """viewer = widgets.Output(layout=widgets.Layout(width='100%'))

def render_aladin():
    with viewer:
        clear_output(wait=True)
        display(HTML(viewer_html(target.value, fov.value, survey.value, selected_name())))

def reload_map(_=None):
    render_aladin()
"""
if old_viewer_setup not in text:
    raise RuntimeError('viewer setup block not found in CMB-0039P source')
text = text.replace(old_viewer_setup, new_viewer_setup, 1)

old_get_coords = """def get_coordinates_from_aladin(_=None):
    # The Colab iframe is cross-origin, so Python cannot read a panned Aladin center directly.
    # This restores the requested button and loads the current Aladin target/center into the single inspector cell.
    try:
        coord = parse_target(target.value)
        _set_coord_fields(coord)
        coord_status.value = '<b style=\"color:#1565c0\">Coordinates loaded from current Aladin target into the single RA Dec cell.</b>'
    except Exception as exc:
        coord_status.value = f'<b style=\"color:#b71c1c\">Coordinate fetch failed: {html.escape(str(exc))}</b>'
"""
new_get_coords = """def _colab_set_coords(ra_dec):
    try:
        text_value = str(ra_dec).strip()
        coord = parse_target(text_value)
        _set_coord_fields(coord)
        coord_status.value = '<b style=\"color:#1b5e20\">Coordinates fetched from live Aladin center into the single RA Dec cell.</b>'
    except Exception as exc:
        coord_status.value = f'<b style=\"color:#b71c1c\">Coordinate fetch failed: {html.escape(str(exc))}</b>'

try:
    from google.colab import output as _colab_output
    _colab_output.register_callback('cmb0039q.set_coords', _colab_set_coords)
except Exception:
    _colab_output = None

def get_coordinates_from_aladin(_=None):
    if _colab_output is None:
        coord_status.value = '<b style=\"color:#b71c1c\">Live Aladin coordinate fetch requires Google Colab callback support.</b>'
        return
    display(Javascript('''
    (async function() {
      try {
        const aladin = window.CMB0039Q_ALADIN;
        if (!aladin || !aladin.getRaDec) {
          alert('Aladin viewer is not ready yet. Press Load Interactive Map, wait a few seconds, then try again.');
          return;
        }
        const rd = aladin.getRaDec();
        if (!rd || rd.length < 2) {
          alert('Could not read Aladin center coordinates.');
          return;
        }
        const text = Number(rd[0]).toFixed(8) + ' ' + Number(rd[1]).toFixed(8);
        await google.colab.kernel.invokeFunction('cmb0039q.set_coords', [text], {});
      } catch (err) {
        alert('Coordinate bridge error: ' + err);
      }
    })();
    '''))
"""
if old_get_coords not in text:
    raise RuntimeError('get_coordinates_from_aladin block not found in CMB-0039P source')
text = text.replace(old_get_coords, new_get_coords, 1)

text = text.replace('get_coordinates_from_aladin()\n\ninspector = widgets.VBox', 'render_aladin()\nget_coordinates_from_aladin()\n\ninspector = widgets.VBox')

GENERATED.write_text(text, encoding='utf-8')
compile(text, str(GENERATED), 'exec')
runpy.run_path(str(GENERATED), run_name='__main__')
