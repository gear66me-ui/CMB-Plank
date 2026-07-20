# CMB-0040C_INFRASTRUCTURE.py
from __future__ import annotations

import contextlib
import html
import io
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    try:
        import astroquery  # noqa: F401
    except Exception:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'astroquery'])

import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, FileLink
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.cosmology import Planck18
from astroquery.ipac.ned import Ned
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

try:
    from astroquery.mast import Catalogs
except Exception:
    Catalogs = None

VERSION = 'CMB-0040C'
DEFAULT_TARGET = '03 32 39.99 -27 48 00.0'
DEFAULT_FOV = 0.08
DEFAULT_SURVEY = 'CDS/P/HST/EPO'
CATALOG_PATH = Path('/content/MY_GALAXIES.csv')

SURVEYS = [
    ('DSS2 color', 'P/DSS2/color'),
    ('DSS2 blue', 'P/DSS2/blue'),
    ('2MASS color infrared', 'P/2MASS/color'),
    ('WISE color infrared', 'P/allWISE/color'),
    ('GALEX GR6/7 ultraviolet', 'P/GALEXGR6/AIS/color'),
    ('Hubble Outreach color', 'CDS/P/HST/EPO'),
    ('Hubble GOODS color', 'CDS/P/HST/GOODS/color'),
    ('Hubble GOODS i-band', 'CDS/P/HST/GOODS/i'),
    ('Hubble R-band', 'CDS/P/HST/R'),
    ('Hubble H-beta', 'CDS/P/HST/Hbeta'),
    ('JWST F150W', 'CDS/P/JWST/F150W'),
    ('JWST F444W', 'CDS/P/JWST/F444W'),
    ('JWST F480M', 'CDS/P/JWST/F480M'),
]

STATE = {'coord': None, 'object': None, 'nearby': pd.DataFrame(), 'warnings': []}


def esc(x):
    return html.escape('' if x is None else str(x))


def safe_float(value):
    try:
        if value is None or np.ma.is_masked(value):
            return np.nan
        return float(value)
    except Exception:
        return np.nan


def selected_name():
    return next((label for label, value in SURVEYS if value == survey.value), str(survey.value))


def aladin_url(target_text, fov_deg, survey_id):
    return 'https://aladin.u-strasbg.fr/AladinLite/?' + urllib.parse.urlencode({
        'target': str(target_text).strip(),
        'fov': f'{float(fov_deg):g}',
        'survey': survey_id,
    })


def viewer_html(target_text, fov_deg, survey_id):
    url = aladin_url(target_text, fov_deg, survey_id)
    return f'''
    <div style="width:100%;background:#000;overflow:visible;">
      <iframe src="{esc(url)}"
        style="width:100%;height:820px;border:0;display:block;background:#000;overflow:visible;"
        allow="fullscreen; clipboard-read; clipboard-write"
        allowfullscreen>
      </iframe>
    </div>
    '''


def dark_box(title='', body='', border='#555', bg='#050505'):
    heading = f'<div style="font-weight:700;font-size:15px;margin-bottom:6px;color:#ffffff">{esc(title)}</div>' if title else ''
    return f'''
    <div style="background:{bg};color:#f2f2f2;border-left:5px solid {border};
                border-radius:7px;padding:11px 13px;margin:8px 0;
                font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.55;">
      {heading}<div>{body}</div>
    </div>
    '''


def parse_target(value):
    value = str(value).strip()
    if not value:
        raise ValueError('Paste one ICRS coordinate string first, for example: 03 32 39.16 -27 48 44.7')
    parts = re.split(r'[ ,]+', value)
    if len(parts) == 2:
        try:
            return SkyCoord(float(parts[0]) * u.deg, float(parts[1]) * u.deg, frame='icrs')
        except Exception:
            pass
    try:
        return SkyCoord(value, unit=(u.hourangle, u.deg), frame='icrs')
    except Exception:
        return SkyCoord.from_name(value)


def first_value(row, names, default=np.nan):
    cols = list(getattr(row, 'colnames', []) or getattr(row, 'index', []))
    low = {str(c).lower(): c for c in cols}
    for name in names:
        key = low.get(str(name).lower(), name)
        if key in cols:
            try:
                if not np.ma.is_masked(row[key]):
                    return row[key]
            except Exception:
                pass
    return default


