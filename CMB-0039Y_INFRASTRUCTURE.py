# CMB-0039Y_INFRASTRUCTURE.py
from __future__ import annotations

import html
import re
import urllib.parse
import subprocess
import sys
import contextlib
import io
from pathlib import Path

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    try:
        import astroquery  # noqa: F401
    except Exception:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', 'astroquery'])

import numpy as np
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, FileLink, clear_output
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.cosmology import Planck18
from astroquery.ipac.ned import Ned
from astroquery.simbad import Simbad

VERSION = 'CMB-0039Y'
DEFAULT_TARGET = '03 32 39.99 -27 48 00.0'
DEFAULT_FOV = 0.08
DEFAULT_SURVEY = 'CDS/P/HST/EPO'  # Hubble Outreach color
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
      <iframe src="{html.escape(url)}"
        style="width:100%;height:820px;border:0;display:block;background:#000;overflow:visible;"
        allow="fullscreen; clipboard-read; clipboard-write"
        allowfullscreen>
      </iframe>
    </div>
    '''

def parse_icrs_single_cell(value):
    value = str(value).strip()
    if not value:
        raise ValueError('Paste one ICRS coordinate pair, for example: 53.166625 -27.800000')

    cleaned = value.replace(',', ' ')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Decimal degrees: RA Dec
    parts = cleaned.split(' ')
    if len(parts) == 2:
        try:
            ra = float(parts[0])
            dec = float(parts[1])
            return SkyCoord(ra * u.deg, dec * u.deg, frame='icrs')
        except Exception:
            pass

    # Sexagesimal compact: HH MM SS +/-DD MM SS
    if len(parts) == 6:
        try:
            ra_s = ':'.join(parts[0:3])
            dec_s = ':'.join(parts[3:6])
            return SkyCoord(ra_s, dec_s, unit=(u.hourangle, u.deg), frame='icrs')
        except Exception:
            pass

    # Sexagesimal with colons: HH:MM:SS +/-DD:MM:SS
    try:
        return SkyCoord(cleaned, unit=(u.hourangle, u.deg), frame='icrs')
    except Exception as exc:
        raise ValueError('Could not parse one-cell ICRS coordinates. Use decimal degrees like 53.166625 -27.800000 or sexagesimal like 03:32:39.99 -27:48:00.0') from exc

def safe_float(value):
    try:
        if value is None or np.ma.is_masked(value):
            return np.nan
        return float(value)
    except Exception:
        return np.nan

def first_value(row, names, default=np.nan):
    cols = set(getattr(row, 'colnames', []) or getattr(row, 'index', []))
    for name in names:
        if name in cols and not np.ma.is_masked(row[name]):
            return row[name]
    return default

def nearest_ned(coord, radius_arcmin=2.0):
    try:
        Ned.TIMEOUT = 30
        table = Ned.query_region(coord, radius=radius_arcmin * u.arcmin)
    except Exception as exc:
        STATE['warnings'].append(f'NED unavailable: {exc}')
        return None, pd.DataFrame()
    rows = []
    if table is not None:
        for row in table:
            ra = safe_float(first_value(row, ['RA', 'RA(deg)']))
            dec = safe_float(first_value(row, ['DEC', 'DEC(deg)']))
            if not np.isfinite(ra) or not np.isfinite(dec):
                continue
            obj_coord = SkyCoord(ra * u.deg, dec * u.deg, frame='icrs')
            rows.append({
                'Object ID': str(first_value(row, ['Object Name', 'Object_Name', 'MAIN_ID'], 'Unknown')),
                'Catalog': 'NED',
                'RA': ra,
                'Dec': dec,
                'Angular separation (arcsec)': coord.separation(obj_coord).arcsec,
                'Redshift': safe_float(first_value(row, ['Redshift', 'z'])),
                'Type': str(first_value(row, ['Type', 'Object Type'], '')),
            })
    if not rows:
        return None, pd.DataFrame()
    frame = pd.DataFrame(rows).sort_values('Angular separation (arcsec)').reset_index(drop=True)
    return frame.iloc[0].to_dict(), frame

def nearest_simbad(coord, radius_arcmin=2.0):
    try:
        Simbad.TIMEOUT = 30
        service = Simbad()
        service.add_votable_fields('otype', 'z_value', 'diameter')
        table = service.query_region(coord, radius=radius_arcmin * u.arcmin)
    except Exception as exc:
        STATE['warnings'].append(f'SIMBAD unavailable: {exc}')
        return None, pd.DataFrame()
    rows = []
    if table is not None:
        for row in table:
            try:
                obj_coord = SkyCoord(str(row['RA']), str(row['DEC']), unit=(u.hourangle, u.deg), frame='icrs')
            except Exception:
                continue
            rows.append({
                'Object ID': str(row['MAIN_ID']),
                'Catalog': 'SIMBAD',
                'RA': obj_coord.ra.deg,
                'Dec': obj_coord.dec.deg,
                'Angular separation (arcsec)': coord.separation(obj_coord).arcsec,
                'Redshift': safe_float(row['Z_VALUE']) if 'Z_VALUE' in table.colnames else np.nan,
                'Type': str(row['OTYPE']) if 'OTYPE' in table.colnames else '',
                'Angular size (arcsec)': safe_float(row['GALDIM_MAJAXIS']) if 'GALDIM_MAJAXIS' in table.colnames else np.nan,
            })
    if not rows:
        return None, pd.DataFrame()
    frame = pd.DataFrame(rows).sort_values('Angular separation (arcsec)').reset_index(drop=True)
    return frame.iloc[0].to_dict(), frame

def fmt(value, digits=4):
    number = safe_float(value)
    return 'Not available' if not np.isfinite(number) else f'{number:,.{digits}f}'

def enrich_object(obj):
    redshift = safe_float(obj.get('Redshift'))
    angular_size = safe_float(obj.get('Angular size (arcsec)'))
    obj.setdefault('Angular size (arcsec)', angular_size)
    obj.setdefault('Morphology', obj.get('Type', 'Not available'))
    obj['Redshift type'] = 'Catalog value; spectroscopic/photometric flag unavailable'
    if np.isfinite(redshift) and redshift > 0:
        scale = Planck18.kpc_proper_per_arcmin(redshift).to_value(u.kpc / u.arcmin) / 60.0 * 3261.563777
        obj.update({
            'Light-travel time (Gyr)': Planck18.lookback_time(redshift).to_value(u.Gyr),
            'Comoving distance (Gly)': Planck18.comoving_distance(redshift).to_value(u.Glyr),
            'Luminosity distance (Gly)': Planck18.luminosity_distance(redshift).to_value(u.Glyr),
            'Angular diameter distance (Gly)': Planck18.angular_diameter_distance(redshift).to_value(u.Glyr),
            'Universe age at emission (Gyr)': Planck18.age(redshift).to_value(u.Gyr),
            'Scale (ly/arcsec)': scale,
            'Estimated physical diameter (ly)': angular_size * scale if np.isfinite(angular_size) else np.nan,
        })
    return obj

def table_html(obj):
    keys = ['Object ID', 'Catalog', 'RA', 'Dec', 'Angular separation (arcsec)', 'Redshift', 'Redshift type',
            'Light-travel time (Gyr)', 'Comoving distance (Gly)', 'Luminosity distance (Gly)',
            'Angular diameter distance (Gly)', 'Universe age at emission (Gyr)', 'Angular size (arcsec)',
            'Estimated physical diameter (ly)', 'Morphology', 'Type']
    rows = []
    for key in keys:
        value = obj.get(key, 'Not available')
        if isinstance(value, (float, np.floating)):
            value = fmt(value)
        rows.append(f'<tr><th style="text-align:left;padding:5px 9px;background:#eef3f8">{html.escape(key)}</th><td style="padding:5px 9px">{html.escape(str(value))}</td></tr>')
    return '<table style="border-collapse:collapse;width:100%;font:13px sans-serif" border="1">' + ''.join(rows) + '</table>'

def archive_links(coord):
    position = f'{coord.ra.deg:.7f},{coord.dec.deg:.7f}'
    return {
        'NED coordinate search': 'https://ned.ipac.caltech.edu/conesearch?search_type=Near+Position+Search&coordinates=' + urllib.parse.quote(position),
        'Hubble / JWST / MAST': 'https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html?searchQuery=' + urllib.parse.quote(position),
        'Spitzer / IRSA': 'https://irsa.ipac.caltech.edu/applications/finderchart/?locstr=' + urllib.parse.quote(position),
        'NASA ADS coordinate search': 'https://ui.adsabs.harvard.edu/search/q=' + urllib.parse.quote(f'pos({coord.ra.deg:.7f},{coord.dec.deg:.7f})'),
        'ALMA': 'https://almascience.eso.org/aq/?result_view=observation',
    }

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
note = widgets.HTML(value='<div style="padding:9px 12px;border-left:4px solid #ffb300;background:#fff8e1;font:13px sans-serif"><b>Coverage note:</b> Hubble and JWST are pointed-observation archives, so blank fields may mean no coverage. Aladin iframe coordinates must be copied manually into the single ICRS cell below.</div>')
viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, DEFAULT_SURVEY))

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

icrs_input = widgets.Text(
    value='',
    description='ICRS RA Dec:',
    placeholder='Paste one coordinate pair, e.g. 53.166625 -27.800000 or 03:32:39.99 -27:48:00.0',
    layout=widgets.Layout(width='920px'),
)
find_button = widgets.Button(description='Find galaxy from ICRS coordinates', button_style='success', icon='search')
use_target_button = widgets.Button(description='Copy loaded target into ICRS cell', icon='copy')
save_button = widgets.Button(description='Save Galaxy', icon='save')
export_button = widgets.Button(description='Export CSV', icon='download')
notes = widgets.Textarea(description='Notes:', placeholder='Free-text notes', layout=widgets.Layout(width='100%', height='90px'))
status = widgets.HTML()
coord_summary = widgets.HTML()
object_output = widgets.Output()
nearby_output = widgets.Output()
coverage_output = widgets.Output()
cosmology_output = widgets.HTML()

def set_coord_summary(coord):
    STATE['coord'] = coord
    coord_summary.value = f'''
    <div style="padding:8px 10px;background:#eef7ff;border-left:4px solid #1976d2;font:13px sans-serif">
      Parsed ICRS: <b>{coord.ra.deg:.8f} {coord.dec.deg:.8f}</b><br>
      Sexagesimal: <b>{coord.ra.to_string(unit=u.hour, sep=':', precision=3)}</b> <b>{coord.dec.to_string(unit=u.deg, sep=':', precision=3, alwayssign=True)}</b>
    </div>
    '''

def copy_loaded_target(_=None):
    try:
        coord = parse_icrs_single_cell(target.value)
    except Exception:
        try:
            coord = SkyCoord(target.value, unit=(u.hourangle, u.deg), frame='icrs')
        except Exception as exc:
            status.value = f'<b style="color:#b71c1c">Could not parse loaded target: {html.escape(str(exc))}</b>'
            return
    icrs_input.value = f'{coord.ra.deg:.8f} {coord.dec.deg:.8f}'
    set_coord_summary(coord)
    status.value = '<b style="color:#1565c0">Loaded target copied into the single ICRS cell.</b>'

def find_galaxy(_=None):
    find_button.disabled = True
    STATE['object'] = None
    STATE['nearby'] = pd.DataFrame()
    STATE['warnings'] = []
    with object_output:
        clear_output()
    with nearby_output:
        clear_output()
    with coverage_output:
        clear_output()
    cosmology_output.value = ''
    try:
        coord = parse_icrs_single_cell(icrs_input.value)
        set_coord_summary(coord)
        status.value = '<b>Parsed coordinates. Querying NED first, then SIMBAD if needed…</b>'
        radius = max(2.0, float(fov.value) * 30.0)
        obj, nearby = nearest_ned(coord, radius)
        if obj is None:
            obj, nearby = nearest_simbad(coord, radius)
        if obj is None:
            warning_text = ' | '.join(STATE['warnings']) or 'No catalog object found.'
            with coverage_output:
                clear_output()
                display(widgets.HTML('<h3>Coordinate links</h3>'))
                for label, url in archive_links(coord).items():
                    display(widgets.HTML(f'<a target="_blank" href="{html.escape(url)}">{html.escape(label)}</a><br>'))
            status.value = f'<b style="color:#b71c1c">No catalog object found near those coordinates.</b><br><span style="color:#6d4c41">{html.escape(warning_text)}</span>'
            return
        obj = enrich_object(obj)
        STATE['object'] = obj
        STATE['nearby'] = nearby.head(25)
        with object_output:
            clear_output()
            display(widgets.HTML('<h3>Nearest catalog object</h3>' + table_html(obj)))
        with nearby_output:
            clear_output()
            display(widgets.HTML('<h3>Nearby catalog objects</h3>'))
            cols = [name for name in ['Object ID', 'Catalog', 'Angular separation (arcsec)', 'Redshift', 'Type'] if name in nearby.columns]
            display(nearby[cols].head(25).style.format(precision=5))
        with coverage_output:
            clear_output()
            display(widgets.HTML('<h3>Coordinate links</h3>'))
            for label, url in archive_links(coord).items():
                display(widgets.HTML(f'<a target="_blank" href="{html.escape(url)}">{html.escape(label)}</a><br>'))
        if np.isfinite(safe_float(obj.get('Redshift'))) and safe_float(obj.get('Redshift')) > 0:
            cosmology_output.value = f'''
            <div style="padding:14px;border-radius:10px;background:#071a2b;color:white;font-family:sans-serif;line-height:1.8">
              <b style="font-size:18px">COSMOLOGY PANEL</b><br>
              Light-travel time: <b>{fmt(obj.get('Light-travel time (Gyr)'),3)} billion years</b><br>
              Comoving distance: <b>{fmt(obj.get('Comoving distance (Gly)'),3)} billion light-years</b><br>
              Universe age at emission: <b>{fmt(obj.get('Universe age at emission (Gyr)'),3)} billion years</b><br>
              Scale: <b>1 arcsecond = {fmt(obj.get('Scale (ly/arcsec)'),0)} light-years</b>
            </div>
            '''
        warning_html = ''
        if STATE['warnings']:
            warning_html = '<br><span style="color:#ef6c00">' + html.escape(' | '.join(STATE['warnings'])) + '</span>'
        status.value = f'<b style="color:#1b5e20">Galaxy search complete: {html.escape(str(obj.get("Object ID", "Unknown")))} via {html.escape(str(obj.get("Catalog", "Catalog")))}</b>{warning_html}'
    except Exception as exc:
        status.value = f'<b style="color:#b71c1c">Find galaxy failed: {html.escape(str(exc))}</b>'
    finally:
        find_button.disabled = False

def save_galaxy(_=None):
    obj = STATE.get('object')
    coord = STATE.get('coord')
    if obj is None or coord is None:
        status.value = '<b style="color:#b71c1c">Find a galaxy before saving.</b>'
        return
    row = {'Date': pd.Timestamp.now().isoformat(), 'RA': f'{coord.ra.deg:.8f}', 'Dec': f'{coord.dec.deg:.8f}', 'Object ID': obj.get('Object ID', 'Unknown'), 'Redshift': obj.get('Redshift', np.nan), 'Distance': obj.get('Comoving distance (Gly)', np.nan), 'Survey': selected_name(), 'Notes': notes.value}
    pd.DataFrame([row]).to_csv(CATALOG_PATH, mode='a', header=not CATALOG_PATH.exists(), index=False)
    status.value = f'<b style="color:#1b5e20">Saved: {CATALOG_PATH}</b>'
    display(FileLink(str(CATALOG_PATH)))

def export_csv(_=None):
    if not CATALOG_PATH.exists():
        pd.DataFrame(columns=['Date', 'RA', 'Dec', 'Object ID', 'Redshift', 'Distance', 'Survey', 'Notes']).to_csv(CATALOG_PATH, index=False)
    display(FileLink(str(CATALOG_PATH)))

find_button.on_click(find_galaxy)
use_target_button.on_click(copy_loaded_target)
save_button.on_click(save_galaxy)
export_button.on_click(export_csv)

inspector = widgets.VBox([
    widgets.HTML('<h2 style="margin:12px 0 4px">GALAXY INSPECTOR — ONE-CELL ICRS SEARCH</h2>'),
    widgets.HTML('<div style="font:13px sans-serif;padding:8px 10px;background:#fffde7;border-left:4px solid #f9a825">Copy coordinates from Aladin and paste them into the single cell below. Do not split RA and Dec.</div>'),
    widgets.HBox([icrs_input]),
    widgets.HBox([find_button, use_target_button, save_button, export_button]),
    coord_summary,
    notes,
    status,
    object_output,
    cosmology_output,
    nearby_output,
    coverage_output,
], layout=widgets.Layout(width='100%'))

display(widgets.VBox([header, controls, note, viewer, inspector], layout=widgets.Layout(width='100%')))
