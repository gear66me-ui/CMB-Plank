# CMB-0040_INFRASTRUCTURE.py
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

VERSION = 'CMB-0040'
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
        raise ValueError('Paste one ICRS coordinate string first, for example: 03 32 34.54 -27 48 48.5')
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
    cols = set(getattr(row, 'colnames', []) or getattr(row, 'index', []))
    for name in names:
        if name in cols and not np.ma.is_masked(row[name]):
            return row[name]
    return default


def coord_from_row(row, table=None):
    names = list(getattr(row, 'colnames', []) or getattr(row, 'index', []))
    lower = {name.lower(): name for name in names}
    ra_keys = ['ra', 'raj2000', 'ra_icrs', '_raj2000', 'alpha', 'ra2000']
    de_keys = ['dec', 'dej2000', 'dec_icrs', '_dej2000', 'delta', 'de2000']
    ra_name = next((lower[k] for k in ra_keys if k in lower), None)
    de_name = next((lower[k] for k in de_keys if k in lower), None)
    if ra_name and de_name:
        ra_val = row[ra_name]
        de_val = row[de_name]
        ra = safe_float(ra_val)
        de = safe_float(de_val)
        if np.isfinite(ra + de):
            return SkyCoord(ra * u.deg, de * u.deg)
        try:
            return SkyCoord(str(ra_val), str(de_val), unit=(u.hourangle, u.deg), frame='icrs')
        except Exception:
            return None
    return None


def object_name_from_row(row):
    names = list(getattr(row, 'colnames', []) or getattr(row, 'index', []))
    preferred = ['Object Name', 'Object_Name', 'MAIN_ID', 'Name', 'ID', 'ID_MAIN', 'Source', 'SourceID', 'objID', 'ObjID', 'designation', 'Designation', 'IAUName']
    for key in preferred:
        if key in names and not np.ma.is_masked(row[key]):
            text = str(row[key]).strip()
            if text:
                return text
    for key in names[:8]:
        if not np.ma.is_masked(row[key]):
            text = str(row[key]).strip()
            if text and len(text) < 80:
                return text
    return 'Catalog row'


def rows_to_dark_table(rows, max_rows=30):
    if not rows:
        return dark_box('No rows', 'No catalog rows were returned.', '#777')
    rows = sorted(rows, key=lambda r: r.get('Angular separation (arcsec)', 999999))[:max_rows]
    head = ''.join(f'<th style="padding:6px 8px;border:1px solid #333;background:#111;color:#fff;text-align:left">{esc(h)}</th>' for h in ['Catalog', 'Object ID', 'RA', 'Dec', 'Sep arcsec', 'Redshift', 'Type'])
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


def nearest_ned(coord, radius_arcsec):
    try:
        Ned.TIMEOUT = 35
        table = Ned.query_region(coord, radius=radius_arcsec * u.arcsec)
    except Exception as exc:
        STATE['warnings'].append(f'NED unavailable: {exc}')
        return []
    rows = []
    if table is not None:
        for row in table[:50]:
            ra = safe_float(first_value(row, ['RA', 'RA(deg)']))
            dec = safe_float(first_value(row, ['DEC', 'DEC(deg)']))
            if not np.isfinite(ra + dec):
                continue
            c = SkyCoord(ra * u.deg, dec * u.deg)
            rows.append({
                'Object ID': str(first_value(row, ['Object Name', 'Object_Name', 'MAIN_ID'], 'NED object')),
                'Catalog': 'NED',
                'RA': ra,
                'Dec': dec,
                'Angular separation (arcsec)': coord.separation(c).arcsec,
                'Redshift': safe_float(first_value(row, ['Redshift', 'z'])),
                'Type': str(first_value(row, ['Type', 'Object Type'], '')),
            })
    return rows


def nearest_simbad(coord, radius_arcsec):
    try:
        Simbad.TIMEOUT = 35
        service = Simbad()
        service.add_votable_fields('otype', 'z_value', 'diameter')
        table = service.query_region(coord, radius=radius_arcsec * u.arcsec)
    except Exception as exc:
        STATE['warnings'].append(f'SIMBAD unavailable: {exc}')
        return []
    rows = []
    if table is not None:
        for row in table[:50]:
            try:
                c = SkyCoord(str(row['RA']), str(row['DEC']), unit=(u.hourangle, u.deg), frame='icrs')
            except Exception:
                continue
            rows.append({
                'Object ID': str(row['MAIN_ID']),
                'Catalog': 'SIMBAD',
                'RA': c.ra.deg,
                'Dec': c.dec.deg,
                'Angular separation (arcsec)': coord.separation(c).arcsec,
                'Redshift': safe_float(row['Z_VALUE']) if 'Z_VALUE' in table.colnames else np.nan,
                'Type': str(row['OTYPE']) if 'OTYPE' in table.colnames else '',
                'Angular size (arcsec)': safe_float(row['GALDIM_MAJAXIS']) if 'GALDIM_MAJAXIS' in table.colnames else np.nan,
            })
    return rows


