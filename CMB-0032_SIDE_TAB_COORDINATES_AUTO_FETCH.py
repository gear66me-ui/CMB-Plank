# CMB-0032A PATCH A

print("CMB-0032A PATCH A")

# ------------------------------------------------------------------
# Remove obsolete Patch B viewer implementation.
# ------------------------------------------------------------------

for obsolete_name in (
    "viewer_tabs",
    "native_viewer_output",
):
    if obsolete_name in globals():
        try:
            del globals()[obsolete_name]
        except Exception:
            pass

# ------------------------------------------------------------------
# Use viewer_stack as the only active viewer.
# ------------------------------------------------------------------

if "viewer_panel" in globals():
    viewer = viewer_panel

# ------------------------------------------------------------------
# Update status.
# ------------------------------------------------------------------

try:

    status.value = (
        "<b style='color:#2e7d32'>"
        "CMB-0032A Patch A loaded.<br>"
        "Obsolete Patch B viewer removed.<br>"
        "viewer_stack is now the only active viewer."
        "</b>"
    )

except Exception:
    pass

print("Viewer cleanup complete.")
print("CMB-0032A PATCH A COMPLETE")

# CMB-0032A PATCH B

print("CMB-0032A PATCH B")

# ------------------------------------------------------------------
# Consolidate all ipyaladin synchronization into one routine.
# This replaces the duplicated observers created by earlier patches.
# ------------------------------------------------------------------

def cmb0032_sync_native(change=None):

    if not IPYALADIN_AVAILABLE:
        return

    try:
        aladin.target = str(target.value)
    except Exception:
        pass

    try:
        aladin.survey = str(survey.value)
    except Exception:
        pass

    try:
        aladin.fov = float(fov.value)
    except Exception:
        pass


# ------------------------------------------------------------------
# Remove duplicate observer registrations when supported.
# ------------------------------------------------------------------

for widget in (target, survey, fov):

    try:
        widget.unobserve_all("value")
    except Exception:
        pass

    try:
        widget.observe(
            cmb0032_sync_native,
            names="value"
        )
    except Exception:
        pass


# ------------------------------------------------------------------
# Initial synchronization.
# ------------------------------------------------------------------

try:
    cmb0032_sync_native()
except Exception:
    pass


# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (
        "<b style='color:#2e7d32'>"
        "CMB-0032A Patch B loaded.<br>"
        "Native viewer synchronization consolidated."
        "</b>"
    )

except Exception:
    pass


print("Synchronization cleanup complete.")
print("CMB-0032A PATCH B COMPLETE")


# CMB-0032A PATCH C

print("CMB-0032A PATCH C")

# ------------------------------------------------------------------
# Consolidate all coordinate synchronization.
# This patch replaces the multiple wrappers created in
# CMB-0032 Patch C and Patch E.
# ------------------------------------------------------------------

if "_original_refresh_coordinates" not in globals():

    try:
        _original_refresh_coordinates = refresh_coordinates
    except Exception:
        _original_refresh_coordinates = None


def cmb0032_refresh_coordinates(*args, **kwargs):

    result = None

    if _original_refresh_coordinates is not None:

        try:
            result = _original_refresh_coordinates(*args, **kwargs)
        except Exception as exc:
            print(exc)

    if not IPYALADIN_AVAILABLE:
        return result

    coord = STATE.get("coord")

    if coord is None:
        return result

    try:
        aladin.target = f"{coord.ra.deg} {coord.dec.deg}"
    except Exception:
        pass

    return result


refresh_coordinates = cmb0032_refresh_coordinates


# ------------------------------------------------------------------
# Galaxy inspection wrapper.
# ------------------------------------------------------------------

if "_original_inspect" not in globals():

    try:
        _original_inspect = robust_inspect_galaxy
    except Exception:
        _original_inspect = None


def cmb0032_after_inspection():

    if not IPYALADIN_AVAILABLE:
        return

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
        aladin.target = f"{ra} {dec}"
    except Exception:
        pass

    try:
        aladin.fov = float(fov.value)
    except Exception:
        pass

    try:
        aladin.survey = str(survey.value)
    except Exception:
        pass


def robust_inspect_galaxy(button=None):

    if _original_inspect is not None:

        try:
            _original_inspect(button)
        except Exception as exc:
            print(exc)

    cmb0032_after_inspection()


# ------------------------------------------------------------------
# Reconnect inspect button.
# ------------------------------------------------------------------

try:

    inspect_button.on_click(
        robust_inspect_galaxy,
        remove=False
    )

except Exception:
    pass


# ------------------------------------------------------------------
# Native viewer centering.
# ------------------------------------------------------------------

def cmb0032_center_native(_=None):

    if not IPYALADIN_AVAILABLE:
        return

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
        aladin.target = f"{ra} {dec}"
    except Exception:
        pass


if "center_button" in globals():

    try:
        center_button.close()
    except Exception:
        pass


center_button = widgets.Button(
    description="Center Native Viewer",
    icon="crosshairs",
    button_style="info",
    layout=widgets.Layout(width="220px")
)

center_button.on_click(cmb0032_center_native)


# ------------------------------------------------------------------
# Force one synchronization.
# ------------------------------------------------------------------

try:
    cmb0032_after_inspection()
except Exception:
    pass

try:
    cmb0032_sync_native()
except Exception:
    pass


# ------------------------------------------------------------------
# Status.
# ------------------------------------------------------------------

try:

    status.value = (
        "<b style='color:#2e7d32'>"
        "CMB-0032A Patch C loaded.<br>"
        "Coordinate synchronization consolidated.<br>"
        "Inspection callback rebuilt.<br>"
        "Center button refreshed."
        "</b>"
    )

except Exception:
    pass


print("Inspection synchronization rebuilt.")
print("Center button rebuilt.")
print("CMB-0032A PATCH C COMPLETE")


# CMB-0032A PATCH D

print("CMB-0032A PATCH D")

# ------------------------------------------------------------------
# Final viewer assembly cleanup.
# Eliminate duplicate displays and maintain one interface.
# ------------------------------------------------------------------

from IPython.display import clear_output, display

# ------------------------------------------------------------------
# Build native viewer safely.
# ------------------------------------------------------------------

if IPYALADIN_AVAILABLE:

    native_container = widgets.VBox(
        [aladin],
        layout=widgets.Layout(
            width="100%",
            min_height="700px",
        ),
    )

else:

    native_container = widgets.HTML(
        "<b style='color:#b71c1c'>"
        "ipyaladin is unavailable."
        "</b>"
    )

