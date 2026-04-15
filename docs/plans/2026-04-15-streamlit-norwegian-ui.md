<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Streamlit Norwegian UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Localize the Streamlit playground (`streamlit_app/`) to Norwegian for surrounding UI text (navigation, buttons, section headers, help), while keeping technical parameter labels, plot labels, docstrings, and library-side text in English.

**Architecture:** In-place string replacement across the 10 `streamlit_app/` files. No locale switcher, no `gettext`, no messages module. The `transformer_thermal_model/` library package is not modified. Design: `docs/plans/2026-04-15-streamlit-norwegian-ui-design.md`.

**Tech Stack:** Streamlit + Plotly + Pydantic schemas from the library. Poetry-managed project, pytest (+ doctests), ruff, mypy. Commits must be Conventional (`feat:`) with DCO sign-off (`git commit -s`); branch name `feat/streamlit-norwegian-ui`.

---

## Conventions for every task

- **Edits:** use the `Edit` tool with exact `old_string` / `new_string`. Preserve SPDX headers, indentation, and surrounding whitespace.
- **Do NOT touch:** docstrings, comments, variable names, function names, SPDX headers, or anything inside `transformer_thermal_model/`.
- **Do NOT touch:** `streamlit_app/plots.py` (entire file — plot titles/legends/axes stay English per design).
- **Verification per task:** `poetry run ruff check streamlit_app/` and `poetry run pytest tests/streamlit_app/ -v` must pass. Mypy runs in the final task.
- **Commits:** one commit per task using `git commit -s`. Conventional commit type is `feat`. Example message:
  ```
  feat(streamlit): localize app frame to Norwegian

  Signed-off-by: Erik Melvær <erik@ren.no>
  ```

---

## Task 1: Branch setup and baseline

**Files:** none modified.

**Step 1: Confirm clean working tree**

```bash
git status
```
Expected: `working tree clean` on `main`.

**Step 2: Create feature branch**

```bash
git checkout -b feat/streamlit-norwegian-ui
```
Expected: `Switched to a new branch 'feat/streamlit-norwegian-ui'`.

**Step 3: Baseline — tests pass before changes**

```bash
poetry run pytest tests/streamlit_app/ -v
```
Expected: all tests pass. Record the count (e.g. "12 passed") so we can confirm the same count at the end.

**Step 4: Baseline — ruff clean before changes**

```bash
poetry run ruff check streamlit_app/
```
Expected: `All checks passed!` (or whatever clean output the repo produces).

No commit for this task.

---

## Task 2: Localize `streamlit_app/app.py`

**Files:**
- Modify: `streamlit_app/app.py`

**Step 1: Apply the string replacements**

Use `Edit` tool for each. All replacements are exact.

| Old | New |
|---|---|
| `page_title="Transformer thermal model",` | `page_title="Termisk transformatormodell",` |
| `st.title("Transformer thermal model")` | `st.title("Termisk transformatormodell")` |
| `"Interactive playground for the "` | `"Interaktiv lekeplass for biblioteket "` |
| `"[`transformer-thermal-model`](https://github.com/alliander-opensource/transformer-thermal-model) "` | `"[`transformer-thermal-model`](https://github.com/alliander-opensource/transformer-thermal-model) "` *(unchanged — link markup)* |
| `"library — IEC 60076-7 thermal simulation for power, distribution, and three-winding transformers."` | `"— IEC 60076-7 termisk simulering for kraft-, distribusjons- og tre-vikling-transformatorer."` |
| `st.header("About")` | `st.header("Om")` |
| `"This app wraps the four headline workflows of the library:\n\n"` | `"Denne appen samler de fire hovedarbeidsflytene i biblioteket:\n\n"` |
| `"- **Basic simulation** — top-oil and hot-spot curves for a power or distribution transformer.\n"` | `"- **Grunnleggende simulering** — topp-olje- og hot-spot-kurver for en kraft- eller distribusjonstransformator.\n"` |
| `"- **Three-winding** — per-winding hot-spot output for three-winding transformers.\n"` | `"- **Tre-vikling** — hot-spot-utdata per vikling for tre-vikling-transformatorer.\n"` |
| `"- **Cooling switch** — dynamic ONAN/ONAF switching driven by temperature or a fan schedule.\n"` | `"- **Kjølebryter** — dynamisk ONAN/ONAF-omkobling styrt av temperatur eller en vifteplan.\n"` |
| `"- **Calibration & aging** — calibrate the hot-spot factor to a target limit and "` | `"- **Kalibrering & aldring** — kalibrer hot-spot-faktoren mot en målgrense og "` |
| `"estimate insulation aging.\n\n"` | `"estimer isolasjonsaldring.\n\n"` |
| `"Load and ambient profiles are built-in presets; each preset adapts to the transformer you pick."` | `"Last- og omgivelsesprofiler er innebygde forhåndsvalg; hvert forhåndsvalg tilpasser seg transformatoren du velger."` |
| `st.caption("Built with Streamlit + Plotly. Source: `streamlit_app/`.")` | `st.caption("Bygget med Streamlit + Plotly. Kildekode: `streamlit_app/`.")` |
| `"Basic simulation",` *(inside `tab_labels`)* | `"Grunnleggende simulering",` |
| `"Three-winding",` *(inside `tab_labels`)* | `"Tre-vikling",` |
| `"Cooling switch",` *(inside `tab_labels`)* | `"Kjølebryter",` |
| `"Calibration & aging",` *(inside `tab_labels`)* | `"Kalibrering & aldring",` |

