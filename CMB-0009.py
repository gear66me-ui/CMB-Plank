"""CMB-0009 — Python-native Gaia DR3 map for the selected sky position.

Run with:
    %run CMB-0009.py

This version avoids browser iframes and data URLs. It downloads a real survey image
through CDS HiPS2FITS, queries Gaia DR3 through the Gaia TAP service, and plots both
inside the Colab notebook with ipywidgets and Matplotlib.
"""

from __future__ import annotations

from io import BytesIO
import math
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
from astropy.io import fits
from astropy.wcs import WCS

VERSION = "CMB-0009"
RA_SEXAGESIMAL = "03:12:59.96"
DEC_SEXAGESIMAL = "-20:02:09.0"
RA_DEG = 48.2498333333
DEC_DEG = -20.0358333333

HIPS2FITS_URL = "https://alasky.cds.unistra.fr/hips-image-services/hips2fits"
GAIA_TAP_URL = "https://gea.esac.esa.int/tap-server/tap/sync"

SURVEYS = {
    "DSS2 color — reliable": "CDS/P/DSS2/color",
    "DSS2 red": "CDS/P/DSS2/red",
    "2MASS color infrared": "CDS/P/2MASS/color",
    "WISE color infrared": "CDS/P/allWISE/color",
}


def _download_fits(fov_arcmin: float, survey_id: str, pixels: int = 900):
    fov_deg = float(fov_arcmin) / 60.0
    params = {
        "hips": survey_id,
        "width": int(pixels),
        "height": int(pixels),
        "fov": fov_deg,
        "projection": "TAN",
        "coordsys": "icrs",
        "ra": RA_DEG,
        "dec": DEC_DEG,
        "format": "fits",
    }
    url = HIPS2FITS_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/9.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        raw = response.read()
    hdul = fits.open(BytesIO(raw), memmap=False)
    return hdul


