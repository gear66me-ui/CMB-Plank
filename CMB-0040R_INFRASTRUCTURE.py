# CMB-0040R_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from IPython.display import display, HTML

VERSION = 'CMB-0040R'
BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040Q_INFRASTRUCTURE.py'

source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace("VERSION = 'CMB-0040Q'", "VERSION = 'CMB-0040R'")
source = source.replace('# CMB-0040Q_INFRASTRUCTURE.py', '# CMB-0040R_INFRASTRUCTURE.py')
exec(compile(source, 'CMB-0040R_BASE_FROM_0040Q.py', 'exec'), globals())

icrs_clean_js = r'''
<style>
  #cmb41_coord {
    border:2px solid #4caf50 !important;
    box-shadow:0 0 10px rgba(76,175,80,.35) !important;
  }
  #cmb40k_findgalaxy {
    width:58px !important;
    height:52px !important;
  }
</style>
<script>
(function(){
  function setStatus(html, color){
    const s = document.getElementById('cmb41_status');
    if(s){ s.innerHTML = html; s.style.borderLeftColor = color || '#4caf50'; }
  }
  function wire(){
    const center = document.getElementById('cmb41_copy_center');
    if(center){
      center.innerHTML = 'Copy ICRS Center';
      center.title = 'Copy center crosshair ICRS / equatorial RA Dec';
    }
    const coord = document.getElementById('cmb41_coord');
    if(coord){
      coord.placeholder = 'ICRS / Equatorial RA Dec from center crosshair';
      coord.title = 'ICRS / Equatorial RA Dec used by Galaxy Finder';
    }
    const findBtn = document.getElementById('cmb40k_findgalaxy');
    if(findBtn){
      findBtn.title = 'Use center crosshair ICRS RA Dec and run Galaxy Finder';
    }
    const status = document.getElementById('cmb41_status');
    if(status && status.dataset.cmb40rDone !== '1'){
      status.dataset.cmb40rDone = '1';
      setStatus('ICRS / Equatorial center mode. Put the galaxy under the crosshair, then press <b>FIND GAL</b>. The widget captures the center RA-Dec and searches the catalogs/surveys automatically.', '#4caf50');
    }
  }
  wire();
  setTimeout(wire, 700);
  setTimeout(wire, 1800);
  setTimeout(wire, 3500);
})();
</script>
'''

display(HTML(icrs_clean_js))
print(VERSION)