**Step 2: Verify**

```bash
poetry run ruff check streamlit_app/app.py
poetry run pytest tests/streamlit_app/ -v
```
Expected: both pass.

**Step 3: Sanity import check**

```bash
poetry run python -c "import streamlit_app.app"
```
This may fail because `app.py` calls `main()` at module import (line 77). If it does, accept the traceback and **only fail this step if the error is a syntax or name error, not a Streamlit runtime error**. The Streamlit-related traceback is expected outside `streamlit run`.

**Step 4: Commit**

```bash
git add streamlit_app/app.py
git commit -s -m "feat(streamlit): localize app frame to Norwegian"
```

---

## Task 3: Localize preset labels in `streamlit_app/presets.py`

**Files:**
- Modify: `streamlit_app/presets.py`

Only the **dictionary keys** change. Preset values, docstrings, and comments stay English.

**Step 1: Apply the string replacements**

| Old | New |
|---|---|
| `"Typical 400 MVA power (ONAF)": TransformerPreset(` | `"Typisk 400 MVA krafttransformator (ONAF)": TransformerPreset(` |
| `"Typical 100 MVA power (ONAN)": TransformerPreset(` | `"Typisk 100 MVA krafttransformator (ONAN)": TransformerPreset(` |
| `"Typical 1 MVA distribution (ONAN)": TransformerPreset(` | `"Typisk 1 MVA distribusjonstransformator (ONAN)": TransformerPreset(` |
| `"Typical three-winding (ONAF)": ThreeWindingTransformerPreset(` | `"Typisk tre-vikling-transformator (ONAF)": ThreeWindingTransformerPreset(` |
| `"IEC reference load (overloads, ~12 h)": _iec_reference_profile,` | `"IEC-referanselast (overlast, ~12 t)": _iec_reference_profile,` |
| `"Constant nominal load (1 week)": _constant_nominal_profile,` | `"Konstant nominell last (1 uke)": _constant_nominal_profile,` |
| `"Step load 50 % → 130 % (24 h)": _step_load_profile,` | `"Trinnlast 50 % → 130 % (24 t)": _step_load_profile,` |
| `"Diurnal sinusoid (48 h)": _diurnal_sinusoid_profile,` | `"Døgnsinusoid (48 t)": _diurnal_sinusoid_profile,` |
| `"Diurnal sinusoid (48 h)": _three_winding_diurnal_profile,` | `"Døgnsinusoid (48 t)": _three_winding_diurnal_profile,` |
| `"Constant nominal load (1 week)": _three_winding_constant_profile,` | `"Konstant nominell last (1 uke)": _three_winding_constant_profile,` |

**Step 2: Verify tests still iterate all presets correctly**

```bash
poetry run pytest tests/streamlit_app/ -v
```
Expected: same pass count as baseline. The tests use `@pytest.mark.parametrize("preset_label", list(TRANSFORMER_PRESETS))` which reads keys at collection time — test *names* will change (e.g. `test_...[Typisk 400 MVA ...]`) but they must all pass.

**Step 3: Ruff**

```bash
poetry run ruff check streamlit_app/presets.py
```
Expected: pass.

**Step 4: Commit**

```bash
git add streamlit_app/presets.py
git commit -s -m "feat(streamlit): translate preset labels to Norwegian"
```

---

