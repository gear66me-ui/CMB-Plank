# CMB-0033A-1
# FOUNDATION / APPLICATION CORE
# Replacement for the CMB-0032 runtime architecture.
# This section contains ONLY imports, configuration,
# global runtime containers and utility functions.

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import math
import os
import gc
import json
import traceback
import warnings

import numpy as np
import pandas as pd

from IPython.display import display, HTML, clear_output

import ipywidgets as widgets

warnings.filterwarnings("ignore")

# ============================================================
# VERSION
# ============================================================

VERSION = "CMB-0033"
PATCH = "33A-1"

print()
print("=" * 70)
print("CMB GALAXY INSPECTOR")
print(VERSION, PATCH)
print("=" * 70)
print()

# ============================================================
# OPTIONAL PACKAGES
# ============================================================

IPYALADIN_AVAILABLE = False

try:

    from ipyaladin import Aladin

    IPYALADIN_AVAILABLE = True

except Exception:

    Aladin = None

print("ipyaladin :", IPYALADIN_AVAILABLE)

# ============================================================
# APPLICATION OBJECT
# ============================================================

APP = {}

APP["version"] = VERSION
APP["patch"] = PATCH

APP["config"] = {}
APP["state"] = {}
APP["viewer"] = {}
APP["widgets"] = {}
APP["runtime"] = {}
APP["statistics"] = {}
APP["callbacks"] = {}
APP["registry"] = {}
APP["services"] = {}

# ============================================================
# STATE
# ============================================================

STATE = APP["state"]

STATE["coord"] = None
STATE["object"] = None
STATE["catalog"] = None
STATE["image"] = None
STATE["table"] = None

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = APP["config"]

CONFIG["viewer_engine"] = (
    "ipyaladin"
    if IPYALADIN_AVAILABLE
    else "none"
)

CONFIG["default_survey"] = "P/DSS2/color"

CONFIG["default_target"] = "M31"

CONFIG["default_fov"] = 0.15

CONFIG["viewer_height"] = "720px"

CONFIG["viewer_width"] = "100%"

# ============================================================
# STATISTICS
# ============================================================

STAT = APP["statistics"]

STAT["refreshes"] = 0
STAT["viewer_updates"] = 0
STAT["center_updates"] = 0
STAT["inspection_requests"] = 0
STAT["runtime_errors"] = 0

# ============================================================
# RUNTIME
# ============================================================

RUNTIME = APP["runtime"]

RUNTIME["initialized"] = False
RUNTIME["busy"] = False
RUNTIME["running"] = False

# ============================================================
# LOGGER
# ============================================================

def log(message):

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(
        f"[{timestamp}] {message}"
    )

# ============================================================
# ERROR LOGGER
# ============================================================

def log_exception(exc):

    STAT["runtime_errors"] += 1

    print()

    print("-" * 60)

    print(type(exc).__name__)

    print(exc)

    print("-" * 60)

# ============================================================
# SAFE FLOAT
# ============================================================

def safe_float(value, default=np.nan):

    try:

        return float(value)

    except Exception:

        return default

# ============================================================
# SAFE INTEGER
# ============================================================

def safe_int(value, default=0):

    try:

        return int(value)

    except Exception:

        return default

# ============================================================
# EXISTS
# ============================================================

def exists(name):

    return name in globals()

# ============================================================
# REGISTRY
# ============================================================

REGISTRY = APP["registry"]

def register(name, obj):

    REGISTRY[name] = obj

    return obj


def resolve(name, default=None):

    return REGISTRY.get(name, default)

# ============================================================
# SERVICE REGISTRY
# ============================================================

SERVICES = APP["services"]

def register_service(name, obj):

    SERVICES[name] = obj

    return obj

# ============================================================
# CLEAN MEMORY
# ============================================================

def runtime_cleanup():

    gc.collect()

# ============================================================
# STARTUP
# ============================================================

log("Application core initialized.")

print()
print("Version :", VERSION)
print("Patch   :", PATCH)
print("Engine  :", CONFIG["viewer_engine"])
print()
print("33A-1 COMPLETE")



# CMB-0033A-2
# RUNTIME STATE MANAGER
# Builds on CMB-0033A-1

# ============================================================
# VIEWER OBJECT
# ============================================================

VIEWER = APP["viewer"]

VIEWER["enabled"] = IPYALADIN_AVAILABLE
VIEWER["widget"] = None
VIEWER["panel"] = None
VIEWER["stack"] = None
VIEWER["native"] = None

VIEWER["last_target"] = None
VIEWER["last_survey"] = None
VIEWER["last_fov"] = None

# ============================================================
# CALLBACK REGISTRY
# ============================================================

CALLBACKS = APP["callbacks"]

CALLBACKS["widget"] = {}
CALLBACKS["button"] = {}

# ============================================================
# OBSERVER MANAGER
# ============================================================

OBSERVERS = {}

OBSERVERS["installed"] = False
OBSERVERS["count"] = 0

# ============================================================
# APPLICATION FLAGS
# ============================================================

APP["flags"] = {}

FLAGS = APP["flags"]

FLAGS["building"] = False
FLAGS["refreshing"] = False
FLAGS["centering"] = False
FLAGS["inspecting"] = False

# ============================================================
# RUNTIME LOCK
# ============================================================

def runtime_begin():

    if RUNTIME["busy"]:
        return False

    RUNTIME["busy"] = True

    return True


def runtime_end():

    RUNTIME["busy"] = False

# ============================================================
# CACHE
# ============================================================

CACHE = {}

CACHE["target"] = None
CACHE["survey"] = None
CACHE["fov"] = None

CACHE["ra"] = None
CACHE["dec"] = None

# ============================================================
# CACHE UPDATE
# ============================================================

def update_cache():

    if "target" in APP["widgets"]:

        CACHE["target"] = str(
            APP["widgets"]["target"].value
        )

    if "survey" in APP["widgets"]:

        CACHE["survey"] = str(
            APP["widgets"]["survey"].value
        )

    if "fov" in APP["widgets"]:

        CACHE["fov"] = safe_float(
            APP["widgets"]["fov"].value
        )

# ============================================================
# CHANGE DETECTOR
# ============================================================

def controls_changed():

    try:

        if "target" not in APP["widgets"]:
            return True

        if CACHE["target"] != str(APP["widgets"]["target"].value):
            return True

        if CACHE["survey"] != str(APP["widgets"]["survey"].value):
            return True

        if CACHE["fov"] != safe_float(APP["widgets"]["fov"].value):
            return True

    except Exception:

        return True

    return False

# ============================================================
# RUNTIME RESET
# ============================================================

def reset_runtime():

    RUNTIME["running"] = False
    RUNTIME["busy"] = False

    STAT["refreshes"] = 0
    STAT["viewer_updates"] = 0
    STAT["center_updates"] = 0
    STAT["inspection_requests"] = 0

# ============================================================
# APPLICATION HEALTH
# ============================================================

def application_health():

    print()

    print("APPLICATION HEALTH")

    print("----------------------------")

    print(
        "Viewer Enabled :",
        VIEWER["enabled"]
    )

    print(
        "Initialized    :",
        RUNTIME["initialized"]
    )

    print(
        "Busy           :",
        RUNTIME["busy"]
    )

    print(
        "Widgets        :",
        len(APP["widgets"])
    )

    print(
        "Registry       :",
        len(REGISTRY)
    )

    print(
        "Services       :",
        len(SERVICES)
    )

# ============================================================
# APPLICATION SUMMARY
# ============================================================

def application_summary():

    print()

    print("STATISTICS")

    print("----------------------------")

    for key in sorted(STAT):

        print(f"{key:24s} {STAT[key]}")

# ============================================================
# STARTUP
# ============================================================

reset_runtime()

update_cache()

register("VIEWER", VIEWER)
register("CACHE", CACHE)
register("STATISTICS", STAT)

register_service(
    "runtime",
    RUNTIME
)

register_service(
    "viewer",
    VIEWER
)

RUNTIME["initialized"] = True

log("Runtime initialized.")

print()

print("Viewer Engine :", CONFIG["viewer_engine"])
print("Runtime Ready :", RUNTIME["initialized"])
print("Registry Size :", len(REGISTRY))

print()

print("33A-2 COMPLETE")


# CMB-0033B-1
# VIEWER + CONTROL WIDGETS
# Requires:
#   CMB-0033A-1
#   CMB-0033A-2

print()
print("Building widgets...")

# ============================================================
# TARGET
# ============================================================

target = widgets.Text(
    value=CONFIG["default_target"],
    description="Target",
    placeholder="NGC, JADES, RA DEC...",
    layout=widgets.Layout(width="100%"),
)

# ============================================================
# SURVEY
# ============================================================

SURVEYS = [

    "P/DSS2/color",
    "P/PanSTARRS/DR1/color-z-zg-g",
    "CDS/P/DESI-Legacy-Surveys/DR10/color",
    "P/2MASS/color",
    "P/allWISE/color",
    "P/GALEXGR6/AIS/color",
    "P/Fermi/color",

]

survey = widgets.Dropdown(

    options=SURVEYS,

    value=CONFIG["default_survey"],

    description="Survey",

    layout=widgets.Layout(width="420px"),

)

# ============================================================
# FIELD OF VIEW
# ============================================================

fov = widgets.FloatSlider(

    value=CONFIG["default_fov"],

    min=0.01,

    max=5.0,

    step=0.01,

    description="FOV",

    continuous_update=False,

    readout_format=".2f",

    layout=widgets.Layout(width="420px"),

)

# ============================================================
# NATIVE VIEWER SWITCH
# ============================================================

use_native = widgets.Checkbox(

    value=IPYALADIN_AVAILABLE,

    description="Use Native ipyaladin",

)

# ============================================================
# STATUS
# ============================================================

status = widgets.HTML(

    value="<b>Ready.</b>",

    layout=widgets.Layout(width="100%"),

)

# ============================================================
# HEADER
# ============================================================

header = widgets.HTML(

    f"""

<h2>

CMB Galaxy Inspector

</h2>

<b>{VERSION}</b>

"""

)

# ============================================================
# BUTTONS
# ============================================================

inspect_button = widgets.Button(

    description="Inspect",

    icon="search",

    button_style="primary",

)

center_button = widgets.Button(

    description="Center",

    icon="crosshairs",

    button_style="info",

)

refresh_button = widgets.Button(

    description="Refresh",

    icon="refresh",

)

# ============================================================
# CONTROL BAR
# ============================================================

button_bar = widgets.HBox(

    [

        inspect_button,

        center_button,

        refresh_button,

    ]

)

controls = widgets.VBox(

    [

        target,

        survey,

        fov,

        button_bar,

        use_native,

    ],

    layout=widgets.Layout(width="100%"),

)

# ============================================================
# BUILD ALADIN
# ============================================================

if IPYALADIN_AVAILABLE:

    try:

        aladin = Aladin(

            target=CONFIG["default_target"],

            survey=CONFIG["default_survey"],

            fov=CONFIG["default_fov"],

            layout=widgets.Layout(

                width=CONFIG["viewer_width"],

                height=CONFIG["viewer_height"],

            ),

        )

    except Exception as exc:

        log_exception(exc)

        aladin = widgets.HTML(

            "<b style='color:red'>"

            "Failed to initialize ipyaladin."

            "</b>"

        )