def coord_from_row(row):
    cols = list(getattr(row, 'colnames', []) or getattr(row, 'index', []))
    low = {str(c).lower().replace('-', '').replace('_', ''): c for c in cols}
    ra_keys = ['ra', 'raj2000', 'raicrs', 'raj2000', 'alpha', 'ra2000', 'radeg']
    de_keys = ['dec', 'dej2000', 'deicrs', 'decicrs', 'delta', 'de2000', 'dedeg']
    ra_name = next((low[k] for k in ra_keys if k in low), None)
    de_name = next((low[k] for k in de_keys if k in low), None)
    if ra_name and de_name:
        ra_val, de_val = row[ra_name], row[de_name]
        ra, de = safe_float(ra_val), safe_float(de_val)
        if np.isfinite(ra + de):
            return SkyCoord(ra * u.deg, de * u.deg, frame='icrs')
        try:
            return SkyCoord(str(ra_val), str(de_val), unit=(u.hourangle, u.deg), frame='icrs')
        except Exception:
            return None
    return None


def object_name_from_row(row):
    cols = list(getattr(row, 'colnames', []) or getattr(row, 'index', []))
    preferred = ['Object Name', 'Object_Name', 'MAIN_ID', 'Name', 'ID', 'ID_MAIN', 'Source', 'SourceID', 'objID', 'ObjID', 'designation', 'Designation', 'IAUName', 'ID_CANDELS', 'ID_3DHST']
    for key in preferred:
        if key in cols:
            try:
                text = str(row[key]).strip()
                if text and text.lower() not in ['--', 'masked']:
                    return text
            except Exception:
                pass
    for key in cols[:10]:
        try:
            text = str(row[key]).strip()
            if text and len(text) < 80 and text.lower() not in ['--', 'masked']:
                return text
        except Exception:
            pass
    return 'Catalog row'


def add_row(rows, seen, coord, obj_id, catalog, ra=np.nan, dec=np.nan, sep=np.nan, redshift=np.nan, typ=''):
    if not np.isfinite(sep) and np.isfinite(safe_float(ra) + safe_float(dec)):
        sep = coord.separation(SkyCoord(safe_float(ra) * u.deg, safe_float(dec) * u.deg)).arcsec
    key = (str(catalog), str(obj_id), round(safe_float(sep) if np.isfinite(safe_float(sep)) else 999999, 3))
    if key in seen:
        return
    seen.add(key)
    rows.append({
        'Object ID': obj_id,
        'Catalog': catalog,
        'RA': safe_float(ra),
        'Dec': safe_float(dec),
        'Angular separation (arcsec)': safe_float(sep),
        'Redshift': safe_float(redshift),
        'Type': typ,
    })


def rows_to_dark_table(rows, max_rows=80):
    rows = sorted(rows, key=lambda r: safe_float(r.get('Angular separation (arcsec)')) if np.isfinite(safe_float(r.get('Angular separation (arcsec)'))) else 999999)[:max_rows]
    if not rows:
        return dark_box('No rows', 'No catalog rows were returned.', '#777')
    headers = ['Catalog', 'Object ID', 'RA', 'Dec', 'Sep arcsec', 'Redshift', 'Type']
    head = ''.join(f'<th style="padding:6px 8px;border:1px solid #333;background:#111;color:#fff;text-align:left">{esc(h)}</th>' for h in headers)
    body = ''
    for r in rows:
        cells = [
            r.get('Catalog', ''),
            r.get('Object ID', ''),
            f"{safe_float(r.get('RA')):.7f}" if np.isfinite(safe_float(r.get('RA'))) else '',
            f"{safe_float(r.get('Dec')):.7f}" if np.isfinite(safe_float(r.get('Dec'))) else '',
            f"{safe_float(r.get('Angular separation (arcsec)')):.3f}" if np.isfinite(safe_float(r.get('Angular separation (arcsec)'))) else '',
            f"{safe_float(r.get('Redshift')):.6f}" if np.isfinite(safe_float(r.get('Redshift'))) else '',
            r.get('Type', ''),
        ]
        body += '<tr>' + ''.join(f'<td style="padding:6px 8px;border:1px solid #333;color:#eee;background:#070707">{esc(c)}</td>' for c in cells) + '</tr>'
    return '<table style="border-collapse:collapse;width:100%;font:13px Arial,Helvetica,sans-serif;margin-top:8px">' + '<tr>' + head + '</tr>' + body + '</table>'


