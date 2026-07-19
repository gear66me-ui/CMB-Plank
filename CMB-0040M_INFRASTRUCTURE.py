# CMB-0040M_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from IPython.display import display, HTML

BASE = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040L_INFRASTRUCTURE.py'
source = urllib.request.urlopen(BASE, timeout=60).read().decode('utf-8')
source = source.replace('# CMB-0040L_INFRASTRUCTURE.py', '# CMB-0040M_INFRASTRUCTURE.py')
source = source.replace("VERSION = 'CMB-0040L'", "VERSION = 'CMB-0040M'")
source = source.replace("CMB-0040L_INFRASTRUCTURE.py", "CMB-0040M_INFRASTRUCTURE.py")
source = source.replace("CMB-0040L", "CMB-0040M")

exec(compile(source, 'CMB-0040M_BASE_FROM_0040L.py', 'exec'), globals())

find_galaxy_dock_button = r'''
<script>
(function(){
  function kernelExec(code){
    try {
      if (window.IPython && IPython.notebook && IPython.notebook.kernel) {
        IPython.notebook.kernel.execute(code);
        return true;
      }
      if (window.Jupyter && Jupyter.notebook && Jupyter.notebook.kernel) {
        Jupyter.notebook.kernel.execute(code);
        return true;
      }
    } catch(e) {}
    return false;
  }

  function installFindGalaxyButton(){
    const dock = document.getElementById('cmb40k_scroll_dock');
    if(!dock || document.getElementById('cmb40m_find_galaxy')) return;

    const btn = document.createElement('button');
    btn.id = 'cmb40m_find_galaxy';
    btn.title = 'Find galaxy from the current copied/selected coordinate';
    btn.textContent = 'Find Galaxy';
    btn.style.cssText = 'width:58px;min-height:38px;margin:6px 0 4px 0;background:#1b5e20;color:#ffffff;border:1px solid #81c784;border-radius:10px;font-size:10px;font-weight:900;line-height:1.05;padding:5px 2px;';

    const label = document.createElement('div');
    label.id = 'cmb40m_find_status';
    label.style.cssText = 'font-size:9px;color:#b9f6ca;line-height:1.05;margin:2px 0 4px 0;';
    label.textContent = 'survey search';

    const hideBtn = document.getElementById('cmb40k_hide');
    if(hideBtn) {
      dock.insertBefore(btn, hideBtn);
      dock.insertBefore(label, hideBtn);
    } else {
      dock.appendChild(btn);
      dock.appendChild(label);
    }

    btn.onclick = function(e){
      e.preventDefault();
      e.stopPropagation();
      const box = document.getElementById('cmb41_coord');
      const val = box ? (box.value || '').trim() : '';
      if(val){
        kernelExec('set_galaxy_field_from_js(' + JSON.stringify(val) + ')');
      }
      const ok = kernelExec('find_object()');
      label.textContent = ok ? 'searching…' : 'kernel unavailable';
      label.style.color = ok ? '#b9f6ca' : '#ffb300';
      setTimeout(function(){ label.textContent = 'survey search'; label.style.color = '#b9f6ca'; }, 3500);
    };
  }

  installFindGalaxyButton();
  setTimeout(installFindGalaxyButton, 800);
  setTimeout(installFindGalaxyButton, 1800);
})();
</script>
'''

display(HTML(find_galaxy_dock_button))
print(VERSION)