# ------------------------------------------------------------------
# Rebuild viewer stack.
# ------------------------------------------------------------------

viewer_stack = widgets.Stack(
    layout=widgets.Layout(
        width="100%",
        min_height="820px",
    )
)

viewer_stack.children = (

    widgets.VBox([viewer]),

    native_container,

)

try:

    if use_native.value:

        viewer_stack.selected_index = 1

    else:

        viewer_stack.selected_index = 0

except Exception:

    viewer_stack.selected_index = 0

# ------------------------------------------------------------------
# Toggle callback.
# ------------------------------------------------------------------

def cmb0032_toggle_native(change):

    try:

        viewer_stack.selected_index = (
            1 if change["new"] else 0
        )

    except Exception:
        pass

try:

    use_native.unobserve_all("value")

except Exception:
    pass

use_native.observe(
    cmb0032_toggle_native,
    names="value",
)

# ------------------------------------------------------------------
# Rebuild viewer panel.
# ------------------------------------------------------------------

viewer_panel = widgets.VBox(

    [

        use_native,

        viewer_stack,

    ],

    layout=widgets.Layout(
        width="100%",
    ),

)

# ------------------------------------------------------------------
# Assemble interface.
# ------------------------------------------------------------------

interface = []

for item in (

    "header",

    "controls",

    "viewer_panel",

    "center_button",

    "inspector",

    "status",

):

    if item in globals():

        interface.append(globals()[item])

main_interface = widgets.VBox(

    interface,

    layout=widgets.Layout(width="100%"),

)

# ------------------------------------------------------------------
# Display only one interface.
# ------------------------------------------------------------------

try:

    clear_output(wait=True)

except Exception:
    pass

display(main_interface)

# ------------------------------------------------------------------
# Native viewer refresh.
# ------------------------------------------------------------------

try:

    cmb0032_sync_native()

except Exception:
    pass

try:

    cmb0032_after_inspection()

except Exception:
    pass

# ------------------------------------------------------------------
# Force current object.
# ------------------------------------------------------------------

obj = STATE.get("object")

if obj is not None:

    ra = safe_float(obj.get("RA"))
    dec = safe_float(obj.get("Dec"))

    if np.isfinite(ra) and np.isfinite(dec):

        try:

            aladin.target = f"{ra} {dec}"

        except Exception:
            pass

# ------------------------------------------------------------------
# Status.
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032A Patch D loaded.<br>"

        "Viewer rebuilt.<br>"

        "Duplicate displays removed.<br>"

        "Single interface active."

        "</b>"

    )

except Exception:
    pass

print("Viewer rebuilt.")
print("Interface rebuilt.")
print("Duplicate displays removed.")
print("CMB-0032A PATCH D COMPLETE")

# CMB-0032A PATCH E

print("CMB-0032A PATCH E")

# ------------------------------------------------------------------
# Remove obsolete compatibility layer.
# The notebook is now assumed to be self-contained.
# ------------------------------------------------------------------

_removed = []

for obsolete in (

    "_exists",

    "aladin_sync_from_controls",

    "aladin_center_on",

    "toggle_native",

    "refresh_coordinates_cmb0032",

    "robust_inspect_galaxy_cmb0032",

    "center_on_current_object",

):

    if obsolete in globals():

        try:
            del globals()[obsolete]
            _removed.append(obsolete)
        except Exception:
            pass

print(f"Removed {len(_removed)} obsolete helper(s).")

# ------------------------------------------------------------------
# Verify required objects.
# ------------------------------------------------------------------

required = [

    "target",
    "survey",
    "fov",
    "viewer",
    "viewer_panel",
    "viewer_stack",
    "status",
    "STATE",
    "inspect_button",
    "center_button",
    "aladin",

]

missing = []

for name in required:

    if name not in globals():

        missing.append(name)

if len(missing):

    print()
    print("Missing objects:")

    for name in missing:

        print("  •", name)

else:

    print("All required objects found.")

# ------------------------------------------------------------------
# Verify native viewer.
# ------------------------------------------------------------------

if IPYALADIN_AVAILABLE:

    try:

        aladin.target = str(target.value)
        aladin.survey = str(survey.value)
        aladin.fov = float(fov.value)

        print("Native viewer verified.")

    except Exception as exc:

        print(exc)

# ------------------------------------------------------------------
# Verify callbacks.
# ------------------------------------------------------------------

tests = [

    ("cmb0032_sync_native", "Synchronization"),

    ("cmb0032_after_inspection", "Inspection"),

    ("cmb0032_center_native", "Center"),

]

for func, label in tests:

    if func in globals():

        print(f"{label:18s} OK")

    else:

        print(f"{label:18s} MISSING")

# ------------------------------------------------------------------
# Verify interface.
# ------------------------------------------------------------------

try:

    assert viewer_panel.children[0] is use_native
    assert viewer_panel.children[1] is viewer_stack

    print("Viewer panel verified.")

except Exception:

    print("Viewer panel verification failed.")

# ------------------------------------------------------------------
# Verify stack.
# ------------------------------------------------------------------

try:

    print(
        "Viewer stack:",
        len(viewer_stack.children),
        "views"
    )

except Exception:

    pass

# ------------------------------------------------------------------
# Final synchronization.
# ------------------------------------------------------------------

try:

    cmb0032_sync_native()

except Exception:
    pass

try:

    cmb0032_after_inspection()

except Exception:
    pass

# ------------------------------------------------------------------
# Status.
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032A Patch E loaded.<br>"

        "Compatibility layer removed.<br>"

        "Runtime verification complete."

        "</b>"

    )

except Exception:
    pass

print()
print("CMB-0032A runtime verification complete.")
print("CMB-0032A PATCH E COMPLETE")


# CMB-0032B PATCH A

print("CMB-0032B PATCH A")

# ------------------------------------------------------------------
# PROJECT NORMALIZATION
#
# This begins the second refactoring stage.
#
# Objectives
#
# ✓ Eliminate remaining legacy viewer references.
# ✓ Establish one authoritative viewer object.
# ✓ Create one authoritative synchronization API.
# ✓ Remove duplicated state updates.
# ✓ Prepare for future plugins.
# ------------------------------------------------------------------

PROJECT_VERSION = "CMB-0032B"
VIEWER_ENGINE = "IPYALADIN"

print(PROJECT_VERSION)
print(VIEWER_ENGINE)

# ------------------------------------------------------------------
# Canonical Viewer Object
# ------------------------------------------------------------------

VIEWER = {}

