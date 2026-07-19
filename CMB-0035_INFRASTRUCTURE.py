# CMB-0035_INFRASTRUCTURE.py
from pathlib import Path
import urllib.request
import runpy

SRC_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0034_INFRASTRUCTURE.py'
GENERATED = Path('CMB-0035_GENERATED_INFRASTRUCTURE.py')

print('CMB-0035 launcher-patcher')
print('Fetching committed CMB-0034 from GitHub...')
text = urllib.request.urlopen(SRC_URL, timeout=60).read().decode('utf-8')
if text.strip().startswith('404'):
    raise RuntimeError('GitHub returned 404 for CMB-0034_INFRASTRUCTURE.py')

text = text.replace('CMB-0034', 'CMB-0035')
text = text.replace('34A-1', '35A-1')
text = text.replace('else "none"', 'else "classic-html"')
text = text.replace('VIEWER["enabled"] = IPYALADIN_AVAILABLE', 'VIEWER["enabled"] = True')
text = text.replace(
    '    print("Classic matplotlib viewer placeholder.")',
    '    display(HTML("<div style=\'height:680px;border:1px solid #888;background:#050505;color:white;font-family:Arial;padding:18px;box-sizing:border-box\'><h2>CMB-0035 Classic Viewer</h2><p>Fallback viewer active because ipyaladin is not installed.</p><div style=\'height:520px;border:1px solid #555;background:radial-gradient(ellipse at center,#eee 0%,#777 13%,#222 45%,#000 100%);position:relative\'><div style=\'position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);color:#ffeb3b;font-size:44px;font-weight:bold\'>+</div></div><p>Viewer panel rendered successfully.</p></div>"))'
)

GENERATED.write_text(text, encoding='utf-8')
compile(text, str(GENERATED), 'exec')
print('Generated:', GENERATED)
print('Running generated CMB-0035 infrastructure...')
print('=' * 70)
runpy.run_path(str(GENERATED), run_name='__main__')
