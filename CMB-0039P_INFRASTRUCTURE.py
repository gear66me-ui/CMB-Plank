# CMB-0039P_INFRASTRUCTURE.py
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
from IPython.display import display, HTML, FileLink, clear_output
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.cosmology import Planck18
from astroquery.ipac.ned import Ned
from astroquery.simbad import Simbad

VERSION = 'CMB-0039P'
DEFAULT_TARGET = '03 32 39.99 -27 48 00.0'
DEFAULT_FOV = 0.08
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

def viewer_html(target_text, fov_deg, survey_id, survey_name):
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

def parse_target(value):
    value = str(value).strip()
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

def nearest_ned(coord, radius_arcmin=2):
    try:
        Ned.TIMEOUT = 20
        table = Ned.query_region(coord, radius=radius_arcmin * u.arcmin)
    except Exception as exc:
        STATE['warnings'].append(f'NED unavailable: {exc}')
        return None, pd.DataFrame()
    rows = []
    if table is not None:
        for row in table:
            ra = safe_float(first_value(row, ['RA', 'RA(deg)']))
            dec = safe_float(first_value(row, ['DEC', 'DEC(deg)']))
            if not np.isfinite(ra + dec):
                continue
            obj_coord = SkyCoord(ra * u.deg, dec * u.deg)
            rows.append({
                'Object ID': str(first_value(row, ['Object Name', 'Object_Name', 'MAIN_ID'], 'Unknown')),
                'Catalog': 'NASA/IPAC Extragalactic Database (NED)',
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

def nearest_simbad(coord, radius_arcmin=2):
    try:
        Simbad.TIMEOUT = 25
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
                obj_coord = SkyCoord(str(row['RA']), str(row['DEC']), unit=(u.hourangle, u.deg))
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

def details(obj):
    redshift = safe_float(obj.get('Redshift'))
    angular_size = safe_float(obj.get('Angular size (arcsec)'))
    out = {
        'Redshift type': 'Catalog value; spectroscopic/photometric flag unavailable',
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

def table_html(obj):
    keys = ['Object ID', 'Catalog', 'RA', 'Dec', 'Redshift', 'Redshift type', 'Light-travel time (Gyr)',
            'Comoving distance (Gly)', 'Luminosity distance (Gly)', 'Angular diameter distance (Gly)',
            'Universe age at emission (Gyr)', 'Angular size (arcsec)', 'Estimated physical diameter (ly)',
            'Stellar mass', 'Star formation rate', 'Morphology', 'Type']
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
        'Hubble / JWST / MAST': 'https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html?searchQuery=' + urllib.parse.quote(position),
        'ALMA': 'https://almascience.eso.org/aq/?result_view=observation',
        'MUSE / ESO': 'https://archive.eso.org/scienceportal/home',
        'Spitzer / IRSA': 'https://irsa.ipac.caltech.edu/applications/finderchart/?locstr=' + urllib.parse.quote(position),
        'Chandra': 'https://cda.harvard.edu/chaser/',
        'Gaia': 'https://gea.esac.esa.int/archive/',
    }

def paper_links(obj, coord):
    query = obj.get('Object ID') or f'{coord.ra.deg:.6f} {coord.dec.deg:.6f}'
    return {
        'NASA ADS papers': 'https://ui.adsabs.harvard.edu/search/q=' + urllib.parse.quote(query),
        'arXiv papers': 'https://arxiv.org/search/?query=' + urllib.parse.quote(query) + '&searchtype=all',
        'NED references': 'https://ned.ipac.caltech.edu/byname?objname=' + urllib.parse.quote(query),
    }

header = widgets.HTML(value=f'''
<div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;font-family:sans-serif">
  <div style="font-size:22px;font-weight:700">INTERACTIVE MULTI-SURVEY SKY MAP — {VERSION}</div>
  <div style="font-size:13px;opacity:.9;margin-top:4px">Original Aladin touch map · drag to pan · pinch or use +/- to zoom · real HiPS survey imagery</div>
</div>
''')

target = widgets.Text(value=DEFAULT_TARGET, description='Target:', layout=widgets.Layout(width='520px'))
survey = widgets.Dropdown(options=SURVEYS, value='CDS/P/HST/GOODS/color', description='Survey:', layout=widgets.Layout(width='520px'))
fov = widgets.Dropdown(options=[('0.01° — very tight', .01), ('0.03°', .03), ('0.08° — HUDF/GOODS', .08), ('0.25°', .25), ('1°', 1.0), ('5°', 5.0), ('20°', 20.0)], value=DEFAULT_FOV, description='Field:', layout=widgets.Layout(width='300px'))
load_button = widgets.Button(description='Load Interactive Map', button_style='primary', icon='globe')
open_button = widgets.Button(description='Open Full Screen', icon='external-link')
note = widgets.HTML(value='<div style="padding:9px 12px;border-left:4px solid #ffb300;background:#fff8e1;font:13px sans-serif"><b>Coverage note:</b> Hubble and JWST are pointed-observation archives, so blank fields may mean no coverage.</div>')
viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, survey.value, 'Hubble GOODS color'))