## Task 4: Localize `streamlit_app/forms.py`

**Files:**
- Modify: `streamlit_app/forms.py`

This is the largest task — `forms.py` holds most UI strings. **Do NOT touch** the `_FieldSpec(...)` tuples (`_LOSS_FIELDS`, `_THERMAL_FIELDS`, `_MODEL_FIELDS`, `_CORRECTION_FIELDS`) — those labels (`"Load loss [W]"` etc.) stay English per design. Likewise keep the inline `st.number_input` labels like `"Nominal load [A]"`, `"HV → LV"`, `"No-load loss [W]"`, `"Ambient surcharge [K]"`, `"Top-oil temp rise [K]"`, `"Winding-oil gradient [K]"`, `"Winding time constant [min]"`, `"Hot-spot factor [-]"`, `"Fan activation temperature [°C]"`, `"Fan deactivation temperature [°C]"`, `"Top-oil rise [K]"`, `"Load loss [W]"`, `"Oil time constant [min]"`, `"Winding time constant [min]"`, `"Initial load [A]"`, `"Initial top-oil temperature [°C]"` — all English.

**Step 1: Help-text replacements**

`"Leave blank to use the library default."` appears in multiple places. Use `Edit` with `replace_all=True`:

| Old | New |
|---|---|
| `"Leave blank to use the library default."` | `"La stå tom for å bruke standardverdi fra biblioteket."` |

**Step 2: Section-header replacements (passed as `group_label` or `st.markdown("**…**")`)**

Find each occurrence precisely so they're unique. These are argument positions in `_collect_field_values(...)` calls inside `render_spec_form`:

| Old | New |
|---|---|
| `losses = _collect_field_values(preset, _LOSS_FIELDS, key_prefix, "Losses")` | `losses = _collect_field_values(preset, _LOSS_FIELDS, key_prefix, "Tap")` |
| `thermals = _collect_field_values(preset, _THERMAL_FIELDS, key_prefix, "Thermal constants")` | `thermals = _collect_field_values(preset, _THERMAL_FIELDS, key_prefix, "Termiske konstanter")` |
| `models = _collect_field_values(preset, _MODEL_FIELDS, key_prefix, "Model constants")` | `models = _collect_field_values(preset, _MODEL_FIELDS, key_prefix, "Modellkonstanter")` |
| `corrections = _collect_field_values(preset, _CORRECTION_FIELDS, key_prefix, "Corrections")` | `corrections = _collect_field_values(preset, _CORRECTION_FIELDS, key_prefix, "Korreksjoner")` |

And in the three-winding form (`render_three_winding_spec_form` + `_render_winding_form`):

| Old | New |
|---|---|
| `with st.expander("Override specifications", expanded=False):` | `with st.expander("Overstyr spesifikasjoner", expanded=False):` |

Note: `"Override specifications"` appears twice in the file (once in `render_spec_form`, once in `render_three_winding_spec_form`). Use `replace_all=True` since the translation is the same.

| Old | New |
|---|---|
| `st.markdown("**Windings**")` | `st.markdown("**Viklinger**")` |
| `lv = _render_winding_form(preset.lv_winding, f"{key_prefix}.lv", "Low-voltage winding")` | `lv = _render_winding_form(preset.lv_winding, f"{key_prefix}.lv", "Lavspenningsvikling")` |
| `mv = _render_winding_form(preset.mv_winding, f"{key_prefix}.mv", "Medium-voltage winding")` | `mv = _render_winding_form(preset.mv_winding, f"{key_prefix}.mv", "Mellomspenningsvikling")` |
| `hv = _render_winding_form(preset.hv_winding, f"{key_prefix}.hv", "High-voltage winding")` | `hv = _render_winding_form(preset.hv_winding, f"{key_prefix}.hv", "Høyspenningsvikling")` |
| `st.markdown("**Inter-winding load losses [W]**")` | `st.markdown("**Tap mellom viklinger [W]**")` |
| `st.markdown("**Common**")` | `st.markdown("**Felles**")` |

**Step 3: Profile-picker captions and selectbox titles**

| Old | New |
|---|---|
| `st.caption(f"{len(profile)} samples · step = {_describe_time_step(profile.time_step)}")` | `st.caption(f"{len(profile)} målinger · tidssteg = {_describe_time_step(profile.time_step)}")` |

Note: this line appears twice (once in `render_profile_picker`, once in `render_three_winding_profile_picker`). Use `replace_all=True`.