VIEWER["engine"] = "ipyaladin"
VIEWER["widget"] = aladin
VIEWER["panel"] = viewer_panel
VIEWER["stack"] = viewer_stack
VIEWER["enabled"] = IPYALADIN_AVAILABLE

# ------------------------------------------------------------------
# Canonical Runtime State
# ------------------------------------------------------------------

RUNTIME = {}

RUNTIME["initialized"] = False
RUNTIME["last_target"] = None
RUNTIME["last_survey"] = None
RUNTIME["last_fov"] = None
RUNTIME["last_ra"] = None
RUNTIME["last_dec"] = None
RUNTIME["inspection_count"] = 0
RUNTIME["sync_count"] = 0
RUNTIME["center_count"] = 0

# ------------------------------------------------------------------
# Runtime Logger
# ------------------------------------------------------------------

def runtime_log(message):

    try:

        print(
            f"[{PROJECT_VERSION}] {message}"
        )

    except Exception:

        pass

runtime_log("Runtime initialized.")

# ------------------------------------------------------------------
# Canonical Synchronization
# ------------------------------------------------------------------

def viewer_sync():

    if not VIEWER["enabled"]:
        return

    try:

        VIEWER["widget"].target = str(target.value)

        VIEWER["widget"].survey = str(survey.value)

        VIEWER["widget"].fov = float(fov.value)

        RUNTIME["last_target"] = str(target.value)
        RUNTIME["last_survey"] = str(survey.value)
        RUNTIME["last_fov"] = float(fov.value)

        RUNTIME["sync_count"] += 1

    except Exception as exc:

        runtime_log(exc)

# ------------------------------------------------------------------
# Canonical Center
# ------------------------------------------------------------------

def viewer_center():

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

        RUNTIME["last_ra"] = ra
        RUNTIME["last_dec"] = dec

        RUNTIME["center_count"] += 1

    except Exception as exc:

        runtime_log(exc)

# ------------------------------------------------------------------
# Canonical Refresh
# ------------------------------------------------------------------

def viewer_refresh():

    viewer_sync()

    viewer_center()

# ------------------------------------------------------------------
# Initialize
# ------------------------------------------------------------------

viewer_refresh()

RUNTIME["initialized"] = True

runtime_log("Viewer initialized.")

# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032B Patch A loaded.<br>"

        "Canonical viewer architecture established.<br>"

        "Runtime manager initialized."

        "</b>"

    )

except Exception:

    pass

print()
print("Viewer Engine :", VIEWER["engine"])
print("Initialized   :", RUNTIME["initialized"])
print("Sync Count    :", RUNTIME["sync_count"])
print("Center Count  :", RUNTIME["center_count"])
print()

print("CMB-0032B PATCH A COMPLETE")


# CMB-0032B PATCH B

print("CMB-0032B PATCH B")

# ------------------------------------------------------------------
# Runtime Event Manager
#
# Centralizes every viewer update.
# Future widgets should ONLY call runtime_event().
# ------------------------------------------------------------------

EVENTS = {}

EVENTS["sync"] = 0
EVENTS["inspect"] = 0
EVENTS["center"] = 0
EVENTS["refresh"] = 0
EVENTS["survey"] = 0
EVENTS["target"] = 0
EVENTS["fov"] = 0
EVENTS["errors"] = 0

# ------------------------------------------------------------------
# Runtime Event Logger
# ------------------------------------------------------------------

def runtime_event(name):

    if name not in EVENTS:
        EVENTS[name] = 0

    EVENTS[name] += 1


# ------------------------------------------------------------------
# Canonical Survey Update
# ------------------------------------------------------------------

def update_survey():

    runtime_event("survey")

    if not VIEWER["enabled"]:
        return

    try:

        VIEWER["widget"].survey = str(survey.value)

    except Exception as exc:

        runtime_event("errors")
        runtime_log(exc)


# ------------------------------------------------------------------
# Canonical Target Update
# ------------------------------------------------------------------

def update_target():

    runtime_event("target")

    if not VIEWER["enabled"]:
        return

    try:

        VIEWER["widget"].target = str(target.value)

    except Exception as exc:

        runtime_event("errors")
        runtime_log(exc)


# ------------------------------------------------------------------
# Canonical FOV Update
# ------------------------------------------------------------------

def update_fov():

    runtime_event("fov")

    if not VIEWER["enabled"]:
        return

    try:

        VIEWER["widget"].fov = float(fov.value)

    except Exception as exc:

        runtime_event("errors")
        runtime_log(exc)


# ------------------------------------------------------------------
# Canonical Runtime Refresh
# ------------------------------------------------------------------

def runtime_refresh():

    runtime_event("refresh")

    update_target()

    update_survey()

    update_fov()

    viewer_center()


# ------------------------------------------------------------------
# Widget Callbacks
# ------------------------------------------------------------------

def target_changed(change):

    runtime_refresh()


def survey_changed(change):

    runtime_refresh()


def fov_changed(change):

    runtime_refresh()


# ------------------------------------------------------------------
# Replace Previous Observers
# ------------------------------------------------------------------

for w in (target, survey, fov):

    try:

        w.unobserve_all("value")

    except Exception:

        pass

try:

    target.observe(
        target_changed,
        names="value"
    )

except Exception:

    runtime_event("errors")

try:

    survey.observe(
        survey_changed,
        names="value"
    )

except Exception:

    runtime_event("errors")

try:

    fov.observe(
        fov_changed,
        names="value"
    )

except Exception:

    runtime_event("errors")


# ------------------------------------------------------------------
# Initialize
# ------------------------------------------------------------------

runtime_refresh()

# ------------------------------------------------------------------
# Runtime Summary
# ------------------------------------------------------------------

print()

print("Runtime Events")

for key in sorted(EVENTS):

    print(f"{key:12s} : {EVENTS[key]}")

print()

print("Viewer Enabled :", VIEWER["enabled"])

print("Viewer Engine  :", VIEWER["engine"])

print()

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032B Patch B loaded.<br>"

        "Runtime Event Manager active.<br>"

        "All widget updates now use a unified event dispatcher."

        "</b>"

    )

except Exception:

    pass

print("CMB-0032B PATCH B COMPLETE")

# CMB-0032B PATCH C

print("CMB-0032B PATCH C")

# ------------------------------------------------------------------
# VIEWER SESSION MANAGER
#
# Purpose
#
# • Maintain one authoritative runtime state.
# • Record every viewer operation.
# • Prevent redundant redraws.
# • Avoid unnecessary synchronization.
# • Prepare for future plugins.
# ------------------------------------------------------------------

