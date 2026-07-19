# CMB-0039H_INFRASTRUCTURE.py
from pathlib import Path
import contextlib
import io
import runpy
import sys
import traceback
import urllib.request

SRC_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0034_INFRASTRUCTURE.py'
GENERATED = Path('CMB-0039H_GENERATED_INFRASTRUCTURE.py')

try:
    text = urllib.request.urlopen(SRC_URL, timeout=60).read().decode('utf-8')
    if text.strip().startswith('404'):
        raise RuntimeError('GitHub returned 404 for CMB-0034_INFRASTRUCTURE.py')

    text = text.replace('CMB-0034', 'CMB-0039H')
    text = text.replace('34A-1', '39H-1')
    text = text.replace('else "none"', 'else "classic-html"')
    text = text.replace('VIEWER["enabled"] = IPYALADIN_AVAILABLE', 'VIEWER["enabled"] = True')
    text = text.replace('VIEWER["native"] = aladin', 'VIEWER["native"] = aladin if IPYALADIN_AVAILABLE else None')
    text = text.replace('value=IPYALADIN_AVAILABLE,\n\n    description="Use Native ipyaladin",', 'value=False,\n\n    description="Use Native ipyaladin",')

    old = '    print("Classic matplotlib viewer placeholder.")'
    new = '''    clear_output(wait=True)
    display(HTML("""
    <div style='border:1px solid #9e9e9e;border-radius:10px;padding:18px;background:#050816;color:#e5e7eb;font-family:Arial,sans-serif;'>
      <h3 style='margin:0 0 8px 0;color:#93c5fd;'>CMB-0039H Star Viewer</h3>
      <div style='font-size:14px;line-height:1.45;'>
        <b>Fallback viewer active.</b><br>
        ipyaladin is not installed, so native sky rendering is disabled.<br>
        Console startup output is suppressed. Widget display only.
      </div>
      <div style='margin-top:12px;padding:10px;background:#111827;border-radius:8px;'>
        Target: <b>M31</b> &nbsp; | &nbsp; Engine: <b>classic-html</b> &nbsp; | &nbsp; Native Viewer: <b>False</b>
      </div>
    </div>
    """))
    STAT["viewer_updates"] += 1'''
    if old not in text:
        raise RuntimeError('Classic viewer placeholder line not found in CMB-0034 source.')
    text = text.replace(old, new, 1)

    text = text.replace('print("Native Viewer    :", VIEWER["enabled"])', 'print("Native Viewer    :", IPYALADIN_AVAILABLE and VIEWER["native"] is not None)')

    GENERATED.write_text(text, encoding='utf-8')
    compile(text, str(GENERATED), 'exec')

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        runpy.run_path(str(GENERATED), run_name='__main__')

except Exception:
    print('CMB-0039H failed:')
    traceback.print_exc(file=sys.stdout)
