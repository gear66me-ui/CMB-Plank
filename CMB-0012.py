"""CMB-0012 — Gaia DR3 image and robust stellar summary.

Run with:
    %run CMB-0012.py

Fixes the Gaia HTTP 400 error by querying only columns published directly in
gaiadr3.gaia_source. The image has no supplied-coordinate circle. Gaia sources
remain as crosses, and the nearest source receives a robust summary using Gaia
astrometry and GSP-Phot parameters when available.
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

VERSION = "CMB-0012"
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
    params = {
        "hips": survey_id,
        "width": int(pixels),
        "height": int(pixels),
        "fov": float(fov_arcmin) / 60.0,
        "projection": "TAN",
        "coordsys": "icrs",
        "ra": RA_DEG,
        "dec": DEC_DEG,
        "format": "fits",
    }
    url = HIPS2FITS_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/12.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return fits.open(BytesIO(response.read()), memmap=False)


def _query_gaia(radius_arcmin: float) -> pd.DataFrame:
    radius_deg = float(radius_arcmin) / 60.0
    adql = f"""
    SELECT TOP 500
        source_id, ra, dec,
        phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, bp_rp,
        parallax, parallax_error, pmra, pmdec, radial_velocity,
        teff_gspphot, logg_gspphot, mh_gspphot,
        distance_gspphot, ag_gspphot
    FROM gaiadr3.gaia_source
    WHERE 1=CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {RA_DEG:.10f}, {DEC_DEG:.10f}, {radius_deg:.10f})
    )
    ORDER BY phot_g_mean_mag ASC
    """
    params = {"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql}
    data = urllib.parse.urlencode(params).encode("utf-8")
    request = urllib.request.Request(
        GAIA_TAP_URL,
        data=data,
        headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/12.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return pd.read_csv(BytesIO(response.read()))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1200]
        raise RuntimeError(f"Gaia TAP query failed with HTTP {exc.code}: {detail}") from exc


def _separation_arcsec(ra, dec):
    dra = (np.asarray(ra, dtype=float) - RA_DEG) * np.cos(np.deg2rad(DEC_DEG))
    ddec = np.asarray(dec, dtype=float) - DEC_DEG
    return np.hypot(dra, ddec) * 3600.0


def _finite(value):
    try:
        return np.isfinite(float(value))
    except Exception:
        return False


def _fmt(value, digits=3, suffix=""):
    return f"{float(value):.{digits}f}{suffix}" if _finite(value) else "Unavailable"


def _spectral_from_teff(teff):
    if not _finite(teff): return "Not determined from Gaia DR3"
    t = float(teff)
    if t >= 30000: return "O-type"
    if t >= 10000: return "B-type"
    if t >= 7500: return "A-type"
    if t >= 6000: return "F-type"
    if t >= 5200: return "G-type"
    if t >= 3700: return "K-type"
    return "M-type"


def _luminosity_class(logg):
    if not _finite(logg): return "Not securely classified; surface gravity unavailable"
    g = float(logg)
    if g >= 4.0: return "Dwarf / main-sequence-like"
    if g >= 3.5: return "Subgiant-like"
    if g >= 1.5: return "Giant-like"
    return "Supergiant-like"


def _distance_pc(row):
    if _finite(row.get("distance_gspphot")) and float(row["distance_gspphot"]) > 0:
        return float(row["distance_gspphot"]), "Gaia GSP-Phot distance"
    if _finite(row.get("parallax")) and float(row["parallax"]) > 0:
        return 1000.0 / float(row["parallax"]), "Simple inverse-parallax distance"
    return np.nan, "Unavailable"


def _absolute_g(gmag, distance_pc, ag):
    if not (_finite(gmag) and _finite(distance_pc) and float(distance_pc) > 0):
        return np.nan
    extinction = float(ag) if _finite(ag) else 0.0
    return float(gmag) - 5.0 * math.log10(float(distance_pc) / 10.0) - extinction


def _rough_luminosity_from_abs_g(abs_g):
    if not _finite(abs_g): return np.nan
    # Approximate optical luminosity relative to the Sun using M_G,sun ≈ 4.67.
    return 10.0 ** (-0.4 * (float(abs_g) - 4.67))


header = widgets.HTML(value=f"""
<div style="padding:12px 16px;border-radius:10px;background:#0b172a;color:white;font-family:sans-serif;">
  <div style="font-size:22px;font-weight:700;">GAIA DR3 STAR MAP — {VERSION}</div>
  <div style="font-size:13px;opacity:.9;margin-top:4px;">
    Search position: RA {RA_SEXAGESIMAL}, Dec {DEC_SEXAGESIMAL} · decimal RA {RA_DEG:.6f}°, Dec {DEC_DEG:.6f}°
  </div>
  <div style="font-size:12px;opacity:.78;margin-top:3px;">Real survey imagery + Gaia DR3 catalogue · no generated images</div>
