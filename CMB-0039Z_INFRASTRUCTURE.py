# CMB-0039Z_INFRASTRUCTURE.py
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
from IPython.display import display, FileLink
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.cosmology import Planck18
from astroquery.ipac.ned import Ned
from astroquery.simbad import Simbad

VERSION = 'CMB-0039Z'
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

DARK_PANEL = 'background:#05070b;color:#f4f7fb;border:1px solid #26364d;border-radius:8px;padding:12px 14px;font:14px sans-serif;line-height:1.6;'
DARK_NOTE = 'background:#05070b;color:#f4f7fb;border-left:5px solid #ffb300;border-radius:4px;padding:10px 12px;font:14px sans-serif;line-height:1.5;'
DARK_INFO = 'background:#07111f;color:#e8f2ff;border-left:5px solid #42a5f5;border-radius:4px;padding:10px 12px;font:14px sans-serif;line-height:1.5;'
DARK_OK = 'background:#071a10;color:#d9ffe6;border-left:5px solid #43a047;border-radius:4px;padding:10px 12px;font:14px sans-serif;line-height:1.5;'
DARK_ERR = 'background:#1d0707;color:#ffe1e1;border-left:5px solid #ef5350;border-radius:4px;padding:10px 12px;font:14px sans-serif;line-height:1.5;'


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


def safe_float(value):
    try:
        if value is None or np.ma.is_masked(value):
            return np.nan
        return float(value)
    except Exception:
        return np.nan


def parse_icrs_one_cell(value):
    value = str(value or '').strip()
    if not value:
        raise ValueError('Paste one ICRS coordinate string into the cell, for example: 03 32 39.21 -27 47 58.7 or 53.163375 -27.799639')
    value = value.replace(',', ' ')
    value = re.sub(r'\s+', ' ', value)
    parts = value.split(' ')
    if len(parts) == 2:
        try:
            return SkyCoord(float(parts[0]) * u.deg, float(parts[1]) * u.deg, frame='icrs')
        except Exception:
            pass
    try:
        return SkyCoord(value, unit=(u.hourangle, u.deg), frame='icrs')
    except Exception as exc:
        raise ValueError(f'Could not parse one-cell ICRS coordinate: {value}') from exc


def coord_summary(coord):
    return (
        f'<b>Parsed ICRS:</b> {coord.ra.deg:.8f} {coord.dec.deg:.8f}<br>'
        f'<b>Sexagesimal:</b> {coord.ra.to_string(unit=u.hour, sep=":", precision=3)} '
        f'{coord.dec.to_string(unit=u.deg, sep=":", precision=3, alwayssign=True)}'
    )


def first_value(row, names, default=np.nan):
    cols = set(getattr(row, 'colnames', []) or getattr(row, 'index', []))
    for name in names:
        if name in cols and not np.ma.is_masked(row[name]):
            return row[name]
    return default


def nearest_ned(coord, radius_arcmin=2):
    try:
        Ned.TIMEOUT = 25
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


def dark_table(mapping, title='Result'):
    rows = []
    for key, value in mapping.items():
        if isinstance(value, (float, np.floating)):
            value = fmt(value, 5)
        rows.append(
            '<tr>'
            f'<th style="text-align:left;padding:7px 10px;background:#101826;color:#ffffff;border:1px solid #2b3a52">{html.escape(str(key))}</th>'
            f'<td style="padding:7px 10px;background:#05070b;color:#f4f7fb;border:1px solid #2b3a52">{html.escape(str(value))}</td>'
            '</tr>'
        )
    return f'<div style="{DARK_PANEL}"><h3 style="margin:0 0 10px;color:white">{html.escape(title)}</h3><table style="border-collapse:collapse;width:100%;font:13px sans-serif">' + ''.join(rows) + '</table></div>'


