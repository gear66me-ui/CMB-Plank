# CMB-0039S_INFRASTRUCTURE.py
from __future__ import annotations

import urllib.request

SRC_URL = 'https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0039P_INFRASTRUCTURE.py'

source = urllib.request.urlopen(SRC_URL, timeout=60).read().decode('utf-8')

# Rollback to the stable full Aladin iframe UI from 39P.
# Preserve: top controls, native Aladin left survey drawer, iframe sky map,
# and Galaxy Inspector underneath. Do not replace the viewer shell.
source = source.replace("# CMB-0039P_INFRASTRUCTURE.py", "# CMB-0039S_INFRASTRUCTURE.py")
source = source.replace("VERSION = 'CMB-0039P'", "VERSION = 'CMB-0039S'")

# Clarify the coordinate button behavior without changing the Aladin UI.
# The embedded Aladin page is cross-origin; Python cannot read a live panned center
# from inside that iframe. This button therefore loads the current Target field into
# the single Galaxy Inspector coordinate cell and leaves the real Aladin interface intact.
source = source.replace(
    "get_aladin_button = widgets.Button(description='Get coordinates from Aladin', button_style='info', icon='crosshairs')",
    "get_aladin_button = widgets.Button(description='Load target into inspector', button_style='info', icon='crosshairs')",
)
source = source.replace(
    "coord_status.value = '<b style=\"color:#1565c0\">Coordinates loaded from current Aladin target into the single RA Dec cell.</b>'",
    "coord_status.value = '<b style=\"color:#1565c0\">Target coordinates loaded into the single RA Dec inspector cell. Aladin viewer UI is preserved.</b>'",
)

exec(compile(source, 'CMB-0039S_FROM_0039P.py', 'exec'), globals())