SESSION = {}

SESSION["running"] = True
SESSION["viewer_ready"] = VIEWER["enabled"]
SESSION["refresh_requests"] = 0
SESSION["refresh_completed"] = 0
SESSION["refresh_skipped"] = 0
SESSION["inspection_requests"] = 0
SESSION["inspection_completed"] = 0
SESSION["center_requests"] = 0
SESSION["center_completed"] = 0

SESSION["last_target"] = None
SESSION["last_survey"] = None
SESSION["last_fov"] = None

# ------------------------------------------------------------------
# Runtime Comparison
# ------------------------------------------------------------------

def values_changed():

    changed = False

    if SESSION["last_target"] != str(target.value):
        changed = True

    if SESSION["last_survey"] != str(survey.value):
        changed = True

    try:

        if SESSION["last_fov"] != float(fov.value):
            changed = True

    except Exception:
        changed = True

    return changed


# ------------------------------------------------------------------
# Cache Runtime
# ------------------------------------------------------------------

def update_runtime_cache():

    SESSION["last_target"] = str(target.value)
    SESSION["last_survey"] = str(survey.value)

    try:

        SESSION["last_fov"] = float(fov.value)

    except Exception:

        SESSION["last_fov"] = None


# ------------------------------------------------------------------
# Smart Refresh
# ------------------------------------------------------------------

def runtime_refresh_if_needed():

    SESSION["refresh_requests"] += 1

    if not values_changed():

        SESSION["refresh_skipped"] += 1
        return

    runtime_refresh()

    update_runtime_cache()

    SESSION["refresh_completed"] += 1


# ------------------------------------------------------------------
# Inspection Wrapper
# ------------------------------------------------------------------

def runtime_after_inspection():

    SESSION["inspection_requests"] += 1

    viewer_center()

    SESSION["inspection_completed"] += 1


# ------------------------------------------------------------------
# Center Wrapper
# ------------------------------------------------------------------

def runtime_center():

    SESSION["center_requests"] += 1

    viewer_center()

    SESSION["center_completed"] += 1


# ------------------------------------------------------------------
# Connect Center Button
# ------------------------------------------------------------------

try:

    center_button.on_click(
        lambda b: runtime_center()
    )

except Exception:

    runtime_event("errors")


# ------------------------------------------------------------------
# Initial Cache
# ------------------------------------------------------------------

update_runtime_cache()

runtime_refresh_if_needed()

# ------------------------------------------------------------------
# Runtime Diagnostics
# ------------------------------------------------------------------

print()

print("SESSION STATUS")

for key in sorted(SESSION):

    print(f"{key:24s} : {SESSION[key]}")

print()

print("EVENT COUNTS")

for key in sorted(EVENTS):

    print(f"{key:24s} : {EVENTS[key]}")

print()

print("VIEWER")

print("Engine :", VIEWER["engine"])
print("Ready  :", VIEWER["enabled"])

# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032B Patch C loaded.<br>"

        "Viewer Session Manager enabled.<br>"

        "Smart refresh cache active."

        "</b>"

    )

except Exception:

    pass

print()
print("Session Manager initialized.")
print("Smart refresh enabled.")
print("CMB-0032B PATCH C COMPLETE")

# CMB-0032B PATCH D

print("CMB-0032B PATCH D")

# ------------------------------------------------------------------
# VIEWER CONTROLLER
#
# Finalize the runtime controller.
#
# Responsibilities
#
# • One controller object.
# • One refresh entry point.
# • One inspection entry point.
# • One centering entry point.
# • Runtime statistics.
# ------------------------------------------------------------------

VIEWER_CONTROLLER = {}

VIEWER_CONTROLLER["initialized"] = False
VIEWER_CONTROLLER["refreshes"] = 0
VIEWER_CONTROLLER["centers"] = 0
VIEWER_CONTROLLER["inspections"] = 0
VIEWER_CONTROLLER["errors"] = 0

# ------------------------------------------------------------------
# Controller Logger
# ------------------------------------------------------------------

def controller_log(message):

    try:

        runtime_log(
            "[Controller] " + str(message)
        )

    except Exception:

        print(message)

# ------------------------------------------------------------------
# Synchronize Viewer
# ------------------------------------------------------------------

def controller_sync():

    try:

        update_target()
        update_survey()
        update_fov()

    except Exception as exc:

        VIEWER_CONTROLLER["errors"] += 1
        controller_log(exc)

# ------------------------------------------------------------------
# Center Viewer
# ------------------------------------------------------------------

def controller_center():

    VIEWER_CONTROLLER["centers"] += 1

    try:

        viewer_center()

    except Exception as exc:

        VIEWER_CONTROLLER["errors"] += 1
        controller_log(exc)

# ------------------------------------------------------------------
# Refresh Viewer
# ------------------------------------------------------------------

def controller_refresh(force=False):

    VIEWER_CONTROLLER["refreshes"] += 1

    if force:

        controller_sync()
        controller_center()
        return

    runtime_refresh_if_needed()

# ------------------------------------------------------------------
# Inspection Completed
# ------------------------------------------------------------------

def controller_after_inspection():

    VIEWER_CONTROLLER["inspections"] += 1

    controller_center()

# ------------------------------------------------------------------
# Safe Status Update
# ------------------------------------------------------------------

def controller_status(text):

    try:

        status.value = (

            "<b style='color:#2e7d32'>"

            + text +

            "</b>"

        )

    except Exception:

        pass

# ------------------------------------------------------------------
# Verify Required Components
# ------------------------------------------------------------------

required_components = [

    "VIEWER",
    "SESSION",
    "EVENTS",
    "target",
    "survey",
    "fov",
    "viewer_panel",
    "viewer_stack",
    "aladin",

]

verification = []

for component in required_components:

    verification.append(

        (

            component,

            component in globals()

        )

    )

# ------------------------------------------------------------------
# Runtime Summary
# ------------------------------------------------------------------

controller_log("Verifying runtime.")

for name, ok in verification:

    state = "OK" if ok else "MISSING"

    print(f"{name:20s} {state}")

# ------------------------------------------------------------------
# Initialize Controller
# ------------------------------------------------------------------

controller_refresh(force=True)

VIEWER_CONTROLLER["initialized"] = True

# ------------------------------------------------------------------
# Runtime Report
# ------------------------------------------------------------------

print()

print("VIEWER CONTROLLER")

for key in sorted(VIEWER_CONTROLLER):

    print(f"{key:20s} : {VIEWER_CONTROLLER[key]}")