else:

    aladin = widgets.HTML(

        "<b style='color:#b71c1c'>"

        "ipyaladin not installed."

        "</b>"

    )

# ============================================================
# PLACEHOLDER CLASSIC VIEWER
# ============================================================

classic_viewer = widgets.Output(

    layout=widgets.Layout(

        width="100%",

        height=CONFIG["viewer_height"],

        border="1px solid lightgray",

    )

)

with classic_viewer:

    print("Classic matplotlib viewer placeholder.")

# ============================================================
# STACK
# ============================================================

viewer_stack = widgets.VBox(

    children=[

        classic_viewer,

        aladin,

    ],

    selected_index=1 if IPYALADIN_AVAILABLE else 0,

    layout=widgets.Layout(

        width="100%",

        height=CONFIG["viewer_height"],

    ),

)

# ============================================================
# VIEWER PANEL
# ============================================================

viewer_panel = widgets.VBox(

    [

        viewer_stack,

    ],

    layout=widgets.Layout(width="100%"),

)

# ============================================================
# REGISTER EVERYTHING
# ============================================================

for name, obj in {

    "target": target,

    "survey": survey,

    "fov": fov,

    "header": header,

    "controls": controls,

    "status": status,

    "inspect_button": inspect_button,

    "center_button": center_button,

    "refresh_button": refresh_button,

    "viewer_stack": viewer_stack,

    "viewer_panel": viewer_panel,

    "aladin": aladin,

}.items():

    APP["widgets"][name] = obj

    register(name, obj)

VIEWER["widget"] = aladin
VIEWER["stack"] = viewer_stack
VIEWER["panel"] = viewer_panel
VIEWER["native"] = aladin

print()

print("Widgets built :", len(APP["widgets"]))

print("Viewer ready.")

print()

print("CMB-0033B-1 COMPLETE")




# CMB-0033B-2
# CALLBACK ENGINE
# Single runtime dispatcher for the entire application.

print()
print("Building callback engine...")

# ============================================================
# VIEWER SYNCHRONIZATION
# ============================================================

def sync_viewer():

    if not VIEWER["enabled"]:
        return

    widget = VIEWER["widget"]

    try:

        widget.target = str(target.value)

    except Exception as exc:

        log_exception(exc)

    try:

        widget.survey = str(survey.value)

    except Exception as exc:

        log_exception(exc)

    try:

        widget.fov = float(fov.value)

    except Exception as exc:

        log_exception(exc)

    VIEWER["last_target"] = str(target.value)
    VIEWER["last_survey"] = str(survey.value)
    VIEWER["last_fov"] = float(fov.value)

    STAT["viewer_updates"] += 1


# ============================================================
# CENTER CURRENT OBJECT
# ============================================================

def center_current_object():

    obj = STATE.get("object")

    if obj is None:
        return

    ra = safe_float(obj.get("RA"))
    dec = safe_float(obj.get("Dec"))

    if not np.isfinite(ra):
        return

    if not np.isfinite(dec):
        return

    try:

        VIEWER["widget"].target = f"{ra} {dec}"

        CACHE["ra"] = ra
        CACHE["dec"] = dec

        STAT["center_updates"] += 1

    except Exception as exc:

        log_exception(exc)


# ============================================================
# MAIN APPLICATION REFRESH
# ============================================================

def application_refresh(force=False):

    if not runtime_begin():
        return

    try:

        changed = controls_changed()

        if force or changed:

            sync_viewer()

            update_cache()

            STAT["refreshes"] += 1

    finally:

        runtime_end()


# ============================================================
# INSPECTION COMPLETE
# ============================================================

def inspection_complete():

    STAT["inspection_requests"] += 1

    center_current_object()


# ============================================================
# WIDGET CALLBACK
# ============================================================

def widget_changed(change):

    application_refresh()


# ============================================================
# BUTTON CALLBACKS
# ============================================================

def refresh_clicked(button):

    application_refresh(force=True)


def center_clicked(button):

    center_current_object()


def inspect_clicked(button):

    try:

        robust_inspect_galaxy(button)

    except NameError:

        log(
            "robust_inspect_galaxy() "
            "will be installed in Section C."
        )

    except Exception as exc:

        log_exception(exc)

    inspection_complete()


# ============================================================
# VIEWER TOGGLE
# ============================================================

def native_toggle(change):

    if change["new"]:

        viewer_stack.selected_index = 1

    else:

        viewer_stack.selected_index = 0


# ============================================================
# REMOVE OLD OBSERVERS
# ============================================================

for widget in (

    target,

    survey,

    fov,

    use_native,

):

    try:

        widget.unobserve_all("value")

    except Exception:

        pass


# ============================================================
# REGISTER OBSERVERS
# ============================================================

target.observe(

    widget_changed,

    names="value",

)

survey.observe(

    widget_changed,

    names="value",

)

fov.observe(

    widget_changed,

    names="value",

)

use_native.observe(

    native_toggle,

    names="value",

)


refresh_button.on_click(

    refresh_clicked

)

center_button.on_click(

    center_clicked

)

inspect_button.on_click(

    inspect_clicked

)


# ============================================================
# CALLBACK REGISTRY
# ============================================================

CALLBACKS["widget"]["target"] = widget_changed
CALLBACKS["widget"]["survey"] = widget_changed
CALLBACKS["widget"]["fov"] = widget_changed

CALLBACKS["button"]["refresh"] = refresh_clicked
CALLBACKS["button"]["center"] = center_clicked
CALLBACKS["button"]["inspect"] = inspect_clicked

OBSERVERS["installed"] = True

OBSERVERS["count"] = (

    len(CALLBACKS["widget"])

    +

    len(CALLBACKS["button"])

)

# ============================================================
# INITIAL SYNCHRONIZATION
# ============================================================

application_refresh(force=True)

# ============================================================
# STATUS
# ============================================================

status.value = (

    "<b style='color:#2e7d32'>"

    "Callback engine initialized.<br>"

    "Single runtime dispatcher active."

    "</b>"

)

print()

print("Observers Installed :", OBSERVERS["installed"])

print("Callback Count      :", OBSERVERS["count"])

print("Viewer Updates      :", STAT["viewer_updates"])

print()

print("CMB-0033B-2 COMPLETE")


# CMB-0033C-1
# COORDINATE ENGINE
# Replaces the multiple coordinate wrappers from CMB-0032

print()
print("Building coordinate engine...")

# ============================================================
# COORDINATE SUPPORT
# ============================================================

ASTROPY_AVAILABLE = False

try:

    from astropy.coordinates import SkyCoord
    import astropy.units as u

    ASTROPY_AVAILABLE = True

except Exception:

    SkyCoord = None
    u = None

print("Astropy :", ASTROPY_AVAILABLE)

# ============================================================
# COORDINATE PARSER
# ============================================================

def build_coordinate(value):

    """
    Accepts:
        Object name
        RA DEC decimal
        Existing SkyCoord

    Returns:
        SkyCoord or None
    """

    if not ASTROPY_AVAILABLE:
        return None

    if isinstance(value, SkyCoord):
        return value

    if value is None:
        return None

    text = str(value).strip()

    if len(text) == 0:
        return None

    # Decimal RA DEC

    pieces = text.split()

    if len(pieces) == 2:

        try:

            ra = float(pieces[0])
            dec = float(pieces[1])

            return SkyCoord(

                ra=ra*u.deg,
                dec=dec*u.deg,
                frame="icrs"

            )

        except Exception:

            pass

    # Name resolution

    try:

        return SkyCoord.from_name(text)

    except Exception:

        return None


# ============================================================
# STORE COORDINATE
# ============================================================

def set_coordinate(coord):

    STATE["coord"] = coord

    if coord is None:
        return

    CACHE["ra"] = coord.ra.deg
    CACHE["dec"] = coord.dec.deg


# ============================================================
# REFRESH COORDINATE
# ============================================================

def refresh_coordinates():

    coord = build_coordinate(target.value)

    set_coordinate(coord)

    if coord is None:

        status.value = (

            "<span style='color:#c62828'>"

            "Unable to resolve target."

            "</span>"

        )

        return False

    if VIEWER["enabled"]:

        try:

            VIEWER["widget"].target = (

                f"{coord.ra.deg:.8f} "

                f"{coord.dec.deg:.8f}"

            )

        except Exception as exc:

            log_exception(exc)

    status.value = (

        "<span style='color:#2e7d32'>"

        f"Resolved: "

        f"RA={coord.ra.deg:.6f}° "

        f"DEC={coord.dec.deg:.6f}°"

        "</span>"

    )

    return True


# ============================================================
# CURRENT OBJECT
# ============================================================

def current_object():

    return STATE.get("object")


# ============================================================
# CENTER CURRENT OBJECT
# ============================================================

def center_object():

    obj = current_object()

    if obj is None:

        refresh_coordinates()

        return

    ra = safe_float(obj.get("RA"))
    dec = safe_float(obj.get("Dec"))

    if not np.isfinite(ra):
        return

    if not np.isfinite(dec):
        return

    try:

        VIEWER["widget"].target = (

            f"{ra:.8f} {dec:.8f}"

        )

    except Exception as exc:

        log_exception(exc)

    CACHE["ra"] = ra
    CACHE["dec"] = dec

    STAT["center_updates"] += 1


# ============================================================
# LOAD OBJECT INTO STATE
# ============================================================

def load_object(record):

    if record is None:

        STATE["object"] = None

        return

    STATE["object"] = dict(record)

    ra = safe_float(record.get("RA"))
    dec = safe_float(record.get("Dec"))

    if np.isfinite(ra):

        CACHE["ra"] = ra

    if np.isfinite(dec):

        CACHE["dec"] = dec


# ============================================================
# COORDINATE SUMMARY
# ============================================================

def coordinate_summary():

    print()

    print("COORDINATE STATUS")

    print("-------------------------")

    print("Coordinate :", STATE["coord"])

    print("RA Cache   :", CACHE["ra"])

    print("DEC Cache  :", CACHE["dec"])

    obj = STATE.get("object")

    if obj is None:

        print("Current Object : None")

    else:

        print(

            "Current Object :",

            obj.get("Object", "<unnamed>")

        )


# ============================================================
# INITIAL SYNCHRONIZATION
# ============================================================

refresh_coordinates()

print()

print("Coordinate engine ready.")

print("CMB-0033C-1 COMPLETE")


# CMB-0033C-2
# GALAXY INSPECTION ENGINE
# Single inspection pipeline for CMB-0033

print()
print("Building inspection engine...")

# ============================================================
# INSPECTION RESULT
# ============================================================

def clear_current_object():

    STATE["object"] = None

    CACHE["ra"] = None
    CACHE["dec"] = None


# ============================================================
# UPDATE STATUS
# ============================================================

def set_status(message, color="#2e7d32"):

    status.value = (

        f"<span style='color:{color}'>"

        f"{message}"

        "</span>"

    )


# ============================================================
# FIND OBJECT
# ============================================================