def dark_nearby_table(frame):
    if frame is None or frame.empty:
        return f'<div style="{DARK_PANEL}"><b>No nearby catalog rows returned.</b></div>'
    cols = [c for c in ['Object ID', 'Catalog', 'Angular separation (arcsec)', 'Redshift', 'Type'] if c in frame.columns]
    rows = []
    for _, row in frame[cols].head(20).iterrows():
        cells = []
        for col in cols:
            val = row[col]
            if isinstance(val, (float, np.floating)):
                val = fmt(val, 5)
            cells.append(f'<td style="padding:6px 8px;border:1px solid #2b3a52;color:#f4f7fb;background:#05070b">{html.escape(str(val))}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    heads = ''.join(f'<th style="padding:6px 8px;border:1px solid #2b3a52;color:white;background:#101826;text-align:left">{html.escape(c)}</th>' for c in cols)
    return f'<div style="{DARK_PANEL}"><h3 style="margin:0 0 10px;color:white">Nearby catalog objects</h3><table style="border-collapse:collapse;width:100%;font:13px sans-serif"><tr>{heads}</tr>' + ''.join(rows) + '</table></div>'


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


def dark_links(title, links):
    body = ''.join(f'<a style="color:#90caf9" target="_blank" href="{html.escape(url)}">{html.escape(label)}</a><br>' for label, url in links.items())
    return f'<div style="{DARK_PANEL}"><h3 style="margin:0 0 10px;color:white">{html.escape(title)}</h3>{body}</div>'


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
note = widgets.HTML(value=f'<div style="{DARK_NOTE}"><b>Coverage note:</b> Hubble and JWST are pointed-observation archives, so blank fields may mean no coverage.</div>')
viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, survey.value))


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

coord_input = widgets.Text(value='', description='ICRS RA Dec:', placeholder='Paste one coordinate cell, e.g. 03 32 39.21 -27 47 58.7 or 53.163375 -27.799639', layout=widgets.Layout(width='100%'))
find_button = widgets.Button(description='Find galaxy from ICRS coordinates', button_style='success', icon='search', layout=widgets.Layout(width='330px'))
copy_target_button = widgets.Button(description='Copy loaded target into ICRS cell', icon='copy', layout=widgets.Layout(width='300px'))
save_button = widgets.Button(description='Save Galaxy', icon='save', layout=widgets.Layout(width='220px'))
export_button = widgets.Button(description='Export CSV', icon='download', layout=widgets.Layout(width='220px'))
notes = widgets.Textarea(description='Notes:', placeholder='Free-text notes', layout=widgets.Layout(width='100%', height='90px'))
coord_status = widgets.HTML(value=f'<div style="{DARK_INFO}">Paste ICRS coordinates into the single cell above. No RA/Dec split boxes.</div>')
result_panel = widgets.HTML(value=f'<div style="{DARK_PANEL}">Galaxy results will appear here on a dark background.</div>')
cosmology_panel = widgets.HTML(value='')
nearby_panel = widgets.HTML(value='')
archive_panel = widgets.HTML(value='')
paper_panel = widgets.HTML(value='')


def copy_loaded_target(_=None):
    coord_input.value = target.value.strip()
    try:
        coord = parse_icrs_one_cell(coord_input.value)
        STATE['coord'] = coord
        coord_status.value = f'<div style="{DARK_INFO}">{coord_summary(coord)}</div>'
    except Exception as exc:
        coord_status.value = f'<div style="{DARK_ERR}"><b>Coordinate parse failed:</b> {html.escape(str(exc))}</div>'


