# CMB-0039V_INFRASTRUCTURE.py
from __future__ import annotations

from pathlib import Path
import urllib.request
import runpy

SRC_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0039P_INFRASTRUCTURE.py'
GENERATED = Path('CMB-0039V_GENERATED_INFRASTRUCTURE.py')

text = urllib.request.urlopen(SRC_URL, timeout=60).read().decode('utf-8')
if text.strip().startswith('404'):
    raise RuntimeError('GitHub returned 404 for CMB-0039P_INFRASTRUCTURE.py')

# Version bump only; preserve the working Aladin iframe interface.
text = text.replace('CMB-0039P', 'CMB-0039V')
text = text.replace("# CMB-0039P_INFRASTRUCTURE.py", "# CMB-0039V_GENERATED_INFRASTRUCTURE.py")

# User-requested default: Hubble Outreach color, not Hubble GOODS color.
text = text.replace("value='CDS/P/HST/GOODS/color', description='Survey:'", "value='CDS/P/HST/EPO', description='Survey:'")
text = text.replace("viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, survey.value, 'Hubble GOODS color'))", "viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, survey.value, 'Hubble Outreach color'))")

# Make the bottom coordinate workflow honest and reliable. The iframe cannot expose live pan/click
# coordinates to Python because it is cross-origin, so this button now uses the single RA Dec
# inspector field when present, otherwise the loaded target. This keeps the Aladin UI intact.
text = text.replace("get_aladin_button = widgets.Button(description='Get coordinates from Aladin', button_style='info', icon='crosshairs')", "get_aladin_button = widgets.Button(description='Use RA Dec / target', button_style='info', icon='crosshairs')")
text = text.replace("placeholder='RA Dec in one cell'", "placeholder='Paste Aladin RA Dec here, or leave blank to use Target'")

old_block = """def get_coordinates_from_aladin(_=None):\n    # The Colab iframe is cross-origin, so Python cannot read a panned Aladin center directly.\n    # This restores the requested button and loads the current Aladin target/center into the single inspector cell.\n    try:\n        coord = parse_target(target.value)\n        _set_coord_fields(coord)\n        coord_status.value = '<b style=\"color:#1565c0\">Coordinates loaded from current Aladin target into the single RA Dec cell.</b>'\n    except Exception as exc:\n        coord_status.value = f'<b style=\"color:#b71c1c\">Coordinate fetch failed: {html.escape(str(exc))}</b>'\n"""
new_block = """def get_coordinates_from_aladin(_=None):\n    # The preserved Aladin viewer is a remote iframe. Browser security blocks Python from\n    # reading its live pan/click center directly, so this uses the single RA Dec field if the\n    # user pasted coordinates from Aladin; otherwise it uses the currently loaded Target.\n    try:\n        source = coord_input.value.strip() or target.value.strip()\n        coord = parse_target(source)\n        _set_coord_fields(coord)\n        coord_status.value = (\n            '<b style=\"color:#1565c0\">Coordinate cell loaded.</b> '\n            '<span style=\"color:#555\">Using pasted RA Dec if present; otherwise using the loaded Target. '</n            'The embedded Aladin iframe cannot expose live pan coordinates to Colab Python.</span>'\n        )\n    except Exception as exc:\n        coord_status.value = f'<b style=\"color:#b71c1c\">Coordinate load failed: {html.escape(str(exc))}</b>'\n"""
if old_block not in text:
    # Fallback line-by-line minimal behavior if the old exact block changes.
    text = text.replace("coord = parse_target(target.value)", "source = coord_input.value.strip() or target.value.strip()\n        coord = parse_target(source)", 1)
    text = text.replace("Coordinates loaded from current Aladin target into the single RA Dec cell.", "Coordinate cell loaded from pasted RA Dec if present; otherwise from the loaded Target.")
else:
    text = text.replace(old_block, new_block, 1)

# Fix accidental typo introduced in string literal construction if present.
text = text.replace("'</n            '", "")

GENERATED.write_text(text, encoding='utf-8')
compile(text, str(GENERATED), 'exec')
runpy.run_path(str(GENERATED), run_name='__main__')
