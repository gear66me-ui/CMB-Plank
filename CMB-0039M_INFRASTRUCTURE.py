# CMB-0039M_INFRASTRUCTURE.py
from IPython.display import display, HTML
import urllib.parse

VERSION = 'CMB-0039M'
DEFAULT_TARGET = '03 32 39.99 -27 48 00.0'
DEFAULT_FOV = 0.08
DEFAULT_SURVEY = 'CDS/P/HST/GOODS/color'

aladin_url = 'https://aladin.cds.unistra.fr/AladinLite/?' + urllib.parse.urlencode({
    'target': DEFAULT_TARGET,
    'fov': str(DEFAULT_FOV),
    'survey': DEFAULT_SURVEY,
})

html = f'''
<div style="width:100%;max-width:1500px;margin:0;padding:0;font-family:Arial,sans-serif;">
  <div style="padding:10px 12px;background:#071421;color:#dbeafe;border-radius:8px 8px 0 0;">
    <b style="font-size:20px;">{VERSION} — Aladin Star Viewer</b>
    <span style="margin-left:14px;font-size:13px;opacity:.85;">Native AladinLite map · left survey drawer restored</span>
  </div>
  <iframe id="cmb39m_aladin_iframe" src="{aladin_url}" style="width:100%;height:820px;border:1px solid #607d8b;display:block;background:#000;" allowfullscreen></iframe>
  <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:10px 12px;background:#0f172a;color:#e5e7eb;border-radius:0 0 8px 8px;">
    <button onclick="cmb39m_get_coords()" style="font-size:15px;padding:9px 14px;border-radius:7px;border:1px solid #60a5fa;background:#2563eb;color:white;">Get coordinates from Aladin</button>
    <input id="cmb39m_radec" value="" placeholder="RA Dec will appear here as one copyable cell" style="flex:1;min-width:320px;font-size:15px;padding:9px;border-radius:7px;border:1px solid #475569;background:#020617;color:#f8fafc;" />
    <button onclick="navigator.clipboard.writeText(document.getElementById('cmb39m_radec').value)" style="font-size:15px;padding:9px 14px;border-radius:7px;border:1px solid #94a3b8;background:#334155;color:white;">Copy</button>
    <button onclick="window.open('{aladin_url}', '_blank')" style="font-size:15px;padding:9px 14px;border-radius:7px;border:1px solid #94a3b8;background:#1f2937;color:white;">Open full screen</button>
    <div id="cmb39m_status" style="font-size:12px;color:#cbd5e1;width:100%;">Tip: use the Aladin crosshair / center, then press Get coordinates. If Colab blocks iframe coordinate access, use Open full screen and copy the center coordinate from Aladin.</div>
  </div>
</div>
<script>
function cmb39m_get_coords() {{
  const out = document.getElementById('cmb39m_radec');
  const status = document.getElementById('cmb39m_status');
  try {{
    const frame = document.getElementById('cmb39m_aladin_iframe');
    const w = frame.contentWindow;
    const a = w && (w.aladin || w.A && w.A.aladinInstance || w.aladinInstance);
    if (a && typeof a.getRaDec === 'function') {{
      const xy = a.getRaDec();
      out.value = Number(xy[0]).toFixed(8) + ' ' + Number(xy[1]).toFixed(8);
      status.textContent = 'Coordinates fetched from Aladin center.';
      return;
    }}
  }} catch (e) {{
    status.textContent = 'Browser blocked direct iframe access. Use Open full screen; this is a Colab/browser security limit.';
  }}
  if (!out.value) out.value = 'DIRECT_IFRAME_COORDINATES_BLOCKED_BY_BROWSER';
}}
</script>
'''

display(HTML(html))
