"""CMB-0018 — Gaia widget for RA 03:19:30.85, Dec -21:45:24.1."""
from __future__ import annotations
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0012.py"
req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/18.0"})
with urllib.request.urlopen(req, timeout=60) as r:
    source = r.read().decode("utf-8")

replacements = [
    ('VERSION = "CMB-0012"', 'VERSION = "CMB-0018"'),
    ('RA_SEXAGESIMAL = "03:12:59.96"', 'RA_SEXAGESIMAL = "03:19:30.85"'),
    ('DEC_SEXAGESIMAL = "-20:02:09.0"', 'DEC_SEXAGESIMAL = "-21:45:24.1"'),
    ('RA_DEG = 48.2498333333', 'RA_DEG = 49.8785416667'),
    ('DEC_DEG = -20.0358333333', 'DEC_DEG = -21.7566944444'),
    ('Mozilla/5.0 CMB-Gaia-Widget/12.0', 'Mozilla/5.0 CMB-Gaia-Widget/18.0'),
]
for old, new in replacements:
    source = source.replace(old, new)

source = source.replace(
    'fig = plt.figure(figsize=(10, 9))',
    'fig = plt.figure(figsize=(10, 9), facecolor="black")',
)
source = source.replace(
    'ax = fig.add_subplot(111, projection=wcs)',
    'ax = fig.add_subplot(111, projection=wcs)\n            ax.set_facecolor("black")',
)
source = source.replace(
    'ax.set_xlabel("Right ascension (ICRS)")',
    'ax.set_xlabel("Right ascension (ICRS)", color="white")',
)
source = source.replace(
    'ax.set_ylabel("Declination (ICRS)")',
    'ax.set_ylabel("Declination (ICRS)", color="white")',
)
source = source.replace(
    'ax.legend(loc="upper right")',
    'legend = ax.legend(loc="upper right", facecolor="#111111", edgecolor="#777777")\n            [t.set_color("white") for t in legend.get_texts()]',
)
source = source.replace(
    'ax.set_title(f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin · Gaia radius {radius_widget.value:g} arcmin\\nGaia DR3 sources shown as crosses; no supplied-coordinate circle")',
    'ax.set_title(f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin\\nGaia DR3 sources", color="white")',
)

start = source.find('            cols = ["source_id","separation_arcsec"')
if start != -1:
    end = source.find('\n\n        except Exception as exc:', start)
    if end != -1:
        source = source[:start] + source[end:]

old = '            print("\\nNearest Gaia source summary")\n            display(summary.style.hide(axis="index").set_properties(**{"text-align": "left"}))'
new = '''            rows = [(str(r["Property"]), str(r["Nearest Gaia source"])) for _, r in summary.iterrows()]
            html_rows = "".join(
                f"<tr><td style='padding:9px 12px;border-bottom:1px solid #2e3944;font-weight:600;color:#b9d8ef;width:42%;'>{p}</td>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #2e3944;color:#f4f7fa;'>{v}</td></tr>"
                for p, v in rows
            )
            display(widgets.HTML(value=f"""
            <div style='margin-top:14px;background:#080c11;color:#f4f7fa;border:1px solid #34404c;border-radius:10px;overflow:hidden;font-family:Arial,sans-serif;'>
              <div style='padding:12px 14px;background:#14202b;font-size:18px;font-weight:700;'>Nearest Gaia source summary</div>
              <table style='width:100%;border-collapse:collapse;font-size:14px;'>
                <thead><tr><th style='padding:9px 12px;text-align:left;background:#1d2a36;'>Property</th><th style='padding:9px 12px;text-align:left;background:#1d2a36;'>Gaia result</th></tr></thead>
                <tbody>{html_rows}</tbody>
              </table>
            </div>
            """))'''
source = source.replace(old, new)

namespace = {"__name__": "__main__", "__file__": "CMB-0018.py"}
exec(compile(source, "CMB-0018.py", "exec"), namespace, namespace)