def find_selected_object():

    """
    Returns the currently selected catalog object.

    Later notebook sections can replace this implementation
    with catalog-specific logic without changing the rest
    of the runtime.
    """

    obj = STATE.get("object")

    if obj is not None:
        return obj

    table = STATE.get("table")

    if table is None:
        return None

    try:

        if len(table) == 0:
            return None

        row = table.iloc[0]

        return dict(row)

    except Exception:

        return None


# ============================================================
# LOAD OBJECT
# ============================================================

def load_selected_object():

    obj = find_selected_object()

    if obj is None:

        clear_current_object()

        return None

    load_object(obj)

    return obj


# ============================================================
# VIEWER CENTER
# ============================================================

def viewer_center_object():

    obj = current_object()

    if obj is None:
        return False

    ra = safe_float(obj.get("RA"))
    dec = safe_float(obj.get("Dec"))

    if not np.isfinite(ra):
        return False

    if not np.isfinite(dec):
        return False

    try:

        if VIEWER["enabled"]:

            VIEWER["widget"].target = (

                f"{ra:.8f} {dec:.8f}"

            )

    except Exception as exc:

        log_exception(exc)

    CACHE["ra"] = ra
    CACHE["dec"] = dec

    return True


# ============================================================
# REFRESH VIEWER
# ============================================================

def refresh_viewer():

    sync_viewer()

    viewer_center_object()


# ============================================================
# MAIN INSPECTION
# ============================================================

def robust_inspect_galaxy(button=None):

    if FLAGS["inspecting"]:
        return

    FLAGS["inspecting"] = True

    try:

        obj = load_selected_object()

        if obj is None:

            set_status(

                "No galaxy selected.",

                "#b71c1c"

            )

            return

        refresh_viewer()

        STAT["inspection_requests"] += 1

        set_status(

            "Galaxy inspection complete."

        )

    except Exception as exc:

        log_exception(exc)

        set_status(

            str(exc),

            "#b71c1c"

        )

    finally:

        FLAGS["inspecting"] = False


# ============================================================
# INSPECTION REPORT
# ============================================================

def inspection_summary():

    print()

    print("INSPECTION")

    print("-------------------------")

    print(

        "Requests :",

        STAT["inspection_requests"]

    )

    obj = STATE.get("object")

    if obj is None:

        print("Current Object : None")

        return

    for key in sorted(obj):

        print(f"{key:20s}", obj[key])


# ============================================================
# BUTTON REWIRE
# ============================================================

try:

    inspect_button._click_handlers.callbacks.clear()

except Exception:

    pass

inspect_button.on_click(

    robust_inspect_galaxy

)

# ============================================================
# REGISTER
# ============================================================

register(

    "robust_inspect_galaxy",

    robust_inspect_galaxy

)

register(

    "viewer_center_object",

    viewer_center_object

)

register(

    "refresh_viewer",

    refresh_viewer

)

register_service(

    "inspection",

    robust_inspect_galaxy

)

print()

print("Inspection engine ready.")

print("Inspection callback installed.")

print()

print("CMB-0033C-2 COMPLETE")

# CMB-0033D-1
# RUNTIME LOOP
# Unified execution pipeline

print()
print("Building runtime manager...")

# ============================================================
# HEARTBEAT
# ============================================================

RUNTIME["heartbeat"] = 0
RUNTIME["last_refresh"] = None
RUNTIME["last_target"] = None

# ============================================================
# STATUS BAR
# ============================================================

def update_status_bar():

    target_name = str(target.value)

    status.value = (
        "<b style='color:#2e7d32'>"
        f"Target: {target_name}"
        f"<br>"
        f"Refreshes: {STAT['refreshes']}"
        f" | Viewer: {STAT['viewer_updates']}"
        f" | Inspections: {STAT['inspection_requests']}"
        "</b>"
    )

# ============================================================
# MAIN REFRESH
# ============================================================

def refresh_runtime(force=False):

    if not runtime_begin():
        return

    try:

        changed = controls_changed()

        if force or changed:

            refresh_coordinates()

            sync_viewer()

            update_cache()

            update_status_bar()

            RUNTIME["heartbeat"] += 1
            RUNTIME["last_target"] = str(target.value)

            STAT["refreshes"] += 1

    except Exception as exc:

        log_exception(exc)

    finally:

        runtime_end()

# ============================================================
# DISPATCHER
# ============================================================

def dispatch(event="refresh"):

    if event == "refresh":

        refresh_runtime()

    elif event == "force":

        refresh_runtime(force=True)

    elif event == "inspect":

        robust_inspect_galaxy()

    elif event == "center":

        center_object()

# ============================================================
# PERIODIC UPDATE
# ============================================================

def heartbeat():

    RUNTIME["heartbeat"] += 1

    return RUNTIME["heartbeat"]

# ============================================================
# HEALTH REPORT
# ============================================================

def runtime_summary():

    print()

    print("RUNTIME SUMMARY")

    print("----------------------------")

    print("Heartbeat :", RUNTIME["heartbeat"])
    print("Busy      :", RUNTIME["busy"])
    print("Running   :", RUNTIME["running"])
    print("Target    :", RUNTIME["last_target"])
    print("Refreshes :", STAT["refreshes"])
    print("Viewer    :", STAT["viewer_updates"])
    print("Inspect   :", STAT["inspection_requests"])

# ============================================================
# CALLBACK REWIRE
# ============================================================

def widget_runtime(change):

    dispatch("refresh")

target.unobserve_all("value")
survey.unobserve_all("value")
fov.unobserve_all("value")

target.observe(widget_runtime, names="value")
survey.observe(widget_runtime, names="value")
fov.observe(widget_runtime, names="value")

refresh_button.on_click(lambda b: dispatch("force"))
center_button.on_click(lambda b: dispatch("center"))
inspect_button.on_click(lambda b: dispatch("inspect"))

# ============================================================
# REGISTRATION
# ============================================================

register(
    "dispatch",
    dispatch
)

register(
    "refresh_runtime",
    refresh_runtime
)

register_service(
    "runtime_dispatcher",
    dispatch
)

refresh_runtime(force=True)

print()

print("Heartbeat :", RUNTIME["heartbeat"])
print("Dispatcher installed.")
print()
print("CMB-0033D-1 COMPLETE")



# CMB-0033D-2
# EVENT BUS & OBSERVER MANAGER
# Centralized notification system

print()
print("Building event bus...")

# ============================================================
# EVENT BUS
# ============================================================

EVENTS = APP.setdefault("events", {})

EVENTS["listeners"] = {}
EVENTS["history"] = []
EVENTS["enabled"] = True

# ============================================================
# SUBSCRIBE
# ============================================================

def subscribe(event_name, callback):

    listeners = EVENTS["listeners"].setdefault(
        event_name,
        []
    )

    if callback not in listeners:
        listeners.append(callback)

# ============================================================
# UNSUBSCRIBE
# ============================================================

def unsubscribe(event_name, callback):

    listeners = EVENTS["listeners"].get(
        event_name,
        []
    )

    if callback in listeners:
        listeners.remove(callback)

# ============================================================
# EMIT
# ============================================================

def emit(event_name, **payload):

    if not EVENTS["enabled"]:
        return

    EVENTS["history"].append(
        (
            event_name,
            payload,
        )
    )

    listeners = EVENTS["listeners"].get(
        event_name,
        []
    )

    for callback in list(listeners):

        try:

            callback(**payload)

        except Exception as exc:

            log_exception(exc)

# ============================================================
# HISTORY
# ============================================================

def clear_event_history():

    EVENTS["history"].clear()


def event_history(limit=20):

    print()

    print("EVENT HISTORY")

    print("---------------------------")

    history = EVENTS["history"][-limit:]

    for i, item in enumerate(history):

        name, payload = item

        print(
            f"{i+1:3d}",
            name,
            payload,
        )

# ============================================================
# OBSERVER CALLBACKS
# ============================================================

def on_refresh(**kwargs):

    update_status_bar()


def on_inspection(**kwargs):

    update_status_bar()


def on_center(**kwargs):

    update_status_bar()

# ============================================================
# REGISTER DEFAULT EVENTS
# ============================================================

subscribe(
    "refresh",
    on_refresh
)

subscribe(
    "inspection",
    on_inspection
)

subscribe(
    "center",
    on_center
)

# ============================================================
# PATCH DISPATCHER
# ============================================================

_original_dispatch = dispatch

def dispatch(event="refresh"):

    _original_dispatch(event)

    emit(
        event,
        target=str(target.value),
        heartbeat=RUNTIME["heartbeat"],
    )

register(
    "dispatch",
    dispatch
)

# ============================================================
# DIAGNOSTICS
# ============================================================

def event_summary():

    print()

    print("EVENT BUS")

    print("---------------------------")

    print(
        "Enabled :",
        EVENTS["enabled"]
    )

    print(
        "Listeners:",
        sum(
            len(v)
            for v in EVENTS["listeners"].values()
        )
    )

    print(
        "Events:",
        len(EVENTS["history"])
    )

    print()

    for name in sorted(EVENTS["listeners"]):

        print(
            f"{name:15s}",
            len(EVENTS["listeners"][name])
        )

# ============================================================
# REGISTER
# ============================================================

register(
    "subscribe",
    subscribe
)

register(
    "unsubscribe",
    unsubscribe
)

register(
    "emit",
    emit
)

register(
    "event_summary",
    event_summary
)

register_service(
    "event_bus",
    EVENTS
)

print()

print("Event bus initialized.")
print("Listeners :", sum(len(v) for v in EVENTS["listeners"].values()))
print("History    :", len(EVENTS["history"]))
print()
print("CMB-0033D-2 COMPLETE")


# CMB-0033E-1
# APPLICATION ASSEMBLY
# Final interface construction

print()
print("Assembling application...")

# ============================================================
# TITLE
# ============================================================

title_panel = widgets.VBox(

    [

        header,

        status,

    ],

    layout=widgets.Layout(

        width="100%",

    ),

)

# ============================================================
# LEFT PANEL
# ============================================================

left_panel = widgets.VBox(

    [

        controls,

    ],

    layout=widgets.Layout(

        width="430px",

    ),

)

# ============================================================
# RIGHT PANEL
# ============================================================

right_panel = widgets.VBox(

    [

        VIEWER["panel"],

    ],

    layout=widgets.Layout(

        width="100%",

    ),

)

# ============================================================
# MAIN BODY
# ============================================================

main_body = widgets.HBox(

    [

        left_panel,

        right_panel,

    ],

    layout=widgets.Layout(

        width="100%",

        align_items="flex-start",

    ),

)

# ============================================================
# ROOT APPLICATION
# ============================================================

root = widgets.VBox(

    [

        title_panel,

        main_body,

    ],

    layout=widgets.Layout(

        width="100%",

    ),

)

# ============================================================
# STORE
# ============================================================

APP["root"] = root

register(

    "root",

    root,

)

register_service(

    "application",

    root,

)

# ============================================================
# STARTUP
# ============================================================

def startup():

    log("Starting CMB-0033...")

    refresh_runtime(force=True)

    update_status_bar()

    emit("startup")

    RUNTIME["running"] = True

startup()

# ============================================================
# DISPLAY
# ============================================================

display(root)

# ============================================================
# FINAL DIAGNOSTICS
# ============================================================

print()

print("======================================")
print("CMB-0033 READY")
print("======================================")