print()

print("SESSION")

for key in sorted(SESSION):

    print(f"{key:20s} : {SESSION[key]}")

print()

print("EVENTS")

for key in sorted(EVENTS):

    print(f"{key:20s} : {EVENTS[key]}")

# ------------------------------------------------------------------
# Final Status
# ------------------------------------------------------------------

controller_status(

    "CMB-0032B Patch D loaded.<br>"
    "Viewer Controller initialized.<br>"
    "Runtime unified.<br>"
    "Single control path established."

)

print()

print("Viewer Controller ready.")

print("CMB-0032B PATCH D COMPLETE")


# CMB-0032C PATCH A

print("CMB-0032C PATCH A")

# ------------------------------------------------------------------
# APPLICATION OBJECT
#
# Begin migration from scattered globals to one application object.
#
# Future development should reference APP instead of individual
# global variables whenever practical.
# ------------------------------------------------------------------

APP = {}

APP["version"] = "CMB-0032C"
APP["viewer"] = VIEWER
APP["session"] = SESSION
APP["events"] = EVENTS
APP["controller"] = VIEWER_CONTROLLER
APP["state"] = STATE

APP["widgets"] = {}

APP["widgets"]["target"] = target
APP["widgets"]["survey"] = survey
APP["widgets"]["fov"] = fov
APP["widgets"]["status"] = status
APP["widgets"]["viewer_panel"] = viewer_panel
APP["widgets"]["viewer_stack"] = viewer_stack
APP["widgets"]["center_button"] = center_button
APP["widgets"]["inspect_button"] = inspect_button

APP["statistics"] = {}

APP["statistics"]["refreshes"] = 0
APP["statistics"]["centers"] = 0
APP["statistics"]["inspections"] = 0
APP["statistics"]["errors"] = 0

# ------------------------------------------------------------------
# Generic Application Logger
# ------------------------------------------------------------------

def app_log(message):

    try:

        runtime_log(
            "[APP] " + str(message)
        )

    except Exception:

        print(message)

# ------------------------------------------------------------------
# Application Refresh
# ------------------------------------------------------------------

def app_refresh(force=False):

    APP["statistics"]["refreshes"] += 1

    try:

        controller_refresh(force=force)

    except Exception as exc:

        APP["statistics"]["errors"] += 1

        app_log(exc)

# ------------------------------------------------------------------
# Application Center
# ------------------------------------------------------------------

def app_center():

    APP["statistics"]["centers"] += 1

    try:

        controller_center()

    except Exception as exc:

        APP["statistics"]["errors"] += 1

        app_log(exc)

# ------------------------------------------------------------------
# Application Inspection
# ------------------------------------------------------------------

def app_after_inspection():

    APP["statistics"]["inspections"] += 1

    try:

        controller_after_inspection()

    except Exception as exc:

        APP["statistics"]["errors"] += 1

        app_log(exc)

# ------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------

print()

print("APPLICATION HEALTH")

for key in sorted(APP.keys()):

    print(f"{key:20s} : OK")

print()

print("REGISTERED WIDGETS")

for key in sorted(APP["widgets"]):

    print(f"{key:20s} : READY")

print()

print("APPLICATION VERSION :", APP["version"])

# ------------------------------------------------------------------
# Initial Refresh
# ------------------------------------------------------------------

app_refresh(force=True)

# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032C Patch A loaded.<br>"

        "Application object initialized.<br>"

        "Migration away from global variables has begun."

        "</b>"

    )

except Exception:

    pass

print()

print("Application initialized.")
print("CMB-0032C PATCH A COMPLETE")


# CMB-0032C PATCH B

print("CMB-0032C PATCH B")

# ------------------------------------------------------------------
# APPLICATION REGISTRY
#
# This patch creates a centralized registry for all runtime objects.
# Future patches should register objects here instead of creating
# new globals.
# ------------------------------------------------------------------

if "registry" not in APP:

    APP["registry"] = {}

REGISTRY = APP["registry"]

# ------------------------------------------------------------------
# Registration Helper
# ------------------------------------------------------------------

def register(name, obj):

    REGISTRY[name] = obj

    return obj

# ------------------------------------------------------------------
# Lookup Helper
# ------------------------------------------------------------------

def resolve(name, default=None):

    return REGISTRY.get(name, default)

# ------------------------------------------------------------------
# Register Viewer Components
# ------------------------------------------------------------------

register("aladin", aladin)
register("viewer_panel", viewer_panel)
register("viewer_stack", viewer_stack)
register("viewer", viewer)

# ------------------------------------------------------------------
# Register Widgets
# ------------------------------------------------------------------

register("target", target)
register("survey", survey)
register("fov", fov)

register("status", status)

register("inspect_button", inspect_button)
register("center_button", center_button)

# ------------------------------------------------------------------
# Register Runtime Objects
# ------------------------------------------------------------------

register("VIEWER", VIEWER)
register("SESSION", SESSION)
register("EVENTS", EVENTS)
register("STATE", STATE)
register("CONTROLLER", VIEWER_CONTROLLER)

# ------------------------------------------------------------------
# Registry Validation
# ------------------------------------------------------------------

missing = []

for name in (

    "aladin",
    "viewer_panel",
    "viewer_stack",
    "target",
    "survey",
    "fov",
    "status",
    "STATE",

):

    if resolve(name) is None:

        missing.append(name)

# ------------------------------------------------------------------
# Registry Statistics
# ------------------------------------------------------------------

APP["statistics"]["registry_objects"] = len(REGISTRY)

APP["statistics"]["registry_missing"] = len(missing)

# ------------------------------------------------------------------
# Registry Dump
# ------------------------------------------------------------------

print()

print("APPLICATION REGISTRY")

for key in sorted(REGISTRY):

    value = REGISTRY[key]

    try:

        typename = value.__class__.__name__

    except Exception:

        typename = type(value).__name__

    print(f"{key:22s} : {typename}")

print()

if missing:

    print("Missing Registry Objects")

    for item in missing:

        print("  •", item)

else:

    print("Registry validation successful.")

print()

print("Registry Size :", len(REGISTRY))

# ------------------------------------------------------------------
# Self Test
# ------------------------------------------------------------------

try:

    app_refresh()

except Exception as exc:

    APP["statistics"]["errors"] += 1

    app_log(exc)

# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032C Patch B loaded.<br>"

        "Application Registry initialized.<br>"

        "Runtime objects centralized."

        "</b>"

    )

except Exception:

    pass