| Old | New |
|---|---|
| `label = st.selectbox(\n        "Load profile",` | `label = st.selectbox(\n        "Lastprofil",` |

Note: `"Load profile"` appears twice. Use `replace_all=True` on the bare string `"Load profile",` — but verify uniqueness first with Grep. If ambiguous with some other occurrence, use larger context anchors.

Also:
| Old | New |
|---|---|
| `return "unknown"` | `return "ukjent"` |

**Step 4: Initial state picker**

| Old | New |
|---|---|
| `mode = st.radio(\n        "Initial state",\n        options=["Cold start", "Initial load", "Initial top-oil temperature"],` | `mode = st.radio(\n        "Starttilstand",\n        options=["Kaldstart", "Startlast", "Start topp-oljetemperatur"],` |
| `if mode == "Cold start":` | `if mode == "Kaldstart":` |
| `if mode == "Initial load":` | `if mode == "Startlast":` |

**⚠ Crucial:** the three radio *options* are translated (because they are UI state labels per design), but the `st.number_input` field labels on the following lines (`"Initial load [A]"`, `"Initial top-oil temperature [°C]"`) **stay English** because they carry units and are technical parameter labels.

**Step 5: Cooling-switch form**

| Old | New |
|---|---|
| `st.markdown("**ONAN/ONAF switch**")` | `st.markdown("**ONAN/ONAF-bryter**")` |
| `mode = st.radio(\n        "Switch trigger",\n        options=["Temperature threshold", "Fan schedule"],` | `mode = st.radio(\n        "Utløser for omkobling",\n        options=["Temperaturgrense", "Vifteplan"],` |
| `if mode == "Temperature threshold":` | `if mode == "Temperaturgrense":` |
| `help="Must be below the activation temperature.",` | `help="Må være lavere enn aktiveringstemperaturen.",` |
| `"Fan-on window (as % of simulation)",` | `"Vifte-på-vindu (i % av simuleringen)",` |
| `with st.expander("ONAN-mode parameters (when fans are off)", expanded=False):` | `with st.expander("ONAN-modus-parametere (når viftene er av)", expanded=False):` |
| `help="Often lower than the ONAF nominal — fans enable a higher rating.",` | `help="Ofte lavere enn ONAF-merkeverdien — vifter gir høyere kapasitet.",` |

**Step 6: Verify**

```bash
poetry run ruff check streamlit_app/forms.py
poetry run pytest tests/streamlit_app/ -v
```
Expected: both pass.

**Step 7: Commit**

```bash
git add streamlit_app/forms.py
git commit -s -m "feat(streamlit): localize shared form helpers to Norwegian"
```

---

## Task 5: Localize `streamlit_app/tabs/basic.py`

**Files:**
- Modify: `streamlit_app/tabs/basic.py`

**Step 1: Replacements**

| Old | New |
|---|---|
| `st.subheader("Basic simulation")` | `st.subheader("Grunnleggende simulering")` |
| `"Configure a power or distribution transformer, pick a built-in load profile, and run the thermal model."` | `"Konfigurer en kraft- eller distribusjonstransformator, velg en innebygd lastprofil og kjør den termiske modellen."` |
| `family = st.radio(\n        "Transformer family",\n        options=["Power", "Distribution"],` | `family = st.radio(\n        "Transformatortype",\n        options=["Kraft", "Distribusjon"],` |
| `is_distribution = family == "Distribution"` | `is_distribution = family == "Distribusjon"` |
| `preset_label = st.selectbox(\n        "Preset",` | `preset_label = st.selectbox(\n        "Forhåndsvalg",` |
| `cooling_type = st.radio(\n            "Cooling type",` | `cooling_type = st.radio(\n            "Kjøletype",` |
| `if st.button("Run simulation", type="primary", key=f"{_KEY}.run"):` | `if st.button("Kjør simulering", type="primary", key=f"{_KEY}.run"):` |
| `st.success("Simulation finished.")` | `st.success("Simulering fullført.")` |

**Do NOT change:** metric labels `"Max top-oil [°C]"`, `"Max hot-spot [°C]"`, `"Top-oil peak at"` — they are output-quantity labels, stay English per design.

**Step 2: Verify**

```bash
poetry run ruff check streamlit_app/tabs/basic.py
poetry run pytest tests/streamlit_app/ -v
```

**Step 3: Commit**

```bash
git add streamlit_app/tabs/basic.py
git commit -s -m "feat(streamlit): localize basic simulation tab to Norwegian"
```