def query_ned(coord, radius_arcsec, rows, seen):
    try:
        Ned.TIMEOUT = 45
        table = Ned.query_region(coord, radius=radius_arcsec * u.arcsec)
    except Exception as exc:
        STATE['warnings'].append(f'NED unavailable: {exc}')
        return
    if table is None:
        return
    for row in table[:80]:
        ra = safe_float(first_value(row, ['RA', 'RA(deg)']))
        dec = safe_float(first_value(row, ['DEC', 'DEC(deg)']))
        add_row(rows, seen, coord, str(first_value(row, ['Object Name', 'Object_Name', 'MAIN_ID'], 'NED object')), 'NED', ra, dec, redshift=first_value(row, ['Redshift', 'z']), typ=str(first_value(row, ['Type', 'Object Type'], '')))


def query_simbad(coord, radius_arcsec, rows, seen):
    try:
        Simbad.TIMEOUT = 45
        service = Simbad()
        service.add_votable_fields('otype', 'z_value')
        table = service.query_region(coord, radius=radius_arcsec * u.arcsec)
    except Exception as exc:
        STATE['warnings'].append(f'SIMBAD unavailable: {exc}')
        return
    if table is None:
        return
    for row in table[:80]:
        try:
            c = SkyCoord(str(row['RA']), str(row['DEC']), unit=(u.hourangle, u.deg), frame='icrs')
            add_row(rows, seen, coord, str(row['MAIN_ID']), 'SIMBAD', c.ra.deg, c.dec.deg, coord.separation(c).arcsec, row['Z_VALUE'] if 'Z_VALUE' in table.colnames else np.nan, str(row['OTYPE']) if 'OTYPE' in table.colnames else '')
        except Exception:
            pass


def query_vizier_catalogs(coord, radius_arcsec, rows, seen):
    radius = radius_arcsec * u.arcsec
    explicit_catalogs = [
        'I/355/gaiadr3', 'I/345/gaia2',
        'II/246/out', 'II/328/allwise', 'II/363/unwise',
        'II/335/galex_ais', 'II/312/ais',
        'IX/57/eRASS1', 'IX/61/xmm4d10s', 'IX/55/xmm3r8s', 'IX/59/csc2master',
        'J/ApJS/207/24', 'J/ApJS/214/24', 'J/ApJS/258/11', 'J/ApJS/229/32',
        'J/ApJ/754/83', 'J/AJ/151/134', 'J/ApJ/837/97'
    ]
    keywords = [
        'GOODS', 'GOODS-S', 'CDFS', 'Chandra Deep Field South', 'CANDELS', 'JADES', 'JWST',
        'HUDF', 'Hubble Source Catalog', '3D-HST', 'GEMS', 'COMBO-17',
        'eROSITA', 'XMM', 'Chandra', 'GALEX', 'AllWISE', 'WISE', '2MASS', 'Gaia', 'VLA', 'ALMA'
    ]
    catalogs = []
    for cat in explicit_catalogs:
        if cat not in catalogs:
            catalogs.append(cat)
    for kw in keywords:
        try:
            found = Vizier.find_catalogs(kw)
            for key in list(found.keys())[:12]:
                if key not in catalogs:
                    catalogs.append(key)
        except Exception as exc:
            STATE['warnings'].append(f'VizieR discovery failed for {kw}: {exc}')
    try:
        v = Vizier(columns=['*', '+_r'], row_limit=120)
        v.TIMEOUT = 45
        result = v.query_region(coord, radius=radius)
        ingest_vizier_result(result, 'VizieR broad cone', coord, rows, seen)
    except Exception as exc:
        STATE['warnings'].append(f'VizieR broad cone unavailable: {exc}')
    for cat in catalogs[:140]:
        try:
            v = Vizier(columns=['*', '+_r'], row_limit=80)
            v.TIMEOUT = 35
            result = v.query_region(coord, radius=radius, catalog=cat)
            ingest_vizier_result(result, cat, coord, rows, seen)
        except Exception:
            continue