def find_galaxy(_=None):
    find_button.disabled = True
    STATE['warnings'] = []
    result_panel.value = f'<div style="{DARK_INFO}"><b>Working…</b> Parsing coordinates and querying NED/SIMBAD.</div>'
    cosmology_panel.value = ''
    nearby_panel.value = ''
    archive_panel.value = ''
    paper_panel.value = ''
    try:
        coord = parse_icrs_one_cell(coord_input.value)
        STATE['coord'] = coord
        coord_status.value = f'<div style="{DARK_INFO}">{coord_summary(coord)}</div>'
        radius = max(2.0, float(fov.value) * 30.0)
        obj, nearby = nearest_ned(coord, radius)
        if obj is None:
            obj, nearby = nearest_simbad(coord, radius)
        if obj is None:
            warning_text = ' | '.join(STATE['warnings']) or 'No catalog response.'
            raise RuntimeError(f'No catalog object found near the supplied coordinates. {warning_text}')
        obj.update(details(obj))
        STATE['object'] = obj
        STATE['nearby'] = nearby.head(25) if nearby is not None else pd.DataFrame()
        result_panel.value = dark_table(obj, 'Nearest catalog object')
        cosmology_panel.value = f'''
        <div style="{DARK_PANEL}">
          <h3 style="margin:0 0 10px;color:white">Cosmology panel</h3>
          You are observing this galaxy as it was: <b>{fmt(obj.get('Light-travel time (Gyr)'),3)} billion years ago</b><br>
          Current comoving distance: <b>{fmt(obj.get('Comoving distance (Gly)'),3)} billion light-years</b><br>
          Universe age when light was emitted: <b>{fmt(obj.get('Universe age at emission (Gyr)'),3)} billion years</b><br>
          Scale: <b>1 arcsecond = {fmt(obj.get('Scale (ly/arcsec)'),0)} light-years</b><br>
          Estimated galaxy diameter: <b>{fmt(obj.get('Estimated physical diameter (ly)'),0)} light-years</b>
        </div>
        '''
        nearby_panel.value = dark_nearby_table(STATE['nearby'])
        archive_panel.value = dark_links('Available-observation searches', archive_links(coord))
        paper_panel.value = dark_links('Publications and survey references', paper_links(obj, coord))
        warnings = ''
        if STATE['warnings']:
            warnings = '<br><span style="color:#ffcc80">' + html.escape(' | '.join(STATE['warnings'])) + '</span>'
        coord_status.value = f'<div style="{DARK_OK}"><b>Inspection complete:</b> {html.escape(str(obj.get("Object ID", "Unknown")))} from {html.escape(str(obj.get("Catalog", "Catalog")))}{warnings}<br>{coord_summary(coord)}</div>'
    except Exception as exc:
        STATE['object'] = None
        result_panel.value = f'<div style="{DARK_ERR}"><b>Find galaxy failed:</b> {html.escape(str(exc))}</div>'
    finally:
        find_button.disabled = False


def save_galaxy(_=None):
    obj = STATE.get('object')
    coord = STATE.get('coord')
    if obj is None or coord is None:
        result_panel.value = f'<div style="{DARK_ERR}">Find a galaxy before saving.</div>'
        return
    row = {
        'Date': pd.Timestamp.now().isoformat(),
        'RA': f'{coord.ra.deg:.8f}',
        'Dec': f'{coord.dec.deg:.8f}',
        'Object ID': obj.get('Object ID', 'Unknown'),
        'Redshift': obj.get('Redshift', np.nan),
        'Distance': obj.get('Comoving distance (Gly)', np.nan),
        'Survey': selected_name(),
        'Notes': notes.value,
    }
    pd.DataFrame([row]).to_csv(CATALOG_PATH, mode='a', header=not CATALOG_PATH.exists(), index=False)
    result_panel.value = f'<div style="{DARK_OK}"><b>Saved:</b> {html.escape(str(CATALOG_PATH))}</div>'
    display(FileLink(str(CATALOG_PATH)))


def export_csv(_=None):
    if not CATALOG_PATH.exists():
        pd.DataFrame(columns=['Date', 'RA', 'Dec', 'Object ID', 'Redshift', 'Distance', 'Survey', 'Notes']).to_csv(CATALOG_PATH, index=False)
    display(FileLink(str(CATALOG_PATH)))


copy_target_button.on_click(copy_loaded_target)
find_button.on_click(find_galaxy)
save_button.on_click(save_galaxy)
export_button.on_click(export_csv)

inspector = widgets.VBox([
    widgets.HTML('<h2 style="margin:12px 0 4px;color:white;background:#05070b;padding:10px;border-radius:8px">GALAXY INSPECTOR — ONE-CELL ICRS SEARCH</h2>'),
    widgets.HTML(value=f'<div style="{DARK_NOTE}">Copy coordinates from Aladin and paste them into the single cell below. Do not split RA and Dec.</div>'),
    coord_input,
    widgets.HBox([find_button, copy_target_button, save_button, export_button]),
    coord_status,
    notes,
    result_panel,
    cosmology_panel,
    nearby_panel,
    archive_panel,
    paper_panel,
], layout=widgets.Layout(width='100%'))

copy_loaded_target()
display(widgets.VBox([header, controls, note, viewer, inspector], layout=widgets.Layout(width='100%')))
print(VERSION)