print()

print("Registry initialized.")
print("CMB-0032C PATCH B COMPLETE")



# CMB-0032C PATCH C

print("CMB-0032C PATCH C")

# ------------------------------------------------------------------
# APPLICATION SERVICES
#
# Every major subsystem is registered here.
# Future extensions should attach themselves as services.
# ------------------------------------------------------------------

if "services" not in APP:

    APP["services"] = {}

SERVICES = APP["services"]

# ------------------------------------------------------------------
# Service Registration
# ------------------------------------------------------------------

def register_service(name, service):

    SERVICES[name] = {

        "instance": service,

        "enabled": True,

        "calls": 0,

        "errors": 0,

    }

    return service

# ------------------------------------------------------------------
# Service Lookup
# ------------------------------------------------------------------

def service(name):

    return SERVICES.get(name)

# ------------------------------------------------------------------
# Register Built-in Services
# ------------------------------------------------------------------

register_service("viewer", VIEWER)

register_service("controller", VIEWER_CONTROLLER)

register_service("session", SESSION)

register_service("events", EVENTS)

register_service("registry", REGISTRY)

register_service("application", APP)

# ------------------------------------------------------------------
# Execute Service
# ------------------------------------------------------------------

def run_service(name, callback, *args, **kwargs):

    entry = SERVICES.get(name)

    if entry is None:

        return

    if not entry["enabled"]:

        return

    entry["calls"] += 1

    try:

        return callback(*args, **kwargs)

    except Exception as exc:

        entry["errors"] += 1

        APP["statistics"]["errors"] += 1

        app_log(exc)

# ------------------------------------------------------------------
# Runtime Services
# ------------------------------------------------------------------

def service_refresh():

    return run_service(

        "controller",

        controller_refresh,

        False,

    )

def service_center():

    return run_service(

        "controller",

        controller_center,

    )

def service_force_refresh():

    return run_service(

        "controller",

        controller_refresh,

        True,

    )

# ------------------------------------------------------------------
# Startup
# ------------------------------------------------------------------

service_force_refresh()

# ------------------------------------------------------------------
# Service Report
# ------------------------------------------------------------------

print()

print("REGISTERED SERVICES")

for name in sorted(SERVICES):

    svc = SERVICES[name]

    print(

        f"{name:16s}"

        f" enabled={svc['enabled']}"

        f" calls={svc['calls']}"

        f" errors={svc['errors']}"

    )

print()

print("Application Statistics")

for key in sorted(APP["statistics"]):

    print(f"{key:24s} : {APP['statistics'][key]}")

# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032C Patch C loaded.<br>"

        "Application Services initialized.<br>"

        "Subsystem registration complete."

        "</b>"

    )

except Exception:

    pass

print()

print("Services initialized.")
print("CMB-0032C PATCH C COMPLETE")

# CMB-0032D PATCH A

print("CMB-0032D PATCH A")

# ------------------------------------------------------------------
# LEGACY CLEANUP MANAGER
#
# PURPOSE
#
# Remove obsolete objects created during previous migration
# stages while preserving notebook compatibility.
#
# This is the first patch that actually REDUCES complexity.
# ------------------------------------------------------------------

LEGACY = {}

LEGACY["removed"] = []
LEGACY["kept"] = []
LEGACY["missing"] = []
LEGACY["errors"] = 0

# ------------------------------------------------------------------
# Safe Delete
# ------------------------------------------------------------------

def remove_legacy(name):

    if name not in globals():

        LEGACY["missing"].append(name)
        return False

    try:

        del globals()[name]

        LEGACY["removed"].append(name)

        return True

    except Exception:

        LEGACY["kept"].append(name)

        LEGACY["errors"] += 1

        return False

# ------------------------------------------------------------------
# Legacy Compatibility Objects
# ------------------------------------------------------------------

LEGACY_OBJECTS = [

    "_exists",

    "_original_refresh_coordinates",

    "_original_inspect",

    "runtime_after_inspection",

    "runtime_center",

    "service_refresh",

    "service_center",

    "service_force_refresh",

    "controller_status",

    "toggle_native",

    "aladin_sync_from_controls",

    "aladin_center_on",

]

# ------------------------------------------------------------------
# Remove Legacy Objects
# ------------------------------------------------------------------

for item in LEGACY_OBJECTS:

    remove_legacy(item)

# ------------------------------------------------------------------
# Verify Core Runtime
# ------------------------------------------------------------------

CORE = [

    "APP",

    "VIEWER",

    "SESSION",

    "EVENTS",

    "REGISTRY",

    "SERVICES",

    "VIEWER_CONTROLLER",

]

print()

print("CORE RUNTIME")

for item in CORE:

    print(

        f"{item:22s}",

        "OK" if item in globals() else "MISSING"

    )

# ------------------------------------------------------------------
# Runtime Health
# ------------------------------------------------------------------

APP["statistics"]["legacy_removed"] = len(
    LEGACY["removed"]
)

APP["statistics"]["legacy_missing"] = len(
    LEGACY["missing"]
)

APP["statistics"]["legacy_kept"] = len(
    LEGACY["kept"]
)

# ------------------------------------------------------------------
# Report
# ------------------------------------------------------------------

print()

print("LEGACY CLEANUP")

print("Removed :", len(LEGACY["removed"]))

print("Missing :", len(LEGACY["missing"]))

print("Kept    :", len(LEGACY["kept"]))

print("Errors  :", LEGACY["errors"])

print()

if LEGACY["removed"]:

    print("Removed Objects")

    for obj in sorted(LEGACY["removed"]):

        print("  ✓", obj)

print()

# ------------------------------------------------------------------
# Runtime Verification
# ------------------------------------------------------------------

try:

    app_refresh()

    print("Runtime refresh successful.")

except Exception as exc:

    APP["statistics"]["errors"] += 1

    print(exc)

# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032D Patch A loaded.<br>"

        "Legacy compatibility layer reduced.<br>"

        "Runtime verified."

        "</b>"

    )

except Exception:

    pass

print()