def ingest_vizier_result(result, label, coord, rows, seen):
    for table in result:
        meta = getattr(table, 'meta', {}) or {}
        cat = meta.get('name') or meta.get('ID') or getattr(table, 'name', None) or label
        description = meta.get('description', '')
        cols = getattr(table, 'colnames', [])
        for row in table[:80]:
            c = coord_from_row(row)
            sep = safe_float(row['_r']) if '_r' in cols else np.nan
            if c is not None:
                sep = coord.separation(c).arcsec
                ra, dec = c.ra.deg, c.dec.deg
            else:
                ra, dec = np.nan, np.nan
            z = first_value(row, ['z', 'Z', 'redshift', 'zphot', 'zspec', 'z_phot', 'z_spec'])
            add_row(rows, seen, coord, object_name_from_row(row), f'VizieR {cat}', ra, dec, sep, z, description[:90])


def query_mast(coord, radius_arcsec, rows, seen):
    if Catalogs is None:
        STATE['warnings'].append('MAST astroquery Catalogs unavailable.')
        return
    mast_catalogs = ['HSC', 'GAIADR3', 'Panstarrs']
    for cat in mast_catalogs:
        try:
            table = Catalogs.query_region(coord, radius=radius_arcsec * u.arcsec, catalog=cat)
        except Exception as exc:
            STATE['warnings'].append(f'MAST {cat} unavailable: {exc}')
            continue
        if table is None:
            continue
        for row in table[:80]:
            c = coord_from_row(row)
            if c is None:
                continue
            add_row(rows, seen, coord, object_name_from_row(row), f'MAST {cat}', c.ra.deg, c.dec.deg, coord.separation(c).arcsec, np.nan, 'MAST catalog row')


def object_details(obj):
    z = safe_float(obj.get('Redshift'))
    body = []
    body.append(f'<b>Catalog:</b> {esc(obj.get("Catalog"))}<br>')
    body.append(f'<b>Object ID:</b> {esc(obj.get("Object ID"))}<br>')
    body.append(f'<b>RA Dec:</b> {safe_float(obj.get("RA")):.8f} {safe_float(obj.get("Dec")):.8f}<br>')
    body.append(f'<b>Separation:</b> {safe_float(obj.get("Angular separation (arcsec)")):.3f} arcsec<br>')
    if np.isfinite(z) and z > 0:
        body.append(f'<b>Redshift:</b> {z:.6f}<br>')
        body.append(f'<b>Lookback time:</b> {Planck18.lookback_time(z).to_value(u.Gyr):.3f} Gyr<br>')
        body.append(f'<b>Comoving distance:</b> {Planck18.comoving_distance(z).to_value(u.Glyr):.3f} Gly<br>')
    else:
        body.append('<b>Redshift:</b> not available in returned row<br>')
    body.append(f'<b>Type/description:</b> {esc(obj.get("Type", ""))}')
    return dark_box('Best catalog match', ''.join(body), '#4caf50')


def archive_links(coord):
    position = f'{coord.ra.deg:.7f},{coord.dec.deg:.7f}'
    links = {
        'CDS / VizieR': 'https://vizier.cds.unistra.fr/viz-bin/VizieR?-c=' + urllib.parse.quote(position),
        'Simbad': 'https://simbad.u-strasbg.fr/simbad/sim-coo?Coord=' + urllib.parse.quote(position) + '&Radius=1&Radius.unit=arcmin',
        'NED': 'https://ned.ipac.caltech.edu/conesearch?in_csys=Equatorial&in_equinox=J2000.0&lon=' + f'{coord.ra.deg:.7f}' + '&lat=' + f'{coord.dec.deg:.7f}' + '&radius=1.0',
        'MAST / Hubble / JWST': 'https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html?searchQuery=' + urllib.parse.quote(position),
        'Chandra': 'https://cda.harvard.edu/chaser/',
        'XMM / ESA': 'https://nxsa.esac.esa.int/nxsa-web/',
        'ALMA': 'https://almascience.eso.org/aq/?result_view=observation',
        'IRSA Finder': 'https://irsa.ipac.caltech.edu/applications/finderchart/?locstr=' + urllib.parse.quote(position),
    }
    html_links = ''.join(f'<a style="color:#90caf9" target="_blank" href="{esc(url)}">{esc(label)}</a><br>' for label, url in links.items())
    return dark_box('Archive search links', html_links, '#9c27b0')


