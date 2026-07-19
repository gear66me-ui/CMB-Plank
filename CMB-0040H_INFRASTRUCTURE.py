# CMB-0040H_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request

BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040C_INFRASTRUCTURE.py'
source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace('# CMB-0040C_INFRASTRUCTURE.py', '# CMB-0040H_INFRASTRUCTURE.py')
source = source.replace("VERSION = 'CMB-0040C'", "VERSION = 'CMB-0040H'")
source = source.replace(
    'Original Aladin touch map · drag to pan · pinch or use +/- to zoom · real HiPS survey imagery',
    'Aladin Lite API map · coordinate copy enabled · full Galaxy Inspector preserved'
)

new_viewer = """def viewer_html(target_text, fov_deg, survey_id):
    import uuid
    viewer_id = 'aladin_' + uuid.uuid4().hex[:10]
    target_js = str(target_text).strip().replace('\\\\', '\\\\\\\\').replace("'", "\\\\'")
    survey_js = str(survey_id).strip().replace('\\\\', '\\\\\\\\').replace("'", "\\\\'")
    fov_js = float(fov_deg)
    return '''
<div style="width:100%;background:#000;color:#fff;border-radius:8px;overflow:hidden;font-family:Arial,Helvetica,sans-serif;">
  <link rel="stylesheet" href="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.min.css" />
  <div style="padding:10px 12px;background:#050505;border-bottom:1px solid #222;display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
    <button id="{vid}_copy_center" style="background:#1565c0;color:white;border:0;border-radius:5px;padding:7px 10px;font-weight:700;">Copy center RA Dec</button>
    <button id="{vid}_copy_cursor" style="background:#4527a0;color:white;border:0;border-radius:5px;padding:7px 10px;font-weight:700;">Copy cursor RA Dec</button>
    <button id="{vid}_copy_click" style="background:#2e7d32;color:white;border:0;border-radius:5px;padding:7px 10px;font-weight:700;">Copy clicked RA Dec</button>
    <span id="{vid}_readout" style="color:#e0e0e0;font-size:13px;margin-left:6px;">Move or click the map. Right-click also opens Aladin copy menu.</span>
  </div>
  <div id="{vid}" style="width:100%;height:820px;background:#000;"></div>
  <script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js"></script>
  <script>
  (function() {{
    const id = '{vid}';
    const readout = document.getElementById(id + '_readout');
    let aladin = null;
    let lastCursor = '';
    let lastClick = '';
    function fmt(pair) {{
      if (!pair || pair.length < 2) return '';
      const ra = Number(pair[0]);
      const dec = Number(pair[1]);
      if (!Number.isFinite(ra) || !Number.isFinite(dec)) return '';
      return ra.toFixed(8) + ' ' + dec.toFixed(8);
    }}
    async function copyText(txt, label) {{
      if (!txt) {{
        readout.innerHTML = '<span style="color:#ffb74d">No ' + label + ' coordinate yet.</span>';
        return;
      }}
      try {{
        await navigator.clipboard.writeText(txt);
        readout.innerHTML = '<span style="color:#81c784">Copied ' + label + ': <b>' + txt + '</b></span>';
      }} catch (e) {{
        readout.innerHTML = '<span style="color:#ffb74d">Clipboard blocked. Select/copy manually: <b>' + txt + '</b></span>';
      }}
    }}
    function boot() {{
      if (!window.A || !A.aladin) {{ setTimeout(boot, 250); return; }}
      aladin = A.aladin('#' + id, {{
        target: '{target}',
        fov: {fov},
        survey: '{survey}',
        showContextMenu: true,
        showCooGridControl: true,
        showSimbadPointerControl: true,
        showShareControl: true,
        showFullscreenControl: true,
        showReticle: true
      }});
      aladin.on('positionChanged', function() {{
        const center = fmt(aladin.getRaDec());
        if (center) readout.innerHTML = 'Center: <b>' + center + '</b>' + (lastClick ? ' · Last click: <b>' + lastClick + '</b>' : '');
      }});
      aladin.on('mouseMove', function(pos) {{ lastCursor = fmt(pos); }});
      aladin.on('click', function(pos) {{
        lastClick = fmt(pos);
        readout.innerHTML = 'Clicked: <b>' + lastClick + '</b> · use Copy clicked, then paste into the one ICRS cell below.';
      }});
      document.getElementById(id + '_copy_center').onclick = function() {{ copyText(fmt(aladin.getRaDec()), 'center'); }};
      document.getElementById(id + '_copy_cursor').onclick = function() {{ copyText(lastCursor, 'cursor'); }};
      document.getElementById(id + '_copy_click').onclick = function() {{ copyText(lastClick, 'clicked'); }};
    }}
    boot();
  }})();
  </script>
</div>
'''.format(vid=viewer_id, target=target_js, fov=fov_js, survey=survey_js)

"""

start = source.index('def viewer_html(target_text, fov_deg, survey_id):')
end = source.index('\n\ndef dark_box', start)
source2 = source[:start] + new_viewer + source[end + 2:]
exec(compile(source2, 'CMB-0040H_INFRASTRUCTURE.py', 'exec'))
