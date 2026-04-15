# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Three-winding simulation tab."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.model import Model

from streamlit_app import forms, plots
from streamlit_app.presets import THREE_WINDING_PRESETS, build_three_winding_transformer

_KEY = "threewinding"


def render() -> None:
    """Render the three-winding simulation tab."""
    st.subheader("Three-winding simulation")
    st.caption("Three-winding transformers with per-winding hot-spot output.")

    preset_label = st.selectbox(
        "Preset",
        options=list(THREE_WINDING_PRESETS),
        key=f"{_KEY}.preset",
    )
    preset = THREE_WINDING_PRESETS[preset_label]

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

    specs = forms.render_three_winding_spec_form(preset.specs, key_prefix=spec_scope)
    profile = forms.render_three_winding_profile_picker(specs, key_prefix=_KEY)
    initial_state = forms.render_initial_state_picker(key_prefix=_KEY)

    if st.button("Run simulation", type="primary", key=f"{_KEY}.run"):
        try:
            transformer = build_three_winding_transformer(preset, specs, cooling_type=cooling_type)
            output = Model(
                temperature_profile=profile,
                transformer=transformer,
                initial_condition=initial_state,
            ).run()
        except Exception as exc:  # noqa: BLE001
            st.error(f"{type(exc).__name__}: {exc}")
            return

        st.success("Simulation finished.")
        _render_per_winding_metrics(output)
        st.plotly_chart(plots.plot_temperatures(output, profile), width="stretch", key=f"{_KEY}.result_plot")


def _render_per_winding_metrics(output) -> None:  # noqa: ANN001
    hot_spot = output.hot_spot_temp_profile
    cols = st.columns(4)
    cols[0].metric("Max top-oil [°C]", f"{float(output.top_oil_temp_profile.max()):.1f}")
    if isinstance(hot_spot, pd.DataFrame):
        for i, winding in enumerate(("low_voltage_side", "middle_voltage_side", "high_voltage_side")):
            cols[i + 1].metric(
                f"Max hot-spot · {winding.split('_')[0].upper()} [°C]",
                f"{float(hot_spot[winding].max()):.1f}",
            )
    else:
        cols[1].metric("Max hot-spot [°C]", f"{float(hot_spot.max()):.1f}")
