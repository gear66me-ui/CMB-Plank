"""CMB-0020 — Standalone Gaia star map with crosshair intensity profiles."""
from __future__ import annotations

from io import BytesIO
import math
import urllib.error
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
from astropy.io import fits
from astropy.wcs import WCS

VERSION = "CMB-0020"
RA_SEXAGESIMAL = "03:19:30.85"
DEC_SEXAGESIMAL = "-21:45:24.1"
RA_DEG = 49.8785416667
DEC_DEG = -21.7566944444

HIPS2FITS_URL = "https://alasky.cds.unistra.fr/hips-image-services/hips2fits"
GAIA_TAP_URL = "https://gea.esac.esa.int/tap-server/tap/sync"
SURVEYS = {
    "DSS2 color — reliable": "CDS/P/DSS2/color",
    "DSS2 red": "CDS/P/DSS2/red",
    "2MASS color infrared": "CDS/P/2MASS/color",
    "WISE color infrared": "CDS/P/allWISE/color",
}


def _download_fits(fov_arcmin: float, survey_id: str, pixels: int):
    params = {
        "hips": survey_id, "width": int(pixels), "height": int(pixels),
        "fov": float(fov_arcmin) / 60.0, "projection": "TAN",
        "coordsys": "icrs", "ra": RA_DEG, "dec": DEC_DEG, "format": "fits",
    }
    url = HIPS2FITS_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/20.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        return fits.open(BytesIO(response.read()), memmap=False)