print()

print("Version          :", VERSION)
print("Patch            :", "E-1")
print("Viewer Engine    :", CONFIG["viewer_engine"])
print("Native Viewer    :", VIEWER["enabled"])
print("Runtime Running  :", RUNTIME["running"])
print("Heartbeat        :", RUNTIME["heartbeat"])
print("Widgets          :", len(APP["widgets"]))
print("Registry         :", len(REGISTRY))
print("Services         :", len(SERVICES))
print("Event Listeners  :", sum(len(v) for v in EVENTS["listeners"].values()))
print("Refreshes        :", STAT["refreshes"])
print("Viewer Updates   :", STAT["viewer_updates"])
print("Inspections      :", STAT["inspection_requests"])

print()

print("Application initialized successfully.")

print()

print("CMB-0033E-1 COMPLETE")

# CMB-0033E-2
# FINAL DIAGNOSTICS, RESET & MAINTENANCE

print()
print("Installing diagnostics...")

# ============================================================
# APPLICATION INFORMATION
# ============================================================

def app_info():

    print()

    print("APPLICATION INFORMATION")
    print("------------------------------")

    print("Version        :", VERSION)
    print("Viewer Engine  :", CONFIG["viewer_engine"])
    print("Viewer Enabled :", VIEWER["enabled"])
    print("Runtime        :", RUNTIME["running"])
    print("Heartbeat      :", RUNTIME["heartbeat"])

    print()

    print("Widgets        :", len(APP["widgets"]))
    print("Registry       :", len(REGISTRY))
    print("Services       :", len(SERVICES))

# ============================================================
# MEMORY REPORT
# ============================================================

def memory_report():

    print()

    print("MEMORY REPORT")
    print("------------------------------")

    print("Widgets :", len(APP["widgets"]))
    print("Registry:", len(REGISTRY))
    print("Services:", len(SERVICES))
    print("Events  :", len(EVENTS["history"]))

# ============================================================
# APPLICATION RESET
# ============================================================

def reset_application():

    print()

    print("Resetting runtime...")

    reset_runtime()

    clear_event_history()

    update_cache()

    refresh_runtime(force=True)

    print("Reset complete.")

# ============================================================
# CLEAR VIEWER
# ============================================================

def clear_viewer():

    try:

        if VIEWER["enabled"]:

            VIEWER["widget"].target = ""

    except Exception as exc:

        log_exception(exc)

    clear_current_object()

    update_status_bar()

# ============================================================
# RELOAD CURRENT TARGET
# ============================================================

def reload_target():

    refresh_coordinates()

    refresh_runtime(force=True)

# ============================================================
# COMPLETE HEALTH CHECK
# ============================================================

def full_health_check():

    print()

    print("====================================")
    print("CMB-0033 HEALTH REPORT")
    print("====================================")

    app_info()

    print()

    runtime_summary()

    print()

    coordinate_summary()

    print()

    event_summary()

    print()

    application_summary()

# ============================================================
# EXPORT SESSION
# ============================================================

def export_session():

    return {

        "version": VERSION,

        "target": str(target.value),

        "survey": str(survey.value),

        "fov": float(fov.value),

        "heartbeat": RUNTIME["heartbeat"],

        "statistics": dict(STAT),

    }

# ============================================================
# IMPORT SESSION
# ============================================================

def import_session(session):

    target.value = session.get(
        "target",
        target.value,
    )

    survey.value = session.get(
        "survey",
        survey.value,
    )

    fov.value = session.get(
        "fov",
        fov.value,
    )

    refresh_runtime(force=True)

# ============================================================
# REGISTER
# ============================================================

register(
    "app_info",
    app_info
)

register(
    "memory_report",
    memory_report
)

register(
    "full_health_check",
    full_health_check
)

register(
    "reset_application",
    reset_application
)

register(
    "reload_target",
    reload_target
)

register(
    "clear_viewer",
    clear_viewer
)

register(
    "export_session",
    export_session
)

register(
    "import_session",
    import_session
)

register_service(
    "maintenance",
    {

        "reset": reset_application,

        "reload": reload_target,

        "health": full_health_check,

    }

)

# ============================================================
# READY
# ============================================================

print()

print("Maintenance tools installed.")

print("Application status : READY")

print()

print("CMB-0033 COMPLETE")
print("All core modules initialized.")



# CMB-0033F-1
# CATALOG MANAGER
# Unified catalog loading, indexing, filtering, and selection

print()
print("Building catalog manager...")

# ============================================================
# STATE
# ============================================================

STATE["catalog"] = None
STATE["catalog_name"] = None
STATE["catalog_index"] = {}
STATE["filtered_catalog"] = None

# ============================================================
# LOAD
# ============================================================

def load_catalog(df, name="Catalog"):

    if df is None:
        raise ValueError("Catalog is None.")

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Catalog must be a pandas DataFrame.")

    STATE["catalog"] = df.copy()

    STATE["filtered_catalog"] = df.copy()

    STATE["catalog_name"] = str(name)

    build_catalog_index()

    log(f"Loaded catalog: {name}")

    return len(df)

# ============================================================
# INDEX
# ============================================================

def build_catalog_index():

    catalog = STATE["catalog"]

    index = {}

    if catalog is None:

        STATE["catalog_index"] = index

        return

    for i, row in catalog.iterrows():

        key = str(

            row.get(

                "Object",

                i

            )

        ).strip()

        index[key] = i

    STATE["catalog_index"] = index

# ============================================================
# SEARCH
# ============================================================

def find_catalog_object(name):

    if STATE["catalog"] is None:
        return None

    key = str(name).strip()

    idx = STATE["catalog_index"].get(key)

    if idx is None:
        return None

    return dict(

        STATE["catalog"].loc[idx]

    )

# ============================================================
# FILTER
# ============================================================

def filter_catalog(text):

    catalog = STATE["catalog"]

    if catalog is None:
        return None

    text = str(text).lower().strip()

    if len(text) == 0:

        STATE["filtered_catalog"] = catalog.copy()

        return STATE["filtered_catalog"]

    mask = np.zeros(

        len(catalog),

        dtype=bool,

    )

    for column in catalog.columns:

        try:

            values = (

                catalog[column]

                .astype(str)

                .str.lower()

            )

            mask |= values.str.contains(

                text,

                regex=False,

                na=False,

            )

        except Exception:

            pass

    STATE["filtered_catalog"] = (

        catalog.loc[mask]

        .reset_index(drop=True)

    )

    return STATE["filtered_catalog"]

# ============================================================
# CURRENT
# ============================================================

def current_catalog():

    return STATE["filtered_catalog"]

# ============================================================
# SELECT
# ============================================================

def select_catalog_object(name):

    obj = find_catalog_object(name)

    if obj is None:

        return False

    load_object(obj)

    refresh_viewer()

    return True

# ============================================================
# SUMMARY
# ============================================================

def catalog_summary():

    print()

    print("CATALOG")

    print("-------------------------")

    print(

        "Name :",

        STATE["catalog_name"]

    )

    if STATE["catalog"] is None:

        print("Rows : None")

    else:

        print(

            "Rows :",

            len(STATE["catalog"])

        )

        print(

            "Filtered :",

            len(

                STATE["filtered_catalog"]

            )

        )

# ============================================================
# REGISTER
# ============================================================

register(
    "load_catalog",
    load_catalog
)

register(
    "filter_catalog",
    filter_catalog
)

register(
    "find_catalog_object",
    find_catalog_object
)

register(
    "select_catalog_object",
    select_catalog_object
)

register(
    "catalog_summary",
    catalog_summary
)

register_service(
    "catalog",
    {

        "load": load_catalog,

        "filter": filter_catalog,

        "find": find_catalog_object,

        "select": select_catalog_object,

    }

)

print()

print("Catalog manager ready.")

print("CMB-0033F-1 COMPLETE")

# CMB-0033F-2
# CATALOG BROWSER WIDGETS
# Interactive catalog browsing and object selection

print()
print("Building catalog browser...")

# ============================================================
# SEARCH BOX
# ============================================================

catalog_search = widgets.Text(
    value="",
    description="Search",
    placeholder="Galaxy, ID, RA, Dec...",
    layout=widgets.Layout(width="100%"),
)

# ============================================================
# OBJECT LIST
# ============================================================

catalog_list = widgets.Select(
    options=[],
    rows=15,
    description="Objects",
    layout=widgets.Layout(width="100%"),
)

# ============================================================
# OBJECT INFORMATION
# ============================================================

catalog_info = widgets.HTML(
    value="<b>No object selected.</b>",
    layout=widgets.Layout(width="100%"),
)

# ============================================================
# UPDATE OBJECT LIST
# ============================================================

def update_catalog_list():

    table = current_catalog()

    if table is None or len(table) == 0:

        catalog_list.options = []

        return

    labels = []

    for _, row in table.iterrows():

        label = str(

            row.get(

                "Object",

                row.name

            )

        )

        labels.append(label)

    catalog_list.options = labels

# ============================================================
# DISPLAY OBJECT
# ============================================================

def display_catalog_object(name):

    obj = find_catalog_object(name)

    if obj is None:

        catalog_info.value = (
            "<span style='color:#b71c1c'>"
            "Object not found."
            "</span>"
        )

        return

    html = "<table>"

    for key in sorted(obj):

        html += (
            f"<tr>"
            f"<td><b>{key}</b></td>"
            f"<td>{obj[key]}</td>"
            f"</tr>"
        )

    html += "</table>"

    catalog_info.value = html

# ============================================================
# SEARCH CALLBACK
# ============================================================

def catalog_search_changed(change):

    filter_catalog(change["new"])

    update_catalog_list()

# ============================================================
# SELECTION CALLBACK
# ============================================================

def catalog_selection_changed(change):

    if change["new"] is None:
        return

    name = change["new"]

    display_catalog_object(name)

    if select_catalog_object(name):

        update_status_bar()

# ============================================================
# CALLBACKS
# ============================================================

catalog_search.observe(
    catalog_search_changed,
    names="value",
)

catalog_list.observe(
    catalog_selection_changed,
    names="value",
)

# ============================================================
# PANEL
# ============================================================

catalog_panel = widgets.VBox(
    [
        widgets.HTML("<h3>Catalog Browser</h3>"),
        catalog_search,
        catalog_list,
        catalog_info,
    ],
    layout=widgets.Layout(width="100%"),
)

# ============================================================
# REGISTER
# ============================================================

APP["widgets"]["catalog_search"] = catalog_search
APP["widgets"]["catalog_list"] = catalog_list
APP["widgets"]["catalog_info"] = catalog_info
APP["widgets"]["catalog_panel"] = catalog_panel

register("catalog_panel", catalog_panel)
register("catalog_search", catalog_search)
register("catalog_list", catalog_list)
register("catalog_info", catalog_info)

# ============================================================
# INITIALIZE
# ============================================================

update_catalog_list()

print()

print("Catalog browser initialized.")
print("Catalog widgets registered.")
print()
print("CMB-0033F-2 COMPLETE")

# CMB-0033F-3
# CATALOG TABLE + SORTING + EXPORT
# Extends the Catalog Manager with interactive table support

print()
print("Building catalog table...")

