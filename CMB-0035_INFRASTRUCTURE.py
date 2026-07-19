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
text = text.replace('else "none"', 'else "classic-output"')
text = text.replace('VIEWER["enabled"] = IPYALADIN_AVAILABLE', 'VIEWER["enabled"] = True')
text = text.replace('    print("Classic matplotlib viewer placeholder.")', '    print("CMB-0035 classic fallback viewer active.")')

GENERATED.write_text(text, encoding='utf-8')
compile(text, str(GENERATED), 'exec')
print('Generated:', GENERATED)
print('Running generated CMB-0035 infrastructure...')
print('=' * 70)
runpy.run_path(str(GENERATED), run_name='__main__')
