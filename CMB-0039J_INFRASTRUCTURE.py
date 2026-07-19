# CMB-0039J_INFRASTRUCTURE.py
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import urllib.request

from IPython.display import clear_output

BASE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0030_GALAXY_INSPECTOR.py"

try:
    import astroquery  # noqa: F401
except Exception:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "astroquery"])

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    with urllib.request.urlopen(BASE_URL, timeout=60) as response:
        source = response.read().decode("utf-8")

source = source.replace('VERSION = "CMB-0030"', 'VERSION = "CMB-0039J"')
source = source.replace('print(VERSION)', '')

clear_output(wait=True)
exec(compile(source, "CMB-0039J_FROM_CMB0030.py", "exec"), globals())
