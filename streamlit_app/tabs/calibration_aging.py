# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Hot-spot calibration + aging tab — Power transformers only.

The library's ``calibrate_hotspot_factor`` supports ``PowerTransformer`` and
``ThreeWindingTransformer``; we only expose the two-winding case here. Aging
math works for any hot-spot series, so the aging view runs on whatever
transformer the calibration produced.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from transformer_thermal_model.aging import days_aged
from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.hot_spot_calibration import calibrate_hotspot_factor
from transformer_thermal_model.model import Model
from transformer_thermal_model.transformer import PaperInsulationType

from streamlit_app import forms, plots
from streamlit_app.presets import TRANSFORMER_PRESETS, build_two_winding_transformer

_KEY = "calibration"


def render() -> None:
    """Render the calibration + aging tab."""
    st.subheader("Hot-spot calibration & insulation aging")
    st.caption(
        "Calibrate the hot-spot factor so a given transformer stays below a target hot-spot limit under "
        "nominal load, then run a simulation with the calibrated transformer and inspect insulation aging."
    )

    power_presets = {
        label: preset
        for label, preset in TRANSFORMER_PRESETS.items()
        if not preset.is_distribution
    }
    preset_label = st.selectbox(
        "Preset (power transformers)",
        options=list(power_presets),
        key=f"{_KEY}.preset",
    )
    preset = power_presets[preset_label]

    # Scope preset-dependent widget keys with the preset label — see the note
    # in ``basic.py``; Streamlit ignores ``value=``/``index=`` for widgets with
    # pre-existing session state, so stable keys would freeze the first preset.
    spec_scope = f"{_KEY}.{preset_label}"

    cooling_type = st.radio(
        "Cooling type",
        options=[CoolerType.ONAN, CoolerType.ONAF],
        index=[CoolerType.ONAN, CoolerType.ONAF].index(preset.default_cooling_type),
        format_func=lambda c: c.value,
        horizontal=True,
        key=f"{spec_scope}.cooling_type",
    )

    specs = forms.render_spec_form(preset.specs, key_prefix=spec_scope)

    st.markdown("**Calibration parameters**")
    cols = st.columns(4)
    with cols[0]:
        hot_spot_limit = st.number_input(
            "Hot-spot limit [°C]", value=98.0, step=1.0, min_value=0.0, key=f"{_KEY}.hot_spot_limit",
        )
    with cols[1]:
        ambient_temp = st.number_input(
            "Ambient temperature [°C]", value=20.0, step=1.0, key=f"{_KEY}.ambient_temp",
        )
    with cols[2]:
        hot_spot_min = st.number_input(
            "Hot-spot factor min", value=1.0, step=0.05, min_value=0.1, key=f"{_KEY}.hsf_min",
        )
    with cols[3]:
        hot_spot_max = st.number_input(
            "Hot-spot factor max", value=1.3, step=0.05, min_value=0.1, key=f"{_KEY}.hsf_max",
        )

    insulation_label = st.selectbox(
        "Paper insulation",
        options=[PaperInsulationType.NORMAL, PaperInsulationType.THERMAL_UPGRADED],
        format_func=lambda p: p.value.replace("_", " ").title(),
        key=f"{_KEY}.insulation",
    )

    profile = forms.render_profile_picker(specs, key_prefix=_KEY)
    initial_state = forms.render_initial_state_picker(key_prefix=_KEY)

    if st.button("Calibrate & run", type="primary", key=f"{_KEY}.run"):
        try:
            uncalibrated = build_two_winding_transformer(preset, specs, cooling_type=cooling_type)
            original_hsf = float(uncalibrated.specs.hot_spot_fac)

            calibrated = calibrate_hotspot_factor(
                uncalibrated_transformer=uncalibrated,
                hot_spot_limit=hot_spot_limit,
                ambient_temp=ambient_temp,
                hot_spot_factor_min=hot_spot_min,
                hot_spot_factor_max=hot_spot_max,
            )
            calibrated_hsf = float(calibrated.specs.hot_spot_fac)

            output = Model(
                temperature_profile=profile,
                transformer=calibrated,
                initial_condition=initial_state,
            ).run()
        except Exception as exc:  # noqa: BLE001
            st.error(f"{type(exc).__name__}: {exc}")
            return

        st.success("Calibration + simulation finished.")

        # Aging only makes sense for two-winding (Series) output here, which is what
        # build_two_winding_transformer produces. If the API ever returns a DataFrame
        # (e.g. if we add three-winding here later), fall back to the maximum column.
        hot_spot_series = (
            output.hot_spot_temp_profile
            if isinstance(output.hot_spot_temp_profile, pd.Series)
            else output.hot_spot_temp_profile.max(axis=1)
        )
        total_days_aged = days_aged(hot_spot_series, insulation_label)

        cols = st.columns(4)
        cols[0].metric(
            "Hot-spot factor",
            f"{calibrated_hsf:.3f}",
            delta=f"{calibrated_hsf - original_hsf:+.3f}",
            help=f"Original: {original_hsf:.3f}",
        )
        cols[1].metric("Max top-oil [°C]", f"{float(output.top_oil_temp_profile.max()):.1f}")
        cols[2].metric("Max hot-spot [°C]", f"{float(hot_spot_series.max()):.1f}")
        cols[3].metric("Days aged over profile", f"{total_days_aged:.3f}")

        st.plotly_chart(plots.plot_temperatures(output, profile), width="stretch", key=f"{_KEY}.temperature_plot")
        st.markdown("**Insulation aging rate**")
        st.plotly_chart(
            plots.plot_aging(hot_spot_series, insulation_label),
            width="stretch",
            key=f"{_KEY}.aging_plot",
        )