def reload_map(_=None):
    viewer.value = viewer_html(target.value, fov.value, survey.value, selected_name())

def open_full(_=None):
    display(widgets.HTML(value=f"<script>window.open({aladin_url(target.value, fov.value, survey.value)!r},'_blank');</script>"))

load_button.on_click(reload_map)
open_button.on_click(open_full)
controls = widgets.VBox([
    widgets.HBox([target]),
    widgets.HBox([survey]),
    widgets.HBox([fov, load_button, open_button]),
])

coord_input = widgets.Text(value='', description='RA Dec:', placeholder='RA Dec in one cell', layout=widgets.Layout(width='620px'))
get_aladin_button = widgets.Button(description='Get coordinates from Aladin', button_style='info', icon='crosshairs')
refresh_button = widgets.Button(description='Refresh Coordinates', icon='refresh')
inspect_button = widgets.Button(description='Inspect Galaxy', button_style='success', icon='search')
save_button = widgets.Button(description='Save Galaxy', icon='save')
export_button = widgets.Button(description='Export CSV', icon='download')
coord_status = widgets.HTML(value='')
notes = widgets.Textarea(description='Notes:', placeholder='Free-text notes', layout=widgets.Layout(width='100%', height='90px'))
status = widgets.HTML()
object_output = widgets.Output()
nearby_output = widgets.Output()
coverage_output = widgets.Output()
publication_output = widgets.Output()
cosmology_output = widgets.HTML()

ra_display = widgets.Text(description='RA:', disabled=True, layout=widgets.Layout(width='360px'))
dec_display = widgets.Text(description='Dec:', disabled=True, layout=widgets.Layout(width='360px'))
fov_display = widgets.Text(description='Field:', disabled=True, layout=widgets.Layout(width='320px'))
survey_display = widgets.Text(description='Survey:', disabled=True, layout=widgets.Layout(width='500px'))

def _set_coord_fields(coord):
    coord_input.value = f'{coord.ra.deg:.8f} {coord.dec.deg:.8f}'
    ra_display.value = f'{coord.ra.deg:.8f}° ({coord.ra.to_string(unit=u.hour, sep=":", precision=3)})'
    dec_display.value = f'{coord.dec.deg:.8f}° ({coord.dec.to_string(unit=u.deg, sep=":", precision=3, alwayssign=True)})'
    fov_display.value = f'{float(fov.value):g}°'
    survey_display.value = selected_name()
    STATE['coord'] = coord

def get_coordinates_from_aladin(_=None):
    # The Colab iframe is cross-origin, so Python cannot read a panned Aladin center directly.
    # This restores the requested button and loads the current Aladin target/center into the single inspector cell.
    try:
        coord = parse_target(target.value)
        _set_coord_fields(coord)
        coord_status.value = '<b style="color:#1565c0">Coordinates loaded from current Aladin target into the single RA Dec cell.</b>'
    except Exception as exc:
        coord_status.value = f'<b style="color:#b71c1c">Coordinate fetch failed: {html.escape(str(exc))}</b>'

def refresh_coordinates(_=None):
    try:
        source = coord_input.value.strip() or target.value
        coord = parse_target(source)
        _set_coord_fields(coord)
        status.value = '<b style="color:#1565c0">Coordinates refreshed.</b>'
    except Exception as exc:
        STATE['coord'] = None
        status.value = f'<b style="color:#b71c1c">Coordinate error: {html.escape(str(exc))}</b>'