# ============================================================
# SORT OPTIONS
# ============================================================

catalog_sort = widgets.Dropdown(
    description="Sort",
    options=[
        "Object",
        "RA",
        "Dec",
        "Redshift",
        "SNR",
    ],
    value="Object",
    layout=widgets.Layout(width="260px"),
)

catalog_reverse = widgets.Checkbox(
    value=False,
    description="Descending",
)

catalog_export = widgets.Button(
    description="Export CSV",
    icon="download",
    button_style="success",
)

# ============================================================
# TABLE OUTPUT
# ============================================================

catalog_table = widgets.Output(
    layout=widgets.Layout(
        border="1px solid lightgray",
        max_height="350px",
        overflow="auto",
    )
)

# ============================================================
# SORT
# ============================================================

def sort_catalog():

    df = current_catalog()

    if df is None:
        return

    column = catalog_sort.value

    if column not in df.columns:
        return

    STATE["filtered_catalog"] = (
        df
        .sort_values(
            by=column,
            ascending=not catalog_reverse.value,
            ignore_index=True,
        )
    )

# ============================================================
# DISPLAY
# ============================================================

def refresh_catalog_table():

    with catalog_table:

        clear_output(wait=True)

        df = current_catalog()

        if df is None:

            print("No catalog loaded.")

            return

        display(df)

# ============================================================
# UPDATE
# ============================================================

def update_catalog_browser():

    sort_catalog()

    update_catalog_list()

    refresh_catalog_table()

# ============================================================
# EXPORT
# ============================================================

def export_catalog(button=None):

    df = current_catalog()

    if df is None:

        print("Nothing to export.")

        return

    filename = (
        f"{VERSION}_CATALOG_EXPORT.csv"
    )

    df.to_csv(
        filename,
        index=False,
    )

    print()

    print("Catalog exported:")

    print(filename)

# ============================================================
# CALLBACKS
# ============================================================

def sort_changed(change):

    update_catalog_browser()

catalog_sort.observe(
    sort_changed,
    names="value",
)

catalog_reverse.observe(
    sort_changed,
    names="value",
)

catalog_export.on_click(
    export_catalog
)

# ============================================================
# PANEL
# ============================================================

catalog_tools = widgets.HBox(
    [
        catalog_sort,
        catalog_reverse,
        catalog_export,
    ]
)

catalog_browser_panel = widgets.VBox(
    [
        catalog_tools,
        catalog_table,
    ]
)

# ============================================================
# REGISTER
# ============================================================

APP["widgets"]["catalog_sort"] = catalog_sort
APP["widgets"]["catalog_reverse"] = catalog_reverse
APP["widgets"]["catalog_export"] = catalog_export
APP["widgets"]["catalog_table"] = catalog_table
APP["widgets"]["catalog_browser_panel"] = catalog_browser_panel

register(
    "catalog_browser_panel",
    catalog_browser_panel,
)

register(
    "refresh_catalog_table",
    refresh_catalog_table,
)

register(
    "update_catalog_browser",
    update_catalog_browser,
)

# ============================================================
# INITIALIZE
# ============================================================

update_catalog_browser()

print()

print("Catalog table initialized.")
print("Sorting enabled.")
print("CSV export enabled.")
print()


# CMB-0033G-1
# FITS IMAGE MANAGER
# Unified FITS loading and image registry

print()
print("Building FITS image manager...")

# ============================================================
# FITS STATE
# ============================================================

STATE["fits"] = {}

FITS = STATE["fits"]

FITS["images"] = {}
FITS["current"] = None
FITS["primary"] = None

# ============================================================
# LOAD DEPENDENCIES
# ============================================================

try:

    from astropy.io import fits
    from astropy.wcs import WCS

    FITS_AVAILABLE = True

except Exception:

    FITS_AVAILABLE = False

print("Astropy FITS :", FITS_AVAILABLE)

# ============================================================
# LOAD FITS
# ============================================================

def load_fits(filename, name=None):

    if not FITS_AVAILABLE:

        raise RuntimeError(
            "astropy is not installed."
        )

    hdul = fits.open(filename)

    data = hdul[0].data

    header = hdul[0].header

    wcs = WCS(header)

    if name is None:

        from pathlib import Path

        name = Path(filename).stem

    FITS["images"][name] = {

        "filename": filename,

        "hdul": hdul,

        "header": header,

        "data": data,

        "wcs": wcs,

    }

    FITS["current"] = name

    if FITS["primary"] is None:

        FITS["primary"] = name

    return name

# ============================================================
# CURRENT IMAGE
# ============================================================

def current_image():

    if FITS["current"] is None:

        return None

    return FITS["images"][

        FITS["current"]

    ]

# ============================================================
# IMAGE LIST
# ============================================================

def image_names():

    return list(

        FITS["images"].keys()

    )

# ============================================================
# SELECT
# ============================================================

def select_image(name):

    if name not in FITS["images"]:

        return False

    FITS["current"] = name

    return True

# ============================================================
# CLOSE
# ============================================================

def close_all_images():

    for image in FITS["images"].values():

        try:

            image["hdul"].close()

        except Exception:

            pass

    FITS["images"].clear()

    FITS["current"] = None

    FITS["primary"] = None

# ============================================================
# SUMMARY
# ============================================================

def fits_summary():

    print()

    print("FITS MANAGER")

    print("---------------------------")

    print(

        "Images :",

        len(

            FITS["images"]

        )

    )

    print(

        "Current:",

        FITS["current"]

    )

    print(

        "Primary:",

        FITS["primary"]

    )

    print()

    for name in image_names():

        img = FITS["images"][name]

        print(

            f"{name:25s}",

            img["data"].shape

        )

# ============================================================
# REGISTER
# ============================================================

register(

    "load_fits",

    load_fits

)

register(

    "current_image",

    current_image

)

register(

    "select_image",

    select_image

)

register(

    "close_all_images",

    close_all_images

)

register(

    "fits_summary",

    fits_summary

)

register_service(

    "fits",

    {

        "load": load_fits,

        "select": select_image,

        "summary": fits_summary,

    }

)

print()

print("FITS image manager initialized.")
print("CMB-0033G-1 COMPLETE")


# CMB-0033G-2
# LAYER MANAGER
# Unified image/layer/overlay registry

print()
print("Building Layer Manager...")

# ============================================================
# LAYER STATE
# ============================================================

STATE["layers"] = {}

LAYERS = STATE["layers"]

LAYERS["order"] = []
LAYERS["items"] = {}
LAYERS["active"] = None

# ============================================================
# CREATE
# ============================================================

def create_layer(

    name,
    image=None,
    visible=True,
    opacity=1.0,
    zorder=0,
    kind="image",

):

    layer = {

        "name": str(name),

        "image": image,

        "visible": bool(visible),

        "opacity": float(opacity),

        "zorder": int(zorder),

        "kind": str(kind),

        "metadata": {},

    }

    LAYERS["items"][name] = layer

    if name not in LAYERS["order"]:

        LAYERS["order"].append(name)

    LAYERS["active"] = name

    return layer

# ============================================================
# REMOVE
# ============================================================

def remove_layer(name):

    if name not in LAYERS["items"]:

        return

    del LAYERS["items"][name]

    if name in LAYERS["order"]:

        LAYERS["order"].remove(name)

    if LAYERS["active"] == name:

        LAYERS["active"] = None

# ============================================================
# ACTIVE
# ============================================================

def active_layer():

    if LAYERS["active"] is None:

        return None

    return LAYERS["items"].get(

        LAYERS["active"]

    )

# ============================================================
# VISIBILITY
# ============================================================

def set_layer_visibility(

    name,

    visible=True,

):

    if name not in LAYERS["items"]:

        return False

    LAYERS["items"][name]["visible"] = bool(

        visible

    )

    return True

# ============================================================
# OPACITY
# ============================================================

def set_layer_opacity(

    name,

    opacity,

):

    if name not in LAYERS["items"]:

        return False

    opacity = max(

        0.0,

        min(

            1.0,

            float(opacity),

        ),

    )

    LAYERS["items"][name]["opacity"] = opacity

    return True

# ============================================================
# REORDER
# ============================================================

def reorder_layers():

    ordered = sorted(

        LAYERS["items"].values(),

        key=lambda x: x["zorder"],

    )

    LAYERS["order"] = [

        layer["name"]

        for layer in ordered

    ]

# ============================================================
# DRAW
# ============================================================

def redraw_layers():

    img = current_image()

    if img is None:

        return

    if "viewer_axes" not in STATE:

        return

    ax = STATE["viewer_axes"]

    ax.clear()

    for name in LAYERS["order"]:

        layer = LAYERS["items"][name]

        if not layer["visible"]:

            continue

        if layer["kind"] != "image":

            continue

        data = layer["image"]

        if data is None:

            continue

        ax.imshow(

            data,

            origin="lower",

            alpha=layer["opacity"],

            interpolation="nearest",

        )

    try:

        STATE["viewer_canvas"].draw_idle()

    except Exception:

        pass

# ============================================================
# AUTO PRIMARY
# ============================================================

def create_primary_layer():

    img = current_image()

    if img is None:

        return

    create_layer(

        name="PRIMARY",

        image=img["data"],

        visible=True,

        opacity=1.0,

        zorder=0,

        kind="image",

    )

# ============================================================
# SUMMARY
# ============================================================

def layer_summary():

    print()

    print("LAYER MANAGER")

    print("---------------------------")

    print(

        "Layers :",

        len(

            LAYERS["items"]

        )

    )

    print(

        "Active :",

        LAYERS["active"]

    )

    print()

    for name in LAYERS["order"]:

        L = LAYERS["items"][name]

        print(

            f"{name:20s}",

            L["kind"],

            "Visible"

            if L["visible"]

            else "Hidden",

            f"Opacity={L['opacity']:.2f}",

            f"Z={L['zorder']}",

        )

# ============================================================
# REGISTER
# ============================================================

register(
    "create_layer",
    create_layer,
)

register(
    "remove_layer",
    remove_layer,
)

register(
    "redraw_layers",
    redraw_layers,
)

register(
    "layer_summary",
    layer_summary,
)

register_service(

    "layers",

    {

        "create": create_layer,

        "remove": remove_layer,

        "redraw": redraw_layers,

    },

)

print()

print("Layer manager initialized.")

print("CMB-0033G-2 COMPLETE")


# CMB-0033G-3
# OVERLAY ENGINE
# Scientific overlay manager

print()
print("Building Overlay Manager...")

# ============================================================
# STATE
# ============================================================

STATE["overlays"] = {}

OVERLAYS = STATE["overlays"]

OVERLAYS["items"] = {}
OVERLAYS["order"] = []

# ============================================================
# CREATE
# ============================================================

def create_overlay(
    name,
    overlay_type="generic",
    artist=None,
    visible=True,
    color="yellow",
    linewidth=1.0,
    alpha=1.0,
    zorder=100,
):

    obj = {

        "name": str(name),
        "type": str(overlay_type),
        "artist": artist,
        "visible": bool(visible),
        "color": color,
        "linewidth": float(linewidth),
        "alpha": float(alpha),
        "zorder": int(zorder),
        "metadata": {},

    }

    OVERLAYS["items"][name] = obj

    if name not in OVERLAYS["order"]:
        OVERLAYS["order"].append(name)

    return obj

