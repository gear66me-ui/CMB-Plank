"""CMB-0013 — Dark-background Gaia image with a concise stellar summary.

Run with:
    %run CMB-0013.py

This version keeps the real survey image and Gaia source crosses, removes the
large 28-source catalogue dump, uses a black plotting background, and presents
only a compact summary table for the nearest Gaia DR3 source.
"""

from __future__ import annotations

import urllib.error
import urllib.request

SOURCE_URL = (
    "https://raw.githubusercontent.com/gear66me-ui/"
    "CMB-Plank/main/CMB-0012.py"
)


def _load_source() -> str:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/13.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise RuntimeError(
            "Unable to load CMB-0012.py from GitHub. Check the internet "
            f"connection. Details: {exc}"
        ) from exc


source = _load_source()
source = source.replace('VERSION = "CMB-0012"', 'VERSION = "CMB-0013"', 1)
source = source.replace(
    'Mozilla/5.0 CMB-Gaia-Widget/12.0',
    'Mozilla/5.0 CMB-Gaia-Widget/13.0',
)

old_figure = '''            fig = plt.figure(figsize=(10, 9))
            ax = fig.add_subplot(111, projection=wcs)
'''
new_figure = '''            fig = plt.figure(figsize=(10, 9), facecolor="black")
            ax = fig.add_subplot(111, projection=wcs)
            ax.set_facecolor("black")
'''
if old_figure not in source:
    raise RuntimeError("Could not apply the CMB-0013 dark-background patch.")
source = source.replace(old_figure, new_figure, 1)

source = source.replace(
    '            ax.set_xlabel("Right ascension (ICRS)")\n'
    '            ax.set_ylabel("Declination (ICRS)")\n'
    '            ax.grid(color="white", alpha=0.18, linestyle=":")\n'
    '            ax.legend(loc="upper right")\n'
    '            ax.set_title(f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin · Gaia radius {radius_widget.value:g} arcmin\\nGaia DR3 sources shown as crosses; no supplied-coordinate circle")\n',
    '            ax.set_xlabel("Right ascension (ICRS)", color="white")\n'
    '            ax.set_ylabel("Declination (ICRS)", color="white")\n'
    '            ax.tick_params(colors="white")\n'
    '            ax.coords[0].set_ticklabel(color="white")\n'
    '            ax.coords[1].set_ticklabel(color="white")\n'
    '            ax.coords[0].set_axislabel("Right ascension (ICRS)", color="white")\n'
    '            ax.coords[1].set_axislabel("Declination (ICRS)", color="white")\n'
    '            ax.grid(color="white", alpha=0.18, linestyle=":")\n'
    '            legend = ax.legend(loc="upper right", facecolor="#111111", edgecolor="#777777")\n'
    '            for text in legend.get_texts(): text.set_color("white")\n'
    '            ax.set_title(f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin\\nGaia DR3 sources", color="white")\n',
    1,
)

old_summary = '''            summary = pd.DataFrame([
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

            print("\\nNearest Gaia source summary")
            display(summary.style.hide(axis="index").set_properties(**{"text-align": "left"}))
            print("\\nNotes: spectral family comes from Gaia effective temperature; dwarf/giant status comes from Gaia surface gravity. Optical luminosity is an approximate estimate from extinction-corrected absolute Gaia G magnitude, not a bolometric luminosity.")

            cols = ["source_id","separation_arcsec","ra","dec","phot_g_mean_mag","bp_rp","parallax","pmra","pmdec","teff_gspphot","logg_gspphot"]
            print(f"\\nGaia DR3 sources loaded: {len(gaia)}")
            display(gaia[cols].head(30).style.format({"separation_arcsec":"{:.3f}","ra":"{:.8f}","dec":"{:.8f}","phot_g_mean_mag":"{:.3f}","bp_rp":"{:.3f}","parallax":"{:.4f}","pmra":"{:.4f}","pmdec":"{:.4f}","teff_gspphot":"{:.0f}","logg_gspphot":"{:.3f}"}))
'''

new_summary = '''            summary = pd.DataFrame([
                ["Gaia DR3 source ID", str(int(nearest["source_id"]))],
                ["Angular separation", _fmt(nearest["separation_arcsec"], 3, " arcsec")],
                ["G magnitude", _fmt(nearest.get("phot_g_mean_mag"), 3)],
                ["Color (BP − RP)", _fmt(nearest.get("bp_rp"), 3)],
                ["Parallax", _fmt(nearest.get("parallax"), 4, " mas")],
                ["Distance", f"{distance_pc:,.1f} pc  ·  {distance_ly:,.1f} light-years" if _finite(distance_pc) else "Unavailable from Gaia DR3"],
                ["Effective temperature", _fmt(teff, 0, " K")],
                ["Likely spectral family", _spectral_from_teff(teff)],
                ["Likely star class", _luminosity_class(logg)],
                ["Approximate optical luminosity", _fmt(approx_lum, 3, " × Sun")],
                ["Proper motion RA", _fmt(nearest.get("pmra"), 3, " mas/yr")],
                ["Proper motion Dec", _fmt(nearest.get("pmdec"), 3, " mas/yr")],
                ["Radial velocity", _fmt(nearest.get("radial_velocity"), 3, " km/s")],
            ], columns=["Property", "Value"])

            styled = (
                summary.style
                .hide(axis="index")
                .set_table_styles([
                    {"selector": "table", "props": [("border-collapse", "collapse"), ("width", "100%"), ("background", "#0b0f14"), ("color", "#f5f7fa"), ("font-family", "Arial, sans-serif")]},
                    {"selector": "th", "props": [("background", "#16202b"), ("color", "#ffffff"), ("padding", "9px"), ("border", "1px solid #3b4652"), ("text-align", "left")]},
                    {"selector": "td", "props": [("padding", "8px 10px"), ("border", "1px solid #303943"), ("text-align", "left")]},
                    {"selector": "tr:nth-child(even)", "props": [("background", "#111821")]},
                ])
            )
            display(widgets.HTML("<div style='margin-top:12px;padding:10px 14px;background:#0b0f14;color:white;border-radius:9px;font:700 18px Arial;'>Nearest Gaia source summary</div>"))
            display(styled)

            if _finite(distance_pc):
                distance_sentence = f"Gaia places this source about {distance_ly:,.0f} light-years away."
            else:
                distance_sentence = "Gaia DR3 does not provide a reliable positive distance estimate for this source."
            class_sentence = _luminosity_class(logg)
            temp_sentence = _spectral_from_teff(teff)
            display(widgets.HTML(
                "<div style='margin-top:10px;padding:12px 14px;background:#111821;color:#eef3f8;border-left:4px solid #4fc3f7;border-radius:6px;font:14px/1.5 Arial;'>"
                f"<b>Plain-English summary:</b> {distance_sentence} Its temperature is consistent with {temp_sentence}. "
                f"The Gaia surface-gravity estimate suggests: {class_sentence}. "
                "Radial velocity is marked unavailable when Gaia did not obtain a usable line-of-sight speed measurement."
                "</div>"
            ))
'''

if old_summary not in source:
    raise RuntimeError("Could not apply the CMB-0013 concise-table patch.")
source = source.replace(old_summary, new_summary, 1)

source = source.replace(
    "The image contains no supplied-coordinate circle. Gaia catalogue sources remain as crosses, and the nearest source is summarized below the image.",
    "Black-background image, Gaia crosses, one concise summary table, and no 28-source catalogue dump.",
    1,
)

namespace = {"__name__": "__main__", "__file__": "CMB-0013.py"}
exec(compile(source, "CMB-0013.py", "exec"), namespace, namespace)