def inspect_galaxy(_=None):
    refresh_coordinates()
    coord = STATE.get('coord')
    if coord is None:
        return
    inspect_button.disabled = True
    STATE['warnings'] = []
    status.value = '<b>Querying NED, then SIMBAD if needed, and calculating Planck18 cosmology…</b>'
    try:
        radius = max(2.0, float(fov.value) * 30.0)
        obj, nearby = nearest_ned(coord, radius)
        if obj is None:
            obj, nearby = nearest_simbad(coord, radius)
        if obj is None:
            warning_text = ' | '.join(STATE['warnings']) or 'No catalog response.'
            raise RuntimeError(f'No catalog object found near the supplied coordinates. {warning_text}')
        obj.update(details(obj))
        STATE['object'] = obj
        STATE['nearby'] = nearby.head(25)
        with object_output:
            clear_output()
            display(widgets.HTML('<h3>Nearest catalog object</h3>' + table_html(obj)))
        with nearby_output:
            clear_output()
            display(widgets.HTML('<h3>Nearby galaxies / catalog objects</h3>'))
            cols = [name for name in ['Object ID', 'Angular separation (arcsec)', 'Redshift'] if name in nearby.columns]
            display(nearby[cols].head(25).style.format(precision=5))
        with coverage_output:
            clear_output()
            display(widgets.HTML('<h3>Available-observation searches</h3>'))
            for label, url in archive_links(coord).items():
                display(widgets.HTML(f'<a target="_blank" href="{html.escape(url)}">{html.escape(label)}</a><br>'))
        with publication_output:
            clear_output()
            display(widgets.HTML('<h3>Publications and survey references</h3>'))
            for label, url in paper_links(obj, coord).items():
                display(widgets.HTML(f'<a target="_blank" href="{html.escape(url)}">{html.escape(label)}</a><br>'))
        cosmology_output.value = f'''
        <div style="padding:14px;border-radius:10px;background:#071a2b;color:white;font-family:sans-serif;line-height:1.8">
          <b style="font-size:18px">COSMOLOGY PANEL</b><br>
          You are observing this galaxy as it was: <b>{fmt(obj.get('Light-travel time (Gyr)'),3)} billion years ago</b><br>
          Current comoving distance: <b>{fmt(obj.get('Comoving distance (Gly)'),3)} billion light-years</b><br>
          Universe age when light was emitted: <b>{fmt(obj.get('Universe age at emission (Gyr)'),3)} billion years</b><br>
          Scale: <b>1 arcsecond = {fmt(obj.get('Scale (ly/arcsec)'),0)} light-years</b><br>
          Estimated galaxy diameter: <b>{fmt(obj.get('Estimated physical diameter (ly)'),0)} light-years</b>
        </div>
        '''
        warning_html = ''
        if STATE['warnings']:
            warning_html = '<br><span style="color:#ef6c00">' + html.escape(' | '.join(STATE['warnings'])) + '</span>'
        status.value = f'<b style="color:#1b5e20">Inspection complete using {html.escape(obj["Catalog"])}: {html.escape(str(obj["Object ID"]))}</b>{warning_html}'
    except Exception as exc:
        status.value = f'<b style="color:#b71c1c">Inspection failed: {html.escape(str(exc))}</b>'
    finally:
        inspect_button.disabled = False

def save_galaxy(_=None):
    obj = STATE.get('object')
    coord = STATE.get('coord')
    if obj is None or coord is None:
        status.value = '<b style="color:#b71c1c">Inspect a galaxy before saving.</b>'
        return
    row = {'Date': pd.Timestamp.now().isoformat(), 'RA': f'{coord.ra.deg:.8f}', 'Dec': f'{coord.dec.deg:.8f}', 'Object ID': obj.get('Object ID', 'Unknown'), 'Redshift': obj.get('Redshift', np.nan), 'Distance': obj.get('Comoving distance (Gly)', np.nan), 'Survey': selected_name(), 'Notes': notes.value}
    pd.DataFrame([row]).to_csv(CATALOG_PATH, mode='a', header=not CATALOG_PATH.exists(), index=False)
    status.value = f'<b style="color:#1b5e20">Saved: {CATALOG_PATH}</b>'
    display(FileLink(str(CATALOG_PATH)))

def export_csv(_=None):
    if not CATALOG_PATH.exists():
        pd.DataFrame(columns=['Date', 'RA', 'Dec', 'Object ID', 'Redshift', 'Distance', 'Survey', 'Notes']).to_csv(CATALOG_PATH, index=False)
    display(FileLink(str(CATALOG_PATH)))

get_aladin_button.on_click(get_coordinates_from_aladin)
refresh_button.on_click(refresh_coordinates)
inspect_button.on_click(inspect_galaxy)
save_button.on_click(save_galaxy)
export_button.on_click(export_csv)
get_coordinates_from_aladin()

inspector = widgets.VBox([
    widgets.HTML('<h2 style="margin:12px 0 4px">GALAXY INSPECTOR</h2>'),
    widgets.HBox([coord_input, get_aladin_button]),
    coord_status,
    widgets.HBox([ra_display, dec_display]),
    widgets.HBox([fov_display, survey_display]),
    widgets.HBox([refresh_button, inspect_button, save_button, export_button]),
    notes,
    status,
    object_output,
    cosmology_output,
    nearby_output,
    coverage_output,
    publication_output,
], layout=widgets.Layout(width='100%'))

display(widgets.VBox([header, controls, note, viewer, inspector], layout=widgets.Layout(width='100%')))
