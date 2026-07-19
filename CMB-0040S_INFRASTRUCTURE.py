# CMB-0040R_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from IPython.display import display, HTML

try:
    from google.colab import output as colab_output
except Exception:
    colab_output = None

BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040C_INFRASTRUCTURE.py'
source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace('# CMB-0040C_INFRASTRUCTURE.py', '# CMB-0040R_INFRASTRUCTURE.py')
source = source.replace("VERSION = 'CMB-0040C'", "VERSION = 'CMB-0040R'")
source = source.replace('Original Aladin touch map · drag to pan · pinch or use +/- to zoom · real HiPS survey imagery', 'One Aladin map · one Copy Center button · joystick Find Galaxy captures crosshair center automatically')

new_viewer = r'''def viewer_html(target_text, fov_deg, survey_id):
    import uuid
    vid = 'cmb40r_' + uuid.uuid4().hex[:10]
    target_js = str(target_text).strip().replace('\\', '\\\\').replace("'", "\\'")
    survey_js = str(survey_id).strip().replace('\\', '\\\\').replace("'", "\\'")
    fov_js = str(float(fov_deg))
    block = """
    <div style="width:100%;background:#000;color:#fff;border-radius:8px;overflow:hidden;font-family:Arial,Helvetica,sans-serif;">
      <div style="padding:10px 12px;background:#050505;border-bottom:1px solid #222;display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
        <button id="__VID___copy_center" style="background:#1565c0;color:white;border:0;border-radius:5px;padding:8px 12px;font-weight:800;min-width:140px;">Copy Center</button>
        <input id="__VID___coord" readonly onclick="this.select()" style="flex:1;min-width:260px;background:#000;color:#fff;border:1px solid #666;border-radius:5px;padding:8px;font-family:monospace;" placeholder="Center RA Dec appears here">
        <span id="__VID___readout" style="color:#e0e0e0;font-size:13px;width:100%;">Put the galaxy under the center crosshair. Use Copy Center or FIND GAL on the joystick.</span>
      </div>
      <div id="__VID__" style="width:100%;height:820px;background:#000;"></div>
      <script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
      <script>
      (function() {
        const id = '__VID__';
        const readout = document.getElementById(id + '_readout');
        const coordBox = document.getElementById(id + '_coord');
        let aladin = null;
        function good(v) { return Number.isFinite(Number(v)); }
        function fmt(ra, dec) { return Number(ra).toFixed(8) + ' ' + Number(dec).toFixed(8); }
        function normalizeRaDec(rd) {
          if (!rd) return '';
          if (Array.isArray(rd) && rd.length >= 2 && good(rd[0]) && good(rd[1])) return fmt(rd[0], rd[1]);
          if (good(rd.ra) && good(rd.dec)) return fmt(rd.ra, rd.dec);
          if (good(rd[0]) && good(rd[1])) return fmt(rd[0], rd[1]);
          return '';
        }
        async function copyText(txt, label) {
          if (!txt) { readout.innerHTML = '<span style="color:#ffb74d">No center coordinate yet. Move the map slightly or wait for Aladin to finish loading.</span>'; return ''; }
          coordBox.value = txt; coordBox.focus(); coordBox.select(); window.cmb40r_latest_coord = txt;
          try { await navigator.clipboard.writeText(txt); readout.innerHTML = '<span style="color:#81c784">Copied ' + label + ': <b>' + txt + '</b></span>'; }
          catch(e) { try { document.execCommand('copy'); } catch(err) {} readout.innerHTML = '<span style="color:#ffb74d">Selected ' + label + ': <b>' + txt + '</b>. Clipboard may need long-press copy.</span>'; }
          return txt;
        }
        function centerText() {
          let txt = '';
          try { if (aladin && typeof aladin.getRaDec === 'function') txt = normalizeRaDec(aladin.getRaDec()); } catch(e) {}
          try { if (!txt && aladin && typeof aladin.getCenter === 'function') txt = normalizeRaDec(aladin.getCenter()); } catch(e) {}
          if (!txt) txt = (coordBox.value || '').trim();
          return txt;
        }
        window.cmb40r_capture_center = function(doCopy) {
          const txt = centerText();
          if (txt) { coordBox.value = txt; window.cmb40r_latest_coord = txt; }
          if (doCopy) return copyText(txt, 'center RA Dec');
          return txt;
        };
        function boot() {
          if (!window.A || !A.init) { setTimeout(boot, 250); return; }
          A.init.then(function() {
            aladin = A.aladin('#' + id, {
              target: '__TARGET__', fov: __FOV__, survey: '__SURVEY__',
              showFrame: true, showGotoControl: true, showLayersControl: true,
              expandLayersControl: true, showShareControl: true, showSimbadPointerControl: true,
              showContextMenu: true, showReticle: true,
              reticleColor: 'rgb(178,50,178)', reticleSize: 22
            });
            window.cmb40r_aladin = aladin;
            readout.innerHTML = 'Ready. Center-crosshair mode: put the galaxy under the crosshair, then press FIND GAL on the joystick.';
            setTimeout(function(){ window.cmb40r_capture_center(false); }, 700);
            setTimeout(function(){ window.cmb40r_capture_center(false); }, 1800);
            aladin.on('positionChanged', function(p) {
              const txt = normalizeRaDec(p);
              if (txt) { coordBox.value = txt; window.cmb40r_latest_coord = txt; }
            });
            document.getElementById(id + '_copy_center').onclick = function() { window.cmb40r_capture_center(true); };
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
exec(compile(source, 'CMB-0040R_BASE.py', 'exec'), globals())


def cmb40r_find_galaxy(coord_text):
    coord_input.value = str(coord_text).strip()
    set_status('Finding galaxy', f'Searching all configured surveys/catalogs at: <b>{esc(coord_input.value)}</b>', '#ff9800')
    find_object(None)

if colab_output is not None:
    colab_output.register_callback('cmb40r.findGalaxy', cmb40r_find_galaxy)

scroll_and_find = r'''
<div id="cmb40r_scroll_dock" style="position:fixed;right:14px;bottom:86px;z-index:999999;width:66px;background:#050505;color:#fff;border:1px solid #555;border-radius:14px;box-shadow:0 0 18px rgba(0,0,0,.65);padding:8px 7px;font-family:Arial,Helvetica,sans-serif;text-align:center;">
  <button id="cmb40r_up" style="width:52px;height:42px;margin:2px 0;background:#263238;color:white;border:1px solid #777;border-radius:10px;font-size:24px;font-weight:900;line-height:1;">▲</button>
  <button id="cmb40r_down" style="width:52px;height:42px;margin:4px 0;background:#0d47a1;color:white;border:1px solid #82b1ff;border-radius:10px;font-size:24px;font-weight:900;line-height:1;">▼</button>
  <button id="cmb40r_find" style="width:52px;height:48px;margin:5px 0;background:#1b5e20;color:#e8ffe8;border:1px solid #81c784;border-radius:10px;font-size:11px;font-weight:900;line-height:1.05;">FIND<br>GAL</button>
  <button id="cmb40r_pgdn" style="width:52px;height:30px;margin:2px 0;background:#111;color:#ddd;border:1px solid #555;border-radius:8px;font-size:11px;font-weight:700;">PG↓</button>
  <button id="cmb40r_hide" style="width:52px;height:24px;margin-top:4px;background:#4a0000;color:#ffcdd2;border:1px solid #7f3333;border-radius:8px;font-size:11px;font-weight:700;">hide</button>
  <div style="font-size:10px;color:#aaa;margin-top:4px;line-height:1.1;">page<br>scroll</div>