# ============================================================
# REMOVE
# ============================================================

def remove_overlay(name):

    if name not in OVERLAYS["items"]:
        return

    artist = OVERLAYS["items"][name]["artist"]

    try:
        if artist is not None:
            artist.remove()
    except Exception:
        pass

    del OVERLAYS["items"][name]

    if name in OVERLAYS["order"]:
        OVERLAYS["order"].remove(name)

# ============================================================
# CLEAR
# ============================================================

def clear_overlays():

    for name in list(OVERLAYS["order"]):
        remove_overlay(name)

# ============================================================
# ACCESS
# ============================================================

def overlay(name):

    return OVERLAYS["items"].get(name)

def overlay_names():

    return list(OVERLAYS["order"])

# ============================================================
# VISIBILITY
# ============================================================

def show_overlay(name):

    obj = overlay(name)

    if obj is None:
        return False

    obj["visible"] = True

    if obj["artist"] is not None:
        obj["artist"].set_visible(True)

    return True


def hide_overlay(name):

    obj = overlay(name)

    if obj is None:
        return False

    obj["visible"] = False

    if obj["artist"] is not None:
        obj["artist"].set_visible(False)

    return True


def toggle_overlay(name):

    obj = overlay(name)

    if obj is None:
        return False

    if obj["visible"]:
        hide_overlay(name)
    else:
        show_overlay(name)

    return True

# ============================================================
# STYLE
# ============================================================

def set_overlay_alpha(name, alpha):

    obj = overlay(name)

    if obj is None:
        return False

    alpha = max(0.0, min(1.0, float(alpha)))

    obj["alpha"] = alpha

    try:
        obj["artist"].set_alpha(alpha)
    except Exception:
        pass

    return True


def set_overlay_color(name, color):

    obj = overlay(name)

    if obj is None:
        return False

    obj["color"] = color

    try:
        obj["artist"].set_color(color)
    except Exception:
        pass

    return True


def set_overlay_linewidth(name, width):

    obj = overlay(name)

    if obj is None:
        return False

    obj["linewidth"] = float(width)

    try:
        obj["artist"].set_linewidth(width)
    except Exception:
        pass

    return True

# ============================================================
# REDRAW
# ============================================================

def redraw_overlays():

    for name in OVERLAYS["order"]:

        obj = OVERLAYS["items"][name]

        artist = obj["artist"]

        if artist is None:
            continue

        try:
            artist.set_visible(obj["visible"])
            artist.set_alpha(obj["alpha"])
            artist.set_zorder(obj["zorder"])
        except Exception:
            pass

    try:
        STATE["viewer_canvas"].draw_idle()
    except Exception:
        pass

# ============================================================
# SUMMARY
# ============================================================

def overlay_summary():

    print()
    print("OVERLAY MANAGER")
    print("-------------------------")
    print("Total:", len(OVERLAYS["items"]))
    print()

    for name in OVERLAYS["order"]:

        o = OVERLAYS["items"][name]

        print(
            f"{name:20s}",
            f"{o['type']:12s}",
            "Visible" if o["visible"] else "Hidden",
            f"alpha={o['alpha']:.2f}",
        )

# ============================================================
# REGISTER
# ============================================================

register("create_overlay", create_overlay)
register("remove_overlay", remove_overlay)
register("clear_overlays", clear_overlays)
register("redraw_overlays", redraw_overlays)
register("overlay_summary", overlay_summary)

register_service(

    "overlays",

    {

        "create": create_overlay,
        "remove": remove_overlay,
        "clear": clear_overlays,
        "summary": overlay_summary,

    }

)

print()
print("Overlay manager initialized.")
print("CMB-0033G-3 COMPLETE")



# CMB-0033G-4
# REGION MANAGER
# Polygon / Circle / Ellipse / Rectangle support

print()
print("Building Region Manager...")

# ============================================================
# STATE
# ============================================================

STATE["regions"] = {}

REGIONS = STATE["regions"]

REGIONS["items"] = {}
REGIONS["active"] = None

# ============================================================
# CREATE
# ============================================================

def create_region(

    name,
    region_type="polygon",
    vertices=None,
    artist=None,

):

    if vertices is None:
        vertices = []

    region = {

        "name": str(name),
        "type": str(region_type),
        "vertices": list(vertices),
        "artist": artist,
        "visible": True,
        "selected": False,
        "metadata": {},

    }

    REGIONS["items"][name] = region
    REGIONS["active"] = name

    return region

# ============================================================
# REMOVE
# ============================================================

def remove_region(name):

    if name not in REGIONS["items"]:
        return

    artist = REGIONS["items"][name]["artist"]

    try:
        if artist is not None:
            artist.remove()
    except Exception:
        pass

    del REGIONS["items"][name]

    if REGIONS["active"] == name:
        REGIONS["active"] = None

# ============================================================
# ACCESS
# ============================================================

def region(name):

    return REGIONS["items"].get(name)


def region_names():

    return list(REGIONS["items"].keys())

# ============================================================
# ACTIVE
# ============================================================

def select_region(name):

    if name not in REGIONS["items"]:
        return False

    for r in REGIONS["items"].values():
        r["selected"] = False

    REGIONS["items"][name]["selected"] = True
    REGIONS["active"] = name

    return True

# ============================================================
# VERTICES
# ============================================================

def update_vertices(name, vertices):

    r = region(name)

    if r is None:
        return False

    r["vertices"] = list(vertices)

    return True


def region_vertices(name):

    r = region(name)

    if r is None:
        return []

    return r["vertices"]

# ============================================================
# VISIBILITY
# ============================================================

def show_region(name):

    r = region(name)

    if r is None:
        return False

    r["visible"] = True

    try:
        r["artist"].set_visible(True)
    except Exception:
        pass

    return True


def hide_region(name):

    r = region(name)

    if r is None:
        return False

    r["visible"] = False

    try:
        r["artist"].set_visible(False)
    except Exception:
        pass

    return True

# ============================================================
# CLEAR
# ============================================================

def clear_regions():

    for name in list(region_names()):
        remove_region(name)

# ============================================================
# SUMMARY
# ============================================================

def region_summary():

    print()
    print("REGION MANAGER")
    print("--------------------------")
    print("Regions :", len(REGIONS["items"]))
    print("Active  :", REGIONS["active"])
    print()

    for name in region_names():

        r = region(name)

        print(

            f"{name:20s}",

            r["type"],

            len(r["vertices"]),

            "vertices",

        )

# ============================================================
# REGISTER
# ============================================================

register(
    "create_region",
    create_region,
)

register(
    "remove_region",
    remove_region,
)

register(
    "clear_regions",
    clear_regions,
)

register(
    "region_summary",
    region_summary,
)

register_service(

    "regions",

    {

        "create": create_region,

        "remove": remove_region,

        "clear": clear_regions,

        "summary": region_summary,

    }

)

print()
print("Region manager initialized.")
print("CMB-0033G-4 COMPLETE")



# CMB-0033G-5
# APERTURE MANAGER
# Scientific aperture definitions and measurements

print()
print("Building Aperture Manager...")

# ============================================================
# STATE
# ============================================================

STATE["apertures"] = {}

APERTURES = STATE["apertures"]

APERTURES["items"] = {}
APERTURES["active"] = None

# ============================================================
# CREATE
# ============================================================

def create_aperture(
    name,
    aperture_type="polygon",
    vertices=None,
    radius=None,
    artist=None,
):

    if vertices is None:
        vertices = []

    aperture = {

        "name": str(name),
        "type": str(aperture_type),
        "vertices": list(vertices),
        "radius": radius,
        "artist": artist,
        "enabled": True,
        "selected": False,
        "metadata": {},

    }

    APERTURES["items"][name] = aperture
    APERTURES["active"] = name

    return aperture

# ============================================================
# REMOVE
# ============================================================

def remove_aperture(name):

    if name not in APERTURES["items"]:
        return

    artist = APERTURES["items"][name]["artist"]

    try:
        if artist is not None:
            artist.remove()
    except Exception:
        pass

    del APERTURES["items"][name]

    if APERTURES["active"] == name:
        APERTURES["active"] = None

# ============================================================
# ACCESS
# ============================================================

def aperture(name):

    return APERTURES["items"].get(name)

def aperture_names():

    return list(APERTURES["items"].keys())

# ============================================================
# ACTIVE
# ============================================================

def select_aperture(name):

    if name not in APERTURES["items"]:
        return False

    for obj in APERTURES["items"].values():
        obj["selected"] = False

    APERTURES["items"][name]["selected"] = True
    APERTURES["active"] = name

    return True

# ============================================================
# ENABLE / DISABLE
# ============================================================

def enable_aperture(name):

    obj = aperture(name)

    if obj is None:
        return False

    obj["enabled"] = True

    return True

def disable_aperture(name):

    obj = aperture(name)

    if obj is None:
        return False

    obj["enabled"] = False

    return True

# ============================================================
# GEOMETRY
# ============================================================

def aperture_vertices(name):

    obj = aperture(name)

    if obj is None:
        return []

    return obj["vertices"]

def update_aperture_vertices(name, vertices):

    obj = aperture(name)

    if obj is None:
        return False

    obj["vertices"] = list(vertices)

    return True

# ============================================================
# MASK PLACEHOLDER
# ============================================================

def aperture_mask(name, shape=None):

    obj = aperture(name)

    if obj is None:
        return None

    # Future implementation:
    # Convert polygon/circle/etc.
    # into binary mask.

    return None

# ============================================================
# SUMMARY
# ============================================================

def aperture_summary():

    print()
    print("APERTURE MANAGER")
    print("---------------------------")
    print("Apertures :", len(APERTURES["items"]))
    print("Active    :", APERTURES["active"])
    print()

    for name in aperture_names():

        a = aperture(name)

        print(
            f"{name:20s}",
            a["type"],
            "Enabled" if a["enabled"] else "Disabled",
            len(a["vertices"]),
            "vertices",
        )

# ============================================================
# REGISTER
# ============================================================

register(
    "create_aperture",
    create_aperture,
)

register(
    "remove_aperture",
    remove_aperture,
)

register(
    "aperture_summary",
    aperture_summary,
)

register_service(

    "apertures",

    {

        "create": create_aperture,

        "remove": remove_aperture,

        "summary": aperture_summary,

    }

)

print()
print("Aperture manager initialized.")
print("CMB-0033G-5 COMPLETE")



# CMB-0033G-6
# MARKER MANAGER
# Interactive astronomical markers

print()
print("Building Marker Manager...")

# ============================================================
# STATE
# ============================================================

STATE["markers"] = {}

MARKERS = STATE["markers"]

MARKERS["items"] = {}
MARKERS["active"] = None

# ============================================================
# CREATE
# ============================================================

def create_marker(
    name,
    x,
    y,
    label=None,
    marker="+",
    color="yellow",
    size=60,
    artist=None,
):

    obj = {

        "name": str(name),
        "x": float(x),
        "y": float(y),
        "label": label,
        "marker": marker,
        "color": color,
        "size": float(size),
        "artist": artist,
        "visible": True,
        "metadata": {},

    }

    MARKERS["items"][name] = obj
    MARKERS["active"] = name

    return obj

