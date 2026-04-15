# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""ONAN/ONAF cooling switch tab — Power transformers only."""

from __future__ import annotations

import streamlit as st

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model import Model

from streamlit_app import forms, plots
from streamlit_app.presets import TRANSFORMER_PRESETS, build_two_winding_transformer

_KEY = "coolingswitch"


def render() -> None:
    """Render the cooling-switch simulation tab."""
    st.subheader("ONAN/ONAF cooling switch")
    st.caption(
        "Simulate a power transformer that dynamically switches between ONAN and ONAF cooling modes — either driven "
        "by a temperature threshold or by a fan schedule."
    )

    onaf_presets = {
        label: preset
        for label, preset in TRANSFORMER_PRESETS.items()
        if not preset.is_distribution and preset.default_cooling_type == CoolerType.ONAF
    }
    if not onaf_presets:
        st.info("No ONAF power transformer presets available.")
        return

    preset_label = st.selectbox(
        "Preset (ONAF power transformers)",
        options=list(onaf_presets),
        key=f"{_KEY}.preset",
    )
    preset = onaf_presets[preset_label]

    # Scope preset-dependent widget keys with the preset label — see the note
    # in ``basic.py``; Streamlit ignores ``value=``/``index=`` for widgets with
    # pre-existing session state, so stable keys would freeze the first preset.
    spec_scope = f"{_KEY}.{preset_label}"

    specs = forms.render_spec_form(preset.specs, key_prefix=spec_scope)
    profile = forms.render_profile_picker(specs, key_prefix=_KEY)

    cooling_switch_settings, fan_on_overlay = forms.render_cooling_switch_form(
        onaf_specs=specs,
        profile_length=len(profile),
        key_prefix=_KEY,
        onan_key_prefix=spec_scope,
    )

    initial_state = forms.render_initial_state_picker(key_prefix=_KEY)

    if st.button("Run simulation", type="primary", key=f"{_KEY}.run"):
        try:
            transformer = build_two_winding_transformer(
                preset,
                specs,
                cooling_type=CoolerType.ONAF,
                cooling_switch_settings=cooling_switch_settings,
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
        cols = st.columns(3)
        cols[0].metric("Max top-oil [°C]", f"{float(output.top_oil_temp_profile.max()):.1f}")
        cols[1].metric("Max hot-spot [°C]", f"{float(output.hot_spot_temp_profile.max()):.1f}")
        cols[2].metric(
            "Fan-on steps",
            f"{int(fan_on_overlay.sum())} / {len(profile)}" if fan_on_overlay is not None else "n/a",
        )
        st.plotly_chart(
            plots.plot_temperatures(output, profile, fan_on=fan_on_overlay),
            width="stretch",
            key=f"{_KEY}.result_plot",
        )
