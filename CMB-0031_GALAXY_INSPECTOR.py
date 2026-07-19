# CMB-0031
from __future__ import annotations

import html
import urllib.request
import numpy as np
import pandas as pd
from IPython.display import clear_output, display
import ipywidgets as widgets

BASE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0030_GALAXY_INSPECTOR_ROBUST.py"
with urllib.request.urlopen(BASE_URL, timeout=40) as response:
    source = response.read().decode("utf-8")
exec(compile(source, "CMB-0030_GALAXY_INSPECTOR_ROBUST.py", "exec"), globals())

VERSION = "CMB-0031"


def dark_table_html(obj, title="Nearest catalog object"):
    keys = [
        "Object ID", "Catalog", "RA", "Dec", "Angular separation (arcsec)",
        "Redshift", "Redshift type", "Light-travel time (Gyr)",
        "Comoving distance (Gly)", "Luminosity distance (Gly)",
        "Angular diameter distance (Gly)", "Universe age at emission (Gyr)",
        "Angular size (arcsec)", "Estimated physical diameter (ly)",
        "Stellar mass", "Star formation rate", "Morphology", "Type",
    ]
    rows = []
    for key in keys:
        value = obj.get(key, "Not available")
        if isinstance(value, (float, np.floating)):
            value = fmt(value)
        rows.append(
            '<tr>'
            f'<th style="text-align:left;padding:7px 10px;background:#151515;color:#ffca28;border:1px solid #333">{html.escape(key)}</th>'
            f'<td style="padding:7px 10px;background:#050505;color:#f5f5f5;border:1px solid #333">{html.escape(str(value))}</td>'
            '</tr>'
        )
    return (
        '<div style="background:#000;color:#fff;padding:14px;border:1px solid #333;border-radius:10px">'
        f'<h3 style="margin:0 0 10px;color:#ff5252">{html.escape(title)}</h3>'
        '<table style="border-collapse:collapse;width:100%;font:13px sans-serif">'
        + ''.join(rows) + '</table></div>'
    )


def select_cosmology_object(primary, nearby):
    primary_z = safe_float(primary.get("Redshift"))
    if np.isfinite(primary_z) and primary_z > 0:
        return primary.copy(), False
    if nearby is None or nearby.empty or "Redshift" not in nearby.columns:
        return primary.copy(), False
    valid = nearby[pd.to_numeric(nearby["Redshift"], errors="coerce") > 0].copy()
    if valid.empty:
        return primary.copy(), False
    valid = valid.sort_values("Angular separation (arcsec)")
    return valid.iloc[0].to_dict(), True