def _query_gaia(radius_arcmin: float) -> pd.DataFrame:
    radius_deg = float(radius_arcmin) / 60.0
    adql = f"""
    SELECT TOP 500 source_id, ra, dec, phot_g_mean_mag, phot_bp_mean_mag,
      phot_rp_mean_mag, bp_rp, parallax, parallax_error, pmra, pmdec,
      radial_velocity, teff_gspphot, logg_gspphot, mh_gspphot,
      distance_gspphot, ag_gspphot
    FROM gaiadr3.gaia_source
    WHERE 1=CONTAINS(POINT('ICRS', ra, dec),
      CIRCLE('ICRS', {RA_DEG:.10f}, {DEC_DEG:.10f}, {radius_deg:.10f}))
    ORDER BY phot_g_mean_mag ASC
    """
    params = {"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql}
    req = urllib.request.Request(
        GAIA_TAP_URL,
        data=urllib.parse.urlencode(params).encode("utf-8"),
        headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/20.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return pd.read_csv(BytesIO(response.read()))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1200]
        raise RuntimeError(f"Gaia TAP query failed with HTTP {exc.code}: {detail}") from exc


def _separation_arcsec(ra, dec):
    dra = (np.asarray(ra, float) - RA_DEG) * np.cos(np.deg2rad(DEC_DEG))
    ddec = np.asarray(dec, float) - DEC_DEG
    return np.hypot(dra, ddec) * 3600.0


def _finite(value):
    try:
        return np.isfinite(float(value))
    except Exception:
        return False


def _fmt(value, digits=3, suffix=""):
    return f"{float(value):.{digits}f}{suffix}" if _finite(value) else "Unavailable"


def _distance_pc(row):
    if _finite(row.get("distance_gspphot")) and float(row["distance_gspphot"]) > 0:
        return float(row["distance_gspphot"]), "Gaia GSP-Phot distance"
    if _finite(row.get("parallax")) and float(row["parallax"]) > 0:
        return 1000.0 / float(row["parallax"]), "Simple inverse-parallax distance"
    return np.nan, "Unavailable"


def _spectral_from_teff(teff):
    if not _finite(teff): return "Not determined"
    t = float(teff)
    if t >= 30000: return "O-type"
    if t >= 10000: return "B-type"
    if t >= 7500: return "A-type"
    if t >= 6000: return "F-type"
    if t >= 5200: return "G-type"
    if t >= 3700: return "K-type"
    return "M-type"


def _luminosity_class(logg):
    if not _finite(logg): return "Not securely classified"
    g = float(logg)
    if g >= 4.0: return "Dwarf / main-sequence-like"
    if g >= 3.5: return "Subgiant-like"
    if g >= 1.5: return "Giant-like"
    return "Supergiant-like"


def _prepare_image(data):
    data = np.asarray(data)
    if data.ndim == 3 and data.shape[0] in (3, 4):
        rgb = np.moveaxis(data[:3], 0, -1).astype(float)
        finite = np.isfinite(rgb)
        lo, hi = np.nanpercentile(rgb[finite], [1, 99.5]) if np.any(finite) else (0, 1)
        shown = np.clip((rgb - lo) / max(hi - lo, 1e-12), 0, 1)
        intensity = np.nanmean(shown, axis=2)
        return shown, intensity, True
    mono = np.squeeze(data).astype(float)
    finite = np.isfinite(mono)
    lo, hi = np.nanpercentile(mono[finite], [1, 99.5]) if np.any(finite) else (0, 1)
    shown = np.clip((mono - lo) / max(hi - lo, 1e-12), 0, 1)
    return shown, shown, False


header = widgets.HTML(value=f"""
<div style='padding:12px 16px;border-radius:10px;background:#0b172a;color:white;font-family:sans-serif;'>
  <div style='font-size:22px;font-weight:700;'>GAIA DR3 STAR MAP — {VERSION}</div>
  <div style='font-size:13px;margin-top:4px;'>RA {RA_SEXAGESIMAL}, Dec {DEC_SEXAGESIMAL} · {RA_DEG:.9f}°, {DEC_DEG:.9f}°</div>
  <div style='font-size:12px;opacity:.78;margin-top:3px;'>Real survey pixels + Gaia DR3 · crosshair X/Y intensity cuts</div>
</div>
""")

fov_widget = widgets.Dropdown(options=[("1 arcmin",1.0),("3 arcmin — recommended",3.0),("6 arcmin",6.0),("12 arcmin",12.0)], value=3.0, description="Field:", layout=widgets.Layout(width="280px"))
survey_widget = widgets.Dropdown(options=list(SURVEYS.keys()), value="DSS2 color — reliable", description="Background:", layout=widgets.Layout(width="360px"))
radius_widget = widgets.Dropdown(options=[("1 arcmin",1.0),("3 arcmin",3.0),("6 arcmin",6.0),("12 arcmin",12.0)], value=3.0, description="Gaia radius:", layout=widgets.Layout(width="280px"))
pixels_widget = widgets.Dropdown(options=[("900 px",900),("1400 px",1400),("2000 px",2000)], value=900, description="Image size:", layout=widgets.Layout(width="250px"))
load_button = widgets.Button(description="Load Crosshair Map", button_style="primary", icon="crosshairs", layout=widgets.Layout(width="220px", height="38px"))
output = widgets.Output()


def _render(_button=None):
    with output:
        clear_output(wait=True)
        print("Loading survey image and Gaia catalogue…")
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
            wcs = WCS(hdu.header).celestial
            shown, intensity, is_rgb = _prepare_image(hdu.data)
            ny, nx = intensity.shape
            x0, y0 = wcs.world_to_pixel_values(RA_DEG, DEC_DEG)
            x0 = int(np.clip(round(x0), 0, nx - 1))
            y0 = int(np.clip(round(y0), 0, ny - 1))
            x_profile = intensity[y0, :]
            y_profile = intensity[:, x0]

            fig = plt.figure(figsize=(11, 10), facecolor="black")
            gs = fig.add_gridspec(2, 2, width_ratios=[5, 1.3], height_ratios=[1.3, 5], hspace=0.05, wspace=0.05)
            ax_top = fig.add_subplot(gs[0, 0])
            ax_img = fig.add_subplot(gs[1, 0], projection=wcs)
            ax_right = fig.add_subplot(gs[1, 1])
            ax_empty = fig.add_subplot(gs[0, 1]); ax_empty.axis("off")

            if is_rgb:
                ax_img.imshow(shown, origin="lower")
            else:
                ax_img.imshow(shown, origin="lower", cmap="gray", vmin=0, vmax=1)
            ax_img.axvline(x0, color="cyan", linewidth=0.9)
            ax_img.axhline(y0, color="cyan", linewidth=0.9)
            mags = pd.to_numeric(gaia["phot_g_mean_mag"], errors="coerce")
            sizes = np.clip(120 - 5 * mags.fillna(20), 18, 95)
            ax_img.scatter(gaia["ra"], gaia["dec"], transform=ax_img.get_transform("world"), s=sizes, marker="x", linewidths=1.1, label="Gaia DR3", zorder=7)
            ax_img.set_xlabel("Right ascension (ICRS)", color="white")
            ax_img.set_ylabel("Declination (ICRS)", color="white")
            ax_img.tick_params(colors="white")
            ax_img.coords[0].set_ticklabel(color="white")
            ax_img.coords[1].set_ticklabel(color="white")
            ax_img.grid(color="white", alpha=0.16, linestyle=":")
            legend = ax_img.legend(loc="upper right", facecolor="#111111", edgecolor="#777777")
            for text in legend.get_texts(): text.set_color("white")
            ax_img.set_facecolor("black")

            ax_top.plot(np.arange(nx), x_profile)
            ax_top.axvline(x0, color="cyan", linewidth=0.9)
            ax_top.set_xlim(0, nx - 1)
            ax_top.set_ylabel("Intensity")
            ax_top.set_title(f"Horizontal intensity cut through target · {survey_widget.value}", color="white")
            ax_top.tick_params(colors="white")
            ax_top.set_facecolor("black")
            ax_top.yaxis.label.set_color("white")
            ax_top.set_xticklabels([])

            ax_right.plot(y_profile, np.arange(ny))
            ax_right.axhline(y0, color="cyan", linewidth=0.9)
            ax_right.set_ylim(0, ny - 1)
            ax_right.set_xlabel("Intensity", color="white")
            ax_right.tick_params(colors="white")
            ax_right.set_facecolor("black")
            ax_right.set_yticklabels([])

            plt.tight_layout()
            plt.show()

            distance_pc, method = _distance_pc(nearest)
            distance_ly = distance_pc * 3.26156 if _finite(distance_pc) else np.nan
            rows = [
                ("Gaia DR3 source ID", str(int(nearest["source_id"]))),
                ("Angular separation", _fmt(nearest["separation_arcsec"], 3, " arcsec")),
                ("G magnitude", _fmt(nearest.get("phot_g_mean_mag"), 3)),
                ("BP − RP color", _fmt(nearest.get("bp_rp"), 3)),
                ("Parallax", _fmt(nearest.get("parallax"), 4, " mas")),
                ("Parallax uncertainty", _fmt(nearest.get("parallax_error"), 4, " mas")),
                ("Distance", f"{distance_pc:,.1f} pc / {distance_ly:,.1f} light-years" if _finite(distance_pc) else "Unavailable"),
                ("Distance method", method),
                ("Effective temperature", _fmt(nearest.get("teff_gspphot"), 0, " K")),
                ("Approximate spectral family", _spectral_from_teff(nearest.get("teff_gspphot"))),
                ("Dwarf / giant assessment", _luminosity_class(nearest.get("logg_gspphot"))),
                ("Proper motion RA", _fmt(nearest.get("pmra"), 3, " mas/yr")),
                ("Proper motion Dec", _fmt(nearest.get("pmdec"), 3, " mas/yr")),
                ("Radial velocity", _fmt(nearest.get("radial_velocity"), 3, " km/s")),
                ("Crosshair pixel", f"x={x0}, y={y0}"),
                ("Crosshair intensity", _fmt(intensity[y0, x0], 5)),
            ]
            html_rows = "".join(f"<tr><td style='padding:8px 12px;border-bottom:1px solid #2e3944;font-weight:600;color:#b9d8ef'>{p}</td><td style='padding:8px 12px;border-bottom:1px solid #2e3944;color:#f4f7fa'>{v}</td></tr>" for p, v in rows)
            display(widgets.HTML(value=f"""
            <div style='margin-top:14px;background:#080c11;color:#f4f7fa;border:1px solid #34404c;border-radius:10px;overflow:hidden;font-family:Arial,sans-serif;'>
              <div style='padding:12px 14px;background:#14202b;font-size:18px;font-weight:700;'>Nearest Gaia source and crosshair summary</div>
              <table style='width:100%;border-collapse:collapse;font-size:14px;'><tbody>{html_rows}</tbody></table>
            </div>"""))
        except Exception as exc:
            print(f"ERROR: {type(exc).__name__}: {exc}")
            print("Try DSS2 color, 3 arcmin field, 3 arcmin Gaia radius, and 900 px.")
        finally:
            if hdul is not None:
                hdul.close()


load_button.on_click(_render)
controls = widgets.VBox([
    widgets.HBox([fov_widget, survey_widget]),
    widgets.HBox([radius_widget, pixels_widget, load_button]),
])
instructions = widgets.HTML(value="""
<div style='padding:9px 12px;border-left:4px solid #00d9ff;background:#eefcff;font:13px sans-serif;'>
The cyan crosshair is fixed on the supplied sky coordinate. The upper graph is the horizontal pixel-intensity cut; the right graph is the vertical cut. For RGB surveys, intensity is the mean of the normalized red, green, and blue channels.
</div>""")
display(widgets.VBox([header, controls, instructions, output], layout=widgets.Layout(width="100%")))