---

## Task 6: Localize `streamlit_app/tabs/three_winding.py`

**Files:**
- Modify: `streamlit_app/tabs/three_winding.py`

**Step 1: Replacements**

| Old | New |
|---|---|
| `st.subheader("Three-winding simulation")` | `st.subheader("Tre-vikling-simulering")` |
| `st.caption("Three-winding transformers with per-winding hot-spot output.")` | `st.caption("Tre-vikling-transformatorer med hot-spot-utdata per vikling.")` |
| `preset_label = st.selectbox(\n        "Preset",` | `preset_label = st.selectbox(\n        "Forhåndsvalg",` |
| `cooling_type = st.radio(\n        "Cooling type",` | `cooling_type = st.radio(\n        "Kjøletype",` |
| `if st.button("Run simulation", type="primary", key=f"{_KEY}.run"):` | `if st.button("Kjør simulering", type="primary", key=f"{_KEY}.run"):` |
| `st.success("Simulation finished.")` | `st.success("Simulering fullført.")` |

**Do NOT change:** `_render_per_winding_metrics` — metric labels like `"Max top-oil [°C]"` and `f"Max hot-spot · {winding.split('_')[0].upper()} [°C]"` stay English (output-quantity labels).

**Step 2: Verify**

```bash
poetry run ruff check streamlit_app/tabs/three_winding.py
poetry run pytest tests/streamlit_app/ -v
```

**Step 3: Commit**

```bash
git add streamlit_app/tabs/three_winding.py
git commit -s -m "feat(streamlit): localize three-winding tab to Norwegian"
```

---

## Task 7: Localize `streamlit_app/tabs/cooling_switch.py`

**Files:**
- Modify: `streamlit_app/tabs/cooling_switch.py`

**Step 1: Replacements**

| Old | New |
|---|---|
| `st.subheader("ONAN/ONAF cooling switch")` | `st.subheader("ONAN/ONAF-kjølebryter")` |
| `"Simulate a power transformer that dynamically switches between ONAN and ONAF cooling modes — either driven "\n        "by a temperature threshold or by a fan schedule."` | `"Simuler en krafttransformator som dynamisk veksler mellom ONAN- og ONAF-kjøling — enten styrt "\n        "av en temperaturgrense eller en vifteplan."` |
| `st.info("No ONAF power transformer presets available.")` | `st.info("Ingen ONAF-krafttransformator-forhåndsvalg tilgjengelig.")` |
| `"Preset (ONAF power transformers)",` | `"Forhåndsvalg (ONAF-krafttransformatorer)",` |
| `if st.button("Run simulation", type="primary", key=f"{_KEY}.run"):` | `if st.button("Kjør simulering", type="primary", key=f"{_KEY}.run"):` |
| `st.success("Simulation finished.")` | `st.success("Simulering fullført.")` |

**Do NOT change:** metric labels `"Max top-oil [°C]"`, `"Max hot-spot [°C]"`, `"Fan-on steps"`. String `"n/a"` also stays (technical fallback).

**Step 2: Verify**

```bash
poetry run ruff check streamlit_app/tabs/cooling_switch.py
poetry run pytest tests/streamlit_app/ -v
```

**Step 3: Commit**

```bash
git add streamlit_app/tabs/cooling_switch.py
git commit -s -m "feat(streamlit): localize cooling switch tab to Norwegian"
```

---

## Task 8: Localize `streamlit_app/tabs/calibration_aging.py`

**Files:**
- Modify: `streamlit_app/tabs/calibration_aging.py`

**Step 1: Replacements**

| Old | New |
|---|---|
| `st.subheader("Hot-spot calibration & insulation aging")` | `st.subheader("Hot-spot-kalibrering & isolasjonsaldring")` |
| `"Calibrate the hot-spot factor so a given transformer stays below a target hot-spot limit under "\n        "nominal load, then run a simulation with the calibrated transformer and inspect insulation aging."` | `"Kalibrer hot-spot-faktoren slik at en gitt transformator holder seg under en målsatt hot-spot-grense ved "\n        "nominell last, kjør deretter en simulering med den kalibrerte transformatoren og inspiser isolasjonsaldring."` |
| `"Preset (power transformers)",` | `"Forhåndsvalg (krafttransformatorer)",` |
| `cooling_type = st.radio(\n        "Cooling type",` | `cooling_type = st.radio(\n        "Kjøletype",` |
| `st.markdown("**Calibration parameters**")` | `st.markdown("**Kalibreringsparametere**")` |
| `insulation_label = st.selectbox(\n        "Paper insulation",` | `insulation_label = st.selectbox(\n        "Papirisolasjon",` |
| `if st.button("Calibrate & run", type="primary", key=f"{_KEY}.run"):` | `if st.button("Kalibrer & kjør", type="primary", key=f"{_KEY}.run"):` |
| `st.success("Calibration + simulation finished.")` | `st.success("Kalibrering + simulering fullført.")` |
| `st.markdown("**Insulation aging rate**")` | `st.markdown("**Isolasjonsaldringstakt**")` |