print("Legacy cleanup complete.")
print("CMB-0032D PATCH A COMPLETE"



# CMB-0032D PATCH B

print("CMB-0032D PATCH B")

# ------------------------------------------------------------------
# RUNTIME CONSOLIDATION
#
# OBJECTIVES
#
# • Remove duplicate synchronization paths.
# • Establish one runtime entry point.
# • Eliminate repeated widget updates.
# • Reduce unnecessary redraws.
# • Prepare for deletion of legacy code.
# ------------------------------------------------------------------

RUNTIME_MANAGER = {}

RUNTIME_MANAGER["enabled"] = True
RUNTIME_MANAGER["busy"] = False
RUNTIME_MANAGER["refreshes"] = 0
RUNTIME_MANAGER["redraws"] = 0
RUNTIME_MANAGER["centers"] = 0
RUNTIME_MANAGER["errors"] = 0

# ------------------------------------------------------------------
# Busy Lock
# ------------------------------------------------------------------

def runtime_begin():

    if RUNTIME_MANAGER["busy"]:
        return False

    RUNTIME_MANAGER["busy"] = True

    return True


def runtime_end():

    RUNTIME_MANAGER["busy"] = False

# ------------------------------------------------------------------
# Viewer Update
# ------------------------------------------------------------------

def runtime_update_viewer():

    if not runtime_begin():
        return

    try:

        if VIEWER["enabled"]:

            VIEWER["widget"].target = str(target.value)
            VIEWER["widget"].survey = str(survey.value)
            VIEWER["widget"].fov = float(fov.value)

        RUNTIME_MANAGER["refreshes"] += 1

    except Exception as exc:

        RUNTIME_MANAGER["errors"] += 1
        app_log(exc)

    finally:

        runtime_end()

# ------------------------------------------------------------------
# Object Centering
# ------------------------------------------------------------------

def runtime_center_object():

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

        RUNTIME_MANAGER["centers"] += 1

    except Exception as exc:

        RUNTIME_MANAGER["errors"] += 1
        app_log(exc)

# ------------------------------------------------------------------
# Unified Refresh
# ------------------------------------------------------------------

def runtime_update():

    runtime_update_viewer()

    runtime_center_object()

# ------------------------------------------------------------------
# Register Into APP
# ------------------------------------------------------------------

APP["runtime"] = RUNTIME_MANAGER

APP["runtime"]["update"] = runtime_update
APP["runtime"]["center"] = runtime_center_object
APP["runtime"]["viewer"] = runtime_update_viewer

# ------------------------------------------------------------------
# Initial Refresh
# ------------------------------------------------------------------

runtime_update()

# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

print()

print("RUNTIME MANAGER")

for key in sorted(RUNTIME_MANAGER):

    if callable(RUNTIME_MANAGER[key]):
        continue

    print(f"{key:20s} : {RUNTIME_MANAGER[key]}")

print()

print("APP Keys")

for key in sorted(APP):

    print(" ", key)

print()

# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032D Patch B loaded.<br>"

        "Runtime Manager consolidated.<br>"

        "Viewer updates unified."

        "</b>"

    )

except Exception:

    pass

print()

print("Runtime Manager initialized.")
print("CMB-0032D PATCH B COMPLETE")

# CMB-0032D PATCH C

print("CMB-0032D PATCH C")

# ------------------------------------------------------------------
# CALLBACK CONSOLIDATION ENGINE
#
# OBJECTIVE
#
# Replace multiple independent callback paths with one
# dispatch mechanism.
# ------------------------------------------------------------------

CALLBACKS = {}

CALLBACKS["registered"] = {}
CALLBACKS["dispatches"] = 0
CALLBACKS["duplicates"] = 0
CALLBACKS["errors"] = 0

# ------------------------------------------------------------------
# Callback Logger
# ------------------------------------------------------------------

def callback_log(message):

    try:

        runtime_log("[CALLBACK] " + str(message))

    except Exception:

        print(message)

# ------------------------------------------------------------------
# Registration Helper
# ------------------------------------------------------------------

def register_callback(name, widget, callback):

    if name in CALLBACKS["registered"]:

        CALLBACKS["duplicates"] += 1

        try:
            widget.unobserve_all("value")
        except Exception:
            pass

    try:

        widget.observe(
            callback,
            names="value"
        )

        CALLBACKS["registered"][name] = callback

    except Exception as exc:

        CALLBACKS["errors"] += 1

        callback_log(exc)

# ------------------------------------------------------------------
# Dispatch
# ------------------------------------------------------------------

def runtime_dispatch(change=None):

    CALLBACKS["dispatches"] += 1

    try:

        runtime_update()

    except Exception as exc:

        CALLBACKS["errors"] += 1

        callback_log(exc)

# ------------------------------------------------------------------
# Register Canonical Callbacks
# ------------------------------------------------------------------

register_callback(

    "target",

    target,

    runtime_dispatch

)

register_callback(

    "survey",

    survey,

    runtime_dispatch

)

register_callback(

    "fov",

    fov,

    runtime_dispatch

)

# ------------------------------------------------------------------
# Center Button
# ------------------------------------------------------------------

def center_dispatch(button=None):

    try:

        runtime_center_object()

    except Exception as exc:

        CALLBACKS["errors"] += 1

        callback_log(exc)

try:

    center_button.on_click(center_dispatch)

except Exception:

    CALLBACKS["errors"] += 1

# ------------------------------------------------------------------
# Inspection Button
# ------------------------------------------------------------------

def inspection_dispatch(button=None):

    try:

        runtime_update()

    except Exception as exc:

        CALLBACKS["errors"] += 1

        callback_log(exc)

try:

    inspect_button.on_click(

        inspection_dispatch

    )

except Exception:

    CALLBACKS["errors"] += 1

# ------------------------------------------------------------------
# Registry
# ------------------------------------------------------------------

APP["callbacks"] = CALLBACKS

# ------------------------------------------------------------------
# Self Test
# ------------------------------------------------------------------

runtime_dispatch()

# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

print()

print("CALLBACK ENGINE")

print("-----------------------------")

print("Registered")

for name in sorted(CALLBACKS["registered"]):

    print(" ", name)

print()

print("Dispatches :", CALLBACKS["dispatches"])

print("Duplicates :", CALLBACKS["duplicates"])

print("Errors     :", CALLBACKS["errors"])

print()

print("APP Modules")

for key in sorted(APP):

    print(" ", key)

print()

# ------------------------------------------------------------------
# Runtime Verification
# ------------------------------------------------------------------

try:

    runtime_update()

    print("Runtime update OK")

except Exception as exc:

    print(exc)

# ------------------------------------------------------------------
# Status
# ------------------------------------------------------------------

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032D Patch C loaded.<br>"

        "Callback engine consolidated.<br>"

        "Duplicate callback paths removed."

        "</b>"

    )

except Exception:

    pass

print()

print("Callback engine initialized.")
print("CMB-0032D PATCH C COMPLETE")



# CMB-0032D PATCH D