# ============================================================
# REMOVE
# ============================================================

def remove_marker(name):

    if name not in MARKERS["items"]:
        return

    artist = MARKERS["items"][name]["artist"]

    try:
        if artist is not None:
            artist.remove()
    except Exception:
        pass

    del MARKERS["items"][name]

    if MARKERS["active"] == name:
        MARKERS["active"] = None

# ============================================================
# ACCESS
# ============================================================

def marker(name):

    return MARKERS["items"].get(name)


def marker_names():

    return list(MARKERS["items"].keys())

# ============================================================
# POSITION
# ============================================================

def move_marker(name, x, y):

    m = marker(name)

    if m is None:
        return False

    m["x"] = float(x)
    m["y"] = float(y)

    try:
        m["artist"].set_offsets([[x, y]])
    except Exception:
        pass

    return True

# ============================================================
# VISIBILITY
# ============================================================

def show_marker(name):

    m = marker(name)

    if m is None:
        return False

    m["visible"] = True

    try:
        m["artist"].set_visible(True)
    except Exception:
        pass

    return True


def hide_marker(name):

    m = marker(name)

    if m is None:
        return False

    m["visible"] = False

    try:
        m["artist"].set_visible(False)
    except Exception:
        pass

    return True

# ============================================================
# CLEAR
# ============================================================

def clear_markers():

    for name in list(marker_names()):
        remove_marker(name)

# ============================================================
# SUMMARY
# ============================================================

def marker_summary():

    print()
    print("MARKER MANAGER")
    print("--------------------------")
    print("Markers :", len(MARKERS["items"]))
    print("Active  :", MARKERS["active"])
    print()

    for name in marker_names():

        m = marker(name)

        print(
            f"{name:20s}",
            f"({m['x']:.2f}, {m['y']:.2f})",
            m["marker"],
        )

# ============================================================
# REGISTER
# ============================================================

register(
    "create_marker",
    create_marker,
)

register(
    "remove_marker",
    remove_marker,
)

register(
    "move_marker",
    move_marker,
)

register(
    "marker_summary",
    marker_summary,
)

register_service(

    "markers",

    {

        "create": create_marker,

        "remove": remove_marker,

        "move": move_marker,

        "summary": marker_summary,

    }

)

print()
print("Marker manager initialized.")
print("CMB-0033G-6 COMPLETE")


# CMB-0033G-7
# ANNOTATION MANAGER
# Text labels, compass, scale bar and beam annotations

print()
print("Building Annotation Manager...")

# ============================================================
# STATE
# ============================================================

STATE["annotations"] = {}

ANNOTATIONS = STATE["annotations"]

ANNOTATIONS["items"] = {}
ANNOTATIONS["active"] = None

# ============================================================
# CREATE
# ============================================================

def create_annotation(
    name,
    x,
    y,
    text,
    color="white",
    fontsize=10,
    visible=True,
    artist=None,
):

    obj = {

        "name": str(name),
        "x": float(x),
        "y": float(y),
        "text": str(text),
        "color": color,
        "fontsize": int(fontsize),
        "visible": bool(visible),
        "artist": artist,
        "metadata": {},

    }

    ANNOTATIONS["items"][name] = obj
    ANNOTATIONS["active"] = name

    return obj

# ============================================================
# REMOVE
# ============================================================

def remove_annotation(name):

    if name not in ANNOTATIONS["items"]:
        return

    artist = ANNOTATIONS["items"][name]["artist"]

    try:
        if artist is not None:
            artist.remove()
    except Exception:
        pass

    del ANNOTATIONS["items"][name]

    if ANNOTATIONS["active"] == name:
        ANNOTATIONS["active"] = None

# ============================================================
# ACCESS
# ============================================================

def annotation(name):

    return ANNOTATIONS["items"].get(name)

def annotation_names():

    return list(ANNOTATIONS["items"].keys())

# ============================================================
# UPDATE
# ============================================================

def update_annotation(name, text):

    obj = annotation(name)

    if obj is None:
        return False

    obj["text"] = str(text)

    try:
        obj["artist"].set_text(text)
    except Exception:
        pass

    return True

# ============================================================
# MOVE
# ============================================================

def move_annotation(name, x, y):

    obj = annotation(name)

    if obj is None:
        return False

    obj["x"] = float(x)
    obj["y"] = float(y)

    try:
        obj["artist"].set_position((x, y))
    except Exception:
        pass

    return True

# ============================================================
# VISIBILITY
# ============================================================

def show_annotation(name):

    obj = annotation(name)

    if obj is None:
        return False

    obj["visible"] = True

    try:
        obj["artist"].set_visible(True)
    except Exception:
        pass

    return True

def hide_annotation(name):

    obj = annotation(name)

    if obj is None:
        return False

    obj["visible"] = False

    try:
        obj["artist"].set_visible(False)
    except Exception:
        pass

    return True

# ============================================================
# CLEAR
# ============================================================

def clear_annotations():

    for name in list(annotation_names()):
        remove_annotation(name)

# ============================================================
# SUMMARY
# ============================================================

def annotation_summary():

    print()
    print("ANNOTATION MANAGER")
    print("---------------------------")
    print("Annotations :", len(ANNOTATIONS["items"]))
    print("Active      :", ANNOTATIONS["active"])
    print()

    for name in annotation_names():

        obj = annotation(name)

        print(
            f"{name:20s}",
            obj["text"],
            f"({obj['x']:.1f}, {obj['y']:.1f})",
        )

# ============================================================
# REGISTER
# ============================================================

register(
    "create_annotation",
    create_annotation,
)

register(
    "remove_annotation",
    remove_annotation,
)

register(
    "move_annotation",
    move_annotation,
)

register(
    "update_annotation",
    update_annotation,
)

register(
    "annotation_summary",
    annotation_summary,
)

register_service(

    "annotations",

    {

        "create": create_annotation,

        "remove": remove_annotation,

        "move": move_annotation,

        "update": update_annotation,

        "summary": annotation_summary,

    }

)

print()
print("Annotation manager initialized.")
print("CMB-0033G-7 COMPLETE")



# CMB-0033G-8
# VIEW STATE MANAGER
# Camera, zoom, pan and viewport synchronization

print()
print("Building View State Manager...")

# ============================================================
# STATE
# ============================================================

STATE["view"] = {}

VIEW = STATE["view"]

VIEW["center_x"] = 0.0
VIEW["center_y"] = 0.0
VIEW["zoom"] = 1.0

VIEW["xmin"] = None
VIEW["xmax"] = None
VIEW["ymin"] = None
VIEW["ymax"] = None

VIEW["history"] = []

# ============================================================
# CENTER
# ============================================================

def set_view_center(x, y):

    VIEW["center_x"] = float(x)
    VIEW["center_y"] = float(y)

    VIEW["history"].append(
        ("center", float(x), float(y))
    )

    return True

# ============================================================
# ZOOM
# ============================================================

def set_zoom(value):

    value = max(0.01, float(value))

    VIEW["zoom"] = value

    VIEW["history"].append(
        ("zoom", value)
    )

    return value

# ============================================================
# LIMITS
# ============================================================

def set_view_limits(

    xmin,
    xmax,
    ymin,
    ymax,

):

    VIEW["xmin"] = float(xmin)
    VIEW["xmax"] = float(xmax)
    VIEW["ymin"] = float(ymin)
    VIEW["ymax"] = float(ymax)

    VIEW["history"].append(
        (
            "limits",
            xmin,
            xmax,
            ymin,
            ymax,
        )
    )

# ============================================================
# RESET
# ============================================================

def reset_view():

    VIEW["center_x"] = 0.0
    VIEW["center_y"] = 0.0
    VIEW["zoom"] = 1.0

    VIEW["xmin"] = None
    VIEW["xmax"] = None
    VIEW["ymin"] = None
    VIEW["ymax"] = None

# ============================================================
# APPLY
# ============================================================

def apply_view(ax=None):

    if ax is None:

        ax = STATE.get("viewer_axes")

    if ax is None:
        return

    if VIEW["xmin"] is not None:

        ax.set_xlim(
            VIEW["xmin"],
            VIEW["xmax"],
        )

        ax.set_ylim(
            VIEW["ymin"],
            VIEW["ymax"],
        )

# ============================================================
# CURRENT VIEW
# ============================================================

def current_view():

    return dict(VIEW)

# ============================================================
# SUMMARY
# ============================================================

def view_summary():

    print()
    print("VIEW MANAGER")
    print("---------------------------")

    print(
        "Center :",
        (
            VIEW["center_x"],
            VIEW["center_y"],
        ),
    )

    print(
        "Zoom   :",
        VIEW["zoom"],
    )

    print(
        "Limits :",
        (
            VIEW["xmin"],
            VIEW["xmax"],
            VIEW["ymin"],
            VIEW["ymax"],
        ),
    )

    print(
        "History:",
        len(VIEW["history"]),
    )

# ============================================================
# REGISTER
# ============================================================

register(
    "set_view_center",
    set_view_center,
)

register(
    "set_zoom",
    set_zoom,
)

register(
    "set_view_limits",
    set_view_limits,
)

register(
    "reset_view",
    reset_view,
)

register(
    "apply_view",
    apply_view,
)

register(
    "current_view",
    current_view,
)

register(
    "view_summary",
    view_summary,
)

register_service(

    "view",

    {

        "center": set_view_center,

        "zoom": set_zoom,

        "limits": set_view_limits,

        "reset": reset_view,

        "summary": view_summary,

    }

)

print()
print("View manager initialized.")
print("CMB-0033G-8 COMPLETE")



# CMB-0033G-9
# SELECTION MANAGER
# Unified object selection and hit-testing

print()
print("Building Selection Manager...")

# ============================================================
# STATE
# ============================================================

STATE["selection"] = {}

SELECTION = STATE["selection"]

SELECTION["type"] = None
SELECTION["name"] = None
SELECTION["object"] = None
SELECTION["history"] = []

# ============================================================
# CLEAR
# ============================================================

def clear_selection():

    SELECTION["type"] = None
    SELECTION["name"] = None
    SELECTION["object"] = None

# ============================================================
# SELECT
# ============================================================

def select_object(

    object_type,
    name,
    obj,

):

    SELECTION["type"] = object_type
    SELECTION["name"] = name
    SELECTION["object"] = obj

    SELECTION["history"].append(

        (

            object_type,
            name,

        )

    )

    return obj

# ============================================================
# GETTERS
# ============================================================

def selected_object():

    return SELECTION["object"]


def selected_name():

    return SELECTION["name"]


def selected_type():

    return SELECTION["type"]

# ============================================================
# TESTS
# ============================================================

def has_selection():

    return SELECTION["object"] is not None

# ============================================================
# HIT TEST
# ============================================================

def hit_test(x, y):

    """
    Placeholder.

    Future versions will inspect:

        markers
        regions
        overlays
        apertures
        annotations

    returning the closest object.
    """

    return None

# ============================================================
# CALLBACK
# ============================================================

def on_pick(event):

    artist = getattr(

        event,

        "artist",

        None,

    )

    if artist is None:

        return

    print(
        "Picked:",
        artist,
    )

# ============================================================
# CONNECT
# ============================================================

