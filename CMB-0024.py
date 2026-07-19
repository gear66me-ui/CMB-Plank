"""CMB-0024 — Interactive S2 orbit widget around Sagittarius A*.

Uses published GRAVITY orbital parameters to show the apparent orbit of S2,
its model position at a selected epoch, projected separation, 3-D orbital
separation, and the Galactic-center distance derived from the S2 orbit fit.
This is a scientific orbit visualization, not an AI-generated image.
"""
from __future__ import annotations

import math
from datetime import date

import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

VERSION = "CMB-0024"

# GRAVITY Collaboration orbital solution (A&A 2021/2022-era solution)
A_MAS = 124.982
ECC = 0.884215
INC_DEG = 134.685
ARG_PERI_DEG = 66.259
NODE_DEG = 227.175
PERIOD_YR = 16.0458
T_PERI_YR = 2018.378990
R0_PC = 8274.9
R0_STAT_PC = 9.3
R0_SYS_PC = 33.0

# Sagittarius A* reference coordinate (ICRS, approximate radio position)
SGRA_RA = "17:45:40.03"
SGRA_DEC = "-29:00:28.2"


def decimal_year(y: int, m: int, d: int) -> float:
    start = date(y, 1, 1)
    end = date(y + 1, 1, 1)
    now = date(y, m, d)
    return y + (now - start).days / (end - start).days


