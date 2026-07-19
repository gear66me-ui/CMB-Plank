# CMB-0030 robust launcher and catalog fallback
from __future__ import annotations

import html
import urllib.request
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.vizier import Vizier
from IPython.display import clear_output, display
import ipywidgets as widgets

BASE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0030_GALAXY_INSPECTOR.py"
with urllib.request.urlopen(BASE_URL, timeout=40) as response:
    base_source = response.read().decode("utf-8")
exec(compile(base_source, "CMB-0030_GALAXY_INSPECTOR.py", "exec"), globals())

DEEP_CATALOGS = [
    ("J/ApJS/214/24", "3D-HST photometric catalog"),
    ("J/ApJS/207/24", "CANDELS GOODS-S multiwavelength catalog"),
]


def _pick_column(table, names):
    lowered = {str(name).lower(): name for name in table.colnames}
    for candidate in names:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None


def _catalog_rows(table, coord, catalog_name):
    if table is None or len(table) == 0:
        return []
    ra_col = _pick_column(table, ["RAJ2000", "RAdeg", "RA", "_RAJ2000"])
    dec_col = _pick_column(table, ["DEJ2000", "DEdeg", "DEC", "_DEJ2000"])
    if ra_col is None or dec_col is None:
        return []
    id_col = _pick_column(table, ["ID", "id", "Seq", "NUMBER", "Object"])
    zspec_col = _pick_column(table, ["z_spec", "zspec", "zsp", "zSpec"])
    zphot_col = _pick_column(table, ["z_peak", "zbest", "zphot", "z_phot", "z"])
    mass_col = _pick_column(table, ["lmass", "logM", "Mstar", "mass"])
    sfr_col = _pick_column(table, ["lsfr", "SFR", "sfr"])
    size_col = _pick_column(table, ["Re", "r_e", "R50", "a"])
    rows = []
    for index, row in enumerate(table):
        try:
            ra = float(row[ra_col])
            dec = float(row[dec_col])
            obj_coord = SkyCoord(ra * u.deg, dec * u.deg)
        except Exception:
            continue
        zspec = safe_float(row[zspec_col]) if zspec_col else np.nan
        zphot = safe_float(row[zphot_col]) if zphot_col else np.nan
        redshift = zspec if np.isfinite(zspec) and zspec > 0 else zphot
        redshift_type = "Spectroscopic" if np.isfinite(zspec) and zspec > 0 else (
            "Photometric" if np.isfinite(zphot) and zphot > 0 else "Unavailable"
        )
        identifier = str(row[id_col]) if id_col else str(index + 1)
        rows.append({
            "Object ID": f"{catalog_name} {identifier}",
            "Catalog": catalog_name,
            "RA": ra,
            "Dec": dec,
            "Angular separation (arcsec)": coord.separation(obj_coord).arcsec,
            "Redshift": redshift,
            "Redshift type": redshift_type,
            "Type": "Galaxy candidate",
            "Morphology": "Galaxy candidate",
            "Stellar mass": safe_float(row[mass_col]) if mass_col else np.nan,
            "Star formation rate": safe_float(row[sfr_col]) if sfr_col else np.nan,
            "Angular size (arcsec)": safe_float(row[size_col]) if size_col else np.nan,
        })
    return rows


def nearest_vizier_deep(coord, radius_arcmin=2.0):
    all_rows = []
    for catalog_id, catalog_name in DEEP_CATALOGS:
        try:
            service = Vizier(columns=["*", "+_r"], row_limit=250, timeout=30)
            result = service.query_region(
                coord,
                radius=radius_arcmin * u.arcmin,
                catalog=catalog_id,
            )
            for table in result.values():
                all_rows.extend(_catalog_rows(table, coord, catalog_name))
        except Exception as exc:
            STATE["warnings"].append(f"{catalog_name} unavailable: {exc}")
    if not all_rows:
        return None, pd.DataFrame()
    frame = pd.DataFrame(all_rows).sort_values("Angular separation (arcsec)").reset_index(drop=True)
    return frame.iloc[0].to_dict(), frame


def robust_inspect_galaxy(_=None):
    refresh_coordinates()
    coord = STATE.get("coord")
    if coord is None:
        return
    inspect_button.disabled = True
    STATE["warnings"] = []
    status.value = "<b>Searching NED, SIMBAD, 3D-HST, and CANDELS/GOODS-S…</b>"
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
            raise RuntimeError(
                "No cataloged source was found within 5 arcminutes. " + warning_text
            )

        calculated = details(obj)
        for key, value in calculated.items():
            if key not in obj or not np.isfinite(safe_float(obj.get(key))):
                obj[key] = value
        STATE["object"] = obj
        STATE["nearby"] = nearby.head(25)

        with object_output:
            clear_output()
            display(widgets.HTML("<h3>Nearest catalog object</h3>" + table_html(obj)))
        with nearby_output:
            clear_output()
            display(widgets.HTML("<h3>Nearby galaxies / catalog objects</h3>"))
            cols = [name for name in ["Object ID", "Angular separation (arcsec)", "Redshift", "Stellar mass"] if name in nearby.columns]
            display(nearby[cols].head(25).style.format(precision=5))
        with coverage_output:
            clear_output()
            display(widgets.HTML("<h3>Available-observation searches</h3>"))
            for label, url in archive_links(coord).items():
                display(widgets.HTML(f'<a target="_blank" href="{html.escape(url)}">{html.escape(label)}</a><br>'))
        with publication_output:
            clear_output()
            display(widgets.HTML("<h3>Publications and survey references</h3>"))
            for label, url in paper_links(obj, coord).items():
                display(widgets.HTML(f'<a target="_blank" href="{html.escape(url)}">{html.escape(label)}</a><br>'))

        cosmology_output.value = f'''<div style="padding:14px;border-radius:10px;background:#071a2b;color:white;font-family:sans-serif;line-height:1.8"><b style="font-size:18px">COSMOLOGY PANEL</b><br>You are observing this galaxy as it was: <b>{fmt(obj.get("Light-travel time (Gyr)"),3)} billion years ago</b><br>Current comoving distance: <b>{fmt(obj.get("Comoving distance (Gly)"),3)} billion light-years</b><br>Universe age when light was emitted: <b>{fmt(obj.get("Universe age at emission (Gyr)"),3)} billion years</b><br>Scale: <b>1 arcsecond = {fmt(obj.get("Scale (ly/arcsec)"),0)} light-years</b><br>Estimated galaxy diameter: <b>{fmt(obj.get("Estimated physical diameter (ly)"),0)} light-years</b></div>'''
        warnings = " | ".join(STATE["warnings"])
        extra = f"<br><span style='color:#ef6c00'>{html.escape(warnings)}</span>" if warnings else ""
        status.value = (
            f'<b style="color:#1b5e20">Inspection complete using {html.escape(str(obj["Catalog"]))} '
            f'within {used_radius:g} arcmin: {html.escape(str(obj["Object ID"]))}</b>{extra}'
        )
    except Exception as exc:
        status.value = f'<b style="color:#b71c1c">Inspection failed: {html.escape(str(exc))}</b>'
    finally:
        inspect_button.disabled = False


inspect_button.on_click(inspect_galaxy, remove=True)
inspect_button.on_click(robust_inspect_galaxy)
status.value = '<b style="color:#1565c0">Robust deep-field catalogs loaded. Press Inspect Galaxy.</b>'
print("CMB-0030 ROBUST CATALOG FALLBACK")
