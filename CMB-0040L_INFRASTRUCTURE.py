# CMB-0040L_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request

BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040K_INFRASTRUCTURE.py'
source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace("# CMB-0040K_INFRASTRUCTURE.py", "# CMB-0040L_INFRASTRUCTURE.py")
source = source.replace("VERSION = 'CMB-0040K'", "VERSION = 'CMB-0040L'")
source = source.replace("joystick / page scroll dock", "joystick / page scroll dock · auto-fill Galaxy Finder from copied coordinates")

marker = "def find_object(_=None):"
inject = """def set_galaxy_field_from_js(coord_text):
    try:
        coord_input.value = str(coord_text).strip()
        set_status('Galaxy Finder populated', f'ICRS field auto-filled from Aladin copy button: <b>{esc(coord_input.value)}</b>', '#4caf50')
    except Exception as exc:
        set_status('Auto-fill failed', str(exc), '#f44336')


"""
if inject.strip() not in source:
    if marker not in source:
        raise RuntimeError('Could not locate Galaxy Finder function insertion point in 40K.')
    source = source.replace(marker, inject + marker, 1)

# Add a tiny bridge under the coordinate-copy panel. It patches IPython.kernel.execute from JS
# after each copy button writes cmb41_coord. This keeps the working copy widget intact and
# also updates the Python ipywidget field below without manual paste.
bridge = r'''
<script>
(function(){
  function sendToPython(value){
    value = (value || '').trim();
    if(!value) return;
    const code = "set_galaxy_field_from_js(" + JSON.stringify(value) + ")";
    try {
      if (window.google && google.colab && google.colab.kernel && google.colab.kernel.invokeFunction) {
        // Fallback path is intentionally not used unless a Python callback is registered.
      }
      if (window.IPython && IPython.notebook && IPython.notebook.kernel) {
        IPython.notebook.kernel.execute(code);
        return;
      }
      if (window.Jupyter && Jupyter.notebook && Jupyter.notebook.kernel) {
        Jupyter.notebook.kernel.execute(code);
        return;
      }
    } catch(e) {}
    const status = document.getElementById('cmb41_status');
    if(status){ status.innerHTML += '<br><span style="color:#ffb300">Auto-fill bridge unavailable. Coordinate is still selected/copied above.</span>'; }
  }
  function wire(){
    const box = document.getElementById('cmb41_coord');
    const buttons = ['cmb41_copy_center','cmb41_copy_cursor','cmb41_copy_click'];
    buttons.forEach(function(id){
      const b = document.getElementById(id);
      if(!b || b.dataset.autofillWired === '1') return;
      b.dataset.autofillWired = '1';
      b.addEventListener('click', function(){
        setTimeout(function(){ if(box) sendToPython(box.value); }, 650);
      });
    });
  }
  wire();
  setTimeout(wire, 1000);
  setTimeout(wire, 2500);
})();
</script>
'''

# Insert bridge directly after the coordinate-copy panel display, before the rest of 40K executes.
needle = "display(HTML(copy_html))"
if needle in source and "set_galaxy_field_from_js" in source:
    source = source.replace(needle, needle + "\ndisplay(HTML(" + repr(bridge) + "))", 1)
else:
    raise RuntimeError('Could not locate copy panel display hook in 40K.')

exec(compile(source, 'CMB-0040L_INFRASTRUCTURE.py', 'exec'))
