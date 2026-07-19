# CMB-0040F_INFRASTRUCTURE.py
# Stable fallback: runs the preserved 40C full widget and adds browser/session guidance for 40E copy mode.
from __future__ import annotations

import subprocess
import sys
import textwrap
from IPython.display import display, HTML

VERSION='CMB-0040F'
BASE_URL='https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0040C_INFRASTRUCTURE.py'
LOCAL='CMB-0040C_INFRASTRUCTURE.py'

subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'ipywidgets', 'astroquery'])
subprocess.check_call(['bash', '-lc', f'curl -sL {BASE_URL} -o {LOCAL}'])

banner = '''
<div style="background:#050505;color:#f2f2f2;border-left:5px solid #ffb300;border-radius:8px;padding:12px 14px;margin:8px 0;font-family:Arial,Helvetica,sans-serif;line-height:1.5">
  <div style="font-weight:700;font-size:16px">CMB-0040F stable mode</div>
  <div>This loads the preserved full CMB-0040C Galaxy Inspector and inclusive catalog search.</div>
  <div style="margin-top:8px">The experimental live Aladin copy buttons in 40E require Colab JavaScript output support. If Colab shows “Could not load JavaScript files”, reload the notebook tab and allow third-party cookies for Colab/googleusercontent/aladin.cds.unistra.fr, then run 40E again.</div>
</div>
'''
display(HTML(banner))

with open(LOCAL, 'r', encoding='utf-8') as f:
    code = f.read()
exec(compile(code, LOCAL, 'exec'), globals())
print(VERSION)