def solve_kepler(mean_anomaly: np.ndarray | float, e: float) -> np.ndarray:
    M = np.asarray(mean_anomaly, dtype=float)
    E = M.copy()
    for _ in range(40):
        step = (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
        E -= step
        if np.nanmax(np.abs(step)) < 1e-13:
            break
    return E


def orbit_at_epoch(epoch: np.ndarray | float):
    t = np.asarray(epoch, dtype=float)
    M = 2.0 * np.pi * ((t - T_PERI_YR) / PERIOD_YR)
    E = solve_kepler(M, ECC)
    nu = 2.0 * np.arctan2(
        np.sqrt(1.0 + ECC) * np.sin(E / 2.0),
        np.sqrt(1.0 - ECC) * np.cos(E / 2.0),
    )
    r_mas = A_MAS * (1.0 - ECC * np.cos(E))

    inc = np.deg2rad(INC_DEG)
    omega = np.deg2rad(ARG_PERI_DEG)
    node = np.deg2rad(NODE_DEG)
    u = omega + nu

    east_mas = r_mas * (
        np.cos(node) * np.cos(u)
        - np.sin(node) * np.sin(u) * np.cos(inc)
    )
    north_mas = r_mas * (
        np.sin(node) * np.cos(u)
        + np.cos(node) * np.sin(u) * np.cos(inc)
    )
    projected_mas = np.hypot(east_mas, north_mas)
    return east_mas, north_mas, r_mas, projected_mas


def fmt(value: float, digits: int = 3) -> str:
    return f"{float(value):,.{digits}f}"


header = widgets.HTML(value=f"""
<div style='padding:12px 16px;border-radius:10px;background:#07131f;color:white;font-family:Arial,sans-serif;'>
  <div style='font-size:22px;font-weight:700;'>S2 ORBIT AROUND SAGITTARIUS A* — {VERSION}</div>
  <div style='font-size:13px;margin-top:4px;'>Sgr A*: RA {SGRA_RA}, Dec {SGRA_DEC}</div>
  <div style='font-size:12px;opacity:.8;margin-top:4px;'>Published GRAVITY orbital solution · scientific model plot · no generated sky image</div>
</div>
""")

epoch_slider = widgets.FloatSlider(
    value=decimal_year(2026, 7, 18),
    min=1992.0,
    max=2035.0,
    step=0.01,
    description="Epoch:",
    continuous_update=False,
    readout_format=".2f",
    layout=widgets.Layout(width="650px"),
)
now_button = widgets.Button(description="Set 2026-07-18", icon="calendar", layout=widgets.Layout(width="170px"))
output = widgets.Output()


def render(_=None):
    with output:
        clear_output(wait=True)
        epoch = float(epoch_slider.value)
        years = np.linspace(T_PERI_YR - PERIOD_YR, T_PERI_YR + PERIOD_YR, 1600)
        east, north, _, _ = orbit_at_epoch(years)
        e0, n0, r0_mas, projected_mas = orbit_at_epoch(epoch)
        e0 = float(np.asarray(e0))
        n0 = float(np.asarray(n0))
        r0_mas = float(np.asarray(r0_mas))
        projected_mas = float(np.asarray(projected_mas))

        # At distance R0, 1 mas subtends R0[kpc] AU.
        au_per_mas = R0_PC / 1000.0
        true_sep_au = r0_mas * au_per_mas
        projected_au = projected_mas * au_per_mas
        pericentre_au = A_MAS * (1.0 - ECC) * au_per_mas
        apocentre_au = A_MAS * (1.0 + ECC) * au_per_mas

        fig, ax = plt.subplots(figsize=(8.5, 8.5), facecolor="black")
        ax.set_facecolor("black")
        ax.plot(east, north, linewidth=1.2, label="S2 apparent orbit")
        ax.scatter([0], [0], marker="x", s=120, linewidths=2.0, label="Sagittarius A*")
        ax.scatter([e0], [n0], s=85, marker="o", label=f"S2 at {epoch:.2f}", zorder=5)
        ax.plot([0, e0], [0, n0], linestyle=":", linewidth=0.9)
        ax.set_aspect("equal", adjustable="box")
        ax.invert_xaxis()  # astronomical convention: east to the left
        ax.set_xlabel("Offset east-west (mas; east left)", color="white")
        ax.set_ylabel("Offset north-south (mas)", color="white")
        ax.set_title("Apparent orbit of S2 around Sagittarius A*", color="white")
        ax.tick_params(colors="white")
        ax.grid(alpha=0.18, linestyle=":")
        legend = ax.legend(facecolor="#111111", edgecolor="#666666")
        for text in legend.get_texts():
            text.set_color("white")
        fig.tight_layout()
        plt.show()

        rows = [
            ("Selected epoch", f"{epoch:.3f}"),
            ("S2 east-west offset", f"{e0:+.3f} mas"),
            ("S2 north-south offset", f"{n0:+.3f} mas"),
            ("Projected angular separation", f"{projected_mas:.3f} mas / {projected_mas/1000:.6f} arcsec"),
            ("Projected physical separation", f"{fmt(projected_au, 1)} AU"),
            ("Model 3-D orbital separation", f"{fmt(true_sep_au, 1)} AU"),
            ("Pericentre distance", f"{fmt(pericentre_au, 1)} AU"),
            ("Apocentre distance", f"{fmt(apocentre_au, 1)} AU"),
            ("Orbital period", f"{PERIOD_YR:.4f} years"),
            ("Orbital eccentricity", f"{ECC:.6f}"),
            ("Galactic-center distance from S2 fit", f"{R0_PC:,.1f} ± {R0_STAT_PC:.1f} stat ± {R0_SYS_PC:.1f} sys pc"),
            ("Galactic-center distance", f"{R0_PC/1000:.4f} kpc / {R0_PC*3.26156:,.0f} light-years"),
        ]
        html_rows = "".join(
            f"<tr><td style='padding:8px 12px;border-bottom:1px solid #2f3944;font-weight:600;color:#b9d8ef;'>{k}</td>"
            f"<td style='padding:8px 12px;border-bottom:1px solid #2f3944;color:#f4f7fa;'>{v}</td></tr>"
            for k, v in rows
        )
        display(widgets.HTML(value=f"""
        <div style='background:#080c11;border:1px solid #34404c;border-radius:10px;overflow:hidden;font-family:Arial,sans-serif;'>
          <div style='padding:11px 14px;background:#14202b;color:white;font-size:18px;font-weight:700;'>S2 orbit and distance results</div>
          <table style='width:100%;border-collapse:collapse;font-size:14px;'>{html_rows}</table>
        </div>
        <div style='margin-top:10px;padding:11px 13px;background:#fff8db;border-left:4px solid #e0a800;font:13px/1.45 Arial,sans-serif;'>
          <b>Important:</b> S2 is not a Gaia target and it does not have one fixed coordinate. Its apparent position changes measurably as it orbits Sagittarius A*. The distance shown here comes from fitting the full angular orbit together with spectroscopy—not from ordinary parallax.
        </div>
        """))


def set_now(_):
    epoch_slider.value = decimal_year(2026, 7, 18)


now_button.on_click(set_now)
epoch_slider.observe(render, names="value")
display(widgets.VBox([header, widgets.HBox([epoch_slider, now_button]), output]))
render()
