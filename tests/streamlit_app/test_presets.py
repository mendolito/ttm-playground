# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Smoke tests for the Streamlit UI preset data.

These tests import preset data only — no Streamlit — and run every preset
transformer/profile pair through ``Model.run()``. Their purpose is to catch
library-side API drift: if the library renames a spec field, changes
``InputProfile.create``, or tightens validation, these tests fail loudly before
the UI does at runtime.
"""

import numpy as np
import pandas as pd
import pytest

from streamlit_app.presets import (
    PROFILE_PRESETS,
    THREE_WINDING_PRESETS,
    THREE_WINDING_PROFILE_PRESETS,
    TRANSFORMER_PRESETS,
    build_three_winding_transformer,
    build_two_winding_transformer,
)
from transformer_thermal_model.model import Model
from transformer_thermal_model.schemas import OutputProfile


@pytest.mark.integrationtest
@pytest.mark.parametrize("preset_label", list(TRANSFORMER_PRESETS))
@pytest.mark.parametrize("profile_label", list(PROFILE_PRESETS))
def test_two_winding_preset_combinations_run(preset_label: str, profile_label: str) -> None:
    """Every (transformer, profile) preset pair must produce a finite OutputProfile."""
    preset = TRANSFORMER_PRESETS[preset_label]
    profile = PROFILE_PRESETS[profile_label](preset.specs.nom_load_sec_side)
    transformer = build_two_winding_transformer(preset, preset.specs)

    output = Model(temperature_profile=profile, transformer=transformer).run()

    _assert_output_is_reasonable(output, profile.ambient_temperature_profile)


@pytest.mark.integrationtest
@pytest.mark.parametrize("preset_label", list(THREE_WINDING_PRESETS))
@pytest.mark.parametrize("profile_label", list(THREE_WINDING_PROFILE_PRESETS))
def test_three_winding_preset_combinations_run(preset_label: str, profile_label: str) -> None:
    """Every three-winding (transformer, profile) preset pair must run successfully."""
    preset = THREE_WINDING_PRESETS[preset_label]
    profile = THREE_WINDING_PROFILE_PRESETS[profile_label](
        preset.specs.lv_winding.nom_load,
        preset.specs.mv_winding.nom_load,
        preset.specs.hv_winding.nom_load,
    )
    transformer = build_three_winding_transformer(preset, preset.specs)

    output = Model(temperature_profile=profile, transformer=transformer).run()

    _assert_output_is_reasonable(output, profile.ambient_temperature_profile)


def _assert_output_is_reasonable(output: OutputProfile, ambient: np.ndarray) -> None:
    assert len(output.top_oil_temp_profile) == len(ambient)
    assert np.isfinite(output.top_oil_temp_profile.to_numpy()).all()

    hot_spot = output.hot_spot_temp_profile
    if isinstance(hot_spot, pd.DataFrame):
        assert np.isfinite(hot_spot.to_numpy()).all()
    else:
        assert np.isfinite(hot_spot.to_numpy()).all()