</div>
""")

fov_widget = widgets.Dropdown(options=[("1 arcmin — tight",1.0),("3 arcmin — recommended",3.0),("6 arcmin",6.0),("12 arcmin",12.0),("30 arcmin",30.0)], value=3.0, description="Field of view:", layout=widgets.Layout(width="330px"))
survey_widget = widgets.Dropdown(options=list(SURVEYS.keys()), value="DSS2 color — reliable", description="Background:", layout=widgets.Layout(width="360px"))
radius_widget = widgets.Dropdown(options=[("1 arcmin",1.0),("3 arcmin",3.0),("6 arcmin",6.0),("12 arcmin",12.0)], value=3.0, description="Gaia radius:", layout=widgets.Layout(width="280px"))
pixels_widget = widgets.Dropdown(options=[("900 px — recommended",900),("1400 px — high resolution",1400),("2000 px — very high",2000)], value=900, description="Image size:", layout=widgets.Layout(width="320px"))
load_button = widgets.Button(description="Load Image + Star Summary", button_style="primary", icon="search", layout=widgets.Layout(width="240px", height="38px"))
output = widgets.Output()


def _render(_button=None):
    with output:
        clear_output(wait=True)
        print("Loading survey image and Gaia DR3 catalogue…")
        hdul = None
        try:
            hdul = _download_fits(fov_widget.value, SURVEYS[survey_widget.value], pixels_widget.value)
            gaia = _query_gaia(radius_widget.value)
            if gaia.empty:
                raise RuntimeError("Gaia DR3 returned no sources inside the selected radius.")

            gaia = gaia.copy()
            gaia["separation_arcsec"] = _separation_arcsec(gaia["ra"], gaia["dec"])
            gaia = gaia.sort_values("separation_arcsec").reset_index(drop=True)
            nearest = gaia.iloc[0]

            hdu = hdul[0]
            data = np.asarray(hdu.data)
            wcs = WCS(hdu.header).celestial
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

            mags = pd.to_numeric(gaia["phot_g_mean_mag"], errors="coerce")
            marker_sizes = np.clip(120 - 5 * mags.fillna(20), 18, 95)
            ax.scatter(gaia["ra"], gaia["dec"], transform=ax.get_transform("world"), s=marker_sizes, marker="x", linewidths=1.15, label="Gaia DR3", zorder=7)
            ax.set_xlabel("Right ascension (ICRS)")
            ax.set_ylabel("Declination (ICRS)")
            ax.grid(color="white", alpha=0.18, linestyle=":")
            ax.legend(loc="upper right")
            ax.set_title(f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin · Gaia radius {radius_widget.value:g} arcmin\nGaia DR3 sources shown as crosses; no supplied-coordinate circle")
            plt.tight_layout()
            plt.show()

            distance_pc, distance_method = _distance_pc(nearest)
            distance_ly = distance_pc * 3.26156 if _finite(distance_pc) else np.nan
            abs_g = _absolute_g(nearest.get("phot_g_mean_mag"), distance_pc, nearest.get("ag_gspphot"))
            approx_lum = _rough_luminosity_from_abs_g(abs_g)
            teff = nearest.get("teff_gspphot")
            logg = nearest.get("logg_gspphot")

            summary = pd.DataFrame([
                ["Gaia DR3 source ID", str(int(nearest["source_id"]))],
                ["Angular separation", _fmt(nearest["separation_arcsec"], 3, " arcsec")],
                ["G magnitude", _fmt(nearest.get("phot_g_mean_mag"), 3)],
                ["BP − RP color", _fmt(nearest.get("bp_rp"), 3)],
                ["Parallax", _fmt(nearest.get("parallax"), 4, " mas")],
                ["Parallax uncertainty", _fmt(nearest.get("parallax_error"), 4, " mas")],
                ["Distance", f"{distance_pc:,.1f} pc / {distance_ly:,.1f} light-years" if _finite(distance_pc) else "Unavailable"],
                ["Distance method", distance_method],
                ["Effective temperature", _fmt(teff, 0, " K")],
                ["Approximate spectral family", _spectral_from_teff(teff)],
                ["Surface gravity log g", _fmt(logg, 3)],
                ["Dwarf / giant assessment", _luminosity_class(logg)],
                ["Absolute Gaia G magnitude", _fmt(abs_g, 3)],
                ["Approximate optical luminosity", _fmt(approx_lum, 3, " L☉")],
                ["Extinction A_G", _fmt(nearest.get("ag_gspphot"), 3, " mag")],
                ["Metallicity [M/H]", _fmt(nearest.get("mh_gspphot"), 3)],
                ["Proper motion RA", _fmt(nearest.get("pmra"), 3, " mas/yr")],
                ["Proper motion Dec", _fmt(nearest.get("pmdec"), 3, " mas/yr")],
                ["Radial velocity", _fmt(nearest.get("radial_velocity"), 3, " km/s")],
            ], columns=["Property", "Nearest Gaia source"])

            print("\nNearest Gaia source summary")
            display(summary.style.hide(axis="index").set_properties(**{"text-align": "left"}))
            print("\nNotes: spectral family comes from Gaia effective temperature; dwarf/giant status comes from Gaia surface gravity. Optical luminosity is an approximate estimate from extinction-corrected absolute Gaia G magnitude, not a bolometric luminosity.")

            cols = ["source_id","separation_arcsec","ra","dec","phot_g_mean_mag","bp_rp","parallax","pmra","pmdec","teff_gspphot","logg_gspphot"]
            print(f"\nGaia DR3 sources loaded: {len(gaia)}")
            display(gaia[cols].head(30).style.format({"separation_arcsec":"{:.3f}","ra":"{:.8f}","dec":"{:.8f}","phot_g_mean_mag":"{:.3f}","bp_rp":"{:.3f}","parallax":"{:.4f}","pmra":"{:.4f}","pmdec":"{:.4f}","teff_gspphot":"{:.0f}","logg_gspphot":"{:.3f}"}))

        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}")
            print("Try DSS2 color, 3 arcmin FOV, 3 arcmin Gaia radius, and 900 px.")
        finally:
            if hdul is not None:
                hdul.close()


load_button.on_click(_render)
controls = widgets.VBox([widgets.HBox([fov_widget, survey_widget]), widgets.HBox([radius_widget, pixels_widget, load_button])])
instructions = widgets.HTML(value="""
<div style="padding:9px 12px;border-left:4px solid #ffd400;background:#fffde7;font:13px sans-serif;">
<b>Recommended:</b> 3 arcmin field, DSS2 color, 3 arcmin Gaia radius, 900 px.<br>
The image contains no supplied-coordinate circle. Gaia catalogue sources remain as crosses, and the nearest source is summarized below the image.
</div>
""")
display(widgets.VBox([header, controls, instructions, output], layout=widgets.Layout(width="100%")))