def nearest_vizier(coord, radius_arcsec):
    rows = []
    radius = radius_arcsec * u.arcsec
    catalog_batches = [
        None,
        ['I/355/gaiadr3', 'II/246/out', 'II/328/allwise', 'II/312/ais', 'II/335/galex_ais'],
        ['J/ApJS/207/24', 'J/ApJS/206/8', 'J/ApJS/214/24', 'J/ApJ/754/83'],
        ['J/ApJS/229/32', 'J/ApJS/258/11', 'J/AJ/151/134', 'J/ApJ/837/97'],
    ]
    seen = set()
    for cats in catalog_batches:
        try:
            v = Vizier(columns=['*', '+_r'], row_limit=80)
            v.TIMEOUT = 35
            result = v.query_region(coord, radius=radius, catalog=cats) if cats else v.query_region(coord, radius=radius)
        except Exception as exc:
            label = 'all VizieR catalogs' if cats is None else ', '.join(cats)
            STATE['warnings'].append(f'VizieR unavailable for {label}: {exc}')
            continue
        for table in result:
            meta = getattr(table, 'meta', {}) or {}
            cat = meta.get('name') or meta.get('ID') or getattr(table, 'name', 'VizieR') or 'VizieR'
            description = meta.get('description', '')
            for row in table[:50]:
                c = coord_from_row(row, table)
                sep = safe_float(row['_r']) if '_r' in getattr(table, 'colnames', []) else np.nan
                if c is not None:
                    sep = coord.separation(c).arcsec
                    ra = c.ra.deg
                    dec = c.dec.deg
                else:
                    ra = np.nan
                    dec = np.nan
                obj_id = object_name_from_row(row)
                key = (str(cat), obj_id, round(sep if np.isfinite(sep) else 999999, 3))
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    'Object ID': obj_id,
                    'Catalog': f'VizieR {cat}',
                    'RA': ra,
                    'Dec': dec,
                    'Angular separation (arcsec)': sep,
                    'Redshift': safe_float(first_value(row, ['z', 'Z', 'redshift', 'zphot', 'zspec'])),
                    'Type': description[:70] if description else '',
                })
        if rows and cats is None:
            break
    return rows


def object_details(obj):
    redshift = safe_float(obj.get('Redshift'))
    angular_size = safe_float(obj.get('Angular size (arcsec)'))
    out = {
        'Redshift type': 'Catalog value if available; source flags vary by catalog',
        'Stellar mass': np.nan,
        'Star formation rate': np.nan,
        'Morphology': obj.get('Type', 'Not available'),
        'Angular size (arcsec)': angular_size,
    }
    if np.isfinite(redshift) and redshift > 0:
        scale = Planck18.kpc_proper_per_arcmin(redshift).to_value(u.kpc / u.arcmin) / 60.0 * 3261.563777
        out.update({
            'Light-travel time (Gyr)': Planck18.lookback_time(redshift).to_value(u.Gyr),
            'Comoving distance (Gly)': Planck18.comoving_distance(redshift).to_value(u.Glyr),
            'Luminosity distance (Gly)': Planck18.luminosity_distance(redshift).to_value(u.Glyr),
            'Angular diameter distance (Gly)': Planck18.angular_diameter_distance(redshift).to_value(u.Glyr),
            'Universe age at emission (Gyr)': Planck18.age(redshift).to_value(u.Gyr),
            'Scale (ly/arcsec)': scale,
            'Estimated physical diameter (ly)': angular_size * scale if np.isfinite(angular_size) else np.nan,
        })
    return out


def fmt(value, digits=4):
    number = safe_float(value)
    return 'Not available' if not np.isfinite(number) else f'{number:,.{digits}f}'


def details_panel(obj):
    obj = dict(obj)
    obj.update(object_details(obj))
    keys = ['Object ID', 'Catalog', 'RA', 'Dec', 'Angular separation (arcsec)', 'Redshift', 'Redshift type',
            'Light-travel time (Gyr)', 'Comoving distance (Gly)', 'Luminosity distance (Gly)',
            'Angular diameter distance (Gly)', 'Universe age at emission (Gyr)', 'Angular size (arcsec)',
            'Estimated physical diameter (ly)', 'Morphology', 'Type']
    body = '<table style="border-collapse:collapse;width:100%;font:13px Arial,Helvetica,sans-serif">'
    for key in keys:
        value = obj.get(key, 'Not available')
        if isinstance(value, (float, np.floating)):
            value = fmt(value)
        body += f'<tr><th style="text-align:left;padding:6px 8px;background:#111;color:#fff;border:1px solid #333;width:32%">{esc(key)}</th><td style="padding:6px 8px;background:#050505;color:#eee;border:1px solid #333">{esc(value)}</td></tr>'
    body += '</table>'
    return dark_box('Nearest matched catalog row', body, '#4caf50')


