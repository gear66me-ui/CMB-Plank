# CMB-0040Q_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from IPython.display import display, HTML

VERSION = 'CMB-0040Q'
BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040P_INFRASTRUCTURE.py'

source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace("VERSION = 'CMB-0040P'", "VERSION = 'CMB-0040Q'")
source = source.replace('# CMB-0040P_INFRASTRUCTURE.py', '# CMB-0040Q_INFRASTRUCTURE.py')
exec(compile(source, 'CMB-0040Q_BASE_FROM_0040P.py', 'exec'), globals())

# Simplify coordinate workflow: use the center crosshair only.
# The FIND GAL joystick button first triggers Copy Center, then runs the Python search.
center_only_js = r'''
<style>
  #cmb41_copy_cursor, #cmb41_copy_click { display:none !important; }
  #cmb41_copy_center {
    background:#0d47a1 !important;
    color:#ffffff !important;
    min-width:132px !important;
  }
  #cmb40k_findgalaxy {
    width:54px !important;
    height:48px !important;
    background:#1b5e20 !important;
    color:#e8ffe8 !important;
    border:1px solid #81c784 !important;
    border-radius:11px !important;
    font-size:11px !important;
    font-weight:900 !important;
    line-height:1.05 !important;
  }
</style>
<script>
(function(){
  function setStatus(html, color){
    const s = document.getElementById('cmb41_status');
    if(s){ s.innerHTML = html; s.style.borderLeftColor = color || '#2196f3'; }
  }
  function getCoord(){
    const box = document.getElementById('cmb41_coord');
    return box ? (box.value || '').trim() : '';
  }
  function callPythonFind(v){
    try {
      if(window.google && google.colab && google.colab.kernel && google.colab.kernel.invokeFunction){
        google.colab.kernel.invokeFunction('cmb40p.findGalaxy', [v || ''], {});
        return true;
      }
    } catch(e) {}
    try {
      if(window.IPython && IPython.notebook && IPython.notebook.kernel){
        IPython.notebook.kernel.execute('run_galaxy_finder_from_js(' + JSON.stringify(v || '') + ')');
        return true;
      }
      if(window.Jupyter && Jupyter.notebook && Jupyter.notebook.kernel){
        Jupyter.notebook.kernel.execute('run_galaxy_finder_from_js(' + JSON.stringify(v || '') + ')');
        return true;
      }
    } catch(e) {}
    return false;
  }
  function triggerCenterAndFind(){
    const findBtn = document.getElementById('cmb40k_findgalaxy');
    const copyBtn = document.getElementById('cmb41_copy_center');
    if(findBtn){
      findBtn.innerHTML = 'FINDING<br>GAL';
      findBtn.style.background = '#ff9800';
      findBtn.style.color = '#111';
    }
    setStatus('<b>Capturing center crosshair coordinate…</b><br>Galaxy Finder will start automatically.', '#ff9800');
    if(copyBtn) copyBtn.click();
    setTimeout(function(){
      const v = getCoord();
      if(!v){
        setStatus('<b>No center coordinate yet.</b><br>Move the map slightly or press Copy Center once, then try FIND GAL again.', '#f44336');
        if(findBtn){ findBtn.innerHTML = 'FIND<br>GAL'; findBtn.style.background = '#1b5e20'; findBtn.style.color = '#e8ffe8'; }
        return;
      }
      setStatus('<b>Center captured:</b> ' + v + '<br>Starting Galaxy Finder…', '#4caf50');
      const ok = callPythonFind(v);
      if(findBtn){
        findBtn.innerHTML = ok ? 'SEARCH<br>SENT' : 'BRIDGE<br>FAIL';
        findBtn.style.background = ok ? '#1565c0' : '#b71c1c';
        findBtn.style.color = '#fff';
        setTimeout(function(){ findBtn.innerHTML = 'FIND<br>GAL'; findBtn.style.background = '#1b5e20'; findBtn.style.color = '#e8ffe8'; }, 3500);
      }
      if(!ok) setStatus('<b>Bridge unavailable.</b><br>The center coordinate is copied/selected above; use the lower Find Galaxy button.', '#f44336');
    }, 900);
  }
  function wire(){
    const center = document.getElementById('cmb41_copy_center');
    if(center){ center.innerHTML = 'Copy Center'; center.title = 'Copy center crosshair RA Dec'; }
    const findBtn = document.getElementById('cmb40k_findgalaxy');
    if(findBtn && findBtn.dataset.cmb40qCenterFind !== '1'){
      findBtn.dataset.cmb40qCenterFind = '1';
      findBtn.onclick = function(e){ e.preventDefault(); e.stopPropagation(); triggerCenterAndFind(); return false; };
      findBtn.innerHTML = 'FIND<br>GAL';
      findBtn.title = 'Copy center crosshair coordinate and run Galaxy Finder';
    }
    const status = document.getElementById('cmb41_status');
    if(status && !status.dataset.cmb40qText){
      status.dataset.cmb40qText = '1';
      status.innerHTML = 'Center-crosshair mode. Put the galaxy under the crosshair, then press <b>FIND GAL</b> on the joystick. It copies the center coordinate and starts Galaxy Finder automatically.';
      status.style.borderLeftColor = '#4caf50';
    }
  }
  wire();
  setTimeout(wire, 600);
  setTimeout(wire, 1600);
  setTimeout(wire, 3200);
})();
</script>
'''

display(HTML(center_only_js))
print(VERSION)
