# CMB-0039W_INFRASTRUCTURE.py
from __future__ import annotations

from pathlib import Path
import urllib.request
import runpy

SRC_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0039P_INFRASTRUCTURE.py'
GENERATED = Path('CMB-0039W_GENERATED_INFRASTRUCTURE.py')

text = urllib.request.urlopen(SRC_URL, timeout=60).read().decode('utf-8')
if text.strip().startswith('404'):
    raise RuntimeError('GitHub returned 404 for CMB-0039P_INFRASTRUCTURE.py')

# Version stamp only.
text = text.replace("VERSION = 'CMB-0039P'", "VERSION = 'CMB-0039W'")
text = text.replace('# CMB-0039P_INFRASTRUCTURE.py', '# CMB-0039W_GENERATED_INFRASTRUCTURE.py')

# Default survey: Hubble Outreach color.
text = text.replace(
    "survey = widgets.Dropdown(options=SURVEYS, value='CDS/P/HST/GOODS/color', description='Survey:', layout=widgets.Layout(width='520px'))",
    "survey = widgets.Dropdown(options=SURVEYS, value='CDS/P/HST/EPO', description='Survey:', layout=widgets.Layout(width='520px'))"
)
text = text.replace(
    "viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, survey.value, 'Hubble GOODS color'))",
    "viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, 'CDS/P/HST/EPO', 'Hubble Outreach color'))"
)

# Make the coordinate button honest: it uses the loaded notebook target, not the iframe internals.
text = text.replace(
    "get_aladin_button = widgets.Button(description='Get coordinates from Aladin', button_style='info', icon='crosshairs')",
    "get_aladin_button = widgets.Button(description='Use loaded target coordinates', button_style='info', icon='crosshairs')"
)
text = text.replace(
    "coord_input = widgets.Text(value='', description='RA Dec:', placeholder='RA Dec in one cell', layout=widgets.Layout(width='620px'))",
    "coord_input = widgets.Text(value='', description='RA Dec:', placeholder='Paste Aladin RA Dec here, or use loaded target', layout=widgets.Layout(width='720px'))"
)
text = text.replace(
    "# The Colab iframe is cross-origin, so Python cannot read a panned Aladin center directly.\n    # This restores the requested button and loads the current Aladin target/center into the single inspector cell.",
    "# Stable iframe mode: Colab cannot read the live panned Aladin center from the remote iframe.\n    # This button loads the current notebook Target into the single inspector coordinate cell."
)
text = text.replace(
    "coord_status.value = '<b style=\"color:#1565c0\">Coordinates loaded from current Aladin target into the single RA Dec cell.</b>'",
    "coord_status.value = '<b style=\"color:#1565c0\">Loaded Target into RA Dec cell. For a panned/clicked Aladin position, paste the Aladin coordinates into this one field.</b>'"
)
text = text.replace(
    "get_aladin_button.on_click(get_coordinates_from_aladin)",
    "get_aladin_button.on_click(get_coordinates_from_aladin)"
)

GENERATED.write_text(text, encoding='utf-8')
compile(text, str(GENERATED), 'exec')
runpy.run_path(str(GENERATED), run_name='__main__')
