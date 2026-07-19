# CMB-0040A_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from pathlib import Path

VERSION = 'CMB-0040A'
SOURCE_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040_INFRASTRUCTURE.py'
GENERATED = Path('/content/CMB-0040A_GENERATED_INFRASTRUCTURE.py')

with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
    text = response.read().decode('utf-8')

text = text.replace('# CMB-0040_INFRASTRUCTURE.py', '# CMB-0040A_GENERATED_INFRASTRUCTURE.py')
text = text.replace("VERSION = 'CMB-0040'", "VERSION = 'CMB-0040A'")
text = text.replace(
    "all_rows = [r for r in all_rows if np.isfinite(safe_float(r.get('Angular separation (arcsec'))) or np.nan) or r.get('Catalog')]",
    "all_rows = [r for r in all_rows if np.isfinite(safe_float(r.get('Angular separation (arcsec)'))) or r.get('Catalog')]"
)

GENERATED.write_text(text, encoding='utf-8')
print('Loaded CMB-0040A syntax-fixed inclusive survey widget')
exec(compile(text, str(GENERATED), 'exec'))