def archive_links(coord):
    position = f'{coord.ra.deg:.7f},{coord.dec.deg:.7f}'
    links = {
        'CDS / VizieR cone-search portal': 'https://vizier.cds.unistra.fr/viz-bin/VizieR-4?-c=' + urllib.parse.quote(position),
        'SIMBAD position search': 'https://simbad.u-strasbg.fr/simbad/sim-coo?Coord=' + urllib.parse.quote(position) + '&Radius=30&Radius.unit=arcsec',
        'NED position search': 'https://ned.ipac.caltech.edu/conesearch?in_csys=Equatorial&in_equinox=J2000.0&lon=' + urllib.parse.quote(f'{coord.ra.deg:.7f}') + '&lat=' + urllib.parse.quote(f'{coord.dec.deg:.7f}') + '&radius=0.01',
        'Hubble / JWST / MAST': 'https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html?searchQuery=' + urllib.parse.quote(position),
        'Spitzer / IRSA': 'https://irsa.ipac.caltech.edu/applications/finderchart/?locstr=' + urllib.parse.quote(position),
        'ALMA': 'https://almascience.eso.org/aq/?result_view=observation',
        'NASA ADS coordinate/text search': 'https://ui.adsabs.harvard.edu/search/q=' + urllib.parse.quote(position),
    }
    body = ''.join(f'<a style="color:#90caf9" target="_blank" href="{esc(url)}">{esc(label)}</a><br>' for label, url in links.items())
    return dark_box('External archive searches', body, '#2196f3')


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
viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, DEFAULT_SURVEY))
note = widgets.HTML(value=dark_box('Coverage note', 'Hubble and JWST are pointed-observation archives, so blank fields may mean no coverage.', '#ffc107'))


def reload_map(_=None):
    viewer.value = viewer_html(target.value, fov.value, survey.value)


def open_full(_=None):
    display(widgets.HTML(value=f"<script>window.open({aladin_url(target.value, fov.value, survey.value)!r},'_blank');</script>"))


load_button.on_click(reload_map)
open_button.on_click(open_full)
controls = widgets.VBox([
    widgets.HBox([target]),
    widgets.HBox([survey]),
    widgets.HBox([fov, load_button, open_button]),
])

coord_input = widgets.Text(
    value='',
    description='ICRS RA Dec:',
    placeholder='Paste one coordinate string: 03 32 34.54 -27 48 48.5   OR   53.14391667 -27.81347222',
    layout=widgets.Layout(width='100%')
)
find_button = widgets.Button(description='Find galaxy from ICRS coordinates', button_style='success', icon='search', layout=widgets.Layout(width='330px'))
copy_target_button = widgets.Button(description='Copy loaded target into ICRS cell', icon='copy', layout=widgets.Layout(width='300px'))
save_button = widgets.Button(description='Save Galaxy', icon='save', layout=widgets.Layout(width='190px'))
export_button = widgets.Button(description='Export CSV', icon='download', layout=widgets.Layout(width='190px'))
notes = widgets.Textarea(description='Notes:', placeholder='Free-text notes', layout=widgets.Layout(width='100%', height='90px'))
status = widgets.HTML(value=dark_box('Ready', 'Paste ICRS coordinates into the single cell, then press Find galaxy from ICRS coordinates.', '#777'))
results = widgets.HTML(value='')
nearby_panel = widgets.HTML(value='')
archives = widgets.HTML(value='')


def set_status(title, body, border='#777'):
    status.value = dark_box(title, body, border)


def copy_target(_=None):
    try:
        coord = parse_target(target.value)
        coord_input.value = f'{coord.ra.to_string(unit=u.hour, sep=" ", precision=2)} {coord.dec.to_string(unit=u.deg, sep=" ", precision=1, alwayssign=True)}'
        set_status('Target copied', f'Copied loaded target into the one-cell ICRS input:<br><b>{esc(coord_input.value)}</b>', '#2196f3')
    except Exception as exc:
        set_status('Copy failed', esc(exc), '#f44336')