def cmb0031_inspect(_=None):
    refresh_coordinates()
    coord = STATE.get("coord")
    if coord is None:
        return
    inspect_button.disabled = True
    STATE["warnings"] = []
    status.value = '<b style="color:#ffca28">Searching NED, SIMBAD, 3D-HST, and CANDELS/GOODS-S…</b>'
    try:
        obj = None
        nearby = pd.DataFrame()
        used_radius = None
        base_radius = max(0.5, float(fov.value) * 15.0)
        radii = sorted(set([base_radius, 1.0, 2.0, 5.0]))
        for radius in radii:
            obj, nearby = nearest_ned(coord, radius)
            if obj is None:
                obj, nearby = nearest_simbad(coord, radius)
            if obj is None:
                obj, nearby = nearest_vizier_deep(coord, radius)
            if obj is not None:
                used_radius = radius
                break
        if obj is None:
            warning_text = " | ".join(STATE["warnings"]) or "No catalog response."
            raise RuntimeError("No cataloged source was found within 5 arcminutes. " + warning_text)

        primary = obj.copy()
        primary.update(details(primary))
        cosmo_obj, substituted = select_cosmology_object(primary, nearby)
        cosmo_obj.update(details(cosmo_obj))

        STATE["object"] = primary
        STATE["nearby"] = nearby.head(25)
        STATE["cosmology_object"] = cosmo_obj

        with object_output:
            clear_output(wait=True)
            display(widgets.HTML(dark_table_html(primary, "Nearest catalog object")))
            if substituted:
                display(widgets.HTML(
                    '<div style="background:#180000;color:#fff3e0;padding:10px;border-left:4px solid #ff5252;margin-top:8px">'
                    'The nearest positional source has no usable redshift. Cosmology below uses the nearest catalog source with a valid redshift, without assigning that redshift to the positional source.'</n                    'div>'
                ))
                display(widgets.HTML(dark_table_html(cosmo_obj, "Nearest source with usable redshift")))

        with nearby_output:
            clear_output(wait=True)
            cols = [c for c in ["Object ID", "Angular separation (arcsec)", "Redshift", "Stellar mass"] if c in nearby.columns]
            styled = nearby[cols].head(25).style.format(precision=5).set_table_styles([
                {"selector": "table", "props": [("background", "#000"), ("color", "#fff"), ("border-collapse", "collapse")]},
                {"selector": "th", "props": [("background", "#151515"), ("color", "#ffca28"), ("border", "1px solid #333")]},
                {"selector": "td", "props": [("background", "#050505"), ("color", "#f5f5f5"), ("border", "1px solid #333")]},
            ])
            display(widgets.HTML('<div style="background:#000;color:#ff5252;padding:10px 12px 0"><h3>Nearby galaxies / catalog objects</h3></div>'))
            display(styled)

        with coverage_output:
            clear_output(wait=True)
            links = ''.join(
                f'<a target="_blank" style="color:#64b5f6" href="{html.escape(url)}">{html.escape(label)}</a><br>'
                for label, url in archive_links(coord).items()
            )
            display(widgets.HTML('<div style="background:#000;color:#fff;padding:12px"><h3 style="color:#ff5252">Available-observation searches</h3>' + links + '</div>'))

        with publication_output:
            clear_output(wait=True)
            links = ''.join(
                f'<a target="_blank" style="color:#64b5f6" href="{html.escape(url)}">{html.escape(label)}</a><br>'
                for label, url in paper_links(cosmo_obj, coord).items()
            )
            display(widgets.HTML('<div style="background:#000;color:#fff;padding:12px"><h3 style="color:#ff5252">Publications and survey references</h3>' + links + '</div>'))

        note_text = ''
        if substituted:
            note_text = f'<br><span style="color:#ffca28">Cosmology source: {html.escape(str(cosmo_obj.get("Object ID")))} at {fmt(cosmo_obj.get("Angular separation (arcsec)"),2)} arcsec.</span>'
        cosmology_output.value = f'''
        <div style="padding:16px;border-radius:10px;background:#000;color:#fff;font-family:sans-serif;line-height:1.9;border:1px solid #333">
          <b style="font-size:19px;color:#ff5252">COSMOLOGY PANEL</b><br>
          You are observing this galaxy as it was: <b>{fmt(cosmo_obj.get("Light-travel time (Gyr)"),3)} billion years ago</b><br>
          Current comoving distance: <b>{fmt(cosmo_obj.get("Comoving distance (Gly)"),3)} billion light-years</b><br>
          Universe age when light was emitted: <b>{fmt(cosmo_obj.get("Universe age at emission (Gyr)"),3)} billion years</b><br>
          Scale: <b>1 arcsecond = {fmt(cosmo_obj.get("Scale (ly/arcsec)"),0)} light-years</b><br>
          Estimated galaxy diameter: <b>{fmt(cosmo_obj.get("Estimated physical diameter (ly)"),0)} light-years</b>
          {note_text}
        </div>
        '''

        warnings = " | ".join(dict.fromkeys(STATE["warnings"]))
        extra = f'<br><span style="color:#ff9800">{html.escape(warnings)}</span>' if warnings else ''
        status.value = (
            f'<b style="color:#76ff03">Inspection complete using {html.escape(str(primary["Catalog"]))} '
            f'within {used_radius:g} arcmin: {html.escape(str(primary["Object ID"]))}</b>{extra}'
        )
    except Exception as exc:
        status.value = f'<b style="color:#ff5252">Inspection failed: {html.escape(str(exc))}</b>'
    finally:
        inspect_button.disabled = False


inspect_button.on_click(robust_inspect_galaxy, remove=True)
inspect_button.on_click(cmb0031_inspect)

header.value = header.value.replace("CMB-0030", "CMB-0031")
inspector.children = (
    widgets.HTML('<div style="background:#000;color:#ff5252;padding:10px 14px;border-radius:8px"><h2 style="margin:0">GALAXY INSPECTOR — CMB-0031</h2></div>'),
    *inspector.children[1:],
)

clear_output(wait=True)
display(widgets.VBox([header, controls, note, viewer, inspector], layout=widgets.Layout(width="100%")))
print("CMB-0031")