header = widgets.HTML(value=f'''
<div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;font-family:sans-serif">
  <div style="font-size:22px;font-weight:700">INTERACTIVE MULTI-SURVEY SKY MAP — {VERSION}</div>
  <div style="font-size:13px;opacity:.9;margin-top:4px">Original Aladin touch map · drag to pan · pinch or use +/- to zoom · real HiPS survey imagery</div>
</div>
''')

target = widgets.Text(value=DEFAULT_TARGET, description='Target:', layout=widgets.Layout(width='520px'))
survey = widgets.Dropdown(options=SURVEYS, value=DEFAULT_SURVEY, description='Survey:', layout=widgets.Layout(width='520px'))
fov = widgets.Dropdown(options=[('0.01° — very tight', .01), ('0.03°', .03), ('0.08° — HUDF/GOODS', .08), ('0.25°', .25), ('1°', 1.0), ('5°', 5.0), ('20°', 20.0)], value=DEFAULT_FOV, description='Field:', layout=widgets.Layout(width='300px'))
load_button = widgets.Button(description='Load Interactive Map', button_style='primary', icon='globe')
open_button = widgets.Button(description='Open Full Screen', icon='external-link')
note = widgets.HTML(value=dark_box('Coverage note', 'Hubble/JWST are pointed-observation archives. Blank imagery may mean no coverage; catalog search still checks broad archives.', '#ffb300'))
viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, DEFAULT_SURVEY))


def reload_map(_=None):
    viewer.value = viewer_html(target.value, fov.value, survey.value)


def open_full(_=None):
    display(widgets.HTML(value=f"<script>window.open({aladin_url(target.value, fov.value, survey.value)!r},'_blank');</script>"))

load_button.on_click(reload_map)
open_button.on_click(open_full)
controls = widgets.VBox([widgets.HBox([target]), widgets.HBox([survey]), widgets.HBox([fov, load_button, open_button])])

coord_input = widgets.Text(value='', description='ICRS RA Dec:', placeholder='03 32 39.16 -27 48 44.7  OR  53.1631667 -27.8124167', layout=widgets.Layout(width='100%'))
find_button = widgets.Button(description='Find galaxy / object from ICRS coordinates', button_style='success', icon='search', layout=widgets.Layout(width='360px'))
copy_target_button = widgets.Button(description='Copy loaded target into ICRS cell', icon='copy', layout=widgets.Layout(width='300px'))
save_button = widgets.Button(description='Save Galaxy', icon='save', layout=widgets.Layout(width='160px'))
export_button = widgets.Button(description='Export CSV', icon='download', layout=widgets.Layout(width='160px'))
notes = widgets.Textarea(description='Notes:', placeholder='Free-text notes', layout=widgets.Layout(width='100%', height='90px'))
status = widgets.HTML(value=dark_box('Ready', 'Paste one ICRS coordinate string and press Find galaxy / object.', '#777'))
results = widgets.HTML(value='')
nearby_panel = widgets.HTML(value='')
archives = widgets.HTML(value='')


def set_status(title, body, border='#2196f3'):
    status.value = dark_box(title, body, border)


def copy_target(_=None):
    coord_input.value = target.value
    set_status('Copied target', 'Loaded target copied into the single ICRS coordinate cell.', '#2196f3')


