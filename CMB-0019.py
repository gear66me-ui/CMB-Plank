"""CMB-0019 — Gaia star study widget with image crosshairs and X/Y intensity profiles.

Target: RA 03:19:30.85, Dec -21:45:24.1
"""
from __future__ import annotations
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/gear66me-ui/CMB-Plank/main/CMB-0012.py"
req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0 CMB-Gaia-Widget/19.0"})
with urllib.request.urlopen(req, timeout=60) as r:
    source = r.read().decode("utf-8")

replacements = [
    ('VERSION = "CMB-0012"', 'VERSION = "CMB-0019"'),
    ('RA_SEXAGESIMAL = "03:12:59.96"', 'RA_SEXAGESIMAL = "03:19:30.85"'),
    ('DEC_SEXAGESIMAL = "-20:02:09.0"', 'DEC_SEXAGESIMAL = "-21:45:24.1"'),
    ('RA_DEG = 48.2498333333', 'RA_DEG = 49.8785416667'),
    ('DEC_DEG = -20.0358333333', 'DEC_DEG = -21.7566944444'),
    ('Mozilla/5.0 CMB-Gaia-Widget/12.0', 'Mozilla/5.0 CMB-Gaia-Widget/19.0'),
]
for old, new in replacements:
    if old not in source:
        raise RuntimeError(f"CMB-0019 could not find required base text: {old}")
    source = source.replace(old, new)

old_plot = '''            fig = plt.figure(figsize=(10, 9))
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
'''

new_plot = '''            from matplotlib.gridspec import GridSpec

            fig = plt.figure(figsize=(12, 10), facecolor="black")
            gs = GridSpec(2, 2, width_ratios=[4.2, 1.35], height_ratios=[1.35, 4.2], hspace=0.08, wspace=0.08)
            ax_x = fig.add_subplot(gs[0, 0])
            ax = fig.add_subplot(gs[1, 0], projection=wcs)
            ax_y = fig.add_subplot(gs[1, 1])
            ax_blank = fig.add_subplot(gs[0, 1])
            ax_blank.axis("off")
            ax.set_facecolor("black")
            ax_x.set_facecolor("black")
            ax_y.set_facecolor("black")

            if data.ndim == 3 and data.shape[0] in (3, 4):
                image = np.moveaxis(data[:3], 0, -1)
                finite = np.isfinite(image)
                if np.any(finite):
                    lo, hi = np.nanpercentile(image[finite], [1, 99.5])
                    image = np.clip((image - lo) / max(hi - lo, 1e-12), 0, 1)
                ax.imshow(image, origin="lower")
                intensity = np.nanmean(image, axis=2)
            else:
                image = np.squeeze(data)
                finite = np.isfinite(image)
                lo, hi = np.nanpercentile(image[finite], [1, 99.5]) if np.any(finite) else (0, 1)
                ax.imshow(image, origin="lower", cmap="gray", vmin=lo, vmax=hi)
                intensity = np.asarray(image, dtype=float)

            ny, nx = intensity.shape
            cx, cy = wcs.world_to_pixel_values(RA_DEG, DEC_DEG)
            cx = int(np.clip(round(cx), 0, nx - 1))
            cy = int(np.clip(round(cy), 0, ny - 1))

            x_profile = np.asarray(intensity[cy, :], dtype=float)
            y_profile = np.asarray(intensity[:, cx], dtype=float)
            x_pixels = np.arange(nx)
            y_pixels = np.arange(ny)

            ax.axvline(cx, color="cyan", linewidth=0.9, alpha=0.95, zorder=9)
            ax.axhline(cy, color="cyan", linewidth=0.9, alpha=0.95, zorder=9)
            ax.plot(cx, cy, marker="+", markersize=16, markeredgewidth=1.5, color="yellow", zorder=10)

            ax_x.plot(x_pixels, x_profile, linewidth=0.9)
            ax_x.axvline(cx, color="cyan", linewidth=0.9)
            ax_x.set_xlim(0, nx - 1)
            ax_x.set_ylabel("Intensity", color="white")
            ax_x.set_title("Horizontal intensity profile through crosshair", color="white", fontsize=11)
            ax_x.tick_params(colors="white", labelbottom=False)
            ax_x.grid(alpha=0.18, linestyle=":")

            ax_y.plot(y_profile, y_pixels, linewidth=0.9)
            ax_y.axhline(cy, color="cyan", linewidth=0.9)
            ax_y.set_ylim(0, ny - 1)
            ax_y.set_xlabel("Intensity", color="white")
            ax_y.set_title("Vertical profile", color="white", fontsize=11)
            ax_y.tick_params(colors="white", labelleft=False)
            ax_y.grid(alpha=0.18, linestyle=":")

            mags = pd.to_numeric(gaia["phot_g_mean_mag"], errors="coerce")
            marker_sizes = np.clip(120 - 5 * mags.fillna(20), 18, 95)
            ax.scatter(gaia["ra"], gaia["dec"], transform=ax.get_transform("world"), s=marker_sizes, marker="x", linewidths=1.15, label="Gaia DR3", zorder=7)
            ax.set_xlabel("Right ascension (ICRS)", color="white")
            ax.set_ylabel("Declination (ICRS)", color="white")
            ax.tick_params(colors="white")
            ax.grid(color="white", alpha=0.18, linestyle=":")
            legend = ax.legend(loc="upper right", facecolor="#111111", edgecolor="#777777")
            [t.set_color("white") for t in legend.get_texts()]
            ax.set_title(f"{survey_widget.value} · FOV {fov_widget.value:g} arcmin\nGaia DR3 crosses + coordinate crosshair", color="white")
            fig.suptitle(f"{VERSION} — X/Y intensity cuts at RA {RA_SEXAGESIMAL}, Dec {DEC_SEXAGESIMAL}", color="white", fontsize=13)
            plt.show()
'''

