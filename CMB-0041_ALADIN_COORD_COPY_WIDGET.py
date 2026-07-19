# CMB-0041_ALADIN_COORD_COPY_WIDGET.py
from IPython.display import display, HTML

VERSION = 'CMB-0041'
DEFAULT_TARGET = '03 32 39.16 -27 48 44.7'
DEFAULT_FOV = 0.08
DEFAULT_SURVEY = 'CDS/P/HST/EPO'

html = f'''
<div style="background:#050505;color:#f2f2f2;border-radius:10px;padding:12px;font-family:Arial,Helvetica,sans-serif">
  <div style="font-size:22px;font-weight:700;margin-bottom:6px">ALADIN COORDINATE COPY WIDGET — {VERSION}</div>
  <div style="font-size:13px;color:#cfcfcf;margin-bottom:10px">
    Same-page Aladin Lite API view. Use the buttons below to copy one-cell ICRS coordinates: <b>RA Dec</b>.
    Right-click inside the sky map for Aladin's native context menu, including copy clicked position.
  </div>

  <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px">
    <label>Target&nbsp;<input id="cmb41_target" value="{DEFAULT_TARGET}" style="width:260px;background:#111;color:white;border:1px solid #555;border-radius:5px;padding:6px"></label>
    <label>FOV&nbsp;<input id="cmb41_fov" value="{DEFAULT_FOV}" style="width:70px;background:#111;color:white;border:1px solid #555;border-radius:5px;padding:6px"></label>
    <select id="cmb41_survey" style="background:#111;color:white;border:1px solid #555;border-radius:5px;padding:6px">
      <option value="P/DSS2/color">DSS2 color</option>
      <option value="P/DSS2/blue">DSS2 blue</option>
      <option value="P/2MASS/color">2MASS color infrared</option>
      <option value="P/allWISE/color">WISE color infrared</option>
      <option value="P/GALEXGR6/AIS/color">GALEX GR6/7 ultraviolet</option>
      <option value="CDS/P/HST/EPO" selected>Hubble Outreach color</option>
      <option value="CDS/P/HST/GOODS/color">Hubble GOODS color</option>
      <option value="CDS/P/HST/GOODS/i">Hubble GOODS i-band</option>
      <option value="CDS/P/JWST/F150W">JWST F150W</option>
      <option value="CDS/P/JWST/F444W">JWST F444W</option>
      <option value="CDS/P/JWST/F480M">JWST F480M</option>
    </select>
    <button id="cmb41_load" style="background:#0d47a1;color:white;border:0;border-radius:6px;padding:7px 11px;font-weight:700">Load map</button>
    <button id="cmb41_copy_center" style="background:#1b5e20;color:white;border:0;border-radius:6px;padding:7px 11px;font-weight:700">Copy center RA Dec</button>
    <button id="cmb41_copy_cursor" style="background:#4a148c;color:white;border:0;border-radius:6px;padding:7px 11px;font-weight:700">Copy cursor RA Dec</button>
    <button id="cmb41_copy_click" style="background:#263238;color:white;border:0;border-radius:6px;padding:7px 11px;font-weight:700">Copy clicked RA Dec</button>
  </div>

  <div id="cmb41_status" style="background:#000;border-left:5px solid #2196f3;border-radius:7px;padding:10px;margin:8px 0;color:white">
    Loading Aladin Lite…
  </div>

  <input id="cmb41_coord" value="" readonly
    style="width:100%;box-sizing:border-box;background:#000;color:#ffffff;border:1px solid #777;border-radius:7px;padding:9px;font-size:16px;font-family:monospace;margin-bottom:10px"
    onclick="this.select()">

  <div id="cmb41_aladin" style="width:100%;height:780px;background:#000;border:1px solid #333;border-radius:8px"></div>
</div>

<script src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
<script>
(function() {{
  let aladin = null;
  let lastCursor = null;
  let lastClick = null;
  const status = document.getElementById('cmb41_status');
  const coordBox = document.getElementById('cmb41_coord');
  const targetBox = document.getElementById('cmb41_target');
  const fovBox = document.getElementById('cmb41_fov');
  const surveyBox = document.getElementById('cmb41_survey');

  function fmt(ra, dec) {{
    return Number(ra).toFixed(8) + ' ' + Number(dec).toFixed(8);
  }}

  async function copyText(text, label) {{
    coordBox.value = text;
    coordBox.focus();
    coordBox.select();
    try {{
      await navigator.clipboard.writeText(text);
      status.innerHTML = '<b>' + label + ' copied:</b> ' + text;
      status.style.borderLeftColor = '#4caf50';
    }} catch(e) {{
      document.execCommand('copy');
      status.innerHTML = '<b>' + label + ' selected:</b> ' + text + '<br>Clipboard may require manual Ctrl+C / long-press copy on this device.';
      status.style.borderLeftColor = '#ffb300';
    }}
  }}

  function loadMap() {{
    const target = targetBox.value || '{DEFAULT_TARGET}';
    const fov = parseFloat(fovBox.value || '{DEFAULT_FOV}');
    const survey = surveyBox.value || '{DEFAULT_SURVEY}';
    document.getElementById('cmb41_aladin').innerHTML = '';
    A.init.then(() => {{
      aladin = A.aladin('#cmb41_aladin', {{
        target: target,
        fov: fov,
        survey: survey,
        showFrame: true,
        showGotoControl: true,
        showLayersControl: true,
        expandLayersControl: true,
        showShareControl: true,
        showSimbadPointerControl: true,
        showContextMenu: true,
        reticleColor: 'rgb(178,50,178)',
        reticleSize: 22
      }});

      status.innerHTML = 'Ready. Pan/zoom the map, then press <b>Copy center RA Dec</b>. Move cursor or click in the map for cursor/click coordinates. Right-click the map for Aladin native copy menu.';
      status.style.borderLeftColor = '#2196f3';

      aladin.on('positionChanged', function(p) {{
        if (p && Number.isFinite(p.ra) && Number.isFinite(p.dec)) {{
          coordBox.value = fmt(p.ra, p.dec);
        }}
      }});

      aladin.on('mouseMove', function(p) {{
        if (p && Number.isFinite(p.ra) && Number.isFinite(p.dec)) {{
          lastCursor = {{ra:p.ra, dec:p.dec}};
        }}
      }});

      aladin.on('objectClicked', function(object, xy) {{
        if (object && Number.isFinite(object.ra) && Number.isFinite(object.dec)) {{
          lastClick = {{ra:object.ra, dec:object.dec}};
          copyText(fmt(object.ra, object.dec), 'Clicked object RA Dec');
        }} else if (xy && aladin && typeof aladin.pix2world === 'function') {{
          const w = aladin.pix2world(xy.x, xy.y);
          if (w && Number.isFinite(w[0]) && Number.isFinite(w[1])) {{
            lastClick = {{ra:w[0], dec:w[1]}};
            copyText(fmt(w[0], w[1]), 'Clicked position RA Dec');
          }}
        }}
      }});
    }});
  }}

  document.getElementById('cmb41_load').onclick = loadMap;
  document.getElementById('cmb41_copy_center').onclick = function() {{
    if (!aladin) {{ status.innerHTML = 'Aladin not ready yet.'; return; }}
    let rd = null;
    if (typeof aladin.getRaDec === 'function') rd = aladin.getRaDec();
    if (!rd && typeof aladin.getCenter === 'function') rd = aladin.getCenter();
    if (rd && Number.isFinite(rd[0]) && Number.isFinite(rd[1])) copyText(fmt(rd[0], rd[1]), 'Center RA Dec');
    else copyText(coordBox.value || targetBox.value, 'Current displayed RA Dec');
  }};
  document.getElementById('cmb41_copy_cursor').onclick = function() {{
    if (lastCursor) copyText(fmt(lastCursor.ra, lastCursor.dec), 'Cursor RA Dec');
    else status.innerHTML = 'Move your cursor/finger over the map first, then press Copy cursor.';
  }};
  document.getElementById('cmb41_copy_click').onclick = function() {{
    if (lastClick) copyText(fmt(lastClick.ra, lastClick.dec), 'Clicked RA Dec');
    else status.innerHTML = 'Click inside the map first. If click capture is blocked on tablet, use Copy center or right-click/long-press Aladin context menu.';
  }};

  loadMap();
}})();
</script>
'''

display(HTML(html))
print(VERSION)
