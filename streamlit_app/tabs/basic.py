# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Basic simulation tab — Power or Distribution transformer, no switch or calibration."""

from __future__ import annotations

import streamlit as st

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model import Model

from streamlit_app import forms, plots
from streamlit_app.presets import TRANSFORMER_PRESETS, build_two_winding_transformer

_KEY = "basic"


def render() -> None:
    """Render the basic simulation tab."""
    st.subheader("Basic simulation")
    st.caption(
        "Configure a power or distribution transformer, pick a built-in load profile, and run the thermal model."
    )

    family = st.radio(
        "Transformer family",
        options=["Power", "Distribution"],
        horizontal=True,
        key=f"{_KEY}.family",
    )
    is_distribution = family == "Distribution"

    matching_presets = {
        label: preset
        for label, preset in TRANSFORMER_PRESETS.items()
        if preset.is_distribution == is_distribution
    }
    preset_label = st.selectbox(
        "Preset",
        options=list(matching_presets),
        key=f"{_KEY}.preset",
    )
    preset = matching_presets[preset_label]

    cooling_type: CoolerType | None = None
    if not is_distribution:
        cooling_type = st.radio(
            "Cooling type",
            options=[CoolerType.ONAN, CoolerType.ONAF],
            index=[CoolerType.ONAN, CoolerType.ONAF].index(preset.default_cooling_type),
            format_func=lambda c: c.value,
            horizontal=True,
            key=f"{_KEY}.cooling_type",
        )

    specs = forms.render_spec_form(preset.specs, key_prefix=_KEY)
    profile = forms.render_profile_picker(specs, key_prefix=_KEY)
    initial_state = forms.render_initial_state_picker(key_prefix=_KEY)

    if st.button("Run simulation", type="primary", key=f"{_KEY}.run"):
        try:
            transformer = build_two_winding_transformer(
                preset,
                specs,
                cooling_type=cooling_type,
            )
            output = Model(
                temperature_profile=profile,
                transformer=transformer,
                initial_condition=initial_state,
            ).run()
        except Exception as exc:  # noqa: BLE001
            st.error(f"{type(exc).__name__}: {exc}")
            return

        st.success("Simulation finished.")
        _render_metrics(output)
        st.plotly_chart(plots.plot_temperatures(output, profile), width="stretch", key=f"{_KEY}.result_plot")


def _render_metrics(output) -> None:  # noqa: ANN001 — OutputProfile, keep module lean
    cols = st.columns(3)
    max_top_oil = float(output.top_oil_temp_profile.max())
    hot_spot = output.hot_spot_temp_profile
    max_hot_spot = float(hot_spot.max() if hasattr(hot_spot, "max") else hot_spot.to_numpy().max())
    t_peak = output.top_oil_temp_profile.idxmax()
    cols[0].metric("Max top-oil [°C]", f"{max_top_oil:.1f}")
    cols[1].metric("Max hot-spot [°C]", f"{max_hot_spot:.1f}")
    cols[2].metric("Top-oil peak at", t_peak.strftime("%Y-%m-%d %H:%M"))