**Do NOT change:** numeric-input labels (`"Hot-spot limit [°C]"`, `"Ambient temperature [°C]"`, `"Hot-spot factor min"`, `"Hot-spot factor max"`) — technical parameters. Metric labels (`"Hot-spot factor"`, `"Max top-oil [°C]"`, `"Max hot-spot [°C]"`, `"Days aged over profile"`) also stay English. Help text `f"Original: {original_hsf:.3f}"` stays English (it's an output-quantity annotation).

**Step 2: Verify**

```bash
poetry run ruff check streamlit_app/tabs/calibration_aging.py
poetry run pytest tests/streamlit_app/ -v
```

**Step 3: Commit**

```bash
git add streamlit_app/tabs/calibration_aging.py
git commit -s -m "feat(streamlit): localize calibration & aging tab to Norwegian"
```

---

## Task 9: Final verification

**Files:** none modified.

**Step 1: Lint the whole streamlit_app**

```bash
poetry run ruff check streamlit_app/
poetry run ruff format --check streamlit_app/
```
Expected: both pass.

**Step 2: Type-check**

```bash
poetry run mypy streamlit_app/
```
Expected: clean (or the same pre-existing state as baseline; if there were pre-existing `mypy` issues on `main`, don't fix them here — out of scope).

**Step 3: Full test suite**

```bash
poetry run pytest
```
Expected: all tests pass with the same count as `main`, modulo parametrize-name changes from renamed preset keys. Library tests and doctests must not be affected.

**Step 4: Confirm no library files were touched**

```bash
git diff --name-only main...HEAD
```
Expected output: **only** files under `streamlit_app/` and `docs/plans/`. If anything under `transformer_thermal_model/` or `tests/` appears, stop and investigate.

**Step 5: Confirm plots.py is untouched**

```bash
git diff --name-only main...HEAD -- streamlit_app/plots.py
```
Expected: empty output.

**Step 6: Manual smoke test (optional but recommended)**

```bash
poetry run streamlit run streamlit_app/app.py
```
Check in browser:
- Title reads **"Termisk transformatormodell"**.
- Four tabs read **"Grunnleggende simulering"**, **"Tre-vikling"**, **"Kjølebryter"**, **"Kalibrering & aldring"**.
- In each tab: section headers are Norwegian, input labels under *Overstyr spesifikasjoner* are English, plot titles/legends English.
- Click *Kjør simulering* in each tab and confirm a toast reading **"Simulering fullført."**.

If anything looks wrong, capture the bad text and file a follow-up task — do not patch on this branch without an explicit ask.

No commit for this task.

---

## Success criteria

- All tests pass (`poetry run pytest`), same count as baseline.
- `poetry run ruff check streamlit_app/` and `poetry run ruff format --check streamlit_app/` pass.
- `poetry run mypy streamlit_app/` passes (or matches pre-existing baseline).
- Git diff against `main` touches only `streamlit_app/*.py`, `streamlit_app/tabs/*.py`, and `docs/plans/*.md` — nothing else.
- `streamlit_app/plots.py`, all docstrings, all comments, and the entire `transformer_thermal_model/` library are untouched.
- Manual smoke test in `streamlit run` shows Norwegian UI chrome and English technical labels.

## Execution notes

- The skill recommends a git worktree. For this narrowly-scoped, mechanical change the user is reviewing interactively — worktree is optional. If you want isolation, `git worktree add ../ttm-norwegian feat/streamlit-norwegian-ui` before Task 1.
- Tests run fast (< 20 s for `tests/streamlit_app/`). Running them per task catches preset-key typos early.
- If a string replacement fails because `old_string` isn't unique, add surrounding context lines to disambiguate — don't blindly use `replace_all` unless the replacement genuinely applies everywhere.