def find_galaxy(_=None):
    find_button.disabled = True
    STATE['warnings'] = []
    results.value = ''
    nearby_panel.value = ''
    archives.value = ''
    try:
        coord = parse_target(coord_input.value)
        STATE['coord'] = coord
        parsed = f'Parsed ICRS decimal: <b>{coord.ra.deg:.8f} {coord.dec.deg:.8f}</b><br>Sexagesimal: <b>{coord.ra.to_string(unit=u.hour, sep=":", precision=3)} {coord.dec.to_string(unit=u.deg, sep=":", precision=3, alwayssign=True)}</b>'
        set_status('Searching inclusive catalog stack', parsed + '<br>Trying NED, SIMBAD, and broad CDS/VizieR cone searches…', '#2196f3')
        radius_arcsec = max(30.0, float(fov.value) * 3600.0 / 6.0)
        all_rows = []
        all_rows.extend(nearest_ned(coord, radius_arcsec))
        all_rows.extend(nearest_simbad(coord, radius_arcsec))
        all_rows.extend(nearest_vizier(coord, radius_arcsec))
        all_rows = [r for r in all_rows if np.isfinite(safe_float(r.get('Angular separation (arcsec'))) or np.nan) or r.get('Catalog')]
        if not all_rows:
            warning_text = '<br>'.join(esc(w) for w in STATE['warnings']) or 'No catalog service returned a row.'
            raise RuntimeError('No catalog rows found in NED, SIMBAD, or VizieR/CDS for this cone.<br>' + warning_text)
        all_rows = sorted(all_rows, key=lambda r: safe_float(r.get('Angular separation (arcsec)')) if np.isfinite(safe_float(r.get('Angular separation (arcsec)'))) else 999999)
        best = all_rows[0]
        STATE['object'] = best
        STATE['nearby'] = pd.DataFrame(all_rows[:80])
        results.value = details_panel(best)
        nearby_panel.value = dark_box('Inclusive catalog matches', rows_to_dark_table(all_rows, max_rows=35), '#8bc34a')
        archives.value = archive_links(coord)
        warn = ''
        if STATE['warnings']:
            warn = '<br><br><span style="color:#ffb74d">' + '<br>'.join(esc(w) for w in STATE['warnings'][:6]) + '</span>'
        set_status('Search complete', f'Found <b>{len(all_rows)}</b> candidate catalog rows within about <b>{radius_arcsec:.1f} arcsec</b>. Best row: <b>{esc(best.get("Object ID"))}</b> from <b>{esc(best.get("Catalog"))}</b>.' + warn, '#4caf50')
    except Exception as exc:
        set_status('Find galaxy failed', str(exc), '#f44336')
    finally:
        find_button.disabled = False


def save_galaxy(_=None):
    obj = STATE.get('object')
    coord = STATE.get('coord')
    if obj is None or coord is None:
        set_status('Save failed', 'Find a galaxy before saving.', '#f44336')
        return
    row = {
        'Date': pd.Timestamp.now().isoformat(),
        'RA': f'{coord.ra.deg:.8f}',
        'Dec': f'{coord.dec.deg:.8f}',
        'Object ID': obj.get('Object ID', 'Unknown'),
        'Catalog': obj.get('Catalog', ''),
        'Redshift': obj.get('Redshift', np.nan),
        'Distance Gly': object_details(obj).get('Comoving distance (Gly)', np.nan),
        'Survey': selected_name(),
        'Notes': notes.value,
    }
    pd.DataFrame([row]).to_csv(CATALOG_PATH, mode='a', header=not CATALOG_PATH.exists(), index=False)
    set_status('Saved', f'Saved row to <b>{esc(CATALOG_PATH)}</b>', '#4caf50')
    display(FileLink(str(CATALOG_PATH)))


def export_csv(_=None):
    if not CATALOG_PATH.exists():
        pd.DataFrame(columns=['Date', 'RA', 'Dec', 'Object ID', 'Catalog', 'Redshift', 'Distance Gly', 'Survey', 'Notes']).to_csv(CATALOG_PATH, index=False)
    display(FileLink(str(CATALOG_PATH)))


find_button.on_click(find_galaxy)
copy_target_button.on_click(copy_target)
save_button.on_click(save_galaxy)
export_button.on_click(export_csv)

inspector = widgets.VBox([
    widgets.HTML('<div style="background:#050505;color:#fff;padding:14px 0 4px 0;font-family:Arial,Helvetica,sans-serif"><h2 style="margin:0">GALAXY INSPECTOR — INCLUSIVE MULTI-CATALOG ICRS SEARCH</h2></div>'),
    widgets.HTML(value=dark_box('', 'Copy coordinates from Aladin and paste them into the single cell below. Do not split RA and Dec. The search now tries NED, SIMBAD, and broad CDS/VizieR catalog cone searches.', '#ff9800')),
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
