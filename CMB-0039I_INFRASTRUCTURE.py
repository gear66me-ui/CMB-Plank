# CMB-0039I 31-style silent star viewer launcher
from __future__ import annotations

import io
import contextlib
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0030_GALAXY_INSPECTOR_ROBUST.py"

with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
    source = response.read().decode("utf-8")

source = source.replace('BASE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0030_GALAXY_INSPECTOR.py"', 'BASE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0030_GALAXY_INSPECTOR.py"')
source = source.replace('VERSION = "CMB-0030"', 'VERSION = "CMB-0039I"')

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    exec(compile(source, "CMB-0039I_FROM_CMB0030_ROBUST.py", "exec"), globals())
