# CMB-0039T_INFRASTRUCTURE.py
from __future__ import annotations

from pathlib import Path
import re
import runpy
import urllib.request

SRC_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0039S_INFRASTRUCTURE.py'
GENERATED = Path('CMB-0039T_GENERATED_INFRASTRUCTURE.py')

text = urllib.request.urlopen(SRC_URL, timeout=60).read().decode('utf-8')
if text.strip().startswith('404'):
    raise RuntimeError('GitHub returned 404 for CMB-0039S_INFRASTRUCTURE.py')

text = text.replace('CMB-0039S', 'CMB-0039T')
text = text.replace("VERSION = 'CMB-0039S'", "VERSION = 'CMB-0039T'")
text = text.replace("placeholder='RA Dec in one cell'", "placeholder='Paste Aladin RA Dec here, or use the loaded Target value'")
text = text.replace("description='Get coordinates from Aladin'", "description='Use loaded/pasted coordinates'")

replacement = """def get_coordinates_from_aladin(_=None):
    # Stable 39T behavior:
    # The preserved Aladin sky map is a remote iframe, so Colab cannot read its live panned/clicked
    # coordinates directly. This button now always fills the Galaxy Inspector from the single
    # coordinate cell when populated, otherwise from the loaded Target field.
    try:
        source = coord_input.value.strip() or target.value.strip()
        coord = parse_target(source)
        _set_coord_fields(coord)
        coord_status.value = (
            '<b style=\"color:#1b5e20\">Coordinates loaded into Galaxy Inspector.</b> '
            '<span style=\"color:#555\">For a panned/clicked Aladin position, paste the displayed RA Dec '
            'into the single RA Dec cell first, then press this button.</span>'
        )
    except Exception as exc:
        coord_status.value = f'<b style=\"color:#b71c1c\">Coordinate load failed: {html.escape(str(exc))}</b>'

"""

pattern = r"def get_coordinates_from_aladin\(_=None\):\n.*?\ndef refresh_coordinates\(_=None\):"
text, count = re.subn(pattern, replacement + "def refresh_coordinates(_=None):", text, count=1, flags=re.S)
if count != 1:
    raise RuntimeError('Could not patch get_coordinates_from_aladin block in CMB-0039S source.')

GENERATED.write_text(text, encoding='utf-8')
compile(text, str(GENERATED), 'exec')
runpy.run_path(str(GENERATED), run_name='__main__')