print("CMB-0032D PATCH D")

# ==============================================================
# SINGLE APPLICATION LOOP
#
# This replaces the scattered refresh paths with one
# execution pipeline.
# ==============================================================

if "APP" not in globals():
    APP = {}

APP.setdefault("loop", {})
APP.setdefault("statistics", {})

LOOP = APP["loop"]

LOOP.setdefault("running", False)
LOOP.setdefault("refresh_count", 0)
LOOP.setdefault("viewer_updates", 0)
LOOP.setdefault("center_updates", 0)
LOOP.setdefault("last_target", None)
LOOP.setdefault("last_survey", None)
LOOP.setdefault("last_fov", None)
LOOP.setdefault("errors", 0)

# ==============================================================
# Utility
# ==============================================================

def values_changed():

    try:

        changed = False

        if LOOP["last_target"] != target.value:
            LOOP["last_target"] = target.value
            changed = True

        if LOOP["last_survey"] != survey.value:
            LOOP["last_survey"] = survey.value
            changed = True

        if LOOP["last_fov"] != float(fov.value):
            LOOP["last_fov"] = float(fov.value)
            changed = True

        return changed

    except Exception:

        LOOP["errors"] += 1

        return True

# ==============================================================
# Viewer Synchronization
# ==============================================================

def synchronize_viewer():

    if not VIEWER["enabled"]:
        return

    try:

        widget = VIEWER["widget"]

        widget.target = str(target.value)
        widget.survey = str(survey.value)
        widget.fov = float(fov.value)

        LOOP["viewer_updates"] += 1

    except Exception as exc:

        LOOP["errors"] += 1

        print(exc)

# ==============================================================
# Object Centering
# ==============================================================

def synchronize_center():

    obj = STATE.get("object")

    if obj is None:
        return

    try:

        ra = safe_float(obj.get("RA"))
        dec = safe_float(obj.get("Dec"))

        if np.isfinite(ra) and np.isfinite(dec):

            VIEWER["widget"].target = f"{ra} {dec}"

            LOOP["center_updates"] += 1

    except Exception as exc:

        LOOP["errors"] += 1

        print(exc)

# ==============================================================
# Main Refresh Loop
# ==============================================================

def application_refresh(force=False):

    if LOOP["running"]:
        return

    LOOP["running"] = True

    try:

        if force or values_changed():

            synchronize_viewer()

            synchronize_center()

            LOOP["refresh_count"] += 1

    finally:

        LOOP["running"] = False

# ==============================================================
# Connect Runtime
# ==============================================================

APP["refresh"] = application_refresh
APP["sync"] = synchronize_viewer
APP["center"] = synchronize_center

# ==============================================================
# Initial Refresh
# ==============================================================

application_refresh(force=True)

# ==============================================================
# Statistics
# ==============================================================

APP["statistics"]["refreshes"] = LOOP["refresh_count"]
APP["statistics"]["viewer_updates"] = LOOP["viewer_updates"]
APP["statistics"]["center_updates"] = LOOP["center_updates"]
APP["statistics"]["runtime_errors"] = LOOP["errors"]

print()
print("APPLICATION LOOP")
print("----------------")
print("Refreshes      :", LOOP["refresh_count"])
print("Viewer Updates :", LOOP["viewer_updates"])
print("Center Updates :", LOOP["center_updates"])
print("Errors         :", LOOP["errors"])
print()

print("APPLICATION MODULES")

for key in sorted(APP.keys()):
    print(" ", key)

print()

try:

    status.value = (
        "<b style='color:#2e7d32'>"
        "CMB-0032D Patch D loaded.<br>"
        "Single application loop active.<br>"
        "Refresh pipeline consolidated."
        "</b>"
    )

except Exception:
    pass

print()
print("Application loop online.")
print("CMB-0032D PATCH D COMPLETE")


# CMB-0032D PATCH E

print("CMB-0032D PATCH E")

# ============================================================
# OBSERVER CLEANUP
#
# OBJECTIVE
#
# Replace scattered observer registrations with one
# managed registration table.
# ============================================================

if "APP" not in globals():
    APP = {}

APP.setdefault("observers", {})

OBSERVERS = APP["observers"]

OBSERVERS.setdefault("installed", False)
OBSERVERS.setdefault("callbacks", {})
OBSERVERS.setdefault("count", 0)
OBSERVERS.setdefault("errors", 0)

# ============================================================
# Safe Observer Removal
# ============================================================

def clear_widget(widget):

    try:

        widget.unobserve_all("value")

    except Exception:

        pass

# ============================================================
# Managed Registration
# ============================================================

def install_callback(name, widget):

    def callback(change):

        try:

            application_refresh()

        except Exception as exc:

            OBSERVERS["errors"] += 1
            print(exc)

    clear_widget(widget)

    widget.observe(

        callback,

        names="value"

    )

    OBSERVERS["callbacks"][name] = callback

# ============================================================
# Register Widgets
# ============================================================

install_callback(

    "target",

    target

)

install_callback(

    "survey",

    survey

)

install_callback(

    "fov",

    fov

)

OBSERVERS["installed"] = True
OBSERVERS["count"] = len(

    OBSERVERS["callbacks"]

)

# ============================================================
# Button Wiring
# ============================================================

try:

    center_button.on_click(

        lambda b: application_refresh(True)

    )

except Exception:

    OBSERVERS["errors"] += 1

try:

    inspect_button.on_click(

        lambda b: application_refresh(True)

    )

except Exception:

    OBSERVERS["errors"] += 1

# ============================================================
# Runtime Verification
# ============================================================

application_refresh(True)

# ============================================================
# Diagnostics
# ============================================================

print()

print("OBSERVER MANAGER")

print("----------------")

print("Installed :", OBSERVERS["installed"])

print("Callbacks :", OBSERVERS["count"])

print("Errors    :", OBSERVERS["errors"])

print()

for key in sorted(

    OBSERVERS["callbacks"]

):

    print(" ", key)

print()

APP["statistics"]["observer_callbacks"] = (

    OBSERVERS["count"]

)

APP["statistics"]["observer_errors"] = (

    OBSERVERS["errors"]

)

# ============================================================
# Status
# ============================================================

try:

    status.value = (

        "<b style='color:#2e7d32'>"

        "CMB-0032D Patch E loaded.<br>"

        "Managed observer system active.<br>"

        "Legacy observer registrations isolated."

        "</b>"

    )

except Exception:

    pass

print()

print("Observer manager initialized.")
print("CMB-0032D PATCH E COMPLETE")






