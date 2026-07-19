# CMB-0040J_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request

BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040C_INFRASTRUCTURE.py'
source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace('# CMB-0040C_INFRASTRUCTURE.py', '# CMB-0040J_INFRASTRUCTURE.py')
source = source.replace("VERSION = 'CMB-0040C'", "VERSION = 'CMB-0040J'")
source = source.replace('Original Aladin touch map · drag to pan · pinch or use +/- to zoom · real HiPS survey imagery', 'One Aladin map · coordinate copy controls attached · Galaxy Finder preserved')

new_viewer = r'''def viewer_html(target_text, fov_deg, survey_id):
    import uuid
    vid = 'cmb40j_' + uuid.uuid4().hex[:10]
    target_js = str(target_text).strip().replace('\\', '\\\\').replace("'", "\\'")
    survey_js = str(survey_id).strip().replace('\\', '\\\\').replace("'", "\\'")
    fov_js = str(float(fov_deg))
    block = """
    <div style="width:100%;background:#000;color:#fff;border-radius:8px;overflow:hidden;font-family:Arial,Helvetica,sans-serif;">
      <div style="padding:10px 12px;background:#050505;border-bottom:1px solid #222;display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
        <button id="__VID___copy_center" style="background:#1565c0;color:white;border:0;border-radius:5px;padding:7px 10px;font-weight:700;">Copy center RA Dec</button>
        <button id="__VID___copy_cursor" style="background:#4527a0;color:white;border:0;border-radius:5px;padding:7px 10px;font-weight:700;">Copy cursor RA Dec</button>
        <button id="__VID___copy_click" style="background:#2e7d32;color:white;border:0;border-radius:5px;padding:7px 10px;font-weight:700;">Copy clicked RA Dec</button>
        <input id="__VID___coord" readonly onclick="this.select()" style="flex:1;min-width:260px;background:#000;color:#fff;border:1px solid #666;border-radius:5px;padding:7px;font-family:monospace;" placeholder="Copied RA Dec appears here">
        <span id="__VID___readout" style="color:#e0e0e0;font-size:13px;width:100%;">Use the buttons here, or right-click/long-press the map for Aladin's native context menu.</span>
      </div>
      <div id="__VID__" style="width:100%;height:820px;background:#000;"></div>
      <script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
      <script>
      (function() {
        const id = '__VID__';
        const readout = document.getElementById(id + '_readout');
        const coordBox = document.getElementById(id + '_coord');
        let aladin = null;
        let lastCursor = null;
        let lastClick = null;
        function good(v) { return Number.isFinite(Number(v)); }
        function fmt(ra, dec) { return Number(ra).toFixed(8) + ' ' + Number(dec).toFixed(8); }
        async function copyText(txt, label) {
          if (!txt) { readout.innerHTML = '<span style="color:#ffb74d">No ' + label + ' coordinate yet.</span>'; return; }
          coordBox.value = txt;
          coordBox.focus();
          coordBox.select();
          try {
            await navigator.clipboard.writeText(txt);
            readout.innerHTML = '<span style="color:#81c784">Copied ' + label + ': <b>' + txt + '</b></span>';
          } catch(e) {
            try { document.execCommand('copy'); } catch(err) {}
            readout.innerHTML = '<span style="color:#ffb74d">Selected ' + label + ': <b>' + txt + '</b>. Long-press/Ctrl+C if clipboard is blocked.</span>';
          }
        }
        function boot() {
          if (!window.A || !A.init) { setTimeout(boot, 250); return; }
          A.init.then(function() {
            aladin = A.aladin('#' + id, {
              target: '__TARGET__',
              fov: __FOV__,
              survey: '__SURVEY__',
              showFrame: true,
              showGotoControl: true,
              showLayersControl: true,
              expandLayersControl: true,
              showShareControl: true,
              showSimbadPointerControl: true,
              showContextMenu: true,
              showReticle: true,
              reticleColor: 'rgb(178,50,178)',
              reticleSize: 22
            });
            readout.innerHTML = 'Ready. This is the only Aladin map. Copy buttons are attached to this map; Galaxy Finder is below.';
            aladin.on('positionChanged', function(p) {
              if (p && good(p.ra) && good(p.dec)) coordBox.value = fmt(p.ra, p.dec);
            });
            aladin.on('mouseMove', function(p) {
              if (p && good(p.ra) && good(p.dec)) lastCursor = {ra:p.ra, dec:p.dec};
            });
            aladin.on('click', function(p) {
              if (p && good(p.ra) && good(p.dec)) {
                lastClick = {ra:p.ra, dec:p.dec};
                coordBox.value = fmt(p.ra, p.dec);
                readout.innerHTML = 'Clicked: <b>' + coordBox.value + '</b>. Copy clicked, then paste into the Galaxy Finder ICRS cell below.';
              }
            });
            aladin.on('objectClicked', function(object, xy) {
              if (object && good(object.ra) && good(object.dec)) {
                lastClick = {ra:object.ra, dec:object.dec};
                copyText(fmt(object.ra, object.dec), 'clicked object RA Dec');
              }
            });
            document.getElementById(id + '_copy_center').onclick = function() {
              let rd = null;
              if (aladin && typeof aladin.getRaDec === 'function') rd = aladin.getRaDec();
              if (rd && rd.length >= 2) copyText(fmt(rd[0], rd[1]), 'center RA Dec');
              else copyText(coordBox.value, 'current displayed RA Dec');
            };
            document.getElementById(id + '_copy_cursor').onclick = function() {
              if (lastCursor) copyText(fmt(lastCursor.ra, lastCursor.dec), 'cursor RA Dec');
              else readout.innerHTML = '<span style="color:#ffb74d">Move over the map first, then press Copy cursor.</span>';
            };
            document.getElementById(id + '_copy_click').onclick = function() {
              if (lastClick) copyText(fmt(lastClick.ra, lastClick.dec), 'clicked RA Dec');
              else readout.innerHTML = '<span style="color:#ffb74d">Click the map first, then press Copy clicked.</span>';
            };
          });
        }
        boot();
      })();
      </script>
    </div>
    """
    return block.replace('__VID__', vid).replace('__TARGET__', target_js).replace('__FOV__', fov_js).replace('__SURVEY__', survey_js)


'''

start = source.index('def viewer_html(target_text, fov_deg, survey_id):')
end = source.index('\ndef dark_box', start)
source = source[:start] + new_viewer + source[end:]
exec(compile(source, 'CMB-0040J_INFRASTRUCTURE.py', 'exec'))