def find_object(_=None):
    find_button.disabled = True
    results.value = ''
    nearby_panel.value = ''
    archives.value = ''
    STATE['warnings'] = []
    try:
        coord = parse_target(coord_input.value)
        STATE['coord'] = coord
        parsed = f'Parsed ICRS decimal: <b>{coord.ra.deg:.8f} {coord.dec.deg:.8f}</b><br>Sexagesimal: <b>{coord.ra.to_string(unit=u.hour, sep=":", precision=3)} {coord.dec.to_string(unit=u.deg, sep=":", precision=3, alwayssign=True)}</b>'
        set_status('Searching inclusive catalog stack', parsed + '<br>Trying NED, SIMBAD, MAST/HSC, broad VizieR, and survey-family discovery for GOODS/CANDELS/JADES/HST/JWST/Gaia/2MASS/WISE/GALEX/X-ray catalogs…', '#2196f3')
        radius_arcsec = max(120.0, min(900.0, float(fov.value) * 3600.0))
        all_rows, seen = [], set()
        print("\n========== NED ==========")
        query_ned(coord, radius_arcsec, all_rows, seen)
        print("NED COMPLETE")

        print("\n========== SIMBAD ==========")
        query_simbad(coord, radius_arcsec, all_rows, seen)
        print("SIMBAD COMPLETE")

        print("\n========== MAST ==========")
        query_mast(coord, radius_arcsec, all_rows, seen)
        print("MAST COMPLETE")

        print("\n========== VIZIER ==========")
        query_vizier_catalogs(coord, radius_arcsec, all_rows, seen)
        print("VIZIER COMPLETE")
        all_rows = [r for r in all_rows if r.get('Catalog')]
        if not all_rows:
            warning_text = '<br>'.join(esc(w) for w in STATE['warnings']) or 'No catalog service returned a row.'
            raise RuntimeError('No catalog rows found in the inclusive stack for this cone.<br>' + warning_text)
        all_rows = sorted(all_rows, key=lambda r: safe_float(r.get('Angular separation (arcsec)')) if np.isfinite(safe_float(r.get('Angular separation (arcsec)'))) else 999999)
        best = all_rows[0]
        STATE['object'] = best
        STATE['nearby'] = pd.DataFrame(all_rows[:120])
        results.value = object_details(best)
        nearby_panel.value = dark_box('Inclusive catalog results', f'{len(all_rows)} rows returned. Showing closest matches.' + rows_to_dark_table(all_rows, 80), '#00bcd4')
        archives.value = archive_links(coord)
        warning_html = ''
        if STATE['warnings']:
            warning_html = '<br><br><b>Service notes:</b><br>' + '<br>'.join(esc(w) for w in STATE['warnings'][:12])
        set_status('Find galaxy complete', f'Best match: <b>{esc(best.get("Object ID"))}</b> in <b>{esc(best.get("Catalog"))}</b>.{warning_html}', '#4caf50')
    except Exception as exc:
        set_status('Find galaxy failed', str(exc), '#f44336')
    finally:
        find_button.disabled = False


def save_galaxy(_=None):
    obj = STATE.get('object')
    coord = STATE.get('coord')
    if obj is None or coord is None:
        set_status('Save blocked', 'Run Find galaxy first.', '#f44336')
        return
    row = {'Date': pd.Timestamp.now().isoformat(), 'RA': f'{coord.ra.deg:.8f}', 'Dec': f'{coord.dec.deg:.8f}', 'Object ID': obj.get('Object ID', 'Unknown'), 'Catalog': obj.get('Catalog', ''), 'Redshift': obj.get('Redshift', np.nan), 'Survey': selected_name(), 'Notes': notes.value}
    pd.DataFrame([row]).to_csv(CATALOG_PATH, mode='a', header=not CATALOG_PATH.exists(), index=False)
    set_status('Saved', f'Saved to {esc(CATALOG_PATH)}', '#4caf50')
    display(FileLink(str(CATALOG_PATH)))


def export_csv(_=None):
    if not CATALOG_PATH.exists():
        pd.DataFrame(columns=['Date', 'RA', 'Dec', 'Object ID', 'Catalog', 'Redshift', 'Survey', 'Notes']).to_csv(CATALOG_PATH, index=False)
    display(FileLink(str(CATALOG_PATH)))

find_button.on_click(find_object)
copy_target_button.on_click(copy_target)
save_button.on_click(save_galaxy)
export_button.on_click(export_csv)

inspector = widgets.VBox([
    widgets.HTML('<div style="background:#050505;color:#ffffff;padding:14px 16px;border-radius:9px;margin-top:12px;font-family:Arial"><h2 style="margin:0">GALAXY INSPECTOR — INCLUSIVE SURVEY SEARCH</h2><div style="color:#ddd;margin-top:6px">Paste one ICRS coordinate string. The search queries broad catalog stacks and survey-family catalog discovery.</div></div>'),
    coord_input,
    widgets.HBox([find_button, copy_target_button, save_button, export_button]),
    status,
    notes,
    results,
    nearby_panel,
    archives,
], layout=widgets.Layout(width='100%'))

display(widgets.VBox([header, controls, note, viewer, inspector], layout=widgets.Layout(width='100%')))
print(VERSION)
