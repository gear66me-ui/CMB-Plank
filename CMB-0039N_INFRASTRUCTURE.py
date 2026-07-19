# CMB-0039N_INFRASTRUCTURE.py
from __future__ import annotations

import html
import urllib.parse
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output

VERSION = 'CMB-0039N'
DEFAULT_TARGET = '03 32 39.99 -27 48 00.0'
DEFAULT_FOV = 0.08

SURVEYS = [
    ('DSS2 color', 'P/DSS2/color'),
    ('DSS2 blue', 'P/DSS2/blue'),
    ('DSS2 red', 'P/DSS2/red'),
    ('PanSTARRS DR1 color', 'P/PanSTARRS/DR1/color-z-zg-g'),
    ('DESI Legacy DR10', 'CDS/P/DESI-Legacy-Surveys/DR10/color'),
    ('2MASS color infrared', 'P/2MASS/color'),
    ('WISE color infrared', 'P/allWISE/color'),
    ('GALEX GR6/7 ultraviolet', 'P/GALEXGR6/AIS/color'),
    ('Hubble Outreach color', 'CDS/P/HST/EPO'),
    ('Hubble GOODS color', 'CDS/P/HST/GOODS/color'),
    ('Hubble GOODS i-band', 'CDS/P/HST/GOODS/i'),
    ('JWST F150W', 'CDS/P/JWST/F150W'),
    ('JWST F444W', 'CDS/P/JWST/F444W'),
]


def aladin_url(target_text, fov_deg, survey_id):
    return 'https://aladin.u-strasbg.fr/AladinLite/?' + urllib.parse.urlencode({
        'target': str(target_text).strip(),
        'fov': f'{float(fov_deg):g}',
        'survey': survey_id,
    })


def selected_name():
    return next((label for label, value in SURVEYS if value == survey.value), survey.value)


def viewer_html(target_text, fov_deg, survey_id, survey_name):
    url = aladin_url(target_text, fov_deg, survey_id)
    return f'''
    <div style="width:100%;background:#000;border:1px solid #78909c;border-radius:10px;overflow:visible;">
      <div style="padding:8px 12px;background:#0b172a;color:white;font-family:sans-serif">
        <b>{html.escape(survey_name)}</b><br>
        <span style="font-size:12px;opacity:.85">Target: {html.escape(str(target_text))} · FOV {float(fov_deg):g}°</span>
      </div>
      <iframe src="{html.escape(url)}"
        style="width:100%;height:860px;border:0;display:block;background:#000;touch-action:auto;overflow:visible;"
        allowfullscreen>
      </iframe>
    </div>
    '''

header = widgets.HTML(value=f'''
<div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;font-family:sans-serif">
  <div style="font-size:22px;font-weight:700">INTERACTIVE MULTI-SURVEY SKY MAP — {VERSION}</div>
  <div style="font-size:13px;opacity:.9;margin-top:4px">
    AladinLite sky map · drag to pan · pinch or use +/- to zoom · real HiPS survey imagery
  </div>
</div>
''')

target = widgets.Text(value=DEFAULT_TARGET, description='Target:', layout=widgets.Layout(width='560px'))
survey = widgets.Dropdown(options=SURVEYS, value='CDS/P/HST/GOODS/color', description='Survey:', layout=widgets.Layout(width='560px'))
fov = widgets.Dropdown(
    options=[('0.01° — very tight', .01), ('0.03°', .03), ('0.08° — HUDF/GOODS', .08), ('0.25°', .25), ('1°', 1.0), ('5°', 5.0), ('20°', 20.0)],
    value=DEFAULT_FOV,
    description='Field:',
    layout=widgets.Layout(width='330px'),
)

load_button = widgets.Button(description='Load Interactive Map', button_style='primary', icon='globe')
open_button = widgets.Button(description='Open Full Screen', icon='external-link')
get_coord_button = widgets.Button(description='Get coordinates from Aladin', button_style='info', icon='crosshairs')
coord_field = widgets.Text(
    value=DEFAULT_TARGET,
    description='RA Dec:',
    placeholder='RA Dec in one field',
    layout=widgets.Layout(width='680px'),
)
status = widgets.HTML(value='')
viewer = widgets.HTML(value=viewer_html(DEFAULT_TARGET, DEFAULT_FOV, survey.value, 'Hubble GOODS color'))


def reload_map(_=None):
    viewer.value = viewer_html(target.value, fov.value, survey.value, selected_name())
    coord_field.value = target.value
    status.value = '<b style="color:#1b5e20">Map loaded.</b>'


def open_full(_=None):
    url = aladin_url(target.value, fov.value, survey.value)
    display(HTML(f"<script>window.open({url!r}, '_blank');</script>"))


def get_coordinates(_=None):
    # Colab cannot read the live pan center from a cross-origin Aladin iframe.
    # This button returns the current loaded target in one copyable field.
    coord_field.value = target.value
    status.value = '<b style="color:#1565c0">Coordinates copied from current loaded target field.</b>'

load_button.on_click(reload_map)
open_button.on_click(open_full)
get_coord_button.on_click(get_coordinates)

controls = widgets.VBox([
    widgets.HBox([target]),
    widgets.HBox([survey]),
    widgets.HBox([fov, load_button, open_button]),
    widgets.HBox([coord_field, get_coord_button]),
    status,
], layout=widgets.Layout(width='100%'))

clear_output(wait=True)
display(widgets.VBox([header, controls, viewer], layout=widgets.Layout(width='100%')))
