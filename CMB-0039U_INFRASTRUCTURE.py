# CMB-0039U_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request
from pathlib import Path
import runpy

SRC_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0039P_INFRASTRUCTURE.py'
GENERATED = Path('CMB-0039U_GENERATED_INFRASTRUCTURE.py')

source = urllib.request.urlopen(SRC_URL, timeout=60).read().decode('utf-8')
if source.strip().startswith('404'):
    raise RuntimeError('GitHub returned 404 for CMB-0039P_INFRASTRUCTURE.py')

text = source.replace('CMB-0039P', 'CMB-0039U')

old_button = "get_aladin_button = widgets.Button(description='Get coordinates from Aladin', button_style='info', icon='crosshairs')"
new_button = "get_aladin_button = widgets.Button(description='Use target / pasted coordinates', button_style='info', icon='crosshairs')"
text = text.replace(old_button, new_button)

old_func = """def get_coordinates_from_aladin(_=None):
    # The Colab iframe is cross-origin, so Python cannot read a panned Aladin center directly.
    # This restores the requested button and loads the current Aladin target/center into the single inspector cell.
    try:
        coord = parse_target(target.value)
        _set_coord_fields(coord)
        coord_status.value = '<b style=\"color:#1565c0\">Coordinates loaded from current Aladin target into the single RA Dec cell.</b>'
    except Exception as exc:
        coord_status.value = f'<b style=\"color:#b71c1c\">Coordinate fetch failed: {html.escape(str(exc))}</b>'
"""
new_func = """def get_coordinates_from_aladin(_=None):
    # Stable mode: keep the full Aladin iframe UI intact.
    # Colab cannot read live pan/click coordinates from the remote Aladin iframe.
    # This button therefore uses the single pasted RA/Dec field when present,
    # otherwise it uses the currently loaded Target field.
    try:
        source = coord_input.value.strip() or target.value.strip()
        coord = parse_target(source)
        _set_coord_fields(coord)
        coord_status.value = '<b style=\"color:#1565c0\">Inspector coordinates loaded from the single RA Dec field / current Target.</b>'
    except Exception as exc:
        coord_status.value = f'<b style=\"color:#b71c1c\">Coordinate load failed: {html.escape(str(exc))}</b>'
"""
if old_func not in text:
    raise RuntimeError('Expected CMB-0039P coordinate function was not found; source changed.')
text = text.replace(old_func, new_func, 1)

old_placeholder = "placeholder='RA Dec in one cell'"
new_placeholder = "placeholder='Paste Aladin RA Dec here, or leave blank to use Target'"
text = text.replace(old_placeholder, new_placeholder)

GENERATED.write_text(text, encoding='utf-8')
compile(text, str(GENERATED), 'exec')
runpy.run_path(str(GENERATED), run_name='__main__')
