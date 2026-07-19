# CMB-0040P_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from IPython.display import display, HTML

VERSION = 'CMB-0040P'
BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040K_INFRASTRUCTURE.py'

source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace("VERSION = 'CMB-0040K'", "VERSION = 'CMB-0040P'")
source = source.replace('# CMB-0040K_INFRASTRUCTURE.py', '# CMB-0040P_INFRASTRUCTURE.py')
exec(compile(source, 'CMB-0040P_BASE_FROM_0040K.py', 'exec'), globals())


def _cmb40p_set_coord(coord_text=''):
    text = str(coord_text or '').strip()
    if text:
        coord_input.value = text
        set_status('Galaxy Finder populated', f'ICRS field auto-filled from Aladin: <b>{esc(text)}</b>', '#4caf50')
    return text


def _cmb40p_find_galaxy(coord_text=''):
    text = _cmb40p_set_coord(coord_text)
    try:
        set_status('Finding galaxy', f'Search triggered from joystick for: <b>{esc(coord_input.value)}</b>', '#ffb300')
        find_button.button_style = 'warning'
        find_button.description = 'Finding galaxy...'
        find_object(None)
        find_button.button_style = 'success'
        find_button.description = 'Find galaxy / object from ICRS coordinates'
        return 'ok'
    except Exception as exc:
        find_button.button_style = 'danger'
        find_button.description = 'Find failed'
        set_status('Joystick Find Galaxy failed', str(exc), '#f44336')
        return 'failed: ' + str(exc)

try:
    from google.colab import output
    output.register_callback('cmb40p.set_coord', _cmb40p_set_coord)
    output.register_callback('cmb40p.find_galaxy', _cmb40p_find_galaxy)
    COLAB_CALLBACKS_READY = True
except Exception as exc:
    COLAB_CALLBACKS_READY = False
    CALLBACK_ERROR = str(exc)

bridge = r'''
<style>
  #cmb40p_findgalaxy {
    width:48px;height:46px;margin:5px 0;background:#1b5e20;color:#e8ffe8;
    border:1px solid #81c784;border-radius:10px;font-size:11px;font-weight:900;line-height:1.05;
  }
  #cmb40p_find_status {font-size:9px;color:#aaa;margin-top:2px;line-height:1.05;}
</style>
<script>
(function(){
  function statusMsg(msg, color){
    const s = document.getElementById('cmb40p_find_status');
    if(s){ s.textContent = msg; s.style.color = color || '#aaa'; }
    const st = document.getElementById('cmb41_status');
    if(st && msg){ st.innerHTML += '<br><span style="color:' + (color || '#aaa') + '">' + msg + '</span>'; }
  }
  function coord(){
    const box = document.getElementById('cmb41_coord');
    return box ? (box.value || '').trim() : '';
  }
  function colabInvoke(name, args){
    try {
      if(window.google && google.colab && google.colab.kernel && google.colab.kernel.invokeFunction){
        google.colab.kernel.invokeFunction(name, args || [], {});
        return true;
      }
    } catch(e) {}
    return false;
  }
  function sendCoord(){
    const v = coord();
    if(!v) return;
    if(!colabInvoke('cmb40p.set_coord', [v])) statusMsg('Colab callback unavailable for auto-fill.', '#ffb300');
  }
  function runFind(btn){
    const v = coord();
    if(!v){
      btn.style.background = '#7b1fa2';
      btn.innerHTML = 'NO<br>COORD';
      statusMsg('No copied coordinate yet. Press Copy center/cursor/clicked first.', '#ffb300');
      setTimeout(function(){ btn.style.background = '#1b5e20'; btn.innerHTML = 'FIND<br>GAL'; }, 1600);
      return;
    }
    btn.style.background = '#ff9800';
    btn.style.color = '#111';
    btn.innerHTML = 'FINDING<br>GAL';
    statusMsg('Finding galaxy triggered…', '#ffb300');
    if(colabInvoke('cmb40p.find_galaxy', [v])){
      setTimeout(function(){ btn.style.background = '#1565c0'; btn.style.color = '#e3f2fd'; btn.innerHTML = 'SEARCH<br>SENT'; statusMsg('Galaxy search sent to Python.', '#64b5f6'); }, 350);
      setTimeout(function(){ btn.style.background = '#1b5e20'; btn.style.color = '#e8ffe8'; btn.innerHTML = 'FIND<br>GAL'; }, 2600);
    } else {
      btn.style.background = '#b71c1c';
      btn.style.color = '#fff';
      btn.innerHTML = 'CALLBACK<br>FAIL';
      statusMsg('Colab callback unavailable. Use the lower green Find button.', '#ef5350');
    }
  }
  function wireCopyAutofill(){
    ['cmb41_copy_center','cmb41_copy_cursor','cmb41_copy_click'].forEach(function(id){
      const b = document.getElementById(id);
      if(!b || b.dataset.cmb40pAutofill === '1') return;
      b.dataset.cmb40pAutofill = '1';
      b.addEventListener('click', function(){ setTimeout(sendCoord, 750); });
    });
  }
  function addFindButton(){
    const dock = document.getElementById('cmb40k_scroll_dock');
    const pgdn = document.getElementById('cmb40k_pgdn');
    if(!dock || document.getElementById('cmb40p_findgalaxy')) return;
    const btn = document.createElement('button');
    btn.id = 'cmb40p_findgalaxy';
    btn.title = 'Run Galaxy Finder using copied coordinate';
    btn.innerHTML = 'FIND<br>GAL';
    btn.onclick = function(e){ e.preventDefault(); e.stopPropagation(); runFind(btn); };
    const s = document.createElement('div');
    s.id = 'cmb40p_find_status';
    s.textContent = 'ready';
    dock.insertBefore(btn, pgdn ? pgdn.nextSibling : dock.firstChild);
    dock.insertBefore(s, btn.nextSibling);
  }
  function wire(){ wireCopyAutofill(); addFindButton(); }
  wire();
  setTimeout(wire, 600);
  setTimeout(wire, 1400);
  setTimeout(wire, 3000);
})();
</script>
'''

display(HTML(bridge))
if COLAB_CALLBACKS_READY:
    set_status('Joystick ready', 'Colab callback bridge is active. Copy a coordinate, then press FIND GAL on the joystick.', '#4caf50')
else:
    set_status('Joystick callback unavailable', CALLBACK_ERROR, '#f44336')
print(VERSION)
