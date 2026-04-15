<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Streamlit app — Norwegian UI localization

**Date:** 2026-04-15
**Status:** Design approved

## Goal

Localize the Streamlit playground (`streamlit_app/`) to Norwegian for the
surrounding UI text — navigation, buttons, section headers, help text —
while keeping technical parameter labels, plot labels, and library-side
text in English.

This is a UI-only change. The `transformer_thermal_model/` library
package is not touched.

## Approach

**In-place replacement.** Edit strings directly in the 10 `streamlit_app/`
files. No locale switcher, no messages module, no `gettext`. The app
becomes Norwegian; English is not preserved as an option.

Rationale: the user asked for Norwegian, not bilingual. A messages module
would add indirection for a payoff (language switching) that was not
requested. If bilingual support is added later, extracting strings from
the (then-Norwegian) code is no harder than extracting them now.

The test suite (`tests/streamlit_app/test_presets.py`) iterates preset
dict keys generically — renaming the keys does not break tests.

## Translation style

Per user choice: **pragmatic — translate surrounding UI text, keep
technical parameter labels in English.**

### Translate to Norwegian

- `app.py`: page title, caption, sidebar header + body + footer, tab
  labels.
- All tab subheaders and captions (`"Basic simulation"` →
  `"Grunnleggende simulering"`, etc.).
- All buttons (`"Run simulation"` → `"Kjør simulering"`) and status
  toasts (`"Simulation finished."` → `"Simulering fullført."`).
- Radio / selectbox / expander **titles** (`"Cooling type"`,
  `"Initial state"`, `"Switch trigger"`, `"Preset"`, `"Load profile"`,
  `"Paper insulation"`).
- Radio **options** that describe UI state (not technical quantities):
  `"Power" / "Distribution"`, `"Cold start" / "Initial load" /
  "Initial top-oil temperature"`, `"Temperature threshold" /
  "Fan schedule"`.
- Group headers rendered via `st.markdown("**…**")`: `"Losses"` →
  `"Tap"`, `"Windings"` → `"Viklinger"`, `"Low-voltage winding"` →
  `"Lavspenningsvikling"`, etc.
- Help text (`"Leave blank to use the library default."` →
  `"La stå tom for å bruke standardverdi fra biblioteket."`).
- Preset dropdown labels (`"Typical 400 MVA power (ONAF)"` →
  `"Typisk 400 MVA krafttransformator (ONAF)"`,
  `"IEC reference load (overloads, ~12 h)"` →
  `"IEC-referanselast (overlast, ~12 t)"`).

### Keep in English

- All **numeric input labels** — `Load loss [W]`,
  `Top-oil temperature rise [K]`, `Hot-spot factor [-]`, oil/winding
  time constants, model exponents, inter-winding loss labels, etc.
- **Metric labels** for simulation output (`Max top-oil [°C]`,
  `Max hot-spot [°C]`, `Top-oil peak at`, `Days aged over profile`,
  `Fan-on steps`).
- **Plot subplot titles, legend entries, axis labels, annotations**
  (`Top-oil`, `Ambient`, `Hot-spot`, `Temperature [°C]`,
  `Aging rate [day / day]`, `Nominal (1 day/day)`,
  `Hot-spot · Low Voltage Side`).
- **ONAN / ONAF / IEC 60076-7** references everywhere.
- Docstrings, code, comments, SPDX headers, variable and function
  names, test assertions.

## Files affected

- `streamlit_app/app.py` — page title/caption, sidebar, tab labels.
- `streamlit_app/forms.py` — most of the UI strings live here (group
  headers, expander titles, radio options, help text). Field labels in
  `_FieldSpec` entries stay English.
- `streamlit_app/presets.py` — preset dictionary keys only.
- `streamlit_app/plots.py` — **unchanged** (all plot text stays English).
- `streamlit_app/tabs/basic.py` — subheader, caption, radio titles,
  button, toast, radio option labels.
- `streamlit_app/tabs/three_winding.py` — same.
- `streamlit_app/tabs/cooling_switch.py` — same, plus `"No ONAF power
  transformer presets available."` info message.
- `streamlit_app/tabs/calibration_aging.py` — same, plus `"Calibration
  parameters"` header.
- `streamlit_app/__init__.py`, `streamlit_app/tabs/__init__.py` —
  unchanged (no user-facing text).

## Risks / non-goals

- **Library error messages surfacing in `st.error(...)`** stay English.
  The tabs catch exceptions from `Model.run()` and render them verbatim
  (`f"{type(exc).__name__}: {exc}"`); translating those would require
  editing `transformer_thermal_model/`, which is out of scope.
- **Plot data** comes from library schemas — three-winding column names
  (`low_voltage_side`) are formatted into legend entries like
  `Hot-spot · Low Voltage Side`; these stay English intentionally to
  avoid a translation mapping.
- No tests are renamed, added, or removed. Existing preset smoke tests
  continue to pass because they iterate preset keys agnostically.