def _query_gaia(radius_arcmin: float) -> pd.DataFrame:
    radius_deg = float(radius_arcmin) / 60.0
    adql = f"""
    SELECT TOP 500
        source_id, ra, dec, phot_g_mean_mag, bp_rp,
        parallax, parallax_error, pmra, pmdec,
        radial_velocity
    FROM gaiadr3.gaia_source
    WHERE 1=CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {RA_DEG:.10f}, {DEC_DEG:.10f}, {radius_deg:.10f})
    )
    ORDER BY phot_g_mean_mag ASC
    """
    params = {
        "REQUEST": "doQuery",
        "LANG": "ADQL",
        "FORMAT": "csv",
        "QUERY": adql,
    }
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(
        GAIA_TAP_URL,
        data=data,
        headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/9.0"},
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        csv_bytes = response.read()
    return pd.read_csv(BytesIO(csv_bytes))


def _separation_arcsec(ra, dec):
    dra = (np.asarray(ra, dtype=float) - RA_DEG) * np.cos(np.deg2rad(DEC_DEG))
    ddec = np.asarray(dec, dtype=float) - DEC_DEG
    return np.hypot(dra, ddec) * 3600.0


header = widgets.HTML(value=f"""
<div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;font-family:sans-serif;">
  <div style="font-size:22px;font-weight:700;">GAIA DR3 STAR MAP — {VERSION}</div>
  <div style="font-size:13px;opacity:.9;margin-top:4px;">
    RA {RA_SEXAGESIMAL}, Dec {DEC_SEXAGESIMAL} · decimal RA {RA_DEG:.6f}°, Dec {DEC_DEG:.6f}°
  </div>
  <div style="font-size:12px;opacity:.78;margin-top:3px;">
    Real survey imagery + Gaia DR3 catalogue · Python-native Colab widget · no iframe
  </div>
</div>
""")

fov_widget = widgets.Dropdown(
    options=[("1 arcmin — tight", 1.0), ("3 arcmin — recommended", 3.0), ("6 arcmin", 6.0), ("12 arcmin", 12.0), ("30 arcmin", 30.0)],
    value=3.0,
    description="Field of view:",
    layout=widgets.Layout(width="330px"),
)

survey_widget = widgets.Dropdown(
    options=list(SURVEYS.keys()),
    value="DSS2 color — reliable",
    description="Background:",
    layout=widgets.Layout(width="360px"),
)

radius_widget = widgets.Dropdown(
    options=[("1 arcmin", 1.0), ("3 arcmin", 3.0), ("6 arcmin", 6.0), ("12 arcmin", 12.0)],
    value=3.0,
    description="Gaia radius:",
    layout=widgets.Layout(width="280px"),
)

pixels_widget = widgets.Dropdown(
    options=[("900 px — recommended", 900), ("1400 px — high resolution", 1400), ("2000 px — very high", 2000)],
    value=900,
    description="Image size:",
    layout=widgets.Layout(width="320px"),
)

load_button = widgets.Button(
    description="Load Gaia Map",
    button_style="primary",
    icon="search",
    layout=widgets.Layout(width="190px", height="38px"),
)

output = widgets.Output()


def _render(_button=None):
    with output:
        clear_output(wait=True)
        print("Loading survey image and Gaia DR3 catalogue…")
        try:
            hdul = _download_fits(fov_widget.value, SURVEYS[survey_widget.value], pixels_widget.value)
            gaia = _query_gaia(radius_widget.value)

            hdu = hdul[0]
            data = np.asarray(hdu.data)
            wcs = WCS(hdu.header)

            fig = plt.figure(figsize=(10, 9))
            ax = fig.add_subplot(111, projection=wcs)

            if data.ndim == 3 and data.shape[0] in (3, 4):
                image = np.moveaxis(data[:3], 0, -1)
                finite = np.isfinite(image)
                if np.any(finite):
                    lo, hi = np.nanpercentile(image[finite], [1, 99.5])
                    image = np.clip((image - lo) / max(hi - lo, 1e-12), 0, 1)
                ax.imshow(image, origin="lower")
            else:
                image = np.squeeze(data)
                finite = np.isfinite(image)
                lo, hi = np.nanpercentile(image[finite], [1, 99.5]) if np.any(finite) else (0, 1)
                ax.imshow(image, origin="lower", cmap="gray", vmin=lo, vmax=hi)

            ax.scatter(
                [RA_DEG], [DEC_DEG], transform=ax.get_transform("world"),
                s=260, facecolors="none", edgecolors="lime", linewidths=2.2,
                label="Supplied coordinate", zorder=6,
            )

            if not gaia.empty:
                mags = pd.to_numeric(gaia["phot_g_mean_mag"], errors="coerce")
                marker_sizes = np.clip(120 - 5 * mags.fillna(20), 18, 95)
                ax.scatter(
                    gaia["ra"], gaia["dec"], transform=ax.get_transform("world"),
                    s=marker_sizes, marker="x", linewidths=1.2, label="Gaia DR3",
                    zorder=7,
                )

            ax.set_xlabel("Right ascension (ICRS)")
            ax.set_ylabel("Declination (ICRS)")
            ax.grid(color="white", alpha=0.18, linestyle=":")
            ax.legend(loc="upper right")
            ax.set_title(
                f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin · Gaia radius {radius_widget.value:g} arcmin\n"
                f"Green circle: RA {RA_SEXAGESIMAL}, Dec {DEC_SEXAGESIMAL}"
            )
            plt.tight_layout()
            plt.show()

            if gaia.empty:
                print("Gaia DR3 returned no sources inside the selected radius.")
            else:
                gaia = gaia.copy()
                gaia["separation_arcsec"] = _separation_arcsec(gaia["ra"], gaia["dec"])
                gaia = gaia.sort_values("separation_arcsec").reset_index(drop=True)
                cols = [
                    "source_id", "separation_arcsec", "ra", "dec", "phot_g_mean_mag",
                    "bp_rp", "parallax", "parallax_error", "pmra", "pmdec", "radial_velocity",
                ]
                print(f"Gaia DR3 sources loaded: {len(gaia)}")
                display(gaia[cols].head(30).style.format({
                    "separation_arcsec": "{:.3f}", "ra": "{:.8f}", "dec": "{:.8f}",
                    "phot_g_mean_mag": "{:.3f}", "bp_rp": "{:.3f}", "parallax": "{:.4f}",
                    "parallax_error": "{:.4f}", "pmra": "{:.4f}", "pmdec": "{:.4f}",
                    "radial_velocity": "{:.3f}",
                }))
                nearest = gaia.iloc[0]
                print()
                print("Nearest Gaia source")
                print(f"Source ID: {int(nearest['source_id'])}")
                print(f"Separation: {nearest['separation_arcsec']:.3f} arcsec")
                print(f"G magnitude: {nearest['phot_g_mean_mag']}")
                print(f"Parallax: {nearest['parallax']} mas")
                print(f"Proper motion: pmRA={nearest['pmra']} mas/yr, pmDec={nearest['pmdec']} mas/yr")

            hdul.close()
        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}")
            print("Try DSS2 color, 3 arcmin FOV, 3 arcmin Gaia radius, and 900 px.")


load_button.on_click(_render)

controls = widgets.VBox([
    widgets.HBox([fov_widget, survey_widget]),
    widgets.HBox([radius_widget, pixels_widget, load_button]),
])

instructions = widgets.HTML(value="""
<div style="padding:9px 12px;border-left:4px solid #ffd400;background:#fffde7;font:13px sans-serif;">
<b>Recommended first run:</b> 3 arcmin field, DSS2 color, 3 arcmin Gaia radius, 900 px, then click <b>Load Gaia Map</b>.
The green circle is your exact coordinate. Gaia DR3 sources are plotted as crosses and listed below the image with source ID, magnitude, parallax, and proper motion.
</div>
""")

display(widgets.VBox([header, controls, instructions, output], layout=widgets.Layout(width="100%")))
