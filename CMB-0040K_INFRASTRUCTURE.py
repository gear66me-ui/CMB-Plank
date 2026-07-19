# CMB-0040K_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from IPython.display import display, HTML

VERSION = 'CMB-0040K'
BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040J_INFRASTRUCTURE.py'

source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace("VERSION = 'CMB-0040J'", "VERSION = 'CMB-0040K'")
source = source.replace('# CMB-0040J_INFRASTRUCTURE.py', '# CMB-0040K_INFRASTRUCTURE.py')

exec(compile(source, 'CMB-0040K_BASE_FROM_0040J.py', 'exec'), globals())

scroll_dock = r'''
<div id="cmb40k_scroll_dock" style="
  position:fixed;
  right:14px;
  bottom:86px;
  z-index:999999;
  width:62px;
  background:#050505;
  color:#fff;
  border:1px solid #555;
  border-radius:14px;
  box-shadow:0 0 18px rgba(0,0,0,.65);
  padding:8px 7px;
  font-family:Arial,Helvetica,sans-serif;
  text-align:center;">
  <button id="cmb40k_up" title="Scroll up" style="width:48px;height:44px;margin:2px 0;background:#263238;color:white;border:1px solid #777;border-radius:10px;font-size:24px;font-weight:900;line-height:1;">▲</button>
  <button id="cmb40k_down" title="Scroll down" style="width:48px;height:44px;margin:4px 0;background:#0d47a1;color:white;border:1px solid #82b1ff;border-radius:10px;font-size:24px;font-weight:900;line-height:1;">▼</button>
  <button id="cmb40k_pgup" title="Page up" style="width:48px;height:30px;margin:4px 0;background:#111;color:#ddd;border:1px solid #555;border-radius:8px;font-size:11px;font-weight:700;">PG↑</button>
  <button id="cmb40k_pgdn" title="Page down" style="width:48px;height:30px;margin:2px 0;background:#111;color:#ddd;border:1px solid #555;border-radius:8px;font-size:11px;font-weight:700;">PG↓</button>
  <button id="cmb40k_hide" title="Hide scroll dock" style="width:48px;height:24px;margin-top:4px;background:#4a0000;color:#ffcdd2;border:1px solid #7f3333;border-radius:8px;font-size:11px;font-weight:700;">hide</button>
  <div style="font-size:10px;color:#aaa;margin-top:4px;line-height:1.1;">page<br>scroll</div>
</div>
<script>
(function(){
  const dock = document.getElementById('cmb40k_scroll_dock');
  function scrollByPixels(px){ window.scrollBy({top:px, left:0, behavior:'smooth'}); }
  document.getElementById('cmb40k_up').onclick = function(e){ e.preventDefault(); e.stopPropagation(); scrollByPixels(-360); };
  document.getElementById('cmb40k_down').onclick = function(e){ e.preventDefault(); e.stopPropagation(); scrollByPixels(360); };
  document.getElementById('cmb40k_pgup').onclick = function(e){ e.preventDefault(); e.stopPropagation(); scrollByPixels(-Math.max(520, Math.floor(window.innerHeight*0.78))); };
  document.getElementById('cmb40k_pgdn').onclick = function(e){ e.preventDefault(); e.stopPropagation(); scrollByPixels(Math.max(520, Math.floor(window.innerHeight*0.78))); };
  document.getElementById('cmb40k_hide').onclick = function(e){ e.preventDefault(); e.stopPropagation(); dock.style.display='none'; };
})();
</script>
'''

display(HTML(scroll_dock))
print(VERSION)