</div>
<script>
(function(){
  const dock = document.getElementById('cmb40r_scroll_dock');
  const findBtn = document.getElementById('cmb40r_find');
  function scrollByPixels(px){ window.scrollBy({top:px, left:0, behavior:'smooth'}); }
  document.getElementById('cmb40r_up').onclick = function(e){ e.preventDefault(); e.stopPropagation(); scrollByPixels(-360); };
  document.getElementById('cmb40r_down').onclick = function(e){ e.preventDefault(); e.stopPropagation(); scrollByPixels(360); };
  document.getElementById('cmb40r_pgdn').onclick = function(e){ e.preventDefault(); e.stopPropagation(); scrollByPixels(Math.max(520, Math.floor(window.innerHeight*0.78))); };
  document.getElementById('cmb40r_hide').onclick = function(e){ e.preventDefault(); e.stopPropagation(); dock.style.display='none'; };
  function setButton(text, bg, color){ findBtn.innerHTML = text; findBtn.style.background = bg; findBtn.style.color = color || '#fff'; }
  function status(msg, color){ const ro = document.querySelector('[id^="cmb40r_"][id$="_readout"]'); if(ro){ ro.innerHTML = msg; ro.style.color = color || '#e0e0e0'; } }
  function invokeFind(v){ try { if(window.google && google.colab && google.colab.kernel && google.colab.kernel.invokeFunction){ google.colab.kernel.invokeFunction('cmb40r.findGalaxy', [v], {}); return true; } } catch(e) {} return false; }
  findBtn.onclick = function(e){
    e.preventDefault(); e.stopPropagation();
    setButton('CAPTURE<br>CTR', '#ff9800', '#111');
    status('<b>Capturing center crosshair coordinate…</b>', '#ffb74d');
    let v = '';
    try { if(window.cmb40r_capture_center) v = window.cmb40r_capture_center(false) || ''; } catch(err) {}
    if(!v) v = (window.cmb40r_latest_coord || '').trim();
    const box = document.querySelector('[id^="cmb40r_"][id$="_coord"]');
    if(!v && box) v = (box.value || '').trim();
    if(!v){ setButton('NO<br>COORD', '#6a1b9a', '#fff'); status('<b>No coordinate captured.</b> Wait for Aladin to finish loading or nudge the map slightly, then press FIND GAL again.', '#ce93d8'); setTimeout(function(){ setButton('FIND<br>GAL', '#1b5e20', '#e8ffe8'); }, 2500); return false; }
    if(box) box.value = v;
    setButton('FINDING<br>GAL', '#ff9800', '#111');
    status('<b>Center captured:</b> ' + v + '<br>Starting Galaxy Finder…', '#81c784');
    const ok = invokeFind(v);
    setButton(ok ? 'SEARCH<br>SENT' : 'BRIDGE<br>FAIL', ok ? '#1565c0' : '#b71c1c', '#fff');
    if(!ok) status('<b>Colab callback bridge unavailable.</b> Coordinate is in the field above; use the lower Find Galaxy button.', '#ef9a9a');
    setTimeout(function(){ setButton('FIND<br>GAL', '#1b5e20', '#e8ffe8'); }, 3500);
    return false;
  };
})();
</script>
'''

display(HTML(scroll_and_find))
print('CMB-0040R')
