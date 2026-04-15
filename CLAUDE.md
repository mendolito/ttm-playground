<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this package does

`transformer-thermal-model` implements the **IEC 60076-7** ("Loading Guide") thermal model for power, distribution, and three-winding transformers. Given transformer specifications plus a load profile and an ambient temperature profile, it computes top-oil and hot-spot temperature time series — the two outputs that drive transformer rating and insulation aging.

The top-level `transformer_thermal_model/__init__.py` is empty; users import from subpackages directly (see Architecture below).

## Common commands

Poetry manages dependencies; Python `>=3.11, <4.0` is required.

```bash
# Setup
poetry install --with dev           # dev dependencies (tests + linters)
poetry install --with docs          # additionally install mkdocs + matplotlib
pre-commit install                  # install git hooks (required)

# Run the full test suite (coverage + doctests are on by default via addopts)
poetry run pytest

# Run a single test / file / marker
poetry run pytest tests/model/test_model.py::test_<name>
poetry run pytest -m integrationtest
poetry run pytest -k "aging"

# Linters / formatters / types
poetry run ruff check --fix
poetry run ruff format
poetry run mypy .
pre-commit run -a                   # runs the same checks CI runs

# Documentation
poetry run mkdocs serve             # preview at http://127.0.0.1:8000
```

Note: `pytest` is configured with `--doctest-modules`, so examples inside docstrings are executed as tests. Keep docstring examples runnable.

## Architecture

The `transformer_thermal_model/` package is split into subpackages by concern. Typical user flow: build a `Transformer` from specs → wrap it in a `Model` together with an `InputProfile` → call `.run()` → get an `OutputProfile`.

- **`model/`** — `Model` class (`model/thermal_model.py`). The simulation driver; holds the differential-equation loop that produces top-oil and hot-spot temperatures.
- **`transformer/`** — Domain objects. `Transformer` (abstract base in `base.py`) plus concrete `PowerTransformer`, `DistributionTransformer`, `ThreeWindingTransformer`. Also `CoolingSwitchController` for dynamic ONAN/ONAF switching and the `TransformerType` / `PaperInsulationType` enums.
- **`cooler/`** — `CoolerType` enum (`ONAN` = natural cooling, `ONAF` = forced-air cooling).
- **`schemas/`** — Pydantic models that form the public data contracts:
  - `specifications/` — `UserTransformerSpecifications` (user inputs), `DefaultTransformerSpecifications` (IEC defaults per type), merged into `TransformerSpecifications`. Three-winding variants live here too.
  - `thermal_model/` — `InputProfile` / `ThreeWindingInputProfile` (load + ambient temp time series), `OutputProfile` (results), `InitialState` hierarchy (`ColdStart`, `InitialLoad`, `InitialTopOilTemp`), `CoolingSwitchSettings` / `ONANParameters`.
- **`hot_spot_calibration/`** — `calibrate_hotspot_factor()` adjusts the hot-spot factor to hit a target temperature limit.
- **`aging/`** — `days_aged()`, `aging_rate_profile()` compute insulation aging from a hot-spot temperature series (per IEC 60076-7 exponential aging model).
- **`toolbox/`** — Thin utilities, notably `create_temp_sim_profile_from_df()` for turning a pandas DataFrame into an `InputProfile`.
- **`components/`** — Helper types for component-level modeling (`BushingConfig`, `TransformerSide`, `VectorConfig`).

### Key relationships to keep in mind

- A `Transformer` is constructed from a `UserTransformerSpecifications` plus a `CoolerType`. Defaults from `DefaultTransformerSpecifications` are merged in automatically by transformer subclass.
- `Model.run()` returns an `OutputProfile` with `top_oil` and `hot_spot` series aligned to the `InputProfile` index.
- ONAN/ONAF switching is configured via `CoolingSwitchSettings` passed to the transformer; the `CoolingSwitchController` toggles cooling dynamically during simulation.
- `calibrate_hotspot_factor()` is a *pre-processing* step: it tunes the hot-spot factor on a transformer so that a subsequent `Model.run()` respects a target temperature limit.

### Tests

Tests live under `tests/`, mirroring the package layout (`tests/model/`, `tests/schemas/`). Shared fixtures in `tests/conftest.py`: `default_user_trafo_specs`, `onan_power_transformer`, `onaf_power_transformer`, `distribution_transformer`, `iec_load_profile`. Integration tests use `@pytest.mark.integrationtest`.

### Examples

Jupyter notebooks in `docs/examples/` are the canonical worked examples — notably `quickstart.ipynb`, `power_transformer_example.ipynb`, `three-winding-calculation.ipynb`, `hot-spot_calibration.ipynb`, and `example_ONAN_ONAF_switch.ipynb`. When changing public API, update the relevant notebook.

## Project conventions

These are non-obvious and enforced by CI — violating them will fail the build:

- **REUSE / SPDX headers.** Every source file (`.py`, `.md`, `.yaml`, etc.) needs an SPDX header. Python files use:

  ```python
  # SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
  #
  # SPDX-License-Identifier: MPL-2.0
  ```

  Markdown uses an equivalent HTML comment block (see the top of this file). When creating new files, copy the header style from a sibling file. The `reuse` pre-commit hook will block commits otherwise.
- **Conventional / Angular commit messages**, enforced by `conventional-pre-commit`. Allowed types: `build`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `style`, `test`. Breaking changes get `!` after the type and a `BREAKING:` paragraph in the body.
- **DCO sign-off required.** Every commit needs `Signed-off-by: Real Name <email>` — use `git commit -s`.
- **Branch naming** mirrors commit types with `/` instead of `:` — e.g. `feat/allow-xyz`, `fix/prevent-nan`, `feat!/breaking-change`.
- **Docstrings use Google style** (`pydocstyle` with `convention = "google"`), ruff line length is 120. Docstring rules `D100`, `D104`, `D203`, `D213` are intentionally disabled; otherwise pydocstyle is strict.
- **Strict typing.** `disallow_untyped_defs` and `disallow_incomplete_defs` are on for the package — every function in `transformer_thermal_model/*` needs full annotations.
- **Doctests run as part of pytest** via `--doctest-modules`. If you add a docstring example with `>>>`, it must execute cleanly.
- **PRs are squash-merged** onto `main` (trunk-based). Keep branches short-lived.
