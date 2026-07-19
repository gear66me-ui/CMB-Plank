# CMB-0040O_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from IPython.display import display, HTML

VERSION = 'CMB-0040O'
BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040K_INFRASTRUCTURE.py'

source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace("VERSION = 'CMB-0040K'", "VERSION = 'CMB-0040O'")
source = source.replace('# CMB-0040K_INFRASTRUCTURE.py', '# CMB-0040O_INFRASTRUCTURE.py')
exec(compile(source, 'CMB-0040O_BASE_FROM_0040K.py', 'exec'), globals())


def set_galaxy_field_from_js(coord_text):
    try:
        coord_input.value = str(coord_text).strip()
        set_status('Galaxy Finder populated', f'ICRS field auto-filled from Aladin copy button: <b>{esc(coord_input.value)}</b>', '#4caf50')
    except Exception as exc:
        set_status('Auto-fill failed', str(exc), '#f44336')


def run_galaxy_finder_from_js(coord_text=''):
    try:
        text = str(coord_text).strip()
        if text:
            coord_input.value = text
        set_status('Finding galaxy...', f'Galaxy Finder triggered from joystick for: <b>{esc(coord_input.value)}</b>', '#ffb300')
        find_object(None)
    except Exception as exc:
        set_status('Joystick Find Galaxy failed', str(exc), '#f44336')

bridge_and_button = r'''
<style>
  #cmb40k_findgalaxy {
    width:48px;height:42px;margin:5px 0;background:#1b5e20;color:#e8ffe8;
    border:1px solid #81c784;border-radius:10px;font-size:11px;font-weight:900;line-height:1.05;
    box-shadow:0 0 0 rgba(0,0,0,0);
  }
  #cmb40k_findgalaxy.finding {
    background:#ff9800 !important;color:#111 !important;border-color:#ffe082 !important;
    box-shadow:0 0 14px rgba(255,152,0,.9) !important;
  }
  #cmb40k_findgalaxy.sent {
    background:#1565c0 !important;color:#e3f2fd !important;border-color:#90caf9 !important;
    box-shadow:0 0 12px rgba(33,150,243,.8) !important;
  }
</style>
<script>
(function(){
  function kernelExec(code){
    try {
      if (window.IPython && IPython.notebook && IPython.notebook.kernel) { IPython.notebook.kernel.execute(code); return true; }
      if (window.Jupyter && Jupyter.notebook && Jupyter.notebook.kernel) { Jupyter.notebook.kernel.execute(code); return true; }
    } catch(e) {}
    return false;
  }
  function coord(){
    const box = document.getElementById('cmb41_coord');
    return box ? (box.value || '').trim() : '';
  }
  function setBtnState(btn, state, html){
    if(!btn) return;
    btn.classList.remove('finding','sent');
    if(state) btn.classList.add(state);
    btn.innerHTML = html;
  }
  function sendCoordToPython(){
    const v = coord();
    if(!v) return;
    kernelExec('set_galaxy_field_from_js(' + JSON.stringify(v) + ')');
  }
  function runFindGalaxy(btn){
    const v = coord();
    setBtnState(btn, 'finding', 'FINDING<br>GAL');
    const status = document.getElementById('cmb41_status');
    if(status){
      status.innerHTML = '<b>Galaxy Finder triggered.</b> Searching all enabled survey/catalog stacks' + (v ? ': ' + v : '.') ;
      status.style.borderLeftColor = '#ff9800';
    }
    const ok = kernelExec('run_galaxy_finder_from_js(' + JSON.stringify(v) + ')');
    if(!ok) {
      setBtnState(btn, '', 'FIND<br>GAL');
      if(status) status.innerHTML += '<br><span style="color:#ffb300">Notebook kernel bridge unavailable. Use the lower Find Galaxy button.</span>';
      return;
    }
    setTimeout(function(){ setBtnState(btn, 'sent', 'SEARCH<br>SENT'); }, 1200);
    setTimeout(function(){ setBtnState(btn, '', 'FIND<br>GAL'); }, 9000);
  }
  function wireCopyAutofill(){
    ['cmb41_copy_center','cmb41_copy_cursor','cmb41_copy_click'].forEach(function(id){
      const b = document.getElementById(id);
      if(!b || b.dataset.cmb40oAutofill === '1') return;
      b.dataset.cmb40oAutofill = '1';
      b.addEventListener('click', function(){ setTimeout(sendCoordToPython, 700); });
    });
  }
  function addFindButton(){
    const dock = document.getElementById('cmb40k_scroll_dock');
    const pgdn = document.getElementById('cmb40k_pgdn');
    if(!dock || document.getElementById('cmb40k_findgalaxy')) return;
    const btn = document.createElement('button');
    btn.id = 'cmb40k_findgalaxy';
    btn.title = 'Run Galaxy Finder using copied coordinate';
    btn.innerHTML = 'FIND<br>GAL';
    btn.onclick = function(e){ e.preventDefault(); e.stopPropagation(); runFindGalaxy(btn); };
    dock.insertBefore(btn, pgdn ? pgdn.nextSibling : dock.firstChild);
  }
  function wire(){ wireCopyAutofill(); addFindButton(); }
  wire();
  setTimeout(wire, 600);
  setTimeout(wire, 1400);
  setTimeout(wire, 3000);
})();
</script>
'''

display(HTML(bridge_and_button))
print(VERSION)