if old_plot not in source:
    raise RuntimeError("CMB-0019 could not safely replace the plotting section in CMB-0012.")
source = source.replace(old_plot, new_plot, 1)

# Remove the large catalogue dump but retain the nearest-source summary.
start = source.find('            cols = ["source_id","separation_arcsec"')
if start != -1:
    end = source.find('\n\n        except Exception as exc:', start)
    if end != -1:
        source = source[:start] + source[end:]

# Use a compact dark HTML summary instead of pandas Styler.
old_summary = '            print("\\nNearest Gaia source summary")\n            display(summary.style.hide(axis="index").set_properties(**{"text-align": "left"}))'
new_summary = '''            rows = [(str(r["Property"]), str(r["Nearest Gaia source"])) for _, r in summary.iterrows()]
            html_rows = "".join(
                f"<tr><td style='padding:9px 12px;border-bottom:1px solid #2e3944;font-weight:600;color:#b9d8ef;width:42%;'>{p}</td>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #2e3944;color:#f4f7fa;'>{v}</td></tr>"
                for p, v in rows
            )
            display(widgets.HTML(value=f"""
            <div style='margin-top:14px;background:#080c11;color:#f4f7fa;border:1px solid #34404c;border-radius:10px;overflow:hidden;font-family:Arial,sans-serif;'>
              <div style='padding:12px 14px;background:#14202b;font-size:18px;font-weight:700;'>Nearest Gaia source summary</div>
              <table style='width:100%;border-collapse:collapse;font-size:14px;'>
                <thead><tr><th style='padding:9px 12px;text-align:left;background:#1d2a36;'>Property</th><th style='padding:9px 12px;text-align:left;background:#1d2a36;'>Gaia result</th></tr></thead>
                <tbody>{html_rows}</tbody>
              </table>
            </div>
            """))'''
if old_summary in source:
    source = source.replace(old_summary, new_summary, 1)

namespace = {"__name__": "__main__", "__file__": "CMB-0019.py"}
exec(compile(source, "CMB-0019.py", "exec"), namespace, namespace)
