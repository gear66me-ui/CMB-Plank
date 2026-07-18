"""CMB-0014 — Gaia image with reliable compact stellar summary.

Run with:
    %run CMB-0014.py

This version keeps the black-background real survey image, removes the supplied
coordinate circle, keeps Gaia source crosses, and renders the nearest-source
summary as explicit HTML so the table always appears inside Colab output.
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
        headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/14.0"},
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
source = source.replace('VERSION = "CMB-0012"', 'VERSION = "CMB-0014"', 1)
source = source.replace(
    'Mozilla/5.0 CMB-Gaia-Widget/12.0',
    'Mozilla/5.0 CMB-Gaia-Widget/14.0',
)

old_figure = '''            fig = plt.figure(figsize=(10, 9))
            ax = fig.add_subplot(111, projection=wcs)
'''
new_figure = '''            fig = plt.figure(figsize=(10, 9), facecolor="black")
            ax = fig.add_subplot(111, projection=wcs)
            ax.set_facecolor("black")
'''
if old_figure not in source:
    raise RuntimeError("Could not apply the CMB-0014 dark-background patch.")
source = source.replace(old_figure, new_figure, 1)

old_axes = '''            ax.set_xlabel("Right ascension (ICRS)")
            ax.set_ylabel("Declination (ICRS)")
            ax.grid(color="white", alpha=0.18, linestyle=":")
            ax.legend(loc="upper right")
            ax.set_title(f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin · Gaia radius {radius_widget.value:g} arcmin\nGaia DR3 sources shown as crosses; no supplied-coordinate circle")
'''
new_axes = '''            ax.set_xlabel("Right ascension (ICRS)", color="white")
            ax.set_ylabel("Declination (ICRS)", color="white")
            ax.tick_params(colors="white")
            ax.coords[0].set_ticklabel(color="white")
            ax.coords[1].set_ticklabel(color="white")
            ax.coords[0].set_axislabel("Right ascension (ICRS)", color="white")
            ax.coords[1].set_axislabel("Declination (ICRS)", color="white")
            ax.grid(color="white", alpha=0.18, linestyle=":")
            legend = ax.legend(loc="upper right", facecolor="#111111", edgecolor="#777777")
            for text in legend.get_texts():
                text.set_color("white")
            ax.set_title(
                f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin\nGaia DR3 sources",
                color="white",
            )
'''
if old_axes not in source:
    raise RuntimeError("Could not apply the CMB-0014 dark-axis patch.")
source = source.replace(old_axes, new_axes, 1)

old_summary_start = '''            summary = pd.DataFrame([
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
'''

new_summary = '''            rows = [
                ("Gaia DR3 source ID", str(int(nearest["source_id"]))),
                ("G apparent magnitude", _fmt(nearest.get("phot_g_mean_mag"), 3)),
                ("Color index (BP − RP)", _fmt(nearest.get("bp_rp"), 3)),
                ("Parallax", _fmt(nearest.get("parallax"), 4, " mas")),
                ("Distance", f"{distance_pc:,.1f} pc · {distance_ly:,.1f} light-years" if _finite(distance_pc) else "Unavailable from Gaia DR3"),
                ("Effective temperature", _fmt(teff, 0, " K")),
                ("Likely spectral type", _spectral_from_teff(teff)),
                ("Likely stellar class", _luminosity_class(logg)),
                ("Approximate optical luminosity", _fmt(approx_lum, 3, " × Sun")),
                ("Proper motion RA", _fmt(nearest.get("pmra"), 3, " mas/yr")),
                ("Proper motion Dec", _fmt(nearest.get("pmdec"), 3, " mas/yr")),
                ("Radial velocity", _fmt(nearest.get("radial_velocity"), 3, " km/s")),
            ]

            table_rows = "".join(
                f"<tr><td>{prop}</td><td>{value}</td></tr>" for prop, value in rows
            )
            table_html = f"""
            <div style='margin-top:14px;background:#080c11;color:#f4f7fa;border:1px solid #34404c;border-radius:10px;overflow:hidden;font-family:Arial,sans-serif;'>
              <div style='padding:12px 14px;background:#14202b;font-size:18px;font-weight:700;'>Nearest Gaia source summary</div>
              <table style='width:100%;border-collapse:collapse;font-size:14px;'>
                <thead><tr><th style='padding:9px 12px;text-align:left;background:#1d2a36;border-bottom:1px solid #3e4b58;'>Property</th><th style='padding:9px 12px;text-align:left;background:#1d2a36;border-bottom:1px solid #3e4b58;'>Gaia result</th></tr></thead>
                <tbody>{table_rows}</tbody>
              </table>
            </div>
            <style>
              table tbody tr:nth-child(even) {{ background:#101821; }}
              table tbody td {{ padding:9px 12px;border-bottom:1px solid #29343f;vertical-align:top; }}
              table tbody td:first-child {{ width:42%;font-weight:600;color:#b9d8ef; }}
            </style>
            """
            display(widgets.HTML(value=table_html))

            if _finite(distance_pc):
                distance_text = f"It is approximately {distance_ly:,.0f} light-years away."
            else:
                distance_text = "Gaia does not provide a reliable positive distance for this source."

            display(widgets.HTML(value=f"""
            <div style='margin-top:10px;padding:12px 14px;background:#101821;color:#eef4f8;border-left:4px solid #4fc3f7;border-radius:7px;font:14px/1.55 Arial,sans-serif;'>
              <b>Summary:</b> {distance_text}
              Its temperature points to <b>{_spectral_from_teff(teff)}</b>, and its surface gravity suggests
              <b>{_luminosity_class(logg)}</b>. G magnitude is the brightness Gaia sees from Earth;
              lower numbers are brighter. Luminosity is an approximate intrinsic optical brightness relative to the Sun.
            </div>
            """))
'''

if old_summary_start not in source:
    raise RuntimeError("Could not apply the CMB-0014 reliable-summary patch.")
source = source.replace(old_summary_start, new_summary, 1)

source = source.replace(
    "The image contains no supplied-coordinate circle. Gaia catalogue sources remain as crosses, and the nearest source is summarized below the image.",
    "Black-background image, Gaia crosses, and one guaranteed HTML stellar-summary table. No multi-source catalogue dump.",
    1,
)

namespace = {"__name__": "__main__", "__file__": "CMB-0014.py"}
exec(compile(source, "CMB-0014.py", "exec"), namespace, namespace)