def connect_pick_events():

    canvas = STATE.get(

        "viewer_canvas"

    )

    if canvas is None:

        return

    try:

        canvas.mpl_connect(

            "pick_event",

            on_pick,

        )

    except Exception:

        pass

# ============================================================
# SUMMARY
# ============================================================

def selection_summary():

    print()
    print("SELECTION MANAGER")
    print("---------------------------")

    print(
        "Type :",
        SELECTION["type"],
    )

    print(
        "Name :",
        SELECTION["name"],
    )

    print(
        "History:",
        len(

            SELECTION["history"]

        ),

    )

# ============================================================
# REGISTER
# ============================================================

register(

    "select_object",

    select_object,

)

register(

    "clear_selection",

    clear_selection,

)

register(

    "selected_object",

    selected_object,

)

register(

    "connect_pick_events",

    connect_pick_events,

)

register(

    "selection_summary",

    selection_summary,

)

register_service(

    "selection",

    {

        "select": select_object,

        "clear": clear_selection,

        "summary": selection_summary,

    },

)

print()
print("Selection manager initialized.")
print("CMB-0033G-9 COMPLETE")


# CMB-0033G-10
# INTERACTION MANAGER
# Mouse, keyboard and navigation events

print()
print("Building Interaction Manager...")

# ============================================================
# STATE
# ============================================================

STATE["interaction"] = {}

INTERACTION = STATE["interaction"]

INTERACTION["mouse_x"] = None
INTERACTION["mouse_y"] = None

INTERACTION["pressed"] = False
INTERACTION["button"] = None

INTERACTION["mode"] = "inspect"

INTERACTION["connections"] = {}

# ============================================================
# MODE
# ============================================================

def set_interaction_mode(mode):

    INTERACTION["mode"] = str(mode)

    return mode


def interaction_mode():

    return INTERACTION["mode"]

# ============================================================
# EVENTS
# ============================================================

def on_mouse_move(event):

    if event.inaxes is None:
        return

    INTERACTION["mouse_x"] = event.xdata
    INTERACTION["mouse_y"] = event.ydata


def on_mouse_press(event):

    INTERACTION["pressed"] = True
    INTERACTION["button"] = event.button


def on_mouse_release(event):

    INTERACTION["pressed"] = False
    INTERACTION["button"] = None


def on_scroll(event):

    if event.button == "up":

        set_zoom(VIEW["zoom"] * 0.90)

    elif event.button == "down":

        set_zoom(VIEW["zoom"] * 1.10)

    try:

        apply_view()

        STATE["viewer_canvas"].draw_idle()

    except Exception:

        pass


def on_key_press(event):

    if event.key == "r":

        reset_view()

    elif event.key == "escape":

        clear_selection()

# ============================================================
# CONNECT
# ============================================================

def connect_interaction():

    canvas = STATE.get("viewer_canvas")

    if canvas is None:
        return

    INTERACTION["connections"]["move"] = canvas.mpl_connect(
        "motion_notify_event",
        on_mouse_move,
    )

    INTERACTION["connections"]["press"] = canvas.mpl_connect(
        "button_press_event",
        on_mouse_press,
    )

    INTERACTION["connections"]["release"] = canvas.mpl_connect(
        "button_release_event",
        on_mouse_release,
    )

    INTERACTION["connections"]["scroll"] = canvas.mpl_connect(
        "scroll_event",
        on_scroll,
    )

    INTERACTION["connections"]["key"] = canvas.mpl_connect(
        "key_press_event",
        on_key_press,
    )

# ============================================================
# DISCONNECT
# ============================================================

def disconnect_interaction():

    canvas = STATE.get("viewer_canvas")

    if canvas is None:
        return

    for cid in INTERACTION["connections"].values():

        try:
            canvas.mpl_disconnect(cid)
        except Exception:
            pass

    INTERACTION["connections"].clear()

# ============================================================
# SUMMARY
# ============================================================

def interaction_summary():

    print()
    print("INTERACTION MANAGER")
    print("---------------------------")
    print("Mode      :", INTERACTION["mode"])
    print("Mouse     :", (INTERACTION["mouse_x"], INTERACTION["mouse_y"]))
    print("Pressed   :", INTERACTION["pressed"])
    print("Button    :", INTERACTION["button"])
    print("Callbacks :", len(INTERACTION["connections"]))

# ============================================================
# REGISTER
# ============================================================

register(
    "connect_interaction",
    connect_interaction,
)

register(
    "disconnect_interaction",
    disconnect_interaction,
)

register(
    "set_interaction_mode",
    set_interaction_mode,
)

register(
    "interaction_summary",
    interaction_summary,
)

register_service(

    "interaction",

    {

        "connect": connect_interaction,

        "disconnect": disconnect_interaction,

        "mode": set_interaction_mode,

        "summary": interaction_summary,

    },

)

print()
print("Interaction manager initialized.")
print("CMB-0033G-10 COMPLETE")



# CMB-0033G-11
# TOOL MANAGER
# Unified tool registry for viewer interaction

print()
print("Building Tool Manager...")

# ============================================================
# STATE
# ============================================================

STATE["tools"] = {}

TOOLS = STATE["tools"]

TOOLS["registry"] = {}
TOOLS["active"] = None

# ============================================================
# REGISTER
# ============================================================

def register_tool(

    name,
    callback=None,
    cursor="arrow",
    description="",

):

    TOOLS["registry"][name] = {

        "name": name,
        "callback": callback,
        "cursor": cursor,
        "description": description,
        "enabled": True,

    }

# ============================================================
# ENABLE
# ============================================================

def enable_tool(name):

    if name not in TOOLS["registry"]:
        return False

    TOOLS["registry"][name]["enabled"] = True
    return True

# ============================================================
# DISABLE
# ============================================================

def disable_tool(name):

    if name not in TOOLS["registry"]:
        return False

    TOOLS["registry"][name]["enabled"] = False
    return True

# ============================================================
# ACTIVATE
# ============================================================

def activate_tool(name):

    if name not in TOOLS["registry"]:
        return False

    if not TOOLS["registry"][name]["enabled"]:
        return False

    TOOLS["active"] = name

    print("Active Tool:", name)

    return True

# ============================================================
# ACCESS
# ============================================================

def active_tool():

    return TOOLS["active"]


def tool(name):

    return TOOLS["registry"].get(name)


def tool_names():

    return sorted(

        TOOLS["registry"].keys()

    )

# ============================================================
# EXECUTE
# ============================================================

def execute_tool(

    *args,
    **kwargs,

):

    name = TOOLS["active"]

    if name is None:
        return

    obj = tool(name)

    if obj is None:
        return

    callback = obj["callback"]

    if callback is None:
        return

    return callback(

        *args,

        **kwargs,

    )

# ============================================================
# DEFAULT TOOLS
# ============================================================

register_tool(

    "inspect",

    description="Inspect objects",

)

register_tool(

    "pan",

    description="Pan image",

)

register_tool(

    "zoom",

    description="Zoom viewer",

)

register_tool(

    "marker",

    description="Create marker",

)

register_tool(

    "region",

    description="Draw region",

)

register_tool(

    "aperture",

    description="Create aperture",

)

activate_tool(

    "inspect"

)

# ============================================================
# SUMMARY
# ============================================================

def tool_summary():

    print()

    print("TOOL MANAGER")

    print("-------------------------")

    print(

        "Registered:",

        len(

            TOOLS["registry"]

        )

    )

    print(

        "Active:",

        TOOLS["active"]

    )

    print()

    for name in tool_names():

        obj = tool(name)

        state = "Enabled"

        if not obj["enabled"]:

            state = "Disabled"

        print(

            f"{name:15s}",

            state,

        )

# ============================================================
# REGISTER
# ============================================================

register(

    "register_tool",

    register_tool,

)

register(

    "activate_tool",

    activate_tool,

)

register(

    "execute_tool",

    execute_tool,

)

register(

    "tool_summary",

    tool_summary,

)

register_service(

    "tools",

    {

        "register": register_tool,

        "activate": activate_tool,

        "execute": execute_tool,

        "summary": tool_summary,

    }

)

print()
print("Tool manager initialized.")
print("CMB-0033G-11 COMPLETE")



# CMB-0033G-12
# COMMAND MANAGER
# Central command dispatcher with undo-ready history

print()
print("Building Command Manager...")

# ============================================================
# STATE
# ============================================================

STATE["commands"] = {}

COMMANDS = STATE["commands"]

COMMANDS["registry"] = {}
COMMANDS["history"] = []
COMMANDS["enabled"] = True

# ============================================================
# REGISTER
# ============================================================

def register_command(

    name,
    callback,
    description="",

):

    COMMANDS["registry"][name] = {

        "name": name,
        "callback": callback,
        "description": description,

    }

# ============================================================
# EXECUTE
# ============================================================

def execute_command(

    name,

    *args,

    **kwargs,

):

    if not COMMANDS["enabled"]:
        return None

    if name not in COMMANDS["registry"]:

        print("Unknown command:", name)
        return None

    command = COMMANDS["registry"][name]

    COMMANDS["history"].append(

        {

            "command": name,
            "args": args,
            "kwargs": kwargs,

        }

    )

    callback = command["callback"]

    if callback is None:
        return None

    return callback(

        *args,

        **kwargs,

    )

# ============================================================
# HISTORY
# ============================================================

def command_history():

    return list(

        COMMANDS["history"]

    )

def clear_command_history():

    COMMANDS["history"].clear()

# ============================================================
# ENABLE
# ============================================================

def enable_commands():

    COMMANDS["enabled"] = True

def disable_commands():

    COMMANDS["enabled"] = False

# ============================================================
# BUILT-IN COMMANDS
# ============================================================

register_command(

    "refresh",

    lambda: redraw_layers(),

    "Refresh viewer",

)

register_command(

    "reset_view",

    reset_view,

    "Reset camera",

)

register_command(

    "clear_selection",

    clear_selection,

    "Clear selection",

)

register_command(

    "clear_markers",

    clear_markers,

    "Remove markers",

)

register_command(

    "clear_regions",

    clear_regions,

    "Remove regions",

)

register_command(

    "clear_overlays",

    clear_overlays,

    "Remove overlays",

)

# ============================================================
# SUMMARY
# ============================================================

def command_summary():

    print()
    print("COMMAND MANAGER")
    print("---------------------------")

    print(

        "Commands :",

        len(

            COMMANDS["registry"]

        )

    )

    print(

        "History  :",

        len(

            COMMANDS["history"]

        )

    )

    print(

        "Enabled  :",

        COMMANDS["enabled"]

    )

    print()

    for name, cmd in sorted(

        COMMANDS["registry"].items()

    ):

        print(

            f"{name:20s}",

            cmd["description"],

        )

# ============================================================
# REGISTER
# ============================================================

register(

    "register_command",

    register_command,

)

register(

    "execute_command",

    execute_command,

)

register(

    "command_history",

    command_history,

)

register(

    "command_summary",

    command_summary,

)

register_service(

    "commands",

    {

        "register": register_command,

        "execute": execute_command,

        "history": command_history,

        "summary": command_summary,

    }

)

print()
print("Command manager initialized.")
print("CMB-0033G-12 COMPLETE")



